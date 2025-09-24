"""Mapping helpers between pay item codes and historical sources."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

NORMALIZE_PATTERN = re.compile(r"[^0-9A-Za-z]+")


def normalize_key(value: str) -> str:
    """Normalise item codes and sheet names for matching."""

    if value is None:
        return ""
    collapsed = NORMALIZE_PATTERN.sub("", value)
    return collapsed.upper()


@dataclass(frozen=True)
class SourceEntry:
    """Represents a historical dataset source (sheet or csv)."""

    key: str
    display_name: str
    kind: str
    data: object


@dataclass(frozen=True)
class MatchResult:
    """Outcome of attempting to align an item code with known sources."""

    matches: List[SourceEntry]
    status: str
    score: int

    @property
    def primary(self) -> Optional[SourceEntry]:
        """Return the first matched source, if any."""

        return self.matches[0] if self.matches else None


class PayItemMapper:
    """Best-effort matcher from item codes to available sources."""

    def __init__(self, sources: Iterable[SourceEntry]):
        self._sources: List[SourceEntry] = list(sources)
        self._by_key: dict[str, List[SourceEntry]] = {}
        for entry in self._sources:
            if not entry.key:
                continue
            self._by_key.setdefault(entry.key, []).append(entry)

    def match(self, item_code: str) -> MatchResult:
        """Return matching sources, status, and score for the provided item."""

        normalised_code = normalize_key(item_code)
        if not normalised_code:
            return MatchResult([], "empty", 0)

        if normalised_code in self._by_key:
            return MatchResult(list(self._by_key[normalised_code]), "exact", 3)

        best_keys: List[str] = []
        best_score = -1
        for key in self._by_key:
            score = self._score(key, normalised_code)
            if score > best_score:
                best_keys = [key]
                best_score = score
            elif score == best_score and score > 0:
                best_keys.append(key)

        if best_score <= 0:
            return MatchResult([], "unmatched", 0)

        matches: List[SourceEntry] = []
        seen: set[int] = set()
        for key in best_keys:
            for entry in self._by_key.get(key, []):
                if id(entry) in seen:
                    continue
                seen.add(id(entry))
                matches.append(entry)
        return MatchResult(matches, "fuzzy", best_score)

    @staticmethod
    def _score(source_key: str, target_key: str) -> int:
        if not source_key or not target_key:
            return -1
        if source_key == target_key:
            return 3
        if source_key.startswith(target_key) or target_key.startswith(source_key):
            return 2
        if target_key in source_key or source_key in target_key:
            return 1
        return -1


__all__ = ["normalize_key", "SourceEntry", "MatchResult", "PayItemMapper"]
