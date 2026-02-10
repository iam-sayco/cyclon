"""Integration tests for Cyclon services."""

from unittest.mock import Mock

import cyclon.paths  # noqa: PLC0415
from cyclon.services.file_service import FileService  # noqa: PLC0415
from cyclon.services.process_service import ProcessService  # noqa: PLC0415


class TestFileServiceIntegration:
    """Integration tests for FileService using real temp directories."""

    def test_plan_operations(self, tmp_path, monkeypatch):
        """Test plan file operations."""
        # Monkeypatch paths to use tmp_path
        monkeypatch.setattr(cyclon.paths, "LOCAL_CYCLON_DIR", tmp_path / ".cyclon")
        monkeypatch.setattr(cyclon.paths, "LOCAL_PLAN_FILE", tmp_path / ".cyclon" / "plan.md")
        monkeypatch.setattr(cyclon.paths, "LOCAL_LOCK_FILE", tmp_path / ".cyclon" / "process.lock")

        service = FileService()

        # Test 1: Plan doesn't exist
        assert service.plan_exists() is False

        # Test 2: Save plan
        service.save_plan("# Test Plan\n\nStep 1")

        # Test 3: Plan exists
        assert service.plan_exists() is True

    def test_lock_file_operations(self, tmp_path, monkeypatch):
        """Test lock file operations."""
        # Monkeypatch paths to use tmp_path
        monkeypatch.setattr(cyclon.paths, "LOCAL_CYCLON_DIR", tmp_path / ".cyclon")
        monkeypatch.setattr(cyclon.paths, "LOCAL_LOCK_FILE", tmp_path / ".cyclon" / "process.lock")

        service = FileService()

        # Test 1: Lock doesn't exist
        assert service.lock_file_exists() is False

        # Test 2: Create lock
        service.create_lock_file()
        assert service.lock_file_exists() is True

        # Test 3: Remove lock
        service.remove_lock_file()
        assert service.lock_file_exists() is False

    def test_clear_session(self, tmp_path, monkeypatch):
        """Test clearing session."""
        # Monkeypatch paths to use tmp_path
        monkeypatch.setattr(cyclon.paths, "LOCAL_CYCLON_DIR", tmp_path / ".cyclon")
        monkeypatch.setattr(cyclon.paths, "LOCAL_PLAN_FILE", tmp_path / ".cyclon" / "plan.md")
        monkeypatch.setattr(cyclon.paths, "LOCAL_LOCK_FILE", tmp_path / ".cyclon" / "process.lock")
        monkeypatch.setattr(cyclon.paths, "LOCAL_CONFIG_FILE", tmp_path / ".cyclon" / "config.json")
        monkeypatch.setattr(cyclon.paths, "LOCAL_PROMPT_FILE", tmp_path / ".cyclon" / "prompt.md")

        service = FileService()

        # Create some files
        service.save_file("test.txt", "test")
        service.save_plan("plan")
        service.create_lock_file()

        # Clear session
        service.clear_session()

        # Files should be removed
        assert not (tmp_path / ".cyclon" / "test.txt").exists()
        assert not (tmp_path / ".cyclon" / "plan.md").exists()
        assert not (tmp_path / ".cyclon" / "process.lock").exists()


class TestProcessServiceIntegration:
    """Integration tests for ProcessService."""

    def test_check_exception(self):
        """Test exception checking."""
        service = ProcessService()

        # Should find exception
        assert service.check_exception("Error: Something went wrong", ["Error:"]) is True

        # Should not find exception
        assert service.check_exception("Normal output", ["Error:"]) is False

        # Empty list
        assert service.check_exception("Error: test", []) is False

    def test_process_state(self):
        """Test process state management."""
        service = ProcessService()

        # No process running
        assert service.is_process_running() is False
        assert service.get_process_pid() is None

        # Set mock process
        mock_pty = Mock()
        mock_pty.isalive.return_value = True
        mock_pty.pid = 12345

        service.current_pty = mock_pty

        assert service.is_process_running() is True
        assert service.get_process_pid() == 12345

    def test_terminal_widget(self):
        """Test terminal widget operations."""
        service = ProcessService()

        # Set mock widget
        mock_widget = Mock()
        service.set_terminal_widget(mock_widget)

        assert service._terminal_widget == mock_widget

    def test_pty_callback(self):
        """Test PTY callback."""
        service = ProcessService()

        mock_callback = Mock()
        service.set_pty_changed_callback(mock_callback)

        assert service._pty_changed_callback == mock_callback
