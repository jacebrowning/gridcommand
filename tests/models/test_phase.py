"""Unit tests for the `models.phase` module."""
# pylint: disable=R0201,C0103,C0111

import pytest

from gridcommand.models.phase import Phases


class TestPhase:

    def test_init(self, phase):
        assert not phase.done
        assert not phase.moves


class TestPhases:

    def test_current(self, phases):
        assert phases.current

    def test_current_none(self):
        assert None is Phases().current

    def test_find_match(self, phases):
        phases.find(1)

    def test_find_missing(self, player):
        with pytest.raises(ValueError):
            player.phases.find(1)
