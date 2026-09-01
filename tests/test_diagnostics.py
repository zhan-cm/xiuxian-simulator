from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from xiuxian_simulator.diagnostics import diagnostics_text, run_diagnostics


class DiagnosticTests(unittest.TestCase):
    def test_missing_modern_asset_is_reported_by_relative_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dist = root / "frontend" / "dist"
            dist.mkdir(parents=True)
            (dist / "index.html").write_text(
                '<!doctype html><script type="module" src="/assets/missing.js"></script>',
                encoding="utf-8",
            )
            (dist / "third-party-licenses.md").write_text("licenses", encoding="utf-8")

            modern = next(item for item in run_diagnostics(root) if item.name == "新版界面资源")
            self.assertFalse(modern.passed)
            self.assertIn("assets/missing.js", modern.detail)
            self.assertNotIn(str(root), modern.detail)
            _, report = diagnostics_text(root)
            self.assertNotIn(str(root), report)

    def test_save_probe_performs_real_write_and_leaves_no_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            save_dir = root / "data" / "saves"

            save_item = next(item for item in run_diagnostics(root) if item.name == "本地存档目录")
            self.assertTrue(save_item.passed, save_item.detail)
            self.assertEqual(list(save_dir.glob(".diagnostic-*")), [])

    def test_remote_frontend_resource_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            dist = root / "frontend" / "dist"
            assets = dist / "assets"
            assets.mkdir(parents=True)
            (assets / "local.js").write_text("", encoding="utf-8")
            (dist / "index.html").write_text(
                '<script src="/assets/local.js"></script><script src="https://cdn.example/game.js"></script>',
                encoding="utf-8",
            )
            (dist / "third-party-licenses.md").write_text("licenses", encoding="utf-8")

            modern = next(item for item in run_diagnostics(root) if item.name == "新版界面资源")
            self.assertFalse(modern.passed)
            self.assertIn("远程资源", modern.detail)


if __name__ == "__main__":
    unittest.main()
