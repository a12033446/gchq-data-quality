# (c) Crown Copyright GCHQ

"""Punctuation and space ratio data quality rule for detecting anomalous data."""

import string
from typing import Literal

import pandas as pd

from gchq_data_quality.rules.metrics.metric_rule import MetricRule
from gchq_data_quality.rules.metrics.utils import _apply_string_ratio_metric


class PunctuationSpaceRatioRule(MetricRule):
    """
    Rule for evaluating if the ratio of punctuation and space characters meets a threshold.

    This metric helps identify anomalous or corrupted data by measuring the proportion
    of punctuation and space characters relative to the total string length.

    The punctuation characters include: !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~
    Plus whitespace characters (spaces, tabs, newlines, etc.)

    High ratios may indicate data quality issues, such as:
    - Corrupted or garbled data
    - Incorrectly formatted fields
    - Encoding issues

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
        >>> # Flag records with more than 20% punctuation/space
        >>> rule = PunctuationSpaceRatioRule(
        ...     field="name",
        ...     threshold=0.2,
        ...     comparison=">"
        ... )
        >>> result = rule.evaluate(df)

        >>> # Ensure records have less than 5% punctuation/space
        >>> rule = PunctuationSpaceRatioRule(
        ...     field="description",
        ...     threshold=0.05,
        ...     comparison="<="
        ... )
        >>> result = rule.evaluate(df)
        ```

    Returns:
        DataQualityResult: Contains the pass rate, number of records evaluated,
        and sample of failed records where punctuation/space ratio did not meet the threshold.
    """

    function: Literal["punctuation_space_ratio"] = "punctuation_space_ratio"

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate punctuation and space character ratio for each string.

        The ratio is calculated as:
        (count of punctuation and space chars) / (total string length)

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Punctuation/space ratios for each record (0.0 to 1.0).
                      NaN for null values.
        """

        def count_punctuation_and_space(s: str) -> int:
            return sum(1 for char in s if char in string.punctuation or char.isspace())

        return _apply_string_ratio_metric(df[self.field], count_punctuation_and_space)
