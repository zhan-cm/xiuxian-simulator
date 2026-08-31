from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dao import DaoEngine
from .progression import ProgressionEngine, REALMS
from .state import GameState


@dataclass(frozen=True, slots=True)
class FormationTemplate:
    id: str
    name: str
    mark: str
    element: str
    role: str
    minimum_realm: int
    base_chance: int
    spirit_cost: int
    integrity_cost: int
    ingredients: dict[str, int]
    summary: str
    effect: str


FORMATIONS: dict[str, FormationTemplate] = {
    "ember-slaying": FormationTemplate(
        "ember-slaying", "赤阳焚敌阵", "焚", "火", "杀阵", 0, 78, 16, 25,
        {"灵铁": 2, "符纸": 2}, "以赤阳阵纹汇聚攻伐灵机，适合正面破敌。", "催动后造成火行阵法伤害。",
    ),
    "stone-ward": FormationTemplate(
        "stone-ward", "玄土结界阵", "镇", "土", "结界", 0, 82, 12, 20,
        {"灵铁": 3}, "阵旗相连如山岳合围，可在危局中稳住阵脚。", "催动后守护本轮，并降低敌方攻势。",
    ),
    "wind-binding": FormationTemplate(
        "wind-binding", "缚风困灵阵", "缚", "木", "困敌", 1, 68, 14, 22,
        {"符纸": 3, "妖兽材料": 1}, "借风木生息封锁腾挪，使敌手难以脱离阵眼。", "催动后束缚敌人，并令下一击必中。",
    ),
    "spirit-gathering": FormationTemplate(
        "spirit-gathering", "青木聚灵阵", "聚", "木", "聚灵", 1, 72, 10, 18,
        {"灵铁": 2, "灵药": 3}, "引四方灵气归于阵心，兼顾修行与临阵续航。", "装配时提高修炼收益；催动可回复灵力。",
    ),
    "five-cycle": FormationTemplate(
        "five-cycle", "五行轮转阵", "轮", "五行", "万象", 2, 58, 20, 30,
        {"灵铁": 4, "五行灵珠": 1, "道韵": 1}, "五行生克自行轮转，能因敌势变化而改换阵眼。", "自动取克制之势发动高额阵法伤害。",
    ),
}


class FormationEngine:
    MAX_INTEGRITY = 100

    @staticmethod
    def template(formation_id: str) -> FormationTemplate:
        try:
            return FORMATIONS[formation_id]
        except KeyError as exc:
            raise ValueError("未知阵图。") from exc

    @classmethod
    def owned_id_by_name(cls, state: GameState, name: str) -> str:
        for formation_id in state.formation_arrays:
            if formation_id == name or cls.template(formation_id).name == name:
                return formation_id
        raise ValueError("尚未炼成这座阵盘。")

    @classmethod
    def active(cls, state: GameState) -> tuple[FormationTemplate, dict[str, Any]] | None:
        formation_id = state.active_formation
        formation = state.formation_arrays.get(formation_id)
        if not formation_id or formation is None:
            return None
        return cls.template(formation_id), formation

    @staticmethod
    def _missing(state: GameState, ingredients: dict[str, int]) -> list[str]:
        return [
            f"{name}×{count}"
            for name, count in ingredients.items()
            if state.player.resources.get(name, 0) < count
        ]

    @classmethod
    def build_chance(cls, state: GameState, formation_id: str) -> int:
        template = cls.template(formation_id)
        skill = int(state.player.craft_skills.get("阵法", 0))
        facility = int(state.cave_facilities.get("聚灵阵", 0))
        return max(
            12,
            min(
                98,
                template.base_chance
                + (state.player.spirit_sense - 10) * 2
                + skill * 7
                + facility * 4
                + DaoEngine.level(state, "阵道") * 6,
            ),
        )

    @classmethod
    def eligibility(cls, state: GameState, formation_id: str) -> tuple[bool, str]:
        template = cls.template(formation_id)
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if formation_id in state.formation_arrays:
            return False, "阵图已经炼成"
        if state.player.realm_index < template.minimum_realm:
            return False, f"至少需要{REALMS[template.minimum_realm]}境"
        missing = cls._missing(state, template.ingredients)
        if missing:
            return False, "缺少 " + "、".join(missing)
        return True, ""

    @classmethod
    def _consume(cls, state: GameState, ingredients: dict[str, int]) -> None:
        missing = cls._missing(state, ingredients)
        if missing:
            raise ValueError("阵材不足：" + "、".join(missing))
        for name, count in ingredients.items():
            state.player.resources[name] -= count
            if state.player.resources[name] <= 0:
                state.player.resources.pop(name, None)

    @classmethod
    def record(cls, state: GameState, text: str) -> None:
        state.formation_history.append(f"第 {state.turn} 回合｜{text}")
        state.formation_history = state.formation_history[-30:]

    @classmethod
    def build(cls, state: GameState, name: str) -> dict[str, Any]:
        formation_id = next((key for key, item in FORMATIONS.items() if key == name or item.name == name), "")
        if not formation_id:
            raise ValueError("未知阵图。可研习：" + "、".join(item.name for item in FORMATIONS.values()))
        eligible, reason = cls.eligibility(state, formation_id)
        if not eligible:
            raise ValueError(reason)
        template = cls.template(formation_id)
        cls._consume(state, template.ingredients)
        chance = cls.build_chance(state, formation_id)
        roll = ProgressionEngine.deterministic_roll(state, f"formation-build:{formation_id}:{state.turn}")
        success = roll <= chance
        leveled_up = False
        if success:
            state.formation_arrays[formation_id] = {
                "integrity": cls.MAX_INTEGRITY,
                "built_turn": state.turn,
                "activations": 0,
            }
            if not state.active_formation:
                state.active_formation = formation_id
            successes = int(state.player.craft_successes.get("阵法", 0)) + 1
            state.player.craft_successes["阵法"] = successes
            old_level = int(state.player.craft_skills.get("阵法", 0))
            new_level = min(4, successes // 2)
            if new_level > old_level:
                state.player.craft_skills["阵法"] = new_level
                leveled_up = True
            cls.record(state, f"炼成{template.name}（{roll}/{chance}）")
        else:
            cls.record(state, f"炼制{template.name}失败（{roll}/{chance}），阵材损毁")
        return {
            "success": success,
            "name": template.name,
            "roll": roll,
            "chance": chance,
            "leveled_up": leveled_up,
        }

    @classmethod
    def deploy(cls, state: GameState, name: str) -> str:
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择，再更换阵盘。")
        formation_id = cls.owned_id_by_name(state, name)
        state.active_formation = formation_id
        template = cls.template(formation_id)
        cls.record(state, f"装配{template.name}")
        return template.name

    @classmethod
    def repair(cls, state: GameState, name: str) -> dict[str, Any]:
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择，再修复阵盘。")
        formation_id = cls.owned_id_by_name(state, name)
        formation = state.formation_arrays[formation_id]
        before = int(formation.get("integrity", cls.MAX_INTEGRITY))
        if before >= cls.MAX_INTEGRITY:
            raise ValueError("阵基完整，无需修复。")
        if state.player.resources.get("灵铁", 0) < 1:
            raise ValueError("修复阵盘需要 灵铁×1。")
        state.player.resources["灵铁"] -= 1
        if state.player.resources["灵铁"] <= 0:
            state.player.resources.pop("灵铁", None)
        formation["integrity"] = min(cls.MAX_INTEGRITY, before + 35)
        gain = int(formation["integrity"]) - before
        template = cls.template(formation_id)
        cls.record(state, f"修复{template.name}，阵基 +{gain}")
        return {"name": template.name, "integrity_gain": gain}

    @classmethod
    def cultivation_multiplier(cls, state: GameState) -> float:
        active = cls.active(state)
        if not active or active[0].role != "聚灵" or int(active[1].get("integrity", 0)) <= 0:
            return 1.0
        return 1.0 + 0.05 + int(state.player.craft_skills.get("阵法", 0)) * 0.02 + DaoEngine.level(state, "阵道") * 0.02

    @classmethod
    def activation_cost(cls, state: GameState, template: FormationTemplate) -> tuple[int, int]:
        dao_level = DaoEngine.level(state, "阵道")
        return max(6, template.spirit_cost - dao_level * 2), max(10, template.integrity_cost - dao_level * 2)

    @classmethod
    def activate_combat(cls, state: GameState) -> str:
        if state.phase != "combat" or not state.combat:
            raise ValueError("只有战斗中才能催动阵法。")
        if state.combat.get("formation_used"):
            raise ValueError("本场战斗已经催动过阵法。")
        active = cls.active(state)
        if not active:
            raise ValueError("当前没有装配阵盘。")
        template, formation = active
        spirit_cost, integrity_cost = cls.activation_cost(state, template)
        integrity = int(formation.get("integrity", 0))
        if integrity < integrity_cost:
            raise ValueError("阵基残破，需要先用灵铁修复。")
        if state.player.spirit < spirit_cost:
            raise ValueError(f"催动阵法需要 {spirit_cost} 点灵力。")
        state.player.spirit -= spirit_cost
        formation["integrity"] = integrity - integrity_cost
        formation["activations"] = int(formation.get("activations", 0)) + 1
        state.combat["formation_used"] = True
        level = int(state.player.craft_skills.get("阵法", 0)) + DaoEngine.level(state, "阵道")
        if template.role == "结界":
            state.combat["formation_guard"] = True
            state.combat["enemy_bound"] = True
            return f"{template.name}化作厚土结界，本轮减伤并压制敌方攻势"
        if template.role == "困敌":
            state.combat["enemy_bound"] = True
            state.combat["player_observed"] = True
            return f"{template.name}封锁腾挪，敌方攻势受限，你的下一击必中"
        if template.role == "聚灵":
            before = state.player.spirit
            state.player.spirit = min(state.player.spirit_max, state.player.spirit + 28 + level * 4)
            return f"{template.name}引灵归元，灵力恢复 {state.player.spirit - before} 点"
        base = 24 if template.role == "杀阵" else 38
        damage = max(1, base + level * 7 - int(state.combat.get("enemy_defense", 0)) // 4)
        state.combat["enemy_health"] = max(0, int(state.combat["enemy_health"]) - damage)
        detail = "，五行阵势自行取敌所忌" if template.role == "万象" else ""
        return f"{template.name}轰然运转，造成 {damage} 点阵法伤害{detail}"

    @classmethod
    def combat_availability(cls, state: GameState) -> tuple[bool, str]:
        if state.phase != "combat":
            return False, "当前不在战斗中"
        if state.combat.get("formation_used"):
            return False, "本场战斗已经催动过阵法"
        active = cls.active(state)
        if not active:
            return False, "当前没有装配阵盘"
        template, formation = active
        spirit_cost, integrity_cost = cls.activation_cost(state, template)
        if int(formation.get("integrity", 0)) < integrity_cost:
            return False, "阵基残破，需要先修复"
        if state.player.spirit < spirit_cost:
            return False, f"需要 {spirit_cost} 点灵力"
        return True, ""

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        active = cls.active(state)
        arrays: list[dict[str, Any]] = []
        for formation_id, template in FORMATIONS.items():
            owned = state.formation_arrays.get(formation_id)
            integrity = int(owned.get("integrity", 0)) if owned else 0
            eligible, reason = cls.eligibility(state, formation_id)
            ingredients = "、".join(f"{name}×{count}" for name, count in template.ingredients.items())
            can_repair = bool(owned) and state.phase == "playing" and integrity < cls.MAX_INTEGRITY and state.player.resources.get("灵铁", 0) >= 1
            arrays.append(
                {
                    "id": formation_id,
                    "name": template.name,
                    "mark": template.mark,
                    "element": template.element,
                    "role": template.role,
                    "minimum_realm": REALMS[template.minimum_realm],
                    "summary": template.summary,
                    "effect": template.effect,
                    "ingredients": ingredients,
                    "chance": cls.build_chance(state, formation_id),
                    "owned": bool(owned),
                    "active": active is not None and active[0].id == formation_id,
                    "integrity": integrity,
                    "integrity_max": cls.MAX_INTEGRITY,
                    "build_action": f"炼阵 {template.name}",
                    "can_build": eligible,
                    "build_reason": reason,
                    "deploy_action": f"装配阵法 {template.name}",
                    "can_deploy": bool(owned) and state.phase == "playing",
                    "deploy_reason": (
                        "请先完成当前抉择" if state.phase != "playing" else
                        "尚未炼成" if not owned else ""
                    ),
                    "repair_action": f"修复阵法 {template.name}",
                    "can_repair": can_repair,
                    "repair_reason": (
                        "请先完成当前抉择" if state.phase != "playing" else
                        "尚未炼成" if not owned else
                        "阵基完整" if owned and integrity >= cls.MAX_INTEGRITY else
                        "缺少 灵铁×1" if state.player.resources.get("灵铁", 0) < 1 else ""
                    ),
                }
            )
        arrays.sort(key=lambda item: (not item["active"], not item["owned"], FORMATIONS[item["id"]].minimum_realm))
        return {
            "count": len(state.formation_arrays),
            "active_id": active[0].id if active else "",
            "active_name": active[0].name if active else "",
            "skill_level": int(state.player.craft_skills.get("阵法", 0)),
            "dao_level": DaoEngine.level(state, "阵道"),
            "arrays": arrays,
            "history": list(reversed(state.formation_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        owned = [item for item in snapshot["arrays"] if item["owned"]]
        roster = "\n".join(
            f"{item['name']}｜阵基 {item['integrity']}/{item['integrity_max']}｜{item['role']}"
            f"{'｜已装配' if item['active'] else ''}"
            for item in owned
        ) or "尚未炼成阵盘。"
        return (
            f"【五行阵图】\n装配：{snapshot['active_name'] or '无'}｜阵法技艺 {snapshot['skill_level']} 级｜阵道 {snapshot['dao_level']} 层\n"
            f"{roster}\n指令：炼阵 [阵名]／装配阵法 [阵名]／修复阵法 [阵名]；战斗中可催动阵法"
        )
