"""Configuration service for Cyclon application."""

import json
from typing import Any

from cyclon.constants import CONFIG_FILENAME
from cyclon.exceptions import ConfigError
from cyclon.paths import DEFAULT_CONFIG_FILE, LOCAL_CONFIG_FILE, LOCAL_CYCLON_DIR, PROVIDERS_FILE
from cyclon.validation import validate_optional_string, validate_string


class ConfigService:
    """Service for managing configuration operations.

    This service handles all configuration-related operations including
    loading, saving, and validating configuration files.

    Attributes:
        None

    Example:
        >>> service = ConfigService()
        >>> is_valid, missing = service.validate_config()
        >>> if is_valid:
        ...     print("Configuration is valid")
    """

    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration and return status with missing items.

        Checks if the local configuration file exists and contains
        required fields (provider and model).

        Returns:
            Tuple containing:
                - bool: True if configuration is valid, False otherwise
                - List[str]: List of missing configuration items

        Raises:
            ConfigError: If there's an error reading the configuration file
        """
        missing = []

        if not LOCAL_CONFIG_FILE.exists():
            missing.extend(["provider", "model"])
            return False, missing

        try:
            with open(LOCAL_CONFIG_FILE) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}") from e
        except OSError as e:
            raise ConfigError(f"Error reading config file: {e}") from e

        if not config.get("provider"):
            missing.append("provider")
        if not config.get("model"):
            missing.append("model")

        return len(missing) == 0, missing

    def get_status_message(self) -> str:
        """Generate status message about current configuration.

        Creates a formatted status message showing the current state
        of providers file, config file, and configured provider/model.

        Returns:
            str: Formatted status message with color codes

        Raises:
            ConfigError: If there's an error reading configuration files
        """
        status_lines = []

        if PROVIDERS_FILE.exists():
            status_lines.append("[green]●[/green] Providers file detected")
        else:
            status_lines.append("[red]●[/red] Providers file missing")

        config_exists = LOCAL_CONFIG_FILE.exists()

        if config_exists:
            status_lines.append("[green]●[/green] Config file detected")

            try:
                with open(LOCAL_CONFIG_FILE) as f:
                    config = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                raise ConfigError(f"Error reading config file: {e}") from e

            provider = config.get("provider")
            model = config.get("model")

            if provider:
                status_lines.append(f"[green]●[/green] Provider: [b]{provider}[/b]")
            else:
                status_lines.append(
                    "[orange1]●[/orange1] [orange1]Provider not set - use /provider[/orange1]"
                )

            if model:
                status_lines.append(f"[green]●[/green] Model: [b]{model}[/b]")
            else:
                status_lines.append(
                    "[orange1]●[/orange1] [orange1]Model not set - use /model[/orange1]"
                )
        else:
            status_lines.append("[orange1]●[/orange1] Config file not found")
            status_lines.append(
                "[orange1]●[/orange1] [orange1]Provider not set - use /provider[/orange1]"
            )
            status_lines.append(
                "[orange1]●[/orange1] [orange1]Model not set - use /model[/orange1]"
            )

        status_lines.append("")

        is_valid, missing = self.validate_config()
        if is_valid:
            status_lines.append("[b green]✓ Application is ready![/b green]")
            status_lines.append("Create or provide your plan and let's get to work.")
        else:
            status_lines.append("[b orange1]⚠ Setup required[/b orange1]")
            missing_str = " and ".join([f"[b]/{item}[/b]" for item in missing])
            status_lines.append(f"Please configure {missing_str} first, then paste your plan.")

        status_lines.append("")
        return "\n".join(status_lines)

    def load_providers(self) -> dict[str, Any]:
        """Load providers configuration from providers file.

        Reads the providers.json file and returns its contents.

        Returns:
            Dict[str, Any]: Dictionary containing provider configurations.
                Returns empty dict if file doesn't exist.

        Raises:
            ConfigError: If there's an error reading or parsing the providers file
        """
        if PROVIDERS_FILE.exists():
            try:
                with open(PROVIDERS_FILE) as f:
                    result: dict[str, Any] = json.load(f)
                    return result
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid JSON in providers file: {e}") from e
            except OSError as e:
                raise ConfigError(f"Error reading providers file: {e}") from e
        return {}

    def load_config(self) -> dict[str, Any]:
        """Load configuration with defaults and local overrides.

        Loads default config first, then overrides with local config if exists.

        Returns:
            Dict[str, Any]: Merged configuration dictionary

        Raises:
            ConfigError: If there's an error reading configuration files
        """
        config = {}

        if DEFAULT_CONFIG_FILE.exists():
            try:
                with open(DEFAULT_CONFIG_FILE) as f:
                    config = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                raise ConfigError(f"Error reading default config: {e}") from e

        if LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE) as f:
                    local = json.load(f)
                    config.update(local)
            except (json.JSONDecodeError, OSError) as e:
                raise ConfigError(f"Error reading local config: {e}") from e

        return config

    def _save_json_config(self, key: str, value: str) -> None:
        """Save configuration key-value to config.json.

        Args:
            key: Configuration key to save
            value: Value to save for the key

        Raises:
            ConfigError: If there's an error writing the configuration file
        """
        config_dir = LOCAL_CYCLON_DIR
        config_file = config_dir / CONFIG_FILENAME

        try:
            config_dir.mkdir(exist_ok=True)

            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)
            else:
                config = {}

            config[key] = value

            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except OSError as e:
            raise ConfigError(f"Error saving config file: {e}") from e
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in existing config file: {e}") from e

    def save_provider_config(self, provider_name: str) -> None:
        """Save provider configuration.

        Args:
            provider_name: Name of the provider to save

        Raises:
            ValueError: If provider_name is empty or not a string
            ConfigError: If there's an error saving the configuration
        """
        validate_string(provider_name, "provider_name")
        self._save_json_config("provider", provider_name)

    def save_model_config(self, model_name: str) -> None:
        """Save model configuration.

        Args:
            model_name: Name of the model to save

        Raises:
            ValueError: If model_name is empty or not a string
            ConfigError: If there's an error saving the configuration
        """
        validate_string(model_name, "model_name")
        self._save_json_config("model", model_name)

    def build_command(
        self, provider: str | None = None, model: str | None = None, prompt: str | None = None
    ) -> list[str]:
        """Build command for given provider, model and prompt.

        Constructs a command list based on provider configuration and
        replaces placeholders with actual values.

        Args:
            provider: Provider name. If None, uses configured provider.
            model: Model name. If None, uses configured model.
            prompt: Prompt text to substitute in command.

        Returns:
            List[str]: Constructed command as list of strings.
                Returns empty list if config is invalid.

        Raises:
            ValueError: If arguments have invalid types
            ConfigError: If there's an error reading configuration
        """
        validate_optional_string(provider, "provider")
        validate_optional_string(model, "model")
        validate_optional_string(prompt, "prompt")

        providers = self.load_providers()

        if provider is None and LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE) as f:
                    config = json.load(f)
                provider = config.get("provider", "opencode")
            except (json.JSONDecodeError, OSError) as e:
                raise ConfigError(f"Error reading config for command building: {e}") from e

        if model is None and LOCAL_CONFIG_FILE.exists():
            try:
                with open(LOCAL_CONFIG_FILE) as f:
                    config = json.load(f)
                model = config.get("model", "")
            except (json.JSONDecodeError, OSError) as e:
                raise ConfigError(f"Error reading config for command building: {e}") from e

        if not LOCAL_CONFIG_FILE.exists() or provider not in providers:
            return []

        provider_config = providers[provider]
        cmd = provider_config["command"]

        if isinstance(cmd, str):
            cmd = [cmd]

        model_placeholder = provider_config.get("model_placeholder", "{model}")

        result_cmd = []
        for part in cmd:
            modified_part = part
            if model_placeholder in modified_part and model:
                modified_part = modified_part.replace(model_placeholder, model)
            if "{prompt}" in modified_part and prompt:
                modified_part = modified_part.replace("{prompt}", prompt)
            result_cmd.append(modified_part)

        return result_cmd
