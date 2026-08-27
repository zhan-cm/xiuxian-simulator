from __future__ import annotations

import re
from dataclasses import dataclass, field

from .progression import ProgressionEngine
from .state import GameState


MARKET_PRICES = {
    "聚气丹": 20,
    "筑基丹": 500,
    "凝晶丹": 1200,
    "结丹灵药": 3000,
    "结婴丹": 8000,
    "具灵丹": 18000,
    "化神丹": 40000,
    "悟道丹": 80000,
    "羽化丹": 160000,
    "登仙丹": 320000,
    "灵药": 12,
    "妖兽材料": 30,
    "天材地宝": 2500,
    "五行灵珠": 4000,
    "道韵": 8000,
}

AREAS = {
    "青岳山麓": (0, 12),
    "百草谷": (0, 18),
    "迷雾山谷": (1, 28),
    "古战场外围": (2, 38),
}

SECTS = ("青云宗", "丹霞谷", "玄剑门")
SECT_TASKS = {
    "采药": ("fortune", 30, 8, {"灵药": 2}),
    "巡逻": ("spirit_sense", 45, 10, {}),
    "猎妖": ("speed", 60, 12, {"妖兽材料": 1}),
    "护送": ("dao_heart", 80, 14, {}),
    "镇守": ("spirit_sense", 100, 18, {"灵药": 1}),
}


@dataclass(frozen=True, slots=True)
class ExplorationResult:
    area: str
    roll: int
    event: str
    rewards: dict[str, int] = field(default_factory=dict)
    spirit_stones: int = 0
    health_loss: int = 0
    fatal: bool = False


@dataclass(frozen=True, slots=True)
class SectTaskResult:
    task: str
    success: bool
    roll: int
    chance: int
    spirit_stones: int = 0
    contribution: int = 0
    rewards: dict[str, int] = field(default_factory=dict)
    health_loss: int = 0
    fatal: bool = False


class EconomyEngine:
    @staticmethod
    def add_resources(state: GameState, rewards: dict[str, int]) -> None:
        for name, count in rewards.items():
            if count > 0:
                state.player.resources[name] = state.player.resources.get(name, 0) + count

    @staticmethod
    def market_lines() -> list[str]:
        return [
            f"{name}：买 {price}／卖 {max(1, price * 3 // 5)} 灵石"
            for name, price in MARKET_PRICES.items()
        ]

    @staticmethod
    def parse_trade(action: str) -> tuple[str, str, int] | None:
        text = action.strip()
        if text.startswith("坊市 "):
            text = text.removeprefix("坊市 ").strip()
        match = re.fullmatch(r"(买|卖)\s*(\S+?)(?:\s*[×xX*]?\s*(\d+))?", text)
        if not match:
            return None
        return match.group(1), match.group(2), int(match.group(3) or 1)

    @classmethod
    def trade(cls, state: GameState, operation: str, item: str, count: int) -> tuple[int, int]:
        if item not in MARKET_PRICES:
            raise ValueError(f"坊市暂无此物：{item}")
        if count < 1 or count > 999:
            raise ValueError("交易数量必须在 1～999 之间。")
        price = MARKET_PRICES[item]
        if operation == "买":
            total = price * count
            if state.player.spirit_stones < total:
                raise ValueError(f"灵石不足：需要 {total}，当前 {state.player.spirit_stones}。")
            state.player.spirit_stones -= total
            cls.add_resources(state, {item: count})
            return -total, count
        if operation == "卖":
            owned = state.player.resources.get(item, 0)
            if owned < count:
                raise ValueError(f"持有数量不足：{item}×{owned}，试图出售 {count}。")
            total = max(1, price * 3 // 5) * count
            state.player.resources[item] = owned - count
            if state.player.resources[item] <= 0:
                state.player.resources.pop(item, None)
            state.player.spirit_stones += total
            return total, -count
        raise ValueError("交易指令必须是买或卖。")

    @classmethod
    def explore(cls, state: GameState, area: str) -> ExplorationResult:
        if area not in AREAS:
            raise ValueError("未知区域。可探索：" + "、".join(AREAS))
        minimum_realm, danger = AREAS[area]
        player = state.player
        if player.realm_index < minimum_realm:
            raise ValueError(
                f"【危险警告】{area}至少需要{minimum_realm + 1}阶大境界实力；"
                f"当前为{player.realm}，贸然深入近乎送死。"
            )
        roll = ProgressionEngine.deterministic_roll(state, f"explore:{area}:{state.turn}")
        score = roll + (player.fortune - 10) + player.realm_index * 2
        rewards: dict[str, int] = {}
        stones = 0
        health_loss = 0
        fatal = False

        if score <= danger:
            escape_roll = ProgressionEngine.deterministic_roll(state, f"explore-escape:{area}:{state.turn}")
            escape_chance = max(10, min(95, 45 + player.speed + player.spirit_sense + player.realm_index * 5 - danger))
            if escape_roll <= escape_chance:
                event = f"遭遇妖兽后及时退走（遁逃 {escape_roll}/{escape_chance}）"
            else:
                health_loss = 18 + danger + player.realm_index * 4
                player.health = max(0, player.health - health_loss)
                fatal = player.health <= 0
                event = "遭妖兽伏击，重伤而退" if not fatal else "遭妖兽伏击，陨落荒野"
        elif score < 58:
            count = 1 + score % 3
            rewards = {"灵药": count}
            event = "在山野间寻得一片灵药"
        elif score < 76:
            count = 1 + score % 2
            rewards = {"妖兽材料": count}
            event = "拾得斗法后遗落的妖兽材料"
        elif score < 90:
            stones = 20 + player.realm_index * 20 + score % 21
            event = "发现散修遗落的灵石袋"
        elif score < 97:
            rewards = {"天材地宝": 1}
            event = "寻得一株初生的天材地宝"
        elif score < 100:
            rewards = {"五行灵珠": 1}
            event = "在灵脉裂隙中凝得五行灵珠"
        else:
            rewards = {"道韵": 1}
            event = "观天地异象，截得一缕道韵"

        player.location = f"东洲·{area}"
        player.spirit_stones += stones
        cls.add_resources(state, rewards)
        if fatal:
            player.condition = "陨落于野外探索"
            state.phase = "ended"
        return ExplorationResult(area, roll, event, rewards, stones, health_loss, fatal)

    @staticmethod
    def join_sect(state: GameState, sect: str) -> tuple[bool, int, int]:
        if sect not in SECTS:
            raise ValueError("当前可申请：" + "、".join(SECTS))
        if state.player.sect != "散修":
            raise ValueError(f"你已是{state.player.sect}·{state.player.sect_rank}，不能重复拜入宗门。")
        player = state.player
        chance = max(20, min(95, 55 + player.aptitude + player.comprehension // 2 + player.reputation // 5))
        roll = ProgressionEngine.deterministic_roll(state, f"join-sect:{sect}:{state.turn}")
        if roll <= chance:
            player.sect = sect
            player.sect_rank = "外门弟子"
            player.reputation += 2
            return True, roll, chance
        return False, roll, chance

    @classmethod
    def sect_task(cls, state: GameState, task: str) -> SectTaskResult:
        if state.player.sect == "散修":
            raise ValueError("散修没有宗门任务；请先输入“拜入 青云宗”等指令参加入门试炼。")
        if task not in SECT_TASKS:
            raise ValueError("可领取任务：" + "、".join(SECT_TASKS))
        attribute, stones, contribution, rewards = SECT_TASKS[task]
        player = state.player
        value = getattr(player, attribute)
        chance = max(20, min(95, 58 + value * 2 + player.realm_index * 5))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-task:{task}:{state.turn}")
        if roll <= chance:
            player.spirit_stones += stones
            player.sect_contribution += contribution
            cls.add_resources(state, rewards)
            return SectTaskResult(task, True, roll, chance, stones, contribution, dict(rewards))

        health_loss = 0
        fatal = False
        if task in {"猎妖", "护送", "镇守"}:
            health_loss = 15 + (5 if task == "镇守" else 0)
            player.health = max(0, player.health - health_loss)
            fatal = player.health <= 0
            if fatal:
                player.condition = f"陨落于宗门{task}任务"
                state.phase = "ended"
        return SectTaskResult(task, False, roll, chance, health_loss=health_loss, fatal=fatal)
