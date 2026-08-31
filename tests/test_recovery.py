from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.items import InventoryEngine
from xiuxian_simulator.progression import ProgressionEngine
from xiuxian_simulator.recovery import RecoveryEngine
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


class RecoveryTests(unittest.TestCase):
    def test_old_save_condition_is_exposed_without_mutating_snapshot(self) -> None:
        payload = GameState(phase="playing").to_dict()
        payload.pop("injuries")
        payload.pop("injury_history")
        payload["player"]["condition"] = "战败重伤"
        state = GameState.from_dict(payload)
        before = state.to_dict()

        snapshot = RecoveryEngine.snapshot(state)

        self.assertTrue(snapshot["active"])
        self.assertEqual(snapshot["injuries"][0]["id"], "flesh")
        self.assertEqual(snapshot["injuries"][0]["severity_label"], "沉重")
        self.assertEqual(state.to_dict(), before)

    def test_injuries_apply_real_cultivation_and_combat_penalties(self) -> None:
        healthy = GameState(phase="playing", rng_seed=44)
        state = GameState.from_dict(healthy.to_dict())
        RecoveryEngine.register(state, "meridian", 2, "术法反噬")

        self.assertAlmostEqual(RecoveryEngine.cultivation_multiplier(state), 0.82)
        self.assertAlmostEqual(RecoveryEngine.combat_multiplier(state), 0.88)
        self.assertAlmostEqual(RecoveryEngine.damage_taken_multiplier(state), 1.08)
        self.assertEqual(RecoveryEngine.speed_penalty(state), 1)
        self.assertIn("沉重经脉受损", state.player.condition)
        self.assertLess(ProgressionEngine.cultivation_gain(state).total, ProgressionEngine.cultivation_gain(healthy).total)

        CombatEngine.prepare(healthy, "山野劫修")
        CombatEngine.prepare(state, "山野劫修")
        CombatEngine.start(healthy)
        CombatEngine.start(state)
        healthy_before = int(healthy.combat["enemy_health"])
        wounded_before = int(state.combat["enemy_health"])
        CombatEngine.act(healthy, "攻击")
        CombatEngine.act(state, "攻击")
        healthy_damage = healthy_before - int(healthy.combat["enemy_health"])
        wounded_damage = wounded_before - int(state.combat["enemy_health"])
        self.assertGreater(healthy_damage, wounded_damage)

    def test_monthly_recovery_cures_injury_and_clears_condition(self) -> None:
        state = GameState(phase="playing")
        RecoveryEngine.register(state, "flesh", 1, "山路跌伤")

        self.assertEqual(state.injuries["flesh"]["months_left"], 2)
        self.assertEqual(RecoveryEngine.tick_month(state), [])
        events = RecoveryEngine.tick_month(state)

        self.assertEqual(events, ["筋骨外伤已随岁月痊愈"])
        self.assertFalse(RecoveryEngine.has_active(state))
        self.assertEqual(state.player.condition, "无")

    def test_rest_advances_time_recovers_resources_and_autosaves(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.health = 50
            engine.state.player.spirit = 40
            RecoveryEngine.register(engine.state, "flesh", 2, "斗法失利")
            before_turn = engine.state.turn

            output = engine.process("静养")

            self.assertEqual(engine.state.turn, before_turn + 1)
            self.assertGreater(engine.state.player.health, 50)
            self.assertGreater(engine.state.player.spirit, 40)
            self.assertLess(engine.state.injuries["flesh"]["months_left"], 4)
            self.assertIn("闭门静养", output)
            self.assertTrue((Path(temp_dir) / "autosave.json").is_file())

    def test_healing_pill_treats_injury_even_at_full_health(self) -> None:
        state = GameState(phase="playing")
        state.player.resources["疗伤丹"] = 1
        RecoveryEngine.register(state, "meridian", 2, "强行运功")

        result = InventoryEngine.use(state, "疗伤丹")

        self.assertIn("调养期缩短 3 月", result)
        self.assertEqual(state.injuries["meridian"]["months_left"], 3)
        self.assertNotIn("疗伤丹", state.player.resources)

    def test_cave_recuperation_treats_wound_at_full_vitals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.cave_facilities["静室"] = 1
            engine.state.cave_spirit_energy = 20
            RecoveryEngine.register(engine.state, "foundation", 1, "破境暗伤")

            output = engine.process("洞府调息")

            self.assertIn("洞府调息", output)
            # 调息消耗 10 灵蕴，同月洞府按既有规则自然生成 3 点。
            self.assertEqual(engine.state.cave_spirit_energy, 13)
            self.assertLess(engine.state.injuries["foundation"]["months_left"], 6)

    def test_breakthrough_is_blocked_until_wounds_are_healed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.stage_index = 3
            engine.state.player.realm = "炼气·圆满"
            engine.state.player.cultivation = engine.state.player.cultivation_required
            RecoveryEngine.register(engine.state, "heart", 1, "问心失守")
            before_turn = engine.state.turn

            output = engine.process("突破")

            self.assertEqual(engine.state.turn, before_turn)
            self.assertEqual(engine.state.phase, "playing")
            self.assertIn("伤势未愈", output)

    def test_invalid_saved_severity_is_safely_clamped(self) -> None:
        state = GameState(
            phase="playing",
            injuries={"flesh": {"severity": 99, "months_left": 2, "source": "旧档异常"}},
        )
        snapshot = RecoveryEngine.snapshot(state)
        self.assertEqual(snapshot["injuries"][0]["severity"], 3)
        self.assertAlmostEqual(snapshot["penalties"]["combat"], 0.84)


if __name__ == "__main__":
    unittest.main()
