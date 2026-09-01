from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

from xiuxian_simulator import __version__
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.56.0"


class ReleaseReadinessTests(unittest.TestCase):
    def test_runtime_and_package_versions_match(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        package = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "frontend" / "package-lock.json").read_text(encoding="utf-8"))

        self.assertEqual(project["project"]["version"], VERSION)
        self.assertEqual(package["version"], VERSION)
        self.assertEqual(lock["version"], VERSION)
        self.assertEqual(lock["packages"][""]["version"], VERSION)
        self.assertEqual(__version__, VERSION)
        self.assertEqual(GameState().version, VERSION)

    def test_production_frontend_is_split_and_licensed(self) -> None:
        dist = ROOT / "frontend" / "dist"
        index = (dist / "index.html").read_text(encoding="utf-8")
        scripts = re.findall(r'<script[^>]+src="([^"]+\.js)"', index)
        assets = sorted((dist / "assets").glob("*.js"))

        self.assertTrue(scripts)
        self.assertGreaterEqual(len(assets), 4)
        self.assertLess(max(path.stat().st_size for path in assets), 500_000)
        self.assertTrue((dist / "third-party-licenses.md").is_file())
        self.assertTrue(all(not re.search(r"[ \t]+$", path.read_text(encoding="utf-8"), re.MULTILINE) for path in assets))

        package = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        self.assertIn("scripts/normalize-dist.mjs", package["scripts"]["build"])

    def test_continuous_integration_covers_both_stacks(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for expected in (
            "python -m pytest",
            "python -m xiuxian_simulator --check",
            "python scripts/package_release.py --check",
            "npm run lint",
            "npm test",
            "npm run build",
            "npm run verify:dist",
        ):
            self.assertIn(expected, workflow)
        self.assertIn("PYTHONUTF8: '1'", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("release:", workflow)

    def test_player_guide_defaults_to_modern_interface(self) -> None:
        guide = (ROOT / "首次游玩指南.md").read_text(encoding="utf-8")
        self.assertLess(guide.index("启动新版界面.bat"), guide.index("启动网页版.bat"))
        self.assertIn("成果巡览", guide)
        self.assertIn("不会修改真实存档", guide)
        self.assertIn("自动保留备份", guide)

    def test_formal_release_policy_is_explicit(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        checklist = (ROOT / "docs" / "正式发布检查清单.md").read_text(encoding="utf-8")
        self.assertIn("内部 V0.x 迭代不再创建标签或 GitHub Release", readme)
        self.assertIn("v1.0.0", readme)
        self.assertIn("唯一的 v1.0.0 标签", checklist)

    def test_windows_release_bundle_is_clean_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive = Path(temp_dir) / "Wendao-Changsheng-v0.56.0-windows.zip"
            second_archive = Path(temp_dir) / "rebuild.zip"
            for output in (archive, second_archive):
                subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "package_release.py"),
                        "--version",
                        VERSION,
                        "--output",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )

            self.assertEqual(archive.read_bytes(), second_archive.read_bytes())

            checksum_file = archive.with_suffix(".zip.sha256")
            expected = hashlib.sha256(archive.read_bytes()).hexdigest()
            self.assertEqual(checksum_file.read_text(encoding="utf-8").split()[0], expected)

            with zipfile.ZipFile(archive) as bundle:
                names = set(bundle.namelist())
            prefix = f"Wendao-Changsheng-v{VERSION}/"
            for required in (
                ".env.example",
                "main.py",
                "检查环境.bat",
                "启动网页版.bat",
                "启动新版界面.bat",
                "src/xiuxian_simulator/__init__.py",
                "frontend/dist/index.html",
                "data/saves/.gitkeep",
            ):
                self.assertIn(prefix + required, names)
            self.assertFalse(any("/tests/" in name or "/node_modules/" in name for name in names))
            self.assertFalse(any(name.endswith(("autosave.json", "autosave.json.bak", ".env")) for name in names))


if __name__ == "__main__":
    unittest.main()
