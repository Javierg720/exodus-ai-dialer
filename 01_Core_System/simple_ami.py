"""Simple Asterisk Manager Interface (AMI) Client - Uses blocking sockets (proven to work) with asyncio.to_thread()"""

import asyncio
import socket
import threading
from typing import Dict, Callable, Optional, Any
from loguru import logger


class SimpleAMIManager:
    """Blocking AMI client (like test_ami.py that works) wrapped for async."""

    def __init__(self, host: str, port: int, username: str, secret: str):
        self.host = host
        self.port = port
        self.username = username
        self.secret = secret

        self._socket: Optional[socket.socket] = None
        self._event_handlers: Dict[str, list[Callable]] = {}
        self._listen_thread: Optional[threading.Thread] = None
        self._connected = False
        self._action_id = 0
        self._lock = threading.Lock()

        # Queue for action responses (keyed by ActionID)
        self._pending_actions: Dict[str, asyncio.Future] = {}
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def register_event(self, event_name: str, handler: Callable):
        """Register a callback for an AMI event."""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
        logger.debug(f"Registered handler for event: {event_name}")

    async def connect(self):
        """Connect to Asterisk AMI and login."""
        # Store event loop for callbacks
        self._event_loop = asyncio.get_event_loop()

        # Do blocking connection in thread
        await asyncio.to_thread(self._blocking_connect)

    def _blocking_connect(self):
        """Blocking connection (like test_ami.py that works)."""
        try:
            # Create socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((self.host, self.port))

            # Read welcome banner
            welcome = self._socket.recv(1024).decode()
            logger.debug(f"AMI banner: {welcome.strip()}")

            # Send login
            login_cmd = (
                f"Action: Login\r\n"
                f"Username: {self.username}\r\n"
                f"Secret: {self.secret}\r\n"
                f"\r\n"
            )
            self._socket.sendall(login_cmd.encode())

            # Read login response
            response = self._read_response_blocking()

            if response.get("Response") != "Success":
                raise Exception(f"AMI login failed: {response}")

            logger.info(f"✅ AMI connected to {self.host}:{self.port}")
            self._connected = True

            # Start listening thread
            self._listen_thread = threading.Thread(
                target=self._listen_for_events_blocking, daemon=True
            )
            self._listen_thread.start()

        except Exception as e:
            logger.error(f"❌ AMI connection failed: {e}")
            raise

    def _read_response_blocking(self) -> Dict[str, str]:
        """Read a single AMI response (blocking, like test_ami.py)."""
        buffer = b""

        # Read until we get a complete message (ending with \r\n\r\n)
        while b"\r\n\r\n" not in buffer:
            chunk = self._socket.recv(4096)
            if not chunk:
                break
            buffer += chunk

        # Parse the message
        response = {}
        message_str = buffer.split(b"\r\n\r\n")[0].decode()

        for line in message_str.split("\r\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                response[key] = value

        return response

    def _listen_for_events_blocking(self):
        """Background thread that listens for ALL AMI messages (blocking)."""
        logger.info("👂 AMI event listener started")

        try:
            buffer = b""
            while self._connected:
                try:
                    # Read data (may timeout - that's OK, just continue)
                    chunk = self._socket.recv(4096)
                    if not chunk:
                        break
                except socket.timeout:
                    # Socket timeout is normal - just means no data available
                    continue

                buffer += chunk

                # Process complete messages (separated by \r\n\r\n)
                while b"\r\n\r\n" in buffer:
                    message_bytes, buffer = buffer.split(b"\r\n\r\n", 1)

                    # Parse message
                    message = {}
                    for line in message_bytes.decode().split("\r\n"):
                        if ": " in line:
                            key, value = line.split(": ", 1)
                            message[key] = value

                    if not message:
                        continue

                    # Check if this is a response to an action (has ActionID)
                    action_id = message.get("ActionID")
                    if action_id and action_id in self._pending_actions:
                        # Deliver response to waiting send_action() call
                        future = self._pending_actions.pop(action_id)
                        if not future.done():
                            # Schedule future completion in event loop
                            self._event_loop.call_soon_threadsafe(
                                future.set_result, message
                            )
                        continue

                    # Check if this is an event (has "Event:" field)
                    event_name = message.get("Event")
                    if event_name:
                        # Log all events for debugging
                        logger.debug(f"📥 AMI Event: {event_name}")

                        if event_name in self._event_handlers:
                            # Call all registered handlers for this event
                            for handler in self._event_handlers[event_name]:
                                try:
                                    # Schedule handler in event loop - DON'T block the listener thread
                                    # Store future so it completes even if we don't wait
                                    future = asyncio.run_coroutine_threadsafe(
                                        handler(self, message), self._event_loop
                                    )

                                    # Add callback to log completion/errors
                                    def _on_complete(f):
                                        try:
                                            f.result()  # Re-raise any exceptions
                                        except Exception as e:
                                            logger.error(
                                                f"Error in async event handler for {event_name}: {e}",
                                                exc_info=True,
                                            )

                                    future.add_done_callback(_on_complete)
                                except Exception as e:
                                    logger.error(
                                        f"Error scheduling event handler for {event_name}: {e}",
                                        exc_info=True,
                                    )

        except Exception as e:
            logger.error(f"❌ AMI event listener error: {e}")
            self._connected = False

    async def send_action(
        self, action: Dict[str, Any], timeout: float = 5.0
    ) -> Dict[str, str]:
        """Send an AMI action and wait for response."""
        # Create future in current event loop
        future = asyncio.Future()

        # Do blocking send in thread
        await asyncio.to_thread(self._blocking_send_action, action, future)

        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"⏱️ AMI action timeout: {action.get('Action')}")
            raise

    async def send_action_with_events(
        self, action: Dict[str, Any], event_name: str, complete_event: str, timeout: float = 10.0
    ) -> tuple[Dict[str, str], list[Dict[str, str]]]:
        """Send an AMI action and collect events until complete event is received.

        Used for actions like CoreShowChannels that return multiple events.

        Args:
            action: The AMI action dictionary
            event_name: The event type to collect (e.g., "CoreShowChannel")
            complete_event: The event that signals completion (e.g., "CoreShowChannelsComplete")
            timeout: Maximum time to wait for all events

        Returns:
            Tuple of (initial_response, list_of_events)
        """
        # Generate unique ActionID for this request
        self._action_id += 1
        action_id = f"action-{self._action_id}"
        action["ActionID"] = action_id

        events = []
        events_complete = asyncio.Event()

        # Temporary handler to collect events with matching ActionID
        async def collect_event(manager, event: Dict[str, str]):
            if event.get("ActionID") == action_id:
                if event.get("Event") == complete_event:
                    events_complete.set()
                elif event.get("Event") == event_name:
                    events.append(event)

        # Register temporary handlers
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        if complete_event not in self._event_handlers:
            self._event_handlers[complete_event] = []

        self._event_handlers[event_name].append(collect_event)
        self._event_handlers[complete_event].append(collect_event)

        try:
            # Send the action and get initial response
            response = await self.send_action(action, timeout=timeout)

            if response.get("Response") != "Success":
                return response, []

            # Wait for all events to be collected
            try:
                await asyncio.wait_for(events_complete.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ Timeout waiting for {complete_event}, collected {len(events)} events")

            return response, events

        finally:
            # Clean up temporary handlers
            if collect_event in self._event_handlers.get(event_name, []):
                self._event_handlers[event_name].remove(collect_event)
            if collect_event in self._event_handlers.get(complete_event, []):
                self._event_handlers[complete_event].remove(collect_event)

    def _blocking_send_action(self, action: Dict[str, Any], future: asyncio.Future):
        """Send action (blocking, like test_ami.py that works)."""
        with self._lock:
            # Use provided ActionID or generate unique one
            if "ActionID" in action:
                action_id = action["ActionID"]
            else:
                self._action_id += 1
                action_id = f"action-{self._action_id}"

            # Register future
            self._pending_actions[action_id] = future

            # Build action string
            action_str = f"ActionID: {action_id}\r\n"

            for key, value in action.items():
                if key == "ActionID":
                    continue  # Already added above
                if key == "Variable" and isinstance(value, list):
                    # Handle Variable as list
                    for var in value:
                        action_str += f"Variable: {var}\r\n"
                else:
                    action_str += f"{key}: {value}\r\n"

            action_str += "\r\n"

            # Send action (blocking)
            logger.debug(
                f"📤 Sending AMI action: {action.get('Action')} (ID: {action_id})"
            )
            logger.debug(f"📤 Full AMI command:\n{action_str}")

            self._socket.sendall(action_str.encode())

            logger.debug(f"📤 Command sent via sendall")

    async def close(self):
        """Close the AMI connection."""
        await asyncio.to_thread(self._blocking_close)

    def _blocking_close(self):
        """Close connection (blocking)."""
        logger.info("Closing AMI connection...")
        self._connected = False

        if self._socket:
            try:
                logoff_cmd = "Action: Logoff\r\n\r\n"
                self._socket.sendall(logoff_cmd.encode())
            except:
                pass

            self._socket.close()

        if self._listen_thread:
            self._listen_thread.join(timeout=2)

        logger.info("✅ AMI connection closed")


# Backwards compatibility alias
Manager = SimpleAMIManager
