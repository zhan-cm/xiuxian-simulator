from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from importlib import metadata, util
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiagnosticItem:
    name: str
    passed: bool
    detail: str


def _runtime_dependencies() -> DiagnosticItem:
    required = ("fastapi", "uvicorn")
    missing = [name for name in required if util.find_spec(name) is None]
    if missing:
        return DiagnosticItem(
            "新版本地接口",
            False,
            f"缺少 {', '.join(missing)}；启动新版界面时会尝试自动安装",
        )
    versions: list[str] = []
    for name in required:
        try:
            versions.append(f"{name} {metadata.version(name)}")
        except metadata.PackageNotFoundError:
            versions.append(name)
    return DiagnosticItem("新版本地接口", True, " · ".join(versions))


def _modern_assets(root: Path) -> DiagnosticItem:
    dist = root / "frontend" / "dist"
    index = dist / "index.html"
    licenses = dist / "third-party-licenses.md"
    if not index.is_file():
        return DiagnosticItem("新版界面资源", False, "缺少 frontend/dist/index.html")
    try:
        html = index.read_text(encoding="utf-8")
    except OSError as exc:
        return DiagnosticItem("新版界面资源", False, f"入口无法读取：{type(exc).__name__}")
    all_references = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', html)
    remote = [name for name in all_references if name.startswith(("http://", "https://", "//"))]
    if remote:
        return DiagnosticItem("新版界面资源", False, f"入口包含远程资源：{remote[0]}")
    references = sorted(
        {
            match.lstrip("/")
            for match in all_references
            if match.startswith("/assets/")
        }
    )
    missing = [name for name in references if not (dist / name).is_file()]
    if not references:
        return DiagnosticItem("新版界面资源", False, "入口没有引用任何本地生产资源")
    if missing:
        return DiagnosticItem("新版界面资源", False, f"缺少 {len(missing)} 个生产资源：{missing[0]}")
    if not licenses.is_file() or licenses.stat().st_size == 0:
        return DiagnosticItem("新版界面资源", False, "缺少第三方许可清单")
    return DiagnosticItem("新版界面资源", True, f"{len(references)} 个生产资源 · 第三方许可已就绪")


def _writable_save_directory(root: Path, save_dir: Path | None = None) -> DiagnosticItem:
    save_dir = save_dir or root / "data" / "saves"
    temporary = save_dir / f".diagnostic-{os.getpid()}.tmp"
    committed = save_dir / f".diagnostic-{os.getpid()}.ready"
    try:
        save_dir.mkdir(parents=True, exist_ok=True)
        temporary.unlink(missing_ok=True)
        committed.unlink(missing_ok=True)
        with temporary.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write("wendao-save-check\n")
            stream.flush()
        os.replace(temporary, committed)
        if committed.read_text(encoding="utf-8") != "wendao-save-check\n":
            raise OSError("写入后的内容无法核对")
    except OSError as exc:
        return DiagnosticItem("本地存档目录", False, f"无法完成实际写入：{type(exc).__name__}")
    finally:
        for path in (temporary, committed):
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
    return DiagnosticItem("本地存档目录", True, "data/saves 可创建、写入、原子替换并回读")


def run_diagnostics(root: Path, *, save_dir: Path | None = None) -> list[DiagnosticItem]:
    root = root.resolve()
    items: list[DiagnosticItem] = []
    python_ok = sys.version_info >= (3, 11)
    items.append(DiagnosticItem("Python", python_ok, f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
    items.append(_runtime_dependencies())

    rule_path = root / "docs" / "修仙模拟器 · 问道长生.docx"
    rule_ok = rule_path.is_file() and rule_path.stat().st_size > 0
    items.append(DiagnosticItem("原始规则文档", rule_ok, "docs/修仙模拟器 · 问道长生.docx"))

    content_path = root / "data" / "content" / "decision_choices.json"
    try:
        payload = json.loads(content_path.read_text(encoding="utf-8"))
        content_ok = payload.get("schema_version") == 1 and isinstance(payload.get("phases"), dict)
        content_detail = f"{len(payload.get('phases', {}))} 个抉择阶段"
    except (OSError, json.JSONDecodeError) as exc:
        content_ok = False
        content_detail = f"data/content/decision_choices.json 无法读取或解析（{type(exc).__name__}）"
    items.append(DiagnosticItem("结构化内容", content_ok, content_detail))

    web_assets = [root / "web" / name for name in ("index.html", "app.css", "app.js", "showcase.js")]
    items.append(DiagnosticItem("网页资源", all(path.is_file() for path in web_assets), "HTML / CSS / JavaScript"))
    items.append(_modern_assets(root))
    items.append(_writable_save_directory(root, save_dir))
    return items


def diagnostics_text(root: Path, *, save_dir: Path | None = None) -> tuple[bool, str]:
    items = run_diagnostics(root, save_dir=save_dir)
    lines = ["《问道长生》V0.59 运行环境检查"]
    for item in items:
        lines.append(f"[{'通过' if item.passed else '失败'}] {item.name}：{item.detail}")
    passed = all(item.passed for item in items)
    lines.append("检查完成，可以启动新版界面。" if passed else "存在未通过项目，请按报告提示修复后重试。")
    return passed, "\n".join(lines)
