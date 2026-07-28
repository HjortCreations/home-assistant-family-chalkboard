#!/usr/bin/env python3
"""Ask Node.js to parse both browser frontends."""

import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = PROJECT_ROOT / "src" / "index.html"
PANEL_FILE = (
    PROJECT_ROOT
    / "custom_components"
    / "family_chalkboard"
    / "frontend"
    / "family-chalkboard-panel.js"
)


def _check_script(script: str, label: str) -> None:
    """Write a temporary JavaScript file and ask Node.js to parse it."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".js",
        encoding="utf-8",
        delete=False,
    ) as temporary:
        temporary.write(script)
        script_file = Path(temporary.name)

    try:
        subprocess.run(
            ["node", "--check", script_file],
            check=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise SystemExit("Node.js is required for the frontend syntax check") from error
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"JavaScript syntax check failed for {label}") from error
    finally:
        script_file.unlink(missing_ok=True)


def main() -> None:
    """Check the standalone app and Home Assistant panel."""
    html = HTML_FILE.read_text(encoding="utf-8")
    start = html.rfind("<script>")
    end = html.rfind("</script>")
    if start < 0 or end <= start:
        raise SystemExit("Could not find the inline application script")

    _check_script(
        html[start + len("<script>") : end],
        "standalone app",
    )
    _check_script(
        PANEL_FILE.read_text(encoding="utf-8"),
        "Home Assistant panel",
    )


if __name__ == "__main__":
    main()
