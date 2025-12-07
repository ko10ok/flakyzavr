from pathlib import Path
from time import monotonic_ns

from vedro import Scenario
from vedro.core import VirtualScenario
from vedro.core import VirtualStep


def make_scenario(name=None, path=None, test_dir: Path = Path('/tmp/tests')) -> VirtualScenario:
    if path is None:
        path = f"scenario_{monotonic_ns()}.py"

    class _Scenario(Scenario):
        subject = name or path
        __file__ = Path(path)

    return VirtualScenario(_Scenario, steps=[], project_dir=test_dir)


def make_step(steps=None) -> VirtualStep:
    def fn(self):
        ...

    return VirtualStep(fn)


def describe_scenario(scenario: VirtualScenario) -> dict:
    env = getattr(scenario._orig_scenario, 'env', None)
    env_desc = env.description if env else None

    desc = f"Scenario(path={scenario._orig_scenario.__name__}"
    if hasattr(scenario._orig_scenario, 'env'):
        desc += f", env={scenario._orig_scenario.env}"
    desc += ")"
    return {
        "path": scenario._orig_scenario.__name__,
        "skipped": scenario.is_skipped(),
        "env": env,
        "env_desc": env_desc,
        "description": repr(scenario),
    }
