# (c) Crown Copyright GCHQ

"""Number ratio data quality rule for measuring numeric character proportion."""

from typing import Literal

import pandas as pd

from gchq_data_quality.rules.metrics.metric_rule import MetricRule
from gchq_data_quality.rules.metrics.utils import _apply_string_ratio_metric


class NumberRatioRule(MetricRule):
    """
    Rule for evaluating if the ratio of numeric characters meets a specified threshold.

    This metric measures the proportion of numeric digits (0-9) relative to the
    total string length. It helps identify anomalous data for example if a text field is
    suddenly a uuid or starts to have numbers.

    The rule checks if the ratio of each value in the field passes the comparison
    check against the specified threshold. Null values are skipped (not evaluated).

    Attributes:
        field (str): The column containing strings to check.
        threshold (float): The ratio threshold to compare against (0.0 to 1.0).
        comparison (Literal["<=", "<", ">=", ">"]): The comparison operator to use.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> # Flag records with more than 50% numbers (unusual for names)
        >>> rule = NumberRatioRule(
        ...     field="name",
        ...     threshold=0.5,
        ...     comparison=">"
        ... )
        >>> result = rule.evaluate(df)

        >>> # Ensure product codes have at least 30% numbers
        >>> rule = NumberRatioRule(
        ...     field="product_code",
        ...     threshold=0.3,
        ...     comparison=">="
        ... )
        >>> result = rule.evaluate(df)
        ```

    Returns:
        DataQualityResult: Contains the pass rate, number of records evaluated,
        and sample of failed records where number ratio did not meet the threshold.
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
