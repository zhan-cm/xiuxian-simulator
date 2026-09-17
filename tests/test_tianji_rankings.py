import unittest
from pathlib import Path

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.state import GameState
from xiuxian_simulator.tianji_rankings import PRODIGY_TEMPLATES, TianjiRankingsEngine
from xiuxian_simulator.webapp import WebApplication


class TestTianjiRankings(unittest.TestCase):
    def test_calculate_power_and_rank(self) -> None:
        state = GameState(phase="playing")
        state.player.realm_index = 1
        state.player.health_max = 200
        state.player.spirit_max = 200
        power = TianjiRankingsEngine.calculate_player_power(state)
        self.assertGreater(power, 400)

        rank = TianjiRankingsEngine.get_player_rank(state)
        self.assertGreaterEqual(rank, 1)
        self.assertLessEqual(rank, len(PRODIGY_TEMPLATES) + 1)

    def test_prodigies_ladder(self) -> None:
        state = GameState(phase="playing")
        state.player.name = "林修远"
        state.player.dao_name = "青木"
        ladder = TianjiRankingsEngine.get_prodigies_ladder(state)

        # Should include all templates + player
        self.assertEqual(len(ladder), len(PRODIGY_TEMPLATES) + 1)
        player_entry = next((item for item in ladder if item["is_player"]), None)
        self.assertIsNotNone(player_entry)
        self.assertEqual(player_entry["name"], "林修远")

        # NPCs like Gu Qingxuan should be present
        gu = next((item for item in ladder if item["name"] == "顾清玄"), None)
        self.assertIsNotNone(gu)
        self.assertTrue(gu["is_npc"])

    def test_challenge_prodigy_flow(self) -> None:
        state = GameState(phase="playing")
        state.player.realm_index = 3
        state.player.health = 300
        state.player.health_max = 300
        state.player.spirit_max = 300
        state.player.resources["天机排位"] = 12

        # Target prodigy at rank 10
        ladder = TianjiRankingsEngine.get_prodigies_ladder(state)
        target = next((item for item in ladder if not item["is_player"] and item["rank"] < 12), None)
        self.assertIsNotNone(target)

        res = TianjiRankingsEngine.challenge_prodigy(state, target["id"])
        self.assertIn("登榜问剑", res["msg"])
        self.assertIn("target", res)

    def test_challenge_errors(self) -> None:
        state = GameState(phase="playing")
        # Self-challenge
        with self.assertRaises(ValueError):
            TianjiRankingsEngine.challenge_prodigy(state, "player-self")

        # Low health
        state.player.health = 10
        with self.assertRaises(ValueError):
            TianjiRankingsEngine.challenge_prodigy(state, "prodigy-gu-qingxuan")

    def test_redeem_treasure(self) -> None:
        state = GameState(phase="playing")
        state.player.resources["天机令"] = 100
        state.player.cultivation = 50

        # Redeem pill
        res = TianjiRankingsEngine.redeem_treasure(state, "tj-pill")
        self.assertEqual(res["treasure"], "太虚蕴灵丹")
        self.assertEqual(state.player.resources["天机令"], 100 - 45)
        self.assertEqual(state.player.cultivation, 200)

        # Insufficient tokens error
        with self.assertRaises(ValueError):
            TianjiRankingsEngine.redeem_treasure(state, "tj-box")

    def test_snapshot_structure(self) -> None:
        state = GameState(phase="playing")
        state.player.resources["天机令"] = 50
        snap = TianjiRankingsEngine.snapshot(state)

        self.assertIn("player_rank", snap)
        self.assertIn("player_power", snap)
        self.assertEqual(snap["tokens"], 50)
        self.assertGreater(len(snap["prodigies"]), 10)
        self.assertGreater(len(snap["overlords"]), 0)
        self.assertGreater(len(snap["sects"]), 0)
        self.assertGreater(len(snap["treasures"]), 0)
        self.assertGreater(len(snap["news"]), 0)

    def test_engine_actions_and_webapp(self) -> None:
        engine = build_engine()
        engine.process("开始游戏")
        engine.process("确认默认创角")
        engine.state.player.resources["天机令"] = 100
        engine.state.player.health = 200
        engine.state.player.health_max = 200
        engine.state.player.realm_index = 2

        out_view = engine.process("天机榜")
        self.assertIn("天机阁 · 百晓风云谱", out_view)
        self.assertIn("青云潜龙榜", out_view)

        out_challenge = engine.process("登榜问剑 prodigy-qingyun-wa门")
        self.assertIn("登榜问剑", out_challenge)

        out_redeem = engine.process("天机兑换 tj-amulet")
        self.assertIn("天机避劫符", out_redeem)

        root = Path(__file__).resolve().parent.parent
        webapp = WebApplication(engine, root)
        snap = webapp.snapshot()
        self.assertIn("tianji_rankings", snap)
        self.assertGreater(len(snap["tianji_rankings"]["prodigies"]), 0)


if __name__ == "__main__":
    unittest.main()
