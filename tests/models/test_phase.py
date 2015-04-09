"""Unit tests for the `models.phase` module."""
# pylint: disable=R0201,C0103,C0111

from unittest.mock import Mock

import pytest


class TestPhase:

    def test_init(self, phase):
        assert not phase.done
        assert not phase.moves


class TestPhases:

    def test_find_match(self, phases):
        phases.append(Mock())
        phases.find(1)

    def test_find_missing(self, phases):
        with pytest.raises(ValueError):
            phases.find(1)
