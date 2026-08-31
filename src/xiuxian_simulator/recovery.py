from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import GameState


SEVERITY_LABELS = ("", "轻微", "沉重", "危重")


@dataclass(frozen=True, slots=True)
class InjuryDefinition:
    id: str
    name: str
    mark: str
    description: str
    base_months: int
    cultivation_penalty: tuple[float, float, float]
    combat_penalty: tuple[float, float, float]
    damage_taken: tuple[float, float, float]
    speed_penalty: tuple[int, int, int]


INJURIES: dict[str, InjuryDefinition] = {
    "flesh": InjuryDefinition(
        "flesh", "筋骨外伤", "伤", "斗法、行旅或险地留下的筋骨创伤。",
        2, (0.96, 0.91, 0.84), (0.97, 0.92, 0.84), (1.04, 1.10, 1.18), (1, 2, 4),
    ),
    "meridian": InjuryDefinition(
        "meridian", "经脉受损", "脉", "灵力反噬伤及经络，吐纳与施法都会受阻。",
        3, (0.91, 0.82, 0.68), (0.95, 0.88, 0.76), (1.03, 1.08, 1.14), (0, 1, 2),
    ),
    "heart": InjuryDefinition(
        "heart", "心魔侵蚀", "心", "道心蒙尘，强行修炼或破境风险极高。",
        4, (0.93, 0.84, 0.72), (0.97, 0.92, 0.84), (1.02, 1.06, 1.10), (0, 0, 1),
    ),
    "foundation": InjuryDefinition(
        "foundation", "道基暗伤", "基", "大境界失败留下的暗伤，必须长期调养。",
        6, (0.86, 0.72, 0.56), (0.93, 0.84, 0.72), (1.05, 1.12, 1.20), (1, 2, 3),
    ),
}


LEGACY_CONDITIONS = (
    (("暗伤",), "foundation", 2),
    (("走火入魔", "心魔"), "heart", 2),
    (("反噬",), "meridian", 2),
    (("重伤", "负伤", "战败", "受创"), "flesh", 2),
)


class RecoveryEngine:
    @staticmethod
    def _severity(record: dict[str, Any]) -> int:
        """Normalize old or hand-edited save data without mutating it."""
        return max(1, min(3, int(record.get("severity", 1))))

    @staticmethod
    def _record(state: GameState, text: str) -> None:
        state.injury_history.append(f"第 {state.turn} 回合｜{text}")
        state.injury_history = state.injury_history[-30:]

    @staticmethod
    def _legacy(state: GameState) -> tuple[str, int] | None:
        condition = state.player.condition
        if not condition or condition == "无" or "陨落" in condition or "寿元耗尽" in condition:
            return None
        for words, kind, severity in LEGACY_CONDITIONS:
            if any(word in condition for word in words):
                return kind, severity
        return None

    @classmethod
    def capture_legacy(cls, state: GameState, source: str = "旧有伤势") -> bool:
        legacy = cls._legacy(state)
        if not legacy:
            return False
        kind, severity = legacy
        if kind in state.injuries:
            return False
        cls.register(state, kind, severity, source, replace_condition=False)
        cls.sync_condition(state)
        return True

    @classmethod
    def register(
        cls,
        state: GameState,
        kind: str,
        severity: int,
        source: str,
        *,
        replace_condition: bool = True,
    ) -> dict[str, Any]:
        if kind not in INJURIES:
            raise ValueError(f"未知伤势类型：{kind}")
        if state.phase == "ended" or state.player.health <= 0:
            return {}
        definition = INJURIES[kind]
        severity = max(1, min(3, int(severity)))
        existing = state.injuries.get(kind, {})
        merged_severity = max(severity, cls._severity(existing)) if existing else severity
        months = max(
            definition.base_months * merged_severity,
            int(existing.get("months_left", 0)),
        )
        record = {
            "kind": kind,
            "severity": merged_severity,
            "months_left": months,
            "source": source,
            "acquired_turn": int(existing.get("acquired_turn", state.turn)),
        }
        state.injuries[kind] = record
        cls._record(state, f"因{source}留下{SEVERITY_LABELS[merged_severity]}{definition.name}，预计调养 {months} 月")
        if replace_condition:
            cls.sync_condition(state)
        return record

    @classmethod
    def active(cls, state: GameState) -> list[tuple[InjuryDefinition, dict[str, Any]]]:
        active: list[tuple[InjuryDefinition, dict[str, Any]]] = []
        for kind, record in state.injuries.items():
            definition = INJURIES.get(kind)
            if definition and int(record.get("months_left", 0)) > 0:
                active.append((definition, record))
        if not active:
            legacy = cls._legacy(state)
            if legacy:
                kind, severity = legacy
                definition = INJURIES[kind]
                active.append((definition, {
                    "kind": kind,
                    "severity": severity,
                    "months_left": definition.base_months * severity,
                    "source": state.player.condition,
                    "acquired_turn": state.turn,
                    "legacy": True,
                }))
        return sorted(active, key=lambda item: (-cls._severity(item[1]), item[0].name))

    @classmethod
    def has_active(cls, state: GameState) -> bool:
        return bool(cls.active(state))

    @classmethod
    def sync_condition(cls, state: GameState) -> None:
        if state.phase == "ended":
            return
        names = []
        for kind, record in state.injuries.items():
            definition = INJURIES.get(kind)
            if definition and int(record.get("months_left", 0)) > 0:
                severity = max(1, min(3, int(record.get("severity", 1))))
                names.append(f"{SEVERITY_LABELS[severity]}{definition.name}")
        state.player.condition = "、".join(names) if names else "无"

    @classmethod
    def tick_month(cls, state: GameState) -> list[str]:
        if state.phase == "ended":
            return []
        cls.capture_legacy(state)
        events: list[str] = []
        for kind, record in list(state.injuries.items()):
            record["months_left"] = max(0, int(record.get("months_left", 0)) - 1)
            if int(record["months_left"]) <= 0:
                definition = INJURIES.get(kind)
                state.injuries.pop(kind, None)
                if definition:
                    message = f"{definition.name}已随岁月痊愈"
                    events.append(message)
                    cls._record(state, message)
        if state.injuries and state.player.health < state.player.health_max:
            recovered = min(3 + state.player.realm_index, state.player.health_max - state.player.health)
            state.player.health += recovered
        cls.sync_condition(state)
        return events

    @classmethod
    def treat(cls, state: GameState, potency: int, source: str) -> str:
        cls.capture_legacy(state)
        active = cls.active(state)
        if not active:
            return "没有需要处理的持续伤势"
        definition, record = active[0]
        before = int(record.get("months_left", 0))
        record["months_left"] = max(0, before - max(1, potency))
        if int(record["months_left"]) <= 0:
            state.injuries.pop(definition.id, None)
            result = f"{definition.name}痊愈"
        else:
            result = f"{definition.name}调养期缩短 {before - int(record['months_left'])} 月"
        cls._record(state, f"{source}：{result}")
        cls.sync_condition(state)
        return result

    @classmethod
    def rest(cls, state: GameState) -> dict[str, Any]:
        cls.capture_legacy(state)
        if not cls.has_active(state) and state.player.health >= state.player.health_max and state.player.spirit >= state.player.spirit_max:
            raise ValueError("气血、灵力与伤势均已安定，无需专门静养。")
        health_before = state.player.health
        spirit_before = state.player.spirit
        health_gain = 22 + state.player.realm_index * 4
        spirit_gain = 18 + state.player.realm_index * 3
        state.player.health = min(state.player.health_max, state.player.health + health_gain)
        state.player.spirit = min(state.player.spirit_max, state.player.spirit + spirit_gain)
        room = state.cave_facilities.get("静室", 0)
        treatment = cls.treat(state, 1 + room, "闭门静养") if cls.has_active(state) else "调匀气血灵力"
        return {
            "health": state.player.health - health_before,
            "spirit": state.player.spirit - spirit_before,
            "treatment": treatment,
            "room_bonus": room,
        }

    @classmethod
    def cultivation_multiplier(cls, state: GameState) -> float:
        multiplier = 1.0
        for definition, record in cls.active(state):
            multiplier *= definition.cultivation_penalty[cls._severity(record) - 1]
        return max(0.35, multiplier)

    @classmethod
    def combat_multiplier(cls, state: GameState) -> float:
        multiplier = 1.0
        for definition, record in cls.active(state):
            multiplier *= definition.combat_penalty[cls._severity(record) - 1]
        return max(0.45, multiplier)

    @classmethod
    def damage_taken_multiplier(cls, state: GameState) -> float:
        multiplier = 1.0
        for definition, record in cls.active(state):
            multiplier *= definition.damage_taken[cls._severity(record) - 1]
        return min(1.8, multiplier)

    @classmethod
    def speed_penalty(cls, state: GameState) -> int:
        return sum(definition.speed_penalty[cls._severity(record) - 1] for definition, record in cls.active(state))

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        entries = []
        for definition, record in cls.active(state):
            severity = cls._severity(record)
            entries.append({
                "id": definition.id,
                "name": definition.name,
                "mark": definition.mark,
                "severity": severity,
                "severity_label": SEVERITY_LABELS[severity],
                "months_left": int(record.get("months_left", 0)),
                "source": str(record.get("source", "来历不明")),
                "description": definition.description,
                "effects": [
                    f"吐纳 ×{definition.cultivation_penalty[severity - 1]:.2f}",
                    f"攻势 ×{definition.combat_penalty[severity - 1]:.2f}",
                    f"受伤 ×{definition.damage_taken[severity - 1]:.2f}",
                    (
                        f"遁速 -{definition.speed_penalty[severity - 1]}"
                        if definition.speed_penalty[severity - 1]
                        else "遁速无碍"
                    ),
                ],
            })
        cultivation = cls.cultivation_multiplier(state)
        combat = cls.combat_multiplier(state)
        damage = cls.damage_taken_multiplier(state)
        speed = cls.speed_penalty(state)
        condition = "、".join(f"{entry['severity_label']}{entry['name']}" for entry in entries)
        return {
            "active": bool(entries),
            "count": len(entries),
            "condition": condition or state.player.condition,
            "health": state.player.health,
            "health_max": state.player.health_max,
            "spirit": state.player.spirit,
            "spirit_max": state.player.spirit_max,
            "injuries": entries,
            "penalties": {
                "cultivation": cultivation,
                "combat": combat,
                "damage_taken": damage,
                "speed": speed,
            },
            "can_rest": state.phase == "playing",
            "rest_reason": "" if state.phase == "playing" else "当前状态无法静养",
            "rest_action": "静养",
            "has_healing_pill": state.player.resources.get("疗伤丹", 0) > 0,
            "pill_action": "使用 疗伤丹",
            "history": list(reversed(state.injury_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["active"]:
            return "【伤势卷宗】气血安定，经脉无碍，当前没有持续伤势。"
        lines = ["【伤势卷宗 · 调养有时】"]
        for injury in snapshot["injuries"]:
            lines.append(
                f"{injury['severity_label']}{injury['name']}｜尚需 {injury['months_left']} 月｜"
                f"{'、'.join(injury['effects'])}｜缘起：{injury['source']}"
            )
        lines.append("指令：静养／使用 疗伤丹／洞府调息；伤势未愈时不可突破大境界。")
        return "\n".join(lines)
