from __future__ import annotations

from dataclasses import dataclass

from .progression import ProgressionEngine, REALMS
from .state import GameState


@dataclass(frozen=True, slots=True)
class Region:
    key: str
    name: str
    minimum_realm: int
    danger: int
    description: str
    specialties: tuple[str, ...]
    demands: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TravelResult:
    origin: str
    destination: str
    method: str
    months: int
    roll: int
    chance: int
    stone_cost: int
    spirit_cost: int
    health_loss: int
    fatal: bool
    event: str


REGIONS: dict[str, Region] = {
    "东洲": Region("东洲", "东洲·青岳", 0, 12, "散修与凡人杂居，青云宗和天机坊市守望青岳。", ("灵药", "聚气丹", "清茶"), ("妖兽材料", "雪晶")),
    "南疆": Region("南疆", "南疆·赤炎", 1, 34, "火脉纵横，妖兽成群，赤阳宗与万兽谷各据一方。", ("妖兽材料", "火云刃", "烈酒"), ("灵药", "清茶")),
    "西漠": Region("西漠", "西漠·流沙", 3, 52, "流沙掩埋上古遗迹，佛门净土与魔渊仅一线之隔。", ("符纸", "火球符", "灵铁"), ("灵药", "冰莲")),
    "北原": Region("北原", "北原·寒渊", 5, 72, "长夜雪暴笼罩寒渊，雪族与幽冥殿在裂隙两侧对峙。", ("冰莲", "雪晶", "玄龟甲"), ("疗伤丹", "烈酒")),
    "中州": Region("中州", "中州·天阙", 1, 28, "天下道统汇聚天阙，珍宝云集，也最不缺恃强凌弱之人。", ("奇闻玉简", "山水画卷", "青木长生诀残卷"), ("天材地宝", "妖兽材料")),
}

REGION_ORDER = ("东洲", "南疆", "西漠", "北原", "中州")

DISTANCES: dict[tuple[str, str], int] = {
    ("东洲", "南疆"): 3,
    ("东洲", "西漠"): 4,
    ("东洲", "北原"): 4,
    ("东洲", "中州"): 2,
    ("南疆", "西漠"): 4,
    ("南疆", "北原"): 5,
    ("南疆", "中州"): 2,
    ("西漠", "北原"): 4,
    ("西漠", "中州"): 2,
    ("北原", "中州"): 3,
}

METHOD_LABELS = {"caravan": "随商队同行", "swift": "御风独行"}


class TravelEngine:
    @staticmethod
    def current_region(state: GameState) -> str:
        location = state.player.location
        for key in REGION_ORDER:
            if location.startswith(key):
                return key
        return "东洲"

    @staticmethod
    def normalize_destination(destination: str) -> str:
        text = destination.strip()
        for key, region in REGIONS.items():
            if text in {key, region.name} or text.startswith(key):
                return key
        raise ValueError("未知地域。可前往：" + "、".join(REGION_ORDER))

    @staticmethod
    def distance(origin: str, destination: str) -> int:
        if origin == destination:
            return 0
        return DISTANCES.get((origin, destination), DISTANCES.get((destination, origin), 4))

    @classmethod
    def duration(cls, origin: str, destination: str, method: str = "") -> int:
        distance = cls.distance(origin, destination)
        if method == "caravan":
            return distance + 1
        if method == "swift":
            return max(1, distance - 1)
        return distance

    @staticmethod
    def requirement_label(minimum_realm: int) -> str:
        return f"{REALMS[min(minimum_realm, len(REALMS) - 1)]}可达"

    @classmethod
    def prepare(cls, state: GameState, destination: str) -> dict[str, object]:
        key = cls.normalize_destination(destination)
        origin = cls.current_region(state)
        region = REGIONS[key]
        if key == origin:
            raise ValueError(f"你已经身在{region.name}。")
        if state.player.realm_index < region.minimum_realm:
            realm = REALMS[region.minimum_realm]
            raise ValueError(f"【跨域警告】前往{region.name}至少需要{realm}境；当前为{state.player.realm}。")
        state.pending_travel = {
            "origin": origin,
            "destination": key,
            "distance": cls.distance(origin, key),
        }
        state.phase = "travel_choice"
        return dict(state.pending_travel)

    @classmethod
    def method_costs(cls, state: GameState, method: str) -> tuple[int, int, int]:
        pending = state.pending_travel
        if not pending:
            raise ValueError("当前没有待确认的跨域行程。")
        origin = str(pending["origin"])
        destination = str(pending["destination"])
        months = cls.duration(origin, destination, method)
        if method == "caravan":
            return months, months * 30, 0
        if method == "swift":
            return months, 0, months * 18
        raise ValueError("请选择随商队同行或御风独行。")

    @classmethod
    def decision(cls, state: GameState) -> dict[str, object]:
        if state.phase != "travel_choice" or not state.pending_travel:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        origin = str(state.pending_travel["origin"])
        destination = str(state.pending_travel["destination"])
        choices: list[dict[str, object]] = []
        for method, tone in (("caravan", "safe"), ("swift", "primary")):
            months, stones, spirit = cls.method_costs(state, method)
            missing = ""
            if stones and state.player.spirit_stones < stones:
                missing = f"需要 {stones} 灵石，当前仅有 {state.player.spirit_stones}"
            if spirit and state.player.spirit < spirit:
                missing = f"需要 {spirit} 灵力，当前仅有 {state.player.spirit}"
            cost = f"{stones} 灵石" if stones else f"{spirit} 灵力"
            description = (
                "路线较慢，但有人照应，遭遇劫修与妖兽的风险更低。"
                if method == "caravan"
                else "更快抵达，沿途风险更高；遁速与境界会影响平安抵达的机会。"
            )
            choices.append(
                {
                    "label": f"{METHOD_LABELS[method]} · {months} 月",
                    "action": f"行旅选择 {method}",
                    "summary": f"消耗 {cost}",
                    "description": description,
                    "tone": tone,
                    "disabled": bool(missing),
                    "disabled_reason": missing,
                }
            )
        choices.append(
            {
                "label": "暂不启程",
                "action": "行旅选择 cancel",
                "description": "留在当前地域，不消耗时间与资源。",
                "tone": "quiet",
            }
        )
        return {
            "eyebrow": "跨域行旅",
            "title": f"从{REGIONS[origin].name}前往{REGIONS[destination].name}",
            "hint": "远行会一次结算数月岁月；寿元、世界事件与委托期限都会同步推进。",
            "exclusive": True,
            "choices": choices,
        }

    @classmethod
    def resolve(cls, state: GameState, method: str) -> TravelResult | None:
        if state.phase != "travel_choice" or not state.pending_travel:
            raise ValueError("当前没有待确认的跨域行程。")
        if method == "cancel":
            state.pending_travel = {}
            state.phase = "playing"
            return None
        months, stones, spirit = cls.method_costs(state, method)
        if stones > state.player.spirit_stones:
            raise ValueError(f"灵石不足：需要 {stones}，当前 {state.player.spirit_stones}。")
        if spirit > state.player.spirit:
            raise ValueError(f"灵力不足：需要 {spirit}，当前 {state.player.spirit}。")

        origin = str(state.pending_travel["origin"])
        destination = str(state.pending_travel["destination"])
        region = REGIONS[destination]
        state.player.spirit_stones -= stones
        state.player.spirit -= spirit
        if stones:
            state.trade_profit -= stones
        advantage = max(0, state.player.realm_index - region.minimum_realm)
        if method == "caravan":
            chance = 94 - region.danger // 8 + advantage * 3 + (state.player.fortune - 10) // 2
        else:
            chance = 82 - region.danger // 5 + advantage * 4 + (state.player.speed - 10)
        chance = max(25, min(97, chance))
        roll = ProgressionEngine.deterministic_roll(state, f"travel:{origin}:{destination}:{method}:{state.turn}")
        health_loss = 0
        fatal = False
        if roll <= chance:
            event = "沿途虽有风波，最终都被你避开。" if roll > 18 else "途中结识行脚商人，尚未入城便已听清当地行情。"
        else:
            health_loss = max(8, region.danger // 3 + months * 2 - advantage * 3)
            state.player.health = max(0, state.player.health - health_loss)
            fatal = state.player.health <= 0
            event = "途中遭遇劫修与妖兽夹击，虽突围而出，却付出了气血代价。"
            state.player.condition = "行旅负伤" if not fatal else f"陨落于{origin}至{destination}商路"

        if not fatal:
            state.player.location = region.name
            if destination not in state.visited_regions:
                state.visited_regions.append(destination)
            state.phase = "playing"
        else:
            state.phase = "ended"
        state.pending_travel = {}
        record = f"{REGIONS[origin].name} → {region.name}｜{METHOD_LABELS[method]}｜{months}月"
        state.travel_history.append(record)
        state.travel_history = state.travel_history[-30:]
        return TravelResult(
            origin,
            destination,
            METHOD_LABELS[method],
            months,
            roll,
            chance,
            stones,
            spirit,
            health_loss,
            fatal,
            event,
        )

    @classmethod
    def atlas_lines(cls, state: GameState) -> list[str]:
        current = cls.current_region(state)
        lines: list[str] = []
        for key in REGION_ORDER:
            region = REGIONS[key]
            months = cls.distance(current, key)
            lines.append(
                f"{region.name}｜{cls.requirement_label(region.minimum_realm)}｜行程 {months} 月｜"
                f"危险度 {region.danger}｜特产 {'、'.join(region.specialties)}｜求购 {'、'.join(region.demands)}｜{region.description}"
            )
        return lines

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, object]:
        current = cls.current_region(state)
        visited = set(state.visited_regions) | {current}
        regions = []
        for key in REGION_ORDER:
            region = REGIONS[key]
            regions.append(
                {
                    "key": key,
                    "name": region.name,
                    "minimum_realm": region.minimum_realm,
                    "minimum_realm_label": REALMS[region.minimum_realm],
                    "danger": region.danger,
                    "description": region.description,
                    "specialties": list(region.specialties),
                    "demands": list(region.demands),
                    "months": cls.distance(current, key),
                    "current": key == current,
                    "visited": key in visited,
                    "accessible": state.player.realm_index >= region.minimum_realm,
                    "action": f"前往 {key}",
                }
            )
        return {
            "current": current,
            "current_name": REGIONS[current].name,
            "visited": sorted(visited, key=REGION_ORDER.index),
            "pending": dict(state.pending_travel),
            "trade_profit": state.trade_profit,
            "regions": regions,
            "history": list(state.travel_history[-8:]),
        }
