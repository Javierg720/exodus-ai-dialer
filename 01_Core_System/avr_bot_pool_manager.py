#!/usr/bin/env python3
"""
AVR Bot Pool Manager - Minimal state tracker for AVR containerized bots.

This manager assumes bots are already running in Docker containers (AVR agents) and:
- Tracks which ports are busy/idle/crashed.
- Implements round-robin assignment.
- Enforces wrap-up time after calls.
- Monitors Docker container health via AVRBotManager.

Compatible with dialer_orchestrator.py - drop-in replacement for BotPoolManager.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from loguru import logger
from bot_pool_interface import BotPoolInterface, BotStatus
from avr_bot_manager import AVRBotManager
from datetime import datetime


@dataclass
class BotInstance:
    """Represents an AVR bot running in Docker."""
    port: int
    status: BotStatus = BotStatus.IDLE
    current_call_uuid: Optional[str] = None
    busy_since: Optional[float] = None
    wrap_up_end_time: Optional[float] = None  # 5-second cooldown after call
    crashes: int = 0 # Track crashes for logging/reporting

    def is_available(self) -> bool:
        """Check if this bot is available (not busy, not in wrap-up, not crashed).

        Returns:
            True if bot is available
        """
        now = time.time()
        in_wrap_up = self.wrap_up_end_time and now < self.wrap_up_end_time
        return self.status == BotStatus.IDLE and not in_wrap_up and self.status != BotStatus.CRASHED


class AVRBotPoolManager(BotPoolInterface):
    """Lightweight manager for pre-running AVR Docker bot containers.

    AVR bots are managed externally by docker-compose. This class only:
    - Tracks which ports are busy/idle
    - Implements round-robin assignment
    - Enforces wrap-up time after calls
    - Monitors Docker container health via AVRBotManager
    """

    def __init__(
        self,
        base_port: int = 9092,
        num_instances: int = 20,
        wrap_up_time: float = 5.0,  # Seconds
        health_check_interval: float = 30.0, # Seconds between Docker checks
        **kwargs  # Accept and ignore bot_script, config_path, etc.
    ):
        self.base_port = base_port
        self.num_instances = num_instances
        self.wrap_up_time = wrap_up_time
        self.health_check_interval = health_check_interval

        # Create bot instances (Docker containers assumed to be running)
        self.bots: Dict[int, BotInstance] = {}
        for i in range(num_instances):
            port = base_port + i
            self.bots[port] = BotInstance(port=port)

        # Lock for thread-safe bot assignment
        self._lock = asyncio.Lock()
        self._next_bot_index = 0
        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        
        # Docker utility manager
        self.docker_manager = AVRBotManager()

        logger.info(f"🐳 AVR Bot Pool Manager initialized: {num_instances} instances, "
                   f"ports {base_port}-{base_port + num_instances - 1}")
        logger.info("💡 Assumes AVR Docker containers are already running")

    async def start(self):
        """Start monitoring and initial health check."""
        logger.info("🚀 AVR Bot Pool starting monitoring...")
        await self.check_health() # Initial check
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"✅ Tracking {len(self.bots)} bot ports: {self.base_port}-{self.base_port + self.num_instances - 1}")

    async def stop(self):
        """Stop monitoring."""
        logger.info("🛑 AVR Bot Pool manager stopping monitoring...")
        self._stop_event.set()
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ AVR Bot Pool manager stopped")

    async def _monitor_loop(self):
        """Continuous monitoring loop for Docker container health."""
        logger.info("👀 AVR Bot Pool monitoring started")
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self.health_check_interval)
                await self.check_health()
        except asyncio.CancelledError:
            logger.info("👀 AVR Bot Pool monitoring stopped")
            raise

    async def check_health(self):
        """Perform a health check on all bots (checks Docker status)."""
        logger.debug("🔍 Checking Docker container health...")
        
        # Use AVRBotManager to get actual Docker status
        docker_statuses = self.docker_manager.get_running_bots()
        
        for docker_status in docker_statuses:
            port = docker_status["port"]
            bot = self.bots.get(port)
            
            if not bot:
                continue # Should not happen

            # Check if the container is running
            if docker_status["status"] != "RUNNING":
                if bot.status != BotStatus.CRASHED:
                    logger.error(f"❌ Bot {port} CRASHED! Docker status: {docker_status['status']}")
                    bot.status = BotStatus.CRASHED
                    bot.crashes += 1
                    # Attempt to restart the bot (non-blocking)
                    asyncio.create_task(self._restart_bot(port))
            else:
                # Container is running, so it can be IDLE or BUSY (based on our internal state)
                if bot.status == BotStatus.CRASHED:
                    logger.info(f"✅ Bot {port} recovered from crash, setting to IDLE.")
                    bot.status = BotStatus.IDLE
                
                # Check wrap-up time
                now = time.time()
                if bot.wrap_up_end_time and now >= bot.wrap_up_end_time:
                    bot.wrap_up_end_time = None
                    if bot.status == BotStatus.BUSY and not bot.current_call_uuid:
                        bot.status = BotStatus.IDLE
                        logger.debug(f"🔓 Bot {bot.port} wrap-up complete, now IDLE")

    async def _restart_bot(self, port: int):
        """Restart a crashed bot container via Docker utility."""
        logger.warning(f"🔄 Attempting to restart crashed bot {port}...")
        # Use AVRBotManager to restart the Docker container
        success = self.docker_manager.restart_bot(port)
        
        if success:
            logger.info(f"✅ Bot {port} Docker container restarted successfully.")
            # Give it a moment to start up before marking IDLE
            await asyncio.sleep(5) 
            bot = self.bots.get(port)
            if bot:
                bot.status = BotStatus.IDLE
        else:
            logger.error(f"❌ Failed to restart bot {port} Docker container.")
            
    def get_total_instances(self) -> int:
        """Get the total number of bot instances configured."""
        return self.num_instances

    def get_all_bot_ports(self) -> List[int]:
        """Get a list of all bot ports managed by the pool."""
        return list(self.bots.keys())

    async def get_idle_bot_port(self, call_uuid: str) -> Optional[int]:
        """Get an idle bot port using round-robin assignment.

        Args:
            call_uuid: Unique call identifier for tracking

        Returns:
            Port number of assigned bot, or None if all busy/crashed
        """
        async with self._lock:
            # Ensure wrap-up times are checked before assignment
            await self.check_health() 
            
            # Find truly available bots (IDLE and not CRASHED)
            available_bots = [
                bot for bot in self.bots.values()
                if bot.status == BotStatus.IDLE and bot.wrap_up_end_time is None
            ]

            if not available_bots:
                logger.warning("⚠️  No idle bots available (all busy, crashed, or in wrap-up)!")
                return None

            # Round-robin selection
            selected_bot = available_bots[self._next_bot_index % len(available_bots)]
            self._next_bot_index += 1

            # Mark busy
            selected_bot.status = BotStatus.BUSY
            selected_bot.current_call_uuid = call_uuid
            selected_bot.busy_since = time.time()

            logger.info(f"📞 POOL: Bot {selected_bot.port} ATOMICALLY assigned to call {call_uuid}")
            return selected_bot.port

    async def mark_bot_idle(self, port: int):
        """Mark a bot as idle with wrap-up time.

        Args:
            port: Bot port number
        """
        if port not in self.bots:
            logger.error(f"❌ Attempted to mark unknown bot {port} as idle")
            return

        bot = self.bots[port]
        # Only mark idle if not crashed
        if bot.status != BotStatus.CRASHED:
            bot.current_call_uuid = None
            bot.wrap_up_end_time = time.time() + self.wrap_up_time
            bot.status = BotStatus.IDLE # Set to IDLE immediately, wrap-up check handles availability
            logger.info(f"🔒 Bot {port} entering {self.wrap_up_time}s wrap-up period")
        else:
            logger.warning(f"⚠️ Bot {port} is CRASHED, skipping mark_bot_idle.")

    def get_pool_stats(self) -> dict:
        """Get current pool statistics.

        Returns:
            Dict with bot counts by status
        """
        now = time.time()
        
        # Recalculate availability based on wrap-up time
        idle_count = sum(
            1 for bot in self.bots.values()
            if bot.status == BotStatus.IDLE and (not bot.wrap_up_end_time or now >= bot.wrap_up_end_time)
        )
        busy_count = sum(
            1 for bot in self.bots.values()
            if bot.status == BotStatus.BUSY
        )
        crashed_count = sum(
            1 for bot in self.bots.values()
            if bot.status == BotStatus.CRASHED
        )
        wrap_up_count = sum(
            1 for bot in self.bots.values()
            if bot.status == BotStatus.IDLE and bot.wrap_up_end_time and now < bot.wrap_up_end_time
        )

        return {
            "total": len(self.bots),
            "idle": idle_count,
            "busy": busy_count,
            "crashed": crashed_count,
            "wrap_up": wrap_up_count,
            "base_port": self.base_port,
            "wrap_up_time": self.wrap_up_time
        }

    def get_bot_status(self, port: int) -> Optional[BotStatus]:
        """Get status of a specific bot."""
        bot = self.bots.get(port)
        return bot.status if bot else None

    def is_available(self, port: int) -> bool:
        """Check if a bot is available (not busy, not in wrap-up, not crashed)."""
        bot = self.bots.get(port)
        if not bot:
            return False

        now = time.time()
        in_wrap_up = bot.wrap_up_end_time and now < bot.wrap_up_end_time
        return bot.status == BotStatus.IDLE and not in_wrap_up and bot.status != BotStatus.CRASHED

# Alias for drop-in compatibility with dialer_orchestrator
BotPoolManager = AVRBotPoolManager
