from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .progression import ProgressionEngine
from .state import GameState


SECT_RANKS = ("外门弟子", "内门弟子", "真传弟子", "长老", "掌门")
PROMOTION_REQUIREMENTS = {
    "内门弟子": (100, 0),
    "真传弟子": (300, 1),
    "长老": (800, 3),
    "掌门": (1500, 5),
}
SECT_INHERITANCES = {
    "青云宗": "青木长生诀残卷",
    "丹霞谷": "赤炎真经残卷",
    "玄剑门": "太虚剑典残卷",
}


@dataclass(frozen=True, slots=True)
class PromotionResult:
    success: bool
    old_rank: str
    new_rank: str
    roll: int
    chance: int


@dataclass(frozen=True, slots=True)
class TournamentResult:
    success: bool
    roll: int
    chance: int
    contribution: int = 0
    reputation: int = 0
    reward: str = ""


class SectProgressionEngine:
    @staticmethod
    def next_rank(state: GameState) -> str:
        if state.player.sect == "散修":
            raise ValueError("散修没有宗门职位；请先拜入宗门。")
        try:
            index = SECT_RANKS.index(state.player.sect_rank)
        except ValueError as exc:
            raise ValueError(f"未知宗门职位：{state.player.sect_rank}") from exc
        return "" if index == len(SECT_RANKS) - 1 else SECT_RANKS[index + 1]

    @classmethod
    def promotion_requirements(cls, state: GameState) -> tuple[str, int, int]:
        target = cls.next_rank(state)
        if not target:
            return "", 0, 0
        contribution, minimum_realm = PROMOTION_REQUIREMENTS[target]
        return target, contribution, minimum_realm

    @classmethod
    def promote(cls, state: GameState) -> PromotionResult:
        target, contribution, minimum_realm = cls.promotion_requirements(state)
        if not target:
            raise ValueError("你已是掌门，宗门之内再无更高职位。")
        player = state.player
        if player.sect_contribution < contribution:
            raise ValueError(f"晋升{target}需要贡献 {contribution}，当前 {player.sect_contribution}。")
        if player.realm_index < minimum_realm:
            raise ValueError(
                f"晋升{target}至少需要第 {minimum_realm + 1} 大境界，当前为{player.realm}。"
            )
        chance = max(20, min(95, 60 + player.comprehension + player.reputation // 5 + player.realm_index * 5))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-promotion:{player.sect}:{target}:{state.turn}")
        old_rank = player.sect_rank
        success = roll <= chance
        if success:
            player.sect_rank = target
            privilege = f"{player.sect}{target}权限"
            if privilege not in state.sect_privileges:
                state.sect_privileges.append(privilege)
            player.reputation += 5
        else:
            player.reputation = max(-100, player.reputation - 2)
        return PromotionResult(success, old_rank, player.sect_rank, roll, chance)

    @staticmethod
    def tournament_available(state: GameState) -> bool:
        return state.calendar_year >= 390 and (state.calendar_year - 390) % 10 == 0

    @classmethod
    def tournament(cls, state: GameState) -> TournamentResult:
        player = state.player
        if player.sect == "散修":
            raise ValueError("散修不能参加宗门大比。")
        if not cls.tournament_available(state):
            next_year = WorldTimelineEngine.next_year(state.calendar_year, 10, 390)
            raise ValueError(f"本年并非宗门大比之年；下一届为天玄历 {next_year} 年。")
        key = f"{state.calendar_year}:{player.sect}"
        if key in state.sect_tournament_results:
            raise ValueError("你已经参加过本届宗门大比。")
        chance = max(
            10,
            min(95, 45 + player.realm_index * 12 + player.stage_index * 4 + player.reputation // 4 + player.sect_contribution // 25),
        )
        roll = ProgressionEngine.deterministic_roll(state, f"sect-tournament:{key}:{state.turn}")
        success = roll <= chance
        contribution = 120 if success else 20
        reputation = 20 if success else 2
        reward = SECT_INHERITANCES.get(player.sect, "宗门秘传残卷") if success else ""
        player.sect_contribution += contribution
        player.reputation += reputation
        if reward:
            player.resources[reward] = player.resources.get(reward, 0) + 1
        state.sect_tournament_results[key] = "夺魁" if success else "落选"
        return TournamentResult(success, roll, chance, contribution, reputation, reward)

    @staticmethod
    def defect(state: GameState) -> str:
        player = state.player
        if player.sect == "散修":
            raise ValueError("你本就是散修，无宗可叛。")
        old_sect = player.sect
        old_rank = player.sect_rank
        player.sect = "散修"
        player.sect_rank = "无"
        player.sect_contribution = 0
        player.reputation -= 30
        player.karma += 5
        player.tags.append(f"叛离{old_sect}·原{old_rank}")
        state.world_tension += 2
        return old_sect


class WorldTimelineEngine:
    @staticmethod
    def next_year(current: int, interval: int, anchor: int) -> int:
        if current < anchor:
            return anchor
        remainder = (current - anchor) % interval
        return current if remainder == 0 else current + interval - remainder

    @staticmethod
    def _auction_roll(state: GameState) -> int:
        material = f"auction:{state.rng_seed}:{state.calendar_year}:{state.month}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % 100 + 1

    @classmethod
    def tick(cls, state: GameState) -> list[str]:
        key = f"{state.calendar_year}:{state.month}"
        if key in state.world_event_keys:
            return []
        events = []
        year = state.calendar_year
        if state.month == 1:
            if year >= 390 and (year - 390) % 5 == 0:
                events.append("五年一度的升仙大会开幕，各地炼气修士汇聚东洲。")
            if year >= 390 and (year - 390) % 10 == 0:
                events.append("十年一度的宗门大比开启，各宗真传名额与藏经阁权限重新争夺。")
            if year >= 400 and (year - 400) % 20 == 0:
                events.append("猎魔大会发布征召，正魔边境的冲突令九州局势升温。")
                state.world_tension += 5
            if year == 1387:
                events.append("千年灵气潮汐正式降临，沉睡灵脉与域外裂隙同时苏醒。")
                state.aura_level = "福地"
                state.world_tension += 20
        if cls._auction_roll(state) <= 3:
            events.append("天机坊市临时宣布一场拍卖会，珍稀功法与来路不明的宝物即将现世。")
        state.world_event_keys.append(key)
        for event in events:
            state.world_events.append(f"天玄历 {year} 年·{state.month}月｜{event}")
            state.last_world_event = event
        state.world_events = state.world_events[-100:]
        return events

    @classmethod
    def schedule_lines(cls, state: GameState) -> list[str]:
        year = state.calendar_year
        return [
            f"升仙大会：天玄历 {cls.next_year(year, 5, 390)} 年",
            f"宗门大比：天玄历 {cls.next_year(year, 10, 390)} 年",
            f"猎魔大会：天玄历 {cls.next_year(year, 20, 400)} 年",
            "灵气潮汐：天玄历 1387 年",
        ]
