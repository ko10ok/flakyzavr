from types import TracebackType
from typing import Any


def list_code(traceback: TracebackType, scenario_path: str) -> str:
    f_code = traceback.tb_frame.f_code
    filename = traceback.tb_frame.f_code.co_filename
    firstlineno = f_code.co_firstlineno
    lineno = traceback.tb_frame.f_lineno

    with open(filename, 'r') as code:
        lines = [
            f'{">" if idx + 1 == lineno else " "} {str(idx + 1): >3}|{line}'
            for idx, line in enumerate(code.read().splitlines())
        ]

    if scenario_path not in filename:
        return '\n'.join(
            ['# ' + filename + ':'] +
            lines[lineno - 1:lineno]
        )

    return '\n'.join(
        ['# ' + filename + ':'] +
        lines[firstlineno - 2:lineno + 3]
    )


def render_tb(traceback: TracebackType, test_file: str) -> str:
    if traceback.tb_next:
        return list_code(traceback, test_file) + '\n\n' + render_tb(traceback.tb_next, test_file)
    return list_code(traceback, test_file)


def render_error(error: Any) -> str:
    return f'{error.__class__.__name__}{str(error)}'
