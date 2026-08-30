from __future__ import annotations

import hashlib
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from .relationships import NPCS, RelationshipEngine
from .state import GameState


SEED_BONDS: dict[tuple[str, str], tuple[int, str]] = {
    ("顾清玄", "云栖"): (18, "曾在天机坊市互通消息"),
    ("顾清玄", "谢无咎"): (-16, "正魔立场素有分歧"),
    ("顾清玄", "白凝霜"): (9, "曾于论剑会上有一面之缘"),
    ("云栖", "洛浅浅"): (13, "常以奇闻和灵物互换所需"),
    ("谢无咎", "白凝霜"): (-11, "北原旧事留下芥蒂"),
    ("谢无咎", "墨尘"): (15, "游历西漠时曾并肩脱险"),
    ("墨尘", "洛浅浅"): (8, "彼此知道不少九州逸闻"),
}


@dataclass(frozen=True, slots=True)
class NetworkInterventionResult:
    choice: str
    success: bool
    description: str
    roll: int = 0
    chance: int = 0
    spirit_cost: int = 0


class NpcNetworkEngine:
    """Persistent relationships and autonomous encounters between core NPCs."""

    @staticmethod
    def _number(state: GameState, purpose: str, maximum: int) -> int:
        material = (
            f"{state.rng_seed}:{state.turn}:{state.calendar_year}:{state.month}:network:{purpose}"
        ).encode("utf-8")
        digest = hashlib.sha256(material).digest()
        return int.from_bytes(digest[:8], "big") % maximum

    @staticmethod
    def key(left: str, right: str) -> str:
        if left not in NPCS or right not in NPCS:
            raise ValueError("人物不在九州故人谱中。")
        if left == right:
            raise ValueError("人物不能与自己形成缘网关系。")
        return "|".join(sorted((left, right)))

    @classmethod
    def ensure_all(cls, state: GameState) -> None:
        for (left, right), (score, origin) in SEED_BONDS.items():
            key = cls.key(left, right)
            state.npc_bonds.setdefault(
                key,
                {
                    "left": left,
                    "right": right,
                    "score": score,
                    "encounters": 0,
                    "origin": origin,
                    "last_event": origin,
                    "events": [f"天玄历 {state.calendar_year} 年｜{origin}"],
                },
            )

    @classmethod
    def bond(cls, state: GameState, left: str, right: str) -> dict[str, Any]:
        cls.ensure_all(state)
        key = cls.key(left, right)
        if key not in state.npc_bonds:
            first, second = key.split("|", 1)
            state.npc_bonds[key] = {
                "left": first,
                "right": second,
                "score": 0,
                "encounters": 0,
                "origin": "尚无深交",
                "last_event": "尚无深交",
                "events": [],
            }
        return state.npc_bonds[key]

    @staticmethod
    def bond_label(score: int) -> str:
        if score >= 60:
            return "生死之交"
        if score >= 35:
            return "同盟"
        if score >= 15:
            return "相熟"
        if score > -15:
            return "泛交"
        if score > -40:
            return "嫌隙"
        return "宿敌"

    @staticmethod
    def bond_tone(score: int) -> str:
        if score >= 35:
            return "allied"
        if score >= 15:
            return "friendly"
        if score <= -40:
            return "hostile"
        if score <= -15:
            return "strained"
        return "neutral"

    @classmethod
    def _record(cls, state: GameState, left: str, right: str, description: str, delta: int) -> int:
        bond = cls.bond(state, left, right)
        score = max(-100, min(100, int(bond.get("score", 0)) + delta))
        bond["score"] = score
        bond["encounters"] = int(bond.get("encounters", 0)) + 1
        bond["last_event"] = description
        events = list(bond.get("events", []))
        events.append(f"天玄历 {state.calendar_year} 年｜{description}")
        bond["events"] = events[-12:]
        entry = f"{state.time_label}｜{description}｜缘势 {delta:+d}"
        state.npc_network_log.append(entry)
        state.npc_network_log = state.npc_network_log[-60:]
        state.last_npc_network_event = entry
        return score

    @classmethod
    def create_dispute(cls, state: GameState, left: str, right: str, cause: str) -> dict[str, Any]:
        if state.pending_npc_network_event:
            raise ValueError("已有一桩人物纷争等待处理。")
        if state.npc_world.get(left, {}).get("alive") is False or state.npc_world.get(right, {}).get("alive") is False:
            raise ValueError("故人已逝，旧日纷争不再继续。")
        state.npc_network_counter += 1
        pending = {
            "id": f"缘网-{state.npc_network_counter}",
            "left": left,
            "right": right,
            "cause": cause,
            "expires_turn": state.turn + 4,
            "created_turn": state.turn,
        }
        state.pending_npc_network_event = pending
        return pending

    @classmethod
    def tick(cls, state: GameState) -> str:
        cls.ensure_all(state)
        if state.turn % 3:
            return ""
        living = [name for name in NPCS if state.npc_world.get(name, {}).get("alive", True)]
        pairs = list(combinations(living, 2))
        if not pairs:
            return ""
        left, right = pairs[cls._number(state, "pair", len(pairs))]
        event_index = cls._number(state, f"event:{left}:{right}", 6)

        if event_index == 0:
            delta = 6
            description = f"{left}与{right}结伴历练，互相照应后平安归来。"
        elif event_index == 1:
            delta = 4
            description = f"{left}与{right}坐而论道，虽所修不同，却各有所得。"
        elif event_index == 2:
            delta = 8
            description = f"{left}在险地援手{right}，这一份人情被认真记下。"
            state.npc_world.get(right, {}).update({"wounded": False})
        elif event_index == 3:
            delta = -6
            description = f"{left}与{right}因一处灵地归属争执不下。"
            if not state.pending_npc_network_event:
                cls.create_dispute(state, left, right, "灵地归属")
        elif event_index == 4:
            delta = -9
            description = f"{left}与{right}旧怨爆发，短暂斗法后不欢而散。"
            if not state.pending_npc_network_event:
                cls.create_dispute(state, left, right, "旧怨斗法")
        else:
            delta = 2 if cls._number(state, f"rumor:{left}:{right}", 2) else -2
            description = f"九州传闻将{left}与{right}牵到一处，真相尚无人说清。"

        cls._record(state, left, right, description, delta)
        return description

    @classmethod
    def expire_pending(cls, state: GameState) -> str:
        pending = state.pending_npc_network_event
        if not pending or int(pending.get("expires_turn", 0)) >= state.turn:
            return ""
        left, right = str(pending["left"]), str(pending["right"])
        description = f"{left}与{right}的{pending['cause']}无人介入，嫌隙在沉默中加深。"
        cls._record(state, left, right, description, -4)
        state.pending_npc_network_event = {}
        return description

    @classmethod
    def mediation_requirements(cls, state: GameState, left: str, right: str) -> tuple[bool, int, str]:
        left_affinity = RelationshipEngine.affinity(state, left)
        right_affinity = RelationshipEngine.affinity(state, right)
        known = min(left_affinity, right_affinity) >= 10 or state.player.reputation >= 20
        if state.player.spirit < 20:
            return False, 0, "灵力不足 20"
        if not known:
            return False, 0, "需双方好感至少 10，或声望达到 20"
        score = int(cls.bond(state, left, right).get("score", 0))
        chance = max(
            25,
            min(
                90,
                38
                + state.player.dao_heart * 2
                + state.player.reputation // 2
                + max(0, min(left_affinity, right_affinity)) // 4
                + score // 10,
            ),
        )
        return True, chance, ""

    @classmethod
    def intervene(cls, state: GameState, choice: str, favored: str = "") -> NetworkInterventionResult:
        pending = state.pending_npc_network_event
        if not pending:
            raise ValueError("当前没有可介入的人物纷争。")
        left, right = str(pending["left"]), str(pending["right"])
        if state.npc_world.get(left, {}).get("alive") is False or state.npc_world.get(right, {}).get("alive") is False:
            state.pending_npc_network_event = {}
            raise ValueError("纷争一方已经辞世，此事只能留在旧闻中。")

        if choice == "调停":
            available, chance, reason = cls.mediation_requirements(state, left, right)
            if not available:
                raise ValueError(reason)
            state.player.spirit -= 20
            roll = cls._number(state, f"mediate:{pending['id']}", 100) + 1
            success = roll <= chance
            if success:
                description = f"你分别听取{left}与{right}所言，终于替二人解开眼前死结。"
                cls._record(state, left, right, description, 12)
                RelationshipEngine.add_affinity(state, left, 2)
                RelationshipEngine.add_affinity(state, right, 2)
                state.player.reputation += 2
            else:
                description = f"你试图调停{left}与{right}，却因旧怨太深，反让局面更加僵硬。"
                cls._record(state, left, right, description, -6)
                RelationshipEngine.add_affinity(state, left, -1)
                RelationshipEngine.add_affinity(state, right, -1)
                state.player.reputation = max(0, state.player.reputation - 1)
            result = NetworkInterventionResult("调停", success, description, roll, chance, 20)
        elif choice == "偏袒":
            if favored not in {left, right}:
                raise ValueError(f"只能选择偏袒{left}或{right}。")
            if RelationshipEngine.affinity(state, favored) < 10:
                raise ValueError(f"与{favored}好感尚未达到 10，不足以公开为其出面。")
            other = right if favored == left else left
            description = f"你公开站在{favored}一边；{favored}领了这份情，{other}却将此事记在心中。"
            cls._record(state, left, right, description, -10)
            RelationshipEngine.add_affinity(state, favored, 5)
            RelationshipEngine.add_affinity(state, other, -5)
            state.player.reputation = max(0, state.player.reputation - 2)
            state.player.karma += 2
            result = NetworkInterventionResult(f"偏袒{favored}", True, description)
        elif choice == "旁观":
            roll = cls._number(state, f"observe:{pending['id']}", 100) + 1
            if roll <= 45:
                description = f"你没有介入；{left}与{right}各退一步，此事暂且搁下。"
                cls._record(state, left, right, description, 2)
            else:
                description = f"你选择旁观；{left}与{right}终究未能和解，隔阂更深。"
                cls._record(state, left, right, description, -5)
            result = NetworkInterventionResult("旁观", True, description, roll, 45)
        else:
            raise ValueError("介入方式可选：调停／偏袒 [姓名]／旁观。")

        state.pending_npc_network_event = {}
        return result

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        view = GameState.from_dict(state.to_dict())
        cls.ensure_all(view)
        bonds: list[dict[str, Any]] = []
        for key, item in view.npc_bonds.items():
            left, right = str(item["left"]), str(item["right"])
            if view.npc_world.get(left, {}).get("alive") is False or view.npc_world.get(right, {}).get("alive") is False:
                continue
            score = int(item.get("score", 0))
            bonds.append(
                {
                    "id": key,
                    "left": left,
                    "right": right,
                    "score": score,
                    "label": cls.bond_label(score),
                    "tone": cls.bond_tone(score),
                    "encounters": int(item.get("encounters", 0)),
                    "origin": str(item.get("origin", "尚无深交")),
                    "last_event": str(item.get("last_event", "尚无深交")),
                    "events": list(item.get("events", []))[-5:],
                }
            )
        bonds.sort(key=lambda item: (abs(int(item["score"])), int(item["encounters"])), reverse=True)

        pending = dict(view.pending_npc_network_event)
        if pending:
            left, right = str(pending["left"]), str(pending["right"])
            available, chance, reason = cls.mediation_requirements(view, left, right)
            pending.update(
                {
                    "expires_in": max(0, int(pending["expires_turn"]) - view.turn),
                    "can_mediate": available,
                    "mediate_chance": chance,
                    "mediate_reason": reason,
                    "can_favor_left": RelationshipEngine.affinity(view, left) >= 10,
                    "can_favor_right": RelationshipEngine.affinity(view, right) >= 10,
                }
            )

        connected = {name for item in bonds if int(item["score"]) != 0 for name in (str(item["left"]), str(item["right"]))}
        return {
            "connected_count": len(connected),
            "bond_count": len(bonds),
            "allied_count": sum(1 for item in bonds if int(item["score"]) >= 35),
            "rival_count": sum(1 for item in bonds if int(item["score"]) <= -15),
            "bonds": bonds,
            "pending": pending,
            "history": list(view.npc_network_log)[-10:],
            "last_event": view.last_npc_network_event,
        }
