#!/usr/bin/env python3
"""A tiny, dependency-free server for Family Chalkboard."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import tempfile
import threading
from collections.abc import Iterable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import IPv4Network, IPv6Network, ip_address, ip_network
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

VERSION = "1.0.0"
APP_FILE = Path(__file__).with_name("index.html")
DEFAULT_STATE = {"version": 1, "note": "", "strokes": []}
DEFAULT_ALLOWED_NETWORKS = (
    "127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,fc00::/7"
)
MAX_STATE_BYTES = 5 * 1024 * 1024
MAX_NOTE_LENGTH = 1000
MAX_STROKES = 2500
MAX_POINTS_PER_STROKE = 10000
MAX_TOTAL_POINTS = 200000
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
Network = IPv4Network | IPv6Network


class InvalidState(ValueError):
    """Raised when a client submits malformed or excessive board state."""


def _finite_number(value: Any, field: str) -> float:
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


def encode_state(state: dict[str, Any]) -> bytes:
    return json.dumps(
        state,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def decode_state(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InvalidState("state is not valid JSON") from error
    return validate_state(value)


class StateStore:
    """Atomic JSON persistence for a single shared chalkboard."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self._lock = threading.Lock()

    def load(self) -> dict[str, Any]:
        with self._lock:
            try:
                payload = self.state_file.read_bytes()
            except FileNotFoundError:
                return dict(DEFAULT_STATE)
        return decode_state(payload)

    def save(self, state: dict[str, Any]) -> None:
        normalized = validate_state(state)
        payload = encode_state(normalized)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.state_file.name}.",
                suffix=".tmp",
                dir=self.state_file.parent,
            )
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary_path, self.state_file)
            finally:
                temporary_path.unlink(missing_ok=True)


def parse_networks(value: str) -> tuple[Network, ...]:
    networks: list[Network] = []
    for item in value.split(","):
        candidate = item.strip()
        if candidate:
            networks.append(ip_network(candidate, strict=False))
    if not networks:
        raise ValueError("at least one allowed network is required")
    return tuple(networks)


def client_allowed(address: str, networks: Iterable[Network]) -> bool:
    try:
        client = ip_address(address)
    except ValueError:
        return False
    return any(
        client.version == network.version and client in network for network in networks
    )


@dataclass(frozen=True)
class ServerSettings:
    app_file: Path
    store: StateStore
    allowed_networks: tuple[Network, ...]
    verbose: bool = False


class ChalkboardServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: tuple[str, int],
        settings: ServerSettings,
    ):
        self.settings = settings
        super().__init__(server_address, ChalkboardHandler)


class ChalkboardHandler(BaseHTTPRequestHandler):
    server: ChalkboardServer

    def log_message(self, message_format: str, *args: Any) -> None:
        if self.server.settings.verbose:
            super().log_message(message_format, *args)

    def send_bytes(
        self,
        status: int,
        content_type: str,
        payload: bytes,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; "
            "connect-src 'self'; "
            "img-src 'self' data:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-ancestors *",
        )
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path in {"/", "/chalkboard", "/chalkboard/"}:
            try:
                payload = self.server.settings.app_file.read_bytes()
            except OSError:
                self.send_bytes(
                    500,
                    "text/plain; charset=utf-8",
                    b"application file is unavailable\n",
                )
                return
            self.send_bytes(200, "text/html; charset=utf-8", payload)
            return

        if path == "/health":
            self.send_bytes(200, "text/plain; charset=utf-8", b"ok\n")
            return

        if path in {"/api/state", "/chalkboard/state"}:
            try:
                payload = encode_state(self.server.settings.store.load())
            except (InvalidState, OSError):
                self.send_bytes(
                    500,
                    "text/plain; charset=utf-8",
                    b"stored state is unavailable\n",
                )
                return
            self.send_bytes(200, "application/json; charset=utf-8", payload)
            return

        self.send_bytes(404, "text/plain; charset=utf-8", b"not found\n")

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path not in {"/api/state", "/chalkboard/state"}:
            self.send_bytes(404, "text/plain; charset=utf-8", b"not found\n")
            return

        if not client_allowed(
            self.client_address[0],
            self.server.settings.allowed_networks,
        ):
            self.send_bytes(403, "text/plain; charset=utf-8", b"forbidden\n")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_STATE_BYTES:
            self.send_bytes(
                413,
                "text/plain; charset=utf-8",
                b"invalid payload size\n",
            )
            return

        try:
            state = decode_state(self.rfile.read(content_length))
            self.server.settings.store.save(state)
        except InvalidState:
            self.send_bytes(
                400,
                "text/plain; charset=utf-8",
                b"invalid state\n",
            )
            return
        except OSError:
            self.send_bytes(
                500,
                "text/plain; charset=utf-8",
                b"could not save state\n",
            )
            return

        self.send_bytes(204, "text/plain; charset=utf-8", b"")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Serve a shared, touch-friendly family chalkboard.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("CHALKBOARD_HOST", "0.0.0.0"),
        help="address to listen on (default: CHALKBOARD_HOST or 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        default=int(os.environ.get("CHALKBOARD_PORT", "8765")),
        type=int,
        help="port to listen on (default: CHALKBOARD_PORT or 8765)",
    )
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("CHALKBOARD_DATA_DIR", "./data"),
        help="directory for board.json (default: CHALKBOARD_DATA_DIR or ./data)",
    )
    parser.add_argument(
        "--allowed-networks",
        default=os.environ.get(
            "CHALKBOARD_ALLOWED_NETWORKS",
            DEFAULT_ALLOWED_NETWORKS,
        ),
        help="comma-separated CIDR networks allowed to save",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=os.environ.get("CHALKBOARD_VERBOSE", "").lower()
        in {"1", "true", "yes"},
        help="enable HTTP request logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    return parser


def create_server(
    host: str,
    port: int,
    data_dir: Path,
    allowed_networks: tuple[Network, ...],
    *,
    app_file: Path = APP_FILE,
    verbose: bool = False,
) -> ChalkboardServer:
    settings = ServerSettings(
        app_file=app_file,
        store=StateStore(data_dir / "board.json"),
        allowed_networks=allowed_networks,
        verbose=verbose,
    )
    return ChalkboardServer((host, port), settings)


def main() -> int:
    arguments = build_parser().parse_args()
    try:
        networks = parse_networks(arguments.allowed_networks)
    except ValueError as error:
        raise SystemExit(f"Invalid --allowed-networks value: {error}") from error

    server = create_server(
        arguments.host,
        arguments.port,
        Path(arguments.data_dir).expanduser().resolve(),
        networks,
        verbose=arguments.verbose,
    )
    host, port = server.server_address[:2]
    print(f"Family Chalkboard {VERSION} listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
