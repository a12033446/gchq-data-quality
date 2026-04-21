# (c) Crown Copyright GCHQ

"""Utility helpers for metrics-based string ratio calculations."""

from collections.abc import Callable

import pandas as pd
from pandas._libs.missing import NAType


def _apply_string_ratio_metric(
    series: pd.Series, count_fn: Callable[[str], int]
) -> pd.Series:
    """Apply a ratio metric to each string in a pandas Series.

    Null values are preserved as pd.NA. Empty strings are treated as 0.0.

    Args:
        series (pd.Series): String values to evaluate.
        count_fn (Callable[[str], int]): Function that returns the count of
            matching characters for a given string.

    Returns:
        pd.Series: Ratio values for each record.
    """

    def calculate_ratio(s: str) -> float | NAType:
        if pd.isna(s):
            return pd.NA
        if len(s) == 0:
            return 0.0
        return count_fn(s) / len(s)

    return series.apply(calculate_ratio)
