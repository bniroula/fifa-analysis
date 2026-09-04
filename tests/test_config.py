"""Tests for the tournament metadata config."""

from __future__ import annotations

from fifa import config


def test_nine_tournaments_1994_to_2026():
    assert len(config.TOURNAMENTS) == 9
    assert config.TOURNAMENT_YEARS == (
        1994,
        1998,
        2002,
        2006,
        2010,
        2014,
        2018,
        2022,
        2026,
    )


def test_group_plus_knockout_equals_total():
    for t in config.TOURNAMENTS:
        assert t.group_matches + t.knockout_matches == t.total_matches


def test_expected_scope_total_is_604():
    assert sum(t.total_matches for t in config.TOURNAMENTS) == 604


def test_hosts_lookup():
    assert config.hosts_for(2018) == frozenset({"Russia"})
    assert config.hosts_for(2002) == frozenset({"South Korea", "Japan"})
    assert config.hosts_for(2026) == frozenset({"United States", "Canada", "Mexico"})
    assert config.hosts_for(1234) == frozenset()
