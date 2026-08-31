from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import GameState


@dataclass(frozen=True, slots=True)
class LegacyDefinition:
    id: str
    name: str
    mark: str
    summary: str
    effect: str


LEGACIES: dict[str, LegacyDefinition] = {
    "tempered-body": LegacyDefinition(
        "tempered-body",
        "百炼余骨",
        "骨",
        "前世所受苦厄沉入根骨，下一世更能承受漫漫道途。",
        "气血上限 +12，寿元 +6",
    ),
    "lucid-seed": LegacyDefinition(
        "lucid-seed",
        "宿慧道种",
        "悟",
        "前世未尽的思索凝成一粒道种，生而更易明心见性。",
        "悟性 +2，道心 +1，初始感悟 +10",
    ),
    "hidden-hoard": LegacyDefinition(
        "hidden-hoard",
        "袖里余藏",
        "藏",
        "一只无名乾坤袋跨过轮回，留下足以重新起步的资粮。",
        "初始灵石 +180，聚气丹 +2",
    ),
    "world-vow": LegacyDefinition(
        "world-vow",
        "九州余愿",
        "愿",
        "曾经撼动九州的愿力并未消散，新生仍会被山河记得。",
        "声望 +8，五域声望 +5，悟道点 +1",
    ),
}


RANKS = (
    (1400, "近仙传说"),
    (900, "当世名宿"),
    (500, "九州俊彦"),
    (200, "一域留名"),
    (0, "凡尘留痕"),
)


class LegacyEngine:
    @staticmethod
    def score(state: GameState) -> int:
        player = state.player
        return max(
            0,
            state.turn
            + player.realm_index * 260
            + player.stage_index * 35
            + state.journey_points * 3
            + len(state.completed_commissions) * 28
            + len(state.story_completed) * 85
            + sum(int(level) for level in player.dao_levels.values()) * 32
            + len(state.visited_regions) * 22
            + len(state.spirit_beasts) * 35
            + len(state.formation_arrays) * 24
            + len(state.sect_library_claims) * 26
            + int(state.founded_sect.get("level", 0)) * 80
            + len(state.sect_disciples) * 20
            + int(state.founded_sect.get("renown", 0))
            + max(0, player.reputation)
            + max(0, state.trade_profit // 20),
        )

    @classmethod
    def rank(cls, score: int) -> str:
        return next(label for threshold, label in RANKS if score >= threshold)

    @staticmethod
    def cause(state: GameState) -> str:
        player = state.player
        condition = player.condition.strip()
        if "寿元" in condition or player.age >= player.lifespan:
            return "寿元尽头，安然坐化"
        if condition and condition != "无":
            return condition
        for entry in reversed(state.history):
            if any(word in entry for word in ("陨落", "坐化", "寿元耗尽", "道途止于")):
                return entry.split("｜")[-1]
        return "道途于无名处落幕"

    @classmethod
    def option_ids(cls, state: GameState) -> list[str]:
        third = "world-vow" if state.story_ending or len(state.story_completed) >= 4 else "hidden-hoard"
        return ["tempered-body", "lucid-seed", third]

    @classmethod
    def chronicle(cls, state: GameState) -> dict[str, Any]:
        player = state.player
        score = cls.score(state)
        known_relations = sum(
            1
            for relation in state.npc_relations.values()
            if int(relation.get("affinity", 0)) != 0 or relation.get("path")
        )
        highlights: list[str] = []
        if state.story_ending:
            highlights.append(f"灵潮终局：{state.story_ending.get('title', '因果落定')}")
        elif state.story_completed:
            highlights.append(f"灵潮因果推进 {len(state.story_completed)}/6")
        if state.bonded_artifact:
            highlights.append(f"本命法宝：{state.bonded_artifact}")
        if state.founded_sect.get("name"):
            highlights.append(f"开宗立派：{state.founded_sect['name']}")
        if state.dao_partners:
            highlights.append(f"道侣：{'、'.join(state.dao_partners[:2])}")
        if state.spirit_beasts:
            highlights.append(f"灵兽相随 {len(state.spirit_beasts)} 只")
        if not highlights:
            highlights.append(f"在{player.location}留下最后一段行迹")
        return {
            "life": state.life_number,
            "name": player.name,
            "dao_name": player.dao_name,
            "realm": player.realm,
            "sect": player.sect,
            "age": player.age,
            "lifespan": player.lifespan,
            "year": state.calendar_year,
            "month": state.month,
            "turn": state.turn,
            "cause": cls.cause(state),
            "score": score,
            "rank": cls.rank(score),
            "location": player.location,
            "ending": str(state.story_ending.get("title", "")),
            "highlights": highlights[:4],
            "metrics": {
                "regions": len(set(state.visited_regions)),
                "story": len(state.story_completed),
                "relations": known_relations,
                "commissions": len(state.completed_commissions),
                "dao_levels": sum(int(level) for level in player.dao_levels.values()),
                "beasts": len(state.spirit_beasts),
            },
            "selected_legacy": state.legacy_choice,
            "epilogue": (
                f"{player.dao_name or player.name}止步于{player.realm}，但这段{cls.rank(score)}的仙途并未彻底消散。"
                "从三道轮回余痕中亲自择一，下一世会继承有限而真实的起步优势。"
            ),
        }

    @classmethod
    def ensure_ending(cls, state: GameState) -> bool:
        if state.phase != "ended":
            return False
        existing = next((item for item in state.past_lives if int(item.get("life", 0)) == state.life_number), None)
        if existing is None:
            state.past_lives.append(cls.chronicle(state))
            state.past_lives = state.past_lives[-12:]
            state.legacy_options = cls.option_ids(state)
            return True
        if not state.legacy_options and not state.legacy_choice:
            state.legacy_options = cls.option_ids(state)
        return False

    @classmethod
    def choose(cls, state: GameState, legacy_id: str) -> LegacyDefinition:
        if state.phase != "ended":
            raise ValueError("只有本世落幕后，才能铭刻轮回传承。")
        cls.ensure_ending(state)
        if legacy_id not in state.legacy_options or legacy_id not in LEGACIES:
            raise ValueError("这道传承不在本世可选余痕之中。")
        state.legacy_choice = legacy_id
        for item in reversed(state.past_lives):
            if int(item.get("life", 0)) == state.life_number:
                item["selected_legacy"] = legacy_id
                break
        return LEGACIES[legacy_id]

    @classmethod
    def apply_inheritance(cls, state: GameState) -> str:
        if state.legacy_applied or not state.active_legacy:
            return ""
        definition = LEGACIES.get(state.active_legacy)
        if definition is None:
            state.legacy_applied = True
            return ""
        player = state.player
        if definition.id == "tempered-body":
            player.health_max += 12
            player.health = player.health_max
            player.lifespan += 6
        elif definition.id == "lucid-seed":
            player.comprehension += 2
            player.dao_heart += 1
            player.dao_insight += 10
        elif definition.id == "hidden-hoard":
            player.spirit_stones += 180
            player.resources["聚气丹"] = player.resources.get("聚气丹", 0) + 2
        elif definition.id == "world-vow":
            player.reputation += 8
            player.dao_points += 1
            for region in state.regional_reputation:
                state.regional_reputation[region] += 5
        player.tags.append(f"轮回道痕·{definition.name}")
        player.character_notes += f"；轮回传承：{definition.name}"
        state.legacy_applied = True
        return f"轮回传承“{definition.name}”苏醒：{definition.effect}"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        latest = next(
            (item for item in reversed(state.past_lives) if int(item.get("life", 0)) == state.life_number),
            None,
        )
        if state.phase == "ended" and latest is None:
            latest = cls.chronicle(state)
        option_ids = state.legacy_options or (cls.option_ids(state) if state.phase == "ended" else [])
        options = []
        for legacy_id in option_ids:
            definition = LEGACIES.get(legacy_id)
            if definition:
                options.append({
                    "id": definition.id,
                    "name": definition.name,
                    "mark": definition.mark,
                    "summary": definition.summary,
                    "effect": definition.effect,
                    "selected": state.legacy_choice == definition.id,
                    "action": f"铭刻传承 {definition.id}",
                })
        active = LEGACIES.get(state.active_legacy)
        return {
            "ended": state.phase == "ended",
            "life_number": state.life_number,
            "completed_lives": max(len(state.past_lives), 1 if state.phase == "ended" and latest else 0),
            "latest": latest or {},
            "options": options,
            "selected": state.legacy_choice,
            "can_begin_next": state.phase == "ended" and bool(state.legacy_choice),
            "begin_action": "开始游戏",
            "active_legacy": ({
                "id": active.id,
                "name": active.name,
                "mark": active.mark,
                "summary": active.summary,
                "effect": active.effect,
            } if active else {}),
            "past_lives": list(reversed(state.past_lives[-6:])),
        }

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        snapshot = cls.snapshot(state)
        if not snapshot["ended"]:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        selected = LEGACIES.get(str(snapshot["selected"]))
        if selected:
            return {
                "eyebrow": "轮回已定",
                "title": f"{selected.name}已经铭入神魂",
                "hint": selected.effect,
                "exclusive": True,
                "choices": [{
                    "label": "启封下一世",
                    "action": "开始游戏",
                    "description": "保留历世评传，并带着所选道痕重新创角。",
                    "tone": "primary",
                }],
            }
        return {
            "eyebrow": "本世落幕",
            "title": "择一道痕，留给下一世",
            "hint": "传承只影响下一世的起步，不会抹去失败、死亡或数值代价。",
            "exclusive": True,
            "choices": [
                {
                    "label": option["name"],
                    "action": option["action"],
                    "summary": option["effect"],
                    "description": option["summary"],
                    "tone": "primary" if index == 0 else "quiet",
                }
                for index, option in enumerate(snapshot["options"])
            ],
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        latest = snapshot["latest"]
        if not latest:
            active = snapshot["active_legacy"]
            return "【轮回道痕】" + (f"{active['name']}｜{active['effect']}" if active else "尚无前世评传。")
        options = "\n".join(f"{item['name']}｜{item['effect']}｜铭刻传承 {item['id']}" for item in snapshot["options"])
        selected = LEGACIES.get(str(snapshot["selected"]))
        return (
            f"【第 {latest['life']} 世 · 仙途评传】\n"
            f"{latest['name']}（{latest['dao_name']}）｜{latest['realm']}｜享年 {latest['age']}｜{latest['rank']} {latest['score']} 分\n"
            f"落幕：{latest['cause']}\n{latest['epilogue']}\n\n"
            + (f"已选：{selected.name}｜{selected.effect}\n输入“开始游戏”启封下一世。" if selected else f"【轮回余痕】\n{options}")
        )
