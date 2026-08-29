from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .state import GameState


Condition = Callable[[GameState], bool]


@dataclass(frozen=True, slots=True)
class JourneyReward:
    points: int = 0
    spirit_stones: int = 0
    reputation: int = 0
    merit: int = 0
    resources: dict[str, int] = field(default_factory=dict)

    def label(self) -> str:
        parts: list[str] = []
        if self.points:
            parts.append(f"历练 +{self.points}")
        if self.spirit_stones:
            parts.append(f"灵石 +{self.spirit_stones}")
        if self.reputation:
            parts.append(f"声望 +{self.reputation}")
        if self.merit:
            parts.append(f"功德 +{self.merit}")
        parts.extend(f"{name}×{count}" for name, count in self.resources.items())
        return "、".join(parts) or "无"


@dataclass(frozen=True, slots=True)
class JourneyTask:
    id: str
    title: str
    description: str
    hint: str
    condition: Condition
    reward: JourneyReward


@dataclass(frozen=True, slots=True)
class JourneyChapter:
    id: str
    number: int
    title: str
    summary: str
    tasks: tuple[JourneyTask, ...]
    reward: JourneyReward


def _history_contains(state: GameState, *needles: str) -> bool:
    return any(any(needle in entry for needle in needles) for entry in state.history)


CHAPTERS: tuple[JourneyChapter, ...] = (
    JourneyChapter(
        "chapter-1",
        1,
        "初涉仙途",
        "先让经脉、脚步与乾坤袋都真正踏入修行。",
        (
            JourneyTask("c1-cultivate", "初次吐纳", "完成一次修炼或闭关。", "从一键行动选择“吐纳修炼”。", lambda state: _history_contains(state, "修炼"), JourneyReward(10, 20)),
            JourneyTask("c1-explore", "踏访青岳", "完成一次东洲探索。", "打开地图，选择可进入地点。", lambda state: _history_contains(state, "探索"), JourneyReward(10, resources={"疗伤丹": 1})),
            JourneyTask("c1-resource", "首份收获", "乾坤袋中拥有任意资源。", "探索、交易或奇遇均可获得物品。", lambda state: bool(state.player.inventory) or sum(state.player.resources.values()) > 0, JourneyReward(10, 30)),
        ),
        JourneyReward(30, 50, reputation=2, resources={"聚气丹": 2}),
    ),
    JourneyChapter(
        "chapter-2",
        2,
        "立足东洲",
        "经营一处根基，也在人、宗与百艺之间找到位置。",
        (
            JourneyTask("c2-cave", "营造洞府", "任意洞府设施达到一级。", "筹措灵石与材料后升级设施。", lambda state: max(state.cave_facilities.values(), default=0) >= 1, JourneyReward(15, resources={"灵药": 3})),
            JourneyTask("c2-craft", "百艺初成", "成功完成一次炼丹、炼器、制符或灵植。", "在技艺面板选择材料充足的配方。", lambda state: sum(state.player.craft_successes.values()) >= 1, JourneyReward(15, 50)),
            JourneyTask("c2-bond", "尘缘落笔", "与任意修士达到 20 好感。", "交谈、论道或赠送对方喜欢的礼物。", lambda state: any(int(item.get("affinity", 0)) >= 20 for item in state.npc_relations.values()), JourneyReward(15, merit=3)),
            JourneyTask("c2-standing", "一方立身", "加入宗门，或让个人声望达到 10。", "宗门与散修声望是两条等价路线。", lambda state: state.player.sect != "散修" or state.player.reputation >= 10, JourneyReward(15, 80)),
        ),
        JourneyReward(50, 120, resources={"筑基丹": 1, "五行灵珠": 1}),
    ),
    JourneyChapter(
        "chapter-3",
        3,
        "名动一州",
        "以筑基修为走过生死、秘境与众人耳目。",
        (
            JourneyTask("c3-foundation", "筑基之门", "成功踏入筑基境。", "炼气圆满后准备合适的突破路线。", lambda state: state.player.realm_index >= 1, JourneyReward(25, reputation=5)),
            JourneyTask("c3-victory", "斗法留名", "赢得一次生死战或切磋。", "先观察敌情，再选择合适战术。", lambda state: state.journey_counters.get("combat_victory", 0) >= 1, JourneyReward(25, 100)),
            JourneyTask("c3-realm", "秘境寻真", "真正进入任意秘境。", "秘境入口确认后才计入章程。", lambda state: _history_contains(state, "确认进入"), JourneyReward(25, resources={"天材地宝": 1})),
            JourneyTask("c3-fame", "声名鹊起", "声望达到 15，或宗门贡献达到 100。", "大比、任务、切磋都能积累名望。", lambda state: state.player.reputation >= 15 or state.player.sect_contribution >= 100, JourneyReward(25, merit=5)),
        ),
        JourneyReward(80, 300, reputation=10, resources={"凝晶丹": 1}),
    ),
    JourneyChapter(
        "chapter-4",
        4,
        "执掌因果",
        "结丹之后，你的选择开始改变他人与九州。",
        (
            JourneyTask("c4-core", "金丹大道", "踏入金丹境。", "积累修为并完成下一次大境界突破。", lambda state: state.player.realm_index >= 2, JourneyReward(40, reputation=8)),
            JourneyTask("c4-dao", "道途有伴", "拥有道侣，或与一人达到 60 好感。", "关系由玩家主动确立，不限定性别。", lambda state: bool(state.dao_partners) or any(int(item.get("affinity", 0)) >= 60 for item in state.npc_relations.values()), JourneyReward(40, merit=8)),
            JourneyTask("c4-world", "落子天下", "完成一次天下干预。", "筑基以上每年可选择一次干预。", lambda state: bool(state.world_interventions), JourneyReward(40, reputation=8)),
            JourneyTask("c4-mastery", "一艺登堂", "任意技艺或洞府设施达到二级。", "持续制作，或继续经营洞府。", lambda state: max((*state.player.craft_skills.values(), *state.cave_facilities.values()), default=0) >= 2, JourneyReward(40, 200)),
        ),
        JourneyReward(120, 500, reputation=15, merit=10, resources={"结丹灵药": 1, "道韵": 1}),
    ),
)


class JourneyEngine:
    @staticmethod
    def mark(state: GameState, event: str, amount: int = 1) -> None:
        state.journey_counters[event] = state.journey_counters.get(event, 0) + amount

    @classmethod
    def chapter_unlocked(cls, state: GameState, chapter: JourneyChapter) -> bool:
        return chapter.number == 1 or f"chapter-{chapter.number - 1}" in state.journey_claims

    @classmethod
    def task_complete(cls, state: GameState, task: JourneyTask) -> bool:
        return bool(task.condition(state))

    @classmethod
    def task_claimed(cls, state: GameState, task: JourneyTask) -> bool:
        return task.id in state.journey_claims

    @classmethod
    def chapter_complete(cls, state: GameState, chapter: JourneyChapter) -> bool:
        return all(cls.task_complete(state, task) for task in chapter.tasks)

    @classmethod
    def chapter_reward_ready(cls, state: GameState, chapter: JourneyChapter) -> bool:
        return all(cls.task_claimed(state, task) for task in chapter.tasks)

    @staticmethod
    def _grant(state: GameState, reward: JourneyReward) -> None:
        state.journey_points += reward.points
        state.player.spirit_stones += reward.spirit_stones
        state.player.reputation += reward.reputation
        state.player.merit += reward.merit
        for name, count in reward.resources.items():
            state.player.resources[name] = state.player.resources.get(name, 0) + count

    @classmethod
    def claim(cls, state: GameState, claim_id: str) -> str:
        if claim_id in state.journey_claims:
            raise ValueError("这份道途奖励已经领取。")
        for chapter in CHAPTERS:
            if claim_id == chapter.id:
                if not cls.chapter_unlocked(state, chapter):
                    raise ValueError("前一章道途尚未完成。")
                if not cls.chapter_reward_ready(state, chapter):
                    raise ValueError("请先完成并领取本章全部历练。")
                cls._grant(state, chapter.reward)
                state.journey_claims.append(chapter.id)
                return f"{chapter.title}章成｜{chapter.reward.label()}"
            for task in chapter.tasks:
                if claim_id != task.id:
                    continue
                if not cls.chapter_unlocked(state, chapter):
                    raise ValueError("这一章道途尚未解锁。")
                if not cls.task_complete(state, task):
                    raise ValueError(f"历练尚未完成：{task.title}。{task.hint}")
                cls._grant(state, task.reward)
                state.journey_claims.append(task.id)
                return f"{task.title}｜{task.reward.label()}"
        raise ValueError("未知的道途奖励。")

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, object]:
        chapters: list[dict[str, object]] = []
        active_id = CHAPTERS[-1].id
        for chapter in CHAPTERS:
            unlocked = cls.chapter_unlocked(state, chapter)
            chapter_claimed = chapter.id in state.journey_claims
            tasks = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "hint": task.hint,
                    "complete": cls.task_complete(state, task),
                    "claimed": cls.task_claimed(state, task),
                    "reward": task.reward.label(),
                    "claim_action": f"领取道途奖励 {task.id}",
                }
                for task in chapter.tasks
            ]
            completed = sum(1 for task in tasks if task["complete"])
            if unlocked and not chapter_claimed and active_id == CHAPTERS[-1].id:
                active_id = chapter.id
            chapters.append(
                {
                    "id": chapter.id,
                    "number": chapter.number,
                    "title": chapter.title,
                    "summary": chapter.summary,
                    "unlocked": unlocked,
                    "claimed": chapter_claimed,
                    "complete": cls.chapter_complete(state, chapter),
                    "completed_tasks": completed,
                    "total_tasks": len(chapter.tasks),
                    "reward_ready": cls.chapter_reward_ready(state, chapter),
                    "reward": chapter.reward.label(),
                    "claim_action": f"领取道途奖励 {chapter.id}",
                    "tasks": tasks,
                }
            )
        active = next(item for item in chapters if item["id"] == active_id)
        return {"points": state.journey_points, "active_chapter_id": active_id, "active": active, "chapters": chapters}

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        data = cls.snapshot(state)
        active = data["active"]
        assert isinstance(active, dict)
        lines = [
            f"【道途章程 · 第{active['number']}章｜{active['title']}】",
            str(active["summary"]),
            f"进度 {active['completed_tasks']}/{active['total_tasks']}｜历练 {data['points']}",
        ]
        for task in active["tasks"]:
            assert isinstance(task, dict)
            status = "已领取" if task["claimed"] else "可领取" if task["complete"] else "进行中"
            lines.append(f"{status}｜{task['title']}｜{task['description']}｜奖励 {task['reward']}")
        if active["reward_ready"] and not active["claimed"]:
            lines.append(f"章成奖励可领取｜{active['reward']}")
        return "\n".join(lines)
