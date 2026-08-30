from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .state import GameState, PlayerState


INSIGHT_PER_POINT = 20
MAX_BRANCH_LEVEL = 3
TIER_REALMS = (0, 1, 3)
REALM_LABELS = ("炼气", "筑基", "金丹")


@dataclass(frozen=True, slots=True)
class DaoBranch:
    name: str
    mark: str
    subtitle: str
    summary: str
    effects: tuple[str, str, str]


BRANCHES: dict[str, DaoBranch] = {
    "剑道": DaoBranch("剑道", "剑", "锋芒由心", "逐层磨砺攻伐之意。", ("攻击威力 +5%", "攻击威力累计 +10%", "攻击威力累计 +15%")),
    "丹道": DaoBranch("丹道", "丹", "草木成真", "提升炼丹时对药性的把握。", ("炼丹成功率 +5%", "炼丹成功率累计 +10%", "炼丹成功率累计 +15%")),
    "器道": DaoBranch("器道", "器", "万物为兵", "令武器与护甲更契合自身。", ("法宝效果 +5%", "法宝效果累计 +10%", "法宝效果累计 +15%")),
    "符道": DaoBranch("符道", "符", "一笔通玄", "强化制符与符箓临阵威力。", ("制符成功率 +5%，符箓威力 +10%", "制符累计 +10%，符箓累计 +20%", "制符累计 +15%，符箓累计 +30%")),
    "阵道": DaoBranch("阵道", "阵", "借势天地", "让洞府阵势持续蕴养灵机。", ("洞府每月灵蕴 +1", "洞府每月灵蕴累计 +2", "洞府每月灵蕴累计 +3")),
    "体道": DaoBranch("体道", "体", "血肉为炉", "以肉身承载更深厚的道基。", ("气血上限 +5", "气血上限累计 +10", "气血上限累计 +15")),
    "御兽道": DaoBranch("御兽道", "兽", "万灵同契", "理解妖兽与秘境生灵的踪迹。", ("秘境探索成功率 +3%", "秘境探索累计 +6%", "秘境探索累计 +9%")),
    "无情道": DaoBranch("无情道", "寂", "澄心断念", "以尘缘代价换取心魔中的清明。", ("心魔劫 +4%，正向好感收益 -10%", "心魔劫累计 +8%，正向好感收益 -20%", "心魔劫累计 +12%，正向好感收益 -30%")),
    "有情道": DaoBranch("有情道", "情", "众生照我", "从相知与同行中体悟大道。", ("正向好感收益 +10%，双修 +10%", "正向好感累计 +20%，双修累计 +20%", "正向好感累计 +30%，双修累计 +30%")),
}


class DaoEngine:
    @staticmethod
    def player_level(player: PlayerState, branch: str) -> int:
        return max(0, min(MAX_BRANCH_LEVEL, int(player.dao_levels.get(branch, 0))))

    @classmethod
    def level(cls, state: GameState, branch: str) -> int:
        return cls.player_level(state.player, branch)

    @classmethod
    def gain_insight(cls, state: GameState, amount: int, source: str) -> int:
        gained = max(0, int(amount))
        if gained <= 0:
            return 0
        state.player.dao_insight = min(9999, state.player.dao_insight + gained)
        cls._record(state, f"{source}｜感悟 +{gained}")
        return gained

    @staticmethod
    def contemplation_gain(state: GameState) -> int:
        aura = {"贫瘠": 0, "普通": 1, "浓郁": 2, "福地": 3, "洞天": 4}.get(state.aura_level, 1)
        return max(6, 5 + state.player.comprehension // 3 + state.player.dao_heart // 5 + aura)

    @classmethod
    def contemplate(cls, state: GameState) -> int:
        cost = 10
        if state.player.spirit < cost:
            raise ValueError(f"灵力不足：观想需要 {cost} 点灵力，当前 {state.player.spirit}。")
        state.player.spirit -= cost
        return cls.gain_insight(state, cls.contemplation_gain(state), "静坐观想")

    @classmethod
    def digest(cls, state: GameState, limit: int | None = None, *, required: bool = True) -> int:
        available = state.player.dao_insight // INSIGHT_PER_POINT
        converted = available if limit is None else min(available, max(0, int(limit)))
        if converted <= 0:
            if required:
                raise ValueError(
                    f"感悟尚不足以凝成悟道点：当前 {state.player.dao_insight}/{INSIGHT_PER_POINT}。"
                )
            return 0
        state.player.dao_insight -= converted * INSIGHT_PER_POINT
        state.player.dao_points += converted
        cls._record(state, f"闭关消化感悟｜悟道点 +{converted}")
        return converted

    @classmethod
    def eligibility(cls, state: GameState, branch: str) -> tuple[bool, str]:
        if branch not in BRANCHES:
            return False, "未知道途"
        current = cls.level(state, branch)
        if current >= MAX_BRANCH_LEVEL:
            return False, "已臻当前圆满"
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if state.player.dao_points < 1:
            return False, "需要悟道点×1"
        required_realm = TIER_REALMS[current]
        if state.player.realm_index < required_realm:
            return False, f"第 {current + 1} 层需至少{REALM_LABELS[current]}境"
        return True, ""

    @classmethod
    def enlighten(cls, state: GameState, branch: str) -> int:
        eligible, reason = cls.eligibility(state, branch)
        if not eligible:
            raise ValueError(reason)
        before = cls.level(state, branch)
        new_level = before + 1
        state.player.dao_points -= 1
        state.player.dao_levels[branch] = new_level
        if branch == "体道":
            state.player.health_max += 5
            state.player.health = min(state.player.health_max, state.player.health + 5)
        cls._record(state, f"点亮{branch}第 {new_level} 层｜{BRANCHES[branch].effects[new_level - 1]}")
        return new_level

    @classmethod
    def attack_multiplier(cls, state: GameState) -> float:
        return 1 + cls.level(state, "剑道") * 0.05

    @classmethod
    def craft_bonus(cls, state: GameState, craft: str) -> int:
        branch = {"炼丹": "丹道", "炼器": "器道", "符箓": "符道"}.get(craft, "")
        return cls.level(state, branch) * 5 if branch else 0

    @classmethod
    def artifact_multiplier(cls, state: GameState) -> float:
        return 1 + cls.level(state, "器道") * 0.05

    @classmethod
    def talisman_multiplier(cls, state: GameState) -> float:
        return 1 + cls.level(state, "符道") * 0.10

    @classmethod
    def cave_energy_bonus(cls, state: GameState) -> int:
        return cls.level(state, "阵道")

    @classmethod
    def adventure_bonus(cls, state: GameState) -> int:
        return cls.level(state, "御兽道") * 3

    @classmethod
    def heart_trial_bonus(cls, state: GameState) -> int:
        return cls.level(state, "无情道") * 4

    @classmethod
    def affinity_gain(cls, state: GameState, amount: int) -> int:
        if amount <= 0:
            return amount
        multiplier = 1 + cls.level(state, "有情道") * 0.10 - cls.level(state, "无情道") * 0.10
        return max(1, math.ceil(amount * max(0.4, multiplier)))

    @classmethod
    def dual_cultivation_multiplier(cls, state: GameState) -> float:
        return 1 + cls.level(state, "有情道") * 0.10

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        free_to_act = state.phase == "playing"
        branches: list[dict[str, Any]] = []
        for branch in BRANCHES.values():
            level = cls.level(state, branch.name)
            eligible, reason = cls.eligibility(state, branch.name)
            next_effect = branch.effects[level] if level < MAX_BRANCH_LEVEL else "当前三层已圆满"
            branches.append(
                {
                    "id": branch.name,
                    "name": branch.name,
                    "mark": branch.mark,
                    "subtitle": branch.subtitle,
                    "summary": branch.summary,
                    "level": level,
                    "max_level": MAX_BRANCH_LEVEL,
                    "effect": branch.effects[level - 1] if level else "尚未点亮",
                    "next_effect": next_effect,
                    "eligible": eligible,
                    "disabled_reason": reason,
                    "action": f"点亮 {branch.name}",
                }
            )
        return {
            "insight": state.player.dao_insight,
            "insight_required": INSIGHT_PER_POINT,
            "points": state.player.dao_points,
            "total_levels": sum(item["level"] for item in branches),
            "branches": branches,
            "history": list(state.player.dao_history[-20:]),
            "contemplate_action": "观想",
            "digest_action": "闭关悟道",
            "can_contemplate": state.player.spirit >= 10 and free_to_act,
            "contemplate_reason": "请先完成当前抉择" if not free_to_act else ("" if state.player.spirit >= 10 else "灵力不足 10 点"),
            "can_digest": state.player.dao_insight >= INSIGHT_PER_POINT and free_to_act,
            "digest_reason": "请先完成当前抉择" if not free_to_act else ("" if state.player.dao_insight >= INSIGHT_PER_POINT else f"感悟需达到 {INSIGHT_PER_POINT}"),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        lines = [
            "【悟道九途】",
            f"感悟 {snapshot['insight']}/{snapshot['insight_required']}｜悟道点 {snapshot['points']}｜已点亮 {snapshot['total_levels']} 层",
        ]
        for branch in snapshot["branches"]:
            state_text = f"{branch['level']}/{branch['max_level']}"
            next_text = branch["next_effect"] if branch["eligible"] else branch["disabled_reason"]
            lines.append(f"{branch['name']} {state_text}｜{branch['effect']}｜下一层：{next_text}")
        lines.append("指令：观想／闭关悟道／点亮 [剑道等九途]")
        return "\n".join(lines)

    @staticmethod
    def _record(state: GameState, text: str) -> None:
        state.player.dao_history.append(f"第 {state.turn} 回合｜{text}")
        state.player.dao_history = state.player.dao_history[-30:]
