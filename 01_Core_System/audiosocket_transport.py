#!/usr/bin/env python3
"""
AudioSocket Transport for Pipecat

Implements Asterisk AudioSocket protocol for telephony integration.
AudioSocket is a simple TCP protocol for streaming bidirectional audio
between Asterisk and external applications.

Protocol Specification (TLV Format):
All packets use Type-Length-Value framing:
- Type: 1 byte (packet type)
- Length: 2 bytes (big-endian, payload length)
- Value: Variable length payload

Packet Types:
- 0x00: Terminate connection
- 0x01: UUID (16-byte binary UUID or variable-length string)
- 0x03: DTMF (1-byte ASCII digit)
- 0x10: Audio (16-bit signed PCM, 8kHz, mono, little-endian)
- 0xff: Error

Connection Flow:
1. Asterisk connects via TCP to host:port
2. First packet: UUID packet [0x01][len_hi len_lo][uuid_bytes]
3. Subsequent packets: Audio frames [0x10][len_hi len_lo][audio_data]
4. Bidirectional: Both directions use same TLV format

References:
- Asterisk AudioSocket: https://wiki.asterisk.org/wiki/display/AST/AudioSocket
- Source: res/res_audiosocket.c in Asterisk repository
- AVR Implementation: https://github.com/agentvoiceresponse/avr-app
"""

import asyncio
import struct
import io
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass
from collections import deque

import numpy as np
from scipy import signal
from loguru import logger

from pipecat.frames.frames import (
    StartFrame,
    EndFrame,
    CancelFrame,
    InputAudioRawFrame,
    OutputAudioRawFrame,
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.transports.base_input import BaseInputTransport
from pipecat.transports.base_output import BaseOutputTransport
from pipecat.transports.base_transport import BaseTransport, TransportParams


# AudioSocket Constants
AUDIOSOCKET_SAMPLE_RATE = 8000  # Asterisk AudioSocket uses 8kHz
AUDIOSOCKET_CHANNELS = 1  # Mono
AUDIOSOCKET_SAMPLE_WIDTH = 2  # 16-bit = 2 bytes

# Pipecat typically uses 16kHz
PIPECAT_SAMPLE_RATE = 16000
PIPECAT_CHANNELS = 1


class AudioSocketParams(TransportParams):
    """Configuration parameters for AudioSocket transport.

    Parameters:
        audio_out_enabled: Enable audio output (always True for AudioSocket)
        audio_in_enabled: Enable audio input (always True for AudioSocket)
        audio_out_sample_rate: Output sample rate (16kHz for Pipecat)
        audio_in_sample_rate: Input sample rate (16kHz for Pipecat)
    """

    audio_out_enabled: bool = True
    audio_in_enabled: bool = True
    audio_out_sample_rate: int = PIPECAT_SAMPLE_RATE
    audio_in_sample_rate: int = PIPECAT_SAMPLE_RATE
    audio_out_channels: int = PIPECAT_CHANNELS
    audio_in_channels: int = PIPECAT_CHANNELS


@dataclass
class AudioSocketCallbacks:
    """Callback functions for AudioSocket events.

    Parameters:
        on_call_connected: Called when Asterisk connects with a call UUID
        on_call_disconnected: Called when the call ends
        on_server_ready: Called when the TCP server is ready to accept connections
    """

    on_call_connected: Callable[[str], Awaitable[None]]  # UUID
    on_call_disconnected: Callable[[str], Awaitable[None]]  # UUID
    on_server_ready: Callable[[], Awaitable[None]]


# Audio keepalive constants
SILENCE_20MS = b'\x00' * 320  # 320 bytes = 160 samples * 2 bytes = 20ms @ 8kHz
FRAME_INTERVAL = 0.020  # 20ms = 50 FPS


class AudioKeepalivePlayer:
    """Maintains continuous 50 FPS audio stream to prevent buffer starvation."""
    
    def __init__(self, writer: asyncio.StreamWriter):
        self.writer = writer
        self.queue = deque(maxlen=500)  # ~10 seconds buffer
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.frames_sent = 0
        self.silence_sent = 0
        
    async def start(self):
        """Start 50 FPS keepalive loop."""
        if self.running:
            return
        self.running = True
        self.task = asyncio.create_task(self._keepalive_loop())
        logger.info("🎵 AudioKeepalive started - 50 FPS stream")
        
    async def stop(self):
        """Stop keepalive loop."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info(f"🛑 Keepalive stopped - {self.frames_sent} frames, {self.silence_sent} silence")
        
    def enqueue_audio(self, pcm_8k: bytes):
        """Add audio to queue (chunked into 320-byte frames)."""
        for i in range(0, len(pcm_8k), 320):
            chunk = pcm_8k[i:i+320]
            if len(chunk) < 320:
                chunk += b'\x00' * (320 - len(chunk))
            self.queue.append(chunk)
            
    async def _keepalive_loop(self):
        """Send frames at exactly 50 FPS."""
        import time
        next_frame_time = time.time()
        
        while self.running:
            try:
                chunk = self.queue.popleft() if self.queue else SILENCE_20MS
                if chunk != SILENCE_20MS:
                    self.frames_sent += 1
                else:
                    self.silence_sent += 1
                    
                header = struct.pack('>BH', 0x10, 320)
                self.writer.write(header + chunk)
                await self.writer.drain()
                
                next_frame_time += FRAME_INTERVAL
                sleep_time = next_frame_time - time.time()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    next_frame_time = time.time()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Keepalive error: {e}")
                await asyncio.sleep(0.02)


class AudioResampler:
    """Handles audio resampling between Asterisk (8kHz) and Pipecat (16kHz).

    Uses scipy's resample_poly with optimized Kaiser windows for high-quality
    resampling with minimal latency and artifacts.
    """

    @staticmethod
    def normalize_audio(samples: np.ndarray) -> np.ndarray:
        """Prevent clipping by normalizing peak levels and removing DC offset.

        Args:
            samples: Audio samples as numpy array (any dtype)

        Returns:
            Normalized samples (same dtype)
        """
        # Handle empty arrays (end-of-stream markers)
        if samples.size == 0:
            return samples

        # Remove DC offset (critical for telephony - prevents "tinny" sound)
        samples = samples - samples.mean()
        
        max_val = np.abs(samples).max()
        if max_val > 32767 * 0.95:  # 95% of int16 max to prevent clipping
            scale = (32767 * 0.95) / max_val
            samples = samples * scale
        return samples

    @staticmethod
    def resample_8k_to_16k(audio_8k: bytes) -> bytes:
        """Resample audio from 8kHz to 16kHz with quality optimization.

        Args:
            audio_8k: Raw 16-bit PCM audio at 8kHz

        Returns:
            Raw 16-bit PCM audio at 16kHz
        """
        # Handle empty audio frames (end-of-stream markers)
        if len(audio_8k) == 0:
            return b''

        # Convert bytes to numpy array (keep as float for processing)
        samples = np.frombuffer(audio_8k, dtype=np.int16).astype(np.float32)

        # Resample from 8kHz to 16kHz (2x upsampling)
        # Kaiser window with beta=5.0 for better voice quality
        samples_16k = signal.resample_poly(
            samples,
            up=2,
            down=1,
            window=('kaiser', 5.0),  # Optimized for voice (smoother passband)
            padtype='line'           # Better edge handling
        )

        # Normalize to prevent clipping
        samples_16k = AudioResampler.normalize_audio(samples_16k)

        # Convert back to int16 and bytes
        samples_16k_int16 = samples_16k.astype(np.int16)
        return samples_16k_int16.tobytes()

    @staticmethod
    def resample_16k_to_8k(audio_16k: bytes) -> bytes:
        """Resample audio from 16kHz to 8kHz with quality optimization.

        Args:
            audio_16k: Raw 16-bit PCM audio at 16kHz

        Returns:
            Raw 16-bit PCM audio at 8kHz
        """
        # Handle empty audio frames (end-of-stream markers)
        if len(audio_16k) == 0:
            return b''

        # Convert bytes to numpy array (keep as float for processing)
        samples = np.frombuffer(audio_16k, dtype=np.int16).astype(np.float32)

        # Resample from 16kHz to 8kHz (2x downsampling)
        # Kaiser window with beta=8.0 for aggressive anti-aliasing
        samples_8k = signal.resample_poly(
            samples,
            up=1,
            down=2,
            window=('kaiser', 8.0),  # Stronger anti-aliasing for downsampling
            padtype='line'
        )

        # Normalize to prevent clipping
        samples_8k = AudioResampler.normalize_audio(samples_8k)

        # Convert back to int16 and bytes
        samples_8k_int16 = samples_8k.astype(np.int16)
        return samples_8k_int16.tobytes()


class AudioSocketInputTransport(BaseInputTransport):
    """AudioSocket input transport for receiving audio from Asterisk.

    Handles incoming TCP connections from Asterisk, reads the call UUID,
    and streams audio data to the Pipecat pipeline with resampling from
    8kHz to 16kHz.
    """

    def __init__(
        self,
        transport: BaseTransport,
        host: str,
        port: int,
        params: AudioSocketParams,
        callbacks: AudioSocketCallbacks,
        **kwargs,
    ):
        """Initialize AudioSocket input transport.

        Args:
            transport: Parent transport instance
            host: Host address to bind TCP server
            port: Port number to bind TCP server
            params: AudioSocket configuration parameters
            callbacks: Event callbacks
            **kwargs: Additional arguments for parent class
        """
        super().__init__(params, **kwargs)

        self._transport = transport
        self._host = host
        self._port = port
        self._params = params
        self._callbacks = callbacks

        self._server: Optional[asyncio.Server] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._call_uuid: Optional[str] = None

        self._server_task = None
        self._read_task = None
        self._stop_server_event = asyncio.Event()

        self._initialized = False

    async def start(self, frame: StartFrame):
        """Start the AudioSocket TCP server."""
        await super().start(frame)

        if self._initialized:
            return

        self._initialized = True

        if not self._server_task:
            self._server_task = self.create_task(self._server_task_handler())

        await self.set_transport_ready(frame)

    async def stop(self, frame: EndFrame):
        """Stop the AudioSocket server and cleanup."""
        await super().stop(frame)
        self._stop_server_event.set()

        if self._read_task:
            await self.cancel_task(self._read_task)
            self._read_task = None

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None

        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None

        if self._server_task:
            await self._server_task
            self._server_task = None

    async def cancel(self, frame: CancelFrame):
        """Cancel the AudioSocket server immediately."""
        await super().cancel(frame)

        if self._read_task:
            await self.cancel_task(self._read_task)
            self._read_task = None

        if self._server_task:
            await self.cancel_task(self._server_task)
            self._server_task = None

    async def cleanup(self):
        """Cleanup resources."""
        await super().cleanup()
        await self._transport.cleanup()

    async def _server_task_handler(self):
        """Start TCP server and wait for connections."""
        logger.info(f"🎙️  AudioSocket server starting on {self._host}:{self._port}")

        self._server = await asyncio.start_server(
            self._client_handler, self._host, self._port
        )

        addrs = ", ".join(str(sock.getsockname()) for sock in self._server.sockets)
        logger.info(f"✅ AudioSocket server listening on {addrs}")

        await self._callbacks.on_server_ready()
        await self._stop_server_event.wait()

    async def _client_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """Handle incoming Asterisk connection."""
        addr = writer.get_extra_info("peername")
        logger.info(f"📞 Asterisk connected from {addr}")

        # Close previous connection if exists (one call at a time)
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                logger.warning("Replacing existing connection with new call")
            except (BrokenPipeError, ConnectionError, OSError) as e:
                logger.info(f"Previous connection already closed: {e}")

        self._reader = reader
        self._writer = writer
        
        # Disable TCP Nagle's algorithm for immediate frame transmission
        # This prevents 40-200ms buffering delays that cause audio choppiness
        if hasattr(writer.transport, 'set_nodelay'):
            writer.transport.set_nodelay(True)
            logger.info("✅ TCP_NODELAY enabled - reduced latency mode")

        try:
            # Step 1: Read UUID packet (TLV format)
            # AudioSocket uses Type-Length-Value framing for ALL packets
            # UUID packet: [0x01][len_hi len_lo][uuid_bytes]

            # Read packet header (3 bytes: 1 type + 2 length big-endian)
            header = await reader.readexactly(3)
            msg_type = header[0]
            payload_len = struct.unpack('>H', header[1:3])[0]

            logger.info(f"🔍 First packet: type=0x{msg_type:02x}, length={payload_len} bytes")

            # Validate UUID packet type
            if msg_type != 0x01:
                logger.warning(f"⚠️  Expected UUID packet (0x01), got 0x{msg_type:02x}")

            # Read UUID payload
            if payload_len > 0:
                uuid_bytes = await reader.readexactly(payload_len)
                # Try to decode as string UUID
                try:
                    self._call_uuid = uuid_bytes.decode('utf-8').strip()
                except UnicodeDecodeError:
                    # If binary UUID (16 bytes), convert to string
                    if payload_len == 16:
                        import uuid
                        self._call_uuid = str(uuid.UUID(bytes=uuid_bytes))
                        logger.info(f"📋 Binary UUID converted: {self._call_uuid}")
                    else:
                        # Generate new UUID if can't decode
                        import uuid
                        self._call_uuid = str(uuid.uuid4())
                        logger.warning(f"⚠️  Could not decode UUID payload, generated: {self._call_uuid}")
            else:
                # Empty UUID, generate one
                import uuid
                self._call_uuid = str(uuid.uuid4())
                logger.warning(f"⚠️  Empty UUID payload, generated: {self._call_uuid}")

            if self._call_uuid:
                logger.info(f"📋 Call UUID: {self._call_uuid}")

            # Set writer on output transport for bidirectional audio
            output_transport = self._transport.output()
            if isinstance(output_transport, AudioSocketOutputTransport):
                await output_transport.set_connection(writer)

            # Notify call connected
            await self._callbacks.on_call_connected(self._call_uuid)

            # Step 2: Start reading audio stream
            if not self._read_task:
                self._read_task = self.create_task(self._read_audio_stream())

        except Exception as e:
            logger.error(f"Error in AudioSocket client handler: {e}")
            await self._cleanup_connection()

    async def _read_audio_stream(self):
        """Read audio data from Asterisk and push to pipeline."""
        import struct

        frame_count = 0

        try:
            logger.info("🎧 Starting audio read stream - waiting for incoming audio...")
            while self._reader and not self._reader.at_eof():
                # Read AudioSocket frame header (3 bytes: type + length)
                try:
                    header = await self._reader.readexactly(3)
                    logger.info(f"📨 Received header: type=0x{header[0]:02x}, len={struct.unpack('>H', header[1:3])[0]}")
                except asyncio.IncompleteReadError as e:
                    logger.info(f"📭 Connection closed (got {frame_count} audio frames)")
                    break

                if not header or len(header) < 3:
                    logger.info(f"📭 No more data (got {frame_count} audio frames)")
                    break

                # Parse header: 1 byte type + 2 bytes length (big-endian)
                msg_type = header[0]
                payload_len = struct.unpack('>H', header[1:3])[0]

                # Read payload
                try:
                    payload = await self._reader.readexactly(payload_len)
                except asyncio.IncompleteReadError as e:
                    logger.warning(f"Incomplete frame: expected {payload_len}, got {len(e.partial)}")
                    break

                # Only process audio frames (type 0x10)
                if msg_type != 0x10:
                    logger.info(f"⚠️ Non-audio frame received: type=0x{msg_type:02x}, len={payload_len}")
                    continue

                frame_count += 1
                if frame_count % 10 == 1:  # Log every ~200ms
                    logger.info(f"🎵 Incoming audio frame {frame_count}: {len(payload)} bytes")

                # Audio is 16-bit signed linear PCM at 8kHz
                audio_8k = payload

                # Resample 8kHz -> 16kHz
                audio_16k = AudioResampler.resample_8k_to_16k(audio_8k)

                # Push to pipeline
                frame = InputAudioRawFrame(
                    audio=audio_16k,
                    sample_rate=PIPECAT_SAMPLE_RATE,
                    num_channels=PIPECAT_CHANNELS,
                )
                await self.push_audio_frame(frame)

            logger.info(f"🏁 Audio stream ended after {frame_count} frames")

        except asyncio.CancelledError:
            logger.info("Audio read task cancelled")
            raise
        except Exception as e:
            logger.error(f"❌ Error reading audio stream: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            await self._cleanup_connection()

    async def _cleanup_connection(self):
        """Cleanup connection and notify disconnect."""
        if self._call_uuid:
            logger.info(f"📴 Call ended: {self._call_uuid}")
            await self._callbacks.on_call_disconnected(self._call_uuid)
            self._call_uuid = None

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
            self._reader = None

        # CRITICAL: Clear read task reference so next call can start a new one
        self._read_task = None


class AudioSocketOutputTransport(BaseOutputTransport):
    """AudioSocket output transport for sending audio to Asterisk.

    Handles outgoing audio frames from Pipecat pipeline, resampling from
    16kHz to 8kHz, and sending to Asterisk via TCP connection.
    """

    def __init__(self, transport: BaseTransport, params: AudioSocketParams, **kwargs):
        """Initialize AudioSocket output transport.

        Args:
            transport: Parent transport instance
            params: AudioSocket configuration parameters
            **kwargs: Additional arguments for parent class
        """
        super().__init__(params, **kwargs)

        self._transport = transport
        self._params = params
        self._writer: Optional[asyncio.StreamWriter] = None
        self._initialized = False
        
        # Audio keepalive player - prevents buffer starvation
        self._keepalive: Optional[AudioKeepalivePlayer] = None

        # Frame buffering for initial audio (prevents choppy start)
        # Buffer up to 5 seconds of audio (~800 frames at 160 frames/sec)
        self._frame_buffer = deque(maxlen=800)
        self._buffer_size_limit = 800
        self._frames_buffered = 0

        # Debugging statistics
        self._frames_received = 0
        self._frames_sent = 0
        self._frames_dropped = 0
        self._bytes_sent = 0
        self._last_frame_time = None

    async def set_connection(self, writer: Optional[asyncio.StreamWriter]):
        """Set the active Asterisk connection writer.

        Args:
            writer: StreamWriter for the active connection, or None to clear
        """
        if self._writer and writer != self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            logger.warning("Replacing writer with new connection")

        # Stop old keepalive if exists
        if self._keepalive:
            await self._keepalive.stop()
            self._keepalive = None
        
        self._writer = writer
        
        # Disable TCP Nagle for output stream (reduce latency)
        if writer and hasattr(writer.transport, 'set_nodelay'):
            writer.transport.set_nodelay(True)

        if writer:
            logger.info("🔗 AudioSocket output connection established - ready to send audio")
            
            # Start keepalive player - prevents buffer starvation
            self._keepalive = AudioKeepalivePlayer(writer)
            await self._keepalive.start()
            logger.info("✅ Audio keepalive started - continuous 50 FPS stream")

            # Flush buffered frames
            if len(self._frame_buffer) > 0:
                logger.info(f"🎵 Flushing {len(self._frame_buffer)} buffered audio frames")
                flushed_count = 0

                while self._frame_buffer:
                    frame = self._frame_buffer.popleft()
                    success = await self._send_frame(frame)
                    if success:
                        flushed_count += 1
                    else:
                        logger.error("Failed to flush buffered frame")
                        break

                logger.info(f"✅ Flushed {flushed_count} buffered frames to Asterisk")
                self._frames_buffered = 0
        else:
            logger.info("🔌 AudioSocket output connection cleared")
            # Clear buffer when connection is closed
            self._frame_buffer.clear()
            self._frames_buffered = 0

    async def start(self, frame: StartFrame):
        """Start the output transport."""
        await super().start(frame)

        if self._initialized:
            return

        self._initialized = True

        # CRITICAL: Register MediaSender infrastructure to enable frame routing
        logger.info("🎬 Initializing AudioSocket output MediaSender...")
        await self.set_transport_ready(frame)
        logger.info("✅ AudioSocket output transport ready - MediaSender registered for destination [None]")

    async def stop(self, frame: EndFrame):
        """Stop the output transport."""
        await super().stop(frame)

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

    async def _send_frame(self, frame: OutputAudioRawFrame) -> bool:
        """Internal method to send a single audio frame to Asterisk.

        Args:
            frame: Output audio frame at 16kHz (Pipecat rate)

        Returns:
            True if audio was written successfully, False otherwise
        """
        import struct
        import time

        if not self._writer:
            return False

        try:
            # Resample 16kHz -> 8kHz for Asterisk (16-bit signed linear PCM)
            audio_8k = AudioResampler.resample_16k_to_8k(frame.audio)

            # CRITICAL: Use keepalive player instead of direct send
            # This prevents buffer starvation during TTS/LLM processing
            if self._keepalive:
                # Enqueue audio - keepalive loop will send at 50 FPS
                self._keepalive.enqueue_audio(audio_8k)
                
                # Update statistics
                self._frames_sent += 1
                self._bytes_sent += len(audio_8k)
                self._last_frame_time = time.time()
            else:
                logger.warning("⚠️ No keepalive player - audio dropped")
                return False

            # Log progress every 10 frames
            if self._frames_sent % 10 == 1:
                logger.info(f"📤 Audio output: frame {self._frames_sent}/{self._frames_received}, "
                           f"{self._bytes_sent} bytes sent, {self._frames_dropped} dropped, "
                           f"{self._frames_buffered} buffered")

            logger.debug(f"✅ Sent AudioSocket frame #{self._frames_sent}: {len(audio_8k)} bytes audio")
            return True

        except Exception as e:
            logger.error(f"❌ Error writing audio to Asterisk: {e}")
            logger.error(f"📊 Stats: {self._frames_sent} sent, {self._frames_dropped} dropped")
            logger.error("💡 Troubleshooting: TCP connection may be closed or broken")
            import traceback
            logger.error(traceback.format_exc())
            # Connection might be broken
            self._writer = None
            return False

    async def write_audio_frame(self, frame: OutputAudioRawFrame) -> bool:
        """Write audio frame to Asterisk (called by BaseOutputTransport).

        Args:
            frame: Output audio frame at 16kHz (Pipecat rate)

        Returns:
            True if audio was written successfully, False otherwise
        """
        self._frames_received += 1
        logger.info(f"🎙️  WRITE_AUDIO_FRAME CALLED: frame #{self._frames_received}, has_writer={self._writer is not None}")

        if not self._writer:
            # Buffer frames while waiting for connection
            if len(self._frame_buffer) < self._buffer_size_limit:
                self._frame_buffer.append(frame)
                self._frames_buffered += 1
                if self._frames_buffered == 1:
                    logger.info("🎵 Buffering initial audio frames (connection not ready yet)")
                elif self._frames_buffered % 100 == 0:
                    logger.info(f"🎵 Buffered {self._frames_buffered} frames (waiting for connection)")
                return True
            else:
                # Buffer is full, drop the frame
                self._frames_dropped += 1
                logger.warning(f"⚠️  Buffer full, dropped frame {self._frames_dropped}")
                return False

        # Writer is available, send immediately
        return await self._send_frame(frame)

    def get_diagnostics(self) -> dict:
        """Get diagnostic information about the output transport.

        Returns:
            Dictionary with transport state and statistics
        """
        return {
            "initialized": self._initialized,
            "has_writer": self._writer is not None,
            "frames_received": self._frames_received,
            "frames_sent": self._frames_sent,
            "frames_dropped": self._frames_dropped,
            "frames_buffered": self._frames_buffered,
            "buffer_size": len(self._frame_buffer),
            "bytes_sent": self._bytes_sent,
            "last_frame_time": self._last_frame_time,
            "sample_rate": self.sample_rate,
            "audio_chunk_size": self.audio_chunk_size,
        }

    def log_diagnostics(self):
        """Log diagnostic information."""
        diag = self.get_diagnostics()
        logger.info("=" * 60)
        logger.info("📊 AudioSocket Output Transport Diagnostics")
        logger.info("=" * 60)
        logger.info(f"  Initialized: {diag['initialized']}")
        logger.info(f"  Writer connected: {diag['has_writer']}")
        logger.info(f"  Frames received: {diag['frames_received']}")
        logger.info(f"  Frames sent: {diag['frames_sent']}")
        logger.info(f"  Frames dropped: {diag['frames_dropped']}")
        logger.info(f"  Frames buffered: {diag['frames_buffered']}")
        logger.info(f"  Buffer size: {diag['buffer_size']}")
        logger.info(f"  Bytes sent: {diag['bytes_sent']}")
        logger.info(f"  Last frame: {diag['last_frame_time']}")
        logger.info(f"  Sample rate: {diag['sample_rate']} Hz")
        logger.info(f"  Chunk size: {diag['audio_chunk_size']} bytes")
        logger.info("=" * 60)

    async def cleanup(self):
        """Cleanup resources."""
        # Log final statistics
        logger.info("🛑 AudioSocket output transport shutting down")
        self.log_diagnostics()
        await super().cleanup()
        await self._transport.cleanup()


class AudioSocketTransport(BaseTransport):
    """AudioSocket transport for Asterisk telephony integration.

    Implements Asterisk AudioSocket protocol for bidirectional audio streaming
    between Asterisk PBX and Pipecat voice AI pipelines.

    Example:
        ```python
        transport = AudioSocketTransport(
            host="0.0.0.0",
            port=9092,
            params=AudioSocketParams(),
            callbacks=AudioSocketCallbacks(
                on_call_connected=lambda uuid: logger.info(f"Call: {uuid}"),
                on_call_disconnected=lambda uuid: logger.info(f"Ended: {uuid}"),
                on_server_ready=lambda: logger.info("Ready for calls"),
            ),
        )

        pipeline = Pipeline([
            transport.input(),
            deepgram_stt,
            llm,
            edge_tts,
            transport.output(),
        ])
        ```
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9092,
        params: AudioSocketParams = AudioSocketParams(),
        callbacks: AudioSocketCallbacks = None,
        **kwargs,
    ):
        """Initialize AudioSocket transport.

        Args:
            host: Host address to bind TCP server (default: 0.0.0.0)
            port: Port number to bind TCP server (default: 9092)
            params: Transport configuration parameters
            callbacks: Event callbacks for call lifecycle
            **kwargs: Additional arguments for parent class
        """
        super().__init__(**kwargs)

        self._host = host
        self._port = port
        self._params = params

        # Default callbacks if not provided
        self._callbacks = callbacks or AudioSocketCallbacks(
            on_call_connected=self._default_on_call_connected,
            on_call_disconnected=self._default_on_call_disconnected,
            on_server_ready=self._default_on_server_ready,
        )

        # Create input and output transports
        self._input = AudioSocketInputTransport(
            self, host, port, params, self._callbacks, name=self._input_name
        )
        self._output = AudioSocketOutputTransport(self, params, name=self._output_name)

    def input(self) -> BaseInputTransport:
        """Get the input transport for receiving audio from Asterisk."""
        return self._input

    def output(self) -> BaseOutputTransport:
        """Get the output transport for sending audio to Asterisk."""
        return self._output

    async def cleanup(self):
        """Cleanup transport resources."""
        pass

    # Default callbacks
    async def _default_on_call_connected(self, uuid: str):
        logger.info(f"📞 Call connected: {uuid}")

    async def _default_on_call_disconnected(self, uuid: str):
        logger.info(f"📴 Call disconnected: {uuid}")

    async def _default_on_server_ready(self):
        logger.info("✅ AudioSocket server ready for calls")
