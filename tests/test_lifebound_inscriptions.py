from __future__ import annotations

import unittest
from xiuxian_simulator.artifact_growth import ArtifactGrowthEngine, INSCRIPTIONS, INFUSIBLE_MATERIALS
from xiuxian_simulator.state import GameState
from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.tianji_rankings import TianjiRankingsEngine


class TestLifeboundInscriptions(unittest.TestCase):
    def setUp(self) -> None:
        self.state = GameState(phase='playing')
        self.state.player.inventory = ['玄铁剑', '护身法袍']
        self.state.player.equipped_weapon = '玄铁剑'
        self.state.player.equipped_armor = '护身法袍'
        self.state.player.spirit_stones = 2000
        self.state.player.spirit = 100
        self.state.player.resources = {
            '灵铁': 20,
            '妖兽材料': 15,
            '天工万象铁': 5,
            '太玄剑魄': 2,
        }

    def test_catalog_structure(self) -> None:
        self.assertEqual(len(INSCRIPTIONS), 9)
        self.assertIn('锋锐', INSCRIPTIONS)
        self.assertIn('固本', INSCRIPTIONS)
        self.assertIn('混沌', INSCRIPTIONS)
        self.assertIn('天工万象铁', INFUSIBLE_MATERIALS)

    def test_inscribe_and_wash(self) -> None:
        ArtifactGrowthEngine.bind(self.state, '玄铁剑')
        self.assertEqual(self.state.bonded_artifact, '玄铁剑')

        res = ArtifactGrowthEngine.inscribe(self.state, '玄铁剑', '锋锐')
        self.assertIn('锋锐', res['inscriptions'])
        self.assertEqual(self.state.player.resources['灵铁'], 17)

        can, reason = ArtifactGrowthEngine.inscribe_availability(self.state, '玄铁剑', '锋锐')
        self.assertFalse(can)
        self.assertIn('已铭刻', reason)

        wash_res = ArtifactGrowthEngine.wash(self.state, '玄铁剑', '锋锐')
        self.assertEqual(wash_res['washed'], '锋锐')
        self.assertNotIn('锋锐', wash_res['inscriptions'])

    def test_slot_limits_and_type_restrictions(self) -> None:
        self.state.player.inventory.append('青锋剑')
        self.state.player.equipped_weapon = '青锋剑'
        ArtifactGrowthEngine.bind(self.state, '青锋剑')
        ArtifactGrowthEngine.inscribe(self.state, '青锋剑', '锋锐')
        ArtifactGrowthEngine.inscribe(self.state, '青锋剑', '固本')
        
        can, reason = ArtifactGrowthEngine.inscribe_availability(self.state, '青锋剑', '聚灵')
        self.assertFalse(can)
        self.assertIn('最多铭刻', reason)

        self.state.player.inventory.append('玄龟甲')
        can_armor, armor_reason = ArtifactGrowthEngine.inscribe_availability(self.state, '玄龟甲', '噬血')
        self.assertFalse(can_armor)
        self.assertIn('武器类', armor_reason)

    def test_infusion_and_spirit_commune(self) -> None:
        ArtifactGrowthEngine.bind(self.state, '玄铁剑')
        before_res = self.state.artifact_refinements['玄铁剑']['resonance']

        infuse_res = ArtifactGrowthEngine.infuse(self.state, '玄铁剑', '天工万象铁')
        self.assertEqual(infuse_res['material'], '天工万象铁')
        self.assertEqual(infuse_res['resonance'], before_res + 8)

        commune_res = ArtifactGrowthEngine.spirit_commune(self.state, '玄铁剑')
        self.assertIn('stage', commune_res)
        self.assertIn('title', commune_res)

    def test_engine_action_dispatch(self) -> None:
        from xiuxian_simulator.cli import build_engine
        engine = build_engine()
        engine.process('开始游戏')
        engine.process('确认默认创角')
        engine.state.player.inventory.append('玄铁剑')
        engine.state.player.equipped_weapon = '玄铁剑'
        engine.state.player.spirit_stones = 1000
        engine.state.player.resources['灵铁'] = 10

        out_bind = engine.process('认主法宝 玄铁剑')
        self.assertIn('法宝认主', out_bind)

        out_inscribe = engine.process('铭刻器纹 玄铁剑 锋锐')
        self.assertIn('器纹铭刻', out_inscribe)

        out_commune = engine.process('器灵感应 玄铁剑')
        self.assertIn('器灵通微', out_commune)

        out_wash = engine.process('洗练器纹 玄铁剑 锋锐')
        self.assertIn('器纹洗练', out_wash)

    def test_snapshot_read_only_and_power(self) -> None:
        clean_state = GameState(phase='playing')
        snap = ArtifactGrowthEngine.snapshot(clean_state)
        self.assertIn('all_inscriptions', snap)
        self.assertIn('infusable_materials', snap)
        self.assertEqual(clean_state.artifact_refinements, {})

        power_before = TianjiRankingsEngine.calculate_player_power(clean_state)
        clean_state.bonded_artifact = '玄铁剑'
        clean_state.artifact_refinements['玄铁剑'] = {
            'level': 2,
            'resonance': 50,
            'inscriptions': ['锋锐', '固本'],
        }
        power_after = TianjiRankingsEngine.calculate_player_power(clean_state)
        self.assertGreater(power_after, power_before)


if __name__ == '__main__':
    unittest.main()
