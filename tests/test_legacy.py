from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.legacy import LEGACIES, LegacyEngine
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


class LegacyTests(unittest.TestCase):
    def test_old_save_defaults_and_ended_snapshot_are_read_only(self) -> None:
        payload = GameState(phase="ended").to_dict()
        for key in ("life_number", "past_lives", "legacy_options", "legacy_choice", "active_legacy", "legacy_applied"):
            payload.pop(key)
        payload["player"]["condition"] = "陨落于古战场"
        state = GameState.from_dict(payload)
        before = state.to_dict()

        snapshot = LegacyEngine.snapshot(state)

        self.assertTrue(snapshot["ended"])
        self.assertEqual(snapshot["latest"]["cause"], "陨落于古战场")
        self.assertEqual(len(snapshot["options"]), 3)
        self.assertEqual(state.to_dict(), before)

    def test_ending_is_recorded_once_with_stable_options(self) -> None:
        state = GameState(phase="ended", turn=28)
        state.player.condition = "战败重伤"

        self.assertTrue(LegacyEngine.ensure_ending(state))
        self.assertFalse(LegacyEngine.ensure_ending(state))
        self.assertEqual(len(state.past_lives), 1)
        self.assertEqual(state.legacy_options, ["tempered-body", "lucid-seed", "hidden-hoard"])
        self.assertEqual(state.past_lives[0]["score"], LegacyEngine.score(state))

    def test_story_completion_unlocks_world_vow_option(self) -> None:
        state = GameState(phase="ended", story_completed=["a", "b", "c", "d"])
        LegacyEngine.ensure_ending(state)
        self.assertIn("world-vow", state.legacy_options)
        self.assertNotIn("hidden-hoard", state.legacy_options)

    def test_real_death_path_creates_chronicle_and_autosaves(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.age = engine.state.player.lifespan - 1
            engine.state.month = 12

            output = engine.process("修炼")

            self.assertEqual(engine.state.phase, "ended")
            self.assertEqual(len(engine.state.past_lives), 1)
            self.assertEqual(engine.state.past_lives[0]["life"], 1)
            self.assertIn("仙途评传", output)
            loaded = engine.saves.load("autosave")
            self.assertEqual(len(loaded.past_lives), 1)

    def test_next_life_requires_choice_and_applies_selected_inheritance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.state.phase = "ended"
            engine.state.player.condition = "陨落于雷劫"

            blocked = engine.process("开始游戏")
            self.assertIn("先亲自铭刻", blocked)
            self.assertEqual(engine.state.phase, "ended")

            chosen = engine.process("铭刻传承 hidden-hoard")
            self.assertIn("袖里余藏", chosen)
            engine.process("开始游戏")
            self.assertEqual(engine.state.phase, "character_creation_basic")
            self.assertEqual(engine.state.life_number, 2)
            self.assertEqual(engine.state.active_legacy, "hidden-hoard")
            self.assertEqual(len(engine.state.past_lives), 1)

            completed = engine.process("确认默认创角")
            self.assertEqual(engine.state.player.spirit_stones, 280)
            self.assertEqual(engine.state.player.resources["聚气丹"], 2)
            self.assertTrue(engine.state.legacy_applied)
            self.assertIn("轮回传承“袖里余藏”苏醒", completed)

            blocked_restart = engine.process("开始游戏")
            self.assertIn("不能以“开始游戏”跳过此生", blocked_restart)
            self.assertEqual(engine.state.player.spirit_stones, 280)
            self.assertEqual(engine.state.life_number, 2)

    def test_every_legacy_has_a_real_bounded_effect(self) -> None:
        for legacy_id, definition in LEGACIES.items():
            with self.subTest(legacy=legacy_id):
                state = GameState(phase="playing", active_legacy=legacy_id)
                before = state.to_dict()
                text = LegacyEngine.apply_inheritance(state)
                self.assertIn(definition.name, text)
                self.assertTrue(state.legacy_applied)
                self.assertNotEqual(state.to_dict(), before)
                self.assertEqual(LegacyEngine.apply_inheritance(state), "")


if __name__ == "__main__":
    unittest.main()
