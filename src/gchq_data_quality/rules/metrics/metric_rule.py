"""Abstract base class for metric-based data quality rules."""

from abc import abstractmethod
from typing import Literal, Self

import pandas as pd
from pydantic import Field, model_validator

from gchq_data_quality.models import DamaFramework, DataQualityDimension
from gchq_data_quality.results.models import DataQualityResult
from gchq_data_quality.rules.base import BaseRule
from gchq_data_quality.rules.utils.rules_utils import ensure_columns_exist_pandas


class MetricRule(BaseRule):
    """
    Abstract base class for metric-based data quality rules.

    MetricRule provides a common framework for rules that measure a numeric metric
    on field values and return an aggregated metric value.

    Subclasses implement the specific metric calculation by overriding
    `_get_metric_values_pandas()`.

    Attributes:
        field (str): The column to measure.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DataQualityDimension): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values.
        na_values (str | list[Any] | None): Additional values considered as missing.
    """

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

    def _evaluate_in_pandas(self, df: pd.DataFrame) -> DataQualityResult:
        """Evaluate metric rules by returning the aggregated metric value.

        Metric rules no longer perform a threshold comparison or return a pass_rate.
        Instead, they calculate the metric values per record and expose the
        aggregated metric value on the resulting DataQualityResult.
        """
        columns_used = self._get_columns_used_pandas()
        ensure_columns_exist_pandas(df, columns_used)
        df = self._copy_and_subset_dataframe(df, columns_used)
        df = self._handle_dataframe_coercion(df)
        df = self._handle_na_values_pandas(df, columns_used, self.na_values)

        metric_values = self._get_metric_values_pandas(df)
        records_evaluated = int(metric_values.notna().sum())
        metric_value = metric_values.mean()
        if pd.isna(metric_value):
            metric_value = None

        return DataQualityResult(
            field=self.field,
            data_quality_dimension=self.data_quality_dimension,
            metric=self.metric_name,
            metric_value=metric_value,
            records_evaluated=records_evaluated,
            pass_rate=None,
            rule_id=self.rule_id,
            rule_description=self.rule_description,
            rule_data=self.to_json(),
        )

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
        """Unused for metric rules.

        MetricRule returns an aggregated metric value instead of a per-record pass/fail mask.
        This default implementation returns all True so the base evaluation path remains valid
        if it is ever called indirectly.
        """
        return pd.Series(True, index=df.index)
