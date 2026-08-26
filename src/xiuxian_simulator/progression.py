from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from .state import GameState, PlayerState


REALMS = ("炼气", "筑基", "结晶", "金丹", "具灵", "元婴", "化神", "悟道", "羽化", "登仙")
STAGES = ("初期", "中期", "后期", "圆满")

BASE_CULTIVATION = (10.0, 9.0, 8.5, 8.0, 7.5, 7.0, 6.0, 5.0, 4.0, 3.0)
STAGE_REQUIREMENTS = (100, 200, 350, 500, 750, 1000, 1500, 2500, 4000, 6000)
LIFESPANS = (100, 200, 300, 500, 800, 1200, 2000, 5000, 10000, 50000)

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
    retreat: float
    total: int

    def summary(self) -> str:
        return (
            f"基数 {self.base:g} × 资质 {self.aptitude:.2f} × 灵根 {self.spiritual_root:.2f} × "
            f"功法 {self.technique:.2f} × 灵气 {self.aura:.2f} × 心境 {self.mindset:.2f} × "
            f"体质 {self.constitution:.2f} × 闭关 {self.retreat:.2f} = {self.total}"
        )


@dataclass(frozen=True, slots=True)
class BreakthroughResult:
    success: bool
    roll: int
    chance: int
    old_realm: str
    new_realm: str
    cultivation_after: int


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
        aura = AURA_MULTIPLIERS.get(state.aura_level, 1.0)
        mindset = cls.mindset_multiplier(player)
        constitution = player.modifiers.get("cultivation_multiplier", 1.0)
        retreat_multiplier = 2.0 if retreat else 1.0
        total = max(1, round(base * aptitude * spiritual_root * technique * aura * mindset * constitution * retreat_multiplier))
        return CultivationBreakdown(
            base=base,
            aptitude=aptitude,
            spiritual_root=spiritual_root,
            technique=technique,
            aura=aura,
            mindset=mindset,
            constitution=constitution,
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
    def parse_retreat_months(action: str) -> int | None:
        match = re.fullmatch(r"闭关(?:修炼)?\s*(\d+)\s*(个月|月|年)", action.strip())
        if not match:
            return None
        amount = int(match.group(1))
        if amount < 1:
            return None
        months = amount * 12 if match.group(2) == "年" else amount
        return min(months, 1200)
