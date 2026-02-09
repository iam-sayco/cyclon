"""Configuration manager for Cyclon."""

from pathlib import Path
import json


class ConfigManager:
    def __init__(self, project_root: Path | None = None):
        from cyclon.paths import (
            DEFAULT_CONFIG_FILE, LOCAL_CONFIG_FILE, LOCAL_CYCLON_DIR
        )
        self.local_dir = LOCAL_CYCLON_DIR
        self.default_config = DEFAULT_CONFIG_FILE
        self.local_config_file = LOCAL_CONFIG_FILE

    def load_config(self) -> dict:
        config = {}
        if self.default_config.exists():
            with open(self.default_config, 'r') as f:
                config = json.load(f)
        if self.local_config_file.exists():
            with open(self.local_config_file, 'r') as f:
                local = json.load(f)
                config.update(local)
        return config

    def save(self, config: dict) -> None:
        self.local_dir.mkdir(exist_ok=True)
        with open(self.local_config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def get(self, key: str, default=None):
        return self.load_config().get(key, default)

    def set(self, key: str, value) -> None:
        config = self.load_config()
        config[key] = value
        self.save(config)
