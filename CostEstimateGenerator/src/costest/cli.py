"""Command line interface for the cost estimate generator."""
from __future__ import annotations

import argparse
import logging
import math
import sys
from typing import Dict, Iterable, List, Optional, Sequence, Set

import pandas as pd

from .ai_wrapper import AIHelper
from .config import Config, load_config, read_api_key
from . import io
from .mapping import MatchResult, PayItemMapper, normalize_key
from .stats import StatsSummary, compute_summary
from .writer import update_estimate_audit, update_estimate_draft, write_mapping_debug

LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate cost estimate statistics")
    parser.add_argument("--input-payitems", dest="input_payitems", default=None, help="Directory containing historical CSV files")
    parser.add_argument("--estimate-audit-csv", dest="estimate_audit_csv", default=None, help="Path to Estimate_Audit.csv")
    parser.add_argument("--estimate-xlsx", dest="estimate_xlsx", default=None, help="Path to Estimate_Draft.xlsx")
    parser.add_argument("--payitems-workbook", dest="payitems_workbook", default=None, help="Path to PayItems workbook")
    parser.add_argument("--mapping-debug-csv", dest="mapping_debug_csv", default=None, help="Path for debug mapping csv")
    parser.add_argument("--disable-ai", action="store_true", help="Disable OpenAI assistance")
    parser.add_argument("--api-key-file", dest="api_key_file", default=None, help="File containing API key")
    parser.add_argument("--dry-run", action="store_true", help="Do not write any files")
    parser.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
    return parser


def _find_item_code_column(columns: Iterable[str]) -> Optional[str]:
    for column in columns:
        if column and "item" in column.lower() and "code" in column.lower():
            return column
    return None


def _collect_item_codes(df: pd.DataFrame) -> Set[str]:
    column = _find_item_code_column(df.columns)
    if not column:
        return set()
    series = df[column].dropna()
    return {str(value).strip() for value in series if str(value).strip()}


def _stats_to_dict(stats: StatsSummary) -> Dict[str, float]:
    return {
        "data_points": stats.data_points,
        "mean": stats.mean,
        "std_dev": stats.std_dev,
        "coef_var": stats.coef_var,
        "confidence": stats.confidence,
    }


def _combine_price_values(results: Sequence[io.PriceSeriesResult]) -> List[float]:
    values: List[float] = []
    for result in results:
        if result.has_values():
            values.extend(result.values.tolist())
    return values


def _describe_notes(match: MatchResult, results: Sequence[io.PriceSeriesResult]) -> str:
    if not match.matches:
        return "No matching historical data"
    if not any(result.has_values() for result in results):
        return "No usable prices"
    direct = any(result.has_values() and not result.used_fallback for result in results)
    fallback = any(result.has_values() and result.used_fallback for result in results)
    if direct and fallback:
        return "Mixed direct and fallback columns"
    if direct:
        return "Direct price columns"
    if fallback:
        return "Used fallback columns"
    return "No usable prices"


def _prepare_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def run(config: Config) -> int:
    LOGGER.info("Starting cost estimate generation")
    config.ensure_output_dirs()

    api_key = read_api_key(config)
    ai_helper = AIHelper(api_key=api_key, disabled=config.disable_ai)

    sources: List[SourceEntry] = io.load_historical_sources(
        config.payitems_workbook, config.input_payitems
    )
    mapper = PayItemMapper(sources)

    estimate_audit_df = io.read_estimate_audit_csv(config.estimate_audit_csv)
    item_codes = _collect_item_codes(estimate_audit_df)

    try:
        estimate_sheet_df = io.read_estimate_sheet(config.estimate_xlsx)
        item_codes.update(_collect_item_codes(estimate_sheet_df))
    except FileNotFoundError:
        LOGGER.warning("Estimate workbook %s not found; continuing without it", config.estimate_xlsx)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.error("Failed to read estimate workbook: %s", exc)

    stats_by_item: Dict[str, StatsSummary] = {}
    debug_records: List[Dict[str, object]] = []

    for item_code in sorted(item_codes):
        match = mapper.match(item_code)

        series_results: List[io.PriceSeriesResult] = []
        for entry in match.matches:
            try:
                result = io.extract_price_series(entry.data)
            except Exception as exc:  # pragma: no cover - defensive
                LOGGER.warning("Failed to extract prices from %s: %s", entry.display_name, exc)
                continue
            series_results.append(result)

        combined_prices = _combine_price_values(series_results)
        stats = compute_summary(combined_prices)

        source_names = ", ".join(entry.display_name for entry in match.matches)
        source_kinds = ", ".join(entry.kind for entry in match.matches)
        stats.source = source_names
        stats.notes = _describe_notes(match, series_results)
        stats.fallback_used = stats.fallback_used or any(result.used_fallback for result in series_results)

        if not combined_prices and match.matches:
            # No numeric data available despite a match
            stats.notes = "No usable prices"
            stats.fallback_used = True

        stats_by_item[normalize_key(item_code)] = stats

        ai_summary = ai_helper.summarize(item_code, _stats_to_dict(stats))
        record = {
            "ITEM_CODE": item_code,
            "NORMALISED_CODE": normalize_key(item_code),
            "MATCH_STATUS": match.status,
            "MATCH_SCORE": match.score,
            "MATCHED_SOURCE_COUNT": len(match.matches),
            "SOURCE_NAMES": source_names,
            "SOURCE_KINDS": source_kinds,
            "DATA_POINTS_USED": stats.data_points,
            "MEAN_UNIT_PRICE": stats.mean,
            "STD_DEV": stats.std_dev,
            "COEF_VAR": stats.coef_var if math.isfinite(stats.coef_var) else "inf",
            "CONFIDENCE": stats.confidence,
            "FALLBACK_USED": stats.fallback_used,
            "NOTES": stats.notes,
        }
        if ai_summary:
            record["AI_SUMMARY"] = ai_summary
        debug_records.append(record)

    if not config.dry_run:
        update_estimate_audit(config.estimate_audit_csv, stats_by_item, dry_run=False)
        update_estimate_draft(config.estimate_xlsx, stats_by_item, dry_run=False)
        write_mapping_debug(config.mapping_debug_csv, debug_records, dry_run=False)
    else:
        update_estimate_audit(config.estimate_audit_csv, stats_by_item, dry_run=True)
        update_estimate_draft(config.estimate_xlsx, stats_by_item, dry_run=True)
        write_mapping_debug(config.mapping_debug_csv, debug_records, dry_run=True)

    LOGGER.info("Processing complete for %d items", len(item_codes))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _prepare_logging(args.log_level)
    config = load_config(args)
    try:
        return run(config)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.exception("Pipeline failed: %s", exc)
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
