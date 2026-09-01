from __future__ import annotations

import argparse
import json
import os
import re
import socket
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from package_release import (
    IGNORED_PARTS,
    IGNORED_SUFFIXES,
    REQUIRED_FILES,
    ROOT,
    PackageError,
    normalize_version,
    project_version,
    sha256,
)


PREFIX_PATTERN = re.compile(
    r"Wendao-Changsheng-v(?P<version>\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)"
)
CHECKSUM_PATTERN = re.compile(r"(?P<digest>[0-9A-Fa-f]{64})[ \t]+\*?(?P<filename>[^\r\n]+)")
MAX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024
LOCAL_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class VerificationError(RuntimeError):
    pass


def default_archive() -> Path:
    version = project_version()
    return ROOT / "artifacts" / f"Wendao-Changsheng-v{version}-windows.zip"


def verify_checksum(archive: Path, checksum_file: Path) -> str:
    if not archive.is_file():
        raise VerificationError(f"未找到发布包：{archive}")
    if not checksum_file.is_file():
        raise VerificationError(f"未找到 SHA-256 文件：{checksum_file}")

    lines = [line.strip() for line in checksum_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    if len(lines) != 1:
        raise VerificationError("SHA-256 文件必须且只能包含一条校验记录。")
    match = CHECKSUM_PATTERN.fullmatch(lines[0])
    if match is None:
        raise VerificationError("SHA-256 文件格式无效。")
    if match.group("filename") != archive.name:
        raise VerificationError(
            f"SHA-256 文件指向 {match.group('filename')!r}，与当前发布包 {archive.name!r} 不一致。"
        )

    expected = match.group("digest").lower()
    actual = sha256(archive)
    if actual != expected:
        raise VerificationError(f"SHA-256 不一致：期望 {expected}，实际 {actual}。")
    return actual


def _validate_member(info: zipfile.ZipInfo) -> PurePosixPath:
    name = info.filename
    if not name or "\\" in name or "\0" in name:
        raise VerificationError(f"发布包包含无效路径：{name!r}")
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise VerificationError(f"发布包包含不安全路径：{name!r}")
    if ":" in path.parts[0]:
        raise VerificationError(f"发布包包含盘符路径：{name!r}")
    mode = (info.external_attr >> 16) & 0xFFFF
    if stat.S_IFMT(mode) == stat.S_IFLNK:
        raise VerificationError(f"发布包不允许符号链接：{name!r}")
    return path


def verify_archive(archive: Path, expected_version: str | None = None) -> tuple[str, str, int]:
    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            if not infos:
                raise VerificationError("发布包为空。")

            paths = [_validate_member(info) for info in infos]
            names = [path.as_posix() for path in paths]
            if len(names) != len(set(names)):
                raise VerificationError("发布包包含重复路径。")

            roots = {path.parts[0] for path in paths}
            if len(roots) != 1:
                raise VerificationError("发布包必须只包含一个顶层目录。")
            prefix = roots.pop()
            prefix_match = PREFIX_PATTERN.fullmatch(prefix)
            if prefix_match is None:
                raise VerificationError(f"发布包顶层目录命名无效：{prefix!r}")
            version = prefix_match.group("version")
            if expected_version is not None and version != normalize_version(expected_version):
                raise VerificationError(f"发布包版本为 {version}，期望 {normalize_version(expected_version)}。")

            file_infos = [info for info in infos if not info.is_dir()]
            total_size = sum(info.file_size for info in file_infos)
            if total_size > MAX_UNCOMPRESSED_BYTES:
                raise VerificationError(
                    f"发布包解压后体积异常：{total_size} 字节，超过 {MAX_UNCOMPRESSED_BYTES} 字节上限。"
                )

            relative = {PurePosixPath(info.filename).relative_to(prefix).as_posix() for info in file_infos}
            missing = sorted(REQUIRED_FILES - relative)
            if missing:
                raise VerificationError(f"发布包缺少必需文件：{', '.join(missing)}")
            forbidden = [
                name
                for name in relative
                if any(part in IGNORED_PARTS for part in PurePosixPath(name).parts)
                or PurePosixPath(name).suffix.lower() in IGNORED_SUFFIXES
                or PurePosixPath(name).name in {".env", ".DS_Store"}
                or name.startswith("tests/")
                or (name.startswith("data/saves/") and name != "data/saves/.gitkeep")
            ]
            if forbidden:
                raise VerificationError(f"发布包混入私人或开发文件：{', '.join(sorted(forbidden)[:5])}")

            damaged = bundle.testzip()
            if damaged is not None:
                raise VerificationError(f"发布包内文件损坏：{damaged}")
    except zipfile.BadZipFile as exc:
        raise VerificationError("文件不是有效的 ZIP 发布包。") from exc

    return version, prefix, len(file_infos)


def _run_checked(command: list[str], cwd: Path, label: str) -> str:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
    except subprocess.TimeoutExpired as exc:
        raise VerificationError(f"{label}超过 90 秒，已停止。") from exc
    if result.returncode != 0:
        output = result.stdout.strip()[-4000:]
        raise VerificationError(f"{label}失败（退出码 {result.returncode}）：\n{output}")
    return result.stdout.strip()


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _read_json(url: str, *, data: bytes | None = None) -> dict[str, object]:
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    with LOCAL_OPENER.open(request, timeout=5) as response:
        if response.status != 200:
            raise VerificationError(f"本地接口 {url} 返回 HTTP {response.status}。")
        payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise VerificationError(f"本地接口 {url} 未返回 JSON 对象。")
        return payload


def _smoke_modern_server(project_root: Path) -> None:
    port = _available_port()
    base_url = f"http://127.0.0.1:{port}"
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    process = subprocess.Popen(
        [
            sys.executable,
            str(project_root / "main.py"),
            "--modern-web",
            "--no-open-browser",
            "--port",
            str(port),
        ],
        cwd=project_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        deadline = time.monotonic() + 30
        last_error: Exception | None = None
        health: dict[str, object] | None = None
        while time.monotonic() < deadline:
            if process.poll() is not None:
                output = process.communicate()[0].strip()[-4000:]
                raise VerificationError(f"新版界面服务提前退出（退出码 {process.returncode}）：\n{output}")
            try:
                health = _read_json(f"{base_url}/api/v1/health")
                break
            except (OSError, ValueError, VerificationError) as exc:
                last_error = exc
                time.sleep(0.25)
        if health is None:
            raise VerificationError(f"新版界面服务未能在 30 秒内就绪：{last_error}")
        if health.get("interface") != "react" or health.get("status") != "ok":
            raise VerificationError(f"健康接口返回异常：{health}")

        with LOCAL_OPENER.open(f"{base_url}/", timeout=5) as response:
            shell = response.read().decode("utf-8")
        if "问道长生" not in shell:
            raise VerificationError("React 生产页面未返回《问道长生》入口。")

        state = _read_json(f"{base_url}/api/v1/state")
        if not isinstance(state.get("state"), dict) or state["state"].get("phase") != "new":
            raise VerificationError("初始状态接口未处于 new 阶段。")
        action = _read_json(
            f"{base_url}/api/v1/actions",
            data=json.dumps({"action": "开始游戏"}, ensure_ascii=False).encode("utf-8"),
        )
        if not isinstance(action.get("state"), dict) or action["state"].get("phase") != "character_creation_basic":
            raise VerificationError("行动接口未能从入世推进到创角阶段。")
        exported_save = _read_json(f"{base_url}/api/v1/saves/export?name=autosave")
        if exported_save.get("format") != "wendao-changsheng-save":
            raise VerificationError("自动存档未能导出为便携卷宗。")
        imported_save = _read_json(
            f"{base_url}/api/v1/saves/import",
            data=json.dumps(
                {"data": exported_save, "preferred_name": "", "overwrite": False},
                ensure_ascii=False,
            ).encode("utf-8"),
        )
        if imported_save.get("name") != "autosave_导入1" or imported_save.get("renamed") is not True:
            raise VerificationError("便携卷宗未能在同名冲突时安全另存。")
        showcase = _read_json(f"{base_url}/api/v1/showcase")
        pages = showcase.get("pages")
        if not isinstance(pages, list) or len(pages) < 34:
            raise VerificationError("成果巡览未生成至少 34 页真实场景。")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def smoke_test_archive(archive: Path, prefix: str) -> None:
    with tempfile.TemporaryDirectory(prefix="xiuxian-release-smoke-") as temp_dir:
        extract_root = Path(temp_dir)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(extract_root)
        project_root = extract_root / prefix

        _run_checked([sys.executable, str(project_root / "main.py"), "--check"], project_root, "环境自检")
        _smoke_modern_server(project_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="验证《问道长生》Windows 发布包")
    parser.add_argument("archive", nargs="?", type=Path, default=default_archive(), help="待验证的 ZIP 发布包")
    parser.add_argument("--checksum", type=Path, help="SHA-256 文件，默认使用 ZIP 同名 .sha256")
    parser.add_argument("--expected-version", help="期望的语义版本号")
    parser.add_argument("--smoke", action="store_true", help="解压到临时目录并验证新版页面与本地接口")
    args = parser.parse_args()

    archive = args.archive.resolve()
    checksum_file = (args.checksum or archive.with_suffix(archive.suffix + ".sha256")).resolve()
    try:
        digest = verify_checksum(archive, checksum_file)
        version, prefix, count = verify_archive(archive, args.expected_version)
        if args.smoke:
            smoke_test_archive(archive, prefix)
    except (OSError, PackageError, VerificationError) as exc:
        parser.error(str(exc))

    print(f"发布包验证通过：v{version}，{count} 个文件。")
    print(f"SHA-256：{digest}")
    if args.smoke:
        print("全新解压目录中的新版页面、本地接口、行动推进、便携卷宗与成果巡览均已通过。")


if __name__ == "__main__":
    main()
