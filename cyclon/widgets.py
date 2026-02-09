"""Custom Textual widgets for Cyclon."""

from textual.widgets import Input, Static, RadioSet, RadioButton, RichLog, TextArea
from textual.suggester import Suggester
from textual.events import Key
from rich.text import Text
from textual_autocomplete import AutoComplete
from textual_autocomplete._autocomplete import DropdownItem
from textual.content import Content
import pyte


class TopAlignedAutoComplete(AutoComplete):
    """AutoComplete widget with dropdown positioned above the input field.
    
    Extends Textual's AutoComplete to display suggestions above the target input
    rather than below, useful when the input is at the bottom of the screen.
    
    Attributes:
        target: The input widget to provide autocomplete for
        option_list: List of available autocomplete options
    """
    
    DEFAULT_CSS = """
    TopAlignedAutoComplete {
        width: 100%;
        padding: 1 0;
        border-left: solid #c94ae2;
        border-right: solid #c94ae2;
        border-top: none;
        border-bottom: none;
        layer: overlay;
    }
    
    TopAlignedAutoComplete AutoCompleteList {
        width: 100%;
        border: none;
    }
    
    TopAlignedAutoComplete AutoCompleteList .option-list--option {
        width: 100%;
        padding: 0 2;
    }
    
    TopAlignedAutoComplete AutoCompleteList .option-list--option-highlighted {
        background: #ed4aff;
        color: #1a0a1f;
    }
    """

    def _align_to_target(self) -> None:
        from textual.geometry import Region, Offset, Spacing
        
        target_region = self.target.region
        x = target_region.x
        y = target_region.y
        width, height = self.outer_size
        
        dropdown_y = y - height
        
        x, dropdown_y, _width, _height = Region(x, dropdown_y, width, height).constrain(
            "inside",
            "none",
            Spacing.all(0),
            self.screen.scrollable_content_region,
        )
        self.absolute_offset = Offset(x, dropdown_y)
    
    def _complete(self, option_index: int) -> None:
        from typing import cast
        
        if not self.display or self.option_list.option_count == 0:
            return

        option_list = self.option_list
        highlighted = option_index
        option = cast(DropdownItem, option_list.get_option_at_index(highlighted))
        
        main_content = option.main
        if hasattr(main_content, 'plain'):
            plain_text = main_content.plain
        else:
            plain_text = str(main_content)
        
        highlighted_value = plain_text.split()[0] if plain_text else ""
            
        with self.prevent(Input.Changed):
            self.apply_completion(highlighted_value, self._get_target_state())
        self.post_completion()


class CommandSuggester(Suggester):
    """Suggester for Cyclon slash commands.
    
    Provides command suggestions when user types "/" in the input field.
    
    Attributes:
        COMMANDS: List of available slash commands
    """

    COMMANDS = ["/plan", "/run", "/stop", "/prompt", "/clear", "/new-session", "/model", "/provider", "/help"]

    async def get_suggestion(self, value: str) -> str | None:
        if value.startswith("/"):
            for cmd in self.COMMANDS:
                if cmd.startswith(value) and cmd != value:
                    return cmd
        return None


class TerminalOutput(Static):
    """Terminal output widget with PTY (pseudo-terminal) support.

    Displays terminal output with ANSI escape sequence support using pyte library.
    Handles interactive terminal sessions with keyboard input forwarding.

    Attributes:
        _pty_screen: pyte Screen object for terminal emulation
        _pty_stream: pyte Stream for feeding terminal data
        _write_callback: Callback for forwarding keyboard input to PTY

    Example:
        >>> terminal = TerminalOutput()
        >>> terminal.write("Hello, World!")
        >>> terminal.set_write_callback(lambda data: process_input(data))
    """

    DEFAULT_CSS = """
    TerminalOutput {
        height: 1fr;
        width: 1fr;
        background: transparent;
        content-align: left top;
        padding: 0;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
        scrollbar-background: #1a0a1f;
        scrollbar-color: white;
        scrollbar-background-hover: #1a0a1f;
        scrollbar-color-hover: #ed4aff;
        scrollbar-background-active: #1a0a1f;
        scrollbar-color-active: #ed4aff;
        border: none;
    }
    TerminalOutput:focus {
        border: none;
    }
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pty_screen = pyte.Screen(80, 24)
        self._pty_stream = pyte.Stream(self._pty_screen)
        self._write_callback = None
    
    def set_write_callback(self, callback):
        """Set callback for forwarding keyboard input to PTY process.

        Args:
            callback: Function to call when keyboard input should be sent to PTY
        """
        self._write_callback = callback

    def write(self, data: str):
        """Write data to the terminal screen.

        Feeds data to the pyte stream and renders the updated screen.
        Handles both string and bytes input.

        Args:
            data: String or bytes to write to terminal
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8', errors='replace')
        self._pty_stream.feed(data)
        self._render_screen()

    def _render_screen(self):
        """Render the current PTY screen content to the widget."""
        lines = []
        for line in self._pty_screen.display:
            lines.append(line.rstrip())
        content = '\n'.join(lines)

        text = Text()
        text.append(content, style="white")
        self.update(text)

    def clear(self):
        """Clear the terminal screen and reset PTY state."""
        self._pty_screen.reset()
        self._render_screen()

    def write_line(self, text: str, style: str = "white"):
        """Write a line of text with newline characters.

        Args:
            text: Text to write
            style: Style to apply (currently ignored, for future use)
        """
        plain_text = f"\n{text}\n"
        self._pty_stream.feed(plain_text)
        self._render_screen()

    def on_key(self, event: Key) -> None:
        """Handle keyboard input and forward to PTY process if active.

        Maps special keys to ANSI escape sequences and forwards them
        to the PTY process via the write callback.

        Args:
            event: Key event from Textual
        """
        if self._write_callback:
            key_mapping = {
                "up": "\x1b[A",
                "down": "\x1b[B",
                "right": "\x1b[C",
                "left": "\x1b[D",
                "enter": "\r",
                "tab": "\t",
                "home": "\x1b[H",
                "end": "\x1b[F",
                "pageup": "\x1b[5~",
                "pagedown": "\x1b[6~",
                "delete": "\x1b[3~",
                "backspace": "\x7f",
                "escape": "\x1b",
            }
            
            key_char = event.key
            if key_char in key_mapping:
                key_char = key_mapping[key_char]
            
            self._write_callback(key_char)
            event.stop()
    
    def on_mouse_scroll_up(self, event) -> None:
        pass
    
    def on_mouse_scroll_down(self, event) -> None:
        pass


class StatusIndicator(Static):
    """Status indicator widget showing current provider and model.

    Displays the configured AI provider and model in the header bar.
    Reads configuration from .cyclon/config.json.

    Example:
        >>> indicator = StatusIndicator()
        >>> indicator.update_status()  # Refreshes from config file
    """

    DEFAULT_CSS = """
    StatusIndicator {
        width: auto;
        height: auto;
        background: #ed4aff;
        color: #1a0a1f;
        padding: 0 2;
        text-align: right;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_status()

    def update_status(self):
        """Update the status display from configuration file.

        Reads .cyclon/config.json and displays the configured provider
        and model in the format "provider / model".
        """
        import json
        from pathlib import Path
        
        config_file = Path.cwd() / ".cyclon" / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            provider = config.get("provider", "N/A")
            model = config.get("model", "N/A")
        else:
            provider = "N/A"
            model = "N/A"
        
        self.update(f"[b]{provider}[/b] / {model}")


class Throbber(Static):
    """Animated throbber widget indicating processing activity.

    Displays a spinning animation using Unicode braille patterns.
    Can be activated/deactivated to show/hide the animation.

    Attributes:
        frames: List of animation frames (Unicode characters)
        frame: Current frame index
        active: Whether animation is currently active

    Example:
        >>> throbber = Throbber()
        >>> throbber.set_active(True)  # Start animation
        >>> throbber.advance_frame()   # Advance to next frame
    """

    DEFAULT_CSS = """
    Throbber {
        width: auto;
        height: auto;
        padding: 0 1;
        text-align: left;
    }
    """

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame = 0
    active = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update("")

    def set_active(self, is_active: bool):
        """Activate or deactivate the throbber animation.

        Args:
            is_active: True to show animation, False to hide
        """
        self.active = is_active
        self.update_throbber()

    def advance_frame(self):
        """Advance to the next frame of the animation."""
        self.frame = (self.frame + 1) % len(self.frames)
        self.update_throbber()

    def update_throbber(self):
        """Update the displayed throbber based on active state."""
        if self.active:
            self.update(self.frames[self.frame])
        else:
            self.update("")


class ProcessStatus(Static):
    """Process status widget showing execution state.

    Displays status messages indicating whether a process is running
    or idle. Updates based on process state changes.

    Attributes:
        running_state: Whether a process is currently running
        pty_mode: Whether in PTY interactive mode

    Example:
        >>> status = ProcessStatus()
        >>> status.set_running(True)   # Shows running message
        >>> status.set_running(False)  # Shows idle message
    """

    DEFAULT_CSS = """
    ProcessStatus {
        width: auto;
        height: auto;
        padding: 0 1;
        text-align: left;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running_state = False
        self.pty_mode = False
        self.update("[#999999]🌀 the calm before the storm... type /run to unleash the real power[/#999999]")

    def set_running(self, running: bool):
        """Set the running state and update status display.

        Args:
            running: True if process is running, False otherwise
        """
        self.running_state = running
        self.update_status()

    def set_pty_mode(self, pty_mode: bool):
        """Set the PTY mode state.

        Args:
            pty_mode: True if in PTY interactive mode
        """
        self.pty_mode = pty_mode
        self.update_status()

    def update_status(self):
        """Update the status message based on current state."""
        if self.running_state:
            self.update("[#00ff88]🌪️  winds picking up... /stop to calm the vortex[/#00ff88]")
        else:
            self.update("[#999999]🌀 the calm before the storm... type /run to unleash the real power[/#999999]")

    def get_running_state(self) -> bool:
        """Get the current running state.

        Returns:
            True if a process is currently running
        """
        return self.running_state


class PromptInput(Input):
    """Input widget with command suggestion support.

    Extends Textual's Input widget with CommandSuggester for slash command
    autocomplete functionality.

    Example:
        >>> input_widget = PromptInput()
        >>> # User types "/" and gets command suggestions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, placeholder="Type /plan <your request> to generate a plan, or /help for commands", suggester=CommandSuggester(), **kwargs)
