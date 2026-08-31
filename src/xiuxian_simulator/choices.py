from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .progression import ProgressionEngine
from .state import GameState
from .story import StoryEngine
from .auctions import AuctionEngine
from .travel import TravelEngine
from .regional import RegionalEngine
from .npc_network import NpcNetworkEngine
from .new_era import NewEraEngine
from .beasts import SpiritBeastEngine
from .formations import FormationEngine
from .legacy import LegacyEngine
from .sect_foundation import SectFoundationEngine


class DecisionCatalog:
    def __init__(self, phases: dict[str, dict[str, Any]]) -> None:
        self.phases = phases

    @classmethod
    def load(cls, path: Path) -> "DecisionCatalog":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or not isinstance(payload.get("phases"), dict):
            raise ValueError(f"抉择内容格式无效：{path}")
        return cls(payload["phases"])

    @staticmethod
    def _empty() -> dict[str, Any]:
        return {
            "eyebrow": "",
            "title": "",
            "hint": "",
            "exclusive": False,
            "choices": [],
        }

    @staticmethod
    def _major_breakthrough(state: GameState) -> dict[str, Any]:
        choices = []
        for route, tone in (("人道", "safe"), ("地道", "primary"), ("天道", "danger")):
            requirements = ProgressionEngine.major_requirements(state.player, route)
            needs = "、".join(f"{name}×{count}" for name, count in requirements.items())
            missing = [f"{name}×{count}" for name, count in requirements.items() if state.player.resources.get(name, 0) < count]
            heart_chance, thunder_chance = ProgressionEngine.major_chances_for_state(state, route)
            route_meaning = {
                "人道": "风险最低，成功后气血与灵力小幅增长。",
                "地道": "风险与潜力均衡，成功后六维与根基同步成长。",
                "天道": "风险最高，成功后获得最强六维与根基成长。",
            }[route]
            choices.append(
                {
                    "label": f"{route}筑基",
                    "action": f"突破 {route}",
                    "summary": f"材料 {needs} · 心魔 {heart_chance}% / 雷劫 {thunder_chance}%",
                    "description": f"需要 {needs}；心魔判定 {heart_chance}%，雷劫判定 {thunder_chance}%。{route_meaning}",
                    "tooltip": f"{route_meaning} 两次判定都通过才算突破成功；所需材料：{needs}。",
                    "tone": tone,
                    "disabled": bool(missing),
                    "disabled_reason": "缺少 " + "、".join(missing) if missing else "",
                }
            )
        choices.append(
            {
                "label": "暂缓突破",
                "action": "取消突破",
                "description": "保留当前修为和资源，稍后再作决定。",
                "tone": "quiet",
            }
        )
        return {
            "eyebrow": "破境路线",
            "title": "选择此番道基",
            "hint": "按钮会直接尝试对应路线；失败也会产生真实后果。",
            "exclusive": True,
            "choices": choices,
        }

    @staticmethod
    def _destiny_choices(state: GameState) -> dict[str, Any]:
        choices = [
            {
                "label": trait,
                "action": f"选择 {index}",
                "description": f"将【{trait}】永久写入本世命格。",
                "tone": "primary",
            }
            for index, trait in enumerate(state.pending_choices, 1)
        ]
        return {
            "eyebrow": "逆天改命",
            "title": "三项天资，只可取其一",
            "hint": "点击天资名称即可选择，不需要再输入编号。",
            "exclusive": True,
            "choices": choices,
        }

    @staticmethod
    def _invitations(state: GameState) -> dict[str, Any]:
        choices: list[dict[str, str]] = []
        for name, invitation in state.npc_invitations.items():
            kind = str(invitation.get("kind", "相见"))
            choices.extend(
                (
                    {
                        "label": f"接受{name}的{kind}",
                        "action": f"回应 {name} 接受",
                        "description": "赴约会推进一个月，并按邀约类型获得成长。",
                        "tone": "primary",
                    },
                    {
                        "label": f"婉拒{name}",
                        "action": f"回应 {name} 婉拒",
                        "description": "不赴此约，对方好感会略微下降。",
                        "tone": "quiet",
                    },
                )
            )
        return {
            "eyebrow": "故人传音",
            "title": "尚有邀约等待回应",
            "hint": "邀约会在期限后消失；也可以暂时进行其他行动。",
            "exclusive": False,
            "choices": choices,
        }

    @staticmethod
    def _network_dispute(state: GameState) -> dict[str, Any]:
        pending = NpcNetworkEngine.snapshot(state)["pending"]
        if not pending:
            return DecisionCatalog._empty()
        left, right = str(pending["left"]), str(pending["right"])
        return {
            "eyebrow": "众生缘网",
            "title": f"{left}与{right}尚有一桩纷争",
            "hint": f"缘由：{pending['cause']} · {pending['expires_in']} 个月后将自行落幕",
            "exclusive": True,
            "choices": [
                {
                    "label": "出面调停",
                    "action": "介入人情 调停",
                    "summary": f"预计成功率 {pending['mediate_chance']}% · 消耗灵力 20",
                    "description": "兼顾双方立场；成功可修复缘分并提升声望，失败则可能加深嫌隙。",
                    "tooltip": "成功率受道心、声望、双方好感和当前缘势影响。",
                    "tone": "primary",
                    "disabled": not bool(pending["can_mediate"]),
                    "disabled_reason": str(pending["mediate_reason"]),
                },
                {
                    "label": f"偏袒{left}",
                    "action": f"介入人情 偏袒 {left}",
                    "description": f"{left}好感上升，{right}好感下降；双方嫌隙会明显加深。",
                    "tone": "danger",
                    "disabled": not bool(pending["can_favor_left"]),
                    "disabled_reason": f"与{left}好感需达到 10",
                },
                {
                    "label": f"偏袒{right}",
                    "action": f"介入人情 偏袒 {right}",
                    "description": f"{right}好感上升，{left}好感下降；双方嫌隙会明显加深。",
                    "tone": "danger",
                    "disabled": not bool(pending["can_favor_right"]),
                    "disabled_reason": f"与{right}好感需达到 10",
                },
                {
                    "label": "静观其变",
                    "action": "介入人情 旁观",
                    "description": "不消耗资源，由二人自行处理；关系可能缓和，也可能恶化。",
                    "tone": "quiet",
                },
            ],
        }

    def for_state(self, state: GameState) -> dict[str, Any]:
        if state.phase == "ended":
            return LegacyEngine.decision(state)
        if state.phase == "sect_foundation_choice":
            return SectFoundationEngine.decision(state)
        if state.phase == "beast_taming":
            return SpiritBeastEngine.decision(state)
        if state.phase == "main_story_choice":
            return StoryEngine.decision(state)
        if state.phase == "new_era_choice":
            return NewEraEngine.decision(state)
        if state.phase == "auction_choice":
            return AuctionEngine.decision(state)
        if state.phase == "travel_choice":
            return TravelEngine.decision(state)
        if state.phase == "regional_choice":
            return RegionalEngine.decision(state)
        if state.phase == "major_breakthrough_choice":
            return self._major_breakthrough(state)
        if state.phase == "breakthrough_talent_choice":
            return self._destiny_choices(state)
        if state.phase == "playing" and state.pending_npc_network_event:
            return self._network_dispute(state)
        if state.phase == "playing" and state.npc_invitations:
            return self._invitations(state)

        decision = deepcopy(self.phases.get(state.phase, self._empty()))
        if state.phase == "combat_ready" and state.combat.get("source") != "challenge":
            decision["choices"] = [
                choice for choice in decision.get("choices", []) if choice.get("requires") != "challenge_source"
            ]
        for choice in decision.get("choices", []):
            choice.pop("requires", None)
            if state.phase == "combat" and choice.get("action") == "召唤战宠":
                active = SpiritBeastEngine.active(state)
                reason = ""
                if not active:
                    reason = "当前没有随行战宠"
                elif state.combat.get("beast_summoned"):
                    reason = "本场战斗已经召唤过战宠"
                elif int(active[1].get("vigor", 0)) < SpiritBeastEngine.SUMMON_VIGOR_COST:
                    reason = "战宠精力不足"
                elif state.player.spirit < SpiritBeastEngine.SUMMON_SPIRIT_COST:
                    reason = f"需要 {SpiritBeastEngine.SUMMON_SPIRIT_COST} 点灵力"
                choice["disabled"] = bool(reason)
                choice["disabled_reason"] = reason
            if state.phase == "combat" and choice.get("action") == "催动阵法":
                available, reason = FormationEngine.combat_availability(state)
                choice["disabled"] = not available
                choice["disabled_reason"] = reason
        return decision
