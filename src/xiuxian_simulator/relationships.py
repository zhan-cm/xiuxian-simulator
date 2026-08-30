from __future__ import annotations

from dataclasses import dataclass

from .dao import DaoEngine
from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class NpcTemplate:
    name: str
    gender: str
    identity: str
    age: int
    realm: str
    location: str
    likes: tuple[str, ...]
    dislikes: tuple[str, ...]
    greeting: str
    dao_difficulty: int


@dataclass(frozen=True, slots=True)
class HeartTrialResult:
    choice: str
    success: bool
    roll: int
    chance: int
    description: str
    tension: int
    affected: tuple[str, ...]


NPCS = {
    "顾清玄": NpcTemplate("顾清玄", "男", "青云宗真传·温润剑修", 22, "筑基·后期", "青云宗", ("剑穗", "清茶", "山水画卷"), ("情蛊",), "剑有锋芒，道心却不必处处伤人。", 13),
    "云栖": NpcTemplate("云栖", "女", "天机坊市老板娘·聪慧狡黠", 25, "筑基·中期", "天机坊市", ("灵石匣", "奇闻玉简", "清茶"), ("赝品",), "买卖可以谈，真话却未必有价。", 15),
    "谢无咎": NpcTemplate("谢无咎", "男", "血魔宗少主·亦正亦邪", 24, "金丹·初期", "西漠", ("烈酒", "血玉", "奇闻玉简"), ("戒律经",), "你若肯以命相交，我便不会先负你。", 16),
    "白凝霜": NpcTemplate("白凝霜", "女", "北原雪族圣女·清冷孤高", 21, "金丹·中期", "北原", ("冰莲", "雪晶", "清茶"), ("烈酒",), "北原的雪很静，正适合听人说真话。", 17),
    "墨尘": NpcTemplate("墨尘", "男", "古妖山少主·化形妖族", 19, "筑基·后期", "古妖山", ("灵果", "烤肉", "山水画卷"), ("御兽环",), "本少主只是恰好路过，绝不是来找你的。", 12),
    "洛浅浅": NpcTemplate("洛浅浅", "女", "合欢宗弟子·魅惑多情", 20, "筑基·中期", "南疆", ("甜糕", "灵果", "奇闻玉简"), ("绝情丹",), "世人总说情之一字误道，我倒觉得无情才最误人。", 14),
}


class RelationshipEngine:
    NON_ROMANTIC_PATHS = {"纯友谊", "结义", "师徒", "宿敌", "旧缘", "故人"}

    @staticmethod
    def bond_label(affinity: int, partnered: bool = False, path: str = "") -> str:
        if partnered and affinity >= 100:
            return "生死相许"
        if partnered:
            return "道侣"
        if path:
            return path
        if affinity >= 80:
            return "可结道侣"
        if affinity >= 60:
            return "暧昧"
        if affinity >= 40:
            return "知己"
        if affinity >= 20:
            return "相识"
        return "陌生"

    @staticmethod
    def npc(name: str) -> NpcTemplate:
        if name not in NPCS:
            raise ValueError("未知人物。可互动：" + "、".join(NPCS))
        return NPCS[name]

    @classmethod
    def ensure_alive(cls, state: GameState, name: str) -> None:
        cls.npc(name)
        if state.npc_world.get(name, {}).get("alive") is False:
            raise ValueError(f"{name}已不在人世，只余生平可供追忆。")

    @classmethod
    def relation(cls, state: GameState, name: str) -> dict[str, object]:
        cls.npc(name)
        relation = state.npc_relations.setdefault(name, {"affinity": 0, "interactions": 0})
        return relation

    @classmethod
    def affinity(cls, state: GameState, name: str) -> int:
        return int(cls.relation(state, name).get("affinity", 0))

    @classmethod
    def add_affinity(cls, state: GameState, name: str, amount: int) -> int:
        relation = cls.relation(state, name)
        amount = DaoEngine.affinity_gain(state, amount)
        affinity = max(-100, min(120, int(relation.get("affinity", 0)) + amount))
        relation["affinity"] = affinity
        relation["interactions"] = int(relation.get("interactions", 0)) + 1
        cls.refresh_tension(state)
        return affinity

    @classmethod
    def romantic_names(cls, state: GameState) -> list[str]:
        names: list[str] = []
        for name in NPCS:
            relation = state.npc_relations.get(name, {})
            affinity = int(relation.get("affinity", 0))
            path = str(relation.get("path", ""))
            if name in state.dao_partners or (affinity >= 60 and path not in cls.NON_ROMANTIC_PATHS):
                names.append(name)
        return names

    @classmethod
    def refresh_tension(cls, state: GameState) -> int:
        romantic = cls.romantic_names(state)
        minimum = max(0, len(romantic) - 1) * 25 + max(0, len(state.dao_partners) - 1) * 15
        state.relationship_tension = max(state.relationship_tension, min(100, minimum))
        return state.relationship_tension

    @classmethod
    def begin_heart_trial(cls, state: GameState) -> tuple[list[str], int]:
        names = cls.romantic_names(state)
        cls.refresh_tension(state)
        if len(names) < 2 and state.relationship_tension < 30:
            raise ValueError("尘缘尚未形成情劫；至少需要两段暧昧或道侣关系。")
        state.pending_heart_trial = {"names": names, "started_turn": state.turn}
        state.phase = "heart_trial_choice"
        return names, state.relationship_tension

    @classmethod
    def resolve_heart_trial(cls, state: GameState, choice: str) -> HeartTrialResult:
        if state.phase != "heart_trial_choice" or not state.pending_heart_trial:
            raise ValueError("当前没有待化解的情劫。")
        aliases = {"坦诚": "坦诚相告", "暂避": "暂避锋芒", "问道": "一心问道"}
        choice = aliases.get(choice, choice)
        if choice not in {"坦诚相告", "暂避锋芒", "一心问道"}:
            raise ValueError("请选择：情劫 坦诚相告／情劫 暂避锋芒／情劫 一心问道。")
        names = [name for name in state.pending_heart_trial.get("names", []) if name in NPCS]
        roll = ProgressionEngine.deterministic_roll(state, f"heart-trial:{choice}:{state.turn}")
        chance = 100
        success = True

        if choice == "坦诚相告":
            chance = max(20, min(90, 45 + state.player.dao_heart * 2 - state.relationship_tension // 3))
            success = roll <= chance
            change = 3 if success else -8
            for name in names:
                relation = cls.relation(state, name)
                relation["affinity"] = max(-100, min(120, int(relation.get("affinity", 0)) + change))
            state.relationship_tension = max(0, state.relationship_tension - 25) if success else min(100, state.relationship_tension + 15)
            description = (
                "你没有回避彼此心意，坦然说清前因后果；众人虽各有思量，终究愿意再信你一次。"
                if success
                else "言语未能解开心结，旧日细节反而化作新刺，几段缘分同时蒙上阴影。"
            )
        elif choice == "暂避锋芒":
            for name in names:
                relation = cls.relation(state, name)
                relation["affinity"] = max(-100, int(relation.get("affinity", 0)) - 3)
            state.relationship_tension = max(0, state.relationship_tension - 12)
            description = "你暂离红尘纷扰，以时间平息争执；风波稍退，牵挂却也淡了几分。"
        else:
            former_partners = tuple(state.dao_partners)
            for name in names:
                relation = cls.relation(state, name)
                relation["affinity"] = max(-100, int(relation.get("affinity", 0)) - 20)
                relation["path"] = "旧缘"
            state.dao_partners.clear()
            state.player.dao_heart = min(30, state.player.dao_heart + 2)
            state.relationship_tension = 0
            description = (
                "你亲手斩断纠缠，将所有道侣之契归还天地；道心更坚，故人也从此成为旧缘。"
                if former_partners
                else "你收束所有暧昧，将心神重新放回长生大道；旧日温情从此只作前尘。"
            )

        state.phase = "playing"
        state.pending_heart_trial = {}
        event = f"情劫·{choice}：{description}"
        state.relationship_events.append(event)
        state.relationship_events = state.relationship_events[-20:]
        return HeartTrialResult(choice, success, roll, chance, description, state.relationship_tension, tuple(names))

    @classmethod
    def talk(cls, state: GameState, name: str) -> tuple[str, int]:
        cls.ensure_alive(state, name)
        npc = cls.npc(name)
        affinity = cls.add_affinity(state, name, 2)
        return npc.greeting, affinity

    @classmethod
    def gift(cls, state: GameState, name: str, item: str) -> tuple[int, int]:
        cls.ensure_alive(state, name)
        npc = cls.npc(name)
        if state.player.resources.get(item, 0) < 1:
            raise ValueError(f"乾坤袋中没有{item}。")
        state.player.resources[item] -= 1
        if state.player.resources[item] <= 0:
            state.player.resources.pop(item, None)
        change = 10 if item in npc.likes else (-5 if item in npc.dislikes else 3)
        before = cls.affinity(state, name)
        affinity = cls.add_affinity(state, name, change)
        return affinity - before, affinity

    @classmethod
    def discuss_dao(cls, state: GameState, name: str) -> tuple[bool, int, int, int]:
        cls.ensure_alive(state, name)
        npc = cls.npc(name)
        chance = max(10, min(95, 55 + (state.player.comprehension - npc.dao_difficulty) * 4 + (state.player.dao_heart - 10) * 2))
        roll = ProgressionEngine.deterministic_roll(state, f"discuss-dao:{name}:{state.turn}")
        success = roll <= chance
        change = 6 if success else 1
        affinity = cls.add_affinity(state, name, change)
        if success:
            gain = min(15, state.player.cultivation_required - state.player.cultivation)
            state.player.cultivation += max(0, gain)
        DaoEngine.gain_insight(state, 12 if success else 4, f"与{name}论道")
        return success, roll, chance, affinity

    @classmethod
    def become_partners(cls, state: GameState, name: str) -> int:
        cls.ensure_alive(state, name)
        cls.npc(name)
        affinity = cls.affinity(state, name)
        if affinity < 80:
            raise ValueError(f"与{name}好感尚未达到 80；当前 {affinity}。")
        if name not in state.dao_partners:
            state.dao_partners.append(name)
        cls.refresh_tension(state)
        return affinity

    @classmethod
    def dual_cultivate(cls, state: GameState, name: str) -> tuple[int, int]:
        cls.ensure_alive(state, name)
        if name not in state.dao_partners:
            raise ValueError(f"{name}尚不是你的道侣。")
        breakdown = ProgressionEngine.cultivation_gain(state, retreat=False)
        multiplier = state.player.modifiers.get("dual_cultivation_multiplier", 1.5) * DaoEngine.dual_cultivation_multiplier(state)
        remaining = state.player.cultivation_required - state.player.cultivation
        gain = min(remaining, max(1, round(breakdown.total * multiplier)))
        state.player.cultivation += max(0, gain)
        affinity = cls.add_affinity(state, name, 3)
        return max(0, gain), affinity
