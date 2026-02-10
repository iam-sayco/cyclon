"""Process management service for Cyclon application."""

import asyncio
import select
import signal
import time
from collections.abc import Callable
from typing import Any

from ptyprocess import PtyProcessUnicode  # type: ignore[import-untyped]

from cyclon.constants import PROCESS_TERMINATION_DELAY
from cyclon.exceptions import ProcessError
from cyclon.validation import validate_list, validate_positive_int, validate_string


class ProcessService:
    """Service for managing process operations with PTY support.

    This service handles process execution with pseudo-terminal (PTY) support,
    allowing for interactive command execution and real-time output capture.

    Attributes:
        current_pty: Currently running PTY process
        should_stop_processing: Flag to signal process termination
        _terminal_widget: Widget for displaying terminal output
        _write_callback: Callback for writing data to process
        _pty_changed_callback: Callback for PTY state changes

    Example:
        >>> service = ProcessService()
        >>> returncode, output = await service.run_provider_process(
        ...     ["python", "script.py"], timeout=60
        ... )
    """

    def __init__(self) -> None:
        """Initialize the process service."""
        self.current_pty: PtyProcessUnicode | None = None
        self.should_stop_processing = False
        self._terminal_widget: Any | None = None
        self._write_callback: Callable[[str], None] | None = None
        self._pty_changed_callback: Callable[[], None] | None = None

    def set_terminal_widget(self, widget: Any) -> None:
        """Set the terminal widget for output display.

        Args:
            widget: Widget that supports write() method for output display
        """
        self._terminal_widget = widget

    def set_pty_changed_callback(self, callback: Callable[[], None]) -> None:
        """Set callback to notify when PTY changes.

        Args:
            callback: Function to call when PTY state changes
        """
        self._pty_changed_callback = callback

    def check_exception(self, stderr_output: str, exception_strings: list[str]) -> bool:
        """Check if stderr output contains any exception strings.

        Args:
            stderr_output: Output from stderr to check
            exception_strings: List of exception strings to look for

        Returns:
            bool: True if any exception string is found in output
        """
        return any(exc_str.strip() in stderr_output for exc_str in exception_strings)

    async def run_provider_process(  # noqa: PLR0915
        self,
        command: list[str],
        timeout: int,
        output_callback: Callable[[str], None] | None = None,
    ) -> tuple[int, str]:
        """Run provider process with PTY support.

        Executes a command with PTY support for interactive sessions and
        captures output in real-time.

        Args:
            command: Command to execute as list of arguments
            timeout: Maximum execution time in seconds
            output_callback: Optional callback for real-time error output

        Returns:
            Tuple[int, str]: Return code and captured output

        Raises:
            ValueError: If command is empty or has invalid arguments
            ProcessError: If there's an error running the process
        """
        validate_list(command, "command", item_type=str, min_length=1)
        validate_positive_int(timeout, "timeout")

        output_buffer: list[str] = []
        returncode = 0

        def read_pty_output(pty_proc: PtyProcessUnicode) -> str:
            """Read output from PTY process."""
            try:
                fd = pty_proc.fd
                rlist, _, _ = select.select([fd], [], [], 0.05)
                if rlist:
                    result: str = pty_proc.read(1024)
                    return result
                return ""
            except (EOFError, OSError):
                return ""

        async def read_pty() -> int:
            """Read PTY output asynchronously."""
            while True:
                if self.should_stop_processing or self.current_pty is None:
                    try:
                        if self.current_pty and not self.current_pty.isalive():
                            break
                        elif self.current_pty:
                            self.current_pty.terminate()
                    except Exception:
                        pass
                    return -1

                try:
                    pty = self.current_pty
                    if not pty:
                        break
                    data = await asyncio.to_thread(read_pty_output, pty)
                    if not data:
                        if not self.current_pty or not self.current_pty.isalive():
                            break
                        continue

                    output_buffer.append(data)

                    if self._terminal_widget:
                        self._terminal_widget.write(data)

                except (EOFError, OSError):
                    break

            return 0

        try:
            self.current_pty = PtyProcessUnicode.spawn(command, echo=False)
            self.should_stop_processing = False

            if self._pty_changed_callback:
                self._pty_changed_callback()

            if self._terminal_widget and hasattr(self._terminal_widget, "set_write_callback"):

                def pty_write_callback(data: str) -> None:
                    if self.current_pty and self.current_pty.isalive():
                        self.current_pty.write(data)

                self._terminal_widget.set_write_callback(pty_write_callback)
                self._write_callback = pty_write_callback

            await read_pty()

            returncode = self.current_pty.wait() or 0 if self.current_pty else 0
            self.current_pty = None

            if self._pty_changed_callback:
                self._pty_changed_callback()

            if self._terminal_widget and hasattr(self._terminal_widget, "set_write_callback"):
                self._terminal_widget.set_write_callback(None)
                self._write_callback = None

        except FileNotFoundError:
            error_msg = (
                "[red]Provider command not found. Ensure provider is installed and in PATH.[/red]\n"
            )
            if output_callback:
                output_callback(error_msg)
            returncode = -1
        except ProcessError as e:
            error_msg = f"[red]Process error: {e}[/red]\n"
            if output_callback:
                output_callback(error_msg)
            returncode = -1
        except Exception as e:
            error_msg = f"[red]Error: {e}[/red]\n"
            if output_callback:
                output_callback(error_msg)
            returncode = -1

        return returncode, "".join(output_buffer)

    def stop_process(self) -> None:
        """Stop the current process gracefully or forcefully.

        First attempts graceful termination, then force kills if necessary.

        Raises:
            ProcessError: If there's an error stopping the process
        """
        if not self.current_pty:
            return

        self.should_stop_processing = True

        try:
            if self.current_pty.isalive():
                self.current_pty.terminate()

                # Give it a moment to terminate gracefully
                time.sleep(PROCESS_TERMINATION_DELAY)

                if self.current_pty.isalive():
                    self.current_pty.kill(signal.SIGKILL)
        except Exception:
            try:
                if self.current_pty and self.current_pty.isalive():
                    self.current_pty.kill(signal.SIGKILL)
            except Exception:
                pass
        finally:
            self.current_pty = None
            self.should_stop_processing = False

            if self._pty_changed_callback:
                self._pty_changed_callback()

            if self._terminal_widget and hasattr(self._terminal_widget, "set_write_callback"):
                self._terminal_widget.set_write_callback(None)
                self._write_callback = None

    def write_to_process(self, text: str) -> None:
        """Write text to the current process.

        Args:
            text: Text to write to the process

        Raises:
            ValueError: If text is None or not a string
            ProcessError: If there's an error writing to the process
        """
        validate_string(text, "text", allow_empty=True)

        if self.current_pty and self.current_pty.isalive() and text:
            try:
                self.current_pty.write(text + "\n")
            except OSError as e:
                raise ProcessError(f"Error writing to process: {e}") from e

    def is_process_running(self) -> bool:
        """Check if a process is currently running.

        Returns:
            bool: True if a process is running, False otherwise
        """
        return self.current_pty is not None and self.current_pty.isalive()

    def get_process_pid(self) -> int | None:
        """Get the PID of the current process.

        Returns:
            Optional[int]: Process PID or None if no process is running
        """
        if self.current_pty:
            pid: int = self.current_pty.pid
            return pid
        return None
