from __future__ import annotations

import sys
from pathlib import Path

# Ensure the src directory is importable without requiring installation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
