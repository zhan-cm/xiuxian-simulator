import unittest
from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.sect_visit import SECT_PROFILES, SectVisitEngine
from xiuxian_simulator.state import GameState


class TestSectVisit(unittest.TestCase):
    def test_sect_visit_flow(self) -> None:
        state = GameState(phase="playing")
        state.player.spirit_stones = 500
        state.player.reputation = 20

        # Visit Qingyun Sect
        result = SectVisitEngine.visit(state, "青云宗")
        self.assertEqual(result["sect"], "青云宗")
        self.assertEqual(state.player.spirit_stones, 450)
        self.assertGreater(state.player.reputation, 20)
        if result["success"]:
            self.assertIn("青云剑穗", state.player.resources)

    def test_acquire_treasure(self) -> None:
        state = GameState(phase="playing")
        state.player.spirit_stones = 500
        state.player.reputation = 30

        # Buy pill
        res = SectVisitEngine.acquire_treasure(state, "青云宗", "qy-pill")
        self.assertEqual(res["treasure"], "聚气丹")
        self.assertEqual(res["count"], 3)
        self.assertEqual(state.player.spirit_stones, 500 - 180)
        self.assertEqual(state.player.resources["聚气丹"], 3)

    def test_spar_arena(self) -> None:
        state = GameState(phase="playing")
        state.player.spirit_stones = 100
        state.player.reputation = 10

        res = SectVisitEngine.spar(state, "青云宗")
        self.assertEqual(res["sect"], "青云宗")
        self.assertGreater(state.player.spirit_stones, 100)
        self.assertGreater(state.player.reputation, 10)

    def test_take_bounty(self) -> None:
        state = GameState(phase="playing")
        state.player.spirit_stones = 100
        state.player.reputation = 10

        res = SectVisitEngine.take_bounty(state, "青云宗", "qy-bounty-1")
        self.assertEqual(res["sect"], "青云宗")
        if res["success"]:
            self.assertGreater(state.player.spirit_stones, 100)
            self.assertIn("妖兽材料", state.player.resources)

    def test_engine_actions(self) -> None:
        engine = build_engine()
        engine.process("开始游戏")
        engine.process("确认默认创角")
        engine.state.player.spirit_stones = 1000
        engine.state.player.reputation = 50

        out_visit = engine.process("拜山 青云宗")
        self.assertIn("拜山请益 · 青云宗", out_visit)

        out_buy = engine.process("求丹借宝 青云宗 qy-pill")
        self.assertIn("成功求得【聚气丹", out_buy)

        out_spar = engine.process("山门演武 青云宗")
        self.assertIn("山门演武 · 青云宗", out_spar)

        out_bounty = engine.process("山门历练 青云宗 qy-bounty-1")
        self.assertIn("山门历练 · 青云宗", out_bounty)


if __name__ == "__main__":
    unittest.main()
