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


@dataclass(frozen=True, slots=True)
class SectWarActionResult:
    choice: str
    success: bool
    roll: int
    chance: int
    momentum: int
    description: str


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


class SectWarEngine:
    FACTIONS = ("青云宗", "丹霞谷", "玄剑门", "血煞盟")

    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = f"sect-war:{state.rng_seed}:{state.calendar_year}:{state.month}:{purpose}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % maximum

    @classmethod
    def ensure_strengths(cls, state: GameState) -> None:
        defaults = {"青云宗": 70, "丹霞谷": 64, "玄剑门": 68, "血煞盟": 66}
        for name, strength in defaults.items():
            state.faction_strengths.setdefault(name, strength)

    @classmethod
    def start(cls, state: GameState, attacker: str, defender: str) -> str:
        cls.ensure_strengths(state)
        if attacker == defender or attacker not in cls.FACTIONS or defender not in cls.FACTIONS:
            raise ValueError("宗门战争双方无效。")
        if attacker in state.fallen_factions or defender in state.fallen_factions:
            raise ValueError("已经覆灭的势力不能发动宗门战争。")
        state.active_sect_war = {
            "attacker": attacker,
            "defender": defender,
            "momentum": 0,
            "months": 0,
            "started_year": state.calendar_year,
            "started_month": state.month,
            "player_acted": False,
        }
        state.world_tension = min(100, state.world_tension + 8)
        return f"{attacker}向{defender}宣战，灵舟与护山大阵同时升起。"

    @classmethod
    def maybe_start(cls, state: GameState) -> str:
        if state.active_sect_war or state.month != 3 or (state.calendar_year - 387) % 4 != 0:
            return ""
        alive = [name for name in cls.FACTIONS if name not in state.fallen_factions]
        if len(alive) < 2:
            return ""
        attacker_index = cls._number(state, "attacker", len(alive))
        defender_index = cls._number(state, "defender", len(alive) - 1)
        attacker = alive[attacker_index]
        defenders = [name for name in alive if name != attacker]
        defender = defenders[defender_index]
        return cls.start(state, attacker, defender)

    @classmethod
    def participate(cls, state: GameState, choice: str) -> SectWarActionResult:
        war = state.active_sect_war
        if not war or state.player.sect not in {war.get("attacker"), war.get("defender")}:
            raise ValueError("你的宗门当前并未卷入战争。")
        if war.get("player_acted"):
            raise ValueError("你已经为本次宗门战争作出过选择。")
        if choice not in {"驰援前线", "固守山门", "闭关不出"}:
            raise ValueError("请选择驰援前线、固守山门或闭关不出。")
        direction = 1 if state.player.sect == war["attacker"] else -1
        roll = cls._number(state, f"player:{choice}:{state.turn}", 100) + 1
        chance = 100
        success = True
        effect = 0
        if choice == "驰援前线":
            chance = max(20, min(95, 48 + state.player.realm_index * 10 + state.player.reputation // 5))
            success = roll <= chance
            effect = 2 if success else -1
            state.player.sect_contribution += 100 if success else 20
            state.player.reputation += 8 if success else 1
            if not success:
                state.player.health = max(1, state.player.health - 25)
                state.player.condition = "护宗战负伤"
            description = "你率同门破开敌阵，宗门声势大振。" if success else "你在前线受挫，负伤退回山门。"
        elif choice == "固守山门":
            chance = max(30, min(95, 62 + state.player.dao_heart + state.cave_facilities.get("禁制", 0) * 5))
            success = roll <= chance
            effect = 1 if success else 0
            state.player.sect_contribution += 60 if success else 15
            description = "你稳住护山阵眼，为宗门守住最后退路。" if success else "阵眼几度动摇，你勉强保全自身。"
        else:
            state.player.reputation -= 8
            effect = -1
            description = "你闭门不出，避开杀劫，也让同门记住了你的缺席。"
        war["momentum"] = int(war.get("momentum", 0)) + direction * effect
        war["player_acted"] = True
        return SectWarActionResult(choice, success, roll, chance, int(war["momentum"]), description)

    @classmethod
    def advance(cls, state: GameState) -> str:
        war = state.active_sect_war
        if not war:
            return ""
        war["months"] = int(war.get("months", 0)) + 1
        swing = cls._number(state, f"front:{war['attacker']}:{war['defender']}:{war['months']}", 3) - 1
        war["momentum"] = int(war.get("momentum", 0)) + swing
        if int(war["months"]) < 6 and abs(int(war["momentum"])) < 3:
            return f"{war['attacker']}与{war['defender']}鏖战未休，战局声势 {war['momentum']:+d}。"

        attacker_wins = int(war["momentum"]) >= 0
        winner = str(war["attacker"] if attacker_wins else war["defender"])
        loser = str(war["defender"] if attacker_wins else war["attacker"])
        state.faction_strengths[winner] = min(100, int(state.faction_strengths.get(winner, 50)) + 5)
        state.faction_strengths[loser] = max(0, int(state.faction_strengths.get(loser, 50)) - 14)
        conclusion = f"{winner}赢得宗门战争，{loser}山门受创、势力大损。"
        if state.faction_strengths[loser] <= 15:
            state.faction_strengths[loser] = 0
            if loser not in state.fallen_factions:
                state.fallen_factions.append(loser)
            conclusion = f"{winner}攻破{loser}山门，{loser}自九州势力谱中覆灭。"
            if state.player.sect == loser:
                state.player.tags.append(f"故宗覆灭·{loser}")
                state.player.sect = "散修"
                state.player.sect_rank = "无"
                state.player.sect_contribution = 0
        state.sect_war_history.append(f"天玄历{state.calendar_year}年{state.month}月｜{conclusion}")
        state.sect_war_history = state.sect_war_history[-30:]
        state.active_sect_war = {}
        state.world_tension = max(0, state.world_tension - 3)
        return conclusion


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
        war_started = SectWarEngine.maybe_start(state)
        if war_started:
            events.append(war_started)
        war_update = SectWarEngine.advance(state)
        if war_update:
            events.append(war_update)
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
