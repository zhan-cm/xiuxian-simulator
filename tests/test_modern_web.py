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

            before_snapshot = engine.state.to_dict()
            snapshot = client.get("/api/v1/state")
            self.assertEqual(snapshot.status_code, 200)
            self.assertEqual(snapshot.json()["state"]["phase"], "new")
            self.assertIn("presentation", snapshot.json())
            self.assertEqual(snapshot.json()["journey"]["active_chapter_id"], "chapter-1")
            self.assertEqual(snapshot.json()["commissions"]["active_limit"], 2)
            self.assertEqual(snapshot.json()["story"]["total"], 3)
            self.assertEqual(snapshot.json()["inventory"]["total_types"], 0)
            self.assertFalse(snapshot.json()["auction"]["active"])
            self.assertEqual(snapshot.json()["travel"]["current"], "东洲")
            self.assertEqual(len(snapshot.json()["travel"]["regions"]), 5)
            self.assertEqual(snapshot.json()["regional"]["current_rank"], "初来乍到")
            self.assertEqual(len(snapshot.json()["regional"]["standings"]), 5)
            self.assertEqual(snapshot.json()["cave"]["focus"], "蕴养灵脉")
            self.assertEqual(snapshot.json()["cave"]["spirit_energy_cap"], 24)
            self.assertEqual(snapshot.json()["npc_lives"]["living_count"], 6)
            self.assertEqual(len(snapshot.json()["npc_lives"]["profiles"]), 6)
            self.assertEqual(engine.state.to_dict(), before_snapshot)

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

    def test_showcase_uses_isolated_real_engine_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            original_state = engine.state.to_dict()
            client = TestClient(create_modern_app(engine, ROOT))
            response = client.get("/api/v1/showcase")
            self.assertEqual(response.status_code, 200)
            pages = response.json()["pages"]
            self.assertGreaterEqual(len(pages), 19)
            self.assertEqual(engine.state.to_dict(), original_state)
            self.assertFalse(list(Path(temp_dir).glob("*.json")))
            by_id = {page["id"]: page for page in pages}
            self.assertEqual(by_id["market"]["snapshot"]["presentation"]["blocks"][0]["type"], "market")
            self.assertEqual(by_id["battle"]["snapshot"]["state"]["phase"], "combat_ready")
            self.assertEqual(by_id["breakthrough"]["snapshot"]["state"]["phase"], "major_breakthrough_choice")
            journey = by_id["journey"]["snapshot"]["journey"]
            self.assertEqual(journey["active"]["completed_tasks"], 2)
            self.assertEqual(journey["points"], 0)
            commissions = by_id["commissions"]["snapshot"]["commissions"]
            self.assertEqual(commissions["active_count"], 1)
            self.assertTrue(commissions["active"][0]["ready"])
            self.assertEqual(by_id["story"]["snapshot"]["state"]["phase"], "main_story_choice")
            inventory = by_id["inventory"]["snapshot"]["inventory"]
            self.assertGreaterEqual(inventory["total_types"], 7)
            self.assertEqual(inventory["equipped"]["weapon"], "青锋剑")
            self.assertTrue(next(item for item in inventory["items"] if item["name"] == "疗伤丹")["actionable"])
            auction = by_id["auction"]["snapshot"]["auction"]
            self.assertTrue(auction["active"])
            self.assertEqual(len(auction["lots"]), 4)
            self.assertEqual(auction["closes_in"], 3)
            self.assertEqual(by_id["auction"]["snapshot"]["state"]["phase"], "auction_choice")
            self.assertEqual(len(by_id["auction"]["snapshot"]["decision"]["choices"]), 3)
            atlas = by_id["map"]["snapshot"]["presentation"]["blocks"]
            self.assertEqual([block["type"] for block in atlas[:2]], ["regions", "locations"])
            self.assertEqual(len(atlas[0]["items"]), 5)
            travel = by_id["travel"]["snapshot"]
            self.assertEqual(travel["state"]["phase"], "travel_choice")
            self.assertEqual(len(travel["decision"]["choices"]), 3)
            self.assertEqual(travel["travel"]["pending"]["destination"], "中州")
            regional = by_id["regional"]["snapshot"]
            self.assertEqual(regional["state"]["phase"], "regional_choice")
            self.assertEqual(regional["regional"]["current_rank"], "略有薄名")
            self.assertEqual(regional["presentation"]["title"], "地方机缘 · 南疆")
            self.assertEqual(len(regional["decision"]["choices"]), 3)
            donation = next(choice for choice in regional["decision"]["choices"] if choice["action"] == "地方选择 lure")
            self.assertFalse(donation["disabled"])
            cave = by_id["cave"]["snapshot"]["cave"]
            self.assertEqual(cave["focus"], "百艺轮转")
            self.assertEqual(cave["active_jobs"], 1)
            self.assertEqual(cave["jobs"][0]["recipe"], "聚气丹")
            self.assertGreater(cave["capacity"], cave["active_jobs"])
            relations = by_id["relations"]["snapshot"]["npc_lives"]
            self.assertEqual(relations["pending_count"], 1)
            guardian = next(item for item in relations["profiles"] if item["name"] == "顾清玄")
            self.assertTrue(guardian["pending"])
            self.assertEqual(guardian["pending_kind"], "寿元将尽")
            self.assertTrue(guardian["can_gift_pill"])


if __name__ == "__main__":
    unittest.main()
