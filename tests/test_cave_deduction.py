import unittest
from xiuxian_simulator.cave import CaveEngine
from xiuxian_simulator.crafting import CraftingEngine
from xiuxian_simulator.state import GameState


class TestCaveDeduction(unittest.TestCase):
    def test_snapshot_exposes_structured_crops_and_skills(self) -> None:
        state = GameState(phase="playing")
        state.cave_facilities["灵田"] = 2
        state.player.resources["灵药"] = 10
        CraftingEngine.plant(state, "灵药")

        snapshot = CaveEngine.snapshot(state)
        self.assertEqual(len(snapshot["crops"]), 1)
        crop = snapshot["crops"][0]
        self.assertEqual(crop["name"], "灵药")
        self.assertEqual(crop["expected_yield"], 5)
        self.assertEqual(crop["harvest_action"], "收获 灵药")
        self.assertIn(crop["stage"], ("萌芽期", "抽叶期", "孕灵期", "成熟待采"))

        # Test skills exposed
        self.assertIn("炼丹", snapshot["skills"])
        self.assertIn("灵植", snapshot["skills"])

        # Test instant action exposed in blueprints
        juqi = next(item for item in snapshot["blueprints"] if item["name"] == "聚气丹")
        self.assertEqual(juqi["instant_action"], "炼丹 聚气丹")
        self.assertTrue(juqi["instant_available"])


if __name__ == "__main__":
    unittest.main()
