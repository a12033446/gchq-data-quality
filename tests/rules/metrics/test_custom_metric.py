# (c) Crown Copyright GCHQ

"""Tests for CustomMetricRule using YAML test cases."""

import pandas as pd
import pytest

from gchq_data_quality.rules.metrics import CustomMetricRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_custom_metric(custom_metric_case: dict) -> None:
    """Test CustomMetricRule with various metric expressions and comparisons.

    Test cases are loaded from custom_metric.yaml file. Assumes all values in
    the 'expected' dictionary correspond directly to DataQualityResult attributes.

    For example, if the YAML contains:
        expected:
            pass_rate: 0.8
            records_evaluated: 5
            metric: "text_length"

    Then we verify that result.pass_rate == 0.8, result.records_evaluated == 5,
    and result.metric == "text_length"
    """
    inputs, df = process_test_data_inputs_for_pandas(custom_metric_case)
    result = CustomMetricRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])


def test_custom_metric_invalid_expression() -> None:
    """Invalid metric expression should raise ValueError."""
    with pytest.raises(ValueError, match="must evaluate to numeric values"):
        rule = CustomMetricRule(
            field="text",
            metric_expression="`text`.str.upper()",  # Returns string, not numeric
            comparison=">=",
            threshold=1,
        )
        df = pd.DataFrame({"text": ["hello"]})
        rule.evaluate(df)


def test_custom_metric_missing_backticks() -> None:
    """Metric expression without backticks should raise ValueError."""
    with pytest.raises(ValueError, match="No columns found in expression"):
        rule = CustomMetricRule(
            field="text",
            metric_expression="text.str.len()",  # Missing backticks
            comparison=">=",
            threshold=1,
        )
        df = pd.DataFrame({"text": ["hello"]})
        rule.evaluate(df)


def test_custom_metric_syntax_error() -> None:
    """Invalid pandas expression syntax should raise ValueError."""
    with pytest.raises(ValueError, match="Error evaluating metric expression"):
        rule = CustomMetricRule(
            field="text",
            metric_expression="`text`.invalid_method()",  # Invalid method
            comparison=">=",
            threshold=1,
        )
        df = pd.DataFrame({"text": ["hello"]})
        rule.evaluate(df)
