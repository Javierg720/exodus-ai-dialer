"""
AVR Bot Manager - Manages Docker-based AVR bot containers
"""

import subprocess
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class AVRBotManager:
    """Manages AVR Docker bot containers (ports 9092-9111)"""

    def __init__(self):
        self.bot_ports = list(range(9092, 9102))  # 10 bots: 9092-9101

    def get_running_bots(self) -> List[Dict]:
        """Get status of all AVR bot containers

        Returns:
            List of bot status dictionaries
        """
        bots = []

        for port in self.bot_ports:
            container_name = f"avr-bot-{port}"
            try:
                # Check if container exists and get its status
                result = subprocess.run(
                    ["docker", "inspect", container_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    container_info = json.loads(result.stdout)[0]
                    state = container_info["State"]

                    status = "STOPPED"
                    if state["Running"]:
                        status = "RUNNING"
                    elif state["Restarting"]:
                        status = "RESTARTING"
                    elif state["Dead"]:
                        status = "CRASHED"
                    elif state["ExitCode"] != 0:
                        status = "EXITED"

                    bots.append(
                        {
                            "port": port,
                            "running": state["Running"],
                            "status": status,
                            "started_at": state.get("StartedAt", ""),
                            "finished_at": state.get("FinishedAt", ""),
                            "exit_code": state.get("ExitCode", 0),
                            "pid": state.get("Pid", 0),
                        }
                    )
                else:
                    # Container doesn't exist
                    bots.append(
                        {
                            "port": port,
                            "running": False,
                            "status": "NOT_FOUND",
                            "started_at": None,
                            "finished_at": None,
                            "exit_code": None,
                            "pid": None,
                        }
                    )

            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout checking container {container_name}")
                bots.append(
                    {
                        "port": port,
                        "running": False,
                        "status": "TIMEOUT",
                        "started_at": None,
                        "finished_at": None,
                        "exit_code": None,
                        "pid": None,
                    }
                )
            except Exception as e:
                logger.error(f"Error checking container {container_name}: {e}")
                bots.append(
                    {
                        "port": port,
                        "running": False,
                        "status": "ERROR",
                        "started_at": None,
                        "finished_at": None,
                        "exit_code": None,
                        "pid": None,
                    }
                )

        return bots

    def restart_bot(self, port: int) -> bool:
        """Restart a specific bot container

        Args:
            port: Bot port number

        Returns:
            True if restart successful, False otherwise
        """
        container_name = f"avr-bot-{port}"
        try:
            result = subprocess.run(
                ["docker", "restart", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to restart {container_name}: {e}")
            return False

    def start_bot(self, port: int) -> bool:
        """Start a specific bot container

        Args:
            port: Bot port number

        Returns:
            True if start successful, False otherwise
        """
        container_name = f"avr-bot-{port}"
        try:
            result = subprocess.run(
                ["docker", "start", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to start {container_name}: {e}")
            return False

    def stop_bot(self, port: int) -> bool:
        """Stop a specific bot container

        Args:
            port: Bot port number

        Returns:
            True if stop successful, False otherwise
        """
        container_name = f"avr-bot-{port}"
        try:
            result = subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to stop {container_name}: {e}")
            return False

    def stop_all_bots(self) -> Dict:
        """Stop all bot containers in parallel

        Returns:
            Dictionary with 'success' and 'failed' port lists
        """
        import concurrent.futures

        results = {"success": [], "failed": []}

        def stop_single_bot(port):
            return port, self.stop_bot(port)

        # Stop all bots in parallel with max 10 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(stop_single_bot, port) for port in self.bot_ports
            ]

            for future in concurrent.futures.as_completed(futures, timeout=35):
                try:
                    port, success = future.result()
                    if success:
                        results["success"].append(port)
                    else:
                        results["failed"].append(port)
                except Exception as e:
                    logger.error(f"Error stopping bot: {e}")

        return results

    def start_all_bots(self) -> Dict:
        """Start all bot containers in parallel

        Returns:
            Dictionary with 'success' and 'failed' port lists
        """
        import concurrent.futures

        results = {"success": [], "failed": []}

        def start_single_bot(port):
            return port, self.start_bot(port)

        # Start all bots in parallel with max 10 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(start_single_bot, port) for port in self.bot_ports
            ]

            for future in concurrent.futures.as_completed(futures, timeout=35):
                try:
                    port, success = future.result()
                    if success:
                        results["success"].append(port)
                    else:
                        results["failed"].append(port)
                except Exception as e:
                    logger.error(f"Error starting bot: {e}")

        return results

    def restart_all_bots(self) -> Dict:
        """Restart all bot containers in parallel

        Returns:
            Dictionary with 'success' and 'failed' port lists
        """
        import concurrent.futures

        results = {"success": [], "failed": []}

        def restart_single_bot(port):
            return port, self.restart_bot(port)

        # Restart all bots in parallel with max 10 workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(restart_single_bot, port) for port in self.bot_ports
            ]

            for future in concurrent.futures.as_completed(futures, timeout=35):
                try:
                    port, success = future.result()
                    if success:
                        results["success"].append(port)
                    else:
                        results["failed"].append(port)
                except Exception as e:
                    logger.error(f"Error restarting bot: {e}")

        return results
