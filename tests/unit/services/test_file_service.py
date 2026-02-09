"""Unit tests for FileService."""

import os
from pathlib import Path
from unittest.mock import patch
import pytest
import cyclon.paths

from cyclon.exceptions import FileError


class TestSaveFile:
    """Tests for FileService.save_file() method."""

    def test_save_file_writes_content(self, file_service, mock_cyclon_paths):
        """Test that file content is written correctly."""
        file_service.save_file("test.txt", "Hello World")

        content = mock_cyclon_paths["local_config_file"].parent / "test.txt"
        assert content.exists()
        assert content.read_text() == "Hello World"

    def test_save_file_creates_directory(self, file_service, mock_cyclon_paths):
        """Test that .cyclon directory is created if it doesn't exist."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        if cyclon_dir.exists():
            import shutil
            shutil.rmtree(cyclon_dir)

        file_service.save_file("test.txt", "content")

        assert cyclon_dir.exists()
        assert (cyclon_dir / "test.txt").exists()

    def test_save_file_with_none_filename_raises_value_error(self, file_service):
        """Test that None file_name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_file(None, "content")

        assert "file_name" in str(exc_info.value)

    def test_save_file_with_int_filename_raises_value_error(self, file_service):
        """Test that integer file_name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_file(123, "content")

        assert "file_name" in str(exc_info.value)

    def test_save_file_with_none_content_raises_value_error(self, file_service):
        """Test that None content raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_file("test.txt", None)

        assert "content" in str(exc_info.value)

    def test_save_file_with_int_content_raises_value_error(self, file_service):
        """Test that integer content raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_file("test.txt", 123)

        assert "content" in str(exc_info.value)

    def test_save_file_with_empty_content(self, file_service, mock_cyclon_paths):
        """Test that empty content is allowed."""
        file_service.save_file("test.txt", "")

        content_file = mock_cyclon_paths["local_config_file"].parent / "test.txt"
        assert content_file.exists()
        assert content_file.read_text() == ""

    def test_save_file_oserror_raises_file_error(self, file_service):
        """Test that OSError on write raises FileError."""
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(FileError) as exc_info:
                file_service.save_file("test.txt", "content")

            assert "Error saving file" in str(exc_info.value)


class TestSavePlan:
    """Tests for FileService.save_plan() method."""

    def test_save_plan_writes_content(self, file_service, mock_cyclon_paths):
        """Test that plan content is written correctly."""
        file_service.save_plan("# My Plan")

        assert mock_cyclon_paths["local_plan_file"].exists()
        assert mock_cyclon_paths["local_plan_file"].read_text() == "# My Plan"

    def test_save_plan_with_none_raises_value_error(self, file_service):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_plan(None)

        assert "plan_content" in str(exc_info.value)

    def test_save_plan_with_int_raises_value_error(self, file_service):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.save_plan(123)

        assert "plan_content" in str(exc_info.value)

    def test_save_plan_with_empty_content(self, file_service, mock_cyclon_paths):
        """Test that empty content is allowed."""
        file_service.save_plan("")

        assert mock_cyclon_paths["local_plan_file"].exists()
        assert mock_cyclon_paths["local_plan_file"].read_text() == ""

    def test_save_plan_creates_directory(self, file_service, mock_cyclon_paths):
        """Test that .cyclon directory is created."""
        cyclon_dir = mock_cyclon_paths["local_plan_file"].parent
        if cyclon_dir.exists():
            import shutil
            shutil.rmtree(cyclon_dir)

        file_service.save_plan("plan")

        assert cyclon_dir.exists()
        assert mock_cyclon_paths["local_plan_file"].exists()

    def test_save_plan_oserror_raises_file_error(self, file_service):
        """Test that OSError raises FileError."""
        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(FileError) as exc_info:
                file_service.save_plan("plan")

            assert "Error saving plan file" in str(exc_info.value)


class TestLoadLogo:
    """Tests for FileService.load_logo() method."""

    def test_load_logo_existing_file(self, file_service, mock_cyclon_paths):
        """Test that existing logo file returns its content."""
        mock_cyclon_paths["logo_file"].write_text("MY LOGO")

        result = file_service.load_logo()

        assert result == "MY LOGO"

    def test_load_logo_missing_file_returns_fallback(self, file_service, mock_cyclon_paths):
        """Test that missing logo file returns 'CYCLON'."""
        if mock_cyclon_paths["logo_file"].exists():
            mock_cyclon_paths["logo_file"].unlink()

        result = file_service.load_logo()

        assert result == "CYCLON"

    def test_load_logo_oserror_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that OSError raises FileError."""
        mock_cyclon_paths["logo_file"].touch()

        with patch('builtins.open', side_effect=OSError("Permission denied")):
            with pytest.raises(FileError) as exc_info:
                file_service.load_logo()

            assert "Error reading logo file" in str(exc_info.value)


class TestLoadGeneratePrompt:
    """Tests for FileService.load_generate_prompt() method."""

    def test_load_generate_prompt_existing_template(self, file_service, mock_cyclon_paths):
        """Test that existing template is processed with placeholders."""
        template_file = mock_cyclon_paths["prompts_dir"] / "generate.md"
        template_file.write_text("Plan: {plan_file_path}, User: {user_prompt}")

        result = file_service.load_generate_prompt("my prompt")

        assert "{user_prompt}" not in result
        assert "my prompt" in result
        assert "{plan_file_path}" not in result
        assert str(mock_cyclon_paths["local_plan_file"]) in result

    def test_load_generate_prompt_missing_template(self, file_service, mock_cyclon_paths):
        """Test that missing template returns fallback string."""
        template_file = mock_cyclon_paths["prompts_dir"] / "generate.md"
        if template_file.exists():
            template_file.unlink()

        result = file_service.load_generate_prompt("test prompt")

        assert "test prompt" in result

    def test_load_generate_prompt_replaces_user_prompt(self, file_service, mock_cyclon_paths):
        """Test that {user_prompt} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "generate.md"
        template_file.write_text("Prompt: {user_prompt}")

        result = file_service.load_generate_prompt("My User Prompt")

        assert "My User Prompt" in result
        assert "{user_prompt}" not in result

    def test_load_generate_prompt_replaces_plan_path(self, file_service, mock_cyclon_paths):
        """Test that {plan_file_path} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "generate.md"
        template_file.write_text("Path: {plan_file_path}")

        result = file_service.load_generate_prompt("prompt")

        expected_path = str(mock_cyclon_paths["local_plan_file"])
        assert expected_path in result
        assert "{plan_file_path}" not in result

    def test_load_generate_prompt_none_raises_value_error(self, file_service):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.load_generate_prompt(None)

        assert "user_prompt" in str(exc_info.value)

    def test_load_generate_prompt_int_raises_value_error(self, file_service):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.load_generate_prompt(123)

        assert "user_prompt" in str(exc_info.value)

    def test_load_generate_prompt_resolve_error_raises_file_error(self, file_service):
        """Test that resolve error raises FileError."""
        with patch.object(Path, 'resolve', side_effect=OSError("Resolve error")):
            with pytest.raises(FileError) as exc_info:
                file_service.load_generate_prompt("prompt")

            assert "Error resolving plan file path" in str(exc_info.value)

    def test_load_generate_prompt_read_error_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that read error raises FileError."""
        template_file = mock_cyclon_paths["prompts_dir"] / "generate.md"
        template_file.write_text("content")

        with patch('builtins.open', side_effect=OSError("Read error")):
            with pytest.raises(FileError) as exc_info:
                file_service.load_generate_prompt("prompt")

            assert "Error reading prompt template" in str(exc_info.value)


class TestBuildExecutionPrompt:
    """Tests for FileService.build_execution_prompt() method."""

    def test_build_execution_prompt_existing_template(self, file_service, mock_cyclon_paths):
        """Test that existing template is processed correctly."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("CWD: {cwd}\nPlan: {plan_path}\nUser: {user_instructions}")

        result = file_service.build_execution_prompt()

        assert os.getcwd() in result
        assert str(mock_cyclon_paths["local_plan_file"]) in result
        assert "N/A" in result

    def test_build_execution_prompt_missing_template(self, file_service, mock_cyclon_paths):
        """Test that missing template returns error message."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        if template_file.exists():
            template_file.unlink()

        result = file_service.build_execution_prompt()

        assert result == "Error: prompts/execute.md not found"

    def test_build_execution_prompt_explicit_plan_content(self, file_service, mock_cyclon_paths):
        """Test that plan is read from file when not explicitly provided."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Plan: {plan_path}")
        mock_cyclon_paths["local_plan_file"].write_text("File Plan Content")

        result = file_service.build_execution_prompt()

        # When plan_content is None (default), it reads from file
        # The template contains {plan_path} placeholder, not plan content
        assert str(mock_cyclon_paths["local_plan_file"]) in result

    def test_build_execution_prompt_reads_plan_from_file(self, file_service, mock_cyclon_paths):
        """Test that plan is read from file when not provided."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Plan: {plan_path}")
        mock_cyclon_paths["local_plan_file"].write_text("File Plan")

        result = file_service.build_execution_prompt()

        assert str(mock_cyclon_paths["local_plan_file"]) in result

    def test_build_execution_prompt_replaces_cwd(self, file_service, mock_cyclon_paths):
        """Test that {cwd} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("CWD: {cwd}")

        result = file_service.build_execution_prompt()

        assert os.getcwd() in result
        assert "{cwd}" not in result

    def test_build_execution_prompt_replaces_plan_path(self, file_service, mock_cyclon_paths):
        """Test that {plan_path} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Path: {plan_path}")

        result = file_service.build_execution_prompt()

        expected_path = str(mock_cyclon_paths["local_plan_file"])
        assert expected_path in result
        assert "{plan_path}" not in result

    def test_build_execution_prompt_replaces_lock_file(self, file_service, mock_cyclon_paths):
        """Test that {lock_file} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Lock: {lock_file}")

        result = file_service.build_execution_prompt()

        expected_path = str(mock_cyclon_paths["local_lock_file"])
        assert expected_path in result
        assert "{lock_file}" not in result

    def test_build_execution_prompt_replaces_context_file(self, file_service, mock_cyclon_paths):
        """Test that {context_file} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Context: {context_file}")

        result = file_service.build_execution_prompt()

        assert "{context_file}" not in result

    def test_build_execution_prompt_replaces_user_instructions(self, file_service, mock_cyclon_paths):
        """Test that {user_instructions} placeholder is replaced."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Instructions: {user_instructions}")
        mock_cyclon_paths["local_prompt_file"].write_text("My Instructions")

        result = file_service.build_execution_prompt()

        assert "My Instructions" in result
        assert "{user_instructions}" not in result

    def test_build_execution_prompt_missing_prompt_file(self, file_service, mock_cyclon_paths):
        """Test that missing prompt.md uses 'N/A' for instructions."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("Instructions: {user_instructions}")
        if mock_cyclon_paths["local_prompt_file"].exists():
            mock_cyclon_paths["local_prompt_file"].unlink()

        result = file_service.build_execution_prompt()

        assert "N/A" in result

    def test_build_execution_prompt_resolve_error_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that resolve error raises FileError."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("{cwd}")

        with patch.object(Path, 'resolve', side_effect=OSError("Resolve error")):
            with pytest.raises(FileError) as exc_info:
                file_service.build_execution_prompt()

            assert "Error resolving file paths" in str(exc_info.value)

    def test_build_execution_prompt_plan_read_error_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that plan read error raises FileError."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("{plan_path}")
        if mock_cyclon_paths["local_plan_file"].exists():
            mock_cyclon_paths["local_plan_file"].unlink()

        def open_side_effect(*args, **kwargs):
            if len(args) > 0 and "execute.md" in str(args[0]):
                import io
                return io.StringIO("{plan_path}")
            else:
                raise OSError("Read error")

        with patch('builtins.open', side_effect=open_side_effect):
            with pytest.raises(FileError) as exc_info:
                file_service.build_execution_prompt()

            assert "Error reading plan file" in str(exc_info.value)

    def test_build_execution_prompt_read_error_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that prompt read error raises FileError."""
        template_file = mock_cyclon_paths["prompts_dir"] / "execute.md"
        template_file.write_text("{user_instructions}")
        mock_cyclon_paths["local_prompt_file"].write_text("prompt")

        def open_side_effect(*args, **kwargs):
            if len(args) > 0 and "execute.md" in str(args[0]):
                import io
                return io.StringIO("{user_instructions}")
            elif len(args) > 0 and "prompt.md" in str(args[0]):
                raise OSError("Read error")
            else:
                import io
                return io.StringIO("")

        with patch('builtins.open', side_effect=open_side_effect):
            with pytest.raises(FileError) as exc_info:
                file_service.build_execution_prompt()

            assert "Error reading prompt file" in str(exc_info.value)


class TestClearSession:
    """Tests for FileService.clear_session() method."""

    def test_clear_session_no_files_no_error(self, file_service, mock_cyclon_paths):
        """Test that clearing with no files doesn't raise error."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        for item in cyclon_dir.glob("*"):
            if item.name != "config.json":
                item.unlink()

        file_service.clear_session()

        assert True

    def test_clear_session_removes_lock_file(self, file_service, mock_cyclon_paths):
        """Test that lock file is removed."""
        mock_cyclon_paths["local_lock_file"].touch()

        file_service.clear_session()

        assert not mock_cyclon_paths["local_lock_file"].exists()

    def test_clear_session_removes_context_file(self, file_service, mock_cyclon_paths):
        """Test that context file is removed."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        context_file.write_text("context")

        file_service.clear_session()

        assert not context_file.exists()

    def test_clear_session_removes_all_files_except_config(self, file_service, mock_cyclon_paths):
        """Test that all files except config.json are removed."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        
        # Ensure config.json exists before test
        if not mock_cyclon_paths["local_config_file"].exists():
            mock_cyclon_paths["local_config_file"].write_text("{}")
        
        (cyclon_dir / "test1.txt").write_text("test1")
        (cyclon_dir / "test2.txt").write_text("test2")
        mock_cyclon_paths["local_lock_file"].touch()
        mock_cyclon_paths["local_plan_file"].write_text("plan")

        file_service.clear_session()

        assert mock_cyclon_paths["local_config_file"].exists()
        assert not (cyclon_dir / "test1.txt").exists()
        assert not (cyclon_dir / "test2.txt").exists()
        assert not mock_cyclon_paths["local_lock_file"].exists()
        assert not mock_cyclon_paths["local_plan_file"].exists()

    def test_clear_session_removes_subdirectories(self, file_service, mock_cyclon_paths):
        """Test that subdirectories are removed."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        subdir = cyclon_dir / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("content")

        file_service.clear_session()

        assert not subdir.exists()

    def test_clear_session_preserves_config_file(self, file_service, mock_cyclon_paths):
        """Test that config.json is preserved."""
        config_file = mock_cyclon_paths["local_config_file"]
        config_file.write_text('{"provider": "test"}')

        file_service.clear_session()

        assert config_file.exists()
        assert config_file.read_text() == '{"provider": "test"}'

    def test_clear_session_oserror_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that OSError raises FileError."""
        cyclon_dir = mock_cyclon_paths["local_lock_file"].parent
        (cyclon_dir / "test.txt").write_text("test")

        with patch.object(Path, 'unlink', side_effect=OSError("Delete error")):
            with pytest.raises(FileError) as exc_info:
                file_service.clear_session()

            assert "Error clearing session" in str(exc_info.value)


class TestLoadContent:
    """Tests for FileService.load_content() method."""

    def test_load_content_existing_file(self, file_service, mock_cyclon_paths):
        """Test that existing file returns its content."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        test_file = cyclon_dir / "test.txt"
        test_file.write_text("File Content")

        result = file_service.load_content("test.txt")

        assert result == "File Content"

    def test_load_content_missing_file_returns_none(self, file_service, mock_cyclon_paths):
        """Test that missing file returns None."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        test_file = cyclon_dir / "nonexistent.txt"
        if test_file.exists():
            test_file.unlink()

        result = file_service.load_content("nonexistent.txt")

        assert result is None

    def test_load_content_none_filename_raises_value_error(self, file_service):
        """Test that None file_name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.load_content(None)

        assert "file_name" in str(exc_info.value)

    def test_load_content_int_filename_raises_value_error(self, file_service):
        """Test that integer file_name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_service.load_content(123)

        assert "file_name" in str(exc_info.value)

    def test_load_content_oserror_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that OSError raises FileError."""
        cyclon_dir = mock_cyclon_paths["local_config_file"].parent
        test_file = cyclon_dir / "test.txt"
        test_file.write_text("content")

        with patch('builtins.open', side_effect=OSError("Read error")):
            with pytest.raises(FileError) as exc_info:
                file_service.load_content("test.txt")

            assert "Error reading file" in str(exc_info.value)


class TestPlanExists:
    """Tests for FileService.plan_exists() method."""

    def test_plan_exists_file_exists(self, file_service, mock_cyclon_paths):
        """Test that True is returned when file exists."""
        mock_cyclon_paths["local_plan_file"].touch()

        result = file_service.plan_exists()

        assert result is True

    def test_plan_exists_file_missing(self, file_service, mock_cyclon_paths):
        """Test that False is returned when file doesn't exist."""
        if mock_cyclon_paths["local_plan_file"].exists():
            mock_cyclon_paths["local_plan_file"].unlink()

        result = file_service.plan_exists()

        assert result is False


class TestPromptExists:
    """Tests for FileService.prompt_exists() method."""

    def test_prompt_exists_file_exists(self, file_service, mock_cyclon_paths):
        """Test that True is returned when file exists."""
        mock_cyclon_paths["local_prompt_file"].touch()

        result = file_service.prompt_exists()

        assert result is True

    def test_prompt_exists_file_missing(self, file_service, mock_cyclon_paths):
        """Test that False is returned when file doesn't exist."""
        if mock_cyclon_paths["local_prompt_file"].exists():
            mock_cyclon_paths["local_prompt_file"].unlink()

        result = file_service.prompt_exists()

        assert result is False


class TestLockFileExists:
    """Tests for FileService.lock_file_exists() method."""

    def test_lock_file_exists_file_exists(self, file_service, mock_cyclon_paths):
        """Test that True is returned when file exists."""
        mock_cyclon_paths["local_lock_file"].touch()

        result = file_service.lock_file_exists()

        assert result is True

    def test_lock_file_exists_file_missing(self, file_service, mock_cyclon_paths):
        """Test that False is returned when file doesn't exist."""
        if mock_cyclon_paths["local_lock_file"].exists():
            mock_cyclon_paths["local_lock_file"].unlink()

        result = file_service.lock_file_exists()

        assert result is False


class TestCreateLockFile:
    """Tests for FileService.create_lock_file() method."""

    def test_create_lock_file_creates_file(self, file_service, mock_cyclon_paths):
        """Test that lock file is created."""
        if mock_cyclon_paths["local_lock_file"].exists():
            mock_cyclon_paths["local_lock_file"].unlink()

        file_service.create_lock_file()

        assert mock_cyclon_paths["local_lock_file"].exists()

    def test_create_lock_file_creates_directory(self, file_service, mock_cyclon_paths):
        """Test that .cyclon directory is created."""
        cyclon_dir = mock_cyclon_paths["local_lock_file"].parent
        if cyclon_dir.exists():
            import shutil
            shutil.rmtree(cyclon_dir)

        file_service.create_lock_file()

        assert cyclon_dir.exists()
        assert mock_cyclon_paths["local_lock_file"].exists()

    def test_create_lock_file_oserror_raises_file_error(self, file_service):
        """Test that OSError raises FileError."""
        with patch.object(Path, 'touch', side_effect=OSError("Create error")):
            with pytest.raises(FileError) as exc_info:
                file_service.create_lock_file()

            assert "Error creating lock file" in str(exc_info.value)


class TestRemoveLockFile:
    """Tests for FileService.remove_lock_file() method."""

    def test_remove_lock_file_removes_existing(self, file_service, mock_cyclon_paths):
        """Test that existing lock file is removed."""
        mock_cyclon_paths["local_lock_file"].touch()

        file_service.remove_lock_file()

        assert not mock_cyclon_paths["local_lock_file"].exists()

    def test_remove_lock_file_missing_no_error(self, file_service, mock_cyclon_paths):
        """Test that missing lock file doesn't raise error."""
        if mock_cyclon_paths["local_lock_file"].exists():
            mock_cyclon_paths["local_lock_file"].unlink()

        file_service.remove_lock_file()

        assert True

    def test_remove_lock_file_oserror_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that OSError raises FileError."""
        mock_cyclon_paths["local_lock_file"].touch()

        with patch.object(Path, 'unlink', side_effect=OSError("Delete error")):
            with pytest.raises(FileError) as exc_info:
                file_service.remove_lock_file()

            assert "Error removing lock file" in str(exc_info.value)


class TestContextFileExists:
    """Tests for FileService.context_file_exists() method."""

    def test_context_file_exists_file_exists(self, file_service, mock_cyclon_paths):
        """Test that True is returned when file exists."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        context_file.touch()

        result = file_service.context_file_exists()

        assert result is True

    def test_context_file_exists_file_missing(self, file_service, mock_cyclon_paths):
        """Test that False is returned when file doesn't exist."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        if context_file.exists():
            context_file.unlink()

        result = file_service.context_file_exists()

        assert result is False


class TestRemoveContextFile:
    """Tests for FileService.remove_context_file() method."""

    def test_remove_context_file_removes_existing(self, file_service, mock_cyclon_paths):
        """Test that existing context file is removed."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        context_file.touch()

        file_service.remove_context_file()

        assert not context_file.exists()

    def test_remove_context_file_missing_no_error(self, file_service, mock_cyclon_paths):
        """Test that missing context file doesn't raise error."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        if context_file.exists():
            context_file.unlink()

        file_service.remove_context_file()

        assert True

    def test_remove_context_file_oserror_raises_file_error(self, file_service, mock_cyclon_paths):
        """Test that OSError raises FileError."""
        context_file = mock_cyclon_paths["local_config_file"].parent / "context.md"
        context_file.touch()

        with patch.object(Path, 'unlink', side_effect=OSError("Delete error")):
            with pytest.raises(FileError) as exc_info:
                file_service.remove_context_file()

            assert "Error removing context file" in str(exc_info.value)
