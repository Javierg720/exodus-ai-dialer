"""
Bot Pool Interface - Abstract Base Class for all Bot Pool Managers.

All concrete implementations (Pipecat, AVR Docker, etc.) must inherit from this
interface to ensure compatibility with the Dialer Orchestrator.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from enum import Enum


class BotStatus(Enum):
    """Bot instance status."""
    STARTING = "starting"
    IDLE = "idle"
    BUSY = "busy"
    CRASHED = "crashed"
    STOPPED = "stopped"
    STOPPING = "stopping"


class BotPoolInterface(ABC):
    """Abstract interface for managing a pool of bots."""

    @abstractmethod
    async def start(self):
        """Initialize and start the bot pool (e.g., spawn processes or start monitoring)."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop all bots and cleanup resources."""
        pass

    @abstractmethod
    async def get_idle_bot_port(self, call_uuid: str) -> Optional[int]:
        """
        ATOMIC: Get an idle bot port and immediately mark it busy.
        
        Returns:
            Port number of assigned bot, or None if all busy/crashed.
        """
        pass

    @abstractmethod
    async def mark_bot_idle(self, port: int):
        """Mark a bot as idle (call ended), typically starting a wrap-up timer."""
        pass

    @abstractmethod
    def get_pool_stats(self) -> Dict:
        """Get current pool statistics (total, idle, busy, crashed)."""
        pass

    @abstractmethod
    def get_all_bot_ports(self) -> List[int]:
        """Get a list of all bot ports managed by the pool."""
        pass

    @abstractmethod
    def get_total_instances(self) -> int:
        """Get the total number of bot instances configured."""
        pass

    @abstractmethod
    async def check_health(self):
        """Perform a health check on all bots (e.g., check process/container status)."""
        pass
