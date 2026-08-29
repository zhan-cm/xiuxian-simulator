from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class AuctionLot:
    id: str
    name: str
    summary: str
    reserve: int
    increment: int
    rewards: dict[str, int]
    minimum_realm: int = 0


LOTS: tuple[AuctionLot, ...] = (
    AuctionLot("qi-pills", "一匣聚气丹", "五枚聚气丹，适合炼气修士稳固根基。", 65, 10, {"聚气丹": 5}),
    AuctionLot("herb-case", "百草灵药匣", "八株年份尚可的灵药，可炼丹也可栽种。", 70, 10, {"灵药": 8}),
    AuctionLot("green-sword", "青锋剑", "黄阶金行飞剑，锋锐轻灵。", 130, 20, {"青锋剑": 1}),
    AuctionLot("foundation-pill", "筑基丹", "炼气圆满修士筑就道基的重要丹药。", 380, 40, {"筑基丹": 1}),
    AuctionLot("cloud-robe", "流云衣", "玄阶护甲，兼顾护体与遁速。", 820, 80, {"流云衣": 1}),
    AuctionLot("water-manual", "玄水剑诀残卷", "地阶水行剑诀的参悟残卷。", 980, 100, {"玄水剑诀残卷": 1}, 1),
    AuctionLot("treasure", "天材地宝", "地脉深处孕育的破境奇珍。", 1400, 150, {"天材地宝": 1}, 1),
    AuctionLot("five-orb", "五行灵珠", "五行俱全，可供天道破境或洞府营造。", 2600, 250, {"五行灵珠": 1}, 1),
    AuctionLot("dao-rhyme", "一缕道韵", "从天地异象中截取的大道痕迹。", 5200, 500, {"道韵": 1}, 2),
)

COMPETITORS = (
    ("青衣客", "出价克制，擅长在最后一刻加价", 55),
    ("丹霞谷执事", "财力稳健，对丹药与灵材势在必得", 64),
    ("蒙面女修", "行事果决，常以重价逼退旁人", 72),
    ("中州商盟少主", "灵石雄厚，极少空手而归", 82),
)


class AuctionEngine:
    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = f"auction:{state.rng_seed}:{state.calendar_year}:{state.month}:{purpose}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % maximum

    @classmethod
    def open(cls, state: GameState, duration: int = 2) -> dict[str, Any]:
        if state.auction.get("active"):
            return state.auction
        cycle = state.calendar_year * 12 + state.month
        start = cls._number(state, f"lots:{cycle}", len(LOTS))
        selected = [LOTS[(start + offset * 2) % len(LOTS)] for offset in range(4)]
        competitor = COMPETITORS[cls._number(state, f"competitor:{cycle}", len(COMPETITORS))]
        state.auction = {
            "active": True,
            "cycle": cycle,
            "opened_turn": state.turn,
            "closes_turn": state.turn + max(1, duration),
            "competitor": competitor[0],
            "competitor_style": competitor[1],
            "competitor_pressure": competitor[2],
            "pending_lot": "",
            "lots": [
                {
                    "id": lot.id,
                    "name": lot.name,
                    "summary": lot.summary,
                    "reserve": lot.reserve,
                    "increment": lot.increment,
                    "rewards": dict(lot.rewards),
                    "minimum_realm": lot.minimum_realm,
                    "status": "available",
                    "price": 0,
                    "winner": "",
                }
                for lot in selected
            ],
        }
        return state.auction

    @staticmethod
    def _lot(state: GameState, lot_id: str) -> dict[str, Any]:
        for lot in state.auction.get("lots", []):
            if lot.get("id") == lot_id:
                return lot
        raise ValueError("这件拍品并不存在。")

    @classmethod
    def begin(cls, state: GameState, lot_id: str) -> dict[str, Any]:
        if not state.auction.get("active"):
            raise ValueError("当前没有正在举行的天机拍卖会。")
        lot = cls._lot(state, lot_id)
        if lot.get("status") != "available":
            raise ValueError("这件拍品已经落槌。")
        if state.player.realm_index < int(lot.get("minimum_realm", 0)):
            raise ValueError("境界不足，天机坊拒绝为你登记这件高阶拍品。")
        state.auction["pending_lot"] = lot_id
        state.phase = "auction_choice"
        return lot

    @classmethod
    def _offer(cls, lot: dict[str, Any], strategy: str) -> int:
        multiplier = 1 if strategy == "steady" else 3
        return int(lot["reserve"]) + int(lot["increment"]) * multiplier

    @classmethod
    def resolve(cls, state: GameState, strategy: str) -> tuple[dict[str, Any], bool, int, int, int]:
        lot_id = str(state.auction.get("pending_lot", ""))
        if not lot_id:
            raise ValueError("当前没有等待决断的竞价。")
        lot = cls._lot(state, lot_id)
        if strategy == "withdraw":
            lot.update({"status": "lost", "winner": str(state.auction["competitor"]), "price": int(lot["reserve"])})
            state.auction["pending_lot"] = ""
            state.phase = "playing"
            cls._finish_if_empty(state)
            cls._remember(state, f"你退出《{lot['name']}》竞价，由{lot['winner']}以 {lot['price']} 灵石拍得。")
            return lot, False, 0, 0, 0
        if strategy not in {"steady", "decisive"}:
            raise ValueError("请选择稳健举牌、强势压场或退出竞价。")
        offer = cls._offer(lot, strategy)
        if state.player.spirit_stones < offer:
            raise ValueError(f"灵石不足：此番出价需要 {offer}，当前只有 {state.player.spirit_stones}。")
        pressure = int(state.auction.get("competitor_pressure", 60))
        chance = 48 if strategy == "steady" else 78
        chance += (state.player.fortune - 10) * 2 + min(12, state.player.reputation // 5) - max(0, pressure - 60) // 3
        chance = max(15, min(95, chance))
        roll = ProgressionEngine.deterministic_roll(state, f"auction-bid:{state.auction['cycle']}:{lot_id}:{strategy}")
        won = roll <= chance
        if won:
            state.player.spirit_stones -= offer
            for name, count in dict(lot.get("rewards", {})).items():
                state.player.resources[name] = state.player.resources.get(name, 0) + int(count)
            lot.update({"status": "won", "winner": state.player.name, "price": offer})
            result = f"你以 {offer} 灵石拍得《{lot['name']}》；竞价判定 {roll}/{chance}。"
        else:
            npc_price = offer + int(lot["increment"])
            lot.update({"status": "lost", "winner": str(state.auction["competitor"]), "price": npc_price})
            result = f"{state.auction['competitor']}以 {npc_price} 灵石反压一手，你未能拍得《{lot['name']}》；竞价判定 {roll}/{chance}。"
        state.auction["pending_lot"] = ""
        state.phase = "playing"
        cls._finish_if_empty(state)
        cls._remember(state, result)
        return lot, won, offer, roll, chance

    @staticmethod
    def _remember(state: GameState, text: str) -> None:
        state.auction_history.append(f"天玄历{state.calendar_year}年{state.month}月｜{text}")
        state.auction_history = state.auction_history[-50:]

    @staticmethod
    def _finish_if_empty(state: GameState) -> None:
        if state.auction.get("lots") and all(lot.get("status") != "available" for lot in state.auction["lots"]):
            state.auction["active"] = False

    @classmethod
    def expire(cls, state: GameState) -> list[str]:
        if not state.auction.get("active") or state.turn < int(state.auction.get("closes_turn", 0)):
            return []
        expired: list[str] = []
        for lot in state.auction.get("lots", []):
            if lot.get("status") == "available":
                lot.update({"status": "expired", "winner": "场外买家", "price": int(lot["reserve"])})
                expired.append(str(lot["name"]))
        state.auction["active"] = False
        state.auction["pending_lot"] = ""
        if state.phase == "auction_choice":
            state.phase = "playing"
        if expired:
            cls._remember(state, "拍卖散场，未参与的拍品各归其主：" + "、".join(expired))
        return expired

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        lot = cls._lot(state, str(state.auction.get("pending_lot", "")))
        steady = cls._offer(lot, "steady")
        decisive = cls._offer(lot, "decisive")
        pressure = int(state.auction.get("competitor_pressure", 60))
        return {
            "eyebrow": "一锤定音",
            "title": f"竞拍《{lot['name']}》",
            "hint": f"主要对手：{state.auction['competitor']} · 竞价压力 {pressure}/100；落败不会扣除灵石。",
            "exclusive": True,
            "choices": [
                {
                    "label": f"稳健举牌 · {steady} 灵石",
                    "action": "拍卖选择 steady",
                    "description": "以较低价格试探对手，成交机会受仙缘、声望与对手压力影响。",
                    "tone": "safe",
                    "disabled": state.player.spirit_stones < steady,
                    "disabled_reason": f"还差 {steady - state.player.spirit_stones} 灵石" if state.player.spirit_stones < steady else "",
                },
                {
                    "label": f"强势压场 · {decisive} 灵石",
                    "action": "拍卖选择 decisive",
                    "description": "一次抬高三档价格，以更多灵石显著提高成交机会。",
                    "tone": "primary",
                    "disabled": state.player.spirit_stones < decisive,
                    "disabled_reason": f"还差 {decisive - state.player.spirit_stones} 灵石" if state.player.spirit_stones < decisive else "",
                },
                {
                    "label": "退出竞价",
                    "action": "拍卖选择 withdraw",
                    "description": "不消耗灵石，将这件拍品让给场内对手。",
                    "tone": "quiet",
                },
            ],
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        auction = state.auction
        active = bool(auction.get("active"))
        lots = []
        for raw in auction.get("lots", []):
            lot = dict(raw)
            minimum = int(lot.get("minimum_realm", 0))
            lot["eligible"] = state.player.realm_index >= minimum
            lot["minimum_realm_label"] = ("炼气", "筑基", "结晶", "金丹")[min(minimum, 3)]
            lot["affordable"] = state.player.spirit_stones >= int(lot.get("reserve", 0)) + int(lot.get("increment", 0))
            lot["begin_action"] = f"竞拍 {lot['id']}"
            lots.append(lot)
        return {
            "active": active,
            "title": "天机拍卖会" if active else "拍卖已经散场",
            "closes_in": max(0, int(auction.get("closes_turn", state.turn)) - state.turn) if active else 0,
            "competitor": str(auction.get("competitor", "尚未入场")),
            "competitor_style": str(auction.get("competitor_style", "")),
            "pending": str(auction.get("pending_lot", "")),
            "lots": lots,
            "history": list(reversed(state.auction_history[-8:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        data = cls.snapshot(state)
        if not data["active"]:
            return "【天机拍卖会】\n当前没有拍卖正在举行；临时拍卖会会随九州风声不定期开启。"
        status_labels = {
            "available": "待落槌",
            "won": "已拍得",
            "lost": "已旁落",
            "expired": "已散场",
        }
        lines = [
            f"{lot['name']}｜底价 {lot['reserve']}｜加价 {lot['increment']}｜{status_labels.get(lot['status'], lot['status'])}"
            for lot in data["lots"]
        ]
        return (
            f"【天机拍卖会】\n剩余 {data['closes_in']} 个月｜主要对手：{data['competitor']}\n"
            + "\n".join(lines)
            + "\n指令：竞拍 [拍品编号]"
        )
