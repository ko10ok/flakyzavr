from contextlib import contextmanager
from pathlib import Path
from typing import Union


@contextmanager
def temp_file(file_path: Union[str, Path], content: str):
    """
    Context manager that creates a temporary file with specified content
    and removes it on exit.

    :param file_path: Path where the file should be created
    :param content: Content to write to the file

    Usage:
        with temp_file("path/to/file.txt", "Hello World") as path:
            # file exists here
            pass
        # file is deleted here
    """
    path = Path(file_path)

    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write content to file
    path.write_text(content, encoding='utf-8')

    try:
        yield path
    finally:
        # Clean up: remove the file
        if path.exists():
            path.unlink()
