# (c) Crown Copyright GCHQ

"""String length data quality rule for validating field length constraints."""

from typing import Literal

import pandas as pd
from pydantic import field_validator

from gchq_data_quality.rules.metrics.metric_rule import MetricRule


class StringLengthRule(MetricRule):
    """
    Rule for calculating the average string length in a field.

    The rule calculates the string length for each value in the field and returns
    the average length as the metric value. Null values are skipped (not evaluated).
    Non-string values are coerced to strings before length calculation.

    Attributes:
        field (str): The column containing strings to check.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> rule = StringLengthRule(field="email")
        >>> result = rule.evaluate(df)
        >>> print(result.metric_value)  # Average string length
        ```

    Returns:
        DataQualityResult: Contains the average string length as metric_value,
        number of records evaluated, and no pass rate or failed records.
    """

    function: Literal["string_length"] = "string_length"

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate string length for each value in the field.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: String lengths for each record.
        """
        return df[self.field].str.len()
