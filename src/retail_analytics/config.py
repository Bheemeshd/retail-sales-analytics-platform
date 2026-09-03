"""Project configuration and shared paths."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
ASSET_DIR = ROOT / "assets"
REPORT_DIR = ROOT / "reports"
POWERBI_DIR = ROOT / "powerbi" / "extracts"
DATABASE_PATH = PROCESSED_DIR / "retail_analytics.db"


def ensure_directories() -> None:
    """Create every generated-output directory used by the pipeline."""
    for path in (RAW_DIR, PROCESSED_DIR, ASSET_DIR, REPORT_DIR, POWERBI_DIR):
        path.mkdir(parents=True, exist_ok=True)
