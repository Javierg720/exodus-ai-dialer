#!/usr/bin/env python3
"""
Direct AudioSocket Test Client for AVA Bot
Simulates what Asterisk does - connects directly to bot via AudioSocket protocol
"""

import socket
import struct
import time
import uuid
import subprocess
import wave
import os

# AudioSocket protocol constants
PACKET_TYPE_UUID = 0x01
PACKET_TYPE_AUDIO = 0x10
PACKET_TYPE_TERMINATE = 0x00

# Audio parameters (match AudioSocket: 8kHz, 16-bit, mono)
SAMPLE_RATE = 8000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit

def generate_tts_audio(text, output_file):
    """Generate audio using espeak-ng"""
    print(f"Generating TTS: '{text}'")
    
    # Generate raw audio at 22kHz first
    raw_file = output_file + '.raw'
    subprocess.run([
        'espeak-ng',
        '-v', 'en-us',
        '-s', '150',  # Speed
        '-w', raw_file,
        text
    ], check=True)
    
    # Convert to 8kHz, 16-bit, mono WAV (AudioSocket format)
    result = subprocess.run([
        'sox', raw_file,
        '-r', '8000',
        '-c', '1',
        '-b', '16',
        output_file
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Sox error: {result.stderr}")
        # Try direct conversion if sox fails
        subprocess.run([
            'sox', raw_file, output_file, 'rate', '8000'
        ], check=True)
    
    # Clean up temp file
    if os.path.exists(raw_file):
        os.remove(raw_file)
    
    print(f"✅ Audio saved: {output_file}")

def read_wav_data(filename):
    """Read raw PCM audio data from WAV file"""
    with wave.open(filename, 'rb') as wf:
        if wf.getnchannels() != CHANNELS or wf.getsampwidth() != SAMPLE_WIDTH or wf.getframerate() != SAMPLE_RATE:
            print(f"⚠️  Warning: WAV format mismatch")
            print(f"   Expected: {SAMPLE_RATE}Hz, {CHANNELS}ch, {SAMPLE_WIDTH*8}-bit")
            print(f"   Got: {wf.getframerate()}Hz, {wf.getnchannels()}ch, {wf.getsampwidth()*8}-bit")
        
        return wf.readframes(wf.getnframes())

def send_packet(sock, packet_type, payload):
    """Send AudioSocket TLV packet: [type:1][length:2][payload:n]"""
    header = struct.pack('>BH', packet_type, len(payload))
    packet = header + payload
    print(f"   Sending packet: type=0x{packet_type:02x}, len={len(payload)}, payload={payload[:50] if len(payload) <= 50 else payload[:47] + b'...'}")
    sock.sendall(packet)

def recv_packet(sock):
    """Receive AudioSocket TLV packet"""
    try:
        header = sock.recv(3)
        if len(header) < 3:
            return None, None
        
        packet_type, payload_len = struct.unpack('>BH', header)
        
        if payload_len > 0:
            payload = b''
            while len(payload) < payload_len:
                chunk = sock.recv(payload_len - len(payload))
                if not chunk:
                    break
                payload += chunk
            return packet_type, payload
        
        return packet_type, b''
    except:
        return None, None

def test_call_ava(host='127.0.0.1', port=9092):
    """Make a test call to AVA bot"""
    
    print("=" * 60)
    print("AVA AudioSocket Test Call")
    print("=" * 60)
    
    # Generate test phrase
    test_phrase = "Hello AVA, yes I'm interested in business funding"
    audio_file = '/home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/test_phrase.wav'
    
    print("\n[1/5] Generating TTS audio...")
    try:
        generate_tts_audio(test_phrase, audio_file)
    except FileNotFoundError as e:
        print(f"❌ Error: sox is not installed. Install with: sudo apt install sox")
        return
    except Exception as e:
        print(f"❌ Error generating TTS: {e}")
        return
    
    print("\n[2/5] Reading audio data...")
    try:
        audio_data = read_wav_data(audio_file)
        print(f"✅ Loaded {len(audio_data)} bytes of audio ({len(audio_data)/SAMPLE_RATE/SAMPLE_WIDTH:.1f}s)")
    except Exception as e:
        print(f"❌ Error reading audio: {e}")
        return
    
    print(f"\n[3/5] Connecting to AVA bot at {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print("✅ Connected!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   Make sure avr-bot-9092 container is running")
        return
    
    try:
        # Send UUID packet (required by AudioSocket protocol)
        # Try sending as 16-byte binary UUID (not string)
        print("\n[4/5] Sending UUID...")
        call_uuid = uuid.uuid4()
        uuid_bytes = call_uuid.bytes  # Get 16-byte binary representation
        send_packet(sock, PACKET_TYPE_UUID, uuid_bytes)
        print(f"✅ Sent UUID: {str(call_uuid)} (as 16 binary bytes)")
        
        # Wait for AVA to start speaking and record greeting
        print("\n[5/5] Listening for AVA's greeting...")
        print("(AVA should say: 'Hey there, Ava with Fund Express...')")
        print("\nReceiving audio from AVA...")
        
        audio_received = False
        start_time = time.time()
        received_packets = 0
        greeting_audio = []
        
        # Receive AVA's greeting for a few seconds
        while time.time() - start_time < 10:
            packet_type, payload = recv_packet(sock)
            
            if packet_type is None:
                break
            
            if packet_type == PACKET_TYPE_AUDIO:
                if not audio_received:
                    print("✅ Receiving audio from AVA!")
                    audio_received = True
                if payload:
                    greeting_audio.append(payload)
                received_packets += 1
                if received_packets % 50 == 0:
                    print(f"   Received {received_packets} audio packets...")
            elif packet_type == PACKET_TYPE_TERMINATE:
                print("Bot terminated connection")
                break
        
        if audio_received:
            print(f"✅ Received {received_packets} audio packets from AVA")
        else:
            print("⚠️  No audio received from AVA")
        
        # Wait for AVA to finish speaking
        print("\n🎤 Waiting for AVA to finish speaking...")
        time.sleep(3)
        
        # Send our response audio
        print(f"\n🗣️  Speaking to AVA: '{test_phrase}'")
        
        # Send audio in 20ms chunks (160 samples @ 8kHz = 320 bytes)
        chunk_size = 320
        chunks_sent = 0
        
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i+chunk_size]
            
            # Pad last chunk if needed
            if len(chunk) < chunk_size:
                chunk += b'\x00' * (chunk_size - len(chunk))
            
            send_packet(sock, PACKET_TYPE_AUDIO, chunk)
            chunks_sent += 1
            
            # Send at 50 FPS (20ms intervals)
            time.sleep(0.020)
        
        print(f"✅ Sent {chunks_sent} audio chunks to AVA")
        
        # Listen for AVA's response and record it
        print("\n👂 Listening for AVA's response...")
        response_start = time.time()
        response_packets = 0
        recorded_audio = []
        
        while time.time() - response_start < 15:
            packet_type, payload = recv_packet(sock)
            
            if packet_type is None:
                break
            
            if packet_type == PACKET_TYPE_AUDIO:
                response_packets += 1
                if payload:
                    recorded_audio.append(payload)  # Save the audio
                if response_packets == 1:
                    print("✅ AVA is responding!")
                if response_packets % 50 == 0:
                    print(f"   Received {response_packets} response packets...")
            elif packet_type == PACKET_TYPE_TERMINATE:
                print("Bot terminated connection")
                break
        
        if response_packets > 0:
            print(f"✅ AVA responded with {response_packets} audio packets!")
        else:
            print("⚠️  No response from AVA")
        
        # Save the complete conversation recording (greeting + response)
        print("\n💾 Saving conversation recording...")
        recording_file = '/home/ubuntu/Documents/EXODUS_BACKUP_20251117_163623/ava_conversation.wav'
        
        # Combine greeting and response audio
        all_audio = greeting_audio + recorded_audio
        if all_audio:
            audio_data = b''.join(all_audio)
            with wave.open(recording_file, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(SAMPLE_WIDTH)
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(audio_data)
            
            duration = len(audio_data) / SAMPLE_RATE / SAMPLE_WIDTH
            print(f"✅ Saved {len(audio_data)} bytes ({duration:.1f}s) to: {recording_file}")
        else:
            print("⚠️  No audio to save")
        
        # Send terminate packet
        print("\n📴 Ending call...")
        send_packet(sock, PACKET_TYPE_TERMINATE, b'')
        
    except Exception as e:
        print(f"❌ Error during call: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\n✅ Call ended")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nCheck bot logs to see if AVA processed your speech:")
    print("  docker logs --tail 50 avr-bot-9092")
    print("")

if __name__ == '__main__':
    test_call_ava()
