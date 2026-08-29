from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .state import GameState


Condition = Callable[[GameState], bool]


@dataclass(frozen=True, slots=True)
class StoryChoice:
    id: str
    label: str
    description: str
    tone: str


@dataclass(frozen=True, slots=True)
class StoryNode:
    id: str
    chapter: int
    title: str
    summary: str
    location: str
    condition: Condition
    locked_hint: str
    choices: tuple[StoryChoice, ...]


NODES: tuple[StoryNode, ...] = (
    StoryNode(
        "tide-whisper", 1, "潮声初闻", "青岳地脉传来不合时序的灵潮回响，凡兽躁动，旧碑渗出青光。", "东洲·青岳",
        lambda state: state.phase == "playing", "完成创角后即可调查。",
        (
            StoryChoice("trace", "循迹入山", "亲自追查灵潮源头，可能受伤，但能获得第一手线索。", "danger"),
            StoryChoice("seek-counsel", "访宗问策", "向东洲宗门求证异象，以人情换取更稳妥的情报。", "primary"),
            StoryChoice("observe", "按兵观潮", "暂不卷入各方争夺，静观地脉变化并磨炼道心。", "quiet"),
        ),
    ),
    StoryNode(
        "vein-rift", 2, "灵脉裂隙", "两份异地见闻彼此印证：青岳灵脉并非复苏，而是被某种力量从地下撕开。", "东洲·断云涧",
        lambda state: "tide-whisper" in state.story_completed and state.journey_counters.get("exploration", 0) >= 2,
        "完成第一章，并累计探索两次。",
        (
            StoryChoice("seal", "布阵封隙", "消耗灵石稳定地脉，改善东洲民生并降低天下局势。", "safe"),
            StoryChoice("harvest", "引灵入体", "冒险截取喷涌灵气，获得修为与材料，却会扩大裂隙。", "danger"),
            StoryChoice("report", "昭告诸宗", "把证据交给诸宗会盟，以声望推动各方共同戒备。", "primary"),
        ),
    ),
    StoryNode(
        "demon-seal", 3, "古印魔痕", "裂隙深处显出上古封印。灵气潮汐只是表象，被镇压千年的意志正在苏醒。", "东洲·古战场",
        lambda state: "vein-rift" in state.story_completed and state.player.realm_index >= 1,
        "完成第二章并成功筑基。",
        (
            StoryChoice("guard", "重铸封印", "以功德和资源修补古印，为九州争取时间。", "safe"),
            StoryChoice("study", "参悟魔纹", "承担业力研究封印，换取稀有道韵和更深真相。", "danger"),
            StoryChoice("summon", "召集同道", "凭声望聚集宗门与散修，共同守住东洲。", "primary"),
        ),
    ),
)

NODE_BY_ID = {node.id: node for node in NODES}


class StoryEngine:
    @classmethod
    def available_node(cls, state: GameState) -> StoryNode | None:
        for node in NODES:
            if node.id not in state.story_completed and node.condition(state):
                return node
        return None

    @classmethod
    def begin(cls, state: GameState) -> StoryNode:
        node = cls.available_node(state)
        if node is None:
            raise ValueError(cls.next_hint(state))
        state.pending_story_node = node.id
        state.phase = "main_story_choice"
        return node

    @classmethod
    def resolve(cls, state: GameState, choice_id: str) -> tuple[StoryNode, StoryChoice, str]:
        node = NODE_BY_ID.get(state.pending_story_node)
        if node is None:
            raise ValueError("当前没有等待抉择的主线因果。")
        choice = next((item for item in node.choices if item.id == choice_id), None)
        if choice is None:
            raise ValueError("请选择当前主线中列出的行动。")
        result = cls._apply(state, node.id, choice.id)
        state.story_choices[node.id] = choice.id
        state.story_completed.append(node.id)
        state.story_history.append(f"第{node.chapter}章《{node.title}》｜{choice.label}｜{result}")
        state.story_history = state.story_history[-30:]
        state.pending_story_node = ""
        state.phase = "playing"
        state.main_quest = cls.available_node(state).title if cls.available_node(state) else "灵潮真相待续"
        return node, choice, result

    @staticmethod
    def _apply(state: GameState, node_id: str, choice_id: str) -> str:
        p = state.player
        if (node_id, choice_id) == ("tide-whisper", "trace"):
            p.health = max(1, p.health - 12); p.resources["灵脉石"] = p.resources.get("灵脉石", 0) + 1; state.world_tension += 2
            return "气血 -12，灵脉石×1，天下局势 +2"
        if (node_id, choice_id) == ("tide-whisper", "seek-counsel"):
            p.reputation += 3; state.faction_strengths["青云宗"] = min(100, state.faction_strengths.get("青云宗", 70) + 2)
            return "声望 +3，青云宗实力 +2"
        if (node_id, choice_id) == ("tide-whisper", "observe"):
            p.dao_heart += 1; state.world_tension += 4
            return "道心 +1，天下局势 +4"
        if (node_id, choice_id) == ("vein-rift", "seal"):
            if p.spirit_stones < 120: raise ValueError("布阵封隙需要 120 灵石。")
            p.spirit_stones -= 120; p.merit += 5; state.regional_prosperity["东洲"] = min(100, state.regional_prosperity.get("东洲", 50) + 6); state.world_tension = max(0, state.world_tension - 5)
            return "灵石 -120，功德 +5，东洲民生 +6，天下局势 -5"
        if (node_id, choice_id) == ("vein-rift", "harvest"):
            p.cultivation = min(p.cultivation_required, p.cultivation + 35); p.resources["五行灵珠"] = p.resources.get("五行灵珠", 0) + 1; p.karma += 3; state.world_tension += 7
            return "修为 +35，五行灵珠×1，业力 +3，天下局势 +7"
        if (node_id, choice_id) == ("vein-rift", "report"):
            p.reputation += 6; state.world_tension = max(0, state.world_tension - 2)
            return "声望 +6，天下局势 -2"
        if (node_id, choice_id) == ("demon-seal", "guard"):
            if p.merit < 5: raise ValueError("重铸封印需要至少 5 点功德。")
            p.merit -= 5; state.world_tension = max(0, state.world_tension - 12); state.regional_prosperity["东洲"] = min(100, state.regional_prosperity.get("东洲", 50) + 8)
            return "功德 -5，天下局势 -12，东洲民生 +8"
        if (node_id, choice_id) == ("demon-seal", "study"):
            p.karma += 8; p.resources["道韵"] = p.resources.get("道韵", 0) + 2; state.world_tension += 6
            return "业力 +8，道韵×2，天下局势 +6"
        p.reputation += 8; p.merit += 3; state.faction_strengths["青云宗"] = min(100, state.faction_strengths.get("青云宗", 70) + 5)
        return "声望 +8，功德 +3，青云宗实力 +5"

    @classmethod
    def next_hint(cls, state: GameState) -> str:
        for node in NODES:
            if node.id not in state.story_completed:
                return f"下一章《{node.title}》尚未解锁：{node.locked_hint}"
        return "当前主线篇章已经完成，后续因果将在新版本续写。"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, object]:
        available = cls.available_node(state)
        pending_node = NODE_BY_ID.get(state.pending_story_node)
        choice_labels = {node.id: {choice.id: choice.label for choice in node.choices} for node in NODES}
        return {
            "title": pending_node.title if pending_node else available.title if available else state.main_quest,
            "completed": len(state.story_completed),
            "total": len(NODES),
            "available": available is not None,
            "begin_action": "推进主线",
            "next_hint": pending_node.summary if pending_node else available.summary if available else cls.next_hint(state),
            "pending": state.pending_story_node,
            "chapters": [{"id": n.id, "chapter": n.chapter, "title": n.title, "summary": n.summary, "location": n.location, "completed": n.id in state.story_completed, "choice": choice_labels[n.id].get(state.story_choices.get(n.id, ""), ""), "unlocked": n.condition(state) or state.pending_story_node == n.id or n.id in state.story_completed, "locked_hint": n.locked_hint} for n in NODES],
            "history": list(reversed(state.story_history)),
        }

    @classmethod
    def decision(cls, state: GameState) -> dict[str, object]:
        node = NODE_BY_ID.get(state.pending_story_node)
        if node is None:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        return {"eyebrow": f"主线第 {node.chapter} 章", "title": node.title, "hint": "此选择会推进一个月，并永久写入本世因果。", "exclusive": True, "choices": [{"label": c.label, "action": f"主线选择 {c.id}", "description": c.description, "tone": c.tone} for c in node.choices]}

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        data = cls.snapshot(state)
        lines = [f"【主线卷宗 · {data['title']}】", f"篇章 {data['completed']}/{data['total']}｜{data['next_hint']}"]
        if data["available"]:
            lines.append("当前篇章可推进｜输入：推进主线")
        lines.append("【因果留痕】")
        lines.extend(data["history"] or ["尚未作出主线抉择。"])
        return "\n".join(str(line) for line in lines)
