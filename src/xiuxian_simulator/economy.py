from __future__ import annotations

import re
from dataclasses import dataclass, field

from .progression import ProgressionEngine
from .state import GameState
from .travel import REGIONS, TravelEngine


MARKET_PRICES = {
    "聚气丹": 20,
    "疗伤丹": 60,
    "青木长生诀残卷": 600,
    "赤炎真经残卷": 700,
    "太虚剑典残卷": 3200,
    "五行道藏残卷": 12000,
    "青木缚灵术残卷": 250,
    "庚金剑气残卷": 600,
    "玄水剑诀残卷": 1600,
    "厚土印诀残卷": 2200,
    "青锋剑": 180,
    "玄铁剑": 900,
    "火云刃": 1000,
    "护身法袍": 220,
    "流云衣": 1200,
    "玄龟甲": 1800,
    "灵铁": 25,
    "符纸": 5,
    "火球符": 35,
    "神行符": 80,
    "剑穗": 30,
    "清茶": 10,
    "山水画卷": 80,
    "灵石匣": 120,
    "奇闻玉简": 90,
    "烈酒": 20,
    "血玉": 180,
    "冰莲": 150,
    "雪晶": 100,
    "灵果": 15,
    "烤肉": 12,
    "甜糕": 8,
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
    "赤炎岭": (1, 34),
    "万兽荒原": (1, 42),
    "古妖山外围": (2, 54),
    "流沙古道": (3, 48),
    "佛陀遗迹": (3, 58),
    "魔渊外围": (4, 70),
    "雪族边城": (5, 62),
    "寒渊冰湖": (5, 72),
    "幽冥荒冢": (6, 82),
    "天阙仙城": (1, 26),
    "万剑台": (2, 42),
    "天衍古阵": (3, 60),
}

AREA_REGIONS = {
    "青岳山麓": "东洲", "百草谷": "东洲", "迷雾山谷": "东洲", "古战场外围": "东洲",
    "赤炎岭": "南疆", "万兽荒原": "南疆", "古妖山外围": "南疆",
    "流沙古道": "西漠", "佛陀遗迹": "西漠", "魔渊外围": "西漠",
    "雪族边城": "北原", "寒渊冰湖": "北原", "幽冥荒冢": "北原",
    "天阙仙城": "中州", "万剑台": "中州", "天衍古阵": "中州",
}

AREA_DESCRIPTIONS = {
    "青岳山麓": "山路平缓，散修与低阶妖兽都很常见。",
    "百草谷": "灵药繁茂，采药人也常为一株药草争得头破血流。",
    "迷雾山谷": "终年灵雾遮目，筑基修士也可能迷失。",
    "古战场外围": "阴煞未散，残兵与尸傀仍在夜里游荡。",
    "赤炎岭": "地火喷涌，火行灵材与毒虫都藏在岩缝之间。",
    "万兽荒原": "兽潮迁徙的必经之路，猎物与猎人身份随时互换。",
    "古妖山外围": "化形妖族的疆界之外，越界者很少能全身而退。",
    "流沙古道": "商队沿残破石碑辨路，沙暴会抹去一切足迹。",
    "佛陀遗迹": "断壁间仍有梵音，古阵与遗宝同样危险。",
    "魔渊外围": "魔气从地底渗出，具灵以下不宜久留。",
    "雪族边城": "雪族商旅聚居之地，城外却常有冰兽窥伺。",
    "寒渊冰湖": "万年玄冰下有灵光游动，也有东西在敲击冰面。",
    "幽冥荒冢": "鬼火连成河流，具灵修士也可能被拖入冥隙。",
    "天阙仙城": "天下修士摩肩接踵，机缘与争斗都来得更快。",
    "万剑台": "万剑阁弟子试剑之所，遗落剑意可伤神魂。",
    "天衍古阵": "上古阵纹自行生灭，每一步都可能改换方位。",
}

AREA_ENCOUNTERS = {
    "青岳山麓": "噬灵獾", "百草谷": "铁甲妖狼", "迷雾山谷": "雾隐妖蟒", "古战场外围": "阴煞尸傀",
    "赤炎岭": "赤背火蜥", "万兽荒原": "裂风妖虎", "古妖山外围": "化形妖将",
    "流沙古道": "沙海劫修", "佛陀遗迹": "石胎魔僧", "魔渊外围": "噬魂魔影",
    "雪族边城": "寒甲冰熊", "寒渊冰湖": "玄冰蛟", "幽冥荒冢": "幽冥鬼王",
    "天阙仙城": "中州豪客", "万剑台": "试剑傀儡", "天衍古阵": "阵灵化身",
}

REGIONAL_SUPPLY = {
    "东洲": {"灵药": 0.66, "聚气丹": 0.82, "清茶": 0.72},
    "南疆": {"妖兽材料": 0.66, "火云刃": 0.8, "烈酒": 0.76},
    "西漠": {"符纸": 0.64, "火球符": 0.78, "灵铁": 0.78},
    "北原": {"冰莲": 0.64, "雪晶": 0.65, "玄龟甲": 0.82},
    "中州": {"奇闻玉简": 0.76, "山水画卷": 0.8, "青木长生诀残卷": 0.85},
}

REGIONAL_DEMAND = {
    "东洲": {"妖兽材料": 1.5, "雪晶": 1.55},
    "南疆": {"灵药": 1.5, "清茶": 1.45},
    "西漠": {"灵药": 1.35, "冰莲": 1.45},
    "北原": {"疗伤丹": 1.5, "烈酒": 1.45},
    "中州": {"天材地宝": 1.35, "妖兽材料": 1.45},
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
    encounter: str = ""


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
    def regional_price(state: GameState, item: str, operation: str) -> int:
        if item not in MARKET_PRICES:
            raise ValueError(f"坊市暂无此物：{item}")
        region = TravelEngine.current_region(state)
        prosperity = int(state.regional_prosperity.get(region, 50))
        base = MARKET_PRICES[item]
        if operation == "买":
            supply = REGIONAL_SUPPLY.get(region, {}).get(item, 1.0)
            prosperity_factor = 1.0 + (60 - prosperity) * 0.003
            return max(1, round(base * supply * prosperity_factor))
        if operation == "卖":
            demand = REGIONAL_DEMAND.get(region, {}).get(item, 1.0)
            prosperity_factor = 1.0 + (prosperity - 60) * 0.002
            return max(1, round(base * 0.6 * demand * prosperity_factor))
        raise ValueError("交易指令必须是买或卖。")

    @classmethod
    def market_lines(cls, state: GameState) -> list[str]:
        return [
            f"{name}：买 {cls.regional_price(state, name, '买')}／卖 {cls.regional_price(state, name, '卖')} 灵石"
            for name in MARKET_PRICES
        ]

    @staticmethod
    def market_context(state: GameState) -> tuple[str, str, str]:
        key = TravelEngine.current_region(state)
        region = REGIONS[key]
        return "、".join(region.specialties), "、".join(region.demands), f"{state.trade_profit:+d}"

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
        price = cls.regional_price(state, item, operation)
        if operation == "买":
            total = price * count
            if state.player.spirit_stones < total:
                raise ValueError(f"灵石不足：需要 {total}，当前 {state.player.spirit_stones}。")
            state.player.spirit_stones -= total
            cls.add_resources(state, {item: count})
            cargo = state.trade_cargo.setdefault(item, {"quantity": 0, "cost": 0})
            cargo["quantity"] = int(cargo.get("quantity", 0)) + count
            cargo["cost"] = int(cargo.get("cost", 0)) + total
            return -total, count
        if operation == "卖":
            owned = state.player.resources.get(item, 0)
            if owned < count:
                raise ValueError(f"持有数量不足：{item}×{owned}，试图出售 {count}。")
            total = price * count
            cargo = state.trade_cargo.get(item, {})
            tracked_quantity = int(cargo.get("quantity", 0))
            tracked_cost = int(cargo.get("cost", 0))
            sold_from_cargo = min(count, tracked_quantity)
            realized_cost = round(tracked_cost * sold_from_cargo / tracked_quantity) if tracked_quantity else 0
            state.trade_profit += price * sold_from_cargo - realized_cost
            if sold_from_cargo:
                remaining_quantity = tracked_quantity - sold_from_cargo
                remaining_cost = tracked_cost - realized_cost
                if remaining_quantity:
                    state.trade_cargo[item] = {"quantity": remaining_quantity, "cost": remaining_cost}
                else:
                    state.trade_cargo.pop(item, None)
            state.player.resources[item] = owned - count
            if state.player.resources[item] <= 0:
                state.player.resources.pop(item, None)
                if state.player.equipped_weapon == item:
                    state.player.equipped_weapon = ""
                if state.player.equipped_armor == item:
                    state.player.equipped_armor = ""
            state.player.spirit_stones += total
            return total, -count
        raise ValueError("交易指令必须是买或卖。")

    @classmethod
    def explore(cls, state: GameState, area: str) -> ExplorationResult:
        if area not in AREAS:
            raise ValueError("未知区域。可探索：" + "、".join(AREAS))
        minimum_realm, danger = AREAS[area]
        current_region = TravelEngine.current_region(state)
        area_region = AREA_REGIONS[area]
        if current_region != area_region:
            raise ValueError(f"{area}位于{REGIONS[area_region].name}；请先在九州舆图规划行程。")
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
        encounter = ""

        if score <= danger:
            encounter = AREA_ENCOUNTERS[area]
            event = f"遭遇{encounter}拦路，必须判断战或逃"
        elif score < 58:
            count = 1 + score % 3
            resource = {"东洲": "灵药", "南疆": "妖兽材料", "西漠": "灵铁", "北原": "冰莲", "中州": "符纸"}[area_region]
            rewards = {resource: count}
            event = f"在当地险地寻得{resource}"
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

        player.location = f"{REGIONS[area_region].name}·{area}"
        player.spirit_stones += stones
        cls.add_resources(state, rewards)
        return ExplorationResult(area, roll, event, rewards, stones, health_loss, fatal, encounter)

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
