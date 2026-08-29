from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .state import GameState


@dataclass(frozen=True, slots=True)
class CommissionReward:
    spirit_stones: int
    reputation: int = 0
    merit: int = 0
    resources: dict[str, int] = field(default_factory=dict)

    def label(self) -> str:
        parts = [f"灵石 +{self.spirit_stones}"]
        if self.reputation:
            parts.append(f"声望 +{self.reputation}")
        if self.merit:
            parts.append(f"功德 +{self.merit}")
        parts.extend(f"{name}×{count}" for name, count in self.resources.items())
        return "、".join(parts)


@dataclass(frozen=True, slots=True)
class CommissionTemplate:
    id: str
    title: str
    issuer: str
    kind: str
    summary: str
    target: str
    required: int
    duration: int
    reward: CommissionReward
    min_realm: int = 0
    requires_sect: bool = False


TEMPLATES: tuple[CommissionTemplate, ...] = (
    CommissionTemplate(
        "herb-delivery", "青岳采露", "百草堂", "resource", "坊中伤药告急，收取新鲜灵药。", "灵药", 3, 6,
        CommissionReward(90, reputation=2, resources={"疗伤丹": 1}),
    ),
    CommissionTemplate(
        "mountain-survey", "雾岭踏查", "青岳巡检司", "counter", "查明山麓异动，留下两份可靠见闻。", "exploration", 2, 7,
        CommissionReward(130, reputation=3),
    ),
    CommissionTemplate(
        "monster-hunt", "除祟悬榜", "镇守府", "counter", "击败一名修士或妖邪，平息近郊祸患。", "combat_victory", 1, 8,
        CommissionReward(210, reputation=5, merit=2),
    ),
    CommissionTemplate(
        "artisan-order", "百艺急单", "天工阁", "counter", "成功完成一次炼丹、炼器或制符。", "craft_success", 1, 8,
        CommissionReward(170, reputation=3, resources={"灵铁": 2}),
    ),
    CommissionTemplate(
        "sect-support", "山门协力", "东洲宗门会盟", "counter", "完成一次所属宗门任务。", "sect_task_success", 1, 7,
        CommissionReward(190, reputation=4, merit=2), requires_sect=True,
    ),
    CommissionTemplate(
        "market-runner", "坊市通筹", "四海商会", "counter", "在坊市完成两笔买卖，疏通物资流转。", "market_trade", 2, 5,
        CommissionReward(110, reputation=2),
    ),
    CommissionTemplate(
        "cultivation-notes", "吐纳札记", "散修互助会", "counter", "累计修炼两个月，整理行功心得。", "cultivation_month", 2, 6,
        CommissionReward(100, merit=2, resources={"聚气丹": 1}),
    ),
)

TEMPLATE_BY_ID = {template.id: template for template in TEMPLATES}
KIND_LABELS = {"resource": "物资交付", "counter": "历练委托"}


class CommissionEngine:
    BOARD_SIZE = 4
    ACTIVE_LIMIT = 2
    ROTATION_MONTHS = 3

    @staticmethod
    def mark(state: GameState, event: str, amount: int = 1) -> None:
        if amount <= 0:
            return
        state.journey_counters[event] = state.journey_counters.get(event, 0) + amount

    @classmethod
    def cycle(cls, state: GameState) -> int:
        return max(0, state.turn // cls.ROTATION_MONTHS)

    @classmethod
    def instance_id(cls, template: CommissionTemplate, cycle: int) -> str:
        return f"{template.id}@{cycle}"

    @classmethod
    def board(cls, state: GameState) -> list[tuple[str, CommissionTemplate]]:
        cycle = cls.cycle(state)
        start = cycle % len(TEMPLATES)
        return [
            (cls.instance_id(TEMPLATES[(start + offset) % len(TEMPLATES)], cycle), TEMPLATES[(start + offset) % len(TEMPLATES)])
            for offset in range(cls.BOARD_SIZE)
        ]

    @staticmethod
    def _eligibility(state: GameState, template: CommissionTemplate) -> tuple[bool, str]:
        if state.player.realm_index < template.min_realm:
            return False, f"至少需要第 {template.min_realm + 1} 大境界"
        if template.requires_sect and state.player.sect == "散修":
            return False, "需要先加入任意宗门"
        return True, ""

    @staticmethod
    def _template_for_record(record: dict[str, Any]) -> CommissionTemplate:
        template = TEMPLATE_BY_ID.get(str(record.get("template_id", "")))
        if template is None:
            raise ValueError("委托内容已失传，可选择放弃该委托。")
        return template

    @classmethod
    def accept(cls, state: GameState, instance_id: str) -> str:
        available = dict(cls.board(state))
        template = available.get(instance_id)
        if template is None:
            raise ValueError("这份悬榜已经轮换，请重新查看委托簿。")
        if instance_id in state.active_commissions:
            raise ValueError("这份委托已经接取。")
        if instance_id in state.completed_commissions:
            raise ValueError("本期这份委托已经完成。")
        if len(state.active_commissions) >= cls.ACTIVE_LIMIT:
            raise ValueError(f"同时最多追踪 {cls.ACTIVE_LIMIT} 份委托，请先交付或放弃一份。")
        eligible, reason = cls._eligibility(state, template)
        if not eligible:
            raise ValueError(reason)
        baseline = 0 if template.kind == "resource" else state.journey_counters.get(template.target, 0)
        state.active_commissions[instance_id] = {
            "template_id": template.id,
            "accepted_turn": state.turn,
            "deadline_turn": state.turn + template.duration,
            "baseline": baseline,
        }
        cls._remember(state, f"接取《{template.title}》")
        return f"已接取《{template.title}》，限期 {template.duration} 个月。"

    @classmethod
    def progress(cls, state: GameState, record: dict[str, Any], template: CommissionTemplate) -> int:
        if template.kind == "resource":
            return max(0, state.player.resources.get(template.target, 0))
        baseline = int(record.get("baseline", 0))
        return max(0, state.journey_counters.get(template.target, 0) - baseline)

    @classmethod
    def deliver(cls, state: GameState, instance_id: str) -> str:
        record = state.active_commissions.get(instance_id)
        if record is None:
            raise ValueError("没有追踪这份委托。")
        template = cls._template_for_record(record)
        if state.turn > int(record.get("deadline_turn", state.turn)):
            cls._fail(state, instance_id, template, "逾期")
            raise ValueError(f"《{template.title}》已经逾期，未能领取报酬。")
        current = cls.progress(state, record, template)
        if current < template.required:
            raise ValueError(f"《{template.title}》尚未完成：{current}/{template.required}。")
        if template.kind == "resource":
            state.player.resources[template.target] -= template.required
            if state.player.resources[template.target] <= 0:
                state.player.resources.pop(template.target, None)
        state.player.spirit_stones += template.reward.spirit_stones
        state.player.reputation += template.reward.reputation
        state.player.merit += template.reward.merit
        for name, count in template.reward.resources.items():
            state.player.resources[name] = state.player.resources.get(name, 0) + count
        state.active_commissions.pop(instance_id, None)
        state.completed_commissions.append(instance_id)
        state.commission_renown += 1
        cls._remember(state, f"完成《{template.title}》｜{template.reward.label()}")
        return f"《{template.title}》交付完成｜{template.reward.label()}"

    @classmethod
    def abandon(cls, state: GameState, instance_id: str) -> str:
        record = state.active_commissions.get(instance_id)
        if record is None:
            raise ValueError("没有追踪这份委托。")
        template = cls._template_for_record(record)
        overdue = state.turn > int(record.get("deadline_turn", state.turn))
        cls._fail(state, instance_id, template, "逾期" if overdue else "主动放弃")
        return f"已撤下《{template.title}》；{'逾期不再扣除信誉' if overdue else '委托信誉 -1'}。"

    @classmethod
    def expire_overdue(cls, state: GameState) -> list[str]:
        expired: list[str] = []
        for instance_id, record in list(state.active_commissions.items()):
            if state.turn <= int(record.get("deadline_turn", state.turn)):
                continue
            try:
                template = cls._template_for_record(record)
            except ValueError:
                state.active_commissions.pop(instance_id, None)
                continue
            cls._fail(state, instance_id, template, "逾期")
            expired.append(template.title)
        return expired

    @classmethod
    def _fail(cls, state: GameState, instance_id: str, template: CommissionTemplate, reason: str) -> None:
        state.active_commissions.pop(instance_id, None)
        if reason != "逾期":
            state.commission_renown = max(0, state.commission_renown - 1)
        cls._remember(state, f"《{template.title}》{reason}")

    @staticmethod
    def _remember(state: GameState, text: str) -> None:
        state.commission_history.append(text)
        if len(state.commission_history) > 40:
            state.commission_history = state.commission_history[-40:]

    @classmethod
    def _offer_data(cls, state: GameState, instance_id: str, template: CommissionTemplate) -> dict[str, Any]:
        eligible, disabled_reason = cls._eligibility(state, template)
        accepted = instance_id in state.active_commissions
        completed = instance_id in state.completed_commissions
        if accepted:
            disabled_reason = "已经接取"
        elif completed:
            disabled_reason = "本期已经完成"
        elif len(state.active_commissions) >= cls.ACTIVE_LIMIT:
            disabled_reason = "追踪栏位已满"
        requirement = f"交付 {template.target}×{template.required}" if template.kind == "resource" else template.summary
        return {
            "id": instance_id,
            "template_id": template.id,
            "title": template.title,
            "issuer": template.issuer,
            "kind": template.kind,
            "kind_label": KIND_LABELS[template.kind],
            "summary": template.summary,
            "requirement": requirement,
            "duration": template.duration,
            "reward": template.reward.label(),
            "accepted": accepted,
            "completed": completed,
            "eligible": eligible and not accepted and not completed and len(state.active_commissions) < cls.ACTIVE_LIMIT,
            "disabled_reason": disabled_reason,
            "accept_action": f"接取委托 {instance_id}",
        }

    @classmethod
    def _active_data(cls, state: GameState, instance_id: str, record: dict[str, Any]) -> dict[str, Any]:
        template = cls._template_for_record(record)
        current = min(cls.progress(state, record, template), template.required)
        deadline = int(record.get("deadline_turn", state.turn))
        turns_left = max(0, deadline - state.turn)
        return {
            **cls._offer_data(state, instance_id, template),
            "current": current,
            "required": template.required,
            "progress": round(current * 100 / template.required),
            "ready": current >= template.required and state.turn <= deadline,
            "expired": state.turn > deadline,
            "turns_left": turns_left,
            "deadline_turn": deadline,
            "deliver_action": f"交付委托 {instance_id}",
            "abandon_action": f"放弃委托 {instance_id}",
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        cycle = cls.cycle(state)
        next_turn = (cycle + 1) * cls.ROTATION_MONTHS
        offers = [cls._offer_data(state, instance_id, template) for instance_id, template in cls.board(state)]
        active: list[dict[str, Any]] = []
        for instance_id, record in state.active_commissions.items():
            try:
                active.append(cls._active_data(state, instance_id, record))
            except ValueError:
                continue
        return {
            "title": "东洲悬榜",
            "cycle": cycle,
            "rotation_label": f"{max(1, next_turn - state.turn)} 个月后轮换",
            "active_limit": cls.ACTIVE_LIMIT,
            "active_count": len(active),
            "renown": state.commission_renown,
            "completed_count": len(state.completed_commissions),
            "offers": offers,
            "active": active,
            "history": list(reversed(state.commission_history[-5:])),
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        data = cls.snapshot(state)
        lines = [
            f"【东洲悬榜】信誉 {data['renown']}｜追踪 {data['active_count']}/{data['active_limit']}｜{data['rotation_label']}",
            "【在途委托】",
        ]
        if data["active"]:
            for item in data["active"]:
                status = "可交付" if item["ready"] else "已逾期" if item["expired"] else f"{item['current']}/{item['required']}"
                lines.append(f"{item['title']}｜{status}｜余 {item['turns_left']} 月｜编号 {item['id']}")
        else:
            lines.append("暂无，可从本期悬榜接取两份。")
        lines.append("【本期悬榜】")
        for item in data["offers"]:
            status = item["disabled_reason"] or "可接取"
            lines.append(f"{item['title']}｜{item['issuer']}｜{item['requirement']}｜{item['reward']}｜{status}｜编号 {item['id']}")
        lines.append("指令：接取委托 [编号]／交付委托 [编号]／放弃委托 [编号]")
        return "\n".join(lines)
