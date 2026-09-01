from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .state import GameState


SAFE_NAME = re.compile(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+")
PORTABLE_SAVE_FORMAT = "wendao-changsheng-save"
PORTABLE_SAVE_SCHEMA = 1
MAX_PORTABLE_SAVE_BYTES = 2 * 1024 * 1024


class SaveImportError(ValueError):
    pass


class SaveManager:
    def __init__(self, save_dir: Path) -> None:
        self.save_dir = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize_name(name: str) -> str:
        cleaned = SAFE_NAME.sub("_", name.strip()).strip("_")
        return cleaned[:48] or "autosave"

    def path_for(self, name: str) -> Path:
        return self.save_dir / f"{self.normalize_name(name)}.json"

    def save(self, name: str, state: GameState) -> Path:
        destination = self.path_for(name)
        payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)
        handle, temp_name = tempfile.mkstemp(prefix=".save-", suffix=".tmp", dir=self.save_dir)
        try:
            with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(payload)
                stream.write("\n")
            if destination.is_file():
                shutil.copy2(destination, destination.with_suffix(".json.bak"))
            os.replace(temp_name, destination)
        except Exception:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            raise
        return destination

    def load(self, name: str) -> GameState:
        path = self.path_for(name)
        if not path.is_file():
            raise FileNotFoundError(f"找不到存档：{path.name}")
        with path.open("r", encoding="utf-8") as stream:
            return GameState.from_dict(json.load(stream))

    def list_names(self) -> list[str]:
        return sorted(path.stem for path in self.save_dir.glob("*.json"))

    def list_summaries(self) -> list[dict[str, object]]:
        summaries: list[dict[str, object]] = []
        for path in sorted(self.save_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            player = payload.get("player", {}) if isinstance(payload, dict) else {}
            summaries.append(
                {
                    "name": path.stem,
                    "player_name": str(player.get("name", "无名修士")),
                    "dao_name": str(player.get("dao_name", "")),
                    "realm": str(player.get("realm", "凡人")),
                    "turn": int(payload.get("turn", 0)),
                    "calendar_year": int(payload.get("calendar_year", 387)),
                    "month": int(payload.get("month", 1)),
                    "modified_at": int(path.stat().st_mtime),
                }
            )
        return summaries

    @staticmethod
    def _canonical_state(payload: dict[str, Any]) -> bytes:
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def _state_checksum(cls, payload: dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical_state(payload)).hexdigest()

    def export_payload(self, name: str) -> dict[str, Any]:
        path = self.path_for(name)
        state = self.load(name)
        state_payload = state.to_dict()
        exported_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(timespec="seconds")
        return {
            "format": PORTABLE_SAVE_FORMAT,
            "schema_version": PORTABLE_SAVE_SCHEMA,
            "name": path.stem,
            "game_version": state.version,
            "rule_sha256": state.rule_sha256,
            "exported_at": exported_at,
            "checksum": self._state_checksum(state_payload),
            "state": state_payload,
        }

    @staticmethod
    def _validate_loaded_state(state: GameState) -> None:
        if not isinstance(state.version, str) or not state.version.strip():
            raise SaveImportError("存档缺少有效游戏版本。")
        if not isinstance(state.phase, str) or not state.phase.strip():
            raise SaveImportError("存档阶段无效。")
        if not isinstance(state.turn, int) or isinstance(state.turn, bool) or state.turn < 0:
            raise SaveImportError("存档回合数无效。")
        if not isinstance(state.calendar_year, int) or isinstance(state.calendar_year, bool) or state.calendar_year < 1:
            raise SaveImportError("存档历法年份无效。")
        if not isinstance(state.month, int) or isinstance(state.month, bool) or not 1 <= state.month <= 12:
            raise SaveImportError("存档月份必须在 1～12 之间。")
        if not isinstance(state.player.name, str) or len(state.player.name) > 80:
            raise SaveImportError("存档角色名称无效。")
        if not isinstance(state.history, list) or any(not isinstance(item, str) for item in state.history):
            raise SaveImportError("存档经历记录无效。")

    def _available_import_name(self, requested: str) -> str:
        normalized = self.normalize_name(requested)
        if not self.path_for(normalized).exists():
            return normalized
        for index in range(1, 1000):
            suffix = f"_导入{index}"
            candidate = self.normalize_name(normalized[: 48 - len(suffix)] + suffix)
            if not self.path_for(candidate).exists():
                return candidate
        raise SaveImportError("同名导入卷宗过多，请先整理现有存档。")

    def import_payload(
        self,
        payload: dict[str, Any],
        *,
        preferred_name: str = "",
        overwrite: bool = False,
        expected_rule_sha256: str = "",
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise SaveImportError("导入文件必须是 JSON 对象。")

        source_format = "legacy"
        source_name = ""
        if "format" in payload:
            if payload.get("format") != PORTABLE_SAVE_FORMAT:
                raise SaveImportError("这不是《问道长生》便携卷宗。")
            if payload.get("schema_version") != PORTABLE_SAVE_SCHEMA:
                raise SaveImportError("便携卷宗格式版本暂不受支持。")
            state_payload = payload.get("state")
            if not isinstance(state_payload, dict):
                raise SaveImportError("便携卷宗缺少结构化状态。")
            expected_checksum = payload.get("checksum")
            if not isinstance(expected_checksum, str) or not re.fullmatch(r"[0-9A-Fa-f]{64}", expected_checksum):
                raise SaveImportError("便携卷宗缺少有效内容校验值。")
            actual_checksum = self._state_checksum(state_payload)
            if actual_checksum != expected_checksum.lower():
                raise SaveImportError("便携卷宗内容校验失败，文件可能损坏或被修改。")
            source_format = "portable"
            raw_source_name = payload.get("name", "")
            source_name = raw_source_name.strip() if isinstance(raw_source_name, str) else ""
        else:
            state_payload = payload

        encoded = self._canonical_state(state_payload)
        if len(encoded) > MAX_PORTABLE_SAVE_BYTES:
            raise SaveImportError("存档超过 2 MB 安全上限，已拒绝导入。")
        try:
            state = GameState.from_dict(state_payload)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise SaveImportError(f"存档结构无法读取：{exc}") from exc
        self._validate_loaded_state(state)
        if source_format == "portable":
            metadata_version = str(payload.get("game_version", "")).strip()
            metadata_rule = str(payload.get("rule_sha256", "")).strip()
            if metadata_version and metadata_version != state.version:
                raise SaveImportError("便携卷宗的游戏版本元数据与实际内容不一致。")
            if metadata_rule and state.rule_sha256 and metadata_rule != state.rule_sha256:
                raise SaveImportError("便携卷宗的规则指纹元数据与实际内容不一致。")
        if expected_rule_sha256 and state.rule_sha256 and state.rule_sha256 != expected_rule_sha256:
            raise SaveImportError("存档所用规则与当前规则文档不一致，已拒绝导入。")

        requested_name = preferred_name.strip() or source_name or "导入卷宗"
        destination_name = self.normalize_name(requested_name) if overwrite else self._available_import_name(requested_name)
        destination = self.save(destination_name, state)
        return {
            "name": destination.stem,
            "requested_name": self.normalize_name(requested_name),
            "renamed": destination.stem != self.normalize_name(requested_name),
            "source_format": source_format,
            "game_version": state.version,
            "player_name": state.player.name or "无名修士",
            "realm": state.player.realm,
            "turn": state.turn,
        }
