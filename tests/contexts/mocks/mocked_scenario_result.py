from dataclasses import dataclass

from vedro.core import ExcInfo
from vedro.core import ScenarioResult
from vedro.core import StepResult
from vedro.core import VirtualScenario

from contexts.mocks.mocked_python_traceback import MockedTracedFile
from contexts.mocks.mocked_python_traceback import mocked_traced_file
from helpers.vedro.scenario import make_step


@dataclass
class MockedScenarioResult:
    mocked_traced_file: MockedTracedFile
    scenario_result: ScenarioResult


def mocked_scenario_result(scenario: VirtualScenario,
                           traced_file: MockedTracedFile = None,
                           ) -> MockedScenarioResult:
    scenario_result = ScenarioResult(scenario=scenario)

    step_result = StepResult(step=make_step())

    if traced_file is None:
        traced_file = mocked_traced_file(
            filename=scenario.path,
            line_start=2,
            line_target=4,
        )
    step_result.set_exc_info(
        exc_info=ExcInfo(
            type_=traced_file.error_type,
            value=traced_file.error_type(traced_file.error_description),
            traceback=traced_file.traceback,
        )
    )

    scenario_result.add_step_result(step_result)

    return MockedScenarioResult(
        scenario_result=scenario_result,
        mocked_traced_file=traced_file,
    )
