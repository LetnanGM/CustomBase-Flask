from pathlib import Path

ROOT = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()
)

SRC_ROOT = ROOT / "src"
BOWLPLATE_ROOT = SRC_ROOT / "bowlplate"
PLUGIN_ROOT = BOWLPLATE_ROOT / "plugins"
