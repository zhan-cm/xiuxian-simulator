from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .npc_lifecycle import NpcLifecycleEngine
from .relationships import NPCS, RelationshipEngine
from .state import GameState


REALM_ORDER = {"炼气": 0, "筑基": 1, "结晶": 2, "金丹": 3, "具灵": 4, "元婴": 5, "化神": 6}
TRAVEL_LOCATIONS = ("东洲·青岳", "青岳山麓", "百草谷", "天机坊市")
RELATION_PATHS = ("纯友谊", "结义", "师徒", "宿敌")


@dataclass(frozen=True, slots=True)
class EcologyEvent:
    npc: str
    action: str
    description: str
    invitation: bool = False


class NpcEcologyEngine:
    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = f"{state.rng_seed}:{state.turn}:{state.calendar_year}:{state.month}:{purpose}".encode("utf-8")
        digest = hashlib.sha256(material).digest()
        return int.from_bytes(digest[:8], "big") % maximum

    @classmethod
    def world_record(cls, state: GameState, name: str) -> dict[str, object]:
        return NpcLifecycleEngine.world_record(state, name)

    @classmethod
    def tick(cls, state: GameState) -> EcologyEvent:
        for name in list(state.npc_invitations):
            if int(state.npc_invitations[name].get("expires_turn", 0)) < state.turn:
                state.npc_invitations.pop(name, None)

        names = tuple(name for name in NPCS if bool(cls.world_record(state, name).get("alive", True)))
        if not names:
            return EcologyEvent("九州", "故人寂寥", "昔日故人皆已走完自己的道途，天地仍照常运转。")
        name = names[cls._number(state, "npc-feature", len(names))]
        record = cls.world_record(state, name)
        if name in state.pending_npc_life_events:
            alternatives = tuple(candidate for candidate in names if candidate not in state.pending_npc_life_events)
            if alternatives:
                name = alternatives[cls._number(state, "npc-feature-alternative", len(alternatives))]
                record = cls.world_record(state, name)
        relation = RelationshipEngine.relation(state, name)
        action_index = cls._number(state, f"npc-action:{name}", 5)
        record["events"] = int(record.get("events", 0)) + 1

        if action_index == 0:
            gain = 8 + cls._number(state, f"npc-cultivate:{name}", 13)
            record["cultivation_progress"] = int(record.get("cultivation_progress", 0)) + gain
            record["activity"] = "闭关修行"
            description = f"{name}在{record['location']}闭关参悟，道行积累 +{gain}。"
        elif action_index == 1:
            locations = (NPCS[name].location,) + TRAVEL_LOCATIONS
            destination = locations[cls._number(state, f"npc-travel:{name}", len(locations))]
            record["location"] = destination
            record["activity"] = "外出游历"
            description = f"{name}离开旧地，现身于{destination}。"
        elif action_index == 2:
            earnings = 10 + cls._number(state, f"npc-business:{name}", 31)
            record["spirit_stones"] = int(record.get("spirit_stones", 0)) + earnings
            record["activity"] = "处理自身事务"
            description = f"{name}独自办妥一桩差事，所得灵石 {earnings}。"
        elif action_index == 3:
            wounded = cls._number(state, f"npc-battle:{name}", 100) < 25
            record["wounded"] = wounded
            record["activity"] = "与人斗法"
            description = f"{name}外出斗法，{'负伤归来' if wounded else '全身而退'}。"
        else:
            affinity = int(relation.get("affinity", 0))
            if affinity >= 20 and name not in state.npc_invitations:
                kinds = ("论道", "同行", "委托")
                kind = kinds[cls._number(state, f"npc-invite:{name}", len(kinds))]
                state.npc_invitations[name] = {"kind": kind, "expires_turn": state.turn + 6}
                record["activity"] = "传信相邀"
                description = f"{name}主动传信，邀你{kind}；六个月内可回应。"
                event = EcologyEvent(name, "传信相邀", description, True)
                state.last_npc_event = description
                state.npc_event_log.append(f"第{state.turn}回合｜{description}")
                state.npc_event_log = state.npc_event_log[-50:]
                return event
            record["activity"] = "拜访故交"
            description = f"{name}拜访了一位旧日故交，自己的生活仍在继续。"

        state.last_npc_event = description
        state.npc_event_log.append(f"第{state.turn}回合｜{description}")
        state.npc_event_log = state.npc_event_log[-50:]
        return EcologyEvent(name, str(record["activity"]), description)

    @classmethod
    def respond(cls, state: GameState, name: str, decision: str) -> tuple[str, int, str]:
        RelationshipEngine.npc(name)
        if not bool(cls.world_record(state, name).get("alive", True)):
            raise ValueError(f"{name}已不在人世，旧日邀约也随风而散。")
        if name not in state.npc_invitations:
            raise ValueError(f"当前没有{name}发来的待回应邀约。")
        if decision not in {"接受", "婉拒"}:
            raise ValueError("回应只能选择“接受”或“婉拒”。")
        invitation = state.npc_invitations.pop(name)
        kind = str(invitation["kind"])
        if decision == "婉拒":
            affinity = RelationshipEngine.add_affinity(state, name, -1)
            return kind, affinity, f"你婉拒了{name}的{kind}邀约，好感 -1。"

        affinity = RelationshipEngine.add_affinity(state, name, 5)
        if kind == "论道":
            gain = min(20, max(0, state.player.cultivation_required - state.player.cultivation))
            state.player.cultivation += gain
            reward = f"修为 +{gain}"
        elif kind == "同行":
            state.player.resources["灵药"] = state.player.resources.get("灵药", 0) + 2
            reward = "灵药 +2"
        else:
            state.player.spirit_stones += 40
            reward = "灵石 +40"
        return kind, affinity, f"你接受{name}的{kind}邀约，{reward}，好感 +5。"

    @classmethod
    def set_relation_path(cls, state: GameState, name: str, path: str) -> tuple[str, int]:
        if path not in RELATION_PATHS:
            raise ValueError("关系类型可选：" + "、".join(RELATION_PATHS))
        relation = RelationshipEngine.relation(state, name)
        affinity = int(relation.get("affinity", 0))
        if path == "纯友谊" and affinity < 20:
            raise ValueError(f"确立纯友谊需要好感 20，当前 {affinity}。")
        if path in {"结义", "师徒"} and affinity < 40:
            raise ValueError(f"确立{path}关系需要好感 40，当前 {affinity}。")
        if path == "师徒":
            npc_realm = REALM_ORDER.get(NPCS[name].realm.split("·", 1)[0], 0)
            if npc_realm <= state.player.realm_index:
                raise ValueError(f"{name}当前境界不足以成为你的师长。")
        if path == "宿敌":
            affinity = min(-40, affinity)
            relation["affinity"] = affinity
            if name in state.dao_partners:
                state.dao_partners.remove(name)
        relation["path"] = path
        return path, affinity
