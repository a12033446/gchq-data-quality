# (c) Crown Copyright GCHQ

"""Tests for NumberRatioRule using YAML test cases."""

import pytest

from gchq_data_quality.rules.metrics import NumberRatioRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_number_ratio(number_ratio_case: dict) -> None:
    """Test NumberRatioRule with YAML-driven cases."""
    inputs, df = process_test_data_inputs_for_pandas(number_ratio_case)
    result = NumberRatioRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])
