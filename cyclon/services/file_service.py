"""File operations service for Cyclon application."""

import os
import shutil

from cyclon.constants import (
    CONFIG_FILENAME,
    CONTEXT_FILENAME,
)
from cyclon.exceptions import FileError
from cyclon.paths import (
    LOCAL_CYCLON_DIR,
    LOCAL_LOCK_FILE,
    LOCAL_PLAN_FILE,
    LOCAL_PROMPT_FILE,
    LOGO_FILE,
    PROMPTS_DIR,
)
from cyclon.validation import validate_not_none, validate_string


class FileService:
    """Service for managing file operations.

    This service handles all file-related operations including reading,
    writing, and managing session files.

    Attributes:
        None

    Example:
        >>> service = FileService()
        >>> service.save_file("test.txt", "Hello World")
        >>> content = service.load_content("test.txt")
    """

    def save_file(self, file_name: str, content: str) -> None:
        """Save content to a file in .cyclon directory.

        Args:
            file_name: Name of the file to save
            content: Content to write to the file

        Raises:
            ValueError: If file_name is empty or not a string, or if content is None/not string
            FileError: If there's an error writing the file
        """
        validate_string(file_name, "file_name")
        validate_not_none(content, "content")
        validate_string(content, "content", allow_empty=True)

        try:
            LOCAL_CYCLON_DIR.mkdir(exist_ok=True)
            file_path = LOCAL_CYCLON_DIR / file_name
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            raise FileError(f"Error saving file {file_name}: {e}") from e

    def save_plan(self, plan_content: str) -> None:
        """Save plan content to plan.md.

        Args:
            plan_content: Content of the plan to save

        Raises:
            ValueError: If plan_content is None or not a string
            FileError: If there's an error writing the plan file
        """
        validate_not_none(plan_content, "plan_content")
        validate_string(plan_content, "plan_content", allow_empty=True)

        try:
            LOCAL_CYCLON_DIR.mkdir(exist_ok=True)
            with open(LOCAL_PLAN_FILE, "w", encoding="utf-8") as f:
                f.write(plan_content)
        except OSError as e:
            raise FileError(f"Error saving plan file: {e}") from e

    def load_logo(self) -> str:
        """Load logo content from logo file.

        Returns:
            str: Logo content or "CYCLON" if file doesn't exist

        Raises:
            FileError: If there's an error reading the logo file
        """
        if LOGO_FILE.exists():
            try:
                with open(LOGO_FILE, encoding="utf-8") as f:
                    return f.read()
            except OSError as e:
                raise FileError(f"Error reading logo file: {e}") from e
        return "CYCLON"

    def load_generate_prompt(self, user_prompt: str) -> str:
        """Load generation prompt template and substitute placeholders.

        Args:
            user_prompt: User's prompt to substitute in the template

        Returns:
            str: Processed prompt template with placeholders replaced

        Raises:
            ValueError: If user_prompt is None or not a string
            FileError: If there's an error reading the prompt template
        """
        validate_string(user_prompt, "user_prompt")

        prompts_file = PROMPTS_DIR / "generate.md"

        try:
            plan_file_path = str(LOCAL_PLAN_FILE.resolve())
        except OSError as e:
            raise FileError(f"Error resolving plan file path: {e}") from e

        if prompts_file.exists():
            try:
                with open(prompts_file, encoding="utf-8") as f:
                    template = f.read()

                # Use replace instead of format to avoid issues with other braces
                result = template.replace("{user_prompt}", user_prompt)
                result = result.replace("{plan_file_path}", plan_file_path)
                return result
            except OSError as e:
                raise FileError(f"Error reading prompt template: {e}") from e
        else:
            return f"Generate a detailed plan based on: {user_prompt}"

    def build_execution_prompt(self, plan_content: str | None = None) -> str:
        """Build full execution prompt combining plan and custom prompt.

        Args:
            plan_content: Optional plan content. If None, reads from plan file.

        Returns:
            str: Constructed execution prompt

        Raises:
            FileError: If there's an error reading required files
        """
        prompt_path = PROMPTS_DIR / "execute.md"

        if not prompt_path.exists():
            return "Error: prompts/execute.md not found"

        try:
            with open(prompt_path, encoding="utf-8") as f:
                template = f.read()

            plan_path = LOCAL_PLAN_FILE.resolve()
            lock_file = LOCAL_LOCK_FILE.resolve()
            context_file = (LOCAL_CYCLON_DIR.parent / ".cyclon.context.md").resolve()
        except OSError as e:
            raise FileError(f"Error resolving file paths: {e}") from e

        user_instructions = "N/A"
        if LOCAL_PROMPT_FILE.exists():
            try:
                with open(LOCAL_PROMPT_FILE, encoding="utf-8") as f:
                    user_instructions = f.read()
            except OSError as e:
                raise FileError(f"Error reading prompt file: {e}") from e

        if plan_content is None:
            try:
                with open(LOCAL_PLAN_FILE, encoding="utf-8") as f:
                    plan_content = f.read()
            except OSError as e:
                raise FileError(f"Error reading plan file: {e}") from e

        prompt = template.replace("{cwd}", os.getcwd())
        prompt = prompt.replace("{plan_path}", str(plan_path))
        prompt = prompt.replace("{lock_file}", str(lock_file))
        prompt = prompt.replace("{context_file}", str(context_file))
        prompt = prompt.replace("{user_instructions}", user_instructions)

        return prompt

    def clear_session(self) -> None:
        """Clear session by removing all session files except config.

        Removes lock file, context file, and all other files in the
        .cyclon directory except config.json.

        Raises:
            FileError: If there's an error removing files
        """
        try:
            if LOCAL_LOCK_FILE.exists():
                LOCAL_LOCK_FILE.unlink()

            context_file = LOCAL_CYCLON_DIR / CONTEXT_FILENAME
            if context_file.exists():
                context_file.unlink()

            if LOCAL_CYCLON_DIR.exists():
                for item in LOCAL_CYCLON_DIR.iterdir():
                    if item.name != CONFIG_FILENAME:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
        except OSError as e:
            raise FileError(f"Error clearing session: {e}") from e

    def load_content(self, file_name: str) -> str | None:
        """Load content from a file in .cyclon directory.

        Args:
            file_name: Name of the file to load

        Returns:
            Optional[str]: File content or None if file doesn't exist

        Raises:
            ValueError: If file_name is empty or not a string
            FileError: If there's an error reading the file
        """
        validate_string(file_name, "file_name")

        file_path = LOCAL_CYCLON_DIR / file_name
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    return f.read()
            except OSError as e:
                raise FileError(f"Error reading file {file_name}: {e}") from e
        return None

    def plan_exists(self) -> bool:
        """Check if plan.md exists.

        Returns:
            bool: True if plan file exists, False otherwise
        """
        return LOCAL_PLAN_FILE.exists()

    def prompt_exists(self) -> bool:
        """Check if prompt.md exists.

        Returns:
            bool: True if prompt file exists, False otherwise
        """
        return LOCAL_PROMPT_FILE.exists()

    def lock_file_exists(self) -> bool:
        """Check if process.lock exists.

        Returns:
            bool: True if lock file exists, False otherwise
        """
        return LOCAL_LOCK_FILE.exists()

    def create_lock_file(self) -> None:
        """Create process lock file.

        Raises:
            FileError: If there's an error creating the lock file
        """
        try:
            LOCAL_CYCLON_DIR.mkdir(exist_ok=True)
            LOCAL_LOCK_FILE.touch()
        except OSError as e:
            raise FileError(f"Error creating lock file: {e}") from e

    def remove_lock_file(self) -> None:
        """Remove process lock file.

        Raises:
            FileError: If there's an error removing the lock file
        """
        try:
            if LOCAL_LOCK_FILE.exists():
                LOCAL_LOCK_FILE.unlink()
        except OSError as e:
            raise FileError(f"Error removing lock file: {e}") from e

    def context_file_exists(self) -> bool:
        """Check if context file exists.

        Returns:
            bool: True if context file exists, False otherwise
        """
        context_file = LOCAL_CYCLON_DIR / CONTEXT_FILENAME
        return context_file.exists()

    def remove_context_file(self) -> None:
        """Remove context file.

        Raises:
            FileError: If there's an error removing the context file
        """
        try:
            context_file = LOCAL_CYCLON_DIR / CONTEXT_FILENAME
            if context_file.exists():
                context_file.unlink()
        except OSError as e:
            raise FileError(f"Error removing context file: {e}") from e
