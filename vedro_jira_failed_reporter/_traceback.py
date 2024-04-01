from types import TracebackType
from typing import Any


def list_code(traceback: TracebackType, last=False) -> str:
    f_code = traceback.tb_frame.f_code
    filename = traceback.tb_frame.f_code.co_filename
    firstlineno = f_code.co_firstlineno
    lineno = traceback.tb_frame.f_lineno

    with open(filename, 'r') as code:
        lines = [
            f'{">" if idx + 1 == lineno else " "} {str(idx + 1): >3}|{line}'
            for idx, line in enumerate(code.read().splitlines())
        ]

    if not last:
        return '\n'.join(
            ['# ' + filename + ':'] +
            lines[lineno - 1:lineno]
        )

    return '\n'.join(
        ['# ' + filename + ':'] +
        lines[firstlineno - 2:lineno + 3]
    )


def get_traceback_entrypoint_filename(traceback: TracebackType) -> str:
    if '/scenarios/' in traceback.tb_frame.f_code.co_filename:
        return traceback.tb_frame.f_code.co_filename
    if traceback.tb_next:
        return get_traceback_entrypoint_filename(traceback.tb_next)
    return traceback.tb_frame.f_code.co_filename


def render_tb(traceback: TracebackType) -> str:
    if traceback.tb_next:
        return list_code(traceback) + '\n\n' + render_tb(traceback.tb_next)
    return list_code(traceback, True)


def render_error(error: Any) -> str:
    return f'{error.__class__.__name__}{str(error)}'
