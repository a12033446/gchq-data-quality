# (c) Crown Copyright GCHQ

"""Number ratio data quality rule for measuring numeric character proportion."""

from typing import Literal

import pandas as pd

from gchq_data_quality.rules.metrics.metric_rule import MetricRule
from gchq_data_quality.rules.metrics.utils import _apply_string_ratio_metric


class NumberRatioRule(MetricRule):
    """
    Rule for calculating the average ratio of numeric characters in a field.

    This metric measures the proportion of numeric digits (0-9) relative to the
    total string length. It helps identify anomalous data for example if a text field is
    suddenly a uuid or starts to have numbers.

    The rule calculates the ratio for each value in the field and returns
    the average ratio as the metric value. Null values are skipped (not evaluated).

    Attributes:
        field (str): The column containing strings to check.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> rule = NumberRatioRule(field="name")
        >>> result = rule.evaluate(df)
        >>> print(result.metric_value)  # Average number ratio
        ```

    Returns:
        DataQualityResult: Contains the average ratio as metric_value,
        number of records evaluated, and no pass rate or failed records.
    """

    function: Literal["number_ratio"] = "number_ratio"

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate numeric character ratio for each string.

        The ratio is calculated as:
        (count of numeric digits 0-9) / (total string length)

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Number ratios for each record (0.0 to 1.0).
                      NaN for null values.
        """

        def count_numeric_chars(s: str) -> int:
            return sum(1 for char in s if char.isdigit())

        return _apply_string_ratio_metric(df[self.field], count_numeric_chars)
