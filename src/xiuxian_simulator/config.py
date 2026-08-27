from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    root_dir: Path
    rule_docx: Path
    save_dir: Path
    overlay_prompt: Path
    narrator: str
    autosave_name: str
    openai_api_key: str
    model: str
    api_base: str
    api_timeout: float

    @staticmethod
    def _load_dotenv(path: Path) -> None:
        if not path.is_file():
            return
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)

    @classmethod
    def from_root(cls, root_dir: Path) -> "Settings":
        root = root_dir.resolve()
        cls._load_dotenv(root / ".env")
        try:
            timeout = float(os.getenv("XIU_API_TIMEOUT", "45"))
        except ValueError as exc:
            raise ValueError("XIU_API_TIMEOUT 必须是数字秒数。") from exc
        return cls(
            root_dir=root,
            rule_docx=root / "docs" / "修仙模拟器 · 问道长生.docx",
            save_dir=root / "data" / "saves",
            overlay_prompt=root / "prompts" / "runtime_overlay.txt",
            narrator=os.getenv("XIU_NARRATOR", "local").strip().lower(),
            autosave_name=os.getenv("XIU_SAVE_NAME", "autosave").strip() or "autosave",
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            model=os.getenv("XIU_MODEL", "gpt-5.4").strip() or "gpt-5.4",
            api_base=os.getenv("XIU_API_BASE", "https://api.openai.com/v1").strip().rstrip("/"),
            api_timeout=max(5.0, timeout),
        )
