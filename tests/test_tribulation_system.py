from __future__ import annotations

import unittest
from pathlib import Path

from xiuxian_simulator.state import GameState
from xiuxian_simulator.progression import ProgressionEngine, REALMS
from xiuxian_simulator.tribulation import TribulationEngine, TRIBULATION_TIERS


class TribulationSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = GameState()
        self.player = self.state.player

    def test_tribulation_tiers_and_spectrum(self) -> None:
        """验证九重大境界天劫谱系完整配置。"""
        self.assertEqual(len(TRIBULATION_TIERS), 9)
        # 筑基为一九玄霄
        t1 = TribulationEngine.get_tier_info(1)
        self.assertEqual(t1["name"], "一九玄霄雷劫")
        self.assertEqual(t1["waves_count"], 3)
        # 金丹为三九金阳
        t3 = TribulationEngine.get_tier_info(3)
        self.assertEqual(t3["name"], "三九金阳大天劫")
        self.assertEqual(t3["waves_count"], 3)
        # 元婴为六九紫霄
        t5 = TribulationEngine.get_tier_info(5)
        self.assertEqual(t5["name"], "六九紫霄神雷劫")
        self.assertEqual(t5["waves_count"], 4)
        # 登仙为混沌飞升
        t9 = TribulationEngine.get_tier_info(9)
        self.assertEqual(t9["name"], "混沌九极飞升大劫")
        self.assertEqual(t9["waves_count"], 5)

    def test_dao_protection_evaluation(self) -> None:
        """验证本命法宝器纹、器灵、阵法及避劫符对护道抗劫率的加成。"""
        # 初始状态，无护道
        base_prot = TribulationEngine.evaluate_dao_protection(self.state, "天道")
        self.assertFalse(base_prot.has_artifact)
        self.assertEqual(base_prot.defense_score, 0)
        self.assertEqual(base_prot.readiness_label, "单薄涉险")

        # 装备本命法宝并铭刻雷罡与护命器纹
        self.player.lifebound_artifact = {
            "active": True,
            "name": "太玄斩雷剑",
            "tier": "地阶",
            "affinity": 65,
            "inscriptions": ["雷罡", "护命", "固本"],
            "spirit_stage": "形意",
            "spirit_stage_index": 2,
        }
        self.state.cave_facilities = {"聚灵阵": 2, "禁制": 1}
        self.player.resources["避劫符"] = 1

        prot = TribulationEngine.evaluate_dao_protection(self.state, "天道")
        self.assertTrue(prot.has_artifact)
        self.assertTrue(prot.has_thunder_seal)
        self.assertTrue(prot.has_life_seal)
        self.assertTrue(prot.has_solid_seal)
        self.assertTrue(prot.has_ward_talisman)
        self.assertGreater(prot.thunder_mitigation_rate, 0.40)
        self.assertGreater(prot.defense_score, 100)
        self.assertEqual(prot.readiness_label, "万全通天")
        self.assertIn("雷罡·引雷淬体", prot.protection_tags)
        self.assertIn("护命·绝境免死", prot.protection_tags)

    def test_tribulation_simulation_waves_and_mitigation(self) -> None:
        """验证天劫推演中波次推进与护道减伤机制。"""
        self.player.realm_index = 2  # 结晶境突破金丹
        self.player.stage_index = 3
        self.player.health = 500
        self.player.health_max = 500
        self.player.dao_heart = 20
        self.player.fortune = 20
        self.player.merit = 50

        # 本命法宝有雷罡与固本
        self.player.lifebound_artifact = {
            "active": True,
            "name": "青霄剑",
            "tier": "玄阶",
            "affinity": 50,
            "inscriptions": ["雷罡", "固本"],
            "spirit_stage": "初醒",
            "spirit_stage_index": 1,
        }

        result = TribulationEngine.simulate_tribulation(self.state, "天道")
        self.assertEqual(result.tier_name, "三九金阳大天劫")
        self.assertEqual(result.total_waves, 3)
        self.assertEqual(len(result.waves), 3)
        self.assertGreater(result.mitigated_total, 0)
        # 检查第一波触发机制记录
        first_wave = result.waves[0]
        self.assertTrue(any(t["kind"] == "artifact" for t in first_wave.triggers))

    def test_life_saving_with_inscription_and_talisman(self) -> None:
        """验证在致命天劫下，护命器纹绝境替死并复苏 35% 气血。"""
        self.player.realm_index = 4  # 具灵突破元婴（六九紫霄天劫）
        self.player.stage_index = 3
        self.player.health = 20  # 残血，首波雷击必死
        self.player.health_max = 400
        self.player.lifebound_artifact = {
            "active": True,
            "name": "乾坤护命盾",
            "tier": "地阶",
            "affinity": 80,
            "inscriptions": ["护命"],
            "spirit_stage": "初醒",
            "spirit_stage_index": 1,
        }

        result = TribulationEngine.simulate_tribulation(self.state, "天道")
        self.assertTrue(result.life_saved)
        self.assertIn("护命", result.life_saved_source)
        # 替死后气血得到复苏
        self.assertGreater(result.waves[0].player_health_after, 0)

    def test_major_breakthrough_integration_with_tribulation(self) -> None:
        """验证大境界突破全流程与天劫日志、法宝反哺。"""
        self.player.stage_index = 3
        self.player.cultivation = self.player.cultivation_required
        self.player.health = 500
        self.player.health_max = 500
        self.player.dao_heart = 20
        self.player.fortune = 20
        self.player.merit = 100
        self.player.resources["筑基丹"] = 1
        self.state.rng_seed = 1
        self.player.lifebound_artifact = {
            "active": True,
            "name": "紫雷剑",
            "tier": "玄阶",
            "affinity": 30,
            "inscriptions": ["雷罡"],
            "spirit_stage": "初醒",
            "spirit_stage_index": 1,
        }

        res = ProgressionEngine.major_breakthrough(self.state, "人道")
        self.assertTrue(res.success)
        self.assertEqual(res.old_realm, "炼气·圆满")
        self.assertEqual(res.new_realm, "筑基·初期")
        self.assertIn("tribulation_detail", dir(res))
        self.assertIn("tier_name", res.tribulation_detail)
        self.assertEqual(res.tribulation_detail["tier_name"], "一九玄霄雷劫")
        # 雷罡淬器，契合度提升
        self.assertEqual(self.player.lifebound_artifact["affinity"], 33)

    def test_tribulation_snapshot_format(self) -> None:
        """验证前端快照结构。"""
        snap = TribulationEngine.snapshot(self.state)
        self.assertIn("tier_info", snap)
        self.assertIn("protection", snap)
        self.assertEqual(snap["target_realm"], "筑基")
        self.assertIn("waves_count", snap["tier_info"])
        self.assertIn("readiness_label", snap["protection"])


if __name__ == "__main__":
    unittest.main()
