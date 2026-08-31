from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.art_mastery import ArtMasteryEngine
from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.progression import ProgressionEngine
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


class ArtMasteryTests(unittest.TestCase):
    def test_old_save_defaults_are_compatible_and_snapshot_is_read_only(self) -> None:
        payload = GameState(phase="playing").to_dict()
        payload.pop("technique_mastery")
        payload.pop("spell_mastery")
        payload.pop("art_mastery_history")
        state = GameState.from_dict(payload)
        before = state.to_dict()
        snapshot = ArtMasteryEngine.snapshot(state)
        self.assertEqual(snapshot["known_count"], 2)
        self.assertEqual(snapshot["primary"]["level_label"], "初窥")
        self.assertEqual(state.to_dict(), before)

    def test_cultivation_and_retreat_grow_equipped_techniques(self) -> None:
        state = GameState(phase="playing")
        state.player.known_techniques.append("赤炎真经")
        state.player.equipped_auxiliary_techniques = ["赤炎真经"]
        advances = ArtMasteryEngine.gain_cultivation(state, 6, retreat=True)
        self.assertGreater(state.technique_mastery["聚气诀"], state.technique_mastery["赤炎真经"])
        self.assertIn("聚气诀·小成", advances)

    def test_mastery_changes_real_cultivation_spell_power_and_cost(self) -> None:
        novice = GameState(phase="playing")
        master = GameState(phase="playing")
        master.technique_mastery["聚气诀"] = 480
        master.spell_mastery["流火术"] = 480
        self.assertGreater(ProgressionEngine.cultivation_gain(master).total, ProgressionEngine.cultivation_gain(novice).total)
        self.assertGreater(ArtMasteryEngine.spell_power(master, "流火术", 1.45), 1.45)
        self.assertLess(ArtMasteryEngine.spell_cost(master, "流火术", 20), 20)

    def test_combat_cast_grants_mastery_and_uses_discounted_cost(self) -> None:
        state = GameState(phase="playing", rng_seed=91)
        state.spell_mastery["流火术"] = 260
        CombatEngine.prepare(state, "筑基客卿")
        CombatEngine.start(state)
        before_spirit = state.player.spirit
        result = CombatEngine.act(state, "施法 流火术")
        self.assertEqual(before_spirit - state.player.spirit, 19)
        self.assertGreater(state.spell_mastery["流火术"], 260)
        self.assertIn("灵力 -19", result.player_text)

    def test_study_action_costs_spirit_advances_time_and_autosaves(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before_turn = engine.state.turn
            output = engine.process("参研道法 聚气诀")
            self.assertEqual(engine.state.turn, before_turn + 1)
            self.assertEqual(engine.state.player.spirit, 88)
            self.assertGreater(engine.state.technique_mastery["聚气诀"], 0)
            self.assertIn("参研 · 聚气诀", output)
            self.assertTrue((Path(temp_dir) / "autosave.json").is_file())

    def test_round_mastery_cannot_be_studied(self) -> None:
        state = GameState(phase="playing", technique_mastery={"聚气诀": 480})
        with self.assertRaisesRegex(ValueError, "圆满"):
            ArtMasteryEngine.study(state, "聚气诀")


if __name__ == "__main__":
    unittest.main()
