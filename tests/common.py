import json
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from mythx_models.response import (
    AnalysisInputResponse,
    AnalysisSubmissionResponse,
    DetectedIssuesResponse,
)


def get_test_case(path: str, obj=None, raw=False):
    with open(str(Path(__file__).parent / path)) as f:
        if raw:
            return f.read()
        dict_data = json.load(f)

    if obj is None:
        return dict_data
    return obj.from_dict(dict_data)


@contextmanager
def mock_context(submission_response=None, issues_response=None, input_response=None):
    with patch("pythx.Client.analyze") as analyze_patch, patch(
        "pythx.Client.analysis_ready"
    ) as ready_patch, patch("pythx.Client.report") as report_patch, patch(
        "pythx.Client.request_by_uuid"
    ) as input_patch, patch(
        "solcx.compile_source"
    ) as compile_patch:
        analyze_patch.return_value = submission_response or get_test_case(
            "testdata/analysis-submission-response.json", AnalysisSubmissionResponse
        )
        ready_patch.return_value = True
        report_patch.return_value = deepcopy(issues_response) or get_test_case(
            "testdata/detected-issues-response.json", DetectedIssuesResponse
        )
        input_patch.return_value = input_response or get_test_case(
            "testdata/analysis-input-response.json", AnalysisInputResponse
        )
        compile_patch.return_value = {
            "contract": {
                "abi": "test",
                "ast": "test",
                "bin": "test",
                "bin-runtime": "test",
                "srcmap": "test",
                "srcmap-runtime": "test",
            }
        }
        yield analyze_patch, ready_patch, report_patch, input_patch, compile_patch
