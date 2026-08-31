from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .arts import SPELLS, TECHNIQUES
from .state import GameState


MASTERY_LABELS = ("初窥", "小成", "精通", "大成", "圆满")
MASTERY_THRESHOLDS = (0, 40, 120, 260, 480)
CULTIVATION_MULTIPLIERS = (1.0, 1.03, 1.07, 1.12, 1.18)
TECHNIQUE_COMBAT_MULTIPLIERS = (1.0, 1.02, 1.05, 1.09, 1.14)
SPELL_POWER_MULTIPLIERS = (1.0, 1.03, 1.07, 1.12, 1.18)
SPELL_COST_DISCOUNTS = (0.0, 0.0, 0.03, 0.06, 0.10)


@dataclass(frozen=True, slots=True)
class StudyResult:
    name: str
    kind: str
    gained: int
    old_level: int
    new_level: int
    spirit_cost: int

    @property
    def advanced(self) -> bool:
        return self.new_level > self.old_level


class ArtMasteryEngine:
    STUDY_SPIRIT_COST = 12

    @staticmethod
    def _kind(state: GameState, name: str) -> str:
        if name in state.player.known_techniques and name in TECHNIQUES:
            return "功法"
        if name in state.player.known_spells and name in SPELLS:
            return "法术"
        raise ValueError(f"尚未掌握道法：{name}")

    @staticmethod
    def _store(state: GameState, kind: str) -> dict[str, int]:
        return state.technique_mastery if kind == "功法" else state.spell_mastery

    @staticmethod
    def level_from_xp(xp: int) -> int:
        value = max(0, int(xp))
        return max(index for index, threshold in enumerate(MASTERY_THRESHOLDS) if value >= threshold)

    @classmethod
    def xp(cls, state: GameState, name: str, kind: str | None = None) -> int:
        resolved = kind or cls._kind(state, name)
        return max(0, min(MASTERY_THRESHOLDS[-1], int(cls._store(state, resolved).get(name, 0))))

    @classmethod
    def level(cls, state: GameState, name: str, kind: str | None = None) -> int:
        return cls.level_from_xp(cls.xp(state, name, kind))

    @classmethod
    def _record(cls, state: GameState, text: str) -> None:
        state.art_mastery_history.append(f"第 {state.turn} 回合｜{text}")
        state.art_mastery_history = state.art_mastery_history[-20:]

    @classmethod
    def gain(cls, state: GameState, name: str, amount: int, source: str) -> tuple[int, int, int]:
        kind = cls._kind(state, name)
        store = cls._store(state, kind)
        old_xp = cls.xp(state, name, kind)
        old_level = cls.level_from_xp(old_xp)
        new_xp = min(MASTERY_THRESHOLDS[-1], old_xp + max(0, int(amount)))
        store[name] = new_xp
        new_level = cls.level_from_xp(new_xp)
        if new_level > old_level:
            cls._record(state, f"{name}由{MASTERY_LABELS[old_level]}晋至{MASTERY_LABELS[new_level]}（{source}）")
        return new_xp - old_xp, old_level, new_level

    @classmethod
    def gain_cultivation(cls, state: GameState, months: int, retreat: bool) -> list[str]:
        player = state.player
        base = 6 + player.comprehension // 5 + (2 if retreat else 0)
        advances: list[str] = []
        gained, old, new = cls.gain(state, player.primary_technique, base * months, "闭关" if retreat else "吐纳")
        if gained and new > old:
            advances.append(f"{player.primary_technique}·{MASTERY_LABELS[new]}")
        for name in player.equipped_auxiliary_techniques:
            gained, old, new = cls.gain(state, name, max(1, base // 2) * months, "随修")
            if gained and new > old:
                advances.append(f"{name}·{MASTERY_LABELS[new]}")
        return advances

    @classmethod
    def gain_spell_cast(cls, state: GameState, name: str) -> str:
        amount = 5 + state.player.comprehension // 6
        _, old, new = cls.gain(state, name, amount, "实战施法")
        return f"{name}熟练度突破至{MASTERY_LABELS[new]}" if new > old else ""

    @classmethod
    def study(cls, state: GameState, name: str) -> StudyResult:
        if state.phase != "playing":
            raise ValueError("当前状态无法静心参研道法。")
        kind = cls._kind(state, name)
        if cls.xp(state, name, kind) >= MASTERY_THRESHOLDS[-1]:
            raise ValueError(f"{name}已臻圆满，无需继续参研。")
        if state.player.spirit < cls.STUDY_SPIRIT_COST:
            raise ValueError(f"灵力不足：参研需要 {cls.STUDY_SPIRIT_COST} 点灵力。")
        state.player.spirit -= cls.STUDY_SPIRIT_COST
        amount = 14 + state.player.comprehension // 2
        gained, old, new = cls.gain(state, name, amount, "专心参研")
        cls._record(state, f"参研{name}，熟练度 +{gained}")
        return StudyResult(name, kind, gained, old, new, cls.STUDY_SPIRIT_COST)

    @classmethod
    def cultivation_multiplier(cls, state: GameState, name: str) -> float:
        return CULTIVATION_MULTIPLIERS[cls.level(state, name, "功法")]

    @classmethod
    def technique_combat_multiplier(cls, state: GameState, name: str) -> float:
        return TECHNIQUE_COMBAT_MULTIPLIERS[cls.level(state, name, "功法")]

    @classmethod
    def spell_power(cls, state: GameState, name: str, base: float) -> float:
        return base * SPELL_POWER_MULTIPLIERS[cls.level(state, name, "法术")]

    @classmethod
    def spell_cost(cls, state: GameState, name: str, base: int) -> int:
        discount = SPELL_COST_DISCOUNTS[cls.level(state, name, "法术")]
        return max(1, round(base * (1 - discount)))

    @classmethod
    def _progress(cls, xp: int) -> tuple[int, int, int]:
        level = cls.level_from_xp(xp)
        if level == len(MASTERY_LABELS) - 1:
            return 100, MASTERY_THRESHOLDS[-1], MASTERY_THRESHOLDS[-1]
        start, end = MASTERY_THRESHOLDS[level], MASTERY_THRESHOLDS[level + 1]
        return round((xp - start) / (end - start) * 100), start, end

    @classmethod
    def _card(cls, state: GameState, name: str, kind: str) -> dict[str, Any]:
        player = state.player
        xp = cls.xp(state, name, kind)
        level = cls.level_from_xp(xp)
        progress, _, next_xp = cls._progress(xp)
        maxed = level == len(MASTERY_LABELS) - 1
        can_study = state.phase == "playing" and not maxed and player.spirit >= cls.STUDY_SPIRIT_COST
        if maxed:
            reason = "已臻圆满"
        elif state.phase != "playing":
            reason = "当前状态不可参研"
        elif player.spirit < cls.STUDY_SPIRIT_COST:
            reason = f"需要 {cls.STUDY_SPIRIT_COST} 灵力"
        else:
            reason = ""
        if kind == "功法":
            definition = TECHNIQUES[name]
            role = "主修" if name == player.primary_technique else "辅修" if name in player.equipped_auxiliary_techniques else "已悟"
            effect = f"吐纳 ×{CULTIVATION_MULTIPLIERS[level]:.2f}｜攻防 ×{TECHNIQUE_COMBAT_MULTIPLIERS[level]:.2f}"
            next_effect = "已至极境" if maxed else f"下境：吐纳 ×{CULTIVATION_MULTIPLIERS[level + 1]:.2f}｜攻防 ×{TECHNIQUE_COMBAT_MULTIPLIERS[level + 1]:.2f}"
            element = ""
            cost = 0
        else:
            definition = SPELLS[name]
            role = "已装备" if name == player.equipped_spell else "已悟"
            effective_cost = cls.spell_cost(state, name, definition.spirit_cost)
            effect = f"威力 ×{SPELL_POWER_MULTIPLIERS[level]:.2f}｜灵力 {effective_cost}"
            next_effect = "已至极境" if maxed else f"下境：威力 ×{SPELL_POWER_MULTIPLIERS[level + 1]:.2f}｜灵力 {max(1, round(definition.spirit_cost * (1 - SPELL_COST_DISCOUNTS[level + 1])))}"
            element = definition.element
            cost = effective_cost
        return {
            "name": name,
            "kind": kind,
            "grade": definition.grade,
            "element": element,
            "description": definition.description,
            "role": role,
            "xp": xp,
            "level": level,
            "level_label": MASTERY_LABELS[level],
            "progress": progress,
            "next_xp": next_xp,
            "effect": effect,
            "next_effect": next_effect,
            "spirit_cost": cost,
            "can_study": can_study,
            "disabled_reason": reason,
            "study_action": f"参研道法 {name}",
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        techniques = [cls._card(state, name, "功法") for name in state.player.known_techniques if name in TECHNIQUES]
        spells = [cls._card(state, name, "法术") for name in state.player.known_spells if name in SPELLS]
        techniques.sort(key=lambda item: (item["role"] != "主修", item["role"] != "辅修", item["name"]))
        spells.sort(key=lambda item: (item["role"] != "已装备", item["name"]))
        primary = next((item for item in techniques if item["role"] == "主修"), techniques[0] if techniques else {})
        equipped_spell = next((item for item in spells if item["role"] == "已装备"), spells[0] if spells else {})
        return {
            "primary": primary,
            "equipped_spell": equipped_spell,
            "techniques": techniques,
            "spells": spells,
            "known_count": len(techniques) + len(spells),
            "mastered_count": sum(item["level_label"] == "圆满" for item in techniques + spells),
            "spirit": state.player.spirit,
            "spirit_max": state.player.spirit_max,
            "comprehension": state.player.comprehension,
            "study_cost": cls.STUDY_SPIRIT_COST,
            "history": list(reversed(state.art_mastery_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        lines = ["【道法谱 · 熟练境界】"]
        for item in snapshot["techniques"] + snapshot["spells"]:
            lines.append(f"{item['kind']}｜{item['name']}｜{item['grade']}｜{item['role']}｜{item['level_label']} {item['xp']}/{item['next_xp']}｜{item['effect']}")
        lines.append("指令：参研道法 [名称]／参悟 [名称]／装备功法 [名称]／辅修功法 [名称] [1或2]／装备法术 [名称]")
        return "\n".join(lines)
