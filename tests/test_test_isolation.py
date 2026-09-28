import unittest
from pathlib import Path
from unittest.mock import patch

from xiuxian_simulator.save_manager import SaveManager


class TestSaveIsolation(unittest.TestCase):
    def test_integration_tests_never_write_formal_saves(self):
        tests_dir = Path(__file__).resolve().parent
        formal_dir = (tests_dir.parent / 'data' / 'saves').resolve()
        original_save = SaveManager.save

        def guarded_save(manager, name, state):
            self.assertNotEqual(manager.save_dir.resolve(), formal_dir,
                                'Integration test attempted to overwrite player saves')
            return original_save(manager, name, state)

        for pattern in ('test_tianji_rankings.py', 'test_natural_exploration.py',
                        'test_sect_visit.py', 'test_lifebound_inscriptions.py'):
            with self.subTest(pattern=pattern), patch.object(SaveManager, 'save', guarded_save):
                suite = unittest.defaultTestLoader.discover(str(tests_dir), pattern=pattern)
                result = unittest.TestResult()
                suite.run(result)
                self.assertEqual(result.errors + result.failures, [],
                                 str(result.errors + result.failures))
