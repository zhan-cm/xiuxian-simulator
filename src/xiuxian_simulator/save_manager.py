from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

from .state import GameState


SAFE_NAME = re.compile(r"[^0-9A-Za-z_\-\u4e00-\u9fff]+")


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
