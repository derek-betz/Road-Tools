"""Configuration helpers for the cost estimate generator."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .sample_data import create_payitems_workbook_from_template

_DEFAULT_BASE = Path(__file__).resolve().parents[2]
_DEFAULT_DATA = _DEFAULT_BASE / "data_sample"
_DEFAULT_OUTPUTS = _DEFAULT_BASE / "outputs"

LOGGER = logging.getLogger(__name__)


def _default_payitems_dir() -> Path:
    candidate = _DEFAULT_DATA / "payitems"
    if candidate.exists():
        return candidate
    fallback = _DEFAULT_BASE / "data_in"
    if fallback.exists():
        return fallback
    return candidate


def _default_payitems_workbook() -> Path:
    candidate = _DEFAULT_OUTPUTS / "PayItems_Audit.xlsx"
    if candidate.exists():
        return candidate

    template = _DEFAULT_DATA / "payitems_workbook.json"
    if template.exists():
        try:
            create_payitems_workbook_from_template(template, candidate)
            LOGGER.info("Materialised sample payitems workbook at %s", candidate)
            return candidate
        except Exception as exc:  # pragma: no cover - defensive fallback
            LOGGER.warning("Unable to materialise sample workbook: %s", exc)

    return candidate


@dataclass(frozen=True)
class Config:
    """Runtime configuration resolved from CLI arguments and environment."""

    input_payitems: Path
    estimate_audit_csv: Path
    estimate_xlsx: Path
    payitems_workbook: Path
    mapping_debug_csv: Path
    disable_ai: bool
    api_key_file: Path
    dry_run: bool

    @property
    def base_dir(self) -> Path:
        return _DEFAULT_BASE

    def ensure_output_dirs(self) -> None:
        for candidate in (
            self.estimate_audit_csv.parent,
            self.estimate_xlsx.parent,
            self.mapping_debug_csv.parent,
        ):
            candidate.mkdir(parents=True, exist_ok=True)


def _env_flag(name: str) -> bool:
    value = os.getenv(name)
    if value is None:
        return False
    return value not in {"0", "false", "False", ""}


def load_config(args: Optional[object] = None) -> Config:
    """Create a :class:`Config` from argparse ``args`` and environment."""

    disable_ai = False
    api_key_file = _DEFAULT_BASE / "API_KEY" / "API_KEY.txt"
    mapping_debug_csv = _DEFAULT_OUTPUTS / "payitem_mapping_debug.csv"

    if args is not None:
        def _resolve(value, default):
            return default if value is None else Path(value)

        input_payitems = _resolve(getattr(args, "input_payitems", None), _default_payitems_dir())
        estimate_audit_csv = _resolve(
            getattr(args, "estimate_audit_csv", None), _DEFAULT_OUTPUTS / "Estimate_Audit.csv"
        )
        estimate_xlsx = _resolve(
            getattr(args, "estimate_xlsx", None), _DEFAULT_OUTPUTS / "Estimate_Draft.xlsx"
        )
        payitems_workbook = _resolve(
            getattr(args, "payitems_workbook", None), _default_payitems_workbook()
        )
        api_key_file = _resolve(getattr(args, "api_key_file", None), api_key_file)
        mapping_debug_csv = _resolve(
            getattr(args, "mapping_debug_csv", None), mapping_debug_csv
        )
        disable_ai = getattr(args, "disable_ai", False)
        dry_run = getattr(args, "dry_run", False)
    else:
        input_payitems = _default_payitems_dir()
        estimate_audit_csv = _DEFAULT_OUTPUTS / "Estimate_Audit.csv"
        estimate_xlsx = _DEFAULT_OUTPUTS / "Estimate_Draft.xlsx"
        payitems_workbook = _default_payitems_workbook()
        dry_run = False

    disable_ai = disable_ai or _env_flag("DISABLE_OPENAI")

    return Config(
        input_payitems=input_payitems,
        estimate_audit_csv=estimate_audit_csv,
        estimate_xlsx=estimate_xlsx,
        payitems_workbook=payitems_workbook,
        mapping_debug_csv=mapping_debug_csv,
        disable_ai=disable_ai,
        api_key_file=api_key_file,
        dry_run=dry_run,
    )


def read_api_key(config: Config) -> Optional[str]:
    """Read an API key from file or environment if available."""

    if config.disable_ai:
        return None

    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key

    try:
        return config.api_key_file.read_text(encoding="utf-8").strip() or None
    except FileNotFoundError:
        return None


__all__ = ["Config", "load_config", "read_api_key"]
