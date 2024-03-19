from types import TracebackType
from typing import Any


def list_code(traceback: TracebackType) -> str:
    f_code = traceback.tb_frame.f_code
    filename = traceback.tb_frame.f_code.co_filename
    exec_line_num = f_code.co_firstlineno
    with open(filename, 'r') as code:
        lines = [
            f'{">" if idx == exec_line_num else " "} {str(idx): >3}|{line}'
            for idx, line in enumerate(code.read().splitlines())
        ]

    return '\n'.join(
        ['# ' + filename + ':'] +
        lines[exec_line_num - 2:exec_line_num + 5]
    )


def render_tb(traceback: TracebackType) -> str:
    if traceback.tb_next:
        return render_tb(traceback.tb_next)
    return list_code(traceback)


def render_error(error: Any) -> str:
    return f'{error.__class__.__name__}{str(error)}'
