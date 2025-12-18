from dataclasses import dataclass
from pathlib import Path
from typing import Type
from unittest.mock import Mock


@dataclass
class MockedTracedFile:
    filename: Path
    file_content: str
    line_start: int
    line_target: int
    traceback: Mock
    error_type: Type[Exception]
    error_description: str = None
    next_traceback: 'MockedTracedFile' = None


def mocked_traced_file(
    filename: Path,
    line_start: int,
    line_target: int,
    next_traceback: MockedTracedFile = None,
    file_content: str = None,
    error_type: Type[Exception] = AssertionError,
    error_description: str = "Should be equal 1, 3 given",
) -> MockedTracedFile:
    tb_frame = Mock()
    tb_frame.f_lineno = line_target
    tb_frame.f_code = Mock()
    tb_frame.f_code.co_filename = str(filename)
    tb_frame.f_code.co_firstlineno = line_start

    if file_content is None:
        file_content = '\n'.join([
            f'line {line_no}' for line_no in range(1, 20)
        ])

    traceback = Mock()
    traceback.tb_next = None

    if next_traceback:
        traceback.tb_next = next_traceback.traceback

    traceback.tb_frame = tb_frame

    return MockedTracedFile(
        filename=filename,
        file_content=file_content,
        line_start=line_start,
        line_target=line_target,
        traceback=traceback,
        error_type=error_type,
        error_description=error_description,
        next_traceback=next_traceback,
    )
