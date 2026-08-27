from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.economy import EconomyEngine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.arts import ArtsEngine
from xiuxian_simulator.narrator import LocalNarrator
from xiuxian_simulator.progression import ProgressionEngine
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager
from xiuxian_simulator.state import GameState


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


if __name__ == "__main__":
    unittest.main()
