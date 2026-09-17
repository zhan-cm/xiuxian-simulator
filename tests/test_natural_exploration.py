import unittest
from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.natural_exploration import KYUSHU_LANDMARKS, NaturalExplorationEngine
from xiuxian_simulator.state import GameState
from xiuxian_simulator.travel import TravelEngine
from xiuxian_simulator.webapp import WebApplication


class TestNaturalExploration(unittest.TestCase):
    def test_current_landmark_and_lookup(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        lm = NaturalExplorationEngine.current_landmark(state)
        self.assertEqual(lm.name, "青岳洗剑池")
        self.assertEqual(lm.province, "东洲")

        # Test lookup by id and name
        lm2 = NaturalExplorationEngine.get_landmark_by_id_or_province("dz-sword-pool")
        self.assertEqual(lm2.id, "dz-sword-pool")
        lm3 = NaturalExplorationEngine.get_landmark_by_id_or_province("极北万载寒渊")
        self.assertEqual(lm3.province, "北原")

    def test_meditate(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        state.player.cultivation = 0
        res = NaturalExplorationEngine.meditate(state, "dz-sword-pool")
        self.assertEqual(res["landmark"], "青岳洗剑池")
        self.assertGreater(state.player.cultivation, 0)
        self.assertIn("青岳洗剑池", res["msg"])

        # Test realm requirement error (by-frost-abyss requires realm 3)
        state.player.realm_index = 0
        with self.assertRaises(ValueError):
            NaturalExplorationEngine.meditate(state, "by-frost-abyss")

    def test_harvest(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        state.player.spirit = 50
        state.player.spirit_stones = 100
        res = NaturalExplorationEngine.harvest(state, "dz-sword-pool")
        self.assertEqual(res["landmark"], "青岳洗剑池")
        self.assertEqual(state.player.spirit, 35)

        # Test spirit requirement
        state.player.spirit = 5
        with self.assertRaises(ValueError):
            NaturalExplorationEngine.harvest(state, "dz-sword-pool")

    def test_explore_secret(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        state.player.realm_index = 1
        res = NaturalExplorationEngine.explore_secret(state, "dz-sword-pool")
        self.assertEqual(res["landmark"], "青岳洗剑池")
        self.assertIn("青岳洗剑池", res["msg"])

    def test_ferry_cloud_ship(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        state.player.realm_index = 1
        state.player.spirit_stones = 500

        res = NaturalExplorationEngine.ferry_cloud_ship(state, "南疆")
        self.assertEqual(res["destination"], "南疆")
        self.assertEqual(state.player.location, "南疆·赤炎")
        self.assertEqual(TravelEngine.current_region(state), "南疆")
        self.assertLess(state.player.spirit_stones, 500)
        self.assertTrue(any("渡海灵舟" in h for h in state.travel_history))

    def test_ancient_teleport(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "东洲·青岳"
        # 西漠 minimum realm is 3
        state.player.realm_index = 3
        state.player.spirit_stones = 1000

        res = NaturalExplorationEngine.ancient_teleport(state, "西漠")
        self.assertEqual(res["destination"], "西漠")
        self.assertEqual(state.player.location, "西漠·流沙")
        self.assertEqual(TravelEngine.current_region(state), "西漠")
        self.assertLess(state.player.spirit_stones, 1000)
        self.assertTrue(any("太古挪移" in h for h in state.travel_history))

    def test_snapshot_structure(self) -> None:
        state = GameState(phase="playing")
        state.player.location = "中州·天阙"
        state.player.realm_index = 2
        state.player.spirit_stones = 1000

        snap = NaturalExplorationEngine.snapshot(state)
        self.assertEqual(snap["current_region"], "中州")
        self.assertEqual(snap["current_landmark"]["name"], "昆仑天柱仙台")
        self.assertGreaterEqual(len(snap["landmarks"]), 9)
        self.assertGreater(len(snap["ferry_routes"]), 0)

    def test_engine_and_webapp_integration(self) -> None:
        engine = build_engine()
        engine.process("开始游戏")
        engine.process("确认默认创角")
        engine.state.player.location = "东洲·青岳"
        engine.state.player.spirit_stones = 2000
        engine.state.player.realm_index = 3
        engine.state.player.spirit = 100

        out_view = engine.process("胜境")
        self.assertIn("青岳洗剑池", out_view)

        out_meditate = engine.process("胜境悟道")
        self.assertIn("青岳洗剑池", out_meditate)

        out_harvest = engine.process("胜境采灵")
        self.assertIn("青岳洗剑池", out_harvest)

        out_secret = engine.process("胜境探幽")
        self.assertIn("青岳洗剑池", out_secret)

        out_ferry = engine.process("渡海灵舟 南疆")
        self.assertIn("渡海灵舟", out_ferry)
        self.assertEqual(TravelEngine.current_region(engine.state), "南疆")

        out_teleport = engine.process("古阵挪移 西漠")
        self.assertIn("太古挪移大阵", out_teleport)
        self.assertEqual(TravelEngine.current_region(engine.state), "西漠")

        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        webapp = WebApplication(engine, root)
        app_snap = webapp.snapshot()
        self.assertIn("natural_exploration", app_snap)
        self.assertEqual(app_snap["natural_exploration"]["current_region"], "西漠")


if __name__ == "__main__":
    unittest.main()
