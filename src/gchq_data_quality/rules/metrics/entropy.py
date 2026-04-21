# (c) Crown Copyright GCHQ

"""Entropy measurement data quality rule for validating string entropy."""

from typing import Literal

import numpy as np
import pandas as pd

from gchq_data_quality.rules.metrics.metric_rule import MetricRule


class EntropyRule(MetricRule):
    """
    Rule for evaluating if string entropy meets a specified threshold.

    Shannon entropy is calculated for each string based on character frequency:
    H = -sum(p_i * log2(p_i)) where p_i is the proportion of each character.

    High entropy indicates high character diversity (less predictable).
    Low entropy indicates low character diversity (more predictable).

    The rule checks if the entropy of each value in the field passes the comparison
    check against the specified entropy threshold. Null values are skipped (not evaluated).
    Non-string values are coerced to strings before entropy calculation.

    Attributes:
        field (str): The column containing strings to check.
        threshold (float): The entropy threshold to compare against (0.0 to log2(256) ≈ 8.0).
        comparison (Literal["<=", "<", ">=", ">"]): The comparison operator to use.
        rule_id (str | None): Optional identifier for the rule.
        rule_description (str | None): Optional description of the rule.
        data_quality_dimension (DamaFramework): Associated data quality dimension.
        skip_if_null (Literal["all", "any", "never"]): Controls row skipping for null values (defaults to "any").
        na_values (str | list[Any] | None): Additional values considered as missing.

    Example:
        ```python
        >>> rule = EntropyRule(
        ...     field="password",
        ...     threshold=3.0,
        ...     comparison=">="
        ... )
        >>> result = rule.evaluate(df)

        >>> rule = EntropyRule(
        ...     field="category",
        ...     threshold=2.0,
        ...     comparison="<"
        ... )
        >>> result = rule.evaluate(df)
        ```

    Returns:
        DataQualityResult: Contains the pass rate, number of records evaluated,
        and sample of failed records where string entropy did not meet the threshold.

    Note:
        Empty strings have entropy of 0. Single character strings have entropy of 0.
        Maximum entropy increases with string length (log2(unique_chars)).
    """

    function: Literal["entropy"] = "entropy"

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Shannon entropy for each string in the field.

        Entropy is calculated as: H = -sum(p_i * log2(p_i))
        where p_i is the proportion of each character in the string.

        Args:
            df (pd.DataFrame): The DataFrame to evaluate.

        Returns:
            pd.Series: Entropy values for each record. NaN for null values.
        """

        def calculate_entropy(s: str) -> float:
            """Calculate Shannon entropy for a single string."""
            if pd.isna(s) or len(s) == 0:
                return np.nan if pd.isna(s) else 0.0

            # Count character frequencies
            char_counts = pd.Series(list(s)).value_counts()
            # Calculate probabilities
            probabilities = char_counts / len(s)
            # Calculate entropy: -sum(p * log2(p))
            entropy = -(probabilities * np.log2(probabilities)).sum()
            return entropy

        return df[self.field].apply(calculate_entropy)
