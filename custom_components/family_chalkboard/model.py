"""Board state validation shared by storage and the WebSocket API."""

from __future__ import annotations

import json
import math
import re
from typing import Any, Final

DEFAULT_STATE: Final = {"version": 1, "note": "", "strokes": []}
MAX_STATE_BYTES: Final = 5 * 1024 * 1024
MAX_NOTE_LENGTH: Final = 1000
MAX_STROKES: Final = 2500
MAX_POINTS_PER_STROKE: Final = 10000
MAX_TOTAL_POINTS: Final = 200000
COLOR_PATTERN: Final = re.compile(r"^#[0-9a-fA-F]{6}$")


class InvalidState(ValueError):
    """Raised when board state is malformed or excessive."""


def _finite_number(value: Any, field: str) -> float:
    """Return a finite number or raise InvalidState."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidState(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise InvalidState(f"{field} must be finite")
    return number


def validate_state(value: Any) -> dict[str, Any]:
    """Validate and normalize untrusted board state."""
    if not isinstance(value, dict):
        raise InvalidState("state must be an object")

    try:
        encoded_size = len(
            json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        )
    except (TypeError, ValueError) as error:
        raise InvalidState("state must contain JSON-compatible values") from error
    if encoded_size > MAX_STATE_BYTES:
        raise InvalidState("state is too large")

    note = value.get("note", "")
    if not isinstance(note, str):
        raise InvalidState("note must be a string")
    if len(note) > MAX_NOTE_LENGTH:
        raise InvalidState("note is too long")

    strokes = value.get("strokes", [])
    if not isinstance(strokes, list):
        raise InvalidState("strokes must be an array")
    if len(strokes) > MAX_STROKES:
        raise InvalidState("too many strokes")

    normalized_strokes: list[dict[str, Any]] = []
    total_points = 0
    for stroke_index, stroke in enumerate(strokes):
        if not isinstance(stroke, dict):
            raise InvalidState(f"stroke {stroke_index} must be an object")

        mode = stroke.get("mode")
        if mode not in {"draw", "erase"}:
            raise InvalidState(f"stroke {stroke_index} has an invalid mode")

        color = stroke.get("color", "#f3f1e8")
        if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
            raise InvalidState(f"stroke {stroke_index} has an invalid color")

        width = _finite_number(stroke.get("width"), "width")
        if width < 1 or width > 64:
            raise InvalidState(f"stroke {stroke_index} has an invalid width")

        points = stroke.get("points")
        if not isinstance(points, list) or not points:
            raise InvalidState(f"stroke {stroke_index} needs at least one point")
        if len(points) > MAX_POINTS_PER_STROKE:
            raise InvalidState(f"stroke {stroke_index} has too many points")

        total_points += len(points)
        if total_points > MAX_TOTAL_POINTS:
            raise InvalidState("board has too many points")

        normalized_points: list[dict[str, float]] = []
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                raise InvalidState(
                    f"stroke {stroke_index} point {point_index} must be an object"
                )
            x = _finite_number(point.get("x"), "x")
            y = _finite_number(point.get("y"), "y")
            if not 0 <= x <= 1 or not 0 <= y <= 1:
                raise InvalidState(
                    f"stroke {stroke_index} point {point_index} is outside the board"
                )
            normalized_points.append({"x": x, "y": y})

        normalized_strokes.append(
            {
                "mode": mode,
                "color": color.lower(),
                "width": width,
                "points": normalized_points,
            }
        )

    return {
        "version": 1,
        "note": note,
        "strokes": normalized_strokes,
    }
