from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .state import GameState
from .world import SectWarEngine


@dataclass(frozen=True, slots=True)
class FactionProfile:
    name: str
    mark: str
    path: str
    description: str
    initial_relation: int


FACTIONS: dict[str, FactionProfile] = {
    "青云宗": FactionProfile("青云宗", "云", "正道仙门", "重秩序与传承，愿与守序山门往来。", 12),
    "丹霞谷": FactionProfile("丹霞谷", "丹", "丹道宗门", "看重商路、灵药与稳定的互惠关系。", 8),
    "玄剑门": FactionProfile("玄剑门", "剑", "剑修大宗", "敬重实力，弱小山门难获其真正认可。", 0),
    "血煞盟": FactionProfile("血煞盟", "煞", "魔道联盟", "觊觎新立山门的灵脉与传承，天然敌视。", -32),
}

TREATY_LABELS = {"none": "无盟约", "trade": "通商盟约", "alliance": "攻守同盟"}


class SectDiplomacyEngine:
    ENVOY_COST = 120
    PRESSURE_COST = 80
    TRADE_COST = 220
    ALLIANCE_COST = 360
    WAR_COST = 250
    PEACE_COST = 300

    @classmethod
    def default_data(cls) -> dict[str, Any]:
        return {
            "relations": {name: profile.initial_relation for name, profile in FACTIONS.items()},
            "treaties": {name: "none" for name in FACTIONS},
            "last_action_year": 0,
            "victories": 0,
            "defeats": 0,
            "history": [],
        }

    @classmethod
    def data(cls, state: GameState, *, mutate: bool = False) -> dict[str, Any]:
        current = state.founded_sect.get("diplomacy")
        if isinstance(current, dict):
            if mutate:
                current.setdefault("relations", {})
                current.setdefault("treaties", {})
                current.setdefault("last_action_year", 0)
                current.setdefault("victories", 0)
                current.setdefault("defeats", 0)
                current.setdefault("history", [])
                for name, profile in FACTIONS.items():
                    current["relations"].setdefault(name, profile.initial_relation)
                    current["treaties"].setdefault(name, "none")
            return current
        default = cls.default_data()
        if mutate:
            state.founded_sect["diplomacy"] = default
        return default

    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = f"sect-diplomacy:{state.rng_seed}:{state.calendar_year}:{state.turn}:{purpose}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % maximum

    @classmethod
    def _require(cls, state: GameState) -> tuple[dict[str, Any], dict[str, Any]]:
        sect = state.founded_sect
        if not sect.get("name"):
            raise ValueError("本世尚未开宗立派。")
        if sect.get("ruined"):
            raise ValueError("山门已经覆灭，无法继续主持宗门外交。")
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择。")
        return sect, cls.data(state, mutate=True)

    @classmethod
    def _target(cls, state: GameState, target: str) -> tuple[dict[str, Any], dict[str, Any], FactionProfile]:
        sect, diplomacy = cls._require(state)
        profile = FACTIONS.get(target)
        if profile is None:
            raise ValueError("请选择青云宗、丹霞谷、玄剑门或血煞盟。")
        if target in state.fallen_factions:
            raise ValueError(f"{target}已经覆灭，无法再与之往来。")
        return sect, diplomacy, profile

    @staticmethod
    def _relation(diplomacy: dict[str, Any], target: str) -> int:
        return int(diplomacy.get("relations", {}).get(target, FACTIONS[target].initial_relation))

    @classmethod
    def _change_relation(cls, diplomacy: dict[str, Any], target: str, change: int) -> int:
        relation = max(-100, min(100, cls._relation(diplomacy, target) + change))
        diplomacy.setdefault("relations", {})[target] = relation
        return relation

    @staticmethod
    def stance(score: int) -> str:
        if score >= 60:
            return "莫逆"
        if score >= 30:
            return "友善"
        if score >= 10:
            return "平和"
        if score > -20:
            return "疏远"
        if score > -50:
            return "敌视"
        return "死敌"

    @classmethod
    def _begin_action(cls, state: GameState, diplomacy: dict[str, Any]) -> None:
        if int(diplomacy.get("last_action_year", 0)) == state.calendar_year:
            raise ValueError("本年已经主持过一次宗门外务。")
        diplomacy["last_action_year"] = state.calendar_year

    @classmethod
    def _spend(cls, sect: dict[str, Any], amount: int, label: str) -> None:
        treasury = int(sect.get("treasury", 0))
        if treasury < amount:
            raise ValueError(f"宗门库藏不足：{label}需要 {amount} 库藏。")
        sect["treasury"] = treasury - amount
        sect["expense_lifetime"] = int(sect.get("expense_lifetime", 0)) + amount

    @classmethod
    def record(cls, state: GameState, text: str) -> None:
        diplomacy = cls.data(state, mutate=True)
        history = diplomacy.setdefault("history", [])
        history.append(f"天玄历{state.calendar_year}年{state.month}月｜{text}")
        diplomacy["history"] = history[-30:]

    @classmethod
    def envoy(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.ENVOY_COST, "遣使修好")
        gain = 18 + cls._number(state, f"envoy:{target}", 7)
        relation = cls._change_relation(diplomacy, target, gain)
        sect["renown"] = min(100, int(sect.get("renown", 0)) + 1)
        text = f"遣使拜访{profile.name}，关系 +{gain}，升至{relation}（{cls.stance(relation)}）"
        cls.record(state, text)
        return text

    @classmethod
    def pressure(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        if diplomacy.get("treaties", {}).get(target, "none") != "none":
            raise ValueError("已有盟约在身，需先解除盟约才能施压。")
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.PRESSURE_COST, "边境施压")
        loss = 20 + cls._number(state, f"pressure:{target}", 7)
        relation = cls._change_relation(diplomacy, target, -loss)
        sect["renown"] = min(100, int(sect.get("renown", 0)) + 2)
        state.world_tension = min(100, state.world_tension + 3)
        text = f"向{profile.name}边境施压，关系 -{loss}，降至{relation}（{cls.stance(relation)}）"
        cls.record(state, text)
        return text

    @classmethod
    def trade_pact(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        relation = cls._relation(diplomacy, target)
        if relation < 30:
            raise ValueError(f"与{target}关系至少达到 30 才能缔结商盟；当前 {relation}。")
        if diplomacy.get("treaties", {}).get(target, "none") != "none":
            raise ValueError(f"与{target}已经存在盟约。")
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.TRADE_COST, "缔结商盟")
        diplomacy.setdefault("treaties", {})[target] = "trade"
        relation = cls._change_relation(diplomacy, target, 8)
        sect["experience"] = int(sect.get("experience", 0)) + 20
        text = f"与{profile.name}缔结通商盟约，关系升至 {relation}，宗门月度收入将增加"
        cls.record(state, text)
        return text

    @classmethod
    def alliance(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        relation = cls._relation(diplomacy, target)
        if relation < 60:
            raise ValueError(f"与{target}关系至少达到 60 才能结为盟友；当前 {relation}。")
        if diplomacy.get("treaties", {}).get(target, "none") != "trade":
            raise ValueError("需先缔结通商盟约，才能进一步结为攻守同盟。")
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.ALLIANCE_COST, "缔结盟约")
        diplomacy.setdefault("treaties", {})[target] = "alliance"
        relation = cls._change_relation(diplomacy, target, 10)
        sect["experience"] = int(sect.get("experience", 0)) + 35
        sect["renown"] = min(100, int(sect.get("renown", 0)) + 4)
        text = f"与{profile.name}立下攻守同盟，关系升至 {relation}，双方不再互相宣战"
        cls.record(state, text)
        return text

    @classmethod
    def break_treaty(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        treaty = diplomacy.get("treaties", {}).get(target, "none")
        if treaty == "none":
            raise ValueError(f"与{target}之间并无盟约可解。")
        cls._begin_action(state, diplomacy)
        diplomacy.setdefault("treaties", {})[target] = "none"
        relation = cls._change_relation(diplomacy, target, -25)
        sect["stability"] = max(0, int(sect.get("stability", 0)) - 2)
        state.world_tension = min(100, state.world_tension + 2)
        text = f"解除与{profile.name}的{TREATY_LABELS[treaty]}，关系降至 {relation}"
        cls.record(state, text)
        return text

    @classmethod
    def declare_war(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        relation = cls._relation(diplomacy, target)
        if state.active_sect_war:
            raise ValueError("九州已有一场宗门战争进行中。")
        if int(sect.get("level", 1)) < 2:
            raise ValueError("宗门至少晋为一方宗派，才有资格主动宣战。")
        strength = int(state.faction_strengths.get(str(sect.get("name")), 0))
        if strength < 50:
            raise ValueError(f"宗门实力至少达到 50 才能宣战；当前 {strength}。")
        if relation > -20:
            raise ValueError(f"与{target}尚未敌对到足以宣战；需关系不高于 -20，当前 {relation}。")
        if diplomacy.get("treaties", {}).get(target, "none") != "none":
            raise ValueError("需先解除盟约，才能向对方宣战。")
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.WAR_COST, "整军宣战")
        announcement = SectWarEngine.start(state, str(sect["name"]), target)
        diplomacy.setdefault("relations", {})[target] = min(-75, relation)
        cls.record(state, f"向{profile.name}正式宣战，宗门库藏 -{cls.WAR_COST}")
        return announcement

    @classmethod
    def seek_peace(cls, state: GameState, target: str) -> str:
        sect, diplomacy, profile = cls._target(state, target)
        war = state.active_sect_war
        own_name = str(sect.get("name"))
        if not war or {war.get("attacker"), war.get("defender")} != {own_name, target}:
            raise ValueError(f"当前并未与{target}交战。")
        if int(war.get("months", 0)) < 2:
            raise ValueError("战事至少持续两个月后，双方才肯议和。")
        cls._begin_action(state, diplomacy)
        cls._spend(sect, cls.PEACE_COST, "议和止戈")
        relation = cls._change_relation(diplomacy, target, 12)
        diplomacy.setdefault("treaties", {})[target] = "none"
        state.active_sect_war = {}
        state.world_tension = max(0, state.world_tension - 5)
        conclusion = f"{own_name}与{profile.name}议和止戈，关系回升至 {relation}。"
        state.sect_war_history.append(f"天玄历{state.calendar_year}年{state.month}月｜{conclusion}")
        state.sect_war_history = state.sect_war_history[-30:]
        cls.record(state, conclusion)
        return conclusion

    @classmethod
    def monthly_income_bonus(cls, state: GameState) -> int:
        if not state.founded_sect.get("name") or state.founded_sect.get("ruined"):
            return 0
        diplomacy = cls.data(state)
        return sum(15 if treaty == "trade" else 22 if treaty == "alliance" else 0 for treaty in diplomacy.get("treaties", {}).values())

    @classmethod
    def allied_with(cls, state: GameState, faction: str) -> bool:
        if not state.founded_sect.get("name"):
            return False
        return cls.data(state).get("treaties", {}).get(faction) == "alliance"

    @classmethod
    def _action_state(cls, state: GameState, target: str, kind: str) -> tuple[bool, str]:
        sect = state.founded_sect
        diplomacy = cls.data(state)
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if sect.get("ruined"):
            return False, "山门已经覆灭"
        if target in state.fallen_factions:
            return False, "该势力已经覆灭"
        if int(diplomacy.get("last_action_year", 0)) == state.calendar_year:
            return False, "本年已经主持过宗门外务"
        treasury = int(sect.get("treasury", 0))
        costs = {"envoy": cls.ENVOY_COST, "pressure": cls.PRESSURE_COST, "trade": cls.TRADE_COST, "alliance": cls.ALLIANCE_COST, "war": cls.WAR_COST, "peace": cls.PEACE_COST, "break": 0}
        if treasury < costs[kind]:
            return False, f"需要 {costs[kind]} 库藏"
        relation = cls._relation(diplomacy, target)
        treaty = diplomacy.get("treaties", {}).get(target, "none")
        if kind == "trade" and relation < 30:
            return False, f"关系需达到 30，当前 {relation}"
        if kind == "alliance" and (relation < 60 or treaty != "trade"):
            return False, "需先有商盟且关系达到 60"
        if kind == "pressure" and treaty != "none":
            return False, "需先解除盟约"
        if kind == "war":
            if state.active_sect_war:
                return False, "九州已有宗门战争"
            if int(sect.get("level", 1)) < 2:
                return False, "需晋为一方宗派"
            if int(state.faction_strengths.get(str(sect.get("name")), 0)) < 50:
                return False, "宗门实力需达到 50"
            if relation > -20:
                return False, "关系需降至敌视"
            if treaty != "none":
                return False, "需先解除盟约"
        if kind == "peace":
            war = state.active_sect_war
            if not war or int(war.get("months", 0)) < 2:
                return False, "战事持续两个月后方可议和"
        return True, ""

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        if not state.founded_sect.get("name"):
            return {"visible": False, "factions": [], "history": [], "war": {}, "income_bonus": 0, "acted_this_year": False}
        sect = state.founded_sect
        diplomacy = cls.data(state)
        own_name = str(sect.get("name"))
        war = state.active_sect_war
        war_target = ""
        war_view: dict[str, Any] = {}
        if war and own_name in {war.get("attacker"), war.get("defender")}:
            war_target = str(war["defender"] if war.get("attacker") == own_name else war["attacker"])
            perspective = int(war.get("momentum", 0)) * (1 if war.get("attacker") == own_name else -1)
            war_view = {
                "active": True,
                "target": war_target,
                "side": "进攻方" if war.get("attacker") == own_name else "守方",
                "months": int(war.get("months", 0)),
                "momentum": perspective,
                "momentum_label": "占据上风" if perspective > 0 else "陷入劣势" if perspective < 0 else "势均力敌",
                "player_acted": bool(war.get("player_acted")),
            }
        faction_items = []
        for name, profile in FACTIONS.items():
            relation = cls._relation(diplomacy, name)
            treaty = str(diplomacy.get("treaties", {}).get(name, "none"))
            if war_target == name:
                primary_kind, primary_label, primary_action = "peace", "议和止戈", f"宗门议和 {name}"
                secondary_kind, secondary_label, secondary_action = "war", "战事进行中", ""
            elif treaty == "alliance":
                primary_kind, primary_label, primary_action = "envoy", "盟约稳固", ""
                secondary_kind, secondary_label, secondary_action = "break", "解除盟约", f"解除盟约 {name}"
            elif treaty == "trade":
                if relation >= 60:
                    primary_kind, primary_label, primary_action = "alliance", "结为盟友", f"缔结盟约 {name}"
                else:
                    primary_kind, primary_label, primary_action = "envoy", "遣使修好", f"宗门遣使 {name}"
                secondary_kind, secondary_label, secondary_action = "break", "解除商盟", f"解除盟约 {name}"
            else:
                if relation >= 30:
                    primary_kind, primary_label, primary_action = "trade", "缔结商盟", f"缔结商盟 {name}"
                else:
                    primary_kind, primary_label, primary_action = "envoy", "遣使修好", f"宗门遣使 {name}"
                if relation <= -20:
                    secondary_kind, secondary_label, secondary_action = "war", "整军宣战", f"宗门宣战 {name}"
                else:
                    secondary_kind, secondary_label, secondary_action = "pressure", "边境施压", f"宗门施压 {name}"
            primary_available, primary_reason = cls._action_state(state, name, primary_kind)
            secondary_available, secondary_reason = cls._action_state(state, name, secondary_kind)
            if not primary_action:
                primary_available, primary_reason = False, "当前无需重复操作"
            if not secondary_action:
                secondary_available, secondary_reason = False, "战事已在进行"
            faction_items.append({
                "name": name, "mark": profile.mark, "path": profile.path, "description": profile.description,
                "strength": int(state.faction_strengths.get(name, 0)), "fallen": name in state.fallen_factions,
                "relation": relation, "relation_percent": (relation + 100) // 2, "stance": cls.stance(relation),
                "treaty": treaty, "treaty_label": TREATY_LABELS.get(treaty, "无盟约"),
                "at_war": war_target == name,
                "primary": {"label": primary_label, "action": primary_action, "available": primary_available, "reason": primary_reason},
                "secondary": {"label": secondary_label, "action": secondary_action, "available": secondary_available, "reason": secondary_reason},
            })
        return {
            "visible": True,
            "factions": faction_items,
            "history": list(reversed(diplomacy.get("history", [])[-10:])),
            "war": war_view,
            "income_bonus": cls.monthly_income_bonus(state),
            "acted_this_year": int(diplomacy.get("last_action_year", 0)) == state.calendar_year,
            "victories": int(diplomacy.get("victories", 0)),
            "defeats": int(diplomacy.get("defeats", 0)),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["visible"]:
            return "【宗门外交】需先开宗立派。"
        relations = "｜".join(f"{item['name']} {item['relation']:+d}（{item['stance']}）·{item['treaty_label']}" for item in snapshot["factions"])
        war = snapshot["war"]
        war_text = f"\n【当前战局】对{war['target']}·{war['side']}·{war['momentum_label']}" if war else ""
        return f"【宗门外交】商盟月度收益 +{snapshot['income_bonus']}\n{relations}{war_text}"
