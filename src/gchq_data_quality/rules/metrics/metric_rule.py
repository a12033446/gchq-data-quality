# (c) Crown Copyright GCHQ

"""Abstract base class for metric-based data quality rules."""

from abc import abstractmethod
from operator import eq, ge, gt, le, lt, ne
from typing import Literal, Self

import pandas as pd
from pydantic import Field, model_validator

from gchq_data_quality.models import DamaFramework, DataQualityDimension
from gchq_data_quality.rules.base import BaseRule

# Mapping of comparison operators to their functions
_COMPARISON_OPS = {
    "==": eq,
    "!=": ne,
    "<=": le,
    "<": lt,
    ">=": ge,
    ">": gt,
}


class MetricRule(BaseRule):
    """
    Abstract base class for metric-based data quality rules.

    MetricRule provides a common framework for rules that measure a numeric metric
    on field values and compare against a threshold using a comparison operator.

    Subclasses implement the specific metric calculation by overriding
    `_get_metric_values_pandas()`. The comparison logic is handled automatically.

    Attributes:
        field (str): The column to measure.
        comparison (Literal["<=", "<", ">=", ">"]): The comparison operator to use. Defaults to >=
        threshold (int | float): The threshold value to compare the metric against.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DataQualityDimension): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values.
        na_values (str | list[Any] | None): Additional values considered as missing.
    """

    comparison: Literal["==", "!=", "<=", "<", ">=", ">"] = Field(
        default=">=", description="The comparison operator to use"
    )
    threshold: int | float = Field(
        ..., description="The threshold value to compare the metric against"
    )
    data_quality_dimension: DataQualityDimension = Field(default=DamaFramework.Metric)

    @model_validator(mode="after")
    def set_default_metric_name(self) -> Self:
        """Set metric_name to function name if not provided."""
        if self.metric_name is None:
            # Safely fetch 'function', defaulting to None if it doesn't exist
            func_name = getattr(self, "function", None)

            if func_name is not None:
                self.metric_name = func_name

        return self

    def _coerce_dataframe_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert the field to nullable string type for metric calculation.

        Uses pandas nullable string dtype ('string') to preserve NA values
        while converting non-null values to strings. This is the default
        coercion for metric rules.

        Subclasses can override if different coercion is needed.
        """
        df = df.copy()
        df[self.field] = df[self.field].astype("string")
        return df

    @abstractmethod
    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate metric values for each record in the field.

        This method must be implemented by subclasses to define what metric
        is being measured (e.g., string length, entropy, etc.).

        Args:
            df (pd.DataFrame): The DataFrame to process (contains only required columns).

        Returns:
            pd.Series: Numeric metric values for each record. Should have same length
            and index as the field column, with NaN for null values.
        """
        pass  # pragma: no cover

    def _get_records_passing_mask_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Check if metric values pass the comparison threshold.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Boolean mask where True indicates the metric
            passes the comparison check.
        """
        comparison_op = _COMPARISON_OPS[self.comparison]
        metric_values = self._get_metric_values_pandas(df)
        return comparison_op(metric_values, self.threshold)
