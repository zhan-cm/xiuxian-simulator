from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .progression import REALMS, STAGES, ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class SectDoctrine:
    id: str
    name: str
    mark: str
    summary: str
    effect: str


@dataclass(frozen=True, slots=True)
class SectBuilding:
    id: str
    name: str
    mark: str
    summary: str
    base_cost: int


DOCTRINES: dict[str, SectDoctrine] = {
    "sword": SectDoctrine(
        "sword", "凌霄剑脉", "剑", "以实战磨砺门人，山门以锋芒和护道战力立足九州。", "门人修行 +2/月，宗门实力成长更快"
    ),
    "alchemy": SectDoctrine(
        "alchemy", "丹鼎长生", "丹", "以丹鼎供养山门，让修行资粮和百艺传承形成长久循环。", "宗门收入 +18/月，每年产出疗伤丹"
    ),
    "harmony": SectDoctrine(
        "harmony", "万法同流", "和", "不拘灵根与来处，重视门人心性、忠诚与诸法互证。", "招徒成功率 +12%，门人忠诚成长更快"
    ),
}

BUILDINGS: dict[str, SectBuilding] = {
    "academy": SectBuilding("academy", "传道院", "经", "提高全体门人的月度修行进展。", 320),
    "workshop": SectBuilding("workshop", "百炼坊", "炉", "炼丹炼器所得反哺宗门财政。", 380),
    "ward": SectBuilding("ward", "护山阵", "阵", "稳固山门，并提高宗门在天下势力谱中的实力。", 440),
}

FOCUSES = {
    "recruit": ("广纳门徒", "招徒成功率 +10%，但每名门人月度用度 +1"),
    "elite": ("精研道统", "门人修行 +3/月，宗门月度收入 -8"),
    "world": ("济世行道", "宗门声望每季增长更快，宗门月度收入 -5"),
}

LEVELS = (
    (0, "初立山门"),
    (120, "一方宗派"),
    (340, "名动一域"),
    (760, "九州名门"),
)

DISCIPLE_NAMES = (
    "陆青禾", "裴照川", "宁知微", "叶听澜", "苏观雨", "谢临风",
    "楚星遥", "温如晦", "顾明夷", "林照雪", "沈怀玉", "江归鹤",
)


class SectFoundationEngine:
    FOUNDATION_COST = 2000
    RECRUIT_COST = 180
    TEACH_COST = 120
    MAX_DISCIPLES = 12
    MAX_BUILDING_LEVEL = 3

    @staticmethod
    def active(state: GameState) -> bool:
        return bool(state.founded_sect.get("name"))

    @staticmethod
    def ruined(state: GameState) -> bool:
        return bool(state.founded_sect.get("ruined"))

    @classmethod
    def suggested_name(cls, state: GameState) -> str:
        stem = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", state.player.dao_name)[:4] or "问道"
        return f"{stem}宗"

    @staticmethod
    def _validate_name(name: str) -> str:
        cleaned = name.strip()
        if not re.fullmatch(r"[\u4e00-\u9fffA-Za-z0-9·]{2,8}", cleaned):
            raise ValueError("宗门名需为 2～8 个汉字、字母或数字，可含间隔点。")
        return cleaned

    @classmethod
    def foundation_requirements(cls, state: GameState) -> list[dict[str, Any]]:
        player = state.player
        return [
            {"label": "身份", "value": "散修", "current": player.sect, "met": player.sect == "散修"},
            {"label": "境界", "value": "金丹境", "current": player.realm, "met": player.realm_index >= 3},
            {"label": "声望", "value": "60", "current": player.reputation, "met": player.reputation >= 60},
            {"label": "灵石", "value": str(cls.FOUNDATION_COST), "current": player.spirit_stones, "met": player.spirit_stones >= cls.FOUNDATION_COST},
        ]

    @classmethod
    def foundation_availability(cls, state: GameState) -> tuple[bool, str]:
        if cls.active(state):
            return False, "本世已经开宗立派"
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        missing = [item for item in cls.foundation_requirements(state) if not item["met"]]
        if not missing:
            return True, ""
        item = missing[0]
        if item["label"] == "身份":
            return False, "需先离开原有宗门，恢复散修身份"
        return False, f"{item['label']}不足：需要 {item['value']}，当前 {item['current']}"

    @classmethod
    def begin(cls, state: GameState, name: str = "") -> str:
        available, reason = cls.foundation_availability(state)
        if not available:
            raise ValueError(reason)
        chosen_name = cls._validate_name(name or cls.suggested_name(state))
        if chosen_name in state.faction_strengths:
            raise ValueError("九州势力谱中已经有同名宗门。")
        state.pending_sect_name = chosen_name
        state.phase = "sect_foundation_choice"
        return chosen_name

    @staticmethod
    def cancel(state: GameState) -> None:
        state.pending_sect_name = ""
        state.phase = "playing"

    @classmethod
    def _make_disciple(cls, state: GameState, offset: int, role: str = "入门弟子") -> dict[str, Any]:
        used = {str(item.get("name", "")) for item in state.sect_disciples}
        start = (state.rng_seed + state.turn + offset * 3) % len(DISCIPLE_NAMES)
        name = next((DISCIPLE_NAMES[(start + step) % len(DISCIPLE_NAMES)] for step in range(len(DISCIPLE_NAMES)) if DISCIPLE_NAMES[(start + step) % len(DISCIPLE_NAMES)] not in used), f"门人{len(used) + 1}")
        aptitude = 8 + ((state.rng_seed + state.turn * 7 + offset * 11) % 8)
        loyalty = 68 + ((state.rng_seed + offset * 13) % 17)
        return {
            "name": name,
            "role": role,
            "aptitude": aptitude,
            "loyalty": loyalty,
            "realm_index": 0,
            "stage_index": 0,
            "progress": 8 + aptitude,
            "joined_turn": state.turn,
        }

    @classmethod
    def found(cls, state: GameState, doctrine_id: str) -> SectDoctrine:
        if state.phase != "sect_foundation_choice" or not state.pending_sect_name:
            raise ValueError("尚未开始开宗立派。")
        doctrine = DOCTRINES.get(doctrine_id)
        if doctrine is None:
            raise ValueError("请选择凌霄剑脉、丹鼎长生或万法同流。")
        if state.player.spirit_stones < cls.FOUNDATION_COST:
            raise ValueError(f"立宗所需 {cls.FOUNDATION_COST} 灵石已经不足。")
        name = state.pending_sect_name
        state.player.spirit_stones -= cls.FOUNDATION_COST
        state.player.sect = name
        state.player.sect_rank = "掌门"
        state.player.sect_contribution = 0
        state.player.reputation += 8
        state.founded_sect = {
            "name": name,
            "doctrine": doctrine.id,
            "level": 1,
            "experience": 0,
            "renown": 18,
            "stability": 72,
            "treasury": 500,
            "focus": "recruit",
            "buildings": {"hall": 1, "academy": 0, "workshop": 0, "ward": 0},
            "founded_year": state.calendar_year,
            "founded_month": state.month,
            "last_recruit_turn": -999,
            "last_teach_year": 0,
            "last_focus_year": 0,
            "income_lifetime": 0,
            "expense_lifetime": cls.FOUNDATION_COST,
            "monthly_net": 0,
            "ruined": False,
        }
        state.sect_disciples = []
        state.sect_disciples.append(cls._make_disciple(state, 1, "开山弟子"))
        state.sect_disciples.append(cls._make_disciple(state, 2, "开山弟子"))
        state.faction_strengths[name] = 34
        state.world_milestones.append(f"天玄历{state.calendar_year}年｜{state.player.dao_name}开创{name}，立下{doctrine.name}道统。")
        state.world_milestones = state.world_milestones[-50:]
        cls.record(state, f"开宗立派，立{doctrine.name}为根本道统，首收两名开山弟子")
        state.pending_sect_name = ""
        state.phase = "playing"
        return doctrine

    @classmethod
    def _require_active(cls, state: GameState) -> dict[str, Any]:
        if not cls.active(state):
            raise ValueError("本世尚未开宗立派。")
        if cls.ruined(state):
            raise ValueError("山门已经覆灭，本世无法继续经营。")
        return state.founded_sect

    @classmethod
    def set_focus(cls, state: GameState, focus_id: str) -> str:
        sect = cls._require_active(state)
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择。")
        if focus_id not in FOCUSES:
            raise ValueError("可选方针：广纳门徒、精研道统、济世行道。")
        if sect.get("focus") == focus_id:
            raise ValueError("当前已经采用这一宗门方针。")
        if int(sect.get("last_focus_year", 0)) == state.calendar_year:
            raise ValueError("宗门方针每个自然年只能改定一次。")
        sect["focus"] = focus_id
        sect["last_focus_year"] = state.calendar_year
        name = FOCUSES[focus_id][0]
        cls.record(state, f"掌门议定年度方针：{name}")
        return name

    @classmethod
    def recruit(cls, state: GameState) -> dict[str, Any]:
        sect = cls._require_active(state)
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择。")
        if len(state.sect_disciples) >= cls.MAX_DISCIPLES:
            raise ValueError(f"当前山门最多容纳 {cls.MAX_DISCIPLES} 名门人。")
        turns_left = 6 - (state.turn - int(sect.get("last_recruit_turn", -999)))
        if turns_left > 0:
            raise ValueError(f"距上次开山收徒尚近，还需等待 {turns_left} 个月。")
        if int(sect.get("treasury", 0)) < cls.RECRUIT_COST:
            raise ValueError(f"宗门库藏不足：招徒需要 {cls.RECRUIT_COST} 灵石。")
        doctrine_bonus = 12 if sect.get("doctrine") == "harmony" else 0
        focus_bonus = 10 if sect.get("focus") == "recruit" else 0
        chance = max(30, min(95, 52 + int(sect.get("renown", 0)) // 4 + doctrine_bonus + focus_bonus))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-recruit:{sect['name']}:{state.turn}")
        sect["treasury"] = int(sect.get("treasury", 0)) - cls.RECRUIT_COST
        sect["expense_lifetime"] = int(sect.get("expense_lifetime", 0)) + cls.RECRUIT_COST
        sect["last_recruit_turn"] = state.turn
        success = roll <= chance
        disciple: dict[str, Any] = {}
        if success:
            disciple = cls._make_disciple(state, len(state.sect_disciples) + 3)
            state.sect_disciples.append(disciple)
            sect["experience"] = int(sect.get("experience", 0)) + 18
            sect["renown"] = min(100, int(sect.get("renown", 0)) + 2)
            cls.record(state, f"开山收徒：{disciple['name']}拜入门下（资质 {disciple['aptitude']}）")
        else:
            cls.record(state, f"开山收徒未遇合适门人（判定 {roll}/{chance}）")
        return {"success": success, "roll": roll, "chance": chance, "disciple": disciple}

    @classmethod
    def upgrade_building(cls, state: GameState, building_id: str) -> dict[str, Any]:
        sect = cls._require_active(state)
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择。")
        building = BUILDINGS.get(building_id)
        if building is None:
            raise ValueError("可营造传道院、百炼坊或护山阵。")
        buildings = sect.setdefault("buildings", {"hall": 1, "academy": 0, "workshop": 0, "ward": 0})
        current = int(buildings.get(building.id, 0))
        if current >= cls.MAX_BUILDING_LEVEL:
            raise ValueError(f"{building.name}已经达到当前版本上限。")
        target = current + 1
        cost = building.base_cost * target
        if int(sect.get("treasury", 0)) < cost:
            raise ValueError(f"宗门库藏不足：营造至 {target} 级需要 {cost} 灵石。")
        sect["treasury"] = int(sect.get("treasury", 0)) - cost
        sect["expense_lifetime"] = int(sect.get("expense_lifetime", 0)) + cost
        buildings[building.id] = target
        sect["experience"] = int(sect.get("experience", 0)) + 28 * target
        sect["stability"] = min(100, int(sect.get("stability", 0)) + 3)
        cls.record(state, f"{building.name}营造至 {target} 级，库藏 -{cost}")
        return {"building": building, "level": target, "cost": cost}

    @classmethod
    def teach(cls, state: GameState) -> dict[str, int]:
        sect = cls._require_active(state)
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择。")
        if int(sect.get("last_teach_year", 0)) == state.calendar_year:
            raise ValueError("本年已经主持过一次宗门传法。")
        if int(sect.get("treasury", 0)) < cls.TEACH_COST:
            raise ValueError(f"宗门传法需要 {cls.TEACH_COST} 库藏。")
        academy = int(sect.get("buildings", {}).get("academy", 0))
        progress = 24 + academy * 8 + state.player.comprehension // 4
        for disciple in state.sect_disciples:
            disciple["progress"] = int(disciple.get("progress", 0)) + progress
            disciple["loyalty"] = min(100, int(disciple.get("loyalty", 0)) + 2)
        insight = 6 + academy * 2
        state.player.dao_insight += insight
        sect["treasury"] = int(sect.get("treasury", 0)) - cls.TEACH_COST
        sect["expense_lifetime"] = int(sect.get("expense_lifetime", 0)) + cls.TEACH_COST
        sect["last_teach_year"] = state.calendar_year
        sect["experience"] = int(sect.get("experience", 0)) + 20
        cls.record(state, f"掌门开坛传法，门人修行 +{progress}，自身感悟 +{insight}")
        return {"progress": progress, "insight": insight}

    @classmethod
    def _level_for_experience(cls, experience: int) -> int:
        return max(index + 1 for index, (threshold, _) in enumerate(LEVELS) if experience >= threshold)

    @classmethod
    def _monthly_finance(cls, state: GameState) -> tuple[int, int, int]:
        sect = state.founded_sect
        disciples = len(state.sect_disciples)
        buildings = sect.get("buildings", {})
        income = 15 + disciples * 9 + int(buildings.get("workshop", 0)) * 16
        if sect.get("doctrine") == "alchemy":
            income += 18
        if sect.get("focus") == "elite":
            income -= 8
        elif sect.get("focus") == "world":
            income -= 5
        upkeep = disciples * (4 if sect.get("focus") == "recruit" else 3) + sum(int(value) for value in buildings.values()) * 2
        return max(0, income), upkeep, income - upkeep

    @classmethod
    def tick_month(cls, state: GameState) -> list[str]:
        if not cls.active(state) or cls.ruined(state):
            return []
        sect = state.founded_sect
        events: list[str] = []
        income, upkeep, net = cls._monthly_finance(state)
        treasury = int(sect.get("treasury", 0)) + net
        if treasury < 0:
            sect["treasury"] = 0
            sect["stability"] = max(0, int(sect.get("stability", 0)) - 3)
            events.append("宗门库藏入不敷出，门人心绪浮动，稳定 -3")
        else:
            sect["treasury"] = treasury
        sect["income_lifetime"] = int(sect.get("income_lifetime", 0)) + income
        sect["monthly_net"] = net

        academy = int(sect.get("buildings", {}).get("academy", 0))
        growth = 3 + int(sect.get("level", 1)) + academy * 2
        if sect.get("doctrine") == "sword":
            growth += 2
        if sect.get("focus") == "elite":
            growth += 3
        max_realm = max(0, state.player.realm_index - 1)
        for disciple in state.sect_disciples:
            disciple["progress"] = int(disciple.get("progress", 0)) + growth + int(disciple.get("aptitude", 8)) // 4
            if sect.get("doctrine") == "harmony":
                disciple["loyalty"] = min(100, int(disciple.get("loyalty", 0)) + 1)
            realm_index = int(disciple.get("realm_index", 0))
            stage_index = int(disciple.get("stage_index", 0))
            requirement = 70 + realm_index * 45 + stage_index * 20
            if int(disciple["progress"]) >= requirement:
                if stage_index < len(STAGES) - 1:
                    disciple["stage_index"] = stage_index + 1
                    disciple["progress"] = int(disciple["progress"]) - requirement
                    events.append(f"{disciple['name']}修至{REALMS[realm_index]}·{STAGES[stage_index + 1]}")
                elif realm_index < max_realm:
                    disciple["realm_index"] = realm_index + 1
                    disciple["stage_index"] = 0
                    disciple["progress"] = int(disciple["progress"]) - requirement
                    events.append(f"{disciple['name']}破入{REALMS[realm_index + 1]}·初期")

        sect["experience"] = int(sect.get("experience", 0)) + max(1, len(state.sect_disciples) + sum(int(v) for v in sect.get("buildings", {}).values()))
        old_level = int(sect.get("level", 1))
        new_level = cls._level_for_experience(int(sect["experience"]))
        if new_level > old_level:
            sect["level"] = new_level
            sect["renown"] = min(100, int(sect.get("renown", 0)) + 8)
            events.append(f"{sect['name']}晋为【{LEVELS[new_level - 1][1]}】，宗门声望 +8")

        if state.month in {1, 4, 7, 10}:
            renown_gain = 2 if sect.get("focus") == "world" else 1
            sect["renown"] = min(100, int(sect.get("renown", 0)) + renown_gain)
            if sect.get("doctrine") == "alchemy" and state.month == 1:
                state.player.resources["疗伤丹"] = state.player.resources.get("疗伤丹", 0) + 1
                events.append("丹鼎长生道统完成年度供丹，疗伤丹 +1")
            quarterly = f"{sect['name']}季报：库藏 {sect['treasury']}（月净 {net:+d}），门人 {len(state.sect_disciples)}，声望 {sect['renown']}"
            cls.record(state, quarterly)
            events.append(quarterly)

        strength = min(
            100,
            22 + int(sect.get("level", 1)) * 8 + int(sect.get("renown", 0)) // 3
            + int(sect.get("buildings", {}).get("ward", 0)) * 5
            + (4 if sect.get("doctrine") == "sword" else 0),
        )
        state.faction_strengths[str(sect["name"])] = strength
        return events

    @staticmethod
    def record(state: GameState, text: str) -> None:
        state.sect_foundation_history.append(f"第 {state.turn} 回合｜{text}")
        state.sect_foundation_history = state.sect_foundation_history[-40:]

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        name = state.pending_sect_name or cls.suggested_name(state)
        return {
            "eyebrow": "开宗立派",
            "title": f"为{name}择定根本道统",
            "hint": f"确认后消耗 {cls.FOUNDATION_COST} 灵石，成为掌门并获得两名开山弟子。",
            "exclusive": True,
            "choices": [
                {
                    "label": doctrine.name,
                    "action": f"立宗道统 {doctrine.id}",
                    "summary": doctrine.effect,
                    "description": doctrine.summary,
                    "tone": "primary" if index == 0 else "quiet",
                }
                for index, doctrine in enumerate(DOCTRINES.values())
            ] + [{"label": "暂缓立宗", "action": "取消立宗", "description": "不消耗资源，返回当前道途。", "tone": "quiet"}],
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        requirements = cls.foundation_requirements(state)
        can_found, found_reason = cls.foundation_availability(state)
        pending = state.phase == "sect_foundation_choice"
        doctrines = [
            {
                "id": item.id, "name": item.name, "mark": item.mark, "summary": item.summary,
                "effect": item.effect, "action": f"立宗道统 {item.id}",
            }
            for item in DOCTRINES.values()
        ]
        if not cls.active(state):
            return {
                "visible": state.player.realm_index >= 2 or pending,
                "founded": False,
                "pending": pending,
                "suggested_name": state.pending_sect_name or cls.suggested_name(state),
                "requirements": requirements,
                "can_found": can_found,
                "found_reason": found_reason,
                "begin_action": f"开宗立派 {cls.suggested_name(state)}",
                "doctrines": doctrines,
                "sect": {}, "disciples": [], "buildings": [], "focuses": [], "history": [],
            }

        sect = state.founded_sect
        doctrine = DOCTRINES.get(str(sect.get("doctrine")), next(iter(DOCTRINES.values())))
        experience = int(sect.get("experience", 0))
        level = int(sect.get("level", 1))
        next_threshold = LEVELS[level][0] if level < len(LEVELS) else LEVELS[-1][0]
        previous_threshold = LEVELS[level - 1][0]
        recruit_left = max(0, 6 - (state.turn - int(sect.get("last_recruit_turn", -999))))
        recruit_reason = ""
        if state.phase != "playing":
            recruit_reason = "请先完成当前抉择"
        elif cls.ruined(state):
            recruit_reason = "山门已经覆灭"
        elif len(state.sect_disciples) >= cls.MAX_DISCIPLES:
            recruit_reason = "山门容纳人数已满"
        elif recruit_left:
            recruit_reason = f"还需等待 {recruit_left} 个月"
        elif int(sect.get("treasury", 0)) < cls.RECRUIT_COST:
            recruit_reason = f"需要 {cls.RECRUIT_COST} 库藏"
        buildings = []
        for definition in BUILDINGS.values():
            current = int(sect.get("buildings", {}).get(definition.id, 0))
            cost = definition.base_cost * (current + 1)
            reason = ""
            if state.phase != "playing":
                reason = "请先完成当前抉择"
            elif cls.ruined(state):
                reason = "山门已经覆灭"
            elif current >= cls.MAX_BUILDING_LEVEL:
                reason = "已经达到上限"
            elif int(sect.get("treasury", 0)) < cost:
                reason = f"库藏不足，还需 {cost - int(sect.get('treasury', 0))}"
            buildings.append({
                "id": definition.id, "name": definition.name, "mark": definition.mark,
                "summary": definition.summary, "level": current, "max_level": cls.MAX_BUILDING_LEVEL,
                "cost": cost, "available": not reason, "disabled_reason": reason,
                "action": f"营造山门 {definition.id}",
            })
        disciples = []
        for disciple in state.sect_disciples:
            realm_index = min(len(REALMS) - 1, int(disciple.get("realm_index", 0)))
            stage_index = min(len(STAGES) - 1, int(disciple.get("stage_index", 0)))
            requirement = 70 + realm_index * 45 + stage_index * 20
            disciples.append({
                **disciple,
                "realm": f"{REALMS[realm_index]}·{STAGES[stage_index]}",
                "progress_required": requirement,
                "progress_percent": min(100, round(int(disciple.get("progress", 0)) / requirement * 100)),
            })
        focus_items = []
        for focus_id, (name, effect) in FOCUSES.items():
            current = sect.get("focus") == focus_id
            reason = ""
            if state.phase != "playing":
                reason = "请先完成当前抉择"
            elif current:
                reason = "当前方针"
            elif int(sect.get("last_focus_year", 0)) == state.calendar_year:
                reason = "本年已经改定过方针"
            focus_items.append({"id": focus_id, "name": name, "effect": effect, "current": current, "available": not reason, "disabled_reason": reason, "action": f"宗门方针 {focus_id}"})
        teach_reason = ""
        if state.phase != "playing":
            teach_reason = "请先完成当前抉择"
        elif int(sect.get("last_teach_year", 0)) == state.calendar_year:
            teach_reason = "本年已经传法"
        elif int(sect.get("treasury", 0)) < cls.TEACH_COST:
            teach_reason = f"需要 {cls.TEACH_COST} 库藏"
        return {
            "visible": True,
            "founded": True,
            "pending": False,
            "suggested_name": str(sect.get("name", "")),
            "requirements": requirements,
            "can_found": False,
            "found_reason": "本世已经开宗立派",
            "begin_action": "",
            "doctrines": doctrines,
            "sect": {
                **sect,
                "doctrine_name": doctrine.name,
                "doctrine_mark": doctrine.mark,
                "doctrine_effect": doctrine.effect,
                "level_name": LEVELS[level - 1][1],
                "experience_required": next_threshold,
                "experience_percent": 100 if level >= len(LEVELS) else min(100, round((experience - previous_threshold) / max(1, next_threshold - previous_threshold) * 100)),
                "strength": int(state.faction_strengths.get(str(sect.get("name")), 0)),
            },
            "disciples": disciples,
            "buildings": buildings,
            "focuses": focus_items,
            "history": list(reversed(state.sect_foundation_history[-10:])),
            "recruit_action": "宗门招徒",
            "can_recruit": not recruit_reason,
            "recruit_reason": recruit_reason,
            "recruit_cost": cls.RECRUIT_COST,
            "teach_action": "宗门传法",
            "can_teach": not teach_reason,
            "teach_reason": teach_reason,
            "teach_cost": cls.TEACH_COST,
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["founded"]:
            requirements = "｜".join(f"{item['label']} {item['current']}/{item['value']}" for item in snapshot["requirements"])
            return f"【开宗立派】{requirements}\n{snapshot['found_reason'] or '输入“开宗立派 [宗门名]”择定道统。'}"
        sect = snapshot["sect"]
        disciples = "、".join(f"{item['name']}（{item['realm']}）" for item in snapshot["disciples"]) or "暂无"
        return (
            f"【{sect['name']} · {sect['level_name']}】{sect['doctrine_name']}｜实力 {sect['strength']}\n"
            f"库藏 {sect['treasury']}（月净 {sect['monthly_net']:+d}）｜声望 {sect['renown']}｜稳定 {sect['stability']}｜门人 {len(snapshot['disciples'])}/{cls.MAX_DISCIPLES}\n"
            f"门人：{disciples}\n指令：宗门招徒／宗门传法／宗门方针 [方针]／营造山门 [设施]"
        )
