"""Tests for the difficulty multiplier."""

from renovation_quote.models.difficulty import (
    MAX_MULTIPLIER,
    MIN_MULTIPLIER,
    Condition,
    DifficultyMultiplier,
)


def test_baseline_is_one():
    d = DifficultyMultiplier(floor=1, has_elevator=True, building_age=5, condition=Condition.NORMAL)
    assert d.value == 1.0


def test_elevator_cancels_floor_penalty():
    d = DifficultyMultiplier(floor=8, has_elevator=True)
    assert d.floor_factor == 0.0


def test_walkup_high_floor_adds_penalty():
    d = DifficultyMultiplier(floor=5, has_elevator=False)
    assert d.floor_factor == (5 - 3) * 0.05


def test_old_building_adds_age_factor():
    assert DifficultyMultiplier(building_age=31).age_factor == 0.10
    assert DifficultyMultiplier(building_age=30).age_factor == 0.0


def test_condition_weights():
    assert DifficultyMultiplier(condition=Condition.SEVERE).condition_factor == 0.15


def test_multiplier_is_clamped():
    d = DifficultyMultiplier(
        floor=20, has_elevator=False, building_age=99, condition=Condition.SEVERE
    )
    assert d.value == MAX_MULTIPLIER


def test_multiplier_never_below_one():
    d = DifficultyMultiplier(floor=1, has_elevator=True, building_age=0)
    assert d.value >= MIN_MULTIPLIER
