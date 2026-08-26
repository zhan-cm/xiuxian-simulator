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


if __name__ == "__main__":
    unittest.main()
