# (c) Crown Copyright GCHQ

"""Tests for EntropyRule using YAML test cases."""

import pytest

from gchq_data_quality.rules.metrics import EntropyRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_entropy(entropy_case: dict) -> None:
    """Test EntropyRule with various comparison operators and thresholds.

    Test cases are loaded from entropy.yaml file. Assumes all values in
    the 'expected' dictionary correspond directly to DataQualityResult attributes.

    Entropy is calculated using Shannon entropy: H = -sum(p_i * log2(p_i))
    where p_i is the proportion of each character in the string.
    """
    inputs, df = process_test_data_inputs_for_pandas(entropy_case)
    result = EntropyRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])


def test_entropy_invalid_comparison() -> None:
    """Invalid comparison operator should raise ValueError."""
    with pytest.raises(ValueError):
        EntropyRule(
            field="text",
            threshold=1.5,
            comparison="!=",  # Invalid comparison
        )
