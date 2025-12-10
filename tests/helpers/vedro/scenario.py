from pathlib import Path
from time import monotonic_ns

from vedro import Scenario
from vedro.core import VirtualScenario
from vedro.core import VirtualStep


def make_scenario(name=None, rel_path: Path = None, tests_dir: Path = Path('/tmp/tests')) -> VirtualScenario:
    if rel_path is None:
        rel_path = f"scenario_{monotonic_ns()}.py"

    class _Scenario(Scenario):
        subject = name or rel_path
        __file__ = Path(tests_dir) / Path(rel_path)

    return VirtualScenario(_Scenario, steps=[], project_dir=tests_dir)


def make_step(steps=None) -> VirtualStep:
    def fn(self):
        ...

    return VirtualStep(fn)
