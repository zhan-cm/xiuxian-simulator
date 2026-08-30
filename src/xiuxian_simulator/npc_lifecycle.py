from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .relationships import NPCS, RelationshipEngine
from .state import GameState


REALMS = ("炼气", "筑基", "结晶", "金丹", "具灵", "元婴", "化神", "悟道", "羽化", "登仙")
STAGES = ("初期", "中期", "后期", "圆满")
LIFESPANS = (100, 200, 300, 500, 800, 1200, 2000, 5000, 10000, 50000)
BREAKTHROUGH_PILLS = ("筑基丹", "凝晶丹", "结丹灵药", "结婴丹", "具灵丹", "化神丹", "悟道丹", "羽化丹", "登仙丹")


@dataclass(frozen=True, slots=True)
class NpcLifeResult:
    name: str
    choice: str
    success: bool
    fatal: bool
    roll: int
    chance: int
    description: str
    cost: str


class NpcLifecycleEngine:
    """Own the persistent age, cultivation and mortality of authored NPCs."""

    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = f"{state.rng_seed}:{state.turn}:{state.calendar_year}:{state.month}:{purpose}".encode("utf-8")
        digest = hashlib.sha256(material).digest()
        return int.from_bytes(digest[:8], "big") % maximum

    @staticmethod
    def _realm_parts(realm: str) -> tuple[int, int]:
        major, _, stage = realm.partition("·")
        return REALMS.index(major) if major in REALMS else 0, STAGES.index(stage) if stage in STAGES else 0

    @staticmethod
    def _realm_label(record: dict[str, Any]) -> str:
        realm_index = max(0, min(len(REALMS) - 1, int(record.get("realm_index", 0))))
        stage_index = max(0, min(len(STAGES) - 1, int(record.get("stage_index", 0))))
        return f"{REALMS[realm_index]}·{STAGES[stage_index]}"

    @classmethod
    def world_record(cls, state: GameState, name: str) -> dict[str, Any]:
        npc = RelationshipEngine.npc(name)
        realm_index, stage_index = cls._realm_parts(npc.realm)
        elapsed_years = max(0, state.calendar_year - 387)
        record = state.npc_world.setdefault(name, {})
        defaults: dict[str, Any] = {
            "location": npc.location,
            "activity": "各循其道",
            "cultivation_progress": 0,
            "spirit_stones": 100,
            "wounded": False,
            "events": 0,
            "age": npc.age + elapsed_years,
            "lifespan": LIFESPANS[realm_index],
            "realm_index": realm_index,
            "stage_index": stage_index,
            "realm": npc.realm,
            "alive": True,
            "status": "安然",
            "last_lifecycle_year": state.calendar_year,
            "deceased_year": 0,
            "cause_of_death": "",
            "life_events": [],
        }
        for key, value in defaults.items():
            record.setdefault(key, value.copy() if isinstance(value, list) else value)
        record["realm"] = cls._realm_label(record)
        return record

    @classmethod
    def ensure_all(cls, state: GameState) -> None:
        for name in NPCS:
            cls.world_record(state, name)

    @staticmethod
    def _requirement(record: dict[str, Any]) -> int:
        return 120 + int(record.get("realm_index", 0)) * 80

    @classmethod
    def _record(cls, state: GameState, name: str, text: str) -> None:
        record = cls.world_record(state, name)
        entry = f"天玄历{state.calendar_year}年｜{text}"
        life_events = record.setdefault("life_events", [])
        life_events.append(entry)
        record["life_events"] = life_events[-16:]
        state.npc_lifecycle_log.append(f"{name}｜{entry}")
        state.npc_lifecycle_log = state.npc_lifecycle_log[-80:]
        state.last_npc_lifecycle_event = f"{name}：{text}"

    @classmethod
    def _queue_crisis(cls, state: GameState, name: str, kind: str) -> None:
        record = cls.world_record(state, name)
        realm_index = int(record.get("realm_index", 0))
        pill = BREAKTHROUGH_PILLS[min(realm_index, len(BREAKTHROUGH_PILLS) - 1)]
        state.pending_npc_life_events[name] = {
            "kind": kind,
            "created_turn": state.turn,
            "expires_turn": state.turn + 6,
            "realm": record["realm"],
            "pill": pill,
        }
        record["activity"] = "静候破境"
        record["status"] = "寿元将尽" if kind == "寿元将尽" else "破境在即"
        cls._record(state, name, f"{kind}，向你传来一封护道书。六个月内可回应。")

    @classmethod
    def prepare_guard_request(cls, state: GameState, name: str, kind: str = "破境护道") -> dict[str, Any]:
        record = cls.world_record(state, name)
        if not bool(record.get("alive", True)):
            raise ValueError(f"{name}已不在人世。")
        if kind not in {"破境护道", "寿元将尽"}:
            raise ValueError("护道书类型只能是破境护道或寿元将尽。")
        if name not in state.pending_npc_life_events:
            cls._queue_crisis(state, name, kind)
        return state.pending_npc_life_events[name]

    @classmethod
    def _die(cls, state: GameState, name: str, cause: str) -> None:
        record = cls.world_record(state, name)
        if not bool(record.get("alive", True)):
            return
        record["alive"] = False
        record["status"] = "已故"
        record["activity"] = "此生已终"
        record["wounded"] = False
        record["deceased_year"] = state.calendar_year
        record["cause_of_death"] = cause
        state.npc_invitations.pop(name, None)
        state.pending_npc_life_events.pop(name, None)
        if name in state.dao_partners:
            state.dao_partners.remove(name)
        relation = RelationshipEngine.relation(state, name)
        if int(relation.get("affinity", 0)) >= 20:
            relation["path"] = "故人"
        memorial = {
            "name": name,
            "year": state.calendar_year,
            "age": int(record.get("age", 0)),
            "realm": str(record.get("realm", "")),
            "cause": cause,
        }
        state.npc_memorials.append(memorial)
        state.npc_memorials = state.npc_memorials[-30:]
        state.relationship_events.append(f"故人辞世·{name}：{cause}")
        state.relationship_events = state.relationship_events[-20:]
        cls._record(state, name, f"于{record['age']}岁辞世：{cause}。")

    @classmethod
    def _advance_realm(cls, state: GameState, name: str) -> None:
        record = cls.world_record(state, name)
        old_realm = str(record["realm"])
        realm_index = min(len(REALMS) - 1, int(record.get("realm_index", 0)) + 1)
        record["realm_index"] = realm_index
        record["stage_index"] = 0
        record["realm"] = cls._realm_label(record)
        record["lifespan"] = max(int(record.get("lifespan", 0)), LIFESPANS[realm_index])
        record["cultivation_progress"] = 0
        record["wounded"] = False
        record["status"] = "新境稳固"
        record["activity"] = "破境功成"
        cls._record(state, name, f"从{old_realm}踏入{record['realm']}，寿元上限增至{record['lifespan']}。")

    @classmethod
    def _automatic_breakthrough(cls, state: GameState, name: str) -> None:
        record = cls.world_record(state, name)
        realm_index = int(record.get("realm_index", 0))
        chance = max(12, 74 - realm_index * 7 - max(0, NPCS[name].dao_difficulty - 12))
        roll = 1 + cls._number(state, f"npc-auto-breakthrough:{name}:{record['realm']}:{record['age']}", 100)
        if roll <= chance:
            cls._advance_realm(state, name)
            return
        record["cultivation_progress"] = cls._requirement(record) // 2
        fatal = realm_index >= 3 and roll >= min(100, chance + 28)
        if fatal:
            cls._die(state, name, "独自渡劫失败，身死道消")
        else:
            record["wounded"] = True
            record["status"] = "破境受创"
            record["activity"] = "闭关疗伤"
            cls._record(state, name, f"独自冲击下一境失败（判定 {roll}/{chance}），受创闭关。")

    @classmethod
    def advance_year(cls, state: GameState) -> list[str]:
        cls.ensure_all(state)
        events: list[str] = []
        for name in NPCS:
            record = cls.world_record(state, name)
            if not bool(record.get("alive", True)):
                continue
            last_year = int(record.get("last_lifecycle_year", state.calendar_year))
            years = max(0, state.calendar_year - last_year)
            if years <= 0:
                continue
            for year_offset in range(years):
                record["age"] = int(record.get("age", NPCS[name].age)) + 1
                gain = 12 + cls._number(state, f"npc-annual-cultivation:{name}:{last_year + year_offset + 1}", 17)
                record["cultivation_progress"] = int(record.get("cultivation_progress", 0)) + gain
                if bool(record.get("wounded")) and cls._number(state, f"npc-recover:{name}:{last_year + year_offset + 1}", 100) < 55:
                    record["wounded"] = False
                    record["status"] = "伤势已愈"
                requirement = cls._requirement(record)
                if int(record.get("cultivation_progress", 0)) >= requirement:
                    if int(record.get("stage_index", 0)) < len(STAGES) - 1:
                        record["cultivation_progress"] -= requirement
                        record["stage_index"] = int(record.get("stage_index", 0)) + 1
                        record["realm"] = cls._realm_label(record)
                        record["status"] = "道行精进"
                        record["activity"] = "稳固境界"
                        cls._record(state, name, f"修至{record['realm']}。")
                        events.append(f"{name}修至{record['realm']}")
                    elif name not in state.pending_npc_life_events:
                        affinity = RelationshipEngine.affinity(state, name)
                        if affinity >= 20:
                            kind = "寿元将尽" if int(record["lifespan"]) - int(record["age"]) <= 10 else "破境护道"
                            cls._queue_crisis(state, name, kind)
                            events.append(f"{name}{kind}，传信求援")
                        else:
                            cls._automatic_breakthrough(state, name)
                            events.append(state.last_npc_lifecycle_event)
                if not bool(record.get("alive", True)):
                    break
                remaining = int(record.get("lifespan", 0)) - int(record.get("age", 0))
                if remaining <= 0:
                    if name in state.pending_npc_life_events:
                        continue
                    if RelationshipEngine.affinity(state, name) >= 20 and int(record.get("stage_index", 0)) >= 3:
                        cls._queue_crisis(state, name, "寿元将尽")
                        events.append(f"{name}寿元将尽，传信求援")
                    else:
                        cls._die(state, name, "寿元耗尽，坐化于修行之所")
                        events.append(f"{name}寿元耗尽而坐化")
            record["last_lifecycle_year"] = state.calendar_year
        return [event for event in events if event]

    @classmethod
    def expire_pending(cls, state: GameState) -> list[NpcLifeResult]:
        expired = [name for name, event in state.pending_npc_life_events.items() if int(event.get("expires_turn", 0)) < state.turn]
        return [cls.resolve(state, name, "守候") for name in expired]

    @classmethod
    def resolve(cls, state: GameState, name: str, choice: str) -> NpcLifeResult:
        if name not in state.pending_npc_life_events:
            raise ValueError(f"当前没有{name}需要回应的护道之约。")
        aliases = {"赠药": "赠丹", "亲自护道": "护持", "静候天命": "守候"}
        choice = aliases.get(choice, choice)
        if choice not in {"赠丹", "护持", "守候"}:
            raise ValueError("护道方式可选：赠丹／护持／守候。")
        record = cls.world_record(state, name)
        if not bool(record.get("alive", True)):
            raise ValueError(f"{name}已不在人世。")
        event = state.pending_npc_life_events[name]
        realm_index = int(record.get("realm_index", 0))
        bonus = 0
        cost = "无"
        if choice == "赠丹":
            pill = str(event.get("pill") or BREAKTHROUGH_PILLS[min(realm_index, len(BREAKTHROUGH_PILLS) - 1)])
            if state.player.resources.get(pill, 0) < 1:
                raise ValueError(f"乾坤袋中没有{pill}，无法赠丹护道。")
            state.player.resources[pill] -= 1
            if state.player.resources[pill] <= 0:
                state.player.resources.pop(pill, None)
            bonus = 25
            cost = f"{pill}×1"
        elif choice == "护持":
            if state.player.spirit < 30:
                raise ValueError(f"亲自护道需要灵力 30，当前 {state.player.spirit}。")
            state.player.spirit -= 30
            state.player.merit += 2
            bonus = 14
            cost = "灵力 30"

        base = 72 - realm_index * 7 - max(0, NPCS[name].dao_difficulty - 12)
        if str(event.get("kind")) == "寿元将尽":
            base -= 8
        chance = max(5, min(95, base + bonus))
        roll = 1 + cls._number(state, f"npc-aided-breakthrough:{name}:{record['realm']}:{choice}:{event.get('created_turn')}", 100)
        success = roll <= chance
        fatal = False
        state.pending_npc_life_events.pop(name, None)
        if success:
            cls._advance_realm(state, name)
            affinity_gain = 6 if choice != "守候" else 2
            RelationshipEngine.add_affinity(state, name, affinity_gain)
            description = f"{name}借此护持渡过劫数，踏入{record['realm']}。"
        else:
            record["cultivation_progress"] = cls._requirement(record) // 2
            fatal = int(record.get("age", 0)) >= int(record.get("lifespan", 0)) or roll >= min(100, chance + max(14, 30 - realm_index * 3))
            if choice == "护持":
                state.player.health = max(1, state.player.health - 10)
            if fatal:
                cls._die(state, name, "破境渡劫失败，未能熬过寿元大限")
                description = f"你已尽力，{name}仍在劫数中辞世。"
            else:
                record["wounded"] = True
                record["status"] = "破境受创"
                record["activity"] = "闭关疗伤"
                cls._record(state, name, f"护道未成（判定 {roll}/{chance}），幸而保住性命。")
                description = f"{name}破境未成，受创退回洞府疗养。"
        return NpcLifeResult(name, choice, success, fatal, roll, chance, description, cost)

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        cls.ensure_all(state)
        profiles: list[dict[str, Any]] = []
        for name, npc in NPCS.items():
            record = cls.world_record(state, name)
            relation = RelationshipEngine.relation(state, name)
            affinity = int(relation.get("affinity", 0))
            pending = state.pending_npc_life_events.get(name, {})
            remaining = max(0, int(record.get("lifespan", 0)) - int(record.get("age", 0)))
            pill = str(pending.get("pill", ""))
            profiles.append(
                {
                    "name": name,
                    "gender": npc.gender,
                    "identity": npc.identity,
                    "realm": str(record.get("realm", npc.realm)),
                    "age": int(record.get("age", npc.age)),
                    "lifespan": int(record.get("lifespan", LIFESPANS[0])),
                    "years_remaining": remaining,
                    "life_percent": min(100, round(int(record.get("age", 0)) / max(1, int(record.get("lifespan", 1))) * 100)),
                    "location": str(record.get("location", npc.location)),
                    "activity": str(record.get("activity", "各循其道")),
                    "status": str(record.get("status", "安然")),
                    "alive": bool(record.get("alive", True)),
                    "wounded": bool(record.get("wounded", False)),
                    "affinity": affinity,
                    "relation": RelationshipEngine.bond_label(affinity, name in state.dao_partners, str(relation.get("path", ""))),
                    "likes": list(npc.likes),
                    "pending": bool(pending),
                    "pending_kind": str(pending.get("kind", "")),
                    "expires_in": max(0, int(pending.get("expires_turn", state.turn)) - state.turn),
                    "pill": pill,
                    "can_gift_pill": bool(pill and state.player.resources.get(pill, 0) > 0),
                    "can_guard": state.player.spirit >= 30,
                    "life_events": list(record.get("life_events", []))[-4:],
                    "cause_of_death": str(record.get("cause_of_death", "")),
                }
            )
        profiles.sort(key=lambda item: (not bool(item["pending"]), not bool(item["alive"]), -int(item["affinity"]), str(item["name"])))
        return {
            "living_count": sum(1 for item in profiles if item["alive"]),
            "pending_count": sum(1 for item in profiles if item["pending"]),
            "profiles": profiles,
            "memorials": list(reversed(state.npc_memorials[-12:])),
            "history": list(reversed(state.npc_lifecycle_log[-12:])),
            "last_event": state.last_npc_lifecycle_event,
        }
