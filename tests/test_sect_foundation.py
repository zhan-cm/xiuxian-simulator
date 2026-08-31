from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.choices import DecisionCatalog
from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.legacy import LegacyEngine
from xiuxian_simulator.sect_foundation import BUILDINGS, SectFoundationEngine
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


def eligible_state() -> GameState:
    state = GameState(phase="playing")
    state.player.realm_index = 3
    state.player.realm = "金丹·初期"
    state.player.reputation = 80
    state.player.spirit_stones = 5000
    return state


def founded_state(doctrine: str = "harmony") -> GameState:
    state = eligible_state()
    SectFoundationEngine.begin(state, "青玄宗")
    SectFoundationEngine.found(state, doctrine)
    return state


class SectFoundationTests(unittest.TestCase):
    def test_old_save_defaults_and_snapshot_are_read_only(self) -> None:
        state = GameState.from_dict({"version": "0.52.0", "phase": "playing", "player": {"name": "旧档修士"}})
        before = state.to_dict()

        snapshot = SectFoundationEngine.snapshot(state)

        self.assertFalse(snapshot["founded"])
        self.assertFalse(snapshot["visible"])
        self.assertEqual(state.founded_sect, {})
        self.assertEqual(state.sect_disciples, [])
        self.assertEqual(state.to_dict(), before)

    def test_foundation_requires_identity_realm_reputation_and_stones(self) -> None:
        state = GameState(phase="playing")
        available, reason = SectFoundationEngine.foundation_availability(state)
        self.assertFalse(available)
        self.assertIn("境界不足", reason)

        state.player.realm_index = 3
        state.player.realm = "金丹·初期"
        state.player.reputation = 60
        state.player.spirit_stones = 2000
        state.player.sect = "青云宗"
        available, reason = SectFoundationEngine.foundation_availability(state)
        self.assertFalse(available)
        self.assertIn("散修身份", reason)

        state.player.sect = "散修"
        self.assertEqual(SectFoundationEngine.foundation_availability(state), (True, ""))

    def test_begin_cancel_and_name_validation_do_not_spend_resources(self) -> None:
        state = eligible_state()
        before = state.player.spirit_stones

        with self.assertRaisesRegex(ValueError, "2～8"):
            SectFoundationEngine.begin(state, "宗")
        name = SectFoundationEngine.begin(state, "青玄宗")
        self.assertEqual(name, "青玄宗")
        self.assertEqual(state.phase, "sect_foundation_choice")
        self.assertEqual(state.player.spirit_stones, before)

        decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(state)
        self.assertEqual(len(decision["choices"]), 4)
        self.assertEqual(decision["choices"][0]["action"], "立宗道统 sword")
        SectFoundationEngine.cancel(state)
        self.assertEqual(state.phase, "playing")
        self.assertEqual(state.player.spirit_stones, before)

    def test_foundation_creates_real_faction_and_unique_disciples_once(self) -> None:
        state = eligible_state()
        SectFoundationEngine.begin(state, "青玄宗")
        doctrine = SectFoundationEngine.found(state, "alchemy")

        self.assertEqual(doctrine.name, "丹鼎长生")
        self.assertEqual(state.player.spirit_stones, 3000)
        self.assertEqual(state.player.sect, "青玄宗")
        self.assertEqual(state.player.sect_rank, "掌门")
        self.assertEqual(state.faction_strengths["青玄宗"], 34)
        self.assertEqual(len(state.sect_disciples), 2)
        self.assertEqual(len({item["name"] for item in state.sect_disciples}), 2)
        self.assertTrue(state.world_milestones)
        with self.assertRaisesRegex(ValueError, "已经开宗"):
            SectFoundationEngine.begin(state, "第二宗")

    def test_recruitment_consumes_treasury_and_has_six_month_cooldown(self) -> None:
        state = founded_state()
        state.founded_sect["renown"] = 100
        before_count = len(state.sect_disciples)
        before_treasury = state.founded_sect["treasury"]

        result = SectFoundationEngine.recruit(state)

        self.assertLessEqual(result["chance"], 95)
        self.assertEqual(state.founded_sect["treasury"], before_treasury - SectFoundationEngine.RECRUIT_COST)
        self.assertEqual(len(state.sect_disciples), before_count + (1 if result["success"] else 0))
        with self.assertRaisesRegex(ValueError, "等待 6 个月"):
            SectFoundationEngine.recruit(state)

    def test_building_costs_scale_and_levels_are_capped(self) -> None:
        state = founded_state()
        state.founded_sect["treasury"] = 10000
        definition = BUILDINGS["academy"]

        costs = [SectFoundationEngine.upgrade_building(state, "academy")["cost"] for _ in range(3)]

        self.assertEqual(costs, [definition.base_cost, definition.base_cost * 2, definition.base_cost * 3])
        self.assertEqual(state.founded_sect["buildings"]["academy"], 3)
        with self.assertRaisesRegex(ValueError, "达到当前版本上限"):
            SectFoundationEngine.upgrade_building(state, "academy")

    def test_focus_and_teaching_are_limited_per_year(self) -> None:
        state = founded_state()
        state.founded_sect["treasury"] = 1000
        name = SectFoundationEngine.set_focus(state, "elite")
        self.assertEqual(name, "精研道统")
        with self.assertRaisesRegex(ValueError, "每个自然年"):
            SectFoundationEngine.set_focus(state, "world")

        before_insight = state.player.dao_insight
        result = SectFoundationEngine.teach(state)
        self.assertGreater(result["progress"], 20)
        self.assertEqual(state.player.dao_insight, before_insight + result["insight"])
        with self.assertRaisesRegex(ValueError, "本年已经"):
            SectFoundationEngine.teach(state)

    def test_monthly_simulation_is_bounded_and_reproducible(self) -> None:
        left = founded_state("sword")
        left.founded_sect["treasury"] = 1000
        right = GameState.from_dict(left.to_dict())

        for _ in range(120):
            left.advance_month()
            right.advance_month()
            SectFoundationEngine.tick_month(left)
            SectFoundationEngine.tick_month(right)

        self.assertEqual(left.founded_sect, right.founded_sect)
        self.assertEqual(left.sect_disciples, right.sect_disciples)
        self.assertEqual(left.faction_strengths["青玄宗"], right.faction_strengths["青玄宗"])
        self.assertLessEqual(len(left.sect_foundation_history), 40)
        self.assertGreater(left.founded_sect["experience"], 0)
        self.assertGreaterEqual(left.founded_sect["treasury"], 0)
        self.assertTrue(all(0 <= item["loyalty"] <= 100 for item in left.sect_disciples))

    def test_engine_actions_advance_time_autosave_and_reject_founder_defection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.state = eligible_state()

            prepared = engine.process("开宗立派 青玄宗")
            self.assertIn("等待择定", prepared)
            founded = engine.process("立宗道统 harmony")
            self.assertIn("开山弟子", founded)
            turn = engine.state.turn
            taught = engine.process("宗门传法")
            self.assertIn("掌门传法", taught)
            self.assertEqual(engine.state.turn, turn + 1)
            engine.state.founded_sect["treasury"] = 2000
            built = engine.process("营造山门 academy")
            self.assertIn("工期 3 个月", built)
            self.assertEqual(engine.state.turn, turn + 4)
            self.assertIn("不能以叛宗", engine.process("叛宗"))
            loaded = engine.saves.load("autosave")
            self.assertEqual(loaded.founded_sect["name"], "青玄宗")
            self.assertEqual(loaded.founded_sect["buildings"]["academy"], 1)

    def test_founding_a_sect_adds_value_to_life_chronicle(self) -> None:
        plain = eligible_state()
        founder = founded_state()
        self.assertGreater(LegacyEngine.score(founder), LegacyEngine.score(plain))
        founder.phase = "ended"
        chronicle = LegacyEngine.chronicle(founder)
        self.assertIn("开宗立派：青玄宗", chronicle["highlights"])


if __name__ == "__main__":
    unittest.main()
