from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.sect_diplomacy import SectDiplomacyEngine
from xiuxian_simulator.sect_foundation import SectFoundationEngine
from xiuxian_simulator.legacy import LegacyEngine
from xiuxian_simulator.state import GameState
from xiuxian_simulator.world import SectWarEngine, WorldTimelineEngine


ROOT = Path(__file__).resolve().parents[1]


def founded_state() -> GameState:
    state = GameState()
    state.phase = "playing"
    state.turn = 18
    state.calendar_year = 388
    state.player.dao_name = "清微"
    state.player.realm_index = 3
    state.player.stage_index = 1
    state.player.realm = "金丹·中期"
    state.player.reputation = 86
    state.player.spirit_stones = 5000
    SectFoundationEngine.begin(state, "青玄宗")
    SectFoundationEngine.found(state, "harmony")
    state.founded_sect.update({"level": 3, "experience": 380, "renown": 66, "stability": 84, "treasury": 5000})
    state.faction_strengths["青玄宗"] = 82
    return state


class SectDiplomacyTests(unittest.TestCase):
    def test_old_save_snapshot_is_read_only_and_supplies_defaults(self) -> None:
        state = founded_state()
        state.founded_sect.pop("diplomacy")
        before = state.to_dict()

        snapshot = SectDiplomacyEngine.snapshot(state)

        self.assertEqual(state.to_dict(), before)
        self.assertTrue(snapshot["visible"])
        self.assertEqual(len(snapshot["factions"]), 4)
        self.assertEqual(next(item for item in snapshot["factions"] if item["name"] == "血煞盟")["stance"], "敌视")

    def test_founding_initializes_bounded_diplomacy_data(self) -> None:
        state = founded_state()
        diplomacy = state.founded_sect["diplomacy"]

        self.assertEqual(set(diplomacy["relations"]), set(SectDiplomacyEngine.default_data()["relations"]))
        self.assertTrue(all(value == "none" for value in diplomacy["treaties"].values()))
        self.assertEqual(diplomacy["victories"], 0)

    def test_envoy_costs_treasury_and_enforces_annual_action(self) -> None:
        state = founded_state()
        before_relation = state.founded_sect["diplomacy"]["relations"]["青云宗"]

        result = SectDiplomacyEngine.envoy(state, "青云宗")

        self.assertIn("遣使拜访青云宗", result)
        self.assertEqual(state.founded_sect["treasury"], 5000 - SectDiplomacyEngine.ENVOY_COST)
        self.assertGreater(state.founded_sect["diplomacy"]["relations"]["青云宗"], before_relation)
        with self.assertRaisesRegex(ValueError, "本年已经"):
            SectDiplomacyEngine.envoy(state, "丹霞谷")

    def test_trade_and_alliance_have_persistent_finance_effects(self) -> None:
        state = founded_state()
        diplomacy = state.founded_sect["diplomacy"]
        diplomacy["relations"]["丹霞谷"] = 42

        SectDiplomacyEngine.trade_pact(state, "丹霞谷")
        self.assertEqual(SectDiplomacyEngine.monthly_income_bonus(state), 15)
        state.calendar_year += 1
        diplomacy["relations"]["丹霞谷"] = 65
        SectDiplomacyEngine.alliance(state, "丹霞谷")

        self.assertEqual(diplomacy["treaties"]["丹霞谷"], "alliance")
        self.assertEqual(SectDiplomacyEngine.monthly_income_bonus(state), 22)
        income, _, _ = SectFoundationEngine._monthly_finance(state)
        diplomacy["treaties"]["丹霞谷"] = "none"
        income_without_treaty, _, _ = SectFoundationEngine._monthly_finance(state)
        self.assertEqual(income - income_without_treaty, 22)

    def test_pressure_unlocks_player_declared_dynamic_war(self) -> None:
        state = founded_state()
        relation = state.founded_sect["diplomacy"]["relations"]["玄剑门"]
        self.assertEqual(relation, 0)

        SectDiplomacyEngine.pressure(state, "玄剑门")
        state.calendar_year += 1
        result = SectDiplomacyEngine.declare_war(state, "玄剑门")

        self.assertIn("青玄宗向玄剑门宣战", result)
        self.assertEqual(state.active_sect_war["attacker"], "青玄宗")
        self.assertIn("青玄宗", SectWarEngine.factions(state))

    def test_allied_factions_cannot_be_war_opponents(self) -> None:
        state = founded_state()
        state.founded_sect["diplomacy"]["treaties"]["青云宗"] = "alliance"

        with self.assertRaisesRegex(ValueError, "攻守同盟"):
            SectWarEngine.start(state, "青玄宗", "青云宗")

    def test_founded_sect_victory_has_persistent_rewards(self) -> None:
        state = founded_state()
        before_treasury = state.founded_sect["treasury"]
        SectWarEngine.start(state, "青玄宗", "血煞盟")
        state.active_sect_war.update({"months": 5, "momentum": 3})

        result = SectWarEngine.advance(state)

        self.assertIn("青玄宗赢得", result)
        self.assertEqual(state.founded_sect["treasury"], before_treasury + 350)
        self.assertEqual(state.founded_sect["diplomacy"]["victories"], 1)
        self.assertFalse(state.active_sect_war)
        self.assertTrue(any("战胜血煞盟" in entry for entry in state.founded_sect["diplomacy"]["history"]))

    def test_founded_sect_can_fall_without_erasing_its_legacy(self) -> None:
        state = founded_state()
        state.faction_strengths["青玄宗"] = 20
        SectWarEngine.start(state, "血煞盟", "青玄宗")
        state.active_sect_war.update({"months": 5, "momentum": 3})

        result = SectWarEngine.advance(state)

        self.assertIn("青玄宗自九州势力谱中覆灭", result)
        self.assertTrue(state.founded_sect["ruined"])
        self.assertEqual(state.player.sect, "青玄宗")
        self.assertEqual(state.player.sect_rank, "流亡掌门")
        self.assertEqual(state.player.condition, "山门覆灭·流亡")
        self.assertIn("青玄宗", state.fallen_factions)

    def test_founder_participation_uses_ward_and_changes_sect_state(self) -> None:
        state = founded_state()
        state.founded_sect["buildings"]["ward"] = 3
        before_stability = state.founded_sect["stability"]
        SectWarEngine.start(state, "血煞盟", "青玄宗")

        result = SectWarEngine.participate(state, "固守山门")

        self.assertEqual(result.chance, min(95, 62 + state.player.dao_heart + 15))
        self.assertNotEqual(state.founded_sect["stability"], before_stability)
        self.assertTrue(any("固守山门" in entry for entry in state.sect_foundation_history))

    def test_peace_ends_war_and_records_both_histories(self) -> None:
        state = founded_state()
        SectWarEngine.start(state, "血煞盟", "青玄宗")
        state.active_sect_war["months"] = 2

        result = SectDiplomacyEngine.seek_peace(state, "血煞盟")

        self.assertIn("议和止戈", result)
        self.assertFalse(state.active_sect_war)
        self.assertTrue(any("议和止戈" in entry for entry in state.sect_war_history))
        self.assertTrue(any("议和止戈" in entry for entry in state.founded_sect["diplomacy"]["history"]))

    def test_engine_diplomacy_action_advances_time_and_autosaves(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = build_engine(ROOT)
            engine.saves.save_dir = Path(temp_dir)
            engine.state = founded_state()
            before_turn = engine.state.turn

            result = engine.process("宗门遣使 青云宗")

            self.assertIn("宗门外务", result)
            self.assertEqual(engine.state.turn, before_turn + 1)
            self.assertTrue((Path(temp_dir) / "autosave.json").exists())
            self.assertIn("青云宗", engine.process("宗门外交"))

    def test_snapshot_exposes_war_from_founders_perspective(self) -> None:
        state = founded_state()
        SectWarEngine.start(state, "血煞盟", "青玄宗")
        state.active_sect_war.update({"months": 3, "momentum": 2, "player_acted": True})

        snapshot = SectDiplomacyEngine.snapshot(state)

        self.assertTrue(snapshot["war"]["active"])
        self.assertEqual(snapshot["war"]["target"], "血煞盟")
        self.assertEqual(snapshot["war"]["momentum"], -2)
        self.assertEqual(snapshot["war"]["momentum_label"], "陷入劣势")
        enemy = next(item for item in snapshot["factions"] if item["name"] == "血煞盟")
        self.assertTrue(enemy["at_war"])
        self.assertEqual(enemy["primary"]["label"], "议和止戈")

    def test_diplomatic_victories_enter_final_chronicle(self) -> None:
        state = founded_state()
        before = LegacyEngine.score(state)
        state.founded_sect["diplomacy"]["victories"] = 2

        chronicle = LegacyEngine.chronicle(state)

        self.assertEqual(LegacyEngine.score(state), before + 90)
        self.assertIn("开宗立派：青玄宗·争锋2胜", chronicle["highlights"])

    def test_eight_year_world_simulation_is_reproducible_and_bounded(self) -> None:
        left = founded_state()
        right = GameState.from_dict(left.to_dict())

        for state in (left, right):
            for _ in range(96):
                state.advance_month()
                WorldTimelineEngine.tick(state)
                SectFoundationEngine.tick_month(state)

        self.assertEqual(left.to_dict(), right.to_dict())
        self.assertLessEqual(len(left.sect_war_history), 30)
        self.assertLessEqual(len(left.founded_sect["diplomacy"]["history"]), 30)
        self.assertTrue(all(0 <= strength <= 100 for strength in left.faction_strengths.values()))


if __name__ == "__main__":
    unittest.main()
