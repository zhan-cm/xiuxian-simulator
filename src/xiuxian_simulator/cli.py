from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import Settings
from .engine import GameEngine
from .narrator import FallbackNarrator, LocalNarrator, OpenAINarrator
from .rules import RuleBook
from .save_manager import SaveManager
from .webapp import run_web_server


def find_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_engine(root: Path | None = None) -> GameEngine:
    settings = Settings.from_root(root or find_project_root())
    rules = RuleBook.load(settings.rule_docx)
    saves = SaveManager(settings.save_dir)
    local = LocalNarrator()
    if settings.narrator == "local":
        narrator = local
    elif settings.narrator == "openai":
        instructions = settings.overlay_prompt.read_text(encoding="utf-8")
        narrator = FallbackNarrator(
            OpenAINarrator(
                api_key=settings.openai_api_key,
                model=settings.model,
                instructions=instructions,
                base_url=settings.api_base,
                timeout=settings.api_timeout,
            ),
            local,
        )
    else:
        raise ValueError(f"未知叙事器：{settings.narrator!r}；可选 local 或 openai。")
    return GameEngine(rules, saves, narrator, settings.autosave_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="《问道长生》本地修仙模拟器")
    parser.add_argument("--web", action="store_true", help="启动本地网页界面")
    parser.add_argument("--port", type=int, default=8765, help="网页界面端口，默认 8765")
    parser.add_argument("--no-open-browser", action="store_true", help="启动网页服务但不自动打开浏览器")
    args = parser.parse_args()
    try:
        engine = build_engine()
    except Exception as exc:
        print(f"启动失败：{exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if args.web:
        if not 1 <= args.port <= 65535:
            parser.error("端口必须在 1～65535 之间")
        run_web_server(
            engine,
            find_project_root(),
            port=args.port,
            open_browser=not args.no_open_browser,
        )
        return

    print("问道长生 V0.14 本地基线版")
    print(engine.rules.summary)
    print(f"当前叙事器：{engine.narrator.name}")
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
