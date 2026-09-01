from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.save_manager import (
    PORTABLE_SAVE_FORMAT,
    SaveImportError,
    SaveManager,
)
from xiuxian_simulator.state import GameState


class SavePortabilityTests(unittest.TestCase):
    @staticmethod
    def _state() -> GameState:
        state = GameState(
            phase="playing",
            turn=48,
            calendar_year=391,
            month=7,
            rule_sha256="a" * 64,
        )
        state.player.name = "林渡"
        state.player.realm = "筑基·中期"
        state.remember("于青岳洞府整理卷宗")
        return state

    def test_portable_export_round_trips_without_changing_state(self) -> None:
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            source = SaveManager(Path(source_dir))
            state = self._state()
            source.save("筑基之前", state)

            payload = source.export_payload("筑基之前")
            self.assertEqual(payload["format"], PORTABLE_SAVE_FORMAT)
            self.assertEqual(payload["name"], "筑基之前")
            self.assertEqual(len(payload["checksum"]), 64)

            target = SaveManager(Path(target_dir))
            result = target.import_payload(payload, expected_rule_sha256="a" * 64)
            restored = target.load(result["name"])
            self.assertEqual(restored.to_dict(), state.to_dict())
            self.assertFalse(result["renamed"])
            self.assertEqual(result["source_format"], "portable")

    def test_tampered_portable_save_is_rejected_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            manager.save("原卷", self._state())
            payload = manager.export_payload("原卷")
            payload["state"]["turn"] = 999

            with self.assertRaisesRegex(SaveImportError, "内容校验失败"):
                manager.import_payload(payload)
            self.assertEqual(manager.list_names(), ["原卷"])

    def test_portable_metadata_must_match_checked_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            manager.save("原卷", self._state())
            payload = manager.export_payload("原卷")
            payload["game_version"] = "9.9.9"

            with self.assertRaisesRegex(SaveImportError, "游戏版本元数据"):
                manager.import_payload(payload)
            self.assertEqual(manager.list_names(), ["原卷"])

    def test_legacy_raw_save_imports_and_conflicts_are_renamed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            state = self._state()
            manager.save("旧档", state)

            first = manager.import_payload(state.to_dict(), preferred_name="旧档")
            second = manager.import_payload(state.to_dict(), preferred_name="旧档")
            self.assertEqual(first["name"], "旧档_导入1")
            self.assertEqual(second["name"], "旧档_导入2")
            self.assertTrue(first["renamed"])
            self.assertEqual(first["source_format"], "legacy")
            self.assertEqual(manager.load("旧档_导入2").player.name, "林渡")

    def test_overwrite_requires_explicit_flag_and_keeps_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            previous = self._state()
            manager.save("同名", previous)
            current = self._state()
            current.turn = 77

            result = manager.import_payload(current.to_dict(), preferred_name="同名", overwrite=True)
            self.assertEqual(result["name"], "同名")
            self.assertEqual(manager.load("同名").turn, 77)
            backup = json.loads((Path(temp_dir) / "同名.json.bak").read_text(encoding="utf-8"))
            self.assertEqual(backup["turn"], previous.turn)

    def test_foreign_rule_and_invalid_calendar_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = SaveManager(Path(temp_dir))
            state = self._state()
            with self.assertRaisesRegex(SaveImportError, "规则文档不一致"):
                manager.import_payload(state.to_dict(), expected_rule_sha256="b" * 64)

            invalid = state.to_dict()
            invalid["month"] = 13
            with self.assertRaisesRegex(SaveImportError, "月份"):
                manager.import_payload(invalid)


if __name__ == "__main__":
    unittest.main()
