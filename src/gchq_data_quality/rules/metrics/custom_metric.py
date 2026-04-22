# (c) Crown Copyright GCHQ

"""Custom metric rule for flexible metric calculations using pandas eval expressions."""

from typing import Literal, Self, cast

import pandas as pd
from pydantic import Field

from gchq_data_quality.models import DataQualityDimension, DamaFramework
from gchq_data_quality.rules.metrics.metric_rule import MetricRule
from gchq_data_quality.rules.utils.rules_utils import extract_columns_from_expression, evaluate_metric_expression


class CustomMetricRule(MetricRule):
    """
    Flexible metric rule using pandas eval expressions.

    Allows any pandas Series operation that returns numeric values to be used as a metric.
    The metric expression is evaluated using pandas eval() and the average value is returned.

    Attributes:
        field (str): The column to measure.
        metric_expression (str): Pandas eval expression returning numeric metric values (use backticks for column names).
        metric_name (str | None): Name of the metric being calculated (defaults to None).
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DataQualityDimension): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values.
        na_values (str | list[Any] | None): Additional values considered as missing.

    Examples:
        ```python
        # String length
        >>> rule = CustomMetricRule(
        ...     field="email",
        ...     metric_expression="`email`.str.len()",
        ...     metric_name="email_length"
        ... )
        >>> result = rule.evaluate(df)
        >>> print(result.metric_value)  # Average email length

        # Digit count in password
        >>> rule = CustomMetricRule(
        ...     field="password",
        ...     metric_expression="`password`.str.count(r'[0-9]')",
        ...     metric_name="password_digit_count"
        ... )
        >>> result = rule.evaluate(df)

        # Word count
        >>> rule = CustomMetricRule(
        ...     field="description",
        ...     metric_expression="`description`.str.count(r'\\b\\w+\\b')",
        ...     metric_name="word_count"
        ... )
        >>> result = rule.evaluate(df)

        # Mathematical operations
        >>> rule = CustomMetricRule(
        ...     field="score",
        ...     metric_expression="abs(`predicted` - `actual`)",
        ...     metric_name="prediction_error"
        ... )
        >>> result = rule.evaluate(df)
        ```

    Returns:
        DataQualityResult: Contains the average metric value,
        number of records evaluated, and no pass rate or failed records.
    """

    function: Literal["custom_metric"] = "custom_metric"
    metric_expression: str = Field(
        ...,
        description="Pandas eval expression returning numeric metric values (use backticks for column names)",
    )

    def _get_columns_used_pandas(self) -> list[str]:
        """Extract columns used in the metric expression."""
        columns_in_expression = extract_columns_from_expression(self.metric_expression)
        return list(set(columns_in_expression + [self.field]))

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Evaluate the metric expression using pandas eval.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Numeric metric values for each record.
        """
        return evaluate_metric_expression(df, self.metric_expression)

    def _coerce_dataframe_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """For custom metrics, don't coerce to string type since expressions may need different dtypes.

        Custom metrics can work with numeric, datetime, or other data types depending
        on the expression. Only coerce if specifically needed for the expression.
        """
        return df

    def _get_spark_safe_rule(self) -> Self:
        """We override the default behaviour as we additionally need to make
        the metric_expression spark_safe - in case columns refer to nested data."""
        from gchq_data_quality.spark.utils.rules_utils import (
            get_spark_safe_column_name,
            get_spark_safe_expression,
        )

        rule_copy = self.model_copy()
        rule_copy.field = get_spark_safe_column_name(self.field)
        rule_copy.metric_expression = cast(str, get_spark_safe_expression(self.metric_expression))

        return rule_copy
