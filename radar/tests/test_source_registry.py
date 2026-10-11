from radar.source_registry import GROUPS, SOURCES, sources_for_group


def test_weekly_group_has_the_three_api_sources() -> None:
    assert [s.name for s in sources_for_group("weekly")] == ["koinno", "eu_portal", "ted"]


def test_every_group_member_is_a_registered_source() -> None:
    for names in GROUPS.values():
        assert all(name in SOURCES for name in names)


def test_unknown_group_raises_a_clear_error() -> None:
    import pytest

    with pytest.raises(ValueError, match="unknown group"):
        sources_for_group("daily")


def test_koinno_shows_everything_new_because_it_is_a_small_curated_list() -> None:
    assert SOURCES["koinno"].shows_everything_new is True
    assert SOURCES["ted"].shows_everything_new is False
