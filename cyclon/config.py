"""Configuration manager for Cyclon."""

import json
from pathlib import Path
from typing import Any

from cyclon.paths import DEFAULT_CONFIG_FILE, LOCAL_CONFIG_FILE, LOCAL_CYCLON_DIR


class ConfigManager:
    """Manager for loading and saving configuration files."""

    def __init__(self, project_root: Path | None = None):
        """Initialize ConfigManager with project paths.

        Args:
            project_root: Optional root path for the project.
        """
        self.local_dir = LOCAL_CYCLON_DIR
        self.default_config = DEFAULT_CONFIG_FILE
        self.local_config_file = LOCAL_CONFIG_FILE

    def load_config(self) -> dict[str, Any]:
        """Load configuration from default and local config files.

        Returns:
            Merged configuration dictionary.
        """
        config = {}
        if self.default_config.exists():
            with open(self.default_config) as f:
                config = json.load(f)
        if self.local_config_file.exists():
            with open(self.local_config_file) as f:
                local = json.load(f)
                config.update(local)
        return config

    def save(self, config: dict[str, Any]) -> None:
        """Save configuration to local config file.

        Args:
            config: Configuration dictionary to save.
        """
        self.local_dir.mkdir(exist_ok=True)
        with open(self.local_config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key to retrieve.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self.load_config().get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key.

        Args:
            key: Configuration key to set.
            value: Value to set for the key.
        """
        config = self.load_config()
        config[key] = value
        self.save(config)
