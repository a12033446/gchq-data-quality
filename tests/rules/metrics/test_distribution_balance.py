# (c) Crown Copyright GCHQ

"""Tests for DistributionBalanceRule using YAML test cases."""

import pytest

from gchq_data_quality.rules.metrics import DistributionBalanceRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_distribution_balance(distribution_balance_case: dict) -> None:
    """Test DistributionBalanceRule with YAML-driven cases."""
    inputs, df = process_test_data_inputs_for_pandas(distribution_balance_case)
    result = DistributionBalanceRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])
