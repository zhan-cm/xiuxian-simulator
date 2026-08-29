from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.modern_web import create_modern_app


ROOT = Path(__file__).resolve().parents[1]


class ModernWebTests(unittest.TestCase):
    def test_health_and_state_share_the_existing_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            client = TestClient(create_modern_app(engine, ROOT))

            health = client.get("/api/v1/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json()["interface"], "react")
            self.assertEqual(health.headers["x-content-type-options"], "nosniff")
            self.assertEqual(health.headers["cache-control"], "no-store")

            snapshot = client.get("/api/v1/state")
            self.assertEqual(snapshot.status_code, 200)
            self.assertEqual(snapshot.json()["state"]["phase"], "new")
            self.assertIn("presentation", snapshot.json())

    def test_action_endpoint_advances_the_same_state_machine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            client = TestClient(create_modern_app(engine, ROOT))

            response = client.post("/api/v1/actions", json={"action": "开始游戏"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["state"]["phase"], "character_creation_basic")
            self.assertEqual(response.json()["decision"]["choices"][0]["action"], "确认默认创角")

            invalid = client.post("/api/v1/actions", json={"action": ""})
            self.assertEqual(invalid.status_code, 422)

    def test_react_shell_and_unknown_frontend_route_use_spa_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            client = TestClient(create_modern_app(engine, ROOT))
            for route in ("/", "/showcase"):
                response = client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn("问道长生", response.text)


if __name__ == "__main__":
    unittest.main()
