from __future__ import annotations

import json
import sys
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from chalkboard_server import (
    DEFAULT_STATE,
    InvalidState,
    StateStore,
    client_allowed,
    create_server,
    parse_networks,
    validate_state,
)

VALID_STATE = {
    "version": 1,
    "note": "Milk is in the fridge",
    "strokes": [
        {
            "mode": "draw",
            "color": "#F3F1E8",
            "width": 8,
            "points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.3, "y": 0.4},
            ],
        }
    ],
}


class ValidationTests(unittest.TestCase):
    def test_valid_state_is_normalized(self) -> None:
        normalized = validate_state(VALID_STATE)
        self.assertEqual(normalized["version"], 1)
        self.assertEqual(normalized["strokes"][0]["color"], "#f3f1e8")
        self.assertEqual(normalized["strokes"][0]["width"], 8.0)

    def test_rejects_long_note(self) -> None:
        with self.assertRaises(InvalidState):
            validate_state({"note": "x" * 1001, "strokes": []})

    def test_rejects_unknown_mode(self) -> None:
        invalid = json.loads(json.dumps(VALID_STATE))
        invalid["strokes"][0]["mode"] = "spray"
        with self.assertRaises(InvalidState):
            validate_state(invalid)

    def test_rejects_invalid_color(self) -> None:
        invalid = json.loads(json.dumps(VALID_STATE))
        invalid["strokes"][0]["color"] = "white"
        with self.assertRaises(InvalidState):
            validate_state(invalid)

    def test_rejects_point_outside_board(self) -> None:
        invalid = json.loads(json.dumps(VALID_STATE))
        invalid["strokes"][0]["points"][0]["x"] = 1.1
        with self.assertRaises(InvalidState):
            validate_state(invalid)


class StorageTests(unittest.TestCase):
    def test_missing_state_returns_empty_board(self) -> None:
        with TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "board.json")
            self.assertEqual(store.load(), DEFAULT_STATE)

    def test_state_round_trip(self) -> None:
        with TemporaryDirectory() as directory:
            store = StateStore(Path(directory) / "board.json")
            store.save(VALID_STATE)
            self.assertEqual(store.load()["note"], VALID_STATE["note"])
            self.assertEqual(len(store.load()["strokes"]), 1)


class NetworkTests(unittest.TestCase):
    def test_private_client_is_allowed(self) -> None:
        networks = parse_networks("127.0.0.0/8,192.168.0.0/16")
        self.assertTrue(client_allowed("192.168.1.50", networks))
        self.assertFalse(client_allowed("203.0.113.50", networks))

    def test_empty_network_list_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            parse_networks(" , ")


class HttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.app_file = Path(self.temporary_directory.name) / "index.html"
        self.app_file.write_text("<!doctype html><title>Test</title>", "utf-8")
        self.server = create_server(
            "127.0.0.1",
            0,
            Path(self.temporary_directory.name) / "data",
            parse_networks("127.0.0.0/8"),
            app_file=self.app_file,
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        self.connection = HTTPConnection(
            "127.0.0.1",
            self.server.server_port,
            timeout=3,
        )

    def tearDown(self) -> None:
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temporary_directory.cleanup()

    def request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
    ) -> tuple[int, bytes, dict[str, str]]:
        headers = {"Content-Type": "application/json"} if body else {}
        self.connection.request(method, path, body=body, headers=headers)
        response = self.connection.getresponse()
        response_headers = dict(response.getheaders())
        return response.status, response.read(), response_headers

    def test_health_and_app(self) -> None:
        status, payload, headers = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload, b"ok\n")
        self.assertIn("Content-Security-Policy", headers)

        status, payload, _headers = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"<title>Test</title>", payload)

    def test_save_and_load(self) -> None:
        status, _payload, _headers = self.request(
            "POST",
            "/api/state",
            json.dumps(VALID_STATE).encode("utf-8"),
        )
        self.assertEqual(status, 204)

        status, payload, _headers = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        loaded = json.loads(payload)
        self.assertEqual(loaded["note"], VALID_STATE["note"])
        self.assertEqual(len(loaded["strokes"]), 1)

    def test_invalid_state_is_rejected_without_overwrite(self) -> None:
        valid_payload = json.dumps(VALID_STATE).encode("utf-8")
        status, _payload, _headers = self.request(
            "POST",
            "/api/state",
            valid_payload,
        )
        self.assertEqual(status, 204)

        status, _payload, _headers = self.request(
            "POST",
            "/api/state",
            b'{"note":4,"strokes":[]}',
        )
        self.assertEqual(status, 400)

        status, payload, _headers = self.request("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(payload)["note"], VALID_STATE["note"])


if __name__ == "__main__":
    unittest.main()
