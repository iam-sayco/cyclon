"""Modal screens for Cyclon."""

import json
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Input, RadioButton, RadioSet, Static, TextArea


class BaseModalScreen(ModalScreen):
    """Base class for all modal screens with common functionality."""

    BINDINGS = [("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    BaseModalScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.6);
    }
    BaseModalScreen > Vertical {
        background: #2a1530;
        border: solid #ed4aff;
        padding: 2 4;
        scrollbar-size-vertical: 1;
        scrollbar-background: #2a1530;
        scrollbar-color: white;
        scrollbar-background-hover: #2a1530;
        scrollbar-color-hover: #ed4aff;
        scrollbar-background-active: #2a1530;
        scrollbar-color-active: #ed4aff;
    }
    BaseModalScreen Static {
        margin-bottom: 1;
    }
    BaseModalScreen .modal-header {
        margin-bottom: 1;
    }
    BaseModalScreen Input {
        background: #1a0a1f;
        border: solid #ed4aff;
        color: white;
    }
    BaseModalScreen Input:focus {
        border: solid white;
    }
    BaseModalScreen Input:focus-within {
        border: solid white;
    }
    """

    def on_key(self, event: Key) -> None:
        """Handle escape key to dismiss modal."""
        if event.key == "escape":
            self.dismiss()
            event.stop()


class CommandsModalScreen(BaseModalScreen):
    """Modal screen displaying available commands and their descriptions.

    Shows a help screen with all available slash commands, their usage,
    and descriptions. Can be opened with F1 key or /help command.

    Example:
        >>> def action_show_help(self):
        ...     self.push_screen(CommandsModalScreen())
    """

    DEFAULT_CSS = """
    CommandsModalScreen > Vertical {
        width: 60%;
        height: auto;
        max-height: 80%;
        padding: 2 5 2 4;
        overflow: auto;
    }
    CommandsModalScreen .modal-title-row {
        width: 100%;
        height: auto;
    }
    CommandsModalScreen .modal-title {
        width: auto;
    }
    CommandsModalScreen .esc-hint {
        text-align: right;
        color: #999;
        padding-right: 2;
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the commands help screen.

        Returns:
            ComposeResult with the screen layout
        """
        with Vertical():
            with Horizontal(classes="modal-title-row"):
                yield Static("[b]Available Commands[/b]", classes="modal-title")
                yield Static("(esc to close)", classes="esc-hint")

            yield Static("", classes="modal-header")
            yield Static("[b]Plan Interaction[/b]", classes="modal-header")
            yield Static("[b]/plan[/b] - View or edit work plan (opens editor)")
            yield Static(
                "[b]/plan <prompt>[/b] - Generate plan directly from prompt "
                "(e.g., /plan create a todo app)"
            )
            yield Static("[b]/prompt[/b] - Additional context/info for plan execution")

            yield Static("", classes="modal-header")
            yield Static("[b]Actions[/b]", classes="modal-header")
            yield Static("[b]/run[/b] - Run executing plan")
            yield Static("[b]/stop[/b] - Stop current processing")
            yield Static("[b]/new-session[/b] - Clear all session data except config")
            yield Static("[b]/clear[/b] - Clear output window")

            yield Static("", classes="modal-header")
            yield Static("[b]AI Settings[/b]", classes="modal-header")
            yield Static("[b]/provider[/b] - AI coding tool provider")
            yield Static("[b]/model[/b] - AI model (may not be supported by all providers)")

            yield Static("", classes="modal-header")
            yield Static("[b]Help[/b]", classes="modal-header")
            yield Static("[b]/help[/b] - Show this commands help (or press F1)")


class ProviderModalScreen(BaseModalScreen):
    """Modal screen for selecting AI provider.

    Displays a list of available AI providers (e.g., opencode, copilot)
    as radio buttons. User can select a provider and save the configuration.

    Attributes:
        config_service: Optional ConfigService for loading providers
        providers: Dictionary of available providers

    Example:
        >>> screen = ProviderModalScreen(config_service)
        >>> self.push_screen(screen, self.on_provider_selected)
    """

    DEFAULT_CSS = """
    ProviderModalScreen > Vertical {
        width: 60%;
        height: auto;
        max-height: 80%;
        padding: 2 4;
    }
    ProviderModalScreen RadioSet {
        background: #2a1530;
        border: solid white;
        padding: 0;
    }
    ProviderModalScreen RadioSet:focus {
        border: solid white;
    }
    ProviderModalScreen RadioSet > RadioButton {
        background: transparent;
        color: white;
    }
    ProviderModalScreen RadioSet > RadioButton:hover {
        background: #3a2540;
    }
    ProviderModalScreen RadioSet > RadioButton:focus {
        background: #ed4aff;
        color: black;
    }
    ProviderModalScreen RadioSet > RadioButton.-selected .toggle--label {
        background: #ed4aff !important;
        color: black !important;
        text-style: bold;
    }
    ProviderModalScreen RadioSet > RadioButton.-on {
        text-style: bold;
    }
    ProviderModalScreen RadioSet > RadioButton.-on .toggle--button {
        background: #ed4aff;
        color: white;
    }
    ProviderModalScreen RadioSet > RadioButton .toggle--button {
        color: #ed4aff;
    }
    ProviderModalScreen .close-hint {
        text-align: right;
        color: #999;
        margin-top: 1;
    }
    ProviderModalScreen .save-hint {
        color: #999;
        margin-top: 1;
    }
    """

    def __init__(self, config_service=None, *args, **kwargs):
        """Initialize provider modal with optional config service.

        Args:
            config_service: ConfigService instance for loading providers
            *args: Additional positional arguments for parent class
            **kwargs: Additional keyword arguments for parent class
        """
        super().__init__(*args, **kwargs)
        self.config_service = config_service
        self.providers = self.load_providers()

    def load_providers(self):
        """Load available providers from config service or file.

        Returns:
            Dictionary of provider configurations
        """
        if self.config_service:
            return self.config_service.load_providers()

        providers_file = Path(__file__).parent / "data" / "providers.json"
        if providers_file.exists():
            with open(providers_file) as f:
                return json.load(f)
        return {}

    def compose(self) -> ComposeResult:
        """Compose the provider selection screen.

        Returns:
            ComposeResult with radio buttons for each provider
        """
        with Vertical():
            yield Static("[b]Select Provider[/b]", classes="modal-header")
            radio_buttons = [
                RadioButton(provider_data["label"], id=provider_id)
                for provider_id, provider_data in self.providers.items()
            ]
            yield RadioSet(*radio_buttons, id="provider-radioset")
            yield Static("(hit enter to save)", classes="save-hint")
            yield Static("(esc to close)", classes="close-hint")

    def on_mount(self) -> None:
        """Focus the radio set when screen mounts."""
        radioset = self.query_one("#provider-radioset", RadioSet)
        radioset.focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle provider selection change.

        Dismisses the screen with selected provider information.

        Args:
            event: Radio set change event
        """
        if event.radio_set.id == "provider-radioset" and event.pressed and event.pressed.id:
            self.dismiss(
                {"provider_id": event.pressed.id, "provider_label": str(event.pressed.label)}
            )


class ModelModalScreen(BaseModalScreen):
    """Modal screen for setting the AI model name.

    Provides an input field for entering the model name (e.g., gpt-4, claude-3).
    Pre-populates with current model if available.

    Attributes:
        current_model: Currently configured model name

    Example:
        >>> screen = ModelModalScreen("gpt-4")
        >>> self.push_screen(screen, self.on_model_set)
    """

    DEFAULT_CSS = """
    ModelModalScreen > Vertical {
        width: 60%;
        height: auto;
        max-height: 80%;
        padding: 2 4;
    }
    ModelModalScreen Input {
        margin: 1 0;
    }
    ModelModalScreen .close-hint {
        text-align: right;
        color: #999;
        margin-top: 1;
    }
    ModelModalScreen .save-hint {
        color: #999;
        margin-top: 1;
    }
    """

    def __init__(self, current_model: str = "", *args, **kwargs):
        """Initialize model modal with current model name.

        Args:
            current_model: Current model name to pre-populate input
            *args: Additional positional arguments for parent class
            **kwargs: Additional keyword arguments for parent class
        """
        super().__init__(*args, **kwargs)
        self.current_model = current_model

    def compose(self) -> ComposeResult:
        """Compose the model input screen.

        Returns:
            ComposeResult with input field for model name
        """
        with Vertical():
            yield Static("[b]Set Model[/b]", classes="modal-header")
            yield Input(
                placeholder="Type name of the model", id="model-input", value=self.current_model
            )
            yield Static("(hit enter to save)", classes="save-hint")
            yield Static("(esc to close)", classes="close-hint")

    def on_mount(self) -> None:
        """Focus the input field when screen mounts."""
        model_input = self.query_one("#model-input", Input)
        model_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle model input submission.

        Dismisses the screen with the entered model name if not empty.

        Args:
            event: Input submission event
        """
        if event.input.id == "model-input":
            model_value = event.value.strip()
            if model_value:
                self.dismiss({"model": model_value})
            else:
                self.dismiss()


class FileModalScreen(BaseModalScreen):
    """Modal screen for editing files (plan.md or prompt.md).

    Provides a text area for editing files with syntax highlighting support.
    Files are saved with Ctrl+S or dismissed with Escape.

    Attributes:
        file_name: Name of the file to edit
        modal_title: Title displayed in the modal header
        file_service: Optional FileService for loading/saving content
        content: Current file content

    Example:
        >>> screen = FileModalScreen("plan.md", "Edit Plan", file_service)
        >>> self.push_screen(screen, self.on_file_saved)
    """

    BINDINGS = [("ctrl+s", "save_and_close", "Save")]

    DEFAULT_CSS = """
    FileModalScreen > Vertical {
        width: 80%;
        height: 80%;
        padding: 2 4;
    }
    FileModalScreen TextArea {
        margin: 1 0;
        height: 1fr;
        border: solid #ed4aff;
        background: #2a1530;
        scrollbar-size-vertical: 1;
        scrollbar-background: #2a1530;
        scrollbar-color: white;
        scrollbar-background-hover: #2a1530;
        scrollbar-color-hover: #ed4aff;
        scrollbar-background-active: #2a1530;
        scrollbar-color-active: #ed4aff;
    }
    FileModalScreen TextArea:focus {
        border: solid white;
    }
    FileModalScreen .close-hint {
        text-align: center;
        color: #999;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        file_name: str = "plan.md",
        modal_title: str = "Edit Plan",
        file_service=None,
        *args,
        **kwargs,
    ):
        """Initialize file modal with file configuration.

        Args:
            file_name: Name of the file to edit
            modal_title: Title to display in modal header
            file_service: FileService instance for file operations
            *args: Additional positional arguments for parent class
            **kwargs: Additional keyword arguments for parent class
        """
        super().__init__(*args, **kwargs)
        self.file_name = file_name
        self.modal_title = modal_title
        self.file_service = file_service
        self.content = self.load_content()

    def load_content(self) -> str:
        """Load content from file service or filesystem.

        Returns:
            File content as string, or empty string if file doesn't exist
        """
        if self.file_service:
            content = self.file_service.load_content(self.file_name)
            return content if content is not None else ""

        file_path = Path.cwd() / ".cyclon" / self.file_name
        if file_path.exists():
            with open(file_path) as f:
                return f.read()
        return ""

    def compose(self) -> ComposeResult:
        """Compose the file editor screen.

        Returns:
            ComposeResult with text area for editing file content
        """
        with Vertical():
            yield Static(f"[b]{self.modal_title}[/b]", classes="modal-header")

            if self.file_name == "prompt.md":
                placeholder_text = (
                    "Define your additional requirements (coding standards, "
                    "conventions, etc.) for plan execution..."
                )
            elif self.file_name == "plan.md":
                placeholder_text = "Your work plan with checkboxes..."
            else:
                placeholder_text = f"Your {self.file_name}..."

            text_area = TextArea(placeholder=placeholder_text, id="file-textarea")
            text_area.load_text(self.content)
            yield text_area
            yield Static(
                "(ctrl+s to save and close, esc to close without saving)", classes="close-hint"
            )

    def on_mount(self) -> None:
        """Focus the text area when screen mounts."""
        text_area = self.query_one("#file-textarea", TextArea)
        text_area.focus()

    def action_save_and_close(self) -> None:
        """Save file and dismiss modal.

        Dismisses the screen with file name and content when Ctrl+S is pressed.
        """
        text_area = self.query_one("#file-textarea", TextArea)
        self.dismiss({"file_name": self.file_name, "content": text_area.text})
