from __future__ import annotations

from costest.mapping import MatchResult, PayItemMapper, SourceEntry, normalize_key


def test_normalize_key_strips_non_alphanumeric():
    assert normalize_key("Item 001 - Concrete") == "ITEM001CONCRETE"
    assert normalize_key(" item\t002 ") == "ITEM002"


def test_mapper_prefers_exact_match():
    sources = [
        SourceEntry(key=normalize_key("Item001"), display_name="Item001", kind="workbook", data=None),
        SourceEntry(key=normalize_key("Item004History"), display_name="Item004 History", kind="workbook", data=None),
    ]
    mapper = PayItemMapper(sources)
    result = mapper.match("ITEM-001")
    assert isinstance(result, MatchResult)
    assert result.status == "exact"
    assert result.score == 3
    assert result.primary is sources[0]
    assert [entry.display_name for entry in result.matches] == ["Item001"]


def test_mapper_fuzzy_match_when_no_exact():
    sources = [
        SourceEntry(key=normalize_key("ITEM004HISTORY"), display_name="Item004 History", kind="workbook", data=None),
        SourceEntry(key=normalize_key("OTHER"), display_name="Other", kind="csv", data=None),
    ]
    mapper = PayItemMapper(sources)
    result = mapper.match("ITEM 004")
    assert result.status == "fuzzy"
    assert result.score >= 1
    assert result.primary is sources[0]


def test_mapper_returns_none_for_unknown():
    mapper = PayItemMapper([])
    result = mapper.match("UNKNOWN")
    assert result.matches == []
    assert result.status == "unmatched"
    assert result.score == 0


def test_mapper_returns_all_exact_matches():
    sources = [
        SourceEntry(key=normalize_key("Item001"), display_name="Item001 sheet", kind="workbook", data=None),
        SourceEntry(key=normalize_key("Item001"), display_name="item001.csv", kind="csv", data=None),
        SourceEntry(key=normalize_key("Other"), display_name="Other", kind="csv", data=None),
    ]
    mapper = PayItemMapper(sources)
    result = mapper.match("Item 001")
    assert result.status == "exact"
    assert result.score == 3
    assert len(result.matches) == 2
    assert {entry.display_name for entry in result.matches} == {"Item001 sheet", "item001.csv"}
