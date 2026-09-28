import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from xiuxian_simulator.cli import build_engine
from xiuxian_simulator.modern_web import create_modern_app
from xiuxian_simulator.save_manager import SaveManager
from xiuxian_simulator.state import GameState


ROOT = Path(__file__).resolve().parents[1]


class SaveDeletionTests(unittest.TestCase):
    def test_delete_removes_only_selected_save_and_preserves_recovery_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = SaveManager(Path(directory))
            manager.save('旧档', GameState(turn=1))
            manager.save('旧档', GameState(turn=2))
            manager.save('保留', GameState(turn=3))
            original = manager.path_for('旧档').read_bytes()
            backup = manager.backup_path_for('旧档').read_bytes()
            result = manager.delete('旧档')
            self.assertEqual(manager.list_names(), ['保留'])
            self.assertFalse(manager.backup_path_for('旧档').exists())
            recovery = Path(result['recovery_directory'])
            self.assertEqual((recovery / '旧档.json').read_bytes(), original)
            self.assertEqual((recovery / '旧档.json.bak').read_bytes(), backup)

    def test_delete_rejects_invalid_names_without_touching_autosave(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = SaveManager(Path(directory))
            manager.save('autosave', GameState())
            for name in ('', '../autosave', '  autosave', 'a/b'):
                with self.subTest(name=name), self.assertRaises(ValueError):
                    manager.delete(name)
            self.assertEqual(manager.list_names(), ['autosave'])

    def test_delete_can_remove_corrupt_files_and_repeated_delete_is_not_found(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = SaveManager(Path(directory))
            manager.path_for('坏档').write_bytes(b'broken json')
            manager.delete('坏档')
            with self.assertRaises(FileNotFoundError):
                manager.delete('坏档')

    def test_api_delete_refreshes_list_without_resetting_current_character(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = build_engine(ROOT)
            engine.saves = SaveManager(Path(directory))
            engine.process('快速开始游戏')
            before = engine.state.to_dict()
            client = TestClient(create_modern_app(engine, ROOT))
            response = client.delete('/api/v1/saves', params={'name': 'autosave'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(client.get('/api/v1/state').json()['save_names'], [])
            self.assertEqual(engine.state.to_dict(), before)
            self.assertEqual(client.delete('/api/v1/saves', params={'name': 'autosave'}).status_code, 404)
            self.assertEqual(client.delete('/api/v1/saves', params={'name': '../autosave'}).status_code, 400)
