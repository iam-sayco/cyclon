"""Unit tests for ProcessService."""

from unittest.mock import MagicMock, patch

import pytest

from cyclon.exceptions import ProcessError


# Helper to make async tests terminate quickly
async def quick_await(*args, **kwargs):
    """Quick await helper for async tests to terminate immediately."""
    return ""


class TestInit:
    """Tests for ProcessService.__init__() method."""

    def test_init_initializes_attributes(self, process_service):
        """Test that all attributes are initialized correctly."""
        assert process_service.current_pty is None
        assert process_service.should_stop_processing is False
        assert process_service._terminal_widget is None
        assert process_service._write_callback is None
        assert process_service._pty_changed_callback is None

    def test_current_pty_is_none_initially(self, process_service):
        """Test that current_pty is None initially."""
        assert process_service.current_pty is None

    def test_should_stop_processing_is_false_initially(self, process_service):
        """Test that should_stop_processing is False initially."""
        assert process_service.should_stop_processing is False

    def test_callbacks_are_none_initially(self, process_service):
        """Test that all callbacks are None initially."""
        assert process_service._terminal_widget is None
        assert process_service._write_callback is None
        assert process_service._pty_changed_callback is None


class TestSetTerminalWidget:
    """Tests for ProcessService.set_terminal_widget() method."""

    def test_set_terminal_widget_sets_widget(self, process_service):
        """Test that terminal widget is set correctly."""
        widget = MagicMock()
        process_service.set_terminal_widget(widget)

        assert process_service._terminal_widget == widget

    def test_set_terminal_widget_can_set_none(self, process_service):
        """Test that widget can be set to None."""
        process_service.set_terminal_widget(None)

        assert process_service._terminal_widget is None


class TestSetPtyChangedCallback:
    """Tests for ProcessService.set_pty_changed_callback() method."""

    def test_set_pty_changed_callback_sets_callback(self, process_service):
        """Test that callback is set correctly."""
        callback = MagicMock()
        process_service.set_pty_changed_callback(callback)

        assert process_service._pty_changed_callback == callback

    def test_set_pty_changed_callback_can_set_none(self, process_service):
        """Test that callback can be set to None."""
        process_service.set_pty_changed_callback(None)

        assert process_service._pty_changed_callback is None


class TestCheckException:
    """Tests for ProcessService.check_exception() method."""

    def test_check_exception_found_returns_true(self, process_service):
        """Test that True is returned when exception is found."""
        result = process_service.check_exception(
            "Error: Something went wrong", ["Error:", "Exception"]
        )

        assert result is True

    def test_check_exception_not_found_returns_false(self, process_service):
        """Test that False is returned when exception is not found."""
        result = process_service.check_exception("Normal output", ["Error:", "Exception"])

        assert result is False

    def test_check_exception_empty_list_returns_false(self, process_service):
        """Test that False is returned for empty exception list."""
        result = process_service.check_exception("Some output", [])

        assert result is False

    def test_check_exception_multiple_strings(self, process_service):
        """Test that multiple exception strings work correctly."""
        result = process_service.check_exception(
            "Traceback: Something", ["Error:", "Exception", "Traceback:"]
        )

        assert result is True

    def test_check_exception_partial_match_returns_true(self, process_service):
        """Test that substring match works correctly."""
        result = process_service.check_exception("Error: Something went wrong here", ["Error"])

        assert result is True


class TestRunProviderProcess:
    """Tests for ProcessService.run_provider_process() method."""

    @pytest.mark.asyncio
    async def test_run_provider_process_success(
        self, process_service, mock_pty_process, auto_await_mode
    ):
        """Test that successful execution returns (0, output)."""
        mock_pty_process.isalive.side_effect = [True, False]
        mock_pty_process.wait.return_value = 0

        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn", return_value=mock_pty_process
        ):
            returncode, output = await process_service.run_provider_process(
                ["echo", "test"], timeout=10
            )

            assert returncode == 0

    @pytest.mark.asyncio
    async def test_run_provider_process_file_not_found(self, process_service, auto_await_mode):
        """Test that FileNotFoundError returns (-1, error_msg)."""
        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn",
            side_effect=FileNotFoundError("Command not found"),
        ):
            output_callback = MagicMock()
            returncode, output = await process_service.run_provider_process(
                ["nonexistent", "command"], timeout=10, output_callback=output_callback
            )

            assert returncode == -1
            # output is empty when auto_await_mode raises EOFError
            # But callback should be called
            assert output_callback.called

    @pytest.mark.asyncio
    async def test_run_provider_process_process_error(self, process_service, auto_await_mode):
        """Test that ProcessError returns (-1, error_msg)."""
        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn",
            side_effect=ProcessError("Process error"),
        ):
            output_callback = MagicMock()
            returncode, output = await process_service.run_provider_process(
                ["test", "cmd"], timeout=10, output_callback=output_callback
            )

            assert returncode == -1
            # output is empty when auto_await_mode raises EOFError
            # But callback should be called
            assert output_callback.called

    @pytest.mark.asyncio
    async def test_run_provider_process_empty_command_raises_value_error(
        self, process_service, auto_await_mode
    ):
        """Test that empty command list raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await process_service.run_provider_process([], timeout=10)

        assert "command" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_provider_process_none_in_command_raises_value_error(
        self, process_service, auto_await_mode
    ):
        """Test that None in command raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await process_service.run_provider_process(["test", None], timeout=10)

        assert "command" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_provider_process_timeout_zero_raises_value_error(
        self, process_service, auto_await_mode
    ):
        """Test that timeout=0 raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await process_service.run_provider_process(["test"], timeout=0)

        assert "timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_provider_process_timeout_negative_raises_value_error(
        self, process_service, auto_await_mode
    ):
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await process_service.run_provider_process(["test"], timeout=-1)

        assert "timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_provider_process_timeout_string_raises_value_error(
        self, process_service, auto_await_mode
    ):
        """Test that string timeout raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await process_service.run_provider_process(["test"], timeout="10")

        assert "timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_run_provider_process_calls_output_callback_on_error(
        self, process_service, auto_await_mode
    ):
        """Test that output_callback is called on error."""
        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn",
            side_effect=Exception("Test error"),
        ):
            output_callback = MagicMock()
            await process_service.run_provider_process(
                ["test"], timeout=10, output_callback=output_callback
            )

            assert output_callback.called
            assert "Error" in output_callback.call_args[0][0]

    @pytest.mark.asyncio
    async def test_run_provider_process_calls_pty_callback(
        self, process_service, mock_pty_process, auto_await_mode
    ):
        """Test that pty_changed_callback is called on start and end."""
        mock_pty_process.isalive.return_value = False
        mock_pty_process.wait.return_value = 0

        pty_callback = MagicMock()
        process_service.set_pty_changed_callback(pty_callback)

        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn", return_value=mock_pty_process
        ):
            await process_service.run_provider_process(["test"], timeout=10)

            assert pty_callback.call_count == 2  # Start and end

    @pytest.mark.asyncio
    async def test_run_provider_process_sets_write_callback(
        self, process_service, mock_pty_process, auto_await_mode
    ):
        """Test that write_callback is set and cleared."""
        mock_widget = MagicMock()
        mock_widget.set_write_callback = MagicMock()
        process_service.set_terminal_widget(mock_widget)

        mock_pty_process.isalive.return_value = False
        mock_pty_process.wait.return_value = 0

        with patch(
            "cyclon.services.process_service.PtyProcessUnicode.spawn", return_value=mock_pty_process
        ):
            await process_service.run_provider_process(["test"], timeout=10)

            assert mock_widget.set_write_callback.call_count >= 2


class TestStopProcess:
    """Tests for ProcessService.stop_process() method."""

    def test_stop_process_no_process_no_error(self, process_service):
        """Test that stopping with no process doesn't raise error."""
        process_service.stop_process()

        assert True

    def test_stop_process_terminates_running_process(self, process_service, mock_pty_process):
        """Test that running process is terminated."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        with patch("cyclon.services.process_service.time.sleep"):
            process_service.stop_process()

            mock_pty_process.terminate.assert_called_once()

    def test_stop_process_force_kills_unresponsive_process(self, process_service, mock_pty_process):
        """Test that unresponsive process is killed with SIGKILL."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        with patch("cyclon.services.process_service.time.sleep"):
            process_service.stop_process()

            mock_pty_process.kill.assert_called_once()

    def test_stop_process_clears_current_pty(self, process_service, mock_pty_process):
        """Test that current_pty is cleared."""
        mock_pty_process.isalive.return_value = False
        process_service.current_pty = mock_pty_process

        process_service.stop_process()

        assert process_service.current_pty is None

    def test_stop_process_calls_pty_callback(self, process_service, mock_pty_process):
        """Test that pty_changed_callback is called."""
        mock_pty_process.isalive.return_value = False
        process_service.current_pty = mock_pty_process

        pty_callback = MagicMock()
        process_service.set_pty_changed_callback(pty_callback)

        process_service.stop_process()

        pty_callback.assert_called_once()


class TestWriteToProcess:
    """Tests for ProcessService.write_to_process() method."""

    def test_write_to_process_writes_to_pty(self, process_service, mock_pty_process):
        """Test that text is written to active PTY."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        process_service.write_to_process("test text")

        mock_pty_process.write.assert_called_once_with("test text\n")

    def test_write_to_process_adds_newline(self, process_service, mock_pty_process):
        """Test that newline is added to text."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        process_service.write_to_process("command")

        mock_pty_process.write.assert_called_once_with("command\n")

    def test_write_to_process_no_process_no_write(self, process_service):
        """Test that nothing is written when no process is running."""
        process_service.write_to_process("text")

        assert True

    def test_write_to_process_dead_process_no_write(self, process_service, mock_pty_process):
        """Test that nothing is written to dead process."""
        mock_pty_process.isalive.return_value = False
        process_service.current_pty = mock_pty_process

        process_service.write_to_process("text")

        mock_pty_process.write.assert_not_called()

    def test_write_to_process_empty_text_no_write(self, process_service, mock_pty_process):
        """Test that empty text doesn't write."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        process_service.write_to_process("")

        mock_pty_process.write.assert_not_called()

    def test_write_to_process_none_raises_value_error(self, process_service):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            process_service.write_to_process(None)

        assert "text" in str(exc_info.value)

    def test_write_to_process_int_raises_value_error(self, process_service):
        """Test that integer raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            process_service.write_to_process(123)

        assert "text" in str(exc_info.value)

    def test_write_to_process_oserror_raises_process_error(self, process_service, mock_pty_process):
        """Test that OSError raises ProcessError."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process
        mock_pty_process.write.side_effect = OSError("Write error")

        with pytest.raises(ProcessError) as exc_info:
            process_service.write_to_process("text")

        assert "Error writing to process" in str(exc_info.value)


class TestIsProcessRunning:
    """Tests for ProcessService.is_process_running() method."""

    def test_is_process_running_no_process_returns_false(self, process_service):
        """Test that False is returned when no process is running."""
        result = process_service.is_process_running()

        assert result is False

    def test_is_process_running_dead_process_returns_false(self, process_service, mock_pty_process):
        """Test that False is returned for dead process."""
        mock_pty_process.isalive.return_value = False
        process_service.current_pty = mock_pty_process

        result = process_service.is_process_running()

        assert result is False

    def test_is_process_running_alive_process_returns_true(self, process_service, mock_pty_process):
        """Test that True is returned for alive process."""
        mock_pty_process.isalive.return_value = True
        process_service.current_pty = mock_pty_process

        result = process_service.is_process_running()

        assert result is True


class TestGetProcessPid:
    """Tests for ProcessService.get_process_pid() method."""

    def test_get_process_pid_no_process_returns_none(self, process_service):
        """Test that None is returned when no process is running."""
        result = process_service.get_process_pid()

        assert result is None

    def test_get_process_pid_returns_pid(self, process_service, mock_pty_process):
        """Test that PID is returned for running process."""
        mock_pty_process.pid = 12345
        process_service.current_pty = mock_pty_process

        result = process_service.get_process_pid()

        assert result == 12345
