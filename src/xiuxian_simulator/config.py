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

    @classmethod
    def from_root(cls, root_dir: Path) -> "Settings":
        root = root_dir.resolve()
        return cls(
            root_dir=root,
            rule_docx=root / "docs" / "修仙模拟器 · 问道长生.docx",
            save_dir=root / "data" / "saves",
            overlay_prompt=root / "prompts" / "runtime_overlay.txt",
            narrator=os.getenv("XIU_NARRATOR", "local").strip().lower(),
            autosave_name=os.getenv("XIU_SAVE_NAME", "autosave").strip() or "autosave",
        )

