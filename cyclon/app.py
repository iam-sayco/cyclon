"""Main Cyclon application."""

import asyncio
import json

from ptyprocess import PtyProcessUnicode
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Input, RichLog, Static

from cyclon.constants import COMMANDS_LIST, VALID_COMMANDS
from cyclon.paths import (
    LOCAL_CONFIG_FILE,
    LOCAL_CYCLON_DIR,
    LOCAL_LOCK_FILE,
    LOCAL_PLAN_FILE,
    LOCAL_PROMPT_FILE,
)
from cyclon.screens import (
    CommandsModalScreen,
    FileModalScreen,
    ModelModalScreen,
    ProviderModalScreen,
)
from cyclon.services import ConfigService, FileService, ProcessService
from cyclon.state import AppState
from cyclon.validation import validate_string
from cyclon.widgets import (
    ProcessStatus,
    PromptInput,
    StatusIndicator,
    TerminalOutput,
    Throbber,
    TopAlignedAutoComplete,
)


class CyclonApp(App):
    """Main Cyclon application with dependency injection and centralized state management."""

    def __init__(
        self,
        config_service: ConfigService,
        file_service: FileService,
        process_service: ProcessService,
        app_state: AppState | None = None,
    ):
        super().__init__()
        self.config_service = config_service
        self.file_service = file_service
        self.process_service = process_service
        self.app_state = app_state or AppState()

        # Set up PTY change callback
        def pty_changed_callback():
            self.app_state.current_pty = self.process_service.current_pty

        self.process_service.set_pty_changed_callback(pty_changed_callback)

        # Set up state observers for UI updates
        self._setup_state_observers()

    CSS = """
    Screen {
        align: center middle;
    }
    .main-container {
        max-width: 100w;
        width: 90vw;
        height: 90vh;
        align: center middle;
    }

    .header-bar {
        width: 100%;
        height: auto;
    }

    .output-grid {
        border: solid #ed4aff;
        height: 70%;
        width: 100%;
        margin-bottom: 0;
        margin-top: 1;
    }
    .log-column {
        width: 50%;
        height: 100%;
        border-right: solid #ed4aff;
        padding: 1 2;
    }
    .terminal-column {
        width: 50%;
        height: 100%;
        padding: 1 1 1 1;
    }
    #log-header, #terminal-header {
        padding-bottom: 1;
    }
    .log-box {
        height: 100%;
        width: 100%;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
        scrollbar-background: #2a1530;
        scrollbar-color: white;
        scrollbar-background-hover: #2a1530;
        scrollbar-color-hover: #ed4aff;
        scrollbar-background-active: #2a1530;
        scrollbar-color-active: #ed4aff;
        background: transparent;
    }
    .log-box RichLog {
        background: transparent;
        scrollbar-size-vertical: 1;
        scrollbar-background: transparent;
        scrollbar-color: white;
        scrollbar-background-hover: transparent;
        scrollbar-color-hover: #ed4aff;
        scrollbar-background-active: transparent;
        scrollbar-color-active: #ed4aff;
    }
    .terminal-box {
        height: 100%;
        width: 100%;
    }
    #status-indicator {
        width: auto;
        text-align: right;
        margin: 0;
        padding: 0 2;
    }
    .status-container {
        width: 100%;
        align: left top;
        height: auto;
        margin: 0;
        padding: 0;
    }

    .input-box {
        border: none;
        border-left: solid #ed4aff;
        height: 3;
        width: 100%;
        margin-top: 1;
        padding: 1 2;
    }
    .info-bar {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("f1", "show_commands", "Show Commands"),
        ("ctrl+q", "quit", "Exit"),
    ]

    def _setup_state_observers(self) -> None:
        """Set up observers to sync AppState changes with UI."""

        def on_pty_mode_changed(old_value: bool, new_value: bool) -> None:
            if hasattr(self, "process_status_ref") and self.process_status_ref:
                self.process_status_ref.set_pty_mode(new_value)

        def on_throbber_changed(old_value: bool, new_value: bool) -> None:
            if hasattr(self, "throbber_ref") and self.throbber_ref:
                self.throbber_ref.set_active(new_value)

        def on_process_running_changed(old_value: bool, new_value: bool) -> None:
            if hasattr(self, "process_status_ref") and self.process_status_ref:
                self.process_status_ref.set_running(new_value)

        self.app_state.add_pty_mode_observer(on_pty_mode_changed)
        self.app_state.add_throbber_observer(on_throbber_changed)
        self.app_state.add_process_running_observer(on_process_running_changed)

    @property
    def current_process(self) -> asyncio.subprocess.Process | None:
        """Get the current running process."""
        return self.app_state.current_process

    @current_process.setter
    def current_process(self, value: asyncio.subprocess.Process | None) -> None:
        """Set the current running process."""
        self.app_state.current_process = value

    @property
    def current_process_pid(self) -> int | None:
        """Get the PID of the current process."""
        return self.app_state.current_process_pid

    @property
    def current_pty(self) -> PtyProcessUnicode | None:
        """Get the current PTY process."""
        return self.app_state.current_pty

    @current_pty.setter
    def current_pty(self, value: PtyProcessUnicode | None) -> None:
        """Set the current PTY process."""
        self.app_state.current_pty = value

    @property
    def pty_mode(self) -> bool:
        """Get PTY mode status."""
        return self.app_state.pty_mode

    @pty_mode.setter
    def pty_mode(self, value: bool) -> None:
        """Set PTY mode status."""
        self.app_state.pty_mode = value

    @property
    def throbber_timer(self):
        """Get the throbber timer."""
        return self.app_state.throbber_timer

    @throbber_timer.setter
    def throbber_timer(self, value) -> None:
        """Set the throbber timer."""
        self.app_state.throbber_timer = value

    @property
    def should_stop_processing(self) -> bool:
        """Get flag indicating if processing should stop."""
        return self.app_state.should_stop_processing

    @should_stop_processing.setter
    def should_stop_processing(self, value: bool) -> None:
        """Set flag indicating if processing should stop."""
        self.app_state.should_stop_processing = value

    @property
    def throbber_ref(self):
        """Get reference to throbber widget."""
        return self.app_state.throbber_ref

    @throbber_ref.setter
    def throbber_ref(self, value) -> None:
        """Set reference to throbber widget."""
        self.app_state.throbber_ref = value

    @property
    def process_status_ref(self):
        """Get reference to process status widget."""
        return self.app_state.process_status_ref

    @process_status_ref.setter
    def process_status_ref(self, value) -> None:
        """Set reference to process status widget."""
        self.app_state.process_status_ref = value

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration and return status."""
        return self.config_service.validate_config()

    def get_status_message(self) -> str:
        """Get status message about current configuration."""
        return self.config_service.get_status_message()

    def load_providers(self):
        """Load available providers configuration."""
        return self.config_service.load_providers()

    def load_logo(self) -> str:
        """Load logo content from file."""
        return self.file_service.load_logo()

    def load_config(self) -> dict:
        """Load configuration from file."""
        return self.config_service.load_config()

    def save_plan(self, plan_content: str) -> None:
        """Save plan content to file."""
        self.file_service.save_plan(plan_content)

    def load_generate_prompt(self, user_prompt: str) -> str:
        """Load generation prompt template and substitute placeholders."""
        return self.file_service.load_generate_prompt(user_prompt)

    def check_exception(self, stderr_output: str) -> bool:
        """Check if stderr output contains any exception strings."""
        config = self.load_config()
        exception_strings = config.get("exceptionStrings", [])
        return self.process_service.check_exception(stderr_output, exception_strings)

    def animate_throbber(self):
        """Advance throbber to next frame."""
        if self.throbber_ref:
            self.throbber_ref.advance_frame()
            self.throbber_ref.refresh()

    async def generate_plan(self, user_prompt: str) -> None:
        """Generate a plan from user prompt using AI provider."""
        full_prompt = self.load_generate_prompt(user_prompt)
        command = self.config_service.build_command(prompt=full_prompt)

        if not command:
            self.append_output(
                "[red]Error: Could not build command. Check provider/model config.\n"
            )
            return

        self.append_output("\n[b yellow]Generating plan...[/b yellow]\n")

        self.throbber_ref = self.query_one("#throbber", Throbber)
        self.throbber_ref.set_active(True)
        self.process_status_ref = self.query_one("#process-status", ProcessStatus)
        self.process_status_ref.set_running(True)
        self.throbber_timer = self.set_interval(0.1, self.animate_throbber)

        terminal_widget = self.query_one("#terminal-output", TerminalOutput)
        self.process_service.set_terminal_widget(terminal_widget)

        try:
            returncode, output = await self.process_service.run_provider_process(command, 600)

            self.current_process = None

            if returncode == 0:
                self.append_output("\n[green]✓ Plan generation completed[/green]\n")
                self.append_output(
                    "Use [b]/plan[/b] to view or edit, then [b]/run[/b] to begin execution.\n"
                )
            else:
                self.append_output(
                    f"\n[red]Generation failed with return code {returncode}[/red]\n"
                )

        except FileNotFoundError:
            self.append_output(
                "[red]Provider command not found. Ensure provider is installed and in PATH.[/red]\n"
            )
        except Exception as e:
            self.append_output(f"[red]Error: {e}[/red]\n")
        finally:
            if self.throbber_timer:
                self.throbber_timer.stop()
            if self.throbber_ref:
                self.throbber_ref.set_active(False)
            if self.process_status_ref:
                self.process_status_ref.set_running(False)
            self.throbber_ref.refresh()
            self.process_status_ref.refresh()
            self.current_pty = self.process_service.current_pty
            self.pty_mode = self.process_service.current_pty is not None

    async def run_processing_loop(self) -> None:  # noqa: PLR0912, PLR0915
        """Run the main processing loop for plan execution."""
        config = self.load_config()
        sleep_duration = config.get("sleep", 10)
        timeout = config.get("timeout", 3600)
        lock_file = LOCAL_LOCK_FILE

        full_prompt = self.file_service.build_execution_prompt()
        command = self.config_service.build_command(prompt=full_prompt)

        if not command:
            self.append_output(
                "[red]Error: Could not build command. Check provider/model config.\n"
            )
            return

        self.throbber_ref = self.query_one("#throbber", Throbber)
        self.throbber_ref.set_active(True)
        self.process_status_ref = self.query_one("#process-status", ProcessStatus)
        self.process_status_ref.set_running(True)
        self.throbber_timer = self.set_interval(0.1, self.animate_throbber)

        self.append_output("\n[b yellow]Processing started...[/b yellow]\n")
        self.append_output("Provider command prepared (not shown). Running provider now.\n\n")

        self.should_stop_processing = False
        self.process_service.should_stop_processing = False

        terminal_widget = self.query_one("#terminal-output", TerminalOutput)
        self.process_service.set_terminal_widget(terminal_widget)

        while True:
            if self.should_stop_processing or not lock_file.exists():
                if self.should_stop_processing:
                    self.append_output("Processing stopped by user request.\n")
                else:
                    self.append_output("Lock file removed. Stopping loop.\n")
                break

            await asyncio.sleep(0.01)

            try:
                self.append_output(
                    "[bold yellow]→ Provider running — check Provider Output for "
                    "live logs[/bold yellow]\n"
                )

                returncode, output = await self.process_service.run_provider_process(
                    command, timeout
                )

                self.current_process = None

                if returncode != 0:
                    self.append_output(
                        f"[red]Provider failed with return code {returncode}[/red]\n"
                    )

                    if self.check_exception(output):
                        self.append_output(
                            f"[yellow]Exception matched, sleeping for {sleep_duration} "
                            "seconds...[/yellow]\n"
                        )
                        await asyncio.sleep(sleep_duration)
                        continue
                    else:
                        self.append_output("[red]Unmatched error, stopping.[/red]\n")
                        break
                else:
                    self.append_output("[green]Provider completed successfully.[/green]\n")
                    self.append_output("Iteration complete, proceeding to next.\n\n")
                    await asyncio.sleep(0.5)

            except FileNotFoundError:
                self.append_output(
                    "[red]Provider command not found. Ensure provider is installed "
                    "and in PATH.[/red]\n"
                )
                break
            except Exception as e:
                self.append_output(f"[red]Error: {e}[/red]\n")
                break

        if self.throbber_timer:
            self.throbber_timer.stop()
        if self.throbber_ref:
            self.throbber_ref.set_active(False)
        if self.process_status_ref:
            self.process_status_ref.set_running(False)
        self.append_output("\n[b]Processing finished.[/b]\n")
        self.throbber_ref.refresh()
        self.process_status_ref.refresh()

        self.file_service.remove_context_file()
        self.append_output("Removed context file.\n")

    def append_output(self, text: str) -> None:
        """Append text to the output log."""
        validate_string(text, "text", allow_empty=True)
        self.write_log(text)

    def write_log(self, text: str) -> None:
        """Write text to the application log widget."""
        validate_string(text, "text", allow_empty=True)
        self.query_one("#app-log", RichLog).write(text)

    def write_terminal(self, data: str) -> None:
        """Write data to the terminal output widget."""
        validate_string(data, "data", allow_empty=True)
        self.query_one("#terminal-output", TerminalOutput).write(data)

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        with Container(classes="main-container"):
            yield Static(self.load_logo(), classes="logo", id="logo")

            with Horizontal(classes="output-grid", id="output-grid"):
                with Vertical(classes="log-column"):
                    yield Static("[b]Actions[/b]", id="log-header")
                    with Container(classes="log-box", id="log-container"):
                        yield RichLog(
                            id="app-log",
                            wrap=True,
                            highlight=True,
                            auto_scroll=True,
                            markup=True,
                            max_lines=10000,
                        )

                with Vertical(classes="terminal-column"):
                    yield Static("[b]Provider Output[/b]", id="terminal-header")
                    terminal_widget = TerminalOutput(classes="terminal-box", id="terminal-output")
                    terminal_widget.can_focus = True
                    yield terminal_widget

            with Horizontal(classes="status-container"):
                yield StatusIndicator(id="status-indicator")
                yield Throbber(id="throbber")
                yield ProcessStatus(id="process-status")
            self.prompt_input = PromptInput(classes="input-box")
            yield self.prompt_input
            yield TopAlignedAutoComplete(self.prompt_input, candidates=COMMANDS_LIST)
            yield Static(
                "[b]F1[/b] - Commands | [b]Ctrl+Q[/b] - Exit", classes="info-bar", id="info-bar"
            )

    def _parse_command(self, text: str) -> tuple[str, str]:
        """Parse command text into command name and argument."""
        validate_string(text, "text", allow_empty=True)

        parts = text.split(None, 1)
        command = parts[0] if parts else ""
        argument = parts[1] if len(parts) > 1 else ""
        return command, argument

    def _validate_command_state(self, command: str) -> bool:
        """Validate if command can be executed in current state."""
        if command == "/run" and not LOCAL_PLAN_FILE.exists():
            self.append_output("\n[orange1]⚠ No plan found![/orange1]\n")
            self.append_output(
                "Generate a plan with your description or use [b]/plan[/b] to create one.\n\n"
            )
            return False
        elif (
            command == "/stop" and not self.current_process and not self.process_service.current_pty
        ):
            self.append_output("[yellow]No process is currently running.[/yellow]\n")
            return False
        return True

    def _execute_command(self, command: str, argument: str) -> None:  # noqa: PLR0912
        """Execute the given command with optional argument."""
        validate_string(command, "command")
        validate_string(argument, "argument", allow_empty=True)

        if not self._validate_command_state(command):
            return

        if command == "/stop":
            self.stop_processing()
        elif command == "/clear":
            self.query_one("#app-log", RichLog).clear()
            self.query_one("#terminal-output", TerminalOutput).clear()
        elif command == "/provider":
            self.push_screen(
                ProviderModalScreen(config_service=self.config_service),
                self.on_provider_modal_dismissed,
            )
        elif command == "/model":
            current_model = ""
            if LOCAL_CONFIG_FILE.exists():
                with open(LOCAL_CONFIG_FILE) as f:
                    config = json.load(f)
                    current_model = config.get("model", "")
            self.push_screen(
                ModelModalScreen(current_model=current_model), self.on_model_modal_dismissed
            )
        elif command == "/new-session":
            self.new_session()
        elif command == "/plan":
            if argument:
                asyncio.create_task(self.generate_plan(argument))
            else:
                self.push_screen(
                    FileModalScreen(
                        file_name="plan.md", modal_title="Edit Plan", file_service=self.file_service
                    ),
                    self.on_file_modal_dismissed,
                )
        elif command == "/prompt":
            self.push_screen(
                FileModalScreen(
                    file_name="prompt.md", modal_title="Edit Prompt", file_service=self.file_service
                ),
                self.on_file_modal_dismissed,
            )
        elif command == "/run":
            self.start_execution()
        elif command == "/help":
            self.action_show_commands()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission events."""
        if event.input != self.prompt_input:
            return

        text = event.value.strip()
        event.input.value = ""

        if not text.startswith("/"):
            self.append_output(
                f"[red]Error: Unknown command '{text}'. Commands must start with '/'. "
                "Type /help or press F1 for available commands.[/red]\n"
            )
            return

        command, argument = self._parse_command(text)

        if command not in VALID_COMMANDS:
            self.append_output(
                f"[red]Error: Unknown command '{command}'. "
                "Type /help or press F1 for available commands.[/red]\n"
            )
            return

        if argument:
            self.write_log(f"[dim]→ Executing: {command} with argument[/dim]\n")
        else:
            self.write_log(f"[dim]→ Executing: {command}[/dim]\n")

        self._execute_command(command, argument)

    def on_provider_modal_dismissed(self, result) -> None:
        """Handle provider modal dismissal."""
        if result and isinstance(result, dict):
            provider_id = result.get("provider_id")
            provider_label = result.get("provider_label")
            if provider_id:
                self.config_service.save_provider_config(provider_id)
                self.append_output(f"Provider set to: {provider_label}\n")
                self.query_one("#status-indicator", StatusIndicator).update_status()
        self.prompt_input.value = ""
        self.prompt_input.focus()

    def on_model_modal_dismissed(self, result) -> None:
        """Handle model modal dismissal."""
        if result and isinstance(result, dict):
            model = result.get("model")
            if model:
                self.config_service.save_model_config(model)
                self.append_output(f"Model set to: {model}\n")
                self.query_one("#status-indicator", StatusIndicator).update_status()
        self.prompt_input.value = ""
        self.prompt_input.focus()

    def on_file_modal_dismissed(self, result) -> None:
        """Handle file modal dismissal."""
        if result and isinstance(result, dict):
            file_name = result.get("file_name")
            content = result.get("content")
            if file_name and content is not None:
                self.file_service.save_file(file_name, content)
                self.append_output(f"[green]✓ {file_name} saved to .cyclon/{file_name}[/green]\n")
        self.prompt_input.value = ""
        self.prompt_input.focus()

    def action_show_commands(self) -> None:
        """Show the commands help modal."""
        self.push_screen(CommandsModalScreen())

    async def send_input_to_process(self) -> None:
        """Send input text to the running process."""
        if self.current_pty and self.current_pty.isalive():
            text = self.prompt_input.value
            if text:
                self.current_pty.write(text + "\n")
                self.prompt_input.value = ""

    def _prepare_execution(self, mode: str = "start") -> bool:
        """Prepare and validate execution state for both start and resume modes."""
        if not LOCAL_PLAN_FILE.exists():
            if mode == "resume":
                self.append_output("\n[orange1]⚠ No existing plan found.[/orange1]\n")
                self.append_output("Paste a new plan first.\n\n")
            else:
                self.append_output("\n[orange1]⚠ No plan found![/orange1]\n")
                self.append_output(
                    "Generate a plan with your description or use [b]/plan[/b] to create one.\n\n"
                )
            return False

        is_valid, missing = self.validate_config()
        if not is_valid:
            missing_str = " and ".join([f"/[b]{item}[/b]" for item in missing])
            self.append_output("\n[orange1]⚠ Configuration incomplete![/orange1]\n")
            action_word = "resuming" if mode == "resume" else "running"
            self.append_output(f"Please set {missing_str} before {action_word}.\n\n")
            return False

        with open(LOCAL_PLAN_FILE) as f:
            _ = f.read()

        if mode == "resume":
            self.append_output("\n[b yellow]Resuming session...[/b yellow]\n")
        else:
            self.append_output("\n[b green]Starting execution...[/b green]\n")

        self.append_output("Plan: .cyclon/plan.md loaded\n")
        if LOCAL_PROMPT_FILE.exists():
            self.append_output("Prompt: .cyclon/prompt.md loaded\n")

        lock_file = LOCAL_LOCK_FILE
        if lock_file.exists():
            self.append_output("Using existing lock file: .cyclon/process.lock\n")
        else:
            lock_file.touch()
            self.append_output("Created lock file: .cyclon/process.lock\n")

        context_file = LOCAL_CYCLON_DIR.parent / ".cyclon.context.md"
        if context_file.exists():
            self.append_output("Found context file: .cyclon.context.md (attached to provider)\n")

        self.append_output(
            "[yellow]Starting processing... (observe Provider Output for live logs)[/yellow]\n\n"
        )

        asyncio.create_task(self.run_processing_loop())
        return True

    def resume_processing(self) -> None:
        """Resume processing from existing plan."""
        self._prepare_execution(mode="resume")

    def start_execution(self) -> None:
        """Start execution of the current plan."""
        self._prepare_execution(mode="start")

    def new_session(self) -> None:
        """Start a new session by clearing all data."""
        self.query_one("#app-log", RichLog).clear()

        LOCAL_CYCLON_DIR.mkdir(exist_ok=True)
        self.file_service.clear_session()

        self.append_output("\n[b green]✓ New session started[/b green]\n")
        self.append_output("\n" + self.get_status_message())

    def stop_processing(self) -> None:
        """Stop the current processing and cleanup."""
        try:
            terminal_widget = self.query_one("#terminal-output", TerminalOutput)
            terminal_widget.write("\r\n" + "=" * 40 + "\r\n")
            terminal_widget.write("[STOP] Process killed by user\r\n")
            terminal_widget.write("=" * 40 + "\r\n")
        except Exception:
            pass
        self.append_output("[yellow]Stopping process...[/yellow]\n")

        self.should_stop_processing = True
        self.process_service.should_stop_processing = True

        self.process_service.stop_process()

        self.current_process = None

        self.file_service.remove_lock_file()
        self.append_output("Lock file removed.\n")

        if self.throbber_timer:
            self.throbber_timer.stop()
        if self.throbber_ref:
            self.throbber_ref.set_active(False)
        if self.process_status_ref:
            self.process_status_ref.set_running(False)

    def on_mount(self) -> None:
        """Handle application mount event."""

        def write_status():
            status_message = self.get_status_message()
            self.append_output(status_message)

        self.call_later(write_status)

        if LOCAL_CONFIG_FILE.exists():
            with open(LOCAL_CONFIG_FILE) as f:
                _ = json.load(f)

        self.prompt_input.focus()
