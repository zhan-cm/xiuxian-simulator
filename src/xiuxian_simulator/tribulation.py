from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .state import GameState, PlayerState
from .progression import REALMS, ProgressionEngine

# 九重大境界天劫谱系
TRIBULATION_TIERS: dict[int, dict[str, Any]] = {
    1: {
        "tier": 1,
        "name": "一九玄霄雷劫",
        "title": "玄霄涤凡",
        "description": "天地灵气初凝，降下三波玄霄紫雷涤荡肉胎凡骨，通达仙基。",
        "waves_count": 3,
        "base_power": 120,
        "wave_names": ["第一重 · 青木引雷", "第二重 · 庚金疾雷", "第三重 · 玄霄落顶"],
        "element": "紫霄玄雷",
        "threat_level": "凡凡相蜕",
    },
    2: {
        "tier": 2,
        "name": "二九天煞风雷劫",
        "title": "天煞凝晶",
        "description": "天煞罡风呼啸，双雷交织撕裂气海，淬炼无瑕真元晶核。",
        "waves_count": 3,
        "base_power": 200,
        "wave_names": ["第一重 · 天煞阴风", "第二重 · 破脉煞雷", "第三重 · 晶核洗礼"],
        "element": "天煞风雷",
        "threat_level": "煞气贯脉",
    },
    3: {
        "tier": 3,
        "name": "三九金阳大天劫",
        "title": "金阳凝丹",
        "description": "二十七道金阳劫雷自九霄倾泻而下，金丹始成，夺天地之造化！",
        "waves_count": 3,
        "base_power": 320,
        "wave_names": ["第一重 · 金阳神雷", "第二重 · 烈火雷狱", "第三重 · 九转金阳贯顶"],
        "element": "纯阳天雷",
        "threat_level": "天道轰鸣",
    },
    4: {
        "tier": 4,
        "name": "四九幽冥玄雷劫",
        "title": "幽冥通灵",
        "description": "九幽冥雷与太虚罡气夹击，具现本命通灵神识，沟通冥冥。",
        "waves_count": 4,
        "base_power": 500,
        "wave_names": ["第一重 · 幽冥阴煞", "第二重 · 撼魂冥雷", "第三重 · 太虚幻相", "第四重 · 灵识破茧"],
        "element": "九幽阴雷",
        "threat_level": "阴阳交冲",
    },
    5: {
        "tier": 5,
        "name": "六九紫霄神雷劫",
        "title": "破丹成婴",
        "description": "五十四道紫霄雷罡撕裂苍穹，破丹化婴，跨越修仙生死大玄关！",
        "waves_count": 4,
        "base_power": 750,
        "wave_names": ["第一重 · 紫霄开天", "第二重 · 灭魂阴雷", "第三重 · 碎丹重塑", "第四重 · 紫霄归一雷"],
        "element": "九天紫霄雷",
        "threat_level": "通天死劫",
    },
    6: {
        "tier": 6,
        "name": "七九天罚诛仙劫",
        "title": "化神游虚",
        "description": "天道意志显化诛仙神罚法相，神念出窍神游太虚，逆伐天规。",
        "waves_count": 4,
        "base_power": 1100,
        "wave_names": ["第一重 · 诛仙剑雷", "第二重 · 碎念戮神", "第三重 · 大道审判", "第四重 · 元神登临天道"],
        "element": "天罚诛仙雷",
        "threat_level": "神游太虚",
    },
    7: {
        "tier": 7,
        "name": "八九太虚道劫",
        "title": "法则入体",
        "description": "太虚法则无情轰鸣，万道垂落，非道心通明者刹那化为飞灰！",
        "waves_count": 5,
        "base_power": 1600,
        "wave_names": ["第一重 · 虚空裂痕", "第二重 · 岁月道雷", "第三重 · 乾坤易位", "第四重 · 大道锁链", "第五重 · 悟道成真雷"],
        "element": "太虚道雷",
        "threat_level": "大道倾轧",
    },
    8: {
        "tier": 8,
        "name": "九九寂灭天劫",
        "title": "九九混元",
        "description": "八十一道混元寂灭黑雷铺天盖地，斩尽凡尘因果，羽化蜕仙胎！",
        "waves_count": 5,
        "base_power": 2400,
        "wave_names": ["第一重 · 寂灭天雷", "第二重 · 因果业火", "第三重 · 混元风暴", "第四重 · 仙胎重铸", "第五重 · 羽化绝顶劫"],
        "element": "混元寂灭雷",
        "threat_level": "寂灭万物",
    },
    9: {
        "tier": 9,
        "name": "混沌九极飞升大劫",
        "title": "飞升登仙",
        "description": "太古混沌神雷洞穿三界六道，九天之门大开，渡过即得证长生大道！",
        "waves_count": 5,
        "base_power": 3600,
        "wave_names": ["第一重 · 混沌初开", "第二重 · 太极两仪雷", "第三重 · 四象诛绝", "第四重 · 八卦崩解", "第五重 · 混沌天门贯顶"],
        "element": "鸿蒙混沌雷",
        "threat_level": "天门洞开",
    },
}


@dataclass
class DaoProtectionSummary:
    has_artifact: bool = False
    artifact_name: str = ""
    artifact_tier: str = ""
    affinity: int = 0
    inscriptions: list[str] = field(default_factory=list)
    has_thunder_seal: bool = False
    has_life_seal: bool = False
    has_solid_seal: bool = False
    has_chaos_seal: bool = False
    spirit_stage: str = "未觉醒"
    spirit_stage_index: int = 0
    spirit_dialogue: str = ""
    formation_shield: int = 0
    has_ward_talisman: bool = False
    has_protect_pill: bool = False
    has_breakthrough_pill: bool = False
    thunder_mitigation_rate: float = 0.0
    heart_bonus_rate: float = 0.0
    protection_tags: list[str] = field(default_factory=list)
    defense_score: int = 0
    readiness_label: str = "单薄"


@dataclass
class TribulationWaveRecord:
    wave: int
    name: str
    thunder_damage: int
    mitigated_damage: int
    actual_damage: int
    player_health_before: int
    player_health_after: int
    triggers: list[dict[str, str]]
    passed: bool
    description: str


@dataclass
class TribulationResult:
    success: bool
    tier_name: str
    route: str
    total_waves: int
    waves: list[TribulationWaveRecord]
    fatal: bool
    life_saved: bool
    life_saved_source: str
    heart_trial_passed: bool
    old_realm: str
    new_realm: str
    summary_text: str
    damage_total: int
    mitigated_total: int


class TribulationEngine:
    """天劫雷罚与九重渡劫护道引擎。"""

    @classmethod
    def get_tier_info(cls, target_realm_index: int) -> dict[str, Any]:
        safe_index = max(1, min(len(REALMS) - 1, target_realm_index))
        return TRIBULATION_TIERS.get(safe_index, TRIBULATION_TIERS[1])

    @classmethod
    def evaluate_dao_protection(cls, state: GameState, route: str = "天道") -> DaoProtectionSummary:
        """评估修仙者当前的护道底蕴（本命法宝、器纹、器灵、阵法、丹药符箓）。"""
        player = state.player
        summary = DaoProtectionSummary()

        # 1. 本命法宝与器纹扫描
        lifebound = getattr(player, "lifebound_artifact", None) or {}
        if not lifebound or not lifebound.get("active"):
            bonded = getattr(state, "bonded_artifact", "")
            if bonded and bonded in state.artifact_refinements:
                from .arts import ARTIFACTS
                from .artifact_growth import ArtifactGrowthEngine

                rec = ArtifactGrowthEngine.view_record(state, bonded)
                art = ARTIFACTS.get(bonded)
                stage_idx, stage_name, _ = ArtifactGrowthEngine.spirit_stage_info(int(rec.get("resonance", 0)))
                lifebound = {
                    "active": True,
                    "name": bonded,
                    "tier": art.grade if art else "玄阶",
                    "affinity": int(rec.get("resonance", 0)),
                    "inscriptions": list(rec.get("inscriptions", [])),
                    "spirit_stage": stage_name,
                    "spirit_stage_index": stage_idx,
                }

        if lifebound and lifebound.get("active"):
            summary.has_artifact = True
            summary.artifact_name = lifebound.get("name", "本命灵宝")
            summary.artifact_tier = lifebound.get("tier", "黄阶")
            summary.affinity = int(lifebound.get("affinity", 0))
            summary.inscriptions = list(lifebound.get("inscriptions", []))
            summary.spirit_stage = str(lifebound.get("spirit_stage", "未觉醒"))
            raw_stage_idx = lifebound.get("spirit_stage_index", 0)
            try:
                summary.spirit_stage_index = int(raw_stage_idx)
            except (ValueError, TypeError):
                summary.spirit_stage_index = 0

            # 器纹神威
            if "雷罡" in summary.inscriptions:
                summary.has_thunder_seal = True
                summary.thunder_mitigation_rate += 0.25
                summary.protection_tags.append("雷罡·引雷淬体")
                summary.defense_score += 35
            if "护命" in summary.inscriptions:
                summary.has_life_seal = True
                summary.protection_tags.append("护命·绝境免死")
                summary.defense_score += 40
            if "固本" in summary.inscriptions:
                summary.has_solid_seal = True
                summary.thunder_mitigation_rate += 0.15
                summary.protection_tags.append("固本·玄黄金身")
                summary.defense_score += 20
            if "混沌" in summary.inscriptions:
                summary.has_chaos_seal = True
                summary.thunder_mitigation_rate += 0.15
                summary.protection_tags.append("混沌·万气化一")
                summary.defense_score += 25

            # 契合度基础减伤（每 10 点契合度提供 1.5% 减伤，上限 15%）
            summary.thunder_mitigation_rate += min(0.15, summary.affinity * 0.0015)

            # 器灵境界庇护
            if summary.spirit_stage_index >= 1:  # 初醒
                summary.thunder_mitigation_rate += 0.05
                summary.protection_tags.append("器灵·神识预警")
                summary.defense_score += 10
            if summary.spirit_stage_index >= 2:  # 形意
                summary.protection_tags.append("器灵·法相御雷")
                summary.defense_score += 20
            if summary.spirit_stage_index >= 3:  # 人器合一
                summary.thunder_mitigation_rate += 0.10
                summary.protection_tags.append("器灵·人器合一")
                summary.defense_score += 25
            if summary.spirit_stage_index >= 4:  # 真灵显圣
                summary.protection_tags.append("真灵·显圣破劫")
                summary.defense_score += 45

        # 2. 洞府大阵与宗门光幕
        cave_features = getattr(player, "cave_features", {}) or {}
        facilities = getattr(state, "cave_facilities", {}) or {}
        formation_level = int(cave_features.get("formation_level", 0)) or int(facilities.get("聚灵阵", 0))
        restraint_level = int(cave_features.get("restraint_level", 0)) or int(facilities.get("禁制", 0))
        if formation_level > 0 or restraint_level > 0:
            shield_value = formation_level * 60 + restraint_level * 80 + 100
            summary.formation_shield = shield_value
            summary.protection_tags.append(f"洞府阵幕({shield_value}点)")
            summary.defense_score += 20

        # 3. 避劫符与保命丹药
        resources = getattr(player, "resources", {}) or {}
        if resources.get("避劫符", 0) > 0:
            summary.has_ward_talisman = True
            summary.protection_tags.append("天机·避劫符")
            summary.defense_score += 35
        if resources.get("九转还魂丹", 0) > 0 or resources.get("护脉丹", 0) > 0:
            summary.has_protect_pill = True
            summary.protection_tags.append("保命仙丹")
            summary.defense_score += 20

        # 4. 突破主丹药（人道突破所备）
        from .progression import HUMAN_PILLS

        pill_name = HUMAN_PILLS[player.realm_index] if 0 <= player.realm_index < len(HUMAN_PILLS) else "破境丹"
        if resources.get(pill_name, 0) > 0:
            summary.has_breakthrough_pill = True
            summary.heart_bonus_rate += 0.20
            summary.thunder_mitigation_rate += 0.35
            summary.protection_tags.append(f"{pill_name}·丹气护体")
            summary.defense_score += 25

        # 限制上限
        summary.thunder_mitigation_rate = min(0.85, summary.thunder_mitigation_rate)

        # 评级
        if summary.defense_score >= 100:
            summary.readiness_label = "万全通天"
        elif summary.defense_score >= 65:
            summary.readiness_label = "底蕴深厚"
        elif summary.defense_score >= 35:
            summary.readiness_label = "稍备护道"
        else:
            summary.readiness_label = "单薄涉险"

        return summary

    @classmethod
    def simulate_tribulation(
        cls,
        state: GameState,
        route: str,
        heart_roll: int | None = None,
        thunder_roll: int | None = None,
        base_heart_chance: int | None = None,
        base_thunder_chance: int | None = None,
    ) -> TribulationResult:
        """执行完整天劫推演：波次雷击、神威护道触发、心魔考验与生死逆转。"""
        player = state.player
        target_realm_index = player.realm_index + 1
        tier_info = cls.get_tier_info(target_realm_index)
        protection = cls.evaluate_dao_protection(state, route)

        waves_count = tier_info["waves_count"]
        base_power = tier_info["base_power"]
        wave_names = tier_info["wave_names"]

        # 路线调整天劫强度：天道最猛烈，地道次之，人道相对收敛
        route_multiplier = {"天道": 1.25, "地道": 1.0, "人道": 0.8}.get(route, 1.0)
        # 业障过重天雷更烈，功德深厚削减暴戾
        karma_factor = 1.0 + max(0, player.karma * 0.005) - max(0, player.merit * 0.003)
        karma_factor = max(0.7, min(1.6, karma_factor))

        current_hp = player.health
        shield = protection.formation_shield
        waves_records: list[TribulationWaveRecord] = []
        life_saved = False
        life_saved_source = ""
        total_dmg = 0
        total_mitigated = 0
        failed_wave = -1

        # 判定掷骰（心魔与雷劫概率）
        if base_heart_chance is None or base_thunder_chance is None:
            calc_heart, calc_thunder = ProgressionEngine.major_chances_for_state(state, route)
            base_heart_chance = calc_heart if base_heart_chance is None else base_heart_chance
            base_thunder_chance = calc_thunder if base_thunder_chance is None else base_thunder_chance

        # 护道带来的雷劫通过率修正（最多 +25%）
        effective_thunder_chance = min(99, base_thunder_chance + round(protection.defense_score * 0.2))
        effective_heart_chance = min(99, base_heart_chance + round(protection.heart_bonus_rate * 100))

        if heart_roll is None:
            heart_roll = ProgressionEngine.deterministic_roll(state, f"trib-heart:{route}:{player.realm_index}")
        if thunder_roll is None:
            thunder_roll = ProgressionEngine.deterministic_roll(state, f"trib-thunder:{route}:{player.realm_index}")

        heart_pass = heart_roll <= effective_heart_chance
        thunder_pass = thunder_roll <= effective_thunder_chance

        for i in range(waves_count):
            w_name = wave_names[i] if i < len(wave_names) else f"第{i+1}重 · 天雷诛顶"
            # 每波威力渐强
            wave_power = round(base_power * (0.8 + i * 0.35) * route_multiplier * karma_factor)
            triggers: list[dict[str, str]] = []
            mitigated = 0

            # 1. 洞府大阵吸收
            if shield > 0:
                absorbed = min(shield, round(wave_power * 0.5))
                shield -= absorbed
                mitigated += absorbed
                triggers.append({
                    "kind": "formation",
                    "title": "洞府护山大阵",
                    "desc": f"大阵灵幕剧烈震颤，化解了 {absorbed} 点天雷轰击（灵幕残余 {shield}）。",
                })

            # 2. 本命法宝雷罡器纹神威
            if protection.has_thunder_seal:
                seal_cut = round(wave_power * 0.25)
                mitigated += seal_cut
                triggers.append({
                    "kind": "artifact",
                    "title": f"本命法宝【{protection.artifact_name}】· 雷罡器纹",
                    "desc": f"器身如避雷金针，引雷入胚，削减 {seal_cut} 点狂暴雷能，余烬淬炼法宝！",
                })

            # 3. 固本/混沌器纹
            if protection.has_solid_seal:
                solid_cut = round(wave_power * 0.12)
                mitigated += solid_cut
                triggers.append({
                    "kind": "artifact",
                    "title": "固本神纹 · 玄黄金身",
                    "desc": f"金刚琉璃道骨微鸣，抵御 {solid_cut} 点肉身撕裂雷罡。",
                })
            if protection.has_chaos_seal:
                chaos_cut = round(wave_power * 0.12)
                mitigated += chaos_cut
                triggers.append({
                    "kind": "artifact",
                    "title": "混沌神纹 · 万气化一",
                    "desc": f"混沌清气回旋，化解 {chaos_cut} 点天地异种暴戾天威。",
                })

            # 4. 器灵觉醒神威
            if protection.spirit_stage_index >= 4 and i == waves_count - 1:  # 真灵显圣硬撼绝顶雷
                mitigated += wave_power - mitigated
                triggers.append({
                    "kind": "spirit",
                    "title": "器灵真灵显圣",
                    "desc": "本命器灵脱胎法相显化，顶天立地，硬撼绝顶灭世雷劫，化作漫天仙霞！",
                })
            elif protection.spirit_stage_index >= 2 and i == 1:  # 形意法相抵挡
                spirit_cut = min(wave_power - mitigated, 120)
                mitigated += spirit_cut
                triggers.append({
                    "kind": "spirit",
                    "title": "器灵形意法相",
                    "desc": f"器灵虚影横空出鞘，替主承接 {spirit_cut} 点天劫雷力！",
                })

            # 气血扣减计算：若判定通过，天雷按修士气血比例造成温和道体震荡；若判定失败，造成狂暴毁灭伤害
            mitigated_ratio = min(0.9, mitigated / max(1, wave_power))
            if thunder_pass:
                # 渡劫成功波次：每波扣减 8%~15% 气血作为洗礼
                actual_dmg = max(5, round(player.health_max * (0.08 + i * 0.04) * (1.0 - mitigated_ratio)))
            else:
                # 判定未通过：劫雷狂暴贯顶
                actual_dmg = max(15, wave_power - mitigated)

            hp_before = current_hp
            current_hp -= actual_dmg
            total_dmg += actual_dmg
            total_mitigated += mitigated

            # 绝境检测：气血见底
            wave_passed = True
            if current_hp <= 0 or (not thunder_pass and i == waves_count - 1):
                # 触发护命器纹替死
                if protection.has_life_seal and not life_saved:
                    life_saved = True
                    life_saved_source = "本命法宝 · 护命神纹"
                    current_hp = max(1, round(player.health_max * 0.35))
                    triggers.append({
                        "kind": "life_saving",
                        "title": "护命神纹 · 绝境涅槃",
                        "desc": "死劫当头，本命法宝护命神印爆发出璀璨红莲真火，替主死劫并复苏 35% 气血！",
                    })
                elif protection.has_ward_talisman and not life_saved:
                    # 触发避劫符
                    life_saved = True
                    life_saved_source = "天机阁 · 避劫符"
                    # 消耗避劫符
                    player.resources["避劫符"] -= 1
                    if player.resources["避劫符"] <= 0:
                        player.resources.pop("避劫符", None)
                    current_hp = max(1, round(player.health_max * 0.30))
                    triggers.append({
                        "kind": "life_saving",
                        "title": "天机避劫符 · 替劫消弭",
                        "desc": "避劫符无风自燃化作阴阳双鱼气罩，将灭世死雷挪移至太虚之中！",
                    })
                else:
                    if not thunder_pass:
                        wave_passed = False
                        failed_wave = i + 1
                        current_hp = 0

            desc = f"{w_name}轰然贯顶！天雷威能 {wave_power}，护道抵消 {mitigated}，肉身受震荡 {actual_dmg} 点气血。"
            waves_records.append(
                TribulationWaveRecord(
                    wave=i + 1,
                    name=w_name,
                    thunder_damage=wave_power,
                    mitigated_damage=mitigated,
                    actual_damage=actual_dmg,
                    player_health_before=hp_before,
                    player_health_after=current_hp,
                    triggers=triggers,
                    passed=wave_passed,
                    description=desc,
                )
            )

            if not wave_passed:
                break

        # 综合成功判定：全部波次挺过，且心魔劫与雷劫判定通过（或因绝境护道逆天改命）
        overall_success = (failed_wave == -1) and thunder_pass and heart_pass
        fatal = False

        if not overall_success and life_saved:
            fatal = False

        old_realm = player.realm
        new_realm = f"{REALMS[target_realm_index]}·初期" if overall_success else old_realm

        summary_lines = [
            f"【{tier_info['name']}】· {route}叩关渡劫战报",
            f"天劫雷罚：共降下 {len(waves_records)}/{waves_count} 重九霄神雷，总承雷威 {total_dmg + total_mitigated} 点，护道底蕴抵御化解 {total_mitigated} 点。",
        ]
        if life_saved:
            summary_lines.append(f"【逆天护道】关键时刻触发【{life_saved_source}】，绝境替死复苏！")
        if overall_success:
            summary_lines.append(f"劫云散去，九彩仙霞自天穹垂落，道基升华：{old_realm} 蜕入 【{new_realm}】！")
        else:
            reason = "心魔反噬" if not heart_pass else "雷劫轰顶"
            summary_lines.append(f"天威难测，终在突破关头惜败于{reason}。")

        return TribulationResult(
            success=overall_success,
            tier_name=tier_info["name"],
            route=route,
            total_waves=waves_count,
            waves=waves_records,
            fatal=fatal,
            life_saved=life_saved,
            life_saved_source=life_saved_source,
            heart_trial_passed=heart_pass,
            old_realm=old_realm,
            new_realm=new_realm,
            summary_text="\n".join(summary_lines),
            damage_total=total_dmg,
            mitigated_total=total_mitigated,
        )

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """向前端分发当前修士所面临的天劫前瞻与护道阵列。"""
        player = state.player
        target_realm = min(len(REALMS) - 1, player.realm_index + 1)
        tier_info = cls.get_tier_info(target_realm)
        protection = cls.evaluate_dao_protection(state, "天道")

        return {
            "current_realm": player.realm,
            "target_realm": REALMS[target_realm],
            "target_realm_index": target_realm,
            "tier_info": {
                "tier": tier_info["tier"],
                "name": tier_info["name"],
                "title": tier_info["title"],
                "description": tier_info["description"],
                "waves_count": tier_info["waves_count"],
                "base_power": tier_info["base_power"],
                "wave_names": tier_info["wave_names"],
                "element": tier_info["element"],
                "threat_level": tier_info["threat_level"],
            },
            "protection": {
                "has_artifact": protection.has_artifact,
                "artifact_name": protection.artifact_name,
                "artifact_tier": protection.artifact_tier,
                "affinity": protection.affinity,
                "inscriptions": protection.inscriptions,
                "has_thunder_seal": protection.has_thunder_seal,
                "has_life_seal": protection.has_life_seal,
                "has_solid_seal": protection.has_solid_seal,
                "has_chaos_seal": protection.has_chaos_seal,
                "spirit_stage": protection.spirit_stage,
                "spirit_stage_index": protection.spirit_stage_index,
                "formation_shield": protection.formation_shield,
                "has_ward_talisman": protection.has_ward_talisman,
                "has_protect_pill": protection.has_protect_pill,
                "has_breakthrough_pill": protection.has_breakthrough_pill,
                "thunder_mitigation_rate": round(protection.thunder_mitigation_rate * 100, 1),
                "protection_tags": protection.protection_tags,
                "defense_score": protection.defense_score,
                "readiness_label": protection.readiness_label,
            },
        }
