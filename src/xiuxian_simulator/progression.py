from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from .dao import DaoEngine
from .state import GameState, PlayerState


REALMS = ("炼气", "筑基", "结晶", "金丹", "具灵", "元婴", "化神", "悟道", "羽化", "登仙")
STAGES = ("初期", "中期", "后期", "圆满")

BASE_CULTIVATION = (10.0, 9.0, 8.5, 8.0, 7.5, 7.0, 6.0, 5.0, 4.0, 3.0)
STAGE_REQUIREMENTS = (100, 200, 350, 500, 750, 1000, 1500, 2500, 4000, 6000)
LIFESPANS = (100, 200, 300, 500, 800, 1200, 2000, 5000, 10000, 50000)

HUMAN_PILLS = ("筑基丹", "凝晶丹", "结丹灵药", "结婴丹", "具灵丹", "化神丹", "悟道丹", "羽化丹", "登仙丹")
MAJOR_BASE_RATES = {
    "人道": (95, 90, 85, 80, 75, 70, 60, 50, 30),
    "地道": (85, 80, 75, 70, 65, 60, 50, 40, 20),
    "天道": (70, 65, 60, 55, 50, 45, 35, 25, 9),
}

DESTINY_TRAITS = (
    "剑心通明",
    "丹药精通",
    "气运如虹",
    "肉身成圣",
    "天眼通",
    "双修悟道",
    "聚灵体",
    "心如磐石",
    "万里神行",
    "灵兽亲和",
    "血魔噬魂",
    "大道之体",
)

TECHNIQUE_MULTIPLIERS = {
    "黄阶": 1.0,
    "玄阶": 1.3,
    "地阶": 1.7,
    "天阶": 2.2,
    "仙阶": 3.0,
}

AURA_MULTIPLIERS = {
    "贫瘠": 0.6,
    "普通": 1.0,
    "浓郁": 1.5,
    "福地": 2.0,
    "洞天": 2.5,
}


@dataclass(frozen=True, slots=True)
class CultivationBreakdown:
    base: float
    aptitude: float
    spiritual_root: float
    technique: float
    aura: float
    mindset: float
    constitution: float
    formation: float
    retreat: float
    total: int

    def summary(self) -> str:
        return (
            f"基数 {self.base:g} × 资质 {self.aptitude:.2f} × 灵根 {self.spiritual_root:.2f} × "
            f"功法 {self.technique:.2f} × 灵气 {self.aura:.2f} × 心境 {self.mindset:.2f} × "
            f"体质 {self.constitution:.2f} × 阵法 {self.formation:.2f} × 闭关 {self.retreat:.2f} = {self.total}"
        )


@dataclass(frozen=True, slots=True)
class BreakthroughResult:
    success: bool
    roll: int
    chance: int
    old_realm: str
    new_realm: str
    cultivation_after: int


@dataclass(frozen=True, slots=True)
class MajorBreakthroughResult:
    success: bool
    route: str
    old_realm: str
    new_realm: str
    heart_roll: int
    heart_chance: int
    thunder_roll: int
    thunder_chance: int
    failure_type: str = ""
    fatal: bool = False


class ProgressionEngine:
    @staticmethod
    def spiritual_root_multiplier(root: str) -> float:
        text = root.strip()
        if "变异" in text or any(name in text for name in ("雷灵根", "风灵根", "冰灵根", "阴灵根", "阳灵根")):
            return 1.8
        if "天灵根" in text:
            return 2.0
        if "地灵根" in text or "双灵根" in text:
            return 1.6
        if "真灵根" in text or "三灵根" in text:
            return 1.3
        if "伪灵根" in text or "四灵根" in text or "五灵根" in text:
            return 1.0
        elements = sum(symbol in text for symbol in "金木水火土")
        if elements <= 1:
            return 2.0
        if elements == 2:
            return 1.6
        if elements == 3:
            return 1.3
        return 1.0

    @staticmethod
    def mindset_multiplier(player: PlayerState) -> float:
        requirement = 10 + player.realm_index * 2
        if player.dao_heart >= requirement + 3:
            return 1.2
        if player.dao_heart >= requirement:
            return 1.0
        return 0.5

    @classmethod
    def cultivation_gain(cls, state: GameState, retreat: bool = False) -> CultivationBreakdown:
        player = state.player
        realm_index = max(0, min(player.realm_index, len(REALMS) - 1))
        base = BASE_CULTIVATION[realm_index]
        aptitude = 1 + player.aptitude * 0.05
        spiritual_root = cls.spiritual_root_multiplier(player.spiritual_root)
        technique = TECHNIQUE_MULTIPLIERS.get(player.primary_technique_grade, 1.0)
        from .art_mastery import ArtMasteryEngine

        technique *= ArtMasteryEngine.cultivation_multiplier(state, player.primary_technique)
        aura = AURA_MULTIPLIERS.get(state.aura_level, 1.0)
        mindset = cls.mindset_multiplier(player)
        constitution = player.modifiers.get("cultivation_multiplier", 1.0)
        formation = 1.0
        if state.active_formation == "spirit-gathering" and int(state.formation_arrays.get("spirit-gathering", {}).get("integrity", 0)) > 0:
            formation = 1.05 + player.craft_skills.get("阵法", 0) * 0.02 + player.dao_levels.get("阵道", 0) * 0.02
        retreat_multiplier = 2.0 * (1 + state.cave_facilities.get("静室", 0) * 0.1) if retreat else 1.0
        total = max(1, round(base * aptitude * spiritual_root * technique * aura * mindset * constitution * formation * retreat_multiplier))
        return CultivationBreakdown(
            base=base,
            aptitude=aptitude,
            spiritual_root=spiritual_root,
            technique=technique,
            aura=aura,
            mindset=mindset,
            constitution=constitution,
            formation=formation,
            retreat=retreat_multiplier,
            total=total,
        )

    @staticmethod
    def sync_realm(player: PlayerState) -> None:
        player.realm_index = max(0, min(player.realm_index, len(REALMS) - 1))
        player.stage_index = max(0, min(player.stage_index, len(STAGES) - 1))
        player.realm = f"{REALMS[player.realm_index]}·{STAGES[player.stage_index]}"
        player.cultivation_required = STAGE_REQUIREMENTS[player.realm_index]
        player.lifespan = max(player.lifespan, LIFESPANS[player.realm_index])

    @classmethod
    def cultivate(cls, state: GameState, months: int = 1, retreat: bool = False) -> tuple[int, CultivationBreakdown, int]:
        if months < 1:
            raise ValueError("修炼月数必须至少为 1。")
        breakdown = cls.cultivation_gain(state, retreat=retreat)
        before = state.player.cultivation
        remaining = state.player.cultivation_required - before
        if remaining <= 0:
            return 0, breakdown, 0
        months_used = min(months, math.ceil(remaining / breakdown.total))
        gain = min(remaining, breakdown.total * months_used)
        state.player.cultivation += max(0, gain)
        return max(0, gain), breakdown, months_used

    @staticmethod
    def deterministic_roll(state: GameState, purpose: str) -> int:
        material = f"{state.rng_seed}:{state.rng_counter}:{purpose}".encode("utf-8")
        state.rng_counter += 1
        digest = hashlib.sha256(material).digest()
        return int.from_bytes(digest[:8], "big") % 100 + 1

    @classmethod
    def small_breakthrough(cls, state: GameState) -> BreakthroughResult:
        player = state.player
        cls.sync_realm(player)
        if player.breakthrough_cooldown_months > 0:
            raise ValueError(f"突破反噬尚未平复，还需休养 {player.breakthrough_cooldown_months} 个月。")
        if player.stage_index >= len(STAGES) - 1:
            raise ValueError("当前已是本境圆满，大境界突破需选择人道、地道或天道路线。")
        if player.cultivation < player.cultivation_required:
            raise ValueError(f"修为尚未圆满：{player.cultivation}/{player.cultivation_required}。")

        chance = 75 + (player.comprehension - 10) * 2 + (player.dao_heart - (10 + player.realm_index * 2))
        chance = max(5, min(95, chance))
        old_realm = player.realm
        roll = cls.deterministic_roll(state, f"small-breakthrough:{player.realm_index}:{player.stage_index}")
        success = roll <= chance
        if success:
            player.stage_index += 1
            player.cultivation = 0
            cls.sync_realm(player)
        else:
            player.cultivation = round(player.cultivation_required * 0.7)
        return BreakthroughResult(success, roll, chance, old_realm, player.realm, player.cultivation)

    @staticmethod
    def major_requirements(player: PlayerState, route: str) -> dict[str, int]:
        if route not in MAJOR_BASE_RATES:
            raise ValueError("破境路线必须是人道、地道或天道。")
        if player.realm_index >= len(REALMS) - 1:
            raise ValueError("已至登仙之境，无更高大境界可破。")
        if route == "人道":
            return {HUMAN_PILLS[player.realm_index]: 1}
        if route == "地道":
            return {"天材地宝": 1}
        return {"天材地宝": 1, "五行灵珠": 1, "道韵": 1}

    @staticmethod
    def major_chances(player: PlayerState, route: str) -> tuple[int, int]:
        if route not in MAJOR_BASE_RATES:
            raise ValueError("破境路线必须是人道、地道或天道。")
        base_rate = MAJOR_BASE_RATES[route][player.realm_index]
        gate = math.sqrt(base_rate * 100)
        heart_chance = round(gate + (player.dao_heart - 10) * 1.2)
        thunder_chance = round(gate + (player.fortune - 10) * 0.8 + player.merit * 0.15 - player.karma * 0.25)
        return max(5, min(99, heart_chance)), max(5, min(99, thunder_chance))

    @classmethod
    def major_chances_for_state(cls, state: GameState, route: str) -> tuple[int, int]:
        heart, thunder = cls.major_chances(state.player, route)
        return min(99, heart + DaoEngine.heart_trial_bonus(state)), thunder

    @classmethod
    def major_breakthrough(cls, state: GameState, route: str) -> MajorBreakthroughResult:
        player = state.player
        cls.sync_realm(player)
        if player.breakthrough_cooldown_months > 0:
            raise ValueError(f"突破反噬尚未平复，还需休养 {player.breakthrough_cooldown_months} 个月。")
        if player.stage_index != len(STAGES) - 1 or player.cultivation < player.cultivation_required:
            raise ValueError(
                f"大境界突破要求当前境界圆满且修为满值；当前 {player.realm}，"
                f"修为 {player.cultivation}/{player.cultivation_required}。"
            )

        requirements = cls.major_requirements(player, route)
        missing = [f"{name}×{count}" for name, count in requirements.items() if player.resources.get(name, 0) < count]
        if missing:
            raise ValueError(f"{route}突破资源不足：" + "、".join(missing))
        for name, count in requirements.items():
            player.resources[name] -= count
            if player.resources[name] <= 0:
                player.resources.pop(name, None)

        heart_chance, thunder_chance = cls.major_chances_for_state(state, route)
        old_realm = player.realm
        heart_roll = cls.deterministic_roll(state, f"heart-demon:{route}:{player.realm_index}")
        thunder_roll = cls.deterministic_roll(state, f"thunder:{route}:{player.realm_index}")
        heart_pass = heart_roll <= heart_chance
        thunder_pass = thunder_roll <= thunder_chance
        success = heart_pass and thunder_pass
        failure_type = ""
        fatal = False

        if success:
            player.realm_index += 1
            player.stage_index = 0
            player.cultivation = 0
            cls.sync_realm(player)
            cls._apply_route_reward(player, route)
        else:
            failure_type = "心魔劫" if not heart_pass else "雷劫"
            fatal = cls._apply_major_failure(state, failure_type)

        return MajorBreakthroughResult(
            success=success,
            route=route,
            old_realm=old_realm,
            new_realm=player.realm,
            heart_roll=heart_roll,
            heart_chance=heart_chance,
            thunder_roll=thunder_roll,
            thunder_chance=thunder_chance,
            failure_type=failure_type,
            fatal=fatal,
        )

    @staticmethod
    def _apply_route_reward(player: PlayerState, route: str) -> None:
        if route == "人道":
            player.health_max += 20
            player.spirit_max += 20
        elif route == "地道":
            for attribute in ("aptitude", "comprehension", "spirit_sense", "speed", "dao_heart", "fortune"):
                setattr(player, attribute, min(20, getattr(player, attribute) + 1))
            player.health_max += 40
            player.spirit_max += 40
        else:
            for attribute in ("aptitude", "comprehension", "spirit_sense", "speed", "dao_heart", "fortune"):
                setattr(player, attribute, min(20, getattr(player, attribute) + 2))
            player.health_max += 80
            player.spirit_max += 80
        player.health = player.health_max
        player.spirit = player.spirit_max
        player.breakthrough_quality[player.realm_index] = route

    @classmethod
    def _apply_major_failure(cls, state: GameState, failure_type: str) -> bool:
        player = state.player
        if player.realm_index <= 1:
            player.health = max(1, round(player.health_max * 0.4))
            player.condition = f"重伤（{failure_type}反噬）"
            player.cultivation = round(player.cultivation_required * 0.7)
            player.breakthrough_cooldown_months = 6
            return False
        if player.realm_index <= 5:
            player.stage_index = max(0, player.stage_index - 1)
            player.cultivation = 0
            player.condition = f"暗伤（{failure_type}）"
            player.modifiers["cultivation_multiplier"] = round(
                player.modifiers.get("cultivation_multiplier", 1.0) * 0.9,
                4,
            )
            player.breakthrough_cooldown_months = 24
            cls.sync_realm(player)
            return False

        death_roll = cls.deterministic_roll(state, f"high-realm-failure:{failure_type}:{player.realm_index}")
        if death_roll <= 50:
            player.health = 0
            player.condition = f"陨落于{failure_type}"
            state.phase = "ended"
            return True
        player.stage_index = max(0, player.stage_index - 1)
        player.cultivation = 0
        player.karma += 20
        player.condition = f"走火入魔（{failure_type}）"
        player.breakthrough_cooldown_months = 120
        cls.sync_realm(player)
        return False

    @classmethod
    def destiny_choices(cls, state: GameState, count: int = 3) -> list[str]:
        available = [trait for trait in DESTINY_TRAITS if trait not in state.player.destiny_traits]
        choices: list[str] = []
        while available and len(choices) < count:
            roll = cls.deterministic_roll(state, f"destiny-choice:{len(choices)}")
            index = (roll - 1) % len(available)
            choices.append(available.pop(index))
        return choices

    @staticmethod
    def apply_destiny_trait(player: PlayerState, trait: str) -> None:
        if trait not in DESTINY_TRAITS:
            raise ValueError(f"未知逆天改命：{trait}")
        if trait in player.destiny_traits:
            raise ValueError(f"已拥有逆天改命：{trait}")
        player.destiny_traits.append(trait)
        if trait == "剑心通明":
            player.modifiers["sword_damage_multiplier"] = player.modifiers.get("sword_damage_multiplier", 1.0) + 0.2
        elif trait == "丹药精通":
            player.alchemy_level += 1
        elif trait == "气运如虹":
            player.fortune = min(20, player.fortune + 2)
        elif trait == "肉身成圣":
            player.health_max = round(player.health_max * 1.2)
            player.health = player.health_max
        elif trait == "天眼通":
            player.spirit_sense = min(20, player.spirit_sense + 3)
        elif trait == "双修悟道":
            player.modifiers["dual_cultivation_multiplier"] = 1.5
        elif trait == "聚灵体":
            player.modifiers["cultivation_multiplier"] = player.modifiers.get("cultivation_multiplier", 1.0) * 1.15
        elif trait == "心如磐石":
            player.dao_heart = min(20, player.dao_heart + 3)
            player.tags.append("可抵挡一次心魔")
        elif trait == "万里神行":
            player.speed = min(20, player.speed + 3)
        elif trait == "灵兽亲和":
            player.tags.append("御兽等级+1")
        elif trait == "血魔噬魂":
            player.tags.append("击杀回血")
        elif trait == "大道之体":
            for attribute in ("aptitude", "comprehension", "spirit_sense", "speed", "dao_heart", "fortune"):
                setattr(player, attribute, min(20, getattr(player, attribute) + 1))

    @staticmethod
    def parse_retreat_months(action: str) -> int | None:
        match = re.fullmatch(r"闭关(?:修炼)?\s*(\d+)\s*(个月|月|年)", action.strip())
        if not match:
            return None
        amount = int(match.group(1))
        if amount < 1:
            return None
        months = amount * 12 if match.group(2) == "年" else amount
        return min(months, 1200)
