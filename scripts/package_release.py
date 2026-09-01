from __future__ import annotations

import argparse
import hashlib
import os
import re
import tomllib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = (
    ".env.example",
    "main.py",
    "pyproject.toml",
    "README.md",
    "首次游玩指南.md",
    "检查环境.bat",
    "启动新版界面.bat",
)
PACKAGE_TREES = (
    "src",
    "frontend",
    "data/content",
    "docs",
    "prompts",
    "scripts",
)
EXTRA_FILES = ("data/saves/.gitkeep",)
IGNORED_PARTS = {
    ".git",
    ".github",
    ".npm-cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "node_modules",
}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".tsbuildinfo"}
REQUIRED_FILES = {
    ".env.example",
    "main.py",
    "pyproject.toml",
    "README.md",
    "检查环境.bat",
    "启动新版界面.bat",
    "src/xiuxian_simulator/__init__.py",
    "data/content/decision_choices.json",
    "data/saves/.gitkeep",
    "docs/修仙模拟器 · 问道长生.docx",
    "docs/正式版发布说明.md",
    "frontend/dist/index.html",
    "frontend/dist/third-party-licenses.md",
    "scripts/verify_release.py",
}
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?")


class PackageError(RuntimeError):
    pass


def project_version(root: Path = ROOT) -> str:
    payload = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def normalize_version(raw: str) -> str:
    version = raw.strip().removeprefix("v")
    if not VERSION_PATTERN.fullmatch(version):
        raise PackageError(f"版本号必须使用语义版本格式，例如 1.0.0；收到：{raw!r}")
    return version


def _included(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return (
        path.is_file()
        and not any(part in IGNORED_PARTS for part in relative.parts)
        and path.suffix.lower() not in IGNORED_SUFFIXES
        and path.name not in {".env", ".DS_Store"}
    )


def collect_release_files(root: Path = ROOT) -> list[Path]:
    files: set[Path] = set()
    for name in ROOT_FILES:
        path = root / name
        if path.is_file():
            files.add(path)
    for name in PACKAGE_TREES:
        tree = root / name
        if tree.is_dir():
            files.update(path for path in tree.rglob("*") if _included(path, root))
    for name in EXTRA_FILES:
        path = root / name
        if path.is_file():
            files.add(path)

    relative = {path.relative_to(root).as_posix() for path in files}
    missing = sorted(REQUIRED_FILES - relative)
    if missing:
        raise PackageError(f"发布包缺少必需文件：{', '.join(missing)}")
    forbidden = [
        name
        for name in relative
        if name.startswith(("tests/", ".git/", ".venv/", "artifacts/"))
        or "/node_modules/" in f"/{name}/"
        or (name.startswith("data/saves/") and name != "data/saves/.gitkeep")
    ]
    if forbidden:
        raise PackageError(f"发布清单混入私有或开发文件：{', '.join(sorted(forbidden)[:5])}")
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def _archive_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive(
    output: Path,
    version: str,
    *,
    root: Path = ROOT,
    force: bool = False,
) -> tuple[Path, Path, int]:
    version = normalize_version(version)
    files = collect_release_files(root)
    output = output.resolve()
    checksum_path = output.with_suffix(output.suffix + ".sha256")
    if not force and (output.exists() or checksum_path.exists()):
        raise PackageError(f"目标已存在，请改用新路径或显式传入 --force：{output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.unlink(missing_ok=True)
    prefix = f"Wendao-Changsheng-v{version}"
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                relative = path.relative_to(root).as_posix()
                archive.writestr(_archive_info(f"{prefix}/{relative}"), path.read_bytes())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    checksum = sha256(output)
    checksum_temp = checksum_path.with_name(f".{checksum_path.name}.tmp")
    try:
        checksum_temp.write_text(f"{checksum}  {output.name}\n", encoding="utf-8", newline="\n")
        os.replace(checksum_temp, checksum_path)
    finally:
        checksum_temp.unlink(missing_ok=True)
    return output, checksum_path, len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description="构建《问道长生》Windows 正式发布包")
    parser.add_argument("--version", default=project_version(), help="发布版本，默认读取 pyproject.toml")
    parser.add_argument("--output", type=Path, help="ZIP 输出路径")
    parser.add_argument("--check", action="store_true", help="只验证发布清单，不写入文件")
    parser.add_argument("--force", action="store_true", help="允许覆盖指定的旧发布包")
    args = parser.parse_args()

    try:
        version = normalize_version(args.version)
        files = collect_release_files()
        if args.check:
            print(f"发布清单验证通过：{len(files)} 个文件，版本 v{version}。")
            return
        output = args.output or ROOT / "artifacts" / f"Wendao-Changsheng-v{version}-windows.zip"
        archive, checksum, count = build_archive(output, version, force=args.force)
    except PackageError as exc:
        parser.error(str(exc))

    print(f"发布包已生成：{archive}")
    print(f"SHA-256 校验：{checksum}")
    print(f"共收录 {count} 个文件；私人存档、虚拟环境、依赖缓存和测试目录均已排除。")


if __name__ == "__main__":
    main()
