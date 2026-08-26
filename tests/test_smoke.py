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
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager


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


if __name__ == "__main__":
    unittest.main()

