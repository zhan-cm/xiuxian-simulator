from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import GameState
from .world import SECT_RANKS


@dataclass(frozen=True, slots=True)
class SectOffering:
    id: str
    sect: str
    name: str
    mark: str
    category: str
    minimum_rank: str
    cost: int
    rewards: dict[str, int]
    summary: str


OFFERINGS: tuple[SectOffering, ...] = (
    SectOffering("qingyun-evergreen", "青云宗", "长生青简", "青", "功法", "外门弟子", 100, {"青木长生诀残卷": 1}, "青云宗入门养生法，木行绵长、善于护体。"),
    SectOffering("qingyun-binding", "青云宗", "缚灵秘录", "缚", "法术", "内门弟子", 160, {"青木缚灵术残卷": 1}, "借草木生机束缚敌手，适合稳守与控场。"),
    SectOffering("qingyun-orb", "青云宗", "青岳灵珠", "珠", "奇珍", "真传弟子", 260, {"五行灵珠": 1}, "由青岳主脉温养的五行灵珠，可用于高阶阵图与洞府。"),
    SectOffering("qingyun-dao", "青云宗", "云海道痕", "道", "悟道", "长老", 480, {"道韵": 1}, "历代长老留在云海石壁上的一缕大道余韵。"),
    SectOffering("danxia-flame", "丹霞谷", "丹霞火经", "焰", "功法", "外门弟子", 100, {"赤炎真经残卷": 1}, "以丹火反哺经脉，兼顾炼丹与火行攻伐。"),
    SectOffering("danxia-healing", "丹霞谷", "回春丹匣", "丹", "丹药", "内门弟子", 120, {"疗伤丹": 3}, "谷中常备的护道丹匣，适合远行与秘境历练。"),
    SectOffering("danxia-core", "丹霞谷", "结丹灵药", "金", "破境", "真传弟子", 380, {"结丹灵药": 1}, "由长老亲自看护的结丹主药，只向真传开放。"),
    SectOffering("danxia-dao", "丹霞谷", "丹火道痕", "道", "悟道", "长老", 480, {"道韵": 1}, "炉火千年不熄，凝成可供长老参悟的丹道余韵。"),
    SectOffering("xuanjian-aura", "玄剑门", "庚金剑气录", "剑", "法术", "外门弟子", 120, {"庚金剑气残卷": 1}, "玄剑门外门必争的攻伐法术，以锋锐破甲。"),
    SectOffering("xuanjian-blade", "玄剑门", "玄铁剑胚", "锋", "法宝", "内门弟子", 180, {"玄铁剑": 1}, "经试剑台淬炼的玄铁剑胚，可直接作为主战法宝。"),
    SectOffering("xuanjian-void", "玄剑门", "太虚剑典", "虚", "功法", "真传弟子", 360, {"太虚剑典残卷": 1}, "玄剑门真传根本法，剑意攻守一体。"),
    SectOffering("xuanjian-orb", "玄剑门", "五行剑丸", "丸", "奇珍", "长老", 420, {"五行灵珠": 1}, "五行剑意凝成的剑丸，可作为高阶阵盘枢纽。"),
)


class SectLibraryEngine:
    GUIDANCE_COST = 60

    @staticmethod
    def _rank_index(rank: str) -> int:
        try:
            return SECT_RANKS.index(rank)
        except ValueError:
            return -1

    @classmethod
    def _known_reward(cls, state: GameState, offering: SectOffering) -> bool:
        for item in offering.rewards:
            if not item.endswith("残卷"):
                continue
            art = item.removesuffix("残卷")
            if art in state.player.known_techniques or art in state.player.known_spells:
                return True
        return False

    @classmethod
    def eligibility(cls, state: GameState, offering: SectOffering) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if state.player.sect == "散修":
            return False, "请先拜入宗门"
        if state.player.sect != offering.sect:
            return False, "并非本宗传承"
        if cls._rank_index(state.player.sect_rank) < cls._rank_index(offering.minimum_rank):
            return False, f"需要{offering.minimum_rank}权限"
        if offering.id in state.sect_library_claims:
            return False, "本世已经领取"
        if cls._known_reward(state, offering):
            return False, "已经掌握该传承"
        if state.player.sect_contribution < offering.cost:
            return False, f"贡献不足，还需 {offering.cost - state.player.sect_contribution}"
        return True, ""

    @classmethod
    def claim(cls, state: GameState, offering_id: str) -> tuple[SectOffering, str]:
        offering = next((item for item in OFFERINGS if item.id == offering_id or item.name == offering_id), None)
        if offering is None:
            raise ValueError("未知藏经阁供奉。")
        eligible, reason = cls.eligibility(state, offering)
        if not eligible:
            raise ValueError(reason)
        state.player.sect_contribution -= offering.cost
        for name, count in offering.rewards.items():
            state.player.resources[name] = state.player.resources.get(name, 0) + count
        state.sect_library_claims.append(offering.id)
        reward_text = "、".join(f"{name}×{count}" for name, count in offering.rewards.items())
        cls.record(state, f"以贡献 {offering.cost} 领取{offering.name}，所得 {reward_text}")
        return offering, reward_text

    @classmethod
    def guidance_availability(cls, state: GameState) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if state.player.sect == "散修":
            return False, "散修没有宗门传功"
        if state.founded_sect.get("name") == state.player.sect:
            return False, "自立宗门请由掌门在山门中主持传法"
        key = str(state.calendar_year)
        if key in state.sect_guidance_records:
            return False, "本年已经接受过传功"
        if state.player.sect_contribution < cls.GUIDANCE_COST:
            return False, f"需要 {cls.GUIDANCE_COST} 宗门贡献"
        return True, ""

    @classmethod
    def receive_guidance(cls, state: GameState) -> dict[str, int | str]:
        available, reason = cls.guidance_availability(state)
        if not available:
            raise ValueError(reason)
        rank_index = max(0, cls._rank_index(state.player.sect_rank))
        insight = 10 + rank_index * 4 + state.player.comprehension // 5
        cultivation = min(
            max(0, state.player.cultivation_required - state.player.cultivation),
            6 + rank_index * 4,
        )
        key = str(state.calendar_year)
        state.player.sect_contribution -= cls.GUIDANCE_COST
        state.player.dao_insight += insight
        state.player.cultivation += cultivation
        state.sect_guidance_records.append(key)
        cls.record(state, f"接受{state.player.sect}年度传功，感悟 +{insight}，修为 +{cultivation}")
        return {"sect": state.player.sect, "insight": insight, "cultivation": cultivation}

    @staticmethod
    def record(state: GameState, text: str) -> None:
        state.sect_library_history.append(f"第 {state.turn} 回合｜{text}")
        state.sect_library_history = state.sect_library_history[-30:]

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        member = any(offering.sect == state.player.sect for offering in OFFERINGS)
        offerings: list[dict[str, Any]] = []
        for offering in OFFERINGS:
            if not member or offering.sect != state.player.sect:
                continue
            eligible, reason = cls.eligibility(state, offering)
            offerings.append(
                {
                    "id": offering.id,
                    "sect": offering.sect,
                    "name": offering.name,
                    "mark": offering.mark,
                    "category": offering.category,
                    "minimum_rank": offering.minimum_rank,
                    "cost": offering.cost,
                    "rewards": "、".join(f"{name}×{count}" for name, count in offering.rewards.items()),
                    "summary": offering.summary,
                    "claimed": offering.id in state.sect_library_claims,
                    "available": eligible,
                    "disabled_reason": reason,
                    "action": f"兑换传承 {offering.id}",
                }
            )
        guidance, guidance_reason = cls.guidance_availability(state)
        return {
            "member": member,
            "sect": state.player.sect,
            "rank": state.player.sect_rank,
            "contribution": state.player.sect_contribution,
            "offerings": offerings,
            "claimed_count": len(state.sect_library_claims),
            "guidance_action": "宗门传功",
            "guidance_cost": cls.GUIDANCE_COST,
            "can_receive_guidance": guidance,
            "guidance_reason": guidance_reason,
            "history": list(reversed(state.sect_library_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        if state.player.sect == "散修":
            return "【宗门藏经阁】散修无宗门传承可查；可先在东洲选择宗门参加入门试炼。"
        if state.founded_sect.get("name") == state.player.sect:
            return "【自立山门】本宗典籍与传法由掌门亲自经营；请输入“宗门经营”查看。"
        snapshot = cls.snapshot(state)
        lines = "\n".join(
            f"{item['name']}｜{item['minimum_rank']}｜贡献 {item['cost']}｜{item['rewards']}"
            f"｜{'已领取' if item['claimed'] else item['disabled_reason'] or '可兑换'}"
            for item in snapshot["offerings"]
        )
        return (
            f"【{state.player.sect}藏经阁 · {state.player.sect_rank}】\n宗门贡献 {state.player.sect_contribution}\n"
            f"{lines}\n指令：兑换传承 [编号]／宗门传功（每年一次，贡献 {cls.GUIDANCE_COST}）"
        )
