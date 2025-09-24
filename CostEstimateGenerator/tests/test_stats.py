from __future__ import annotations

import math

from costest import stats


def test_compute_summary_basic():
    summary = stats.compute_summary([100, 110, 105])
    assert summary.data_points == 3
    assert math.isclose(summary.mean, 105.0, rel_tol=1e-6)
    assert math.isclose(summary.std_dev, 5.0, rel_tol=1e-6)
    assert math.isclose(summary.coef_var, 5.0 / 105.0, rel_tol=1e-6)
    expected_conf = (1 - math.exp(-3 / 30.0)) * (1 / (1 + (5.0 / 105.0)))
    assert math.isclose(summary.confidence, expected_conf, rel_tol=1e-6)


def test_coefficient_of_variation_uses_floor():
    cv = stats.coefficient_of_variation(0.0, 2.0)
    assert math.isclose(cv, 2.0 / stats.MEAN_FLOOR)


def test_confidence_zero_points():
    assert stats.confidence_score(0, 1.0) == 0.0


def test_summary_no_values():
    summary = stats.compute_summary([])
    assert summary.data_points == 0
    assert summary.confidence == 0.0
    assert summary.fallback_used is True
    assert summary.cv_for_display == "N/A"
