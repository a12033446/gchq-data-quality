# (c) Crown Copyright GCHQ

"""Tests for StringLengthRule using YAML test cases."""

import pytest

from gchq_data_quality.rules.metrics import StringLengthRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_string_length(string_length_case: dict) -> None:
    """Test StringLengthRule calculates average string length.

    Test cases are loaded from string_length.yaml file. Assumes all values in
    the 'expected' dictionary correspond directly to DataQualityResult attributes.

    For example, if the YAML contains:
        expected:
            metric_value: 8.5
            records_evaluated: 5

    Then we verify that result.metric_value == 8.5 and result.records_evaluated == 5
    """
    inputs, df = process_test_data_inputs_for_pandas(string_length_case)
    result = StringLengthRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])
