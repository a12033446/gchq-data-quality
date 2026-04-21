# (c) Crown Copyright GCHQ

"""Tests for PunctuationSpaceRatioRule using YAML test cases."""

import pytest

from gchq_data_quality.rules.metrics import PunctuationSpaceRatioRule
from tests.conftest import (
    assert_dq_result_matches_expected,
    process_test_data_inputs_for_pandas,
)


def test_punctuation_space_ratio(punctuation_space_ratio_case: dict) -> None:
    inputs, df = process_test_data_inputs_for_pandas(punctuation_space_ratio_case)
    result = PunctuationSpaceRatioRule(**inputs["inputs"]).evaluate(df)
    assert_dq_result_matches_expected(result, inputs["expected"])
