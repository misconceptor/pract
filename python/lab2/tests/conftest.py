"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from lab.models import Student


@pytest.fixture
def sample_students() -> list[Student]:
    """Three students with distinct averages and one missing grade."""
    return [
        Student(1, "Alice", [90, 80, 70]),
        Student(2, "Bob", [60, 50, 40]), 
        Student(3, "Carol", [100, None, 90])
    ]


@pytest.fixture
def empty_students() -> list[Student]:
    """Empty list — convenient for edge cases."""
    return []