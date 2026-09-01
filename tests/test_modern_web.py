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
            self.assertEqual(snapshot.json()["story"]["total"], 6)
            self.assertEqual(len(snapshot.json()["story"]["alignments"]), 3)
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
            self.assertEqual(snapshot.json()["npc_network"]["connected_count"], 6)
            self.assertGreaterEqual(snapshot.json()["npc_network"]["bond_count"], 7)
            self.assertEqual(snapshot.json()["dao"]["points"], 0)
            self.assertEqual(len(snapshot.json()["dao"]["branches"]), 9)
            self.assertEqual(snapshot.json()["spirit_beasts"]["count"], 0)
            self.assertEqual(snapshot.json()["spirit_beasts"]["active_name"], "")
            self.assertEqual(snapshot.json()["formations"]["count"], 0)
            self.assertEqual(snapshot.json()["formations"]["active_name"], "")
            self.assertFalse(snapshot.json()["sect_library"]["member"])
            self.assertEqual(snapshot.json()["sect_library"]["claimed_count"], 0)
            self.assertFalse(snapshot.json()["sect_domain"]["founded"])
            self.assertFalse(snapshot.json()["sect_domain"]["visible"])
            self.assertFalse(snapshot.json()["sect_domain"]["diplomacy"]["visible"])
            self.assertEqual(snapshot.json()["artifacts"]["count"], 0)
            self.assertEqual(snapshot.json()["art_mastery"]["known_count"], 2)
            self.assertEqual(snapshot.json()["art_mastery"]["primary"]["name"], "聚气诀")
            self.assertFalse(snapshot.json()["recovery"]["active"])
            self.assertEqual(snapshot.json()["recovery"]["count"], 0)
            self.assertFalse(snapshot.json()["legacy"]["ended"])
            self.assertEqual(snapshot.json()["legacy"]["life_number"], 1)
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

    def test_portable_save_endpoints_preserve_active_game_and_avoid_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.state.phase = "playing"
            engine.state.turn = 27
            engine.state.player.name = "林渡"
            engine.saves.save("筑基之前", engine.state)
            before = engine.state.to_dict()
            client = TestClient(create_modern_app(engine, ROOT))

            exported = client.get("/api/v1/saves/export", params={"name": "筑基之前"})
            self.assertEqual(exported.status_code, 200)
            self.assertIn("attachment", exported.headers["content-disposition"])
            self.assertIn("filename*=UTF-8''", exported.headers["content-disposition"])
            payload = exported.json()
            self.assertEqual(payload["format"], "wendao-changsheng-save")
            self.assertEqual(payload["state"]["turn"], 27)

            imported = client.post(
                "/api/v1/saves/import",
                json={"data": payload, "preferred_name": "", "overwrite": False},
            )
            self.assertEqual(imported.status_code, 200)
            self.assertEqual(imported.json()["name"], "筑基之前_导入1")
            self.assertTrue(imported.json()["renamed"])
            self.assertEqual(engine.state.to_dict(), before)
            self.assertTrue((Path(temp_dir) / "筑基之前_导入1.json").is_file())

            payload["state"]["turn"] = 28
            rejected = client.post("/api/v1/saves/import", json={"data": payload})
            self.assertEqual(rejected.status_code, 400)
            self.assertIn("内容校验失败", rejected.json()["detail"])

    def test_save_import_request_size_is_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            client = TestClient(create_modern_app(engine, ROOT))
            response = client.post(
                "/api/v1/saves/import",
                content=b"x" * (2 * 1024 * 1024 + 70_000),
                headers={"Content-Type": "application/json"},
            )
            self.assertEqual(response.status_code, 413)
            self.assertIn("2 MB", response.json()["detail"])

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
            self.assertGreaterEqual(len(pages), 34)
            self.assertEqual(engine.state.to_dict(), original_state)
            self.assertFalse(list(Path(temp_dir).glob("*.json")))
            by_id = {page["id"]: page for page in pages}
            recovery = by_id["recovery"]["snapshot"]["recovery"]
            self.assertTrue(recovery["active"])
            self.assertEqual(recovery["count"], 2)
            self.assertEqual(recovery["injuries"][0]["severity_label"], "沉重")
            self.assertLess(recovery["penalties"]["cultivation"], 1)
            self.assertTrue(recovery["has_healing_pill"])
            legacy = by_id["legacy-ending"]["snapshot"]["legacy"]
            self.assertTrue(legacy["ended"])
            self.assertEqual(legacy["latest"]["realm"], "结晶·后期")
            self.assertEqual(legacy["latest"]["metrics"]["regions"], 3)
            self.assertEqual(len(legacy["options"]), 3)
            self.assertEqual(legacy["options"][2]["id"], "world-vow")
            self.assertFalse(legacy["can_begin_next"])
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
            finale = by_id["story-finale"]["snapshot"]
            self.assertEqual(finale["state"]["phase"], "main_story_choice")
            self.assertEqual(finale["story"]["total"], 6)
            self.assertEqual(len(finale["decision"]["choices"]), 3)
            self.assertIn("守世共鸣 5/5", finale["decision"]["choices"][0]["summary"])
            ending = by_id["story-ending"]["snapshot"]
            self.assertEqual(ending["story"]["ending"]["title"], "人间长明")
            self.assertEqual(ending["state"]["world_era"], "灵潮新世")
            era_pending = by_id["new-era-pending"]["snapshot"]
            self.assertEqual(era_pending["state"]["phase"], "new_era_choice")
            self.assertEqual(era_pending["new_era"]["event"]["title"], "灵脉迁徙")
            self.assertEqual(len(era_pending["decision"]["choices"]), 3)
            self.assertFalse(era_pending["decision"]["choices"][0]["disabled"])
            era_chronicle = by_id["new-era-chronicle"]["snapshot"]["new_era"]
            self.assertEqual(era_chronicle["completed"], 3)
            self.assertEqual(era_chronicle["stage"], "新世奠基")
            self.assertEqual(len(era_chronicle["scores"]), 3)
            dao = by_id["dao-tree"]["snapshot"]["dao"]
            self.assertEqual(len(dao["branches"]), 9)
            self.assertEqual(dao["points"], 2)
            self.assertEqual(next(item for item in dao["branches"] if item["id"] == "剑道")["level"], 2)
            beasts = by_id["spirit-beasts"]["snapshot"]["spirit_beasts"]
            self.assertEqual(beasts["count"], 2)
            self.assertEqual(beasts["active_name"], "青风狐")
            self.assertEqual(beasts["materials"], 3)
            self.assertEqual(beasts["beasts"][0]["id"], "qingfeng-fox")
            formations = by_id["formations"]["snapshot"]["formations"]
            self.assertEqual(formations["count"], 3)
            self.assertEqual(formations["active_name"], "青木聚灵阵")
            self.assertEqual(formations["skill_level"], 2)
            self.assertEqual(len(formations["arrays"]), 5)
            self.assertTrue(next(item for item in formations["arrays"] if item["id"] == "spirit-gathering")["active"])
            library = by_id["sect-library"]["snapshot"]["sect_library"]
            self.assertTrue(library["member"])
            self.assertEqual(library["sect"], "青云宗")
            self.assertEqual(library["rank"], "真传弟子")
            self.assertEqual(len(library["offerings"]), 4)
            self.assertTrue(next(item for item in library["offerings"] if item["id"] == "qingyun-evergreen")["claimed"])
            domain = by_id["sect-domain"]["snapshot"]["sect_domain"]
            self.assertTrue(domain["founded"])
            self.assertEqual(domain["sect"]["name"], "青玄宗")
            self.assertEqual(domain["sect"]["doctrine"], "harmony")
            self.assertEqual(domain["sect"]["strength"], 136)
            self.assertEqual(len(domain["disciples"]), 6)
            self.assertEqual(len(domain["buildings"]), 3)
            diplomacy = by_id["sect-diplomacy"]["snapshot"]["sect_domain"]["diplomacy"]
            self.assertTrue(diplomacy["visible"])
            self.assertEqual(len(diplomacy["factions"]), 4)
            self.assertEqual(diplomacy["income_bonus"], 37)
            self.assertEqual(diplomacy["war"]["target"], "血煞盟")
            self.assertEqual(diplomacy["war"]["momentum"], -2)
            self.assertEqual(by_id["sect-diplomacy"]["snapshot"]["state"]["phase"], "sect_war_choice")
            artifacts = by_id["artifacts"]["snapshot"]["artifacts"]
            self.assertEqual(artifacts["count"], 2)
            self.assertEqual(artifacts["bonded_name"], "玄铁剑")
            self.assertEqual(artifacts["bonded"]["level"], 2)
            self.assertEqual(artifacts["bonded"]["resonance"], 68)
            mastery = by_id["art-mastery"]["snapshot"]["art_mastery"]
            self.assertEqual(mastery["known_count"], 5)
            self.assertEqual(mastery["primary"]["name"], "青木长生诀")
            self.assertEqual(mastery["primary"]["level_label"], "大成")
            self.assertEqual(mastery["mastered_count"], 1)
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
            network = by_id["network"]["snapshot"]["npc_network"]
            self.assertEqual(network["pending"]["cause"], "青岳灵地归属")
            self.assertTrue(network["pending"]["can_mediate"])
            self.assertEqual(len(by_id["network"]["snapshot"]["decision"]["choices"]), 4)


if __name__ == "__main__":
    unittest.main()
