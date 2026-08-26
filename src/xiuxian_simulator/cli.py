from __future__ import annotations

import sys
from pathlib import Path

from .config import Settings
from .engine import GameEngine
from .narrator import LocalNarrator
from .rules import RuleBook
from .save_manager import SaveManager


def find_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_engine(root: Path | None = None) -> GameEngine:
    settings = Settings.from_root(root or find_project_root())
    rules = RuleBook.load(settings.rule_docx)
    saves = SaveManager(settings.save_dir)
    if settings.narrator != "local":
        raise ValueError(f"尚未安装叙事器：{settings.narrator!r}；V0.1 请使用 XIU_NARRATOR=local")
    return GameEngine(rules, saves, LocalNarrator(), settings.autosave_name)


def main() -> None:
    try:
        engine = build_engine()
    except Exception as exc:
        print(f"启动失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("问道长生 V0.4 本地基线版")
    print(engine.rules.summary)
    print("输入“开始游戏”进入九州仙途；输入“退出”结束。")

    while True:
        try:
            action = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已离开九州。")
            return
        if action.lower() in {"退出", "quit", "exit", "q"}:
            print("已离开九州。")
            return
        print(engine.process(action))


if __name__ == "__main__":
    main()
