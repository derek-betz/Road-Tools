"""IO helpers for reading Excel and CSV inputs."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from .mapping import SourceEntry, normalize_key

LOGGER = logging.getLogger(__name__)


def _coerce_path(path: Path) -> Path:
    if isinstance(path, Path):
        return path
    return Path(path)


def load_payitems_from_workbook(path: Path) -> List[SourceEntry]:
    path = _coerce_path(path)
    if not path.exists():
        LOGGER.warning("Payitems workbook %s not found", path)
        return []

    sheets = pd.read_excel(path, sheet_name=None)
    entries: List[SourceEntry] = []
    for sheet_name, df in sheets.items():
        key = normalize_key(sheet_name)
        entries.append(SourceEntry(key=key, display_name=sheet_name, kind="workbook", data=df))
    LOGGER.info("Loaded %d payitem sheets from %s", len(entries), path)
    return entries


def load_payitems_from_directory(directory: Path) -> List[SourceEntry]:
    directory = _coerce_path(directory)
    if not directory.exists() or not directory.is_dir():
        LOGGER.warning("Payitems directory %s not found", directory)
        return []

    entries: List[SourceEntry] = []
    for csv_path in sorted(directory.glob("*.csv")):
        try:
            df = pd.read_csv(csv_path)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.error("Failed to load %s: %s", csv_path, exc)
            continue
        key = normalize_key(csv_path.stem)
        entries.append(SourceEntry(key=key, display_name=csv_path.name, kind="csv", data=df))
    LOGGER.info("Loaded %d payitem csv files from %s", len(entries), directory)
    return entries


def load_historical_sources(workbook: Path, directory: Path) -> List[SourceEntry]:
    sources: List[SourceEntry] = []
    sources.extend(load_payitems_from_workbook(workbook))
    sources.extend(load_payitems_from_directory(directory))
    return sources


def read_estimate_audit_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def read_estimate_sheet(path: Path, sheet_name: str = "Estimate") -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name)


def detect_price_columns(columns: Iterable[str]) -> List[str]:
    matches: List[str] = []
    for column in columns:
        lowered = str(column).lower()
        if any(keyword in lowered for keyword in ("price", "unit_price", "unit price")):
            matches.append(column)
    return matches


@dataclass(frozen=True)
class PriceSeriesResult:
    """Container describing the extracted numeric price series."""

    values: pd.Series
    columns_used: List[str]
    used_fallback: bool

    def has_values(self) -> bool:
        return not self.values.empty


def extract_price_series(df: pd.DataFrame) -> PriceSeriesResult:
    price_columns = detect_price_columns(df.columns)
    series = pd.Series(dtype=float)
    for column in price_columns:
        numeric = pd.to_numeric(df[column], errors="coerce")
        series = pd.concat([series, numeric], ignore_index=True)
    series = series.dropna()
    if not series.empty:
        return PriceSeriesResult(series, list(price_columns), used_fallback=False)

    # Fallback to DIST_*/STATE_* columns containing price-like data
    fallback_cols: List[str] = []
    for column in df.columns:
        upper = str(column).upper()
        if upper.startswith("DIST") or upper.startswith("STATE"):
            fallback_cols.append(column)

    fallback_series = pd.Series(dtype=float)
    for column in fallback_cols:
        numeric = pd.to_numeric(df[column], errors="coerce")
        fallback_series = pd.concat([fallback_series, numeric], ignore_index=True)
    fallback_series = fallback_series.dropna()
    return PriceSeriesResult(fallback_series, fallback_cols, used_fallback=bool(fallback_cols))


__all__ = [
    "load_payitems_from_workbook",
    "load_payitems_from_directory",
    "load_historical_sources",
    "read_estimate_audit_csv",
    "read_estimate_sheet",
    "detect_price_columns",
    "PriceSeriesResult",
    "extract_price_series",
]
