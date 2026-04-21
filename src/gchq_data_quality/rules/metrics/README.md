# Metrics Rules

This folder contains metric-based data quality rules that inherit from `MetricRule`.

## Overview

Metric rules are a small family of rules that calculate a numeric metric per record and then compare that metric against a threshold using an operator.

Common behavior is handled by `MetricRule`:
- default string coercion for the target field
- comparison operator support: `<=`, `<`, `>=`, `>`
- shared evaluation logic from `BaseRule`

Concrete metric rules only need to implement the metric calculation.

## Current rules

- `StringLengthRule`
  - Checks the length of a string value
  - Uses `threshold` and `comparison` to decide whether each record passes
  - Example: string length must be `>= 5`

- `EntropyRule`
  - Calculates Shannon entropy for each string
  - Uses `threshold` and `comparison` to test string unpredictability
  - Example: entropy must be `>= 2.0`

## How it works

`MetricRule` provides:
- `comparison: Literal["<=", "<", ">=", ">"]`
- `threshold: int | float`
- `_coerce_dataframe_type()` that casts the field to pandas nullable string
- `_get_records_passing_mask_pandas()` which compares metric values to the threshold

A subclass must implement:
- `_get_metric_values_pandas(df: pd.DataFrame) -> pd.Series`

The returned series should contain one numeric metric value per record, with `NaN` for missing values.

## Adding a new metric rule

1. Create a new file in this folder, e.g. `my_metric.py`.
2. Import `MetricRule` and subclass it.
3. Set `function` to a unique string.
4. Override `_get_metric_values_pandas()`.
5. Optionally override `_coerce_dataframe_type()` if the metric needs a different input type.

### Example

```python
from typing import Literal

import pandas as pd
from pydantic import Field

from gchq_data_quality.models import DamaFramework, DataQualityDimension
from gchq_data_quality.rules.metrics.metric_rule import MetricRule


class VowelCountRule(MetricRule):
    function: Literal["vowel_count"] = "vowel_count"
    data_quality_dimension: DataQualityDimension = Field(
        default=DamaFramework.Validity
    )

    def _get_metric_values_pandas(self, df: pd.DataFrame) -> pd.Series:
        values = df[self.field].str.lower()
        return values.str.count("[aeiou]")
```

## Testing

Use the existing YAML-driven pattern in `tests/data/` and `tests/rules/`.
- Add a new file in `tests/data/` named after the rule, e.g. `vowel_count.yaml`
- Add a test file in `tests/rules/` using the generated fixture `vowel_count_case`

This ensures consistency with the rest of the repository.
