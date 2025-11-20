#!/usr/bin/env python3
"""
Transcript Manager - Captures and stores call transcriptions from AVR bots.

This module:
1. Monitors AVR bot Docker containers for transcripts
2. Extracts conversation data from logs
3. Stores transcripts in the database
4. Associates recordings with calls
"""

import asyncio
import re
import json
# import docker  # Optional - only needed for container monitoring
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from loguru import logger
import aiofiles
import subprocess

class TranscriptManager:
    """Manages call transcripts and recordings."""

    def __init__(self, db_path: str = "dialer.db", recordings_dir: str = "/home/user/Desktop/Projects_Organized/01_Exodus_Dialer/recordings"):
        """Initialize transcript manager.

        Args:
            db_path: Path to SQLite database
            recordings_dir: Directory where recordings are stored
        """
        self.db_path = db_path
        self.recordings_dir = Path(recordings_dir)
        # self.docker_client = docker.from_env()  # Disabled for now
        self.active_calls: Dict[str, Dict] = {}  # call_uuid -> call_data

        # Ensure recordings directory exists
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📝 Transcript Manager initialized - DB: {db_path}, Recordings: {recordings_dir}")

    async def monitor_bot(self, bot_port: int, call_uuid: str):
        """Monitor a specific bot's logs for transcripts.

        Args:
            bot_port: Port number of the bot (e.g., 9092)
            call_uuid: Asterisk call UUID
        """
        container_name = f"avr-bot-{bot_port}"
        logger.info(f"👂 Starting transcript monitoring for {container_name} (Call: {call_uuid})")

        try:
            # For now, just log - container monitoring disabled
            logger.info(f"📝 Transcript monitoring would start here for {container_name}")
            return
            # container = self.docker_client.containers.get(container_name)

            # Initialize call data
            self.active_calls[call_uuid] = {
                "bot_port": bot_port,
                "start_time": datetime.now(),
                "transcript": [],
                "asr_lines": [],
                "llm_responses": []
            }

            # Stream logs from container
            for log_line in container.logs(stream=True, follow=True, tail=0):
                line = log_line.decode('utf-8').strip()

                # Parse ASR transcriptions (user speech)
                if "Received data from external asr service:" in line:
                    match = re.search(r"asr service: (.+)$", line)
                    if match:
                        user_text = match.group(1).strip()
                        if user_text:
                            self.active_calls[call_uuid]["asr_lines"].append({
                                "role": "user",
                                "content": user_text,
                                "timestamp": datetime.now().isoformat()
                            })
                            logger.debug(f"  📥 User: {user_text}")

                # Parse LLM responses (bot speech)
                elif "Sends text from LLM to TTS:" in line:
                    match = re.search(r"to TTS: (.+)$", line)
                    if match:
                        bot_text = match.group(1).strip()
                        if bot_text:
                            self.active_calls[call_uuid]["llm_responses"].append({
                                "role": "assistant",
                                "content": bot_text,
                                "timestamp": datetime.now().isoformat()
                            })
                            logger.debug(f"  🤖 Bot: {bot_text}")

                # Detect call end
                elif "Client connection duration:" in line or "Terminate packet received" in line:
                    logger.info(f"📞 Call ended for {call_uuid}")
                    await self.save_transcript(call_uuid)
                    break

        except docker.errors.NotFound:
            logger.error(f"❌ Container {container_name} not found")
        except Exception as e:
            logger.error(f"❌ Error monitoring {container_name}: {e}")
        finally:
            # Clean up call data
            if call_uuid in self.active_calls:
                await self.save_transcript(call_uuid)
                del self.active_calls[call_uuid]

    async def save_transcript(self, call_uuid: str):
        """Save transcript to database.

        Args:
            call_uuid: Call UUID to save
        """
        if call_uuid not in self.active_calls:
            logger.warning(f"⚠️  No transcript data for call {call_uuid}")
            return

        call_data = self.active_calls[call_uuid]

        # Combine ASR and LLM into full conversation
        conversation = []
        all_messages = sorted(
            call_data["asr_lines"] + call_data["llm_responses"],
            key=lambda x: x["timestamp"]
        )

        # Format transcript
        transcript_lines = []
        for msg in all_messages:
            role = "Customer" if msg["role"] == "user" else "Agent"
            transcript_lines.append(f"{role}: {msg['content']}")

        transcript_text = "\n".join(transcript_lines)

        # Find recording file
        recording_path = None
        for file in self.recordings_dir.glob(f"*{call_uuid}*.wav"):
            recording_path = str(file)
            break

        # Update database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update call_log with transcript and recording
            cursor.execute("""
                UPDATE call_log
                SET transcription_text = ?,
                    recording_url = ?
                WHERE call_uuid = ?
            """, (transcript_text, recording_path, call_uuid))

            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()

            if rows_updated > 0:
                logger.info(f"✅ Saved transcript for call {call_uuid}")
                logger.debug(f"   Transcript length: {len(transcript_text)} chars")
                logger.debug(f"   Recording: {recording_path}")
            else:
                logger.warning(f"⚠️  No call_log entry found for {call_uuid}")

        except Exception as e:
            logger.error(f"❌ Failed to save transcript for {call_uuid}: {e}")

    async def process_recording(self, call_uuid: str, recording_path: str):
        """Process and convert recording to MP3 for smaller file size.

        Args:
            call_uuid: Call UUID
            recording_path: Path to WAV recording
        """
        try:
            wav_path = Path(recording_path)
            mp3_path = wav_path.with_suffix('.mp3')

            # Convert WAV to MP3 using ffmpeg
            cmd = [
                'ffmpeg', '-i', str(wav_path),
                '-codec:a', 'libmp3lame',
                '-b:a', '64k',  # 64 kbps for phone quality
                '-ac', '1',      # Mono
                '-ar', '8000',   # 8kHz sample rate
                str(mp3_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Converted recording to MP3: {mp3_path}")
                # Delete original WAV to save space
                wav_path.unlink()
                return str(mp3_path)
            else:
                logger.error(f"❌ Failed to convert recording: {result.stderr}")
                return str(wav_path)

        except Exception as e:
            logger.error(f"❌ Error processing recording: {e}")
            return recording_path

    async def get_call_history_with_transcripts(self, limit: int = 100, campaign_id: Optional[int] = None):
        """Get call history including transcripts and recordings.

        Args:
            limit: Maximum number of records
            campaign_id: Optional campaign filter

        Returns:
            List of call records with transcripts
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = """
                SELECT
                    cl.*,
                    l.phone_number,
                    l.first_name,
                    l.last_name,
                    c.name as campaign_name
                FROM call_log cl
                LEFT JOIN leads l ON cl.lead_id = l.id
                LEFT JOIN campaigns c ON cl.campaign_id = c.id
                WHERE cl.transcription_text IS NOT NULL
            """

            params = []
            if campaign_id:
                query += " AND cl.campaign_id = ?"
                params.append(campaign_id)

            query += " ORDER BY cl.start_time DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            calls = []
            for row in rows:
                call_dict = dict(row)
                # Parse transcript if JSON
                if call_dict.get('transcription_text'):
                    try:
                        call_dict['transcript_parsed'] = json.loads(call_dict['transcription_text'])
                    except:
                        # Keep as plain text if not JSON
                        pass
                calls.append(call_dict)

            conn.close()

            logger.info(f"📜 Retrieved {len(calls)} calls with transcripts")
            return calls

        except Exception as e:
            logger.error(f"❌ Failed to get call history: {e}")
            return []

    async def start_monitoring(self):
        """Start monitoring all active bot containers."""
        logger.info("🚀 Starting transcript monitoring service")

        while True:
            try:
                # Docker monitoring disabled for now
                logger.debug("Container monitoring disabled - docker module not installed")
                await asyncio.sleep(30)
                continue
                # Check for active bot containers
                # containers = self.docker_client.containers.list(
                #     filters={"name": "avr-bot-"}
                # )

                for container in containers:
                    # Extract port from container name (e.g., avr-bot-9092 -> 9092)
                    match = re.search(r"avr-bot-(\d+)", container.name)
                    if match:
                        bot_port = int(match.group(1))

                        # Check if we're already monitoring this bot
                        # (Would need to implement proper tracking)

                        # For now, just log
                        logger.debug(f"  Found active bot: {container.name}")

                # Sleep before next check
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)


# Standalone service entry point
async def main():
    """Run transcript manager as standalone service."""
    manager = TranscriptManager()
    await manager.start_monitoring()


if __name__ == "__main__":
    # Configure logging
    logger.add(
        "transcript_manager.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG"
    )

    # Run service
    asyncio.run(main())