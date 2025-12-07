from contextlib import contextmanager
from pathlib import Path


@contextmanager
def temp_file(file_path: str | Path, content: str):
    """
    Context manager that creates a temporary file with specified content
    and removes it on exit.
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
