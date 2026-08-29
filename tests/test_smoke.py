from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.choices import DecisionCatalog
from xiuxian_simulator.economy import EconomyEngine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.arts import ArtsEngine
from xiuxian_simulator.crafting import CraftingEngine
from xiuxian_simulator.relationships import RelationshipEngine
from xiuxian_simulator.adventures import AdventureEngine
from xiuxian_simulator.ecology import NpcEcologyEngine
from xiuxian_simulator.world import SectProgressionEngine, SectWarEngine, WorldEvolutionEngine, WorldTimelineEngine
from xiuxian_simulator.webapp import WebApplication
from xiuxian_simulator.config import Settings
from xiuxian_simulator.diagnostics import diagnostics_text, run_diagnostics
from xiuxian_simulator.narrator import FallbackNarrator, LocalNarrator, NarrationError, OpenAINarrator
from xiuxian_simulator.presentation import present_action, welcome_presentation
from xiuxian_simulator.progression import ProgressionEngine
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager
from xiuxian_simulator.state import GameState
from xiuxian_simulator.journey import JourneyEngine
from xiuxian_simulator.commissions import CommissionEngine
from xiuxian_simulator.story import StoryEngine


class SimulatorSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rules = RuleBook.load(ROOT / "docs" / "修仙模拟器 · 问道长生.docx")

    def make_engine(self, save_dir: Path) -> GameEngine:
        return GameEngine(self.rules, SaveManager(save_dir), LocalNarrator())

    def test_rule_document_contains_required_sections(self) -> None:
        self.assertIn("每回合只推进 1 个事件节点", self.rules.text)
        self.assertIn("十九、存档系统", self.rules.text)

    def test_start_create_cultivate_and_autosave(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            self.assertIn("创角大面板", engine.process("开始游戏"))
            self.assertIn("状态卡", engine.process("确认默认创角"))
            before = engine.state.player.cultivation
            result = engine.process("修炼")
            self.assertGreater(engine.state.player.cultivation, before)
            self.assertIn("修为 +", result)
            autosave = Path(temp_dir) / "autosave.json"
            self.assertTrue(autosave.is_file())
            payload = json.loads(autosave.read_text(encoding="utf-8"))
            self.assertEqual(payload["turn"], engine.state.turn)

    def test_named_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.process("存档 初入仙途")
            engine.process("修炼")
            result = engine.process("读档 初入仙途")
            self.assertIn("读档完成", result)
            self.assertEqual(engine.state.player.cultivation, 0)

    def test_journey_chapters_track_progress_and_grant_rewards_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            initial = JourneyEngine.snapshot(engine.state)
            self.assertEqual(initial["active_chapter_id"], "chapter-1")
            self.assertEqual(initial["active"]["completed_tasks"], 0)

            engine.process("修炼")
            engine.state.remember("探索青岳山麓：发现灵药")
            engine.state.player.resources["灵药"] = 1
            progressed = JourneyEngine.snapshot(engine.state)
            self.assertEqual(progressed["active"]["completed_tasks"], 3)

            stones_before = engine.state.player.spirit_stones
            for claim_id in ("c1-cultivate", "c1-explore", "c1-resource"):
                self.assertIn("道途奖励", engine.process(f"领取道途奖励 {claim_id}"))
            self.assertTrue(JourneyEngine.snapshot(engine.state)["active"]["reward_ready"])
            self.assertIn("初涉仙途章成", engine.process("领取道途奖励 chapter-1"))
            self.assertGreater(engine.state.player.spirit_stones, stones_before)
            self.assertEqual(engine.state.journey_points, 60)
            self.assertEqual(JourneyEngine.snapshot(engine.state)["active_chapter_id"], "chapter-2")

            points_before = engine.state.journey_points
            repeated = engine.process("领取道途奖励 c1-cultivate")
            self.assertIn("已经领取", repeated)
            self.assertEqual(engine.state.journey_points, points_before)

    def test_journey_combat_counter_and_old_save_defaults(self) -> None:
        state = GameState.from_dict({"phase": "playing", "player": {}})
        self.assertEqual(state.journey_points, 0)
        self.assertEqual(state.journey_claims, [])
        JourneyEngine.mark(state, "combat_victory")
        self.assertEqual(state.journey_counters["combat_victory"], 1)
        chapter = JourneyEngine.snapshot(state)["chapters"][2]
        victory = next(task for task in chapter["tasks"] if task["id"] == "c3-victory")
        self.assertTrue(victory["complete"])

    def test_commission_resource_delivery_is_persistent_and_idempotent(self) -> None:
        state = GameState(phase="playing", turn=1)
        board = CommissionEngine.snapshot(state)
        herb = next(item for item in board["offers"] if item["template_id"] == "herb-delivery")
        message = CommissionEngine.accept(state, herb["id"])
        self.assertIn("已接取", message)
        self.assertEqual(len(state.active_commissions), 1)
        state.player.resources["灵药"] = 3
        active = CommissionEngine.snapshot(state)["active"][0]
        self.assertTrue(active["ready"])
        stones_before = state.player.spirit_stones
        reward = CommissionEngine.deliver(state, herb["id"])
        self.assertIn("交付完成", reward)
        self.assertEqual(state.player.resources.get("灵药", 0), 0)
        self.assertGreater(state.player.spirit_stones, stones_before)
        self.assertEqual(state.commission_renown, 1)
        with self.assertRaisesRegex(ValueError, "没有追踪"):
            CommissionEngine.deliver(state, herb["id"])

    def test_commission_commands_share_engine_autosave_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            board = CommissionEngine.snapshot(engine.state)
            herb = next(item for item in board["offers"] if item["template_id"] == "herb-delivery")
            self.assertIn("接取委托", engine.process(str(herb["accept_action"])))
            engine.state.player.resources["灵药"] = 3
            self.assertIn("委托交付", engine.process(f"交付委托 {herb['id']}"))
            persisted = SaveManager(Path(temp_dir)).load("autosave")
            self.assertIn(herb["id"], persisted.completed_commissions)
            self.assertEqual(persisted.commission_renown, 1)

    def test_commission_counter_progress_limits_and_expiry(self) -> None:
        state = GameState(phase="playing", turn=1)
        board = CommissionEngine.snapshot(state)
        scout = next(item for item in board["offers"] if item["template_id"] == "mountain-survey")
        hunt = next(item for item in board["offers"] if item["template_id"] == "monster-hunt")
        CommissionEngine.accept(state, scout["id"])
        CommissionEngine.accept(state, hunt["id"])
        with self.assertRaisesRegex(ValueError, "最多追踪"):
            extra = next(item for item in board["offers"] if item["template_id"] == "artisan-order")
            CommissionEngine.accept(state, extra["id"])
        CommissionEngine.mark(state, "exploration", 2)
        ready = next(item for item in CommissionEngine.snapshot(state)["active"] if item["template_id"] == "mountain-survey")
        self.assertTrue(ready["ready"])
        CommissionEngine.deliver(state, scout["id"])
        deadline = int(state.active_commissions[hunt["id"]]["deadline_turn"])
        while state.turn <= deadline:
            state.advance_month()
        self.assertEqual(CommissionEngine.expire_overdue(state), ["除祟悬榜"])
        self.assertNotIn(hunt["id"], state.active_commissions)

    def test_old_save_defaults_include_commission_ledger(self) -> None:
        state = GameState.from_dict({"phase": "playing", "player": {}})
        self.assertEqual(state.active_commissions, {})
        self.assertEqual(state.completed_commissions, [])
        self.assertEqual(state.commission_renown, 0)

    def test_story_branch_changes_world_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            self.assertIn("潮声初闻", engine.process("推进主线"))
            self.assertEqual(engine.state.phase, "main_story_choice")
            before = engine.state.faction_strengths["青云宗"]
            result = engine.process("主线选择 seek-counsel")
            self.assertIn("声望 +3", result)
            self.assertEqual(engine.state.phase, "playing")
            self.assertIn("tide-whisper", engine.state.story_completed)
            self.assertGreater(engine.state.faction_strengths["青云宗"], before)
            loaded = SaveManager(Path(temp_dir)).load("autosave")
            self.assertEqual(loaded.story_choices["tide-whisper"], "seek-counsel")

    def test_story_unlocks_from_real_exploration_and_rejects_unpayable_choice(self) -> None:
        state = GameState(phase="playing")
        StoryEngine.begin(state)
        StoryEngine.resolve(state, "observe")
        self.assertFalse(StoryEngine.snapshot(state)["available"])
        state.journey_counters["exploration"] = 2
        node = StoryEngine.begin(state)
        self.assertEqual(node.id, "vein-rift")
        state.player.spirit_stones = 0
        with self.assertRaisesRegex(ValueError, "120 灵石"):
            StoryEngine.resolve(state, "seal")
        self.assertEqual(state.phase, "main_story_choice")
        self.assertNotIn("vein-rift", state.story_completed)

    def test_old_save_defaults_include_story_ledger(self) -> None:
        state = GameState.from_dict({"phase": "playing", "player": {}})
        self.assertEqual(state.story_completed, [])
        self.assertEqual(state.story_choices, {})
        self.assertEqual(state.pending_story_node, "")

    def test_save_summaries_are_safe_and_newest_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            state = GameState(phase="playing", turn=12, calendar_year=388, month=4)
            state.player.name = "林渡"
            state.player.dao_name = "照微"
            manager.save("春日闭关", state)
            summaries = manager.list_summaries()
            self.assertEqual(len(summaries), 1)
            self.assertEqual(summaries[0]["name"], "春日闭关")
            self.assertEqual(summaries[0]["player_name"], "林渡")
            self.assertEqual(summaries[0]["turn"], 12)
            self.assertNotIn("path", summaries[0])

    def test_overwriting_save_keeps_previous_snapshot_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            previous = GameState(phase="playing", turn=20)
            current = GameState(phase="playing", turn=21)
            manager.save("autosave", previous)
            manager.save("autosave", current)
            backup = Path(temp_dir) / "autosave.json.bak"
            self.assertTrue(backup.is_file())
            self.assertEqual(json.loads(backup.read_text(encoding="utf-8"))["turn"], 20)
            self.assertEqual(manager.load("autosave").turn, 21)

    def test_two_panel_custom_character_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            first = engine.process("姓名=林渡；性别=女；年龄=18；相貌=清冷出众；出身=8；道途=问道飞升")
            self.assertIn("第二面", first)
            second = engine.process(
                "灵根=木火双灵根；体质=凡体；资质=10；悟性=10；神识=10；"
                "遁速=10；道心=10；仙缘=10；天赋=天资聪颖、过目不忘、身轻如燕、天生道心、气运加身"
            )
            self.assertIn("创角完成", second)
            self.assertEqual(engine.state.player.name, "林渡")
            self.assertEqual(engine.state.player.background, "书香门第")
            self.assertEqual(engine.state.player.comprehension, 16)
            self.assertEqual(engine.state.player.appearance, "出众")

    def test_character_creation_rejects_bad_attribute_total(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("姓名=林渡；性别=女；年龄=18；相貌=清秀；出身=1；道途=1")
            result = engine.process(
                "灵根=木灵根；体质=凡体；资质=9；悟性=9；神识=9；"
                "遁速=9；道心=9；仙缘=9；天赋=天资聪颖、过目不忘、身轻如燕、天生道心、气运加身"
            )
            self.assertIn("合计必须为 60", result)
            self.assertEqual(engine.state.phase, "character_creation_traits")

    def test_character_creation_rejects_bad_talent_cost(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("姓名=林渡；性别=女；年龄=18；相貌=清秀；出身=1；道途=1")
            result = engine.process(
                "灵根=木灵根；体质=凡体；资质=10；悟性=10；神识=10；"
                "遁速=10；道心=10；仙缘=10；天赋=天资聪颖"
            )
            self.assertIn("正好使用 5 点", result)

    def test_v01_save_payload_migrates_with_new_defaults(self) -> None:
        payload = {
            "version": "0.1.0",
            "phase": "playing",
            "turn": 3,
            "calendar_year": 387,
            "month": 3,
            "player": {"name": "旧档修士", "cultivation": 42},
            "main_quest": "灵气潮汐将至",
            "history": [],
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.name, "旧档修士")
        self.assertEqual(state.player.cultivation, 42)
        self.assertEqual(state.player.constitution, "凡体")
        self.assertEqual(state.character_draft, {})

    def test_cultivation_formula_and_retreat_multiplier(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            normal = ProgressionEngine.cultivation_gain(engine.state, retreat=False)
            retreat = ProgressionEngine.cultivation_gain(engine.state, retreat=True)
            self.assertEqual(retreat.retreat, 2.0)
            self.assertLessEqual(abs(retreat.total - normal.total * 2), 1)
            self.assertEqual(normal.spiritual_root, 1.6)

    def test_multi_month_retreat_advances_time_and_caps_cultivation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            result = engine.process("闭关3月")
            self.assertEqual(engine.state.month, 3)
            self.assertEqual(engine.state.turn, 3)
            self.assertEqual(engine.state.player.cultivation, engine.state.player.cultivation_required)
            self.assertIn("自动出关", result)
            self.assertIn("结算：", result)

    def test_small_breakthrough_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = self.make_engine(Path(left_dir))
            right = self.make_engine(Path(right_dir))
            for engine in (left, right):
                engine.process("开始游戏")
                engine.process("确认默认创角")
                engine.state.player.cultivation = engine.state.player.cultivation_required
                engine.state.rng_seed = 42
            left_result = left.process("突破")
            right_result = right.process("突破")
            self.assertEqual(left_result, right_result)
            self.assertEqual(left.state.player.stage_index, right.state.player.stage_index)
            self.assertEqual(left.state.player.cultivation, right.state.player.cultivation)

    def test_lifespan_exhaustion_ends_game(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.month = 12
            engine.state.player.age = 99
            engine.state.player.lifespan = 100
            result = engine.process("修炼")
            self.assertEqual(engine.state.phase, "ended")
            self.assertIn("坐化结局", result)

    def test_major_breakthrough_requires_route_resource(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.stage_index = 3
            engine.state.player.cultivation = engine.state.player.cultivation_required
            result = engine.process("突破 人道")
            self.assertIn("筑基丹×1", result)
            self.assertEqual(engine.state.player.realm_index, 0)

    def test_major_breakthrough_route_opens_button_backed_choice_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.stage_index = 3
            engine.state.player.cultivation = engine.state.player.cultivation_required
            result = engine.process("突破")
            self.assertIn("大境界突破路线", result)
            self.assertEqual(engine.state.phase, "major_breakthrough_choice")
            decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(engine.state)
            self.assertEqual([choice["action"] for choice in decision["choices"][:3]], ["突破 人道", "突破 地道", "突破 天道"])
            cancelled = engine.process("取消突破")
            self.assertIn("没有消耗", cancelled)
            self.assertEqual(engine.state.phase, "playing")

    def test_major_breakthrough_success_and_destiny_choice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.stage_index = 3
            player.cultivation = player.cultivation_required
            player.dao_heart = 20
            player.fortune = 20
            player.merit = 100
            player.resources["筑基丹"] = 1
            engine.state.rng_seed = 1
            result = engine.process("突破 人道")
            self.assertIn("逆天改命", result)
            self.assertEqual(player.realm_index, 1)
            self.assertNotIn("筑基丹", player.resources)
            self.assertEqual(engine.state.phase, "breakthrough_talent_choice")
            choices = list(engine.state.pending_choices)
            chosen = engine.process("选择 1")
            self.assertIn(choices[0], chosen)
            self.assertIn(choices[0], player.destiny_traits)
            self.assertEqual(engine.state.phase, "playing")

    def test_failed_major_breakthrough_applies_cooldown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.stage_index = 3
            player.cultivation = player.cultivation_required
            player.dao_heart = 1
            player.fortune = 1
            player.karma = 100
            player.resources.update({"天材地宝": 1, "五行灵珠": 1, "道韵": 1})
            for seed in range(1, 100):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                result = ProgressionEngine.major_breakthrough(probe, "天道")
                if not result.success:
                    engine.state.rng_seed = seed
                    break
            output = engine.process("突破 天道")
            self.assertIn("突破失败", output)
            self.assertGreater(player.breakthrough_cooldown_months, 0)
            blocked = engine.process("突破")
            self.assertIn("还需休养", blocked)
            remaining = player.breakthrough_cooldown_months
            for _ in range(remaining):
                engine.state.advance_month()
            self.assertEqual(player.breakthrough_cooldown_months, 0)
            self.assertIn("大境界突破路线", engine.process("突破"))

    def test_exploration_is_reproducible_and_advances_time(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = self.make_engine(Path(left_dir))
            right = self.make_engine(Path(right_dir))
            for engine in (left, right):
                engine.process("开始游戏")
                engine.process("确认默认创角")
                engine.state.rng_seed = 77
            left_result = left.process("探索 青岳山麓")
            right_result = right.process("探索 青岳山麓")
            self.assertEqual(left_result, right_result)
            self.assertEqual(left.state.turn, 2)
            self.assertEqual(left.state.player.resources, right.state.player.resources)
            self.assertIn("探索", left_result)

    def test_market_buy_and_sell_updates_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.spirit_stones = 1000
            bought = engine.process("买 筑基丹")
            self.assertIn("坊市成交", bought)
            self.assertEqual(engine.state.player.spirit_stones, 500)
            self.assertEqual(engine.state.player.resources["筑基丹"], 1)
            sold = engine.process("卖 筑基丹")
            self.assertIn("+300", sold)
            self.assertNotIn("筑基丹", engine.state.player.resources)
            self.assertEqual(engine.state.player.spirit_stones, 800)

    def test_market_rejects_unaffordable_purchase_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before = engine.state.player.spirit_stones
            result = engine.process("买 筑基丹")
            self.assertIn("灵石不足", result)
            self.assertEqual(engine.state.player.spirit_stones, before)
            self.assertNotIn("筑基丹", engine.state.player.resources)

    def test_sect_join_and_task_rewards_are_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.aptitude = 20
            engine.state.player.comprehension = 20
            for seed in range(1, 100):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                success, _, _ = EconomyEngine.join_sect(probe, "青云宗")
                if success:
                    engine.state.rng_seed = seed
                    break
            joined = engine.process("拜入 青云宗")
            self.assertIn("外门弟子", joined)
            self.assertEqual(engine.state.player.sect, "青云宗")
            engine.state.player.fortune = 20
            task = engine.process("宗门任务 采药")
            self.assertIn("任务完成", task)
            self.assertGreater(engine.state.player.sect_contribution, 0)
            self.assertGreaterEqual(engine.state.player.resources.get("灵药", 0), 2)

    def test_v04_save_payload_gets_economy_defaults(self) -> None:
        payload = {
            "version": "0.4.0",
            "phase": "playing",
            "player": {"name": "旧档散修", "sect": "散修"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.sect_rank, "无")
        self.assertEqual(state.player.sect_contribution, 0)
        self.assertEqual(state.version, "0.4.0")

    def test_enemy_intel_warns_about_higher_realm(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            panel = engine.process("挑战 筑基客卿")
            self.assertIn("胜算极低", panel)
            self.assertEqual(engine.state.phase, "combat_ready")
            left = engine.process("离开")
            self.assertIn("没有贸然出手", left)
            self.assertEqual(engine.state.phase, "playing")

    def test_realm_suppression_matches_document_rules(self) -> None:
        self.assertEqual(CombatEngine.realm_multiplier(0, 3, 1, 0), 0.4)
        self.assertEqual(CombatEngine.realm_multiplier(0, 3, 2, 0), 0.05)
        self.assertEqual(CombatEngine.realm_multiplier(2, 0, 0, 3), 3.5)

    def test_combat_round_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as left_dir, tempfile.TemporaryDirectory() as right_dir:
            left = self.make_engine(Path(left_dir))
            right = self.make_engine(Path(right_dir))
            for engine in (left, right):
                engine.process("开始游戏")
                engine.process("确认默认创角")
                engine.state.rng_seed = 612
                engine.process("挑战 山野劫修")
                engine.process("开战")
            left_result = left.process("攻击")
            right_result = right.process("攻击")
            self.assertEqual(left_result, right_result)
            self.assertEqual(left.state.player.health, right.state.player.health)
            self.assertEqual(left.state.combat["enemy_health"], right.state.combat["enemy_health"])

    def test_defense_halves_incoming_damage(self) -> None:
        guarded = GameState(phase="playing", rng_seed=88)
        exposed = GameState(phase="playing", rng_seed=88)
        for state in (guarded, exposed):
            CombatEngine.prepare(state, "山野劫修")
            CombatEngine.start(state)
        CombatEngine.act(guarded, "防御")
        CombatEngine.act(exposed, "冷静观察")
        guarded_loss = guarded.player.health_max - guarded.player.health
        exposed_loss = exposed.player.health_max - exposed.player.health
        self.assertLessEqual(guarded_loss, (exposed_loss + 1) // 2)

    def test_victory_waits_for_loot_choice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.speed = 30
            engine.state.player.fortune = 30
            engine.state.rng_seed = 5
            engine.process("挑战 噬灵獾")
            engine.process("开战")
            engine.state.combat["enemy_health"] = 1
            won = engine.process("攻击")
            self.assertIn("待取战利品", won)
            self.assertEqual(engine.state.phase, "combat_loot")
            self.assertNotIn("妖兽材料", engine.state.player.resources)
            self.assertEqual(engine.state.player.karma, 5)
            looted = engine.process("拾取全部")
            self.assertIn("妖兽材料 +1", looted)
            self.assertEqual(engine.state.player.resources["妖兽材料"], 1)
            self.assertEqual(engine.state.phase, "playing")

    def test_exploration_can_open_combat_encounter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            for seed in range(1, 500):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if EconomyEngine.explore(probe, "青岳山麓").encounter:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("探索 青岳山麓")
            self.assertIn("敌情面板", result)
            self.assertEqual(engine.state.phase, "combat_ready")
            self.assertEqual(engine.state.combat["source"], "exploration")
            refused = engine.process("离开")
            self.assertIn("无法直接离开", refused)

    def test_v05_save_payload_gets_combat_defaults(self) -> None:
        payload = {
            "version": "0.5.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.combat, {})
        self.assertEqual(state.pending_loot, {})

    def test_learning_technique_consumes_manual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.comprehension = 20
            player.resources["青木长生诀残卷"] = 1
            for seed in range(1, 100):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if ArtsEngine.learn(probe, "青木长生诀").success:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("参悟 青木长生诀")
            self.assertIn("参悟成功", result)
            self.assertIn("青木长生诀", player.known_techniques)
            self.assertNotIn("青木长生诀残卷", player.resources)

    def test_failed_learning_destroys_manual(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.comprehension = 1
            player.resources["五行道藏残卷"] = 1
            for seed in range(1, 300):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if not ArtsEngine.learn(probe, "五行道藏").success:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("参悟 五行道藏")
            self.assertIn("残卷损毁", result)
            self.assertNotIn("五行道藏", player.known_techniques)
            self.assertNotIn("五行道藏残卷", player.resources)

    def test_main_technique_grade_changes_cultivation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before = ProgressionEngine.cultivation_gain(engine.state).total
            engine.state.player.known_techniques.append("太虚剑典")
            equipped = engine.process("装备功法 太虚剑典")
            after = ProgressionEngine.cultivation_gain(engine.state).total
            self.assertIn("地阶", equipped)
            self.assertEqual(engine.state.player.primary_technique_grade, "地阶")
            self.assertGreater(after, before)

    def test_equipped_spell_uses_element_and_spirit_cost(self) -> None:
        state = GameState(phase="playing", rng_seed=19)
        state.player.speed = 30
        CombatEngine.prepare(state, "筑基客卿")
        CombatEngine.start(state)
        state.combat["player_observed"] = True
        before = state.player.spirit
        result = CombatEngine.act(state, "施法 流火术")
        self.assertIn("五行×1.3", result.player_text)
        self.assertEqual(state.player.spirit, before - 20)

    def test_armor_reduces_incoming_damage(self) -> None:
        armored = GameState(phase="playing", rng_seed=101)
        unarmored = GameState(phase="playing", rng_seed=101)
        armored.player.resources["玄龟甲"] = 1
        ArtsEngine.equip_artifact(armored.player, "玄龟甲")
        for state in (armored, unarmored):
            CombatEngine.prepare(state, "山野劫修")
            CombatEngine.start(state)
            CombatEngine.act(state, "冷静观察")
        self.assertGreater(armored.player.health, unarmored.player.health)

    def test_selling_last_artifact_unequips_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.resources["青锋剑"] = 1
            engine.process("装备法宝 青锋剑")
            self.assertEqual(engine.state.player.equipped_weapon, "青锋剑")
            engine.process("卖 青锋剑")
            self.assertEqual(engine.state.player.equipped_weapon, "")

    def test_v06_save_payload_gets_arts_defaults(self) -> None:
        payload = {
            "version": "0.6.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.known_techniques, ["聚气诀"])
        self.assertEqual(state.player.known_spells, ["流火术"])
        self.assertEqual(state.player.equipped_weapon, "")

    def test_successful_alchemy_consumes_materials_and_yields_pills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.spirit_sense = 20
            player.resources["灵药"] = 2
            for seed in range(1, 100):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if CraftingEngine.craft(probe, "炼丹", "聚气丹").success:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("炼丹 聚气丹")
            self.assertIn("成功获得聚气丹×2", result)
            self.assertNotIn("灵药", player.resources)
            self.assertEqual(player.resources["聚气丹"], 2)

    def test_failed_crafting_still_consumes_materials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.spirit_sense = 1
            player.resources.update({"灵药": 8, "妖兽材料": 2})
            for seed in range(1, 300):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if not CraftingEngine.craft(probe, "炼丹", "筑基丹").success:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("炼丹 筑基丹")
            self.assertIn("材料尽毁", result)
            self.assertNotIn("灵药", player.resources)
            self.assertNotIn("妖兽材料", player.resources)
            self.assertNotIn("筑基丹", player.resources)

    def test_three_successes_raise_crafting_rank(self) -> None:
        state = GameState(phase="playing", rng_seed=9)
        state.player.spirit_sense = 20
        state.player.craft_successes["炼丹"] = 2
        state.player.resources["灵药"] = 2
        result = CraftingEngine.craft(state, "炼丹", "聚气丹")
        self.assertTrue(result.success)
        self.assertTrue(result.leveled_up)
        self.assertEqual(state.player.craft_skills["炼丹"], 1)
        self.assertEqual(CraftingEngine.skill_rank(state, "炼丹"), "熟练")

    def test_study_upgrade_improves_retreat_gain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before = ProgressionEngine.cultivation_gain(engine.state, retreat=True).total
            engine.state.player.spirit_stones = 1000
            engine.state.player.resources["灵铁"] = 2
            result = engine.process("升级洞府 静室")
            after = ProgressionEngine.cultivation_gain(engine.state, retreat=True).total
            self.assertIn("静室已升至 1 级", result)
            self.assertGreater(after, before)
            self.assertEqual(engine.state.player.spirit_stones, 800)

    def test_alchemy_room_adds_crafting_chance(self) -> None:
        basic = GameState(phase="playing", rng_seed=33)
        improved = GameState.from_dict(basic.to_dict())
        for state in (basic, improved):
            state.player.resources["灵药"] = 3
        improved.cave_facilities["丹房"] = 2
        basic_result = CraftingEngine.craft(basic, "炼丹", "疗伤丹")
        improved_result = CraftingEngine.craft(improved, "炼丹", "疗伤丹")
        self.assertEqual(improved_result.chance, basic_result.chance + 10)

    def test_spirit_field_requires_growth_before_harvest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.cave_facilities["灵田"] = 1
            engine.state.player.resources["灵药"] = 1
            planted = engine.process("种植 灵药")
            self.assertIn("还需 2 个月", planted)
            early = engine.process("收获 灵药")
            self.assertIn("尚未成熟", early)
            engine.state.advance_month(2)
            harvested = engine.process("收获 灵药")
            self.assertIn("灵药 +4", harvested)
            self.assertEqual(engine.state.player.resources["灵药"], 4)

    def test_fireball_talisman_is_consumed_in_combat(self) -> None:
        state = GameState(phase="playing", rng_seed=29)
        state.player.resources["火球符"] = 1
        CombatEngine.prepare(state, "筑基客卿")
        CombatEngine.start(state)
        state.combat["player_observed"] = True
        result = CombatEngine.act(state, "用符 火球符")
        self.assertIn("五行×1.3", result.player_text)
        self.assertNotIn("火球符", state.player.resources)

    def test_swiftness_talisman_works_from_enemy_intel_panel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.speed = 30
            engine.state.player.resources["神行符"] = 1
            engine.state.rng_seed = 2
            engine.process("挑战 山野劫修")
            result = engine.process("遁走 神行符")
            self.assertIn("遁走成功", result)
            self.assertNotIn("神行符", engine.state.player.resources)
            self.assertEqual(engine.state.phase, "playing")

    def test_v07_save_payload_gets_crafting_defaults(self) -> None:
        payload = {
            "version": "0.7.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.craft_skills, {})
        self.assertEqual(state.cave_facilities, {})
        self.assertEqual(state.spirit_crops, {})

    def test_preferred_gift_changes_affinity_and_consumes_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.resources["清茶"] = 1
            before_turn = engine.state.turn
            result = engine.process("送礼 顾清玄 清茶")
            self.assertIn("好感 +10", result)
            self.assertEqual(RelationshipEngine.affinity(engine.state, "顾清玄"), 10)
            self.assertNotIn("清茶", engine.state.player.resources)
            self.assertEqual(engine.state.turn, before_turn + 1)

    def test_disliked_gift_can_lower_affinity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.resources["烈酒"] = 1
            result = engine.process("送礼 白凝霜 烈酒")
            self.assertIn("好感 -5", result)
            self.assertEqual(RelationshipEngine.affinity(engine.state, "白凝霜"), -5)

    def test_talking_uses_npc_personality_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            result = engine.process("对话 云栖")
            self.assertIn("买卖可以谈", result)
            self.assertEqual(RelationshipEngine.affinity(engine.state, "云栖"), 2)

    def test_partner_choice_is_affinity_gated_and_gender_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.gender = "男"
            blocked = engine.process("结为道侣 顾清玄")
            self.assertIn("尚未达到 80", blocked)
            RelationshipEngine.relation(engine.state, "顾清玄")["affinity"] = 80
            accepted = engine.process("结为道侣 顾清玄")
            self.assertIn("结下道侣之契", accepted)
            self.assertIn("顾清玄", engine.state.dao_partners)

    def test_dual_cultivation_requires_partner_and_gives_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            rejected = engine.process("双修 洛浅浅")
            self.assertIn("尚不是你的道侣", rejected)
            RelationshipEngine.relation(engine.state, "洛浅浅")["affinity"] = 80
            engine.process("结为道侣 洛浅浅")
            before = engine.state.player.cultivation
            result = engine.process("双修 洛浅浅")
            self.assertIn("合修一月", result)
            self.assertGreater(engine.state.player.cultivation, before)
            self.assertEqual(RelationshipEngine.affinity(engine.state, "洛浅浅"), 83)

    def test_multiple_romantic_bonds_raise_relationship_tension(self) -> None:
        state = GameState(phase="playing")
        RelationshipEngine.relation(state, "顾清玄")["affinity"] = 70
        RelationshipEngine.relation(state, "云栖")["affinity"] = 65
        tension = RelationshipEngine.refresh_tension(state)
        self.assertEqual(RelationshipEngine.romantic_names(state), ["顾清玄", "云栖"])
        self.assertGreaterEqual(tension, 25)

    def test_heart_trial_requires_entangled_relationships(self) -> None:
        state = GameState(phase="playing")
        with self.assertRaisesRegex(ValueError, "至少需要两段"):
            RelationshipEngine.begin_heart_trial(state)

    def test_heart_trial_choice_resolves_and_persists_event(self) -> None:
        state = GameState(phase="playing", rng_seed=44)
        for name in ("顾清玄", "云栖"):
            RelationshipEngine.relation(state, name)["affinity"] = 80
        names, tension = RelationshipEngine.begin_heart_trial(state)
        self.assertEqual(names, ["顾清玄", "云栖"])
        self.assertGreaterEqual(tension, 25)
        result = RelationshipEngine.resolve_heart_trial(state, "暂避锋芒")
        self.assertEqual(result.choice, "暂避锋芒")
        self.assertEqual(state.phase, "playing")
        self.assertTrue(state.relationship_events)
        self.assertFalse(state.pending_heart_trial)

    def test_single_minded_heart_trial_ends_all_partner_bonds(self) -> None:
        state = GameState(phase="playing")
        state.dao_partners = ["顾清玄", "云栖"]
        for name in state.dao_partners:
            RelationshipEngine.relation(state, name)["affinity"] = 90
        before_dao_heart = state.player.dao_heart
        RelationshipEngine.begin_heart_trial(state)
        result = RelationshipEngine.resolve_heart_trial(state, "一心问道")
        self.assertEqual(result.tension, 0)
        self.assertEqual(state.dao_partners, [])
        self.assertEqual(state.player.dao_heart, before_dao_heart + 2)
        self.assertEqual(state.npc_relations["顾清玄"]["path"], "旧缘")

    def test_engine_heart_trial_advances_exactly_one_month(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            for name in ("顾清玄", "云栖"):
                RelationshipEngine.relation(engine.state, name)["affinity"] = 80
            before = engine.state.turn
            opened = engine.process("情劫")
            self.assertIn("情劫抉择", opened)
            self.assertEqual(engine.state.phase, "heart_trial_choice")
            resolved = engine.process("情劫 暂避锋芒")
            self.assertIn("情劫 · 暂避锋芒", resolved)
            self.assertEqual(engine.state.turn, before + 1)
            self.assertEqual(engine.state.phase, "playing")

    def test_dao_discussion_is_reproducible(self) -> None:
        left = GameState(phase="playing", rng_seed=303)
        right = GameState.from_dict(left.to_dict())
        left_result = RelationshipEngine.discuss_dao(left, "墨尘")
        right_result = RelationshipEngine.discuss_dao(right, "墨尘")
        self.assertEqual(left_result, right_result)
        self.assertEqual(left.player.cultivation, right.player.cultivation)

    def test_v08_save_payload_gets_relationship_defaults(self) -> None:
        payload = {
            "version": "0.8.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.npc_relations, {})
        self.assertEqual(state.dao_partners, [])

    def test_secret_realm_rejects_underleveled_player_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            result = engine.process("进入秘境 心魔幻境")
            self.assertIn("致命危险", result)
            self.assertEqual(engine.state.phase, "playing")

    def test_secret_realm_requires_confirmation_and_can_cancel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before_turn = engine.state.turn
            entrance = engine.process("进入秘境 通灵秘境")
            self.assertIn("确认进入", entrance)
            self.assertEqual(engine.state.phase, "adventure_ready")
            left = engine.process("离开")
            self.assertIn("没有推进时间", left)
            self.assertEqual(engine.state.turn, before_turn)
            self.assertEqual(engine.state.adventure, {})

    def test_secret_realm_resolution_is_reproducible(self) -> None:
        left = GameState(phase="playing", rng_seed=414)
        AdventureEngine.prepare(left, "通灵秘境")
        AdventureEngine.confirm(left)
        right = GameState.from_dict(left.to_dict())
        left_result = AdventureEngine.resolve(left, "谨慎探索")
        right_result = AdventureEngine.resolve(right, "谨慎探索")
        self.assertEqual(left_result, right_result)
        self.assertEqual(left.adventure, right.adventure)
        self.assertEqual(left.player.health, right.player.health)

    def test_force_exploration_has_lower_chance_and_higher_reward(self) -> None:
        base = GameState(phase="playing")
        base.player.fortune = 30
        AdventureEngine.prepare(base, "通灵秘境")
        AdventureEngine.confirm(base)
        self.assertGreater(
            AdventureEngine.chance(base, "谨慎探索"),
            AdventureEngine.chance(base, "强行探索"),
        )
        for seed in range(1, 500):
            cautious = GameState.from_dict(base.to_dict())
            forceful = GameState.from_dict(base.to_dict())
            cautious.rng_seed = forceful.rng_seed = seed
            cautious_result = AdventureEngine.resolve(cautious, "谨慎探索")
            forceful_result = AdventureEngine.resolve(forceful, "强行探索")
            if cautious_result.success and forceful_result.success:
                break
        else:
            self.fail("未找到两种策略均成功的确定性种子")
        self.assertGreater(
            forceful_result.rewards["灵药"],
            cautious_result.rewards["灵药"],
        )
        self.assertGreater(forceful_result.spirit_stones, cautious_result.spirit_stones)

    def test_leaving_secret_realm_secures_pending_rewards(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.fortune = 30
            engine.process("进入秘境 通灵秘境")
            engine.process("确认进入")
            for seed in range(1, 300):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if AdventureEngine.resolve(probe, "谨慎探索").success:
                    engine.state.rng_seed = seed
                    break
            result = engine.process("谨慎探索")
            self.assertIn("暂存", result)
            before_stones = engine.state.player.spirit_stones
            left = engine.process("退出秘境")
            self.assertIn("带回", left)
            self.assertGreater(engine.state.player.spirit_stones, before_stones)
            self.assertGreater(engine.state.player.resources.get("灵药", 0), 0)
            self.assertEqual(engine.state.phase, "playing")

    def test_secret_realm_failure_can_be_fatal(self) -> None:
        base = GameState(phase="playing")
        base.player.health = 10
        base.player.fortune = 1
        AdventureEngine.prepare(base, "通灵秘境")
        AdventureEngine.confirm(base)
        for seed in range(1, 300):
            state = GameState.from_dict(base.to_dict())
            state.rng_seed = seed
            result = AdventureEngine.resolve(state, "强行探索")
            if not result.success:
                break
        else:
            self.fail("未找到确定性失败种子")
        self.assertTrue(result.fatal)
        self.assertEqual(state.player.health, 0)
        self.assertEqual(state.phase, "ended")

    def test_three_secret_realm_stages_grant_final_inheritance(self) -> None:
        base = GameState(phase="playing")
        base.player.fortune = 100
        for seed in range(1, 500):
            state = GameState.from_dict(base.to_dict())
            state.rng_seed = seed
            AdventureEngine.prepare(state, "通灵秘境")
            AdventureEngine.confirm(state)
            results = []
            for _ in range(3):
                result = AdventureEngine.resolve(state, "谨慎探索")
                results.append(result)
                if not result.success:
                    break
            if len(results) == 3 and all(item.success for item in results):
                break
        else:
            self.fail("未找到三阶段全部成功的确定性种子")
        self.assertTrue(results[-1].completed)
        self.assertEqual(state.phase, "playing")
        self.assertEqual(state.adventure, {})
        self.assertEqual(state.player.resources["通灵秘境传承"], 1)
        self.assertGreater(state.player.spirit_stones, 100)

    def test_random_encounter_uses_twenty_percent_threshold(self) -> None:
        triggered = None
        ordinary = None
        for seed in range(1, 500):
            state = GameState(phase="playing", rng_seed=seed)
            result = AdventureEngine.random_encounter(state, "云游")
            if result.triggered and triggered is None:
                triggered = result
            if not result.triggered and ordinary is None:
                ordinary = result
            if triggered and ordinary:
                break
        self.assertIsNotNone(triggered)
        self.assertIsNotNone(ordinary)
        self.assertLessEqual(triggered.roll, 20)
        self.assertGreater(ordinary.roll, 20)
        left = GameState(phase="playing", rng_seed=77)
        right = GameState.from_dict(left.to_dict())
        self.assertEqual(
            AdventureEngine.random_encounter(left, "云游"),
            AdventureEngine.random_encounter(right, "云游"),
        )

    def test_v09_save_payload_gets_adventure_default(self) -> None:
        payload = {
            "version": "0.9.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.adventure, {})

    def test_npc_ecology_tick_is_reproducible(self) -> None:
        left = GameState(phase="playing", turn=12, rng_seed=515)
        right = GameState.from_dict(left.to_dict())
        left_event = NpcEcologyEngine.tick(left)
        right_event = NpcEcologyEngine.tick(right)
        self.assertEqual(left_event, right_event)
        self.assertEqual(left.npc_world, right.npc_world)
        self.assertEqual(left.npc_event_log, right.npc_event_log)

    def test_regular_month_advances_npc_world(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            result = engine.process("在洞府门前观云")
            self.assertTrue(engine.state.last_npc_event)
            self.assertTrue(engine.state.npc_event_log)
            self.assertIn("人物动态：", result)

    def test_npc_can_autonomously_send_invitation(self) -> None:
        found = None
        for seed in range(1, 1000):
            state = GameState(phase="playing", turn=20, rng_seed=seed)
            for name in ("顾清玄", "云栖", "谢无咎", "白凝霜", "墨尘", "洛浅浅"):
                RelationshipEngine.relation(state, name)["affinity"] = 20
            event = NpcEcologyEngine.tick(state)
            if event.invitation:
                found = (state, event)
                break
        self.assertIsNotNone(found)
        state, event = found
        self.assertIn(event.npc, state.npc_invitations)
        self.assertIn("主动传信", event.description)

    def test_accepting_invitation_grants_reward_and_affinity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            RelationshipEngine.relation(engine.state, "顾清玄")["affinity"] = 20
            engine.state.npc_invitations["顾清玄"] = {
                "kind": "委托",
                "expires_turn": engine.state.turn + 6,
            }
            before_turn = engine.state.turn
            before_stones = engine.state.player.spirit_stones
            result = engine.process("回应 顾清玄 接受")
            self.assertIn("灵石 +40", result)
            self.assertEqual(RelationshipEngine.affinity(engine.state, "顾清玄"), 25)
            self.assertEqual(engine.state.player.spirit_stones, before_stones + 40)
            self.assertEqual(engine.state.turn, before_turn + 1)
            self.assertNotIn("顾清玄", engine.state.npc_invitations)

    def test_pending_invitation_becomes_clickable_decision_pair(self) -> None:
        state = GameState(phase="playing")
        state.npc_invitations["顾清玄"] = {"kind": "论道", "expires_turn": 8}
        decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(state)
        actions = [choice["action"] for choice in decision["choices"]]
        self.assertEqual(actions, ["回应 顾清玄 接受", "回应 顾清玄 婉拒"])
        self.assertFalse(decision["exclusive"])

    def test_relation_paths_are_gated_and_persisted(self) -> None:
        state = GameState(phase="playing")
        with self.assertRaisesRegex(ValueError, "需要好感 40"):
            NpcEcologyEngine.set_relation_path(state, "顾清玄", "结义")
        RelationshipEngine.relation(state, "顾清玄")["affinity"] = 40
        path, affinity = NpcEcologyEngine.set_relation_path(state, "顾清玄", "师徒")
        self.assertEqual((path, affinity), ("师徒", 40))
        self.assertEqual(RelationshipEngine.relation(state, "顾清玄")["path"], "师徒")
        NpcEcologyEngine.set_relation_path(state, "顾清玄", "宿敌")
        self.assertLessEqual(RelationshipEngine.affinity(state, "顾清玄"), -40)

    def test_npc_travel_changes_persist_in_world_record(self) -> None:
        found = None
        for seed in range(1, 1000):
            state = GameState(phase="playing", turn=33, rng_seed=seed)
            event = NpcEcologyEngine.tick(state)
            if event.action == "外出游历":
                found = (state, event)
                break
        self.assertIsNotNone(found)
        state, event = found
        location = state.npc_world[event.npc]["location"]
        restored = GameState.from_dict(state.to_dict())
        self.assertEqual(restored.npc_world[event.npc]["location"], location)

    def test_v10_save_payload_gets_npc_ecology_defaults(self) -> None:
        payload = {
            "version": "0.10.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.npc_world, {})
        self.assertEqual(state.npc_invitations, {})
        self.assertEqual(state.npc_event_log, [])
        self.assertEqual(state.last_npc_event, "")

    def test_world_timeline_triggers_calendar_events_once(self) -> None:
        state = GameState(phase="playing", calendar_year=390, month=1)
        events = WorldTimelineEngine.tick(state)
        self.assertTrue(any("升仙大会" in event for event in events))
        self.assertTrue(any("宗门大比" in event for event in events))
        before = list(state.world_events)
        self.assertEqual(WorldTimelineEngine.tick(state), [])
        self.assertEqual(state.world_events, before)

    def test_crossing_year_updates_world_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.calendar_year = 389
            engine.state.month = 12
            engine.process("静候新岁")
            self.assertEqual((engine.state.calendar_year, engine.state.month), (390, 1))
            self.assertTrue(any("升仙大会" in event for event in engine.state.world_events))
            self.assertTrue(any("宗门大比" in event for event in engine.state.world_events))

    def test_sect_promotion_checks_contribution_and_realm(self) -> None:
        state = GameState(phase="playing")
        state.player.sect = "青云宗"
        state.player.sect_rank = "外门弟子"
        with self.assertRaisesRegex(ValueError, "需要贡献 100"):
            SectProgressionEngine.promote(state)
        state.player.sect_contribution = 100
        state.player.reputation = 100
        for seed in range(1, 300):
            probe = GameState.from_dict(state.to_dict())
            probe.rng_seed = seed
            result = SectProgressionEngine.promote(probe)
            if result.success:
                state = probe
                break
        else:
            self.fail("未找到晋升成功的确定性种子")
        self.assertEqual(state.player.sect_rank, "内门弟子")
        self.assertIn("青云宗内门弟子权限", state.sect_privileges)

    def test_engine_sect_promotion_advances_one_month(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.sect = "青云宗"
            engine.state.player.sect_rank = "外门弟子"
            engine.state.player.sect_contribution = 100
            engine.state.player.reputation = 100
            for seed in range(1, 300):
                probe = GameState.from_dict(engine.state.to_dict())
                probe.rng_seed = seed
                if SectProgressionEngine.promote(probe).success:
                    engine.state.rng_seed = seed
                    break
            before = engine.state.turn
            result = engine.process("申请晋升")
            self.assertIn("晋升为内门弟子", result)
            self.assertEqual(engine.state.turn, before + 1)

    def test_sect_tournament_is_decennial_and_single_entry(self) -> None:
        state = GameState(phase="playing", calendar_year=391)
        state.player.sect = "玄剑门"
        state.player.sect_rank = "外门弟子"
        with self.assertRaisesRegex(ValueError, "下一届"):
            SectProgressionEngine.tournament(state)
        state.calendar_year = 390
        state.player.sect_contribution = 500
        state.player.reputation = 100
        for seed in range(1, 300):
            probe = GameState.from_dict(state.to_dict())
            probe.rng_seed = seed
            result = SectProgressionEngine.tournament(probe)
            if result.success:
                state = probe
                break
        else:
            self.fail("未找到大比夺魁的确定性种子")
        self.assertEqual(state.player.resources["太虚剑典残卷"], 1)
        with self.assertRaisesRegex(ValueError, "已经参加过"):
            SectProgressionEngine.tournament(state)

    def test_defection_requires_confirmation_and_has_consequences(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            player = engine.state.player
            player.sect = "丹霞谷"
            player.sect_rank = "内门弟子"
            player.sect_contribution = 180
            warning = engine.process("叛宗")
            self.assertIn("叛宗警告", warning)
            self.assertEqual(engine.state.phase, "sect_defection_ready")
            result = engine.process("确认叛宗")
            self.assertIn("重归散修", result)
            self.assertEqual(player.sect, "散修")
            self.assertEqual(player.sect_contribution, 0)
            self.assertEqual(player.karma, 5)
            self.assertTrue(any("叛离丹霞谷" in tag for tag in player.tags))

    def test_sect_war_participation_changes_momentum_and_rewards(self) -> None:
        state = GameState(phase="playing", rng_seed=731)
        state.player.sect = "青云宗"
        state.player.sect_rank = "内门弟子"
        SectWarEngine.start(state, "血煞盟", "青云宗")
        before_contribution = state.player.sect_contribution
        result = SectWarEngine.participate(state, "固守山门")
        self.assertEqual(result.choice, "固守山门")
        self.assertTrue(state.active_sect_war["player_acted"])
        self.assertGreater(state.player.sect_contribution, before_contribution)

    def test_sect_war_can_destroy_faction_and_displace_player(self) -> None:
        state = GameState(phase="playing")
        state.player.sect = "丹霞谷"
        state.player.sect_rank = "外门弟子"
        state.faction_strengths["丹霞谷"] = 20
        SectWarEngine.start(state, "玄剑门", "丹霞谷")
        state.active_sect_war.update({"months": 5, "momentum": 4})
        conclusion = SectWarEngine.advance(state)
        self.assertIn("覆灭", conclusion)
        self.assertIn("丹霞谷", state.fallen_factions)
        self.assertEqual(state.player.sect, "散修")
        self.assertFalse(state.active_sect_war)

    def test_engine_exposes_clickable_sect_war_choice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.sect = "青云宗"
            engine.state.player.sect_rank = "外门弟子"
            SectWarEngine.start(engine.state, "血煞盟", "青云宗")
            opened = engine.process("护宗战")
            self.assertIn("护宗战", opened)
            self.assertEqual(engine.state.phase, "sect_war_choice")
            decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(engine.state)
            self.assertEqual([choice["action"] for choice in decision["choices"]], ["驰援前线", "固守山门", "闭关不出"])
            resolved = engine.process("固守山门")
            self.assertIn("护宗战 · 固守山门", resolved)
            self.assertEqual(engine.state.phase, "playing")

    def test_annual_world_evolution_is_reproducible(self) -> None:
        left = GameState(phase="playing", calendar_year=420, month=1, rng_seed=882)
        right = GameState.from_dict(left.to_dict())
        self.assertEqual(WorldEvolutionEngine.annual_tick(left), WorldEvolutionEngine.annual_tick(right))
        self.assertEqual(left.faction_strengths, right.faction_strengths)
        self.assertEqual(left.regional_prosperity, right.regional_prosperity)
        self.assertEqual(WorldEvolutionEngine.annual_tick(left), [])

    def test_world_intervention_changes_persistent_world_state(self) -> None:
        state = GameState(phase="playing", world_tension=35)
        state.player.realm_index = 1
        state.player.spirit_stones = 200
        result = WorldEvolutionEngine.intervene(state, "赈济苍生")
        self.assertEqual(result.choice, "赈济苍生")
        self.assertEqual(state.player.spirit_stones, 100)
        self.assertEqual(state.player.merit, 12)
        self.assertEqual(state.world_tension, 25)
        with self.assertRaisesRegex(ValueError, "本年已经"):
            WorldEvolutionEngine.intervene(state, "探查灵脉")

    def test_engine_world_intervention_uses_clickable_choices(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            engine.state.player.realm_index = 1
            engine.state.player.spirit_stones = 200
            opened = engine.process("干预天下")
            self.assertIn("干预天下", opened)
            self.assertEqual(engine.state.phase, "world_intervention_choice")
            decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(engine.state)
            self.assertEqual(len(decision["choices"]), 4)
            before = engine.state.turn
            resolved = engine.process("赈济苍生")
            self.assertIn("干预天下 · 赈济苍生", resolved)
            self.assertEqual(engine.state.turn, before + 1)

    def test_v11_save_payload_gets_world_and_sect_defaults(self) -> None:
        payload = {
            "version": "0.11.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.sect_privileges, [])
        self.assertEqual(state.sect_tournament_results, {})
        self.assertEqual(state.world_events, [])
        self.assertEqual(state.world_event_keys, [])
        self.assertEqual(state.world_tension, 0)

    def test_openai_narrator_builds_responses_payload(self) -> None:
        captured = {}

        def transport(url, headers, payload, timeout):
            captured.update(url=url, headers=headers, payload=payload, timeout=timeout)
            return {"output_text": "山风掠过青岳，你的试探引来一声遥远剑鸣。"}

        narrator = OpenAINarrator(
            api_key="test-key",
            model="test-model",
            instructions="只负责叙事",
            transport=transport,
        )
        state = GameState(phase="playing")
        state.history = [f"经历{i}" for i in range(12)]
        result = narrator.narrate("夜探藏经阁", state)
        self.assertIn("剑鸣", result)
        self.assertEqual(captured["url"], "https://api.openai.com/v1/responses")
        self.assertEqual(captured["payload"]["model"], "test-model")
        self.assertFalse(captured["payload"]["store"])
        self.assertIn("夜探藏经阁", captured["payload"]["input"])
        self.assertNotIn("经历0", captured["payload"]["input"])
        self.assertIn("经历11", captured["payload"]["input"])
        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-key")

    def test_openai_narrator_parses_nested_output_text(self) -> None:
        narrator = OpenAINarrator(
            api_key="test-key",
            model="test-model",
            instructions="只负责叙事",
            transport=lambda *_: {
                "output": [
                    {"type": "message", "content": [{"type": "output_text", "text": "第一句。"}]},
                    {"type": "message", "content": [{"type": "output_text", "text": "第二句。"}]},
                ]
            },
        )
        self.assertEqual(narrator.narrate("观云", GameState(phase="playing")), "第一句。\n第二句。")

    def test_openai_narrator_requires_api_key(self) -> None:
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            OpenAINarrator(api_key="", model="test-model", instructions="叙事")

    def test_cloud_narrator_falls_back_without_losing_turn(self) -> None:
        primary = OpenAINarrator(
            api_key="test-key",
            model="test-model",
            instructions="叙事",
            transport=lambda *_: (_ for _ in ()).throw(NarrationError("模拟断网")),
        )
        narrator = FallbackNarrator(primary, LocalNarrator())
        result = narrator.narrate("登高", GameState(phase="playing"))
        self.assertIn("自动切换本地叙事", result)
        self.assertIn("登高", result)
        self.assertIn("模拟断网", narrator.last_error)

    def test_settings_loads_local_dotenv_without_overriding_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".env").write_text(
                "XIU_NARRATOR=openai\nOPENAI_API_KEY=file-key\nXIU_MODEL=file-model\n",
                encoding="utf-8",
            )
            with mock.patch.dict(os.environ, {"XIU_MODEL": "environment-model"}, clear=True):
                settings = Settings.from_root(root)
            self.assertEqual(settings.narrator, "openai")
            self.assertEqual(settings.openai_api_key, "file-key")
            self.assertEqual(settings.model, "environment-model")

    def test_web_app_serves_local_interface_and_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            app = WebApplication(engine, ROOT / "web")
            status, content_type, body = app.dispatch("GET", "/")
            self.assertEqual(status, 200)
            self.assertIn("text/html", content_type)
            self.assertIn("问道长生", body.decode("utf-8"))
            self.assertIn("eventHero", body.decode("utf-8"))
            self.assertIn("archiveDialog", body.decode("utf-8"))
            status, content_type, body = app.dispatch("GET", "/api/state")
            payload = json.loads(body)
            self.assertEqual(status, 200)
            self.assertIn("application/json", content_type)
            self.assertEqual(payload["state"]["phase"], "new")
            self.assertIn("Narrator", payload["narrator"])
            self.assertEqual(payload["presentation"]["title"], "灵气潮汐将至")
            self.assertTrue(payload["decision"]["exclusive"])
            self.assertEqual(payload["decision"]["choices"][0]["action"], "开始游戏")
            self.assertIn("顾清玄", payload["npc_profiles"])
            self.assertIn("清茶", payload["npc_profiles"]["顾清玄"]["likes"])
            status, content_type, body = app.dispatch("GET", "/showcase.js")
            self.assertEqual(status, 200)
            self.assertIn("javascript", content_type)
            self.assertIn("成果巡览", body.decode("utf-8"))

    def test_web_action_endpoint_drives_same_game_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            app = WebApplication(engine, ROOT / "web")
            request_body = json.dumps({"action": "开始游戏"}, ensure_ascii=False).encode("utf-8")
            status, _, body = app.dispatch("POST", "/api/action", request_body)
            payload = json.loads(body)
            self.assertEqual(status, 200)
            self.assertIn("创角大面板", payload["output"])
            self.assertEqual(payload["state"]["phase"], "character_creation_basic")
            self.assertEqual(payload["presentation"]["tone"], "system")
            self.assertTrue(payload["presentation"]["sections"])
            self.assertEqual(payload["decision"]["choices"][0]["action"], "确认默认创角")
            self.assertTrue((Path(temp_dir) / "autosave.json").is_file())
            self.assertTrue(payload["save_summaries"])
            self.assertEqual(payload["save_summaries"][0]["name"], "autosave")

    def test_event_presenter_builds_state_change_components(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = self.make_engine(Path(temp_dir))
            engine.process("开始游戏")
            engine.process("确认默认创角")
            before = engine.state.to_dict()
            output = engine.process("修炼")
            presentation = present_action("修炼", output, before, engine.state.to_dict())
            labels = {item["label"] for item in presentation["changes"]}
            self.assertEqual(presentation["tone"], "cultivation")
            self.assertIn("修为", labels)
            self.assertIn("时间流逝", labels)
            self.assertTrue(presentation["has_details"])
            self.assertNotIn("【状态卡", "".join(presentation["paragraphs"]))

    def test_event_presenter_detects_resources_and_affinity(self) -> None:
        before = GameState(phase="playing").to_dict()
        after_state = GameState.from_dict(json.loads(json.dumps(before, ensure_ascii=False)))
        after_state.player.resources["聚气丹"] = 2
        after_state.npc_relations["顾清玄"] = {"affinity": 5}
        result = present_action("送礼 顾清玄 聚气丹", "【赠礼成功】顾清玄欣然收下。", before, after_state.to_dict())
        changes = {(item["label"], item["value"]) for item in result["changes"]}
        self.assertIn(("聚气丹", "+2"), changes)
        self.assertIn(("顾清玄好感", "+5"), changes)
        self.assertEqual(result["tone"], "relation")

    def test_welcome_presentation_is_component_ready(self) -> None:
        result = welcome_presentation()
        self.assertEqual(result["seal"], "道")
        self.assertGreaterEqual(len(result["paragraphs"]), 2)
        self.assertFalse(result["has_details"])

    def test_named_save_and_load_present_as_system_events(self) -> None:
        state = GameState(phase="playing").to_dict()
        saved = present_action("存档 筑基之前", "已存档：筑基之前.json（第 3 回合）", state, state)
        loaded = present_action("读档 筑基之前", "读档完成。\n突破冷却 0 月", state, state)
        self.assertEqual(saved["tone"], "system")
        self.assertEqual(loaded["tone"], "system")

    def test_relation_event_promotes_summary_and_uses_people_component(self) -> None:
        before = GameState(phase="playing").to_dict()
        before["npc_relations"] = {
            "顾清玄": {"affinity": 74, "path": "道侣"},
            "云栖": {"affinity": 66, "path": "暧昧"},
        }
        after = json.loads(json.dumps(before, ensure_ascii=False))
        after["npc_relations"]["云栖"]["affinity"] = 60
        output = (
            "【情劫 · 坦诚相告】\n"
            "言语未能解开心结，旧日细节反而化作新刺，几段缘分同时蒙上阴影。\n"
            "判定：1d100=97，成功率 47%\n尘缘波澜：69/100\n\n"
            "【人物与情缘】\n"
            "顾清玄｜男｜青云宗真传·温润剑修｜24岁｜筑基·后期｜好感 74（道侣）｜所在地 青云宗\n"
            "云栖｜女｜天机坊市老板娘·聪慧狡黠｜27岁｜筑基·中期｜好感 60（暧昧）｜所在地 天机坊市\n\n"
            "【尘缘波澜】69/100｜情劫·坦诚相告：言语未能解开心结。"
        )
        view = present_action("情劫 坦诚相告", output, before, after)
        self.assertEqual(view["paragraphs"], ["言语未能解开心结，旧日细节反而化作新刺，几段缘分同时蒙上阴影。"])
        self.assertEqual([block["type"] for block in view["blocks"]], ["facts", "people", "meter"])
        self.assertEqual(view["blocks"][1]["items"][0]["name"], "云栖")
        self.assertEqual(view["blocks"][1]["items"][0]["gender"], "女")
        self.assertEqual(view["blocks"][1]["items"][0]["age"], "27岁")
        self.assertEqual(view["blocks"][1]["items"][0]["identity"], "天机坊市老板娘")
        self.assertEqual(view["blocks"][2]["value"], 69)
        self.assertEqual(view["blocks"][2]["max"], 100)

    def test_world_collections_become_compact_semantic_blocks(self) -> None:
        state = GameState(phase="playing").to_dict()
        output = (
            "【势力盛衰】\n青云宗 72｜血魔宗 41｜天机阁 65\n"
            "【近期大事记】\n东洲灵脉复苏\n南疆宗门交战\n西漠商路重开\n北原雪灾"
        )
        view = present_action("天下", output, state, state)
        self.assertEqual(view["paragraphs"], ["九州局势已经更新，重要变化已归纳如下。"])
        self.assertEqual(view["blocks"][0]["type"], "facts")
        self.assertTrue(view["blocks"][1]["collapsed"])

    def test_exploration_map_becomes_actionable_danger_cards(self) -> None:
        state = GameState(phase="playing").to_dict()
        output = (
            "【东洲探索地图】\n"
            "青岳山麓｜炼气可入｜危险度 12\n"
            "百草谷｜炼气可入｜危险度 18\n"
            "迷雾山谷｜至少第 2 大境界｜危险度 28\n"
            "古战场外围｜至少第 3 大境界｜危险度 38\n"
            "输入：探索 青岳山麓"
        )
        view = present_action("地图", output, state, state)
        self.assertEqual([block["type"] for block in view["blocks"]], ["locations"])
        items = view["blocks"][0]["items"]
        self.assertEqual([item["danger_label"] for item in items], ["低危", "寻常", "高危", "绝境"])
        self.assertEqual([item["accessible"] for item in items], [True, True, False, False])
        self.assertEqual(items[2]["requirement_label"], "筑基境")
        self.assertEqual(items[3]["requirement_label"], "结晶境")
        self.assertIn("筑基境", items[2]["locked_reason"])
        self.assertIn("不是奖励点数", view["blocks"][0]["legend"])
        self.assertEqual(items[-1]["tone"], "danger")
        self.assertIn("致命", items[-1]["help"])

    def test_exploration_map_keeps_more_than_four_locations(self) -> None:
        state = GameState(phase="playing").to_dict()
        lines = [f"试炼地{index}｜炼气可入｜危险度 {10 + index}" for index in range(1, 7)]
        view = present_action("地图", "【东洲探索地图】\n" + "\n".join(lines), state, state)
        self.assertEqual(len(view["blocks"][0]["items"]), 6)
        self.assertTrue(all(item["accessible"] for item in view["blocks"][0]["items"]))

    def test_market_output_becomes_filterable_trade_items(self) -> None:
        state = GameState(phase="playing").to_dict()
        output = "【青岳坊市】\n聚气丹：买 20／卖 12 灵石\n筑基丹：买 500／卖 300 灵石\n灵药：买 12／卖 7 灵石"
        view = present_action("坊市", output, state, state)
        block = view["blocks"][0]
        self.assertEqual(block["type"], "market")
        self.assertEqual([item["category"] for item in block["items"]], ["丹药", "丹药", "材料"])
        self.assertTrue(block["items"][0]["affordable"])
        self.assertFalse(block["items"][1]["affordable"])
        self.assertEqual(block["items"][0]["buy_action"], "买 聚气丹")

    def test_secret_realms_reuse_accessible_location_cards(self) -> None:
        state = GameState(phase="playing").to_dict()
        output = (
            "【九州秘境】\n"
            "通灵秘境｜炼气可入｜危险度 20｜林海灵雾终年不散。\n"
            "上古洞府｜至少2阶大境界｜危险度 35｜残阵仍在运转。"
        )
        view = present_action("秘境", output, state, state)
        block = view["blocks"][0]
        self.assertEqual(block["type"], "locations")
        self.assertEqual(block["items"][0]["action"], "进入秘境 通灵秘境")
        self.assertFalse(block["items"][1]["accessible"])
        self.assertEqual(block["items"][0]["description"], "林海灵雾终年不散。")

    def test_cave_output_exposes_upgrade_cost_and_lock_reason(self) -> None:
        state = GameState(phase="playing").to_dict()
        state["player"]["spirit_stones"] = 1000
        state["player"]["resources"] = {"灵铁": 10, "灵药": 3, "五行灵珠": 1}
        output = "【洞府】灵气：普通\n静室：0 级\n丹房：0 级\n器坊：0 级\n灵田：0 级\n聚灵阵：0 级\n禁制：0 级\n灵田：无作物"
        view = present_action("洞府", output, state, state)
        block = view["blocks"][0]
        self.assertEqual(block["type"], "facilities")
        self.assertEqual(block["items"][0]["cost_stones"], 200)
        self.assertTrue(block["items"][0]["affordable"])
        self.assertEqual(block["items"][0]["action"], "升级洞府 静室")

    def test_recipes_and_sects_become_actionable_components(self) -> None:
        state = GameState(phase="playing").to_dict()
        state["player"]["resources"] = {"灵药": 2}
        recipes = present_action("技艺", "【已知配方】\n炼丹 聚气丹｜灵药×2 → 聚气丹×2\n炼丹 疗伤丹｜灵药×3 → 疗伤丹×1", state, state)
        self.assertEqual(recipes["blocks"][0]["type"], "recipes")
        self.assertTrue(recipes["blocks"][0]["items"][0]["available"])
        self.assertFalse(recipes["blocks"][0]["items"][1]["available"])
        sects = present_action("宗门", "【东洲宗门】\n青云宗｜入门试炼\n丹霞谷｜入门试炼", state, state)
        self.assertEqual(sects["blocks"][0]["type"], "sects")
        self.assertEqual(sects["blocks"][0]["items"][0]["action"], "拜入 青云宗")

    def test_button_backed_choice_copy_is_not_repeated_as_a_block(self) -> None:
        state = GameState(phase="heart_trial_choice").to_dict()
        output = (
            "【情劫浮现】\n牵涉之人：顾清玄、云栖\n几段心意在同一刻交汇，你必须亲自选择面对之法。\n"
            "尘缘波澜：69/100\n【情劫抉择】\n坦诚相告：承担判定风险\n暂避锋芒：降低风波\n"
            "一心问道：斩断情缘"
        )
        view = present_action("情劫", output, state, state)
        self.assertEqual([block["title"] for block in view["blocks"]], ["尘缘波澜"])
        self.assertEqual(view["blocks"][0]["type"], "meter")
        self.assertIn("必须亲自选择", view["paragraphs"][1])

    def test_web_app_rejects_invalid_or_oversized_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = WebApplication(self.make_engine(Path(temp_dir)), ROOT / "web")
            status, _, _ = app.dispatch("POST", "/api/action", b"not-json")
            self.assertEqual(status, 400)
            status, _, body = app.dispatch("POST", "/api/action", json.dumps({"action": ""}).encode())
            self.assertEqual(status, 400)
            self.assertIn("请输入行动", json.loads(body)["error"])
            status, _, _ = app.dispatch("POST", "/api/action", b"x" * 65537)
            self.assertEqual(status, 413)

    def test_web_app_blocks_unknown_static_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            app = WebApplication(self.make_engine(Path(temp_dir)), ROOT / "web")
            for path in ("/../README.md", "/.env", "/missing.js"):
                status, _, _ = app.dispatch("GET", path)
                self.assertEqual(status, 404)

    def test_combat_decision_hides_impossible_leave_button(self) -> None:
        catalog = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json")
        state = GameState(phase="playing")
        CombatEngine.prepare(state, "山野劫修", source="exploration")
        actions = [choice["action"] for choice in catalog.for_state(state)["choices"]]
        self.assertEqual(actions, ["开战", "遁走"])

    def test_destiny_traits_are_named_clickable_choices(self) -> None:
        state = GameState(phase="breakthrough_talent_choice", pending_choices=["剑心通明", "气运如虹", "天眼通"])
        catalog = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json")
        decision = catalog.for_state(state)
        self.assertEqual([choice["label"] for choice in decision["choices"]], state.pending_choices)
        self.assertEqual([choice["action"] for choice in decision["choices"]], ["选择 1", "选择 2", "选择 3"])

    def test_major_breakthrough_choices_explain_chances_and_lock_missing_materials(self) -> None:
        state = GameState(phase="major_breakthrough_choice")
        state.player.stage_index = 3
        state.player.cultivation = state.player.cultivation_required
        state.player.resources["筑基丹"] = 1
        catalog = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json")
        choices = catalog.for_state(state)["choices"]
        human, earth, heaven, cancel = choices
        self.assertFalse(human["disabled"])
        self.assertIn("心魔", human["summary"])
        self.assertIn("雷劫", human["description"])
        self.assertTrue(earth["disabled"])
        self.assertIn("天材地宝", earth["disabled_reason"])
        self.assertTrue(heaven["disabled"])
        self.assertNotIn("disabled", cancel)

    def test_v13_save_payload_remains_compatible_with_web_version(self) -> None:
        payload = {
            "version": "0.13.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.name, "旧档修士")
        self.assertEqual(state.version, "0.13.0")

    def test_v14_save_payload_remains_compatible_with_structured_ui(self) -> None:
        payload = {
            "version": "0.14.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.name, "旧档修士")
        self.assertEqual(state.version, "0.14.0")

    def test_v15_save_payload_remains_compatible_with_archive_ui(self) -> None:
        payload = {
            "version": "0.15.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.player.name, "旧档修士")
        self.assertEqual(state.version, "0.15.0")

    def test_v16_save_payload_gets_heart_trial_defaults(self) -> None:
        payload = {
            "version": "0.16.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.relationship_tension, 0)
        self.assertEqual(state.relationship_events, [])
        self.assertEqual(state.pending_heart_trial, {})

    def test_v17_save_payload_remains_compatible_with_decision_ui(self) -> None:
        payload = {
            "version": "0.17.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        decision = DecisionCatalog.load(ROOT / "data" / "content" / "decision_choices.json").for_state(state)
        self.assertEqual(decision["choices"], [])
        self.assertEqual(state.player.name, "旧档修士")

    def test_v18_save_payload_gets_sect_war_defaults(self) -> None:
        payload = {
            "version": "0.18.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertIn("青云宗", state.faction_strengths)
        self.assertEqual(state.active_sect_war, {})
        self.assertEqual(state.sect_war_history, [])
        self.assertEqual(state.fallen_factions, [])

    def test_v19_save_payload_gets_world_evolution_defaults(self) -> None:
        payload = {
            "version": "0.19.0",
            "phase": "playing",
            "player": {"name": "旧档修士"},
            "rule_sha256": self.rules.sha256,
        }
        state = GameState.from_dict(payload)
        self.assertEqual(state.world_era, "灵潮前夜")
        self.assertIn("东洲", state.regional_prosperity)
        self.assertEqual(state.world_milestones, [])
        self.assertEqual(state.world_interventions, {})

    def test_release_tree_passes_environment_diagnostics(self) -> None:
        items = run_diagnostics(ROOT)
        self.assertTrue(all(item.passed for item in items), [item.detail for item in items])
        passed, report = diagnostics_text(ROOT)
        self.assertTrue(passed)
        self.assertIn("可以启动网页版", report)

    def test_acceptance_guides_and_first_run_dialog_are_packaged(self) -> None:
        launcher = (ROOT / "启动网页版.bat").read_text(encoding="utf-8")
        page = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "web" / "app.js").read_text(encoding="utf-8")
        showcase = (ROOT / "web" / "showcase.js").read_text(encoding="utf-8")
        styles = (ROOT / "web" / "app.css").read_text(encoding="utf-8")
        self.assertIn("--check", launcher)
        self.assertTrue((ROOT / "检查环境.bat").is_file())
        self.assertTrue((ROOT / "首次游玩指南.md").is_file())
        self.assertIn('id="guideDialog"', page)
        self.assertIn("xiuxian-guide-seen", script)
        self.assertIn('id="icon-cultivate"', page)
        self.assertIn("点击后立即执行", page)
        self.assertIn("仅填入输入框 · 点“推演此行”后生效", page)
        self.assertIn('id="icon-calendar"', page)
        self.assertIn('id="turnBadgeText"', page)
        self.assertIn("function actionAvailability", script)
        self.assertIn("修为已圆满，请先尝试突破", script)
        self.assertIn(".has-tooltip::after", styles)
        self.assertIn(".quick-actions button:disabled", styles)
        self.assertIn("repeat(auto-fit, minmax(min(230px, 100%), 1fr))", styles)
        self.assertIn('.location-action:disabled', styles)
        self.assertIn('location.accessible === false', script)
        self.assertIn('location.danger_help', script)
        self.assertIn('id="openShowcase"', page)
        self.assertIn('id="showcasePanel"', page)
        self.assertIn('src="/showcase.js"', page)
        self.assertIn('label: "01 · 初始入世"', showcase)
        self.assertIn('label: "14 · 游玩指引"', showcase)
        self.assertIn("不修改存档", page)
        self.assertIn("ui.renderSnapshot(liveSnapshot, { suppressNotices: true })", showcase)
        self.assertNotIn('/api/action', showcase)
        self.assertIn(".showcase-panel", styles)
        self.assertIn("容量不限 · 格位按物品自动扩展", script)
        self.assertNotIn('id="narratorLabel"', page)
        self.assertNotIn('id="moreActionCount"', page)
        self.assertNotIn("decision-badge", page)
        self.assertIn('classList.toggle("is-empty"', script)
        self.assertIn('.bar.is-empty[data-kind="cultivation"]', styles)
        self.assertIn('id="detailDialog"', page)
        self.assertIn('id="toastRegion"', page)
        self.assertIn("function announceResult", script)
        self.assertIn("function personDetail", script)
        self.assertIn('.decision-choice.is-selected', styles)
        self.assertIn('.semantic-data-region[data-overflow="true"]', styles)
        self.assertIn('.content-indicator', styles)

    def test_windows_launchers_use_cmd_compatible_line_endings(self) -> None:
        for name in ("启动网页版.bat", "启动新版界面.bat", "检查环境.bat"):
            payload = (ROOT / name).read_bytes()
            self.assertIn(b"\r\n", payload)
            self.assertNotIn(b"\n", payload.replace(b"\r\n", b""))

    def test_fifty_year_world_simulation_is_bounded_and_reproducible(self) -> None:
        left = GameState(phase="playing", rng_seed=991)
        right = GameState.from_dict(left.to_dict())
        for _ in range(600):
            left.advance_month()
            right.advance_month()
            WorldTimelineEngine.tick(left)
            WorldTimelineEngine.tick(right)

        self.assertEqual(left.faction_strengths, right.faction_strengths)
        self.assertEqual(left.regional_prosperity, right.regional_prosperity)
        self.assertEqual(left.world_events, right.world_events)
        self.assertTrue(all(0 <= strength <= 100 for strength in left.faction_strengths.values()))
        self.assertTrue(all(0 <= prosperity <= 100 for prosperity in left.regional_prosperity.values()))
        self.assertLessEqual(len(left.world_events), 100)
        self.assertLessEqual(len(left.world_milestones), 50)
        self.assertLessEqual(len(left.sect_war_history), 30)


if __name__ == "__main__":
    unittest.main()
