# (c) Crown Copyright GCHQ

"""String length data quality rule for validating field length constraints."""

from typing import Literal

import pandas as pd
from pydantic import field_validator

from gchq_data_quality.rules.metrics.metric_rule import MetricRule


class StringLengthRule(MetricRule):
    """
    Rule for evaluating if string length in a field meets a specified threshold.

    The rule checks if the string length of each value in the field passes the comparison
    check against the specified length threshold. Null values are skipped (not evaluated).
    Non-string values are coerced to strings before length checking.

    Attributes:
        field (str): The column containing strings to check.
        threshold (int): The length threshold to compare against (must be non-negative).
        comparison (Literal["<=", "<", ">=", ">"]): The comparison operator to use.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> rule = StringLengthRule(
        ...     field="email",
        ...     threshold=5,
        ...     comparison=">="
        ... )
        >>> result = rule.evaluate(df)

        >>> rule = StringLengthRule(
        ...     field="postal_code",
        ...     threshold=10,
        ...     comparison="<="
        ... )
        >>> result = rule.evaluate(df)
        ```

    Returns:
        DataQualityResult: Contains the pass rate, number of records evaluated,
        and sample of failed records where string length did not meet the threshold.
    """

    function: Literal["string_length"] = "string_length"

    @field_validator("threshold")
    @classmethod
    def validate_threshold_non_negative(cls, v: int | float) -> int | float:
        """Ensure threshold is a non-negative number."""
        if v < 0:
            raise ValueError("threshold must be a non-negative number")
        return v

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate string length for each value in the field.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: String lengths for each record.
        """
        return df[self.field].str.len()
