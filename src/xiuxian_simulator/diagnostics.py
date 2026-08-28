from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiagnosticItem:
    name: str
    passed: bool
    detail: str


def run_diagnostics(root: Path) -> list[DiagnosticItem]:
    root = root.resolve()
    items: list[DiagnosticItem] = []
    python_ok = sys.version_info >= (3, 11)
    items.append(DiagnosticItem("Python", python_ok, f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))

    rule_path = root / "docs" / "修仙模拟器 · 问道长生.docx"
    items.append(DiagnosticItem("原始规则文档", rule_path.is_file() and rule_path.stat().st_size > 0, str(rule_path)))

    content_path = root / "data" / "content" / "decision_choices.json"
    try:
        payload = json.loads(content_path.read_text(encoding="utf-8"))
        content_ok = payload.get("schema_version") == 1 and isinstance(payload.get("phases"), dict)
        content_detail = f"{len(payload.get('phases', {}))} 个抉择阶段"
    except (OSError, json.JSONDecodeError) as exc:
        content_ok = False
        content_detail = str(exc)
    items.append(DiagnosticItem("结构化内容", content_ok, content_detail))

    web_assets = [root / "web" / name for name in ("index.html", "app.css", "app.js", "showcase.js")]
    items.append(DiagnosticItem("网页资源", all(path.is_file() for path in web_assets), "HTML / CSS / JavaScript"))

    save_dir = root / "data" / "saves"
    try:
        save_dir.mkdir(parents=True, exist_ok=True)
        writable = os.access(save_dir, os.W_OK)
        save_detail = str(save_dir)
    except OSError as exc:
        writable = False
        save_detail = str(exc)
    items.append(DiagnosticItem("本地存档目录", writable, save_detail))
    return items


def diagnostics_text(root: Path) -> tuple[bool, str]:
    items = run_diagnostics(root)
    lines = ["《问道长生》运行环境检查"]
    for item in items:
        lines.append(f"[{'通过' if item.passed else '失败'}] {item.name}：{item.detail}")
    passed = all(item.passed for item in items)
    lines.append("检查完成，可以启动网页版。" if passed else "存在未通过项目，请按 README 修复后重试。")
    return passed, "\n".join(lines)
