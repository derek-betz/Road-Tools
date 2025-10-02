"""Generate deterministic example Office documents for manual inspection."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add commitments-reconciler folder to path so commitments_reconciler is importable
SCRIPT_DIR = Path(__file__).resolve().parent
COMMITMENTS_RECONCILER_ROOT = SCRIPT_DIR.parent
if str(COMMITMENTS_RECONCILER_ROOT) not in sys.path:
    sys.path.insert(0, str(COMMITMENTS_RECONCILER_ROOT))

from commitments_reconciler.factories import (  # noqa: E402 - path patched above
    create_sample_commitments_workbook,
    create_sample_environment_doc,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "examples",
        help="Directory that will receive the generated documents.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    workbook_path = args.output_dir / "sample_commitments.xlsx"
    doc_path = args.output_dir / "sample_env_doc.docx"

    create_sample_commitments_workbook(workbook_path)
    create_sample_environment_doc(doc_path)

    print(f"Generated {workbook_path}")  # noqa: T201 - CLI feedback
    print(f"Generated {doc_path}")  # noqa: T201 - CLI feedback
    return 0


if __name__ == "__main__":  # pragma: no cover - convenience entry point
    raise SystemExit(main())
