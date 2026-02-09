"""Unit tests for ConfigService."""

import json
from pathlib import Path
from unittest.mock import mock_open, patch, MagicMock

import pytest

from cyclon.exceptions import ConfigError


class TestValidateConfig:
    """Tests for ConfigService.validate_config() method."""
    
    def test_no_config_file_returns_missing_provider_and_model(self, config_service, mock_cyclon_paths):
        """Test that missing config file returns both provider and model as missing."""
        is_valid, missing = config_service.validate_config()
        
        assert is_valid is False
        assert "provider" in missing
        assert "model" in missing
    
    def test_empty_json_returns_missing_provider_and_model(self, config_service, mock_cyclon_paths):
        """Test that empty JSON config returns both fields as missing."""
        mock_cyclon_paths["local_config_file"].write_text("{}")
        
        is_valid, missing = config_service.validate_config()
        
        assert is_valid is False
        assert "provider" in missing
        assert "model" in missing
    
    def test_only_provider_returns_missing_model(self, config_service, mock_cyclon_paths):
        """Test that config with only provider returns model as missing."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test"})
        )
        
        is_valid, missing = config_service.validate_config()
        
        assert is_valid is False
        assert "provider" not in missing
        assert "model" in missing
    
    def test_only_model_returns_missing_provider(self, config_service, mock_cyclon_paths):
        """Test that config with only model returns provider as missing."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"model": "gpt-4"})
        )
        
        is_valid, missing = config_service.validate_config()
        
        assert is_valid is False
        assert "provider" in missing
        assert "model" not in missing
    
    def test_full_config_returns_valid(self, config_service, mock_cyclon_paths):
        """Test that config with both provider and model is valid."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "gpt-4"})
        )
        
        is_valid, missing = config_service.validate_config()
        
        assert is_valid is True
        assert missing == []
    
    def test_invalid_json_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that invalid JSON raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("invalid json")
        
        with pytest.raises(ConfigError) as exc_info:
            config_service.validate_config()
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_oserror_on_read_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError on file read raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("{}")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service.validate_config()
            
            assert "Error reading config file" in str(exc_info.value)


class TestGetStatusMessage:
    """Tests for ConfigService.get_status_message() method."""
    
    def test_no_providers_file_shows_red_status(self, config_service, mock_cyclon_paths):
        """Test that missing providers file shows red status."""
        # Remove providers file
        mock_cyclon_paths["providers_file"].unlink()
        
        message = config_service.get_status_message()
        
        assert "[red]●[/red] Providers file missing" in message
    
    def test_no_config_file_shows_orange_status(self, config_service, mock_cyclon_paths):
        """Test that missing config file shows orange status."""
        # Ensure config file does not exist
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        
        message = config_service.get_status_message()
        
        assert "[orange1]●[/orange1] Config file not found" in message
    
    def test_valid_config_shows_green_ready(self, config_service, mock_cyclon_paths):
        """Test that valid config shows green ready message."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "gpt-4"})
        )
        
        message = config_service.get_status_message()
        
        assert "[green]●[/green] Config file detected" in message
        assert "[b green]✓ Application is ready![/b green]" in message
    
    def test_invalid_config_shows_setup_required(self, config_service, mock_cyclon_paths):
        """Test that invalid config shows setup required."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test"})  # Missing model
        )
        
        message = config_service.get_status_message()
        
        assert "[b orange1]⚠ Setup required[/b orange1]" in message
    
    def test_oserror_on_read_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError on config read raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("{}")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service.get_status_message()
            
            assert "Error reading config file" in str(exc_info.value)
    
    def test_shows_provider_and_model_names(self, config_service, mock_cyclon_paths):
        """Test that status message shows provider and model names."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "my-provider", "model": "my-model"})
        )
        
        message = config_service.get_status_message()
        
        assert "Provider: [b]my-provider[/b]" in message
        assert "Model: [b]my-model[/b]" in message


class TestLoadProviders:
    """Tests for ConfigService.load_providers() method."""
    
    def test_no_file_returns_empty_dict(self, config_service, mock_cyclon_paths):
        """Test that missing providers file returns empty dict."""
        # Ensure providers file does not exist
        if mock_cyclon_paths["providers_file"].exists():
            mock_cyclon_paths["providers_file"].unlink()
        
        result = config_service.load_providers()
        
        assert result == {}
    
    def test_valid_json_returns_dict(self, config_service, mock_cyclon_paths, sample_providers_data):
        """Test that valid JSON returns parsed dict."""
        mock_cyclon_paths["providers_file"].write_text(
            json.dumps(sample_providers_data)
        )
        
        result = config_service.load_providers()
        
        assert result == sample_providers_data
    
    def test_invalid_json_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that invalid JSON raises ConfigError."""
        mock_cyclon_paths["providers_file"].write_text("invalid json")
        
        with pytest.raises(ConfigError) as exc_info:
            config_service.load_providers()
        
        assert "Invalid JSON" in str(exc_info.value)
    
    def test_oserror_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError raises ConfigError."""
        mock_cyclon_paths["providers_file"].write_text("{}")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service.load_providers()
            
            assert "Error reading providers file" in str(exc_info.value)


class TestLoadConfig:
    """Tests for ConfigService.load_config() method."""
    
    def test_no_files_returns_empty_dict(self, config_service, mock_cyclon_paths):
        """Test that missing both config files returns empty dict."""
        # Ensure both config files do not exist
        if mock_cyclon_paths["default_config_file"].exists():
            mock_cyclon_paths["default_config_file"].unlink()
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        mock_cyclon_paths["local_config_file"].parent.mkdir(exist_ok=True)
        
        result = config_service.load_config()
        
        assert result == {}
    
    def test_only_default_returns_default_content(self, config_service, mock_cyclon_paths):
        """Test that only default config returns its content."""
        # Ensure local config does not exist
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        
        default_data = {"timeout": 300, "provider": "default"}
        mock_cyclon_paths["default_config_file"].write_text(json.dumps(default_data))
        
        result = config_service.load_config()
        
        assert result == default_data
    
    def test_only_local_returns_local_content(self, config_service, mock_cyclon_paths):
        """Test that only local config returns its content."""
        # Ensure default config does not exist
        if mock_cyclon_paths["default_config_file"].exists():
            mock_cyclon_paths["default_config_file"].unlink()
        
        local_data = {"provider": "local", "model": "gpt-4"}
        mock_cyclon_paths["local_config_file"].write_text(json.dumps(local_data))
        
        result = config_service.load_config()
        
        assert result == local_data
    
    def test_both_files_merges_local_overrides_default(self, config_service, mock_cyclon_paths):
        """Test that local config overrides default config."""
        default_data = {"timeout": 300, "provider": "default"}
        local_data = {"provider": "local"}  # Override provider
        
        mock_cyclon_paths["default_config_file"].write_text(json.dumps(default_data))
        mock_cyclon_paths["local_config_file"].write_text(json.dumps(local_data))
        
        result = config_service.load_config()
        
        assert result["timeout"] == 300  # From default
        assert result["provider"] == "local"  # From local (override)
    
    def test_invalid_json_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that invalid JSON raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("invalid json")
        
        with pytest.raises(ConfigError) as exc_info:
            config_service.load_config()
        
        assert "Error reading local config" in str(exc_info.value)
    
    def test_oserror_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("{}")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service.load_config()
            
            assert "Error reading" in str(exc_info.value)


class TestSaveJsonConfig:
    """Tests for ConfigService._save_json_config() method."""
    
    def test_creates_new_file_with_key(self, config_service, mock_cyclon_paths):
        """Test that new config file is created with key."""
        config_service._save_json_config("provider", "test-provider")
        
        content = json.loads(mock_cyclon_paths["local_config_file"].read_text())
        assert content["provider"] == "test-provider"
    
    def test_overwrites_existing_key(self, config_service, mock_cyclon_paths):
        """Test that existing key is overwritten."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "old", "model": "gpt-3"})
        )
        
        config_service._save_json_config("provider", "new-provider")
        
        content = json.loads(mock_cyclon_paths["local_config_file"].read_text())
        assert content["provider"] == "new-provider"
        assert content["model"] == "gpt-3"  # Unchanged
    
    def test_multiple_writes_merge_correctly(self, config_service, mock_cyclon_paths):
        """Test that multiple writes merge correctly."""
        config_service._save_json_config("provider", "test")
        config_service._save_json_config("model", "gpt-4")
        config_service._save_json_config("timeout", "600")
        
        content = json.loads(mock_cyclon_paths["local_config_file"].read_text())
        assert content["provider"] == "test"
        assert content["model"] == "gpt-4"
        assert content["timeout"] == "600"
    
    def test_oserror_on_mkdir_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError on mkdir raises ConfigError."""
        with patch.object(Path, 'mkdir', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service._save_json_config("key", "value")
            
            assert "Error saving config file" in str(exc_info.value)
    
    def test_oserror_on_write_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError on write raises ConfigError."""
        mock_cyclon_paths["local_config_file"].parent.mkdir(exist_ok=True, parents=True)
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service._save_json_config("key", "value")
            
            assert "Error saving config file" in str(exc_info.value)
    
    def test_invalid_existing_json_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that invalid existing JSON raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("invalid json")
        
        with pytest.raises(ConfigError) as exc_info:
            config_service._save_json_config("key", "value")
        
        assert "Invalid JSON" in str(exc_info.value)


class TestSaveProviderConfig:
    """Tests for ConfigService.save_provider_config() method."""
    
    def test_valid_provider_name_saves(self, config_service, mock_cyclon_paths):
        """Test that valid provider name is saved."""
        # Ensure config file does not exist initially
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        
        config_service.save_provider_config("my-provider")
        
        content = json.loads(mock_cyclon_paths["local_config_file"].read_text())
        assert content["provider"] == "my-provider"
    
    def test_none_raises_value_error(self, config_service):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_provider_config(None)
        
        assert "provider_name" in str(exc_info.value)
    
    def test_empty_string_raises_value_error(self, config_service):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_provider_config("")
        
        assert "provider_name" in str(exc_info.value)
    
    def test_integer_raises_value_error(self, config_service):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_provider_config(123)
        
        assert "provider_name" in str(exc_info.value)


class TestSaveModelConfig:
    """Tests for ConfigService.save_model_config() method."""
    
    def test_valid_model_name_saves(self, config_service, mock_cyclon_paths):
        """Test that valid model name is saved."""
        # Ensure config file does not exist initially
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        
        config_service.save_model_config("gpt-4")
        
        content = json.loads(mock_cyclon_paths["local_config_file"].read_text())
        assert content["model"] == "gpt-4"
    
    def test_none_raises_value_error(self, config_service):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_model_config(None)
        
        assert "model_name" in str(exc_info.value)
    
    def test_empty_string_raises_value_error(self, config_service):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_model_config("")
        
        assert "model_name" in str(exc_info.value)
    
    def test_integer_raises_value_error(self, config_service):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.save_model_config(123)
        
        assert "model_name" in str(exc_info.value)


class TestBuildCommand:
    """Tests for ConfigService.build_command() method."""
    
    def test_no_config_returns_empty_list(self, config_service, mock_cyclon_paths):
        """Test that missing config returns empty list."""
        # Ensure config file does not exist
        if mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].unlink()
        
        result = config_service.build_command()
        
        assert result == []
    
    def test_provider_not_in_providers_returns_empty_list(self, config_service, mock_cyclon_paths):
        """Test that unknown provider returns empty list."""
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "unknown", "model": "test"})
        )
        
        result = config_service.build_command()
        
        assert result == []
    
    def test_command_as_string_returns_single_element_list(self, config_service, mock_cyclon_paths):
        """Test that string command is converted to list."""
        providers = {"test": {"name": "Test", "command": "test-cmd"}}
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "model"})
        )
        
        result = config_service.build_command()
        
        assert result == ["test-cmd"]
    
    def test_command_as_list_returns_list(self, config_service, mock_cyclon_paths):
        """Test that list command is returned as-is."""
        providers = {"test": {"name": "Test", "command": ["cmd", "arg"]}}
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "model"})
        )
        
        result = config_service.build_command()
        
        assert result == ["cmd", "arg"]
    
    def test_replaces_model_placeholder(self, config_service, mock_cyclon_paths):
        """Test that model placeholder is replaced."""
        providers = {
            "test": {
                "name": "Test",
                "command": ["cmd", "--model", "{model}"],
                "model_placeholder": "{model}"
            }
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "gpt-4"})
        )
        
        result = config_service.build_command()
        
        assert "gpt-4" in result
    
    def test_replaces_prompt_placeholder(self, config_service, mock_cyclon_paths):
        """Test that prompt placeholder is replaced."""
        providers = {
            "test": {
                "name": "Test",
                "command": ["cmd", "--prompt", "{prompt}"],
                "model_placeholder": "{model}"
            }
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "gpt-4"})
        )
        
        result = config_service.build_command(prompt="hello world")
        
        assert "hello world" in result
    
    def test_explicit_provider_parameter(self, config_service, mock_cyclon_paths):
        """Test that explicit provider parameter is used."""
        providers = {
            "explicit": {"name": "Explicit", "command": ["explicit-cmd"]}
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "other", "model": "test"})
        )
        
        result = config_service.build_command(provider="explicit")
        
        assert "explicit-cmd" in result
    
    def test_explicit_model_parameter(self, config_service, mock_cyclon_paths):
        """Test that explicit model parameter is used."""
        providers = {
            "test": {
                "name": "Test",
                "command": ["cmd", "--model", "{model}"],
                "model_placeholder": "{model}"
            }
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "other"})
        )
        
        result = config_service.build_command(model="explicit-model")
        
        assert "explicit-model" in result
    
    def test_explicit_prompt_parameter(self, config_service, mock_cyclon_paths):
        """Test that explicit prompt parameter is used."""
        providers = {
            "test": {
                "name": "Test",
                "command": ["cmd", "--input", "{prompt}"],
                "model_placeholder": "{model}"
            }
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "test", "model": "gpt-4"})
        )
        
        result = config_service.build_command(prompt="explicit-prompt")
        
        assert "explicit-prompt" in result
    
    def test_all_none_reads_from_config(self, config_service, mock_cyclon_paths):
        """Test that None values read from config file."""
        providers = {
            "config-provider": {
                "name": "Config",
                "command": ["cmd", "--model", "{model}"],
                "model_placeholder": "{model}"
            }
        }
        mock_cyclon_paths["providers_file"].write_text(json.dumps(providers))
        mock_cyclon_paths["local_config_file"].write_text(
            json.dumps({"provider": "config-provider", "model": "config-model"})
        )
        
        result = config_service.build_command()
        
        assert "config-provider" in mock_cyclon_paths["providers_file"].read_text()
        assert result  # Should not be empty
    
    def test_provider_as_int_raises_value_error(self, config_service):
        """Test that integer provider raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            config_service.build_command(provider=123)
        
        assert "provider" in str(exc_info.value)
    
    def test_oserror_on_read_raises_config_error(self, config_service, mock_cyclon_paths):
        """Test that OSError on config read raises ConfigError."""
        mock_cyclon_paths["local_config_file"].write_text("{}")
        
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(ConfigError) as exc_info:
                config_service.build_command()
            
            assert "Error reading providers file" in str(exc_info.value) or "Error reading config" in str(exc_info.value)
