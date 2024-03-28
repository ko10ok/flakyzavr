import os

path = os.path.abspath(os.path.dirname(__file__))


def get_version(filename: str = f'{path}/version') -> str:
    return open(filename, "r").read().strip()
