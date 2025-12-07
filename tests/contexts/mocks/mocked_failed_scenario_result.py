from dataclasses import dataclass
from pathlib import Path
from time import monotonic_ns

from d42 import fake
from vedro.core import ScenarioResult
from vedro.core import VirtualScenario

from contexts.mocks.mocked_python_traceback import MockedTracedFile
from contexts.mocks.mocked_scenario_result import MockedScenarioResult
from contexts.mocks.mocked_scenario_result import mocked_scenario_result
from helpers.vedro.scenario import make_scenario
from schemas.scenario import ScenarioNameSchema


@dataclass
class MockedFailedScenario:
    scenario: VirtualScenario
    traced_file: MockedTracedFile
    mocked_scenario_result: MockedScenarioResult
    scenario_result: ScenarioResult


def mocked_failed_scenario_result(
    scenario_name: str = None,
    scenario_project_filename: Path = None,
    traced_file: MockedTracedFile = None,
    tests_dir: Path = Path('/tmp/tests'),
):
    if scenario_name is None:
        scenario_name = fake(ScenarioNameSchema)

    if scenario_project_filename is None:
        scenario_project_filename = Path(f'scenarios/scenario_{monotonic_ns()}.py')

    scenario = make_scenario(
        name=scenario_name,
        rel_path=scenario_project_filename,
        tests_dir=tests_dir
    )

    scenario_result = mocked_scenario_result(
        scenario=scenario,
        traced_file=traced_file,
    )

    return MockedFailedScenario(
        scenario=scenario,
        traced_file=traced_file,
        mocked_scenario_result=scenario_result,
        scenario_result=scenario_result.scenario_result,
    )
