#!/usr/bin/env python3
"""Extract the inline browser script and ask Node.js to parse it."""

from pathlib import Path
import subprocess
import tempfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = PROJECT_ROOT / "src" / "index.html"


def main() -> None:
    html = HTML_FILE.read_text(encoding="utf-8")
    start = html.rfind("<script>")
    end = html.rfind("</script>")
    if start < 0 or end <= start:
        raise SystemExit("Could not find the inline application script")

    script = html[start + len("<script>") : end]
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".js",
        encoding="utf-8",
        delete=False,
    ) as temporary:
        temporary.write(script)
        script_file = Path(temporary.name)

    try:
        subprocess.run(["node", "--check", script_file], check=True)
    finally:
        script_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
