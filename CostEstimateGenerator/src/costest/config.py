from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class Settings:
    base_dir: Path
    bidtabs_dir: Path
    quantities_glob: str
    quantities_path: str
    project_attributes: Path
    region_map: str
    aliases_csv: Path
    output_dir: Path
    disable_ai: bool
    min_sample_target: int

    @classmethod
    def from_env(cls) -> "Settings":
        base = Path(__file__).resolve().parents[2]
        data_dir = base / "data_sample"
        bidtabs_dir = Path(os.getenv("BIDTABS_DIR", str(data_dir / "BidTabsData"))).expanduser().resolve()
        quantities_glob = os.getenv("QTY_FILE_GLOB", str(data_dir / "*_project_quantities.xlsx"))
        quantities_path = os.getenv("QUANTITIES_XLSX", "").strip()
        project_attrs = Path(os.getenv("PROJECT_ATTRS_XLSX", str(data_dir / "project_attributes.xlsx"))).expanduser().resolve()
        region_map = os.getenv("REGION_MAP_XLSX", "").strip()
        aliases_csv = Path(os.getenv("ALIASES_CSV", str(data_dir / "code_aliases.csv"))).expanduser().resolve()
        output_dir = Path(os.getenv("OUTPUT_DIR", str(base / "outputs"))).expanduser().resolve()
        disable_ai = os.getenv("DISABLE_OPENAI", "0").strip().lower() in {"1", "true", "yes"}
        min_sample_target = int(os.getenv("MIN_SAMPLE_TARGET", "50"))
        return cls(
            base_dir=base,
            bidtabs_dir=bidtabs_dir,
            quantities_glob=quantities_glob,
            quantities_path=quantities_path,
            project_attributes=project_attrs,
            region_map=region_map,
            aliases_csv=aliases_csv,
            output_dir=output_dir,
            disable_ai=disable_ai,
            min_sample_target=min_sample_target,
        )


__all__ = ["Settings"]
