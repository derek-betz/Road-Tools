from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Point to the 'commitments-reconciler' folder so that 'commitments_reconciler'
# (which now lives inside it) is importable without installation.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from commitments_reconciler.factories import (  # noqa: E402 - path patched above
    create_sample_commitments_workbook,
    create_sample_environment_doc,
)


@pytest.fixture()
def commitments_workbook(tmp_path: Path) -> Path:
    destination = tmp_path / "sample_commitments.xlsx"
    return create_sample_commitments_workbook(destination)


@pytest.fixture()
def environment_doc(tmp_path: Path) -> Path:
    destination = tmp_path / "sample_env_doc.docx"
    return create_sample_environment_doc(destination)
