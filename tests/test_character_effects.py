from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.progression import ProgressionEngine
from xiuxian_simulator.relationships import NPCS, RelationshipEngine
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


class CharacterEffectTests(unittest.TestCase):
    def test_background_and_initial_affinity_are_usable_after_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.process("开始游戏")
            engine.process("姓名=林渡；性别=女；年龄=18；相貌=清秀；出身=没落世家；道途=问道飞升")
            engine.process(
                "灵根=木火双灵根；体质=凡体；资质=10；悟性=10；神识=10；"
                "遁速=10；道心=10；仙缘=10；天赋=天资聪颖、过目不忘、身轻如燕、天生道心、桃花运"
            )
            self.assertEqual(engine.state.phase, "playing")
            self.assertIn("青木长生诀", engine.state.player.known_techniques)
            self.assertEqual({RelationshipEngine.affinity(engine.state, name) for name in NPCS}, {20})

    def test_element_and_sword_bonuses_change_combat_damage(self) -> None:
        for element, purpose, modifier in (
            ("火", "spell:流火术", "fire_damage_multiplier"),
            ("冰", "spell:冰魄术", "ice_damage_multiplier"),
            ("金", "spell:庚金剑气", "sword_damage_multiplier"),
            ("雷", "spell:雷鸣术", "element_damage_multiplier"),
        ):
            with self.subTest(modifier=modifier):
                baseline = GameState(phase="playing")
                boosted = GameState.from_dict(baseline.to_dict())
                boosted.player.modifiers[modifier] = 1.3
                for state in (baseline, boosted):
                    CombatEngine.prepare(state, "噬灵獾")
                    CombatEngine.start(state)
                    state.combat["player_observed"] = True
                ordinary = CombatEngine._player_strike(baseline, 1.0, purpose, element)
                enhanced = CombatEngine._player_strike(boosted, 1.0, purpose, element)
                self.assertTrue(ordinary.hit)
                self.assertGreater(enhanced.damage, ordinary.damage)

    def test_dual_cultivation_trait_stacks_with_constitution(self) -> None:
        normal = GameState(phase="playing")
        normal.player.cultivation_required = 1000
        normal.dao_partners.append("顾清玄")
        boosted = GameState.from_dict(normal.to_dict())
        boosted.player.modifiers["dual_cultivation_multiplier"] = 1.2
        ProgressionEngine.apply_destiny_trait(boosted.player, "双修悟道")
        baseline_gain, _ = RelationshipEngine.dual_cultivate(normal, "顾清玄")
        enhanced_gain, _ = RelationshipEngine.dual_cultivate(boosted, "顾清玄")
        self.assertGreater(enhanced_gain, baseline_gain)

    def test_blood_trait_heals_after_real_victory_only(self) -> None:
        state = GameState(phase="playing")
        state.player.health = 40
        state.player.destiny_traits.append("血魔噬魂")
        CombatEngine.prepare(state, "山野劫修")
        CombatEngine.finish_victory(state)
        self.assertEqual(state.player.health, 50)
        sparring = GameState(phase="playing")
        sparring.player.health = 40
        sparring.player.destiny_traits.append("血魔噬魂")
        CombatEngine.prepare(sparring, "山野劫修", mode="切磋")
        CombatEngine.finish_victory(sparring)
        self.assertEqual(sparring.player.health, 40)


if __name__ == "__main__":
    unittest.main()
