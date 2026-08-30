from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import GameState


REGION_KEYS = ("东洲", "南疆", "西漠", "北原", "中州")

REGIONAL_EVENTS: dict[str, dict[str, Any]] = {
    "东洲": {
        "id": "qingyue-spring",
        "title": "青岳灵泉之争",
        "intro": "一眼新生灵泉同时引来山民与青云宗外门管事。两方都请你作证，泉水究竟该归谁使用。",
        "choices": (
            {"id": "share", "label": "开渠共饮", "summary": "地方声望 +10 · 功德 +2", "description": "说服双方共同修渠，让灵泉先救旱田，再供修士取用。", "tone": "safe", "effects": {"regional_reputation": 10, "merit": 2}},
            {"id": "mediate", "label": "立契分泉", "summary": "地方声望 +6 · 灵石 +60", "description": "以修士身份主持契约，也收取一份公证酬劳。", "tone": "primary", "effects": {"regional_reputation": 6, "stones": 60}},
            {"id": "seize", "label": "趁乱取泉", "summary": "灵药 +3 · 地方声望 -6 · 业力 +3", "description": "趁双方争执取走灵液，所得最快，却会留下恶名。", "tone": "danger", "effects": {"regional_reputation": -6, "karma": 3, "resources": {"灵药": 3}}},
        ),
    },
    "南疆": {
        "id": "chiyan-beast-tide",
        "title": "赤炎兽潮",
        "intro": "地火惊动兽群，一支药商车队被困在赤炎岭下。远处号角已断，留给你的时间不多。",
        "choices": (
            {"id": "rescue", "label": "正面救援", "summary": "地方声望 +12 · 灵石 +120 · 气血 -12", "description": "强行杀开兽群，以伤势换下整支车队。", "tone": "danger", "effects": {"regional_reputation": 12, "stones": 120, "health_loss": 12}},
            {"id": "lure", "label": "引兽入谷", "summary": "消耗 30 灵力 · 地方声望 +8 · 妖兽材料 +4", "description": "以术法引走兽群，风险更低，也能收走沿途兽材。", "tone": "primary", "requirements": {"spirit": 30}, "effects": {"regional_reputation": 8, "resources": {"妖兽材料": 4}}},
            {"id": "avoid", "label": "绕路离开", "summary": "不消耗资源", "description": "保全自身，不介入南疆商旅的生死。", "tone": "quiet", "effects": {}},
        ),
    },
    "西漠": {
        "id": "liusha-waystone",
        "title": "流沙古碑",
        "intro": "指引商路的古碑被沙暴折断，迷途者的骸骨已露出半截。碑中残存的符纹也价值不菲。",
        "choices": (
            {"id": "restore", "label": "重立路碑", "summary": "消耗 100 灵石 · 地方声望 +14 · 功德 +2", "description": "雇佣商旅合力重立石碑，让后来者不再葬身流沙。", "tone": "safe", "requirements": {"stones": 100}, "effects": {"regional_reputation": 14, "merit": 2}},
            {"id": "copy", "label": "拓印符纹", "summary": "地方声望 +3 · 道韵 +1 · 业力 +1", "description": "只取碑中道纹，残碑能否继续指路便不再过问。", "tone": "primary", "effects": {"regional_reputation": 3, "karma": 1, "resources": {"道韵": 1}}},
            {"id": "report", "label": "告知商会", "summary": "地方声望 +7 · 灵石 +160", "description": "把路线与损毁情况卖给四海商会，由他们接手修复。", "tone": "quiet", "effects": {"regional_reputation": 7, "stones": 160}},
        ),
    },
    "北原": {
        "id": "hanyuan-famine",
        "title": "寒渊断粮",
        "intro": "暴雪封住雪族边城，伤者与孩童已断药数日。几支商队却在城外等待价格继续上涨。",
        "choices": (
            {"id": "donate", "label": "开囊赠药", "summary": "消耗 疗伤丹×2 · 地方声望 +18 · 功德 +3", "description": "把随身疗伤丹交给雪族医师，先救最危重的人。", "tone": "safe", "requirements": {"resources": {"疗伤丹": 2}}, "effects": {"regional_reputation": 18, "merit": 3}},
            {"id": "escort", "label": "破雪护运", "summary": "地方声望 +12 · 灵石 +180 · 气血 -15", "description": "带领补给队穿过冰兽出没的雪谷。", "tone": "primary", "effects": {"regional_reputation": 12, "stones": 180, "health_loss": 15}},
            {"id": "speculate", "label": "囤货待价", "summary": "灵石 +260 · 地方声望 -12 · 业力 +4", "description": "借断粮推高物价，获利丰厚，也会被北原人记住。", "tone": "danger", "effects": {"regional_reputation": -12, "stones": 260, "karma": 4}},
        ),
    },
    "中州": {
        "id": "tianque-debate",
        "title": "天阙问名",
        "intro": "天阙论道台正在评议灵潮异象。你虽初来，却被点名陈述一路见闻，满座目光都落在你身上。",
        "choices": (
            {"id": "debate", "label": "登台论道", "summary": "地方声望 +12 · 天下声望 +5 · 修为 +20", "description": "以亲历见闻应对群修诘问，让名字第一次传遍天阙。", "tone": "primary", "effects": {"regional_reputation": 12, "global_reputation": 5, "cultivation": 20}},
            {"id": "tribute", "label": "献宝佐证", "summary": "消耗 天材地宝×1 · 地方声望 +20 · 天下声望 +3", "description": "以沿途所得证明灵潮变化，少费口舌却代价不菲。", "tone": "safe", "requirements": {"resources": {"天材地宝": 1}}, "effects": {"regional_reputation": 20, "global_reputation": 3}},
            {"id": "buy", "label": "捐资留名", "summary": "消耗 300 灵石 · 地方声望 +8", "description": "向论道台捐资，换得一席留名。", "tone": "quiet", "requirements": {"stones": 300}, "effects": {"regional_reputation": 8}},
        ),
    },
}


@dataclass(frozen=True, slots=True)
class RegionalResult:
    region: str
    title: str
    choice: str
    effects: tuple[str, ...]


class RegionalEngine:
    @staticmethod
    def current_region(state: GameState) -> str:
        return next((key for key in REGION_KEYS if state.player.location.startswith(key)), "东洲")

    @staticmethod
    def reputation(state: GameState, region: str) -> int:
        return int(state.regional_reputation.get(region, 0))

    @classmethod
    def rank(cls, state: GameState, region: str) -> str:
        value = cls.reputation(state, region)
        if value < -20:
            return "声名狼藉"
        if value < 0:
            return "遭人戒备"
        if value < 10:
            return "初来乍到"
        if value < 25:
            return "略有薄名"
        if value < 50:
            return "受人敬重"
        return "名动一方"

    @classmethod
    def adjust(cls, state: GameState, region: str, amount: int) -> int:
        before = cls.reputation(state, region)
        state.regional_reputation[region] = max(-50, min(100, before + amount))
        return state.regional_reputation[region] - before

    @classmethod
    def benefits(cls, state: GameState, region: str) -> dict[str, Any]:
        value = cls.reputation(state, region)
        buy_percent = max(-6, min(12, value * 2 // 10))
        sell_percent = max(-5, min(9, value * 3 // 20))
        return {
            "reputation": value,
            "rank": cls.rank(state, region),
            "buy_discount": buy_percent,
            "sell_bonus": sell_percent,
            "travel_bonus": max(-5, min(8, value // 10)),
            "exploration_bonus": max(-4, min(8, value // 10)),
        }

    @classmethod
    def price_multiplier(cls, state: GameState, region: str, operation: str) -> float:
        value = max(-30, min(60, cls.reputation(state, region)))
        if operation == "买":
            return 1.0 - value * 0.002
        if operation == "卖":
            return 1.0 + value * 0.0015
        raise ValueError("交易指令必须是买或卖。")

    @classmethod
    def record_arrival(cls, state: GameState, region: str, first_visit: bool) -> int:
        return cls.adjust(state, region, 3) if first_visit else 0

    @classmethod
    def record_exploration(cls, state: GameState, region: str) -> int:
        before = int(state.regional_explorations.get(region, 0))
        after = before + 1
        state.regional_explorations[region] = after
        return cls.adjust(state, region, 1) if after % 2 == 0 else 0

    @classmethod
    def record_trade(cls, state: GameState, region: str, volume: int) -> int:
        before = int(state.regional_trade_volume.get(region, 0))
        after = before + max(0, volume)
        state.regional_trade_volume[region] = after
        gained = min(2, after // 500 - before // 500)
        return cls.adjust(state, region, gained) if gained > 0 else 0

    @classmethod
    def prepare(cls, state: GameState, region: str | None = None) -> dict[str, Any] | None:
        key = region or cls.current_region(state)
        event = REGIONAL_EVENTS[key]
        if str(event["id"]) in state.regional_encounters_completed:
            return None
        state.pending_regional_encounter = {"region": key, "id": event["id"]}
        state.phase = "regional_choice"
        return event

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        pending = state.pending_regional_encounter
        if state.phase != "regional_choice" or not pending:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        key = str(pending["region"])
        event = REGIONAL_EVENTS[key]
        choices = []
        for choice in event["choices"]:
            missing = cls._missing_requirements(state, choice.get("requirements", {}))
            choices.append(
                {
                    "label": choice["label"],
                    "action": f"地方选择 {choice['id']}",
                    "summary": choice.get("summary", ""),
                    "description": choice["description"],
                    "tone": choice.get("tone", "primary"),
                    "disabled": bool(missing),
                    "disabled_reason": "缺少 " + "、".join(missing) if missing else "",
                }
            )
        return {
            "eyebrow": f"{key}机缘",
            "title": str(event["title"]),
            "hint": "地方会记住你的取舍；声望将影响坊市、探索与下一次远行。",
            "exclusive": True,
            "choices": choices,
        }

    @staticmethod
    def _missing_requirements(state: GameState, requirements: dict[str, Any]) -> list[str]:
        missing: list[str] = []
        stones = int(requirements.get("stones", 0))
        spirit = int(requirements.get("spirit", 0))
        if stones > state.player.spirit_stones:
            missing.append(f"灵石×{stones}")
        if spirit > state.player.spirit:
            missing.append(f"灵力×{spirit}")
        for name, count in dict(requirements.get("resources", {})).items():
            if state.player.resources.get(name, 0) < int(count):
                missing.append(f"{name}×{count}")
        return missing

    @classmethod
    def resolve(cls, state: GameState, choice_id: str) -> RegionalResult:
        pending = state.pending_regional_encounter
        if state.phase != "regional_choice" or not pending:
            raise ValueError("当前没有等待处理的地方机缘。")
        key = str(pending["region"])
        event = REGIONAL_EVENTS[key]
        choice = next((item for item in event["choices"] if item["id"] == choice_id or item["label"] == choice_id), None)
        if choice is None:
            raise ValueError("请选择当前地方机缘中的一项应对。")
        requirements = dict(choice.get("requirements", {}))
        missing = cls._missing_requirements(state, requirements)
        if missing:
            raise ValueError("缺少 " + "、".join(missing) + "，无法作出此选择。")
        state.player.spirit_stones -= int(requirements.get("stones", 0))
        state.player.spirit -= int(requirements.get("spirit", 0))
        for name, count in dict(requirements.get("resources", {})).items():
            state.player.resources[name] -= int(count)
            if state.player.resources[name] <= 0:
                state.player.resources.pop(name, None)

        effects = dict(choice.get("effects", {}))
        notes: list[str] = []
        local_change = cls.adjust(state, key, int(effects.get("regional_reputation", 0)))
        if local_change:
            notes.append(f"{key}声望 {local_change:+d}")
        for field_name, label in (("merit", "功德"), ("karma", "业力"), ("global_reputation", "天下声望")):
            amount = int(effects.get(field_name, 0))
            if amount:
                target = "reputation" if field_name == "global_reputation" else field_name
                setattr(state.player, target, getattr(state.player, target) + amount)
                notes.append(f"{label} {amount:+d}")
        stones = int(effects.get("stones", 0))
        if stones:
            state.player.spirit_stones += stones
            notes.append(f"灵石 {stones:+d}")
        cultivation = int(effects.get("cultivation", 0))
        if cultivation:
            gained = min(cultivation, max(0, state.player.cultivation_required - state.player.cultivation))
            state.player.cultivation += gained
            notes.append(f"修为 +{gained}")
        health_loss = int(effects.get("health_loss", 0))
        if health_loss:
            actual = min(health_loss, max(0, state.player.health - 1))
            state.player.health -= actual
            notes.append(f"气血 -{actual}")
        for name, count in dict(effects.get("resources", {})).items():
            state.player.resources[name] = state.player.resources.get(name, 0) + int(count)
            notes.append(f"{name} +{count}")

        event_id = str(event["id"])
        if event_id not in state.regional_encounters_completed:
            state.regional_encounters_completed.append(event_id)
        record = f"{key}《{event['title']}》选择{choice['label']}"
        state.regional_history.append(record)
        state.regional_history = state.regional_history[-30:]
        state.pending_regional_encounter = {}
        state.phase = "playing"
        return RegionalResult(key, str(event["title"]), str(choice["label"]), tuple(notes or ["无直接数值变化"]))

    @classmethod
    def encounter_text(cls, state: GameState, region: str | None = None) -> str:
        key = region or cls.current_region(state)
        event = REGIONAL_EVENTS[key]
        return f"【地方机缘 · {key}】\n《{event['title']}》\n{event['intro']}\n此事需要你亲自作出选择。"

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        lines = []
        for key in REGION_KEYS:
            benefit = cls.benefits(state, key)
            lines.append(
                f"{key}｜{benefit['rank']}｜声望 {benefit['reputation']:+d}｜"
                f"买价优惠 {benefit['buy_discount']:+d}%｜卖价礼遇 {benefit['sell_bonus']:+d}%｜行旅判定 {benefit['travel_bonus']:+d}"
            )
        current = cls.current_region(state)
        event = REGIONAL_EVENTS[current]
        completed = str(event["id"]) in state.regional_encounters_completed
        local = f"《{event['title']}》已了结" if completed else f"《{event['title']}》等待触发"
        return "【五域声名】\n" + "\n".join(lines) + f"\n\n【当前地方机缘】\n{current}：{local}\n输入：地方机缘"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        current = cls.current_region(state)
        standings = []
        for key in REGION_KEYS:
            benefit = cls.benefits(state, key)
            event = REGIONAL_EVENTS[key]
            standings.append(
                {
                    "key": key,
                    **benefit,
                    "trade_volume": int(state.regional_trade_volume.get(key, 0)),
                    "explorations": int(state.regional_explorations.get(key, 0)),
                    "encounter_title": str(event["title"]),
                    "encounter_completed": str(event["id"]) in state.regional_encounters_completed,
                }
            )
        return {
            "current": current,
            "current_rank": cls.rank(state, current),
            "pending": dict(state.pending_regional_encounter),
            "standings": standings,
            "history": list(state.regional_history[-8:]),
        }
