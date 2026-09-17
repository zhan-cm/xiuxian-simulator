from __future__ import annotations

from typing import Any

from .arts import ARTIFACTS, Artifact
from .dao import DaoEngine
from .progression import ProgressionEngine, REALMS
from .state import GameState


GRADE_FACTORS = {"黄阶": 1, "玄阶": 2, "地阶": 3, "天阶": 4, "仙阶": 5}
GRADE_ORDER = {"黄阶": 1, "玄阶": 2, "地阶": 3, "天阶": 4, "仙阶": 5}
GRADE_SLOTS = {"黄阶": 2, "玄阶": 4, "地阶": 6, "天阶": 8, "仙阶": 9}
REFINEMENT_NAMES = ("未炼", "一炼", "二炼", "三炼", "四炼", "五炼")

INSCRIPTIONS: dict[str, dict[str, Any]] = {
    "锋锐": {
        "id": "锋锐",
        "name": "锋锐之纹",
        "slot_type": "通用",
        "desc": "金元肃杀，破甲穿透，物理攻势提升 15%",
        "cost_stones": 150,
        "cost_materials": {"灵铁": 3},
        "req_grade": "黄阶",
        "effect_text": "攻势额外 +15%",
    },
    "固本": {
        "id": "固本",
        "name": "固本之纹",
        "slot_type": "通用",
        "desc": "玄武镇岳，固守灵台，防御额外提升并受创减免",
        "cost_stones": 150,
        "cost_materials": {"灵铁": 3},
        "req_grade": "黄阶",
        "effect_text": "防御额外 +20，伤害减免 8%",
    },
    "聚灵": {
        "id": "聚灵",
        "name": "聚灵之纹",
        "slot_type": "通用",
        "desc": "太清纳气，通灵纳海，灵力上限 +80，每轮回复灵力",
        "cost_stones": 200,
        "cost_materials": {"灵铁": 2, "妖兽材料": 1},
        "req_grade": "玄阶",
        "effect_text": "灵力上限 +80，每轮回复灵力",
    },
    "噬血": {
        "id": "噬血",
        "name": "噬血之纹",
        "slot_type": "武器",
        "desc": "修罗煞印，攻击命中时汲取 12% 伤害反哺自身气血",
        "cost_stones": 300,
        "cost_materials": {"妖兽材料": 3},
        "req_grade": "玄阶",
        "effect_text": "攻击附带 12% 伤害吸血反哺",
    },
    "破妄": {
        "id": "破妄",
        "name": "破妄之纹",
        "slot_type": "通用",
        "desc": "通明道眼，神识 +6，心魔与神识威压抗性大幅提升",
        "cost_stones": 350,
        "cost_materials": {"灵铁": 3, "妖兽材料": 2},
        "req_grade": "玄阶",
        "effect_text": "神识 +6，心魔抗性增强",
    },
    "雷罡": {
        "id": "雷罡",
        "name": "雷罡之纹",
        "slot_type": "通用",
        "desc": "紫霄神雷，攻击附带 40 点天罚雷伤，15% 几率令敌麻痹",
        "cost_stones": 500,
        "cost_materials": {"灵铁": 4, "妖兽材料": 2},
        "req_grade": "地阶",
        "effect_text": "附带 40 点雷伤，15% 几率麻痹",
    },
    "疾风": {
        "id": "疾风",
        "name": "疾风之纹",
        "slot_type": "通用",
        "desc": "御剑凌虚，身法遁速 +6，闪避率提升 10%",
        "cost_stones": 450,
        "cost_materials": {"灵铁": 4, "妖兽材料": 2},
        "req_grade": "地阶",
        "effect_text": "身法遁速 +6，闪避率 +10%",
    },
    "护命": {
        "id": "护命",
        "name": "护命之纹",
        "slot_type": "防具",
        "desc": "神凰还阳，遭受致命死劫时法宝悲鸣护主，免死一次并恢复 35% 气血",
        "cost_stones": 800,
        "cost_materials": {"灵铁": 6, "妖兽材料": 4},
        "req_grade": "天阶",
        "effect_text": "抵御必死绝杀一次，复苏 35% 气血",
    },
    "混沌": {
        "id": "混沌",
        "name": "混沌之纹",
        "slot_type": "通用",
        "desc": "九纹归一，太虚混元，全器纹神威与全属性增幅 20%",
        "cost_stones": 1200,
        "cost_materials": {"灵铁": 8, "妖兽材料": 6},
        "req_grade": "天阶",
        "effect_text": "全属性与法宝神威增幅 20%",
    },
}

INFUSIBLE_MATERIALS: dict[str, dict[str, Any]] = {
    "灵铁": {
        "name": "灵铁",
        "desc": "基础地蕴金石，夯实器身底蕴",
        "resonance_gain": 2,
        "bonus_text": "淬炼器身，微幅提升法宝坚固",
    },
    "妖兽材料": {
        "name": "妖兽材料",
        "desc": "荒古蛮兽精血毛皮，赋予煞气与灵性",
        "resonance_gain": 2,
        "bonus_text": "煞气附灵，微幅提升法宝凶戾",
    },
    "天工万象铁": {
        "name": "天工万象铁",
        "desc": "天机阁神匠九千锤百炼神铁，大幅提升法宝锋锐与器心",
        "resonance_gain": 8,
        "bonus_text": "天工注灵，攻防神威额外 +3%",
    },
    "太玄剑魄": {
        "name": "太玄剑魄",
        "desc": "上古太玄剑帝遗留之纯阳剑道真意，唤醒器灵无上道意",
        "resonance_gain": 15,
        "bonus_text": "太玄剑意，器心大幅契合并强化悟道",
    },
    "洗剑古砂": {
        "name": "洗剑古砂",
        "desc": "东洲青岳洗剑池底沉淀万载灵砂，澄澈法宝器心杂质",
        "resonance_gain": 5,
        "bonus_text": "澄澈剑胎，提升器灵感应",
    },
    "地心火晶": {
        "name": "地心火晶",
        "desc": "南疆地肺深处极阳火髓，温养熔炉神威",
        "resonance_gain": 5,
        "bonus_text": "纯阳地火，提升淬炼成效",
    },
}


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
        record.setdefault("inscriptions", [])
        record.setdefault("infused_materials", {})
        record.setdefault("spirit_awakened", False)
        return record

    @classmethod
    def view_record(cls, state: GameState, name: str) -> dict[str, Any]:
        return {
            "level": 0,
            "resonance": 0,
            "victories": 0,
            "refinements": 0,
            "last_nourished_turn": -cls.NOURISH_COOLDOWN,
            "inscriptions": [],
            "infused_materials": {},
            "spirit_awakened": False,
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

    # ================= 器纹铭刻与洗练 =================

    @classmethod
    def inscribe_availability(cls, state: GameState, artifact_name: str, inscription_id: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        artifact = ARTIFACTS.get(artifact_name)
        if not artifact:
            return False, "未知法宝"
        if not cls.owns(state, artifact_name):
            return False, "乾坤袋中没有此法宝"
        inscr = INSCRIPTIONS.get(inscription_id)
        if not inscr:
            return False, f"未知器纹：{inscription_id}"
        record = cls.view_record(state, artifact_name)
        inscriptions = list(record.get("inscriptions", []))
        if inscription_id in inscriptions:
            return False, "该器纹已铭刻在法宝上"
        max_slots = GRADE_SLOTS.get(artifact.grade, 2)
        if len(inscriptions) >= max_slots:
            return False, f"{artifact.grade}法宝最多铭刻 {max_slots} 道器纹"
        req_grade = inscr.get("req_grade", "黄阶")
        if GRADE_ORDER.get(artifact.grade, 1) < GRADE_ORDER.get(req_grade, 1):
            return False, f"铭刻【{inscr['name']}】需要至少【{req_grade}】法宝"
        if inscr.get("slot_type") == "武器" and artifact.slot != "武器":
            return False, f"【{inscr['name']}】仅可铭刻于武器类法宝"
        if inscr.get("slot_type") in ("防具", "护甲") and artifact.slot not in ("防具", "护甲"):
            return False, f"【{inscr['name']}】仅可铭刻于护甲类法宝"
        cost_stones = int(inscr.get("cost_stones", 0))
        if state.player.spirit_stones < cost_stones:
            return False, f"灵石不足，铭刻需 {cost_stones} 灵石"
        cost_mats = inscr.get("cost_materials", {})
        missing = [
            f"{mat}×{amt}"
            for mat, amt in cost_mats.items()
            if state.player.resources.get(mat, 0) < amt
        ]
        if missing:
            return False, "缺少灵材：" + "、".join(missing)
        return True, ""

    @classmethod
    def inscribe(cls, state: GameState, artifact_name: str, inscription_id: str) -> dict[str, Any]:
        can, reason = cls.inscribe_availability(state, artifact_name, inscription_id)
        if not can:
            raise ValueError(reason)
        inscr = INSCRIPTIONS[inscription_id]
        record = cls.record_for(state, artifact_name)
        state.player.spirit_stones -= int(inscr["cost_stones"])
        for mat, amt in inscr.get("cost_materials", {}).items():
            state.player.resources[mat] -= amt
            if state.player.resources[mat] <= 0:
                state.player.resources.pop(mat, None)
        inscriptions = record.setdefault("inscriptions", [])
        inscriptions.append(inscription_id)
        if state.bonded_artifact == artifact_name:
            record["resonance"] = min(100, int(record.get("resonance", 0)) + 3)
        cls.record(state, f"在{artifact_name}上铭刻【{inscr['name']}】，器纹通灵！")
        return {"artifact": artifact_name, "inscription": inscription_id, "inscriptions": inscriptions}

    @classmethod
    def wash_availability(cls, state: GameState, artifact_name: str, inscription_id: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if not cls.owns(state, artifact_name):
            return False, "乾坤袋中没有此法宝"
        record = cls.view_record(state, artifact_name)
        if inscription_id not in record.get("inscriptions", []):
            return False, "法宝上未铭刻此器纹"
        if state.player.spirit_stones < 50:
            return False, "洗练器纹需要 50 灵石"
        return True, ""

    @classmethod
    def wash(cls, state: GameState, artifact_name: str, inscription_id: str) -> dict[str, Any]:
        can, reason = cls.wash_availability(state, artifact_name, inscription_id)
        if not can:
            raise ValueError(reason)
        state.player.spirit_stones -= 50
        record = cls.record_for(state, artifact_name)
        inscriptions = record.setdefault("inscriptions", [])
        if inscription_id in inscriptions:
            inscriptions.remove(inscription_id)
        cls.record(state, f"以三昧真火洗练{artifact_name}上的【{inscription_id}之纹】。")
        return {"artifact": artifact_name, "washed": inscription_id, "inscriptions": inscriptions}

    # ================= 神料熔铸 =================

    @classmethod
    def infuse_availability(cls, state: GameState, artifact_name: str, material_name: str) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if not cls.owns(state, artifact_name):
            return False, "乾坤袋中没有此法宝"
        if material_name not in INFUSIBLE_MATERIALS:
            return False, f"此材料不可熔铸入法宝：{material_name}"
        if state.player.resources.get(material_name, 0) < 1:
            return False, f"乾坤袋中没有【{material_name}】"
        if state.player.spirit_stones < 30:
            return False, "熔铸需要 30 灵石引火"
        record = cls.view_record(state, artifact_name)
        if int(record.get("resonance", 0)) >= 100:
            return False, "器心契合已达圆满，无需再熔铸"
        return True, ""

    @classmethod
    def infuse(cls, state: GameState, artifact_name: str, material_name: str) -> dict[str, Any]:
        can, reason = cls.infuse_availability(state, artifact_name, material_name)
        if not can:
            raise ValueError(reason)
        info = INFUSIBLE_MATERIALS[material_name]
        state.player.spirit_stones -= 30
        state.player.resources[material_name] -= 1
        if state.player.resources[material_name] <= 0:
            state.player.resources.pop(material_name, None)
        record = cls.record_for(state, artifact_name)
        gain = int(info.get("resonance_gain", 2))
        before = int(record.get("resonance", 0))
        record["resonance"] = min(100, before + gain)
        infused = record.setdefault("infused_materials", {})
        infused[material_name] = infused.get(material_name, 0) + 1
        cls.record(state, f"向{artifact_name}熔入【{material_name}】，器心契合 +{gain}（当前 {record['resonance']}/100）。")
        return {"artifact": artifact_name, "material": material_name, "gained": gain, "resonance": record["resonance"]}

    # ================= 器灵觉醒与通微 =================

    @classmethod
    def spirit_stage_info(cls, resonance: int) -> tuple[int, str, str]:
        if resonance >= 100:
            return 4, "真灵显圣", "法宝真灵已然圆满通玄，宝光照彻九天！‘主人，纵临九霄雷劫，我亦护你飞升！’"
        if resonance >= 90:
            return 3, "人器合一", "法宝灵光万道，与修士神魂水乳交融：‘神魂相通，生死与共！愿随主人问鼎仙道！’"
        if resonance >= 60:
            return 2, "形意相随", "一缕小巧的灵动虚影在法宝旁盘旋：‘主人，我感应到了你的神识温养，好舒服呀~’"
        if resonance >= 30:
            return 1, "器灵初醒", "法宝内部传来微弱如蝉翼的颤鸣，微光流转，似在渴望汲取你的灵力真元。"
        return 0, "器心沉眠", "法宝静静悬浮，尚需继续以自身真元温养器心，唤醒沉眠器灵。"

    @classmethod
    def spirit_commune(cls, state: GameState, artifact_name: str) -> dict[str, Any]:
        if not cls.owns(state, artifact_name):
            raise ValueError("乾坤袋中没有此法宝")
        record = cls.record_for(state, artifact_name)
        resonance = int(record.get("resonance", 0))
        stage, title, dialogue = cls.spirit_stage_info(resonance)
        if stage >= 1:
            record["spirit_awakened"] = True
        gained_spirit = 0
        if state.bonded_artifact == artifact_name and stage >= 1:
            gained_spirit = min(state.player.spirit_max - state.player.spirit, 15)
            state.player.spirit += gained_spirit
        cls.record(state, f"神识沉入{artifact_name}感应器灵：{dialogue}")
        return {
            "artifact": artifact_name,
            "stage": stage,
            "title": title,
            "dialogue": dialogue,
            "gained_spirit": gained_spirit,
        }

    # ================= 战斗与属性加成 =================

    @classmethod
    def attack_bonus(cls, state: GameState, name: str) -> float:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        inscriptions = record.get("inscriptions", [])
        infused = record.get("infused_materials", {})
        base = level * 0.025 + resonance * 0.0005
        if "锋锐" in inscriptions:
            base += 0.15
        if "混沌" in inscriptions:
            base += 0.05
        base += infused.get("天工万象铁", 0) * 0.03
        return base

    @classmethod
    def defense_bonus(cls, state: GameState, name: str) -> int:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        inscriptions = record.get("inscriptions", [])
        infused = record.get("infused_materials", {})
        base = level * 2 + resonance // 20
        if "固本" in inscriptions:
            base += 20
        if "混沌" in inscriptions:
            base += 10
        base += infused.get("天工万象铁", 0) * 5
        return base

    @classmethod
    def speed_bonus(cls, state: GameState, name: str) -> int:
        record = state.artifact_refinements.get(name, {})
        level = int(record.get("level", 0))
        resonance = int(record.get("resonance", 0)) if state.bonded_artifact == name else 0
        inscriptions = record.get("inscriptions", [])
        base = level // 2 + (1 if resonance >= 80 else 0)
        if "疾风" in inscriptions:
            base += 6
        if "混沌" in inscriptions:
            base += 2
        return base

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

            inscriptions = list(record.get("inscriptions", []))
            max_slots = GRADE_SLOTS.get(artifact.grade, 2)
            stage, stage_title, stage_dialogue = cls.spirit_stage_info(resonance)

            available_inscriptions = []
            for i_id, i_info in INSCRIPTIONS.items():
                can_inscribe, inscribe_reason = cls.inscribe_availability(state, name, i_id)
                available_inscriptions.append(
                    {
                        "id": i_id,
                        "name": i_info["name"],
                        "desc": i_info["desc"],
                        "effect_text": i_info["effect_text"],
                        "cost_stones": i_info["cost_stones"],
                        "cost_materials": i_info["cost_materials"],
                        "req_grade": i_info["req_grade"],
                        "slot_type": i_info["slot_type"],
                        "inscribed": i_id in inscriptions,
                        "can_inscribe": can_inscribe,
                        "inscribe_reason": inscribe_reason,
                        "inscribe_action": f"铭刻器纹 {name} {i_id}",
                        "wash_action": f"洗练器纹 {name} {i_id}",
                    }
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
                    "inscriptions": inscriptions,
                    "max_slots": max_slots,
                    "spirit_stage": stage,
                    "spirit_stage_label": stage_title,
                    "spirit_dialogue": stage_dialogue,
                    "spirit_awakened": bool(record.get("spirit_awakened", False)),
                    "spirit_commune_action": f"器灵感应 {name}",
                    "available_inscriptions": available_inscriptions,
                    "infused_materials": dict(record.get("infused_materials", {})),
                }
            )
        artifacts.sort(key=lambda item: (-int(item["bonded"]), -int(item["equipped"]), -int(item["level"]), str(item["name"])))
        bonded = next((item for item in artifacts if item["bonded"]), None)

        infusable_list = []
        for mat_id, mat_info in INFUSIBLE_MATERIALS.items():
            count = state.player.resources.get(mat_id, 0)
            can_infuse = count > 0 and bonded is not None and int(bonded.get("resonance", 0)) < 100
            infusable_list.append(
                {
                    "name": mat_id,
                    "desc": mat_info["desc"],
                    "bonus_text": mat_info["bonus_text"],
                    "resonance_gain": mat_info["resonance_gain"],
                    "count": count,
                    "can_infuse": can_infuse,
                    "infuse_action": f"熔铸神料 {bonded['name']} {mat_id}" if bonded else "",
                }
            )

        return {
            "count": len(artifacts),
            "bonded_name": state.bonded_artifact if bonded else "",
            "bonded": bonded or {},
            "level_cap": cap,
            "level_cap_label": f"{REALMS[state.player.realm_index]}境 · 最多{REFINEMENT_NAMES[cap]}",
            "artifacts": artifacts,
            "all_inscriptions": list(INSCRIPTIONS.values()),
            "infusable_materials": infusable_list,
            "materials": {
                "spirit_stones": state.player.spirit_stones,
                "spirit": state.player.spirit,
                "spirit_max": state.player.spirit_max,
                "spirit_iron": state.player.resources.get("灵铁", 0),
                "beast_materials": state.player.resources.get("妖兽材料", 0),
                "divine_iron": state.player.resources.get("天工万象铁", 0),
                "sword_soul": state.player.resources.get("太玄剑魄", 0),
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
            f"｜器纹 {len(item['inscriptions'])}/{item['max_slots']}"
            f"｜{'本命' if item['bonded'] else '已装备' if item['equipped'] else '袋中'}"
            for item in snapshot["artifacts"]
        ]
        return (
            f"【本命法宝】境界淬炼上限：{snapshot['level_cap_label']}\n"
            + "\n".join(lines)
            + "\n指令：认主法宝 [名称]／淬炼法宝 [名称]／温养法宝 [名称]／铭刻器纹 [法宝名] [器纹名]／洗练器纹 [法宝名] [器纹名]／熔铸神料 [法宝名] [材料名]／器灵感应 [法宝名]"
        )
