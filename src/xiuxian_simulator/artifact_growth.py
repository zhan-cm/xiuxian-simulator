from __future__ import annotations

from typing import Any

from .arts import ARTIFACTS, Artifact
from .dao import DaoEngine
from .progression import ProgressionEngine, REALMS
from .state import GameState


GRADE_FACTORS = {"黄阶": 1, "玄阶": 2, "地阶": 3, "天阶": 4, "仙阶": 5}
REFINEMENT_NAMES = ("未炼", "一炼", "二炼", "三炼", "四炼", "五炼")


class ArtifactGrowthEngine:
    """Long-term refinement and bonding for the existing artifact catalogue."""

    MAX_LEVEL = 5
    BIND_SPIRIT_COST = 10
    NOURISH_SPIRIT_COST = 18
    NOURISH_COOLDOWN = 3

    @staticmethod
    def owns(state: GameState, name: str) -> bool:
        return state.player.resources.get(name, 0) + state.player.inventory.count(name) > 0

    @staticmethod
    def equipped(state: GameState, name: str) -> bool:
        return name in {state.player.equipped_weapon, state.player.equipped_armor}

    @classmethod
    def record_for(cls, state: GameState, name: str) -> dict[str, Any]:
        record = state.artifact_refinements.setdefault(name, {})
        record.setdefault("level", 0)
        record.setdefault("resonance", 0)
        record.setdefault("victories", 0)
        record.setdefault("refinements", 0)
        record.setdefault("last_nourished_turn", -cls.NOURISH_COOLDOWN)
        return record

    @classmethod
    def view_record(cls, state: GameState, name: str) -> dict[str, Any]:
        return {
            "level": 0,
            "resonance": 0,
            "victories": 0,
            "refinements": 0,
            "last_nourished_turn": -cls.NOURISH_COOLDOWN,
            **state.artifact_refinements.get(name, {}),
        }

    @classmethod
    def level_cap(cls, state: GameState) -> int:
        return min(cls.MAX_LEVEL, max(1, state.player.realm_index + 1))

    @classmethod
    def refinement_cost(cls, artifact: Artifact, next_level: int) -> tuple[int, dict[str, int]]:
        factor = GRADE_FACTORS.get(artifact.grade, 1)
        stones = 60 * factor * next_level
        materials = {"灵铁": next_level}
        beast_materials = factor - 1 + (next_level - 1) // 2
        if beast_materials:
            materials["妖兽材料"] = beast_materials
        return stones, materials

    @classmethod
    def refinement_chance(cls, state: GameState, artifact: Artifact, next_level: int) -> int:
        factor = GRADE_FACTORS.get(artifact.grade, 1)
        craft = state.player.craft_skills.get("炼器", 0)
        dao = DaoEngine.player_level(state.player, "器道")
        return max(
            15,
            min(98, 90 - (next_level - 1) * 12 - (factor - 1) * 6 + craft * 7 + dao * 5 + state.player.spirit_sense - 10),
        )

    @classmethod
    def bind_availability(cls, state: GameState, name: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if name not in ARTIFACTS:
            return False, "未知法宝"
        if not cls.owns(state, name):
            return False, "乾坤袋中没有此法宝"
        if not cls.equipped(state, name):
            return False, "请先装备此法宝"
        if state.bonded_artifact == name:
            return False, "已是本命法宝"
        if state.player.spirit < cls.BIND_SPIRIT_COST:
            return False, f"需要 {cls.BIND_SPIRIT_COST} 灵力"
        return True, ""

    @classmethod
    def bind(cls, state: GameState, name: str) -> dict[str, Any]:
        available, reason = cls.bind_availability(state, name)
        if not available:
            raise ValueError(reason)
        previous = state.bonded_artifact
        state.player.spirit -= cls.BIND_SPIRIT_COST
        state.bonded_artifact = name
        record = cls.record_for(state, name)
        record["resonance"] = max(10, int(record["resonance"]))
        cls.record(state, f"{'更易' if previous else '立下'}本命法宝：{name}，器心契合 {record['resonance']}/100")
        return {"name": name, "previous": previous, "resonance": int(record["resonance"])}

    @classmethod
    def refine_availability(cls, state: GameState, name: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        artifact = ARTIFACTS.get(name)
        if artifact is None:
            return False, "未知法宝"
        if not cls.owns(state, name):
            return False, "乾坤袋中没有此法宝"
        record = cls.view_record(state, name)
        level = int(record["level"])
        if level >= cls.MAX_LEVEL:
            return False, "已达五炼圆满"
        cap = cls.level_cap(state)
        if level >= cap:
            next_realm = REALMS[min(len(REALMS) - 1, cap)]
            return False, f"需达到{next_realm}境方可继续"
        stones, materials = cls.refinement_cost(artifact, level + 1)
        if state.player.spirit_stones < stones:
            return False, f"灵石不足，还需 {stones - state.player.spirit_stones}"
        missing = [
            f"{item}×{count}"
            for item, count in materials.items()
            if state.player.resources.get(item, 0) < count
        ]
        if missing:
            return False, "缺少 " + "、".join(missing)
        return True, ""

    @classmethod
    def refine(cls, state: GameState, name: str) -> dict[str, Any]:
        available, reason = cls.refine_availability(state, name)
        if not available:
            raise ValueError(reason)
        artifact = ARTIFACTS[name]
        record = cls.record_for(state, name)
        next_level = int(record["level"]) + 1
        stones, materials = cls.refinement_cost(artifact, next_level)
        chance = cls.refinement_chance(state, artifact, next_level)
        state.player.spirit_stones -= stones
        for item, count in materials.items():
            state.player.resources[item] -= count
            if state.player.resources[item] <= 0:
                state.player.resources.pop(item, None)
        roll = ProgressionEngine.deterministic_roll(state, f"artifact-refine:{name}:{next_level}:{state.turn}")
        success = roll <= chance
        if success:
            record["level"] = next_level
            record["refinements"] = int(record["refinements"]) + 1
            if state.bonded_artifact == name:
                record["resonance"] = min(100, int(record["resonance"]) + 5)
        cls.record(
            state,
            f"淬炼{name}{'成功，升至' + REFINEMENT_NAMES[next_level] if success else '失败，炉火散尽'}（{roll}/{chance}）",
        )
        return {
            "name": name,
            "success": success,
            "level": int(record["level"]),
            "roll": roll,
            "chance": chance,
            "stones": stones,
            "materials": materials,
        }

    @classmethod
    def nourish_availability(cls, state: GameState, name: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if state.bonded_artifact != name:
            return False, "仅可温养本命法宝"
        if not cls.equipped(state, name):
            return False, "请先装备本命法宝"
        record = cls.view_record(state, name)
        if int(record["resonance"]) >= 100:
            return False, "器心已经圆满"
        turns_left = int(record["last_nourished_turn"]) + cls.NOURISH_COOLDOWN - state.turn
        if turns_left > 0:
            return False, f"还需温养气机 {turns_left} 个月"
        if state.player.spirit < cls.NOURISH_SPIRIT_COST:
            return False, f"需要 {cls.NOURISH_SPIRIT_COST} 灵力"
        return True, ""

    @classmethod
    def nourish(cls, state: GameState, name: str) -> dict[str, int | str]:
        available, reason = cls.nourish_availability(state, name)
        if not available:
            raise ValueError(reason)
        record = cls.record_for(state, name)
        dao_bonus = DaoEngine.player_level(state.player, "器道") * 2
        before = int(record["resonance"])
        state.player.spirit -= cls.NOURISH_SPIRIT_COST
        record["resonance"] = min(100, before + 8 + dao_bonus)
        record["last_nourished_turn"] = state.turn
        gained = int(record["resonance"]) - before
        cls.record(state, f"温养{name}，器心契合 +{gained}")
        return {"name": name, "gained": gained, "resonance": int(record["resonance"])}

    @classmethod
    def gain_victory(cls, state: GameState) -> int:
        name = state.bonded_artifact
        if not name or not cls.owns(state, name) or not cls.equipped(state, name):
            return 0
        record = cls.record_for(state, name)
        before = int(record["resonance"])
        record["resonance"] = min(100, before + 3)
        record["victories"] = int(record["victories"]) + 1
        return int(record["resonance"]) - before

    @classmethod
    def attack_bonus(cls, state: GameState, name: str) -> float:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        return level * 0.025 + resonance * 0.0005

    @classmethod
    def defense_bonus(cls, state: GameState, name: str) -> int:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        return level * 2 + resonance // 20

    @classmethod
    def speed_bonus(cls, state: GameState, name: str) -> int:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        return level // 2 + (1 if resonance >= 80 else 0)

    @staticmethod
    def record(state: GameState, text: str) -> None:
        state.artifact_history.append(f"第 {state.turn} 回合｜{text}")
        state.artifact_history = state.artifact_history[-30:]

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        cap = cls.level_cap(state)
        artifacts: list[dict[str, Any]] = []
        for name, artifact in ARTIFACTS.items():
            if not cls.owns(state, name):
                continue
            record = cls.view_record(state, name)
            level = int(record["level"])
            resonance = int(record["resonance"])
            next_level = min(cls.MAX_LEVEL, level + 1)
            stones, materials = cls.refinement_cost(artifact, next_level)
            can_refine, refine_reason = cls.refine_availability(state, name)
            can_bind, bind_reason = cls.bind_availability(state, name)
            can_nourish, nourish_reason = cls.nourish_availability(state, name)
            material_text = "、".join(f"{item}×{count}" for item, count in materials.items())
            growth = (
                f"攻势额外 +{cls.attack_bonus(state, name) * 100:.1f}%"
                if artifact.slot == "武器"
                else f"防御额外 +{cls.defense_bonus(state, name)}"
            )
            artifacts.append(
                {
                    "name": name,
                    "mark": name[:1],
                    "grade": artifact.grade,
                    "slot": artifact.slot,
                    "element": artifact.element,
                    "level": level,
                    "level_label": REFINEMENT_NAMES[level],
                    "level_cap": cap,
                    "resonance": resonance,
                    "victories": int(record["victories"]),
                    "equipped": cls.equipped(state, name),
                    "bonded": state.bonded_artifact == name,
                    "effect": growth,
                    "refine_cost": f"灵石 {stones} · {material_text}",
                    "refine_chance": cls.refinement_chance(state, artifact, next_level),
                    "can_refine": can_refine,
                    "refine_reason": refine_reason,
                    "refine_action": f"淬炼法宝 {name}",
                    "can_bind": can_bind,
                    "bind_reason": bind_reason,
                    "bind_action": f"认主法宝 {name}",
                    "can_nourish": can_nourish,
                    "nourish_reason": nourish_reason,
                    "nourish_action": f"温养法宝 {name}",
                }
            )
        artifacts.sort(key=lambda item: (-int(item["bonded"]), -int(item["equipped"]), -int(item["level"]), str(item["name"])))
        bonded = next((item for item in artifacts if item["bonded"]), None)
        return {
            "count": len(artifacts),
            "bonded_name": state.bonded_artifact if bonded else "",
            "bonded": bonded or {},
            "level_cap": cap,
            "level_cap_label": f"{REALMS[state.player.realm_index]}境 · 最多{REFINEMENT_NAMES[cap]}",
            "artifacts": artifacts,
            "materials": {
                "spirit_stones": state.player.spirit_stones,
                "spirit": state.player.spirit,
                "spirit_max": state.player.spirit_max,
                "spirit_iron": state.player.resources.get("灵铁", 0),
                "beast_materials": state.player.resources.get("妖兽材料", 0),
            },
            "history": list(reversed(state.artifact_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["artifacts"]:
            return "【本命法宝】乾坤袋中尚无法宝；可在坊市购置、炼器打造或从拍卖会寻觅。"
        lines = [
            f"{item['name']}｜{item['grade']}·{item['slot']}｜{item['level_label']}｜契合 {item['resonance']}/100"
            f"｜{'本命' if item['bonded'] else '已装备' if item['equipped'] else '袋中'}"
            for item in snapshot["artifacts"]
        ]
        return (
            f"【本命法宝】境界淬炼上限：{snapshot['level_cap_label']}\n"
            + "\n".join(lines)
            + "\n指令：认主法宝 [名称]／淬炼法宝 [名称]／温养法宝 [名称]"
        )
