# (c) Crown Copyright GCHQ

"""Distribution balance data quality rule for measuring value distribution imbalance."""

from typing import Literal

import pandas as pd

from gchq_data_quality.rules.metrics.metric_rule import MetricRule


class DistributionBalanceRule(MetricRule):
    """
    Rule for measuring the balance of value distribution in a field.

    This metric quantifies how far a column's value distribution is from perfect balance.
    A perfectly balanced distribution would have each unique value appearing with equal
    frequency. The metric calculates the sum of positive distances (over-representations)
    between actual and ideal proportions.

    The balance distance is calculated as:
    - Ideal proportion for each unique value = 1 / number_of_unique_values
    - Actual proportion = count_of_value / total_count
    - Distance_to_balance = sum(max(actual_proportion - ideal_proportion, 0))

    A score of 0 indicates perfect balance. Higher scores indicate greater imbalance.
    The same balance metric is assigned to each record, with the mean taken as the
    final metric value.

    Attributes:
        field (str): The column to measure balance for.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> rule = DistributionBalanceRule(field="category")
        >>> result = rule.evaluate(df)
        >>> print(result.metric_value)  # Balance distance score (0 = perfect balance)
        ```

    Returns:
        DataQualityResult: Contains the distribution balance distance as metric_value,
        number of records evaluated, and no pass rate or failed records.

    Note:
        Null values are excluded from the distribution calculation but count towards
        the records evaluated. Empty distributions (all nulls) return NaN as metric value.
    """

    function: Literal["distribution_balance"] = "distribution_balance"

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate distribution balance distance for each record in the field.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Distribution balance distance for each record.
                      Same value assigned to all non-null records.
                      NaN for null values.
        """
        field_data = df[self.field]

        # Get value counts and proportions, excluding NaN
        value_counts = field_data.value_counts()

        # If all values are null, return NaN series
        if len(value_counts) == 0:
            return pd.Series(float("nan"), index=df.index)

        # Calculate actual proportions
        actual_proportions = value_counts / field_data.notna().sum()

        # Calculate ideal proportion (perfect balance)
        num_unique = len(value_counts)
        ideal_proportion = 1.0 / num_unique

        # Calculate distance to balance: sum of positive differences
        # (only counting over-representation, not under-representation)
        positive_distances = (actual_proportions - ideal_proportion).clip(lower=0)
        balance_distance = positive_distances.sum()

        # Assign the same balance_distance to all records (null=NaN, non-null=balance_distance)
        result = pd.Series(index=df.index, dtype="float64")
        result[field_data.notna()] = balance_distance
        result[field_data.isna()] = float("nan")

        return result
