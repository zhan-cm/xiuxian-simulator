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
    route: str


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
            StoryChoice("trace", "循迹入山", "亲自追查灵潮源头，可能受伤，但能获得第一手线索。", "danger", "seek"),
            StoryChoice("seek-counsel", "访宗问策", "向东洲宗门求证异象，以人情换取更稳妥的情报。", "primary", "unite"),
            StoryChoice("observe", "按兵观潮", "暂不卷入各方争夺，静观地脉变化并磨炼道心。", "quiet", "guard"),
        ),
    ),
    StoryNode(
        "vein-rift", 2, "灵脉裂隙", "两份异地见闻彼此印证：青岳灵脉并非复苏，而是被某种力量从地下撕开。", "东洲·断云涧",
        lambda state: "tide-whisper" in state.story_completed and state.journey_counters.get("exploration", 0) >= 2,
        "完成第一章，并累计探索两次。",
        (
            StoryChoice("seal", "布阵封隙", "消耗灵石稳定地脉，改善东洲民生并降低天下局势。", "safe", "guard"),
            StoryChoice("harvest", "引灵入体", "冒险截取喷涌灵气，获得修为与材料，却会扩大裂隙。", "danger", "seek"),
            StoryChoice("report", "昭告诸宗", "把证据交给诸宗会盟，以声望推动各方共同戒备。", "primary", "unite"),
        ),
    ),
    StoryNode(
        "demon-seal", 3, "古印魔痕", "裂隙深处显出上古封印。灵气潮汐只是表象，被镇压千年的意志正在苏醒。", "东洲·古战场",
        lambda state: "vein-rift" in state.story_completed and state.player.realm_index >= 1,
        "完成第二章并成功筑基。",
        (
            StoryChoice("guard", "重铸封印", "以功德和资源修补古印，为九州争取时间。", "safe", "guard"),
            StoryChoice("study", "参悟魔纹", "承担业力研究封印，换取稀有道韵和更深真相。", "danger", "seek"),
            StoryChoice("summon", "召集同道", "凭声望聚集宗门与散修，共同守住东洲。", "primary", "unite"),
        ),
    ),
    StoryNode(
        "abyss-tide", 4, "魔潮越界", "古印松动的余波越过东洲，南疆火脉化作魔潮，凡城与修士同时被卷入。", "南疆·赤炎岭",
        lambda state: "demon-seal" in state.story_completed and len(set(state.visited_regions)) >= 2,
        "完成第三章，并踏访至少两域。",
        (
            StoryChoice("shelter", "守城安民", "留下护送凡民撤离，以自身气血换取南疆生机。", "safe", "guard"),
            StoryChoice("delve", "深入魔隙", "逆流进入魔潮源头，承担伤势与业力，夺取魔髓中的真相。", "danger", "seek"),
            StoryChoice("rally", "联络五域", "传讯沿途故交与地方势力，让各域第一次共同应对魔潮。", "primary", "unite"),
        ),
    ),
    StoryNode(
        "nine-realms-council", 5, "九州会盟", "灵潮与魔潮同时逼近，中州天阙台召集九州诸宗，争论最后一道防线应由谁掌控。", "中州·天阙台",
        lambda state: "abyss-tide" in state.story_completed and state.player.location.startswith("中州"),
        "完成第四章，并亲自抵达中州。",
        (
            StoryChoice("great-ward", "共筑天幕", "投入两百灵石补足大阵缺口，以万民安危压过宗门私争。", "safe", "guard"),
            StoryChoice("pierce-heaven", "独探天隙", "不等会盟争出结果，独自穿过天隙寻找潮汐背后的飞升旧路。", "danger", "seek"),
            StoryChoice("bind-oath", "缔结九州盟誓", "以声望和前路见闻说服各方立誓，共担灵潮之后的天下。", "primary", "unite"),
        ),
    ),
    StoryNode(
        "tide-conclusion", 6, "潮汐终局", "登仙台上，灵潮、魔意与断裂天门同时显现。你必须决定九州此后以何种方式继续。", "中州·登仙台",
        lambda state: "nine-realms-council" in state.story_completed and state.player.realm_index >= 2,
        "完成第五章，并踏入结晶境。",
        (
            StoryChoice("guard-world", "镇世封天", "把灵潮重新引入九州山河，守住人间，却暂缓飞升之路。", "safe", "guard"),
            StoryChoice("open-gate", "叩问天门", "以己身踏入断裂天门，向未知仙界追问飞升断绝的真相。", "danger", "seek"),
            StoryChoice("unite-realms", "万宗共潮", "让诸宗与五域共同承接灵潮，建立不再由一门独占的九州新约。", "primary", "unite"),
        ),
    ),
)

NODE_BY_ID = {node.id: node for node in NODES}
ROUTE_LABELS = {"guard": "守世", "seek": "问天", "unite": "同道"}
ENDING_INFO = {
    "guard-world": {
        "route": "guard", "title": "人间长明", "era": "灵潮新世", "legacy": "九州守望",
        "epilogue": "天门在你身后缓缓合拢，灵潮化作山河新脉。此世未必人人飞升，却终于有人能安稳活到明日。",
    },
    "open-gate": {
        "route": "seek", "title": "天门初开", "era": "天门初开", "legacy": "天门见证",
        "epilogue": "你踏过断裂天门，将九州的疑问带向无垠虚空。飞升不再只是传说，但门后究竟是什么，仍待后来者求证。",
    },
    "unite-realms": {
        "route": "unite", "title": "九州同盟", "era": "九州盟世", "legacy": "万宗执盟",
        "epilogue": "灵潮被分入五域与万宗，再无人能独占天命。旧日宗门仍会争斗，但九州第一次拥有共同守护的誓约。",
    },
}


class StoryEngine:
    @staticmethod
    def alignments(state: GameState) -> dict[str, int]:
        scores = {route: 0 for route in ROUTE_LABELS}
        for node in NODES:
            selected = state.story_choices.get(node.id, "")
            choice = next((item for item in node.choices if item.id == selected), None)
            if choice and node.id != "tide-conclusion":
                scores[choice.route] += 1
        return scores

    @classmethod
    def ending_preview(cls, state: GameState, choice_id: str) -> dict[str, object]:
        info = ENDING_INFO[choice_id]
        route = str(info["route"])
        resonance = cls.alignments(state)[route]
        if resonance >= 4:
            quality = "道途圆满"
        elif resonance >= 3:
            quality = "因果相契"
        elif resonance >= 2:
            quality = "勉力成局"
        else:
            quality = "逆势而行"
        return {
            **info,
            "resonance": resonance,
            "quality": quality,
            "perfected": resonance >= 3,
        }

    @staticmethod
    def _choice_access(state: GameState, node_id: str, choice_id: str) -> tuple[bool, str]:
        if (node_id, choice_id) == ("vein-rift", "seal") and state.player.spirit_stones < 120:
            return False, "布阵封隙需要 120 灵石"
        if (node_id, choice_id) == ("demon-seal", "guard") and state.player.merit < 5:
            return False, "重铸封印需要至少 5 点功德"
        if (node_id, choice_id) == ("nine-realms-council", "great-ward") and state.player.spirit_stones < 200:
            return False, "共筑天幕需要 200 灵石"
        return True, ""

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
        available, reason = cls._choice_access(state, node.id, choice.id)
        if not available:
            raise ValueError(reason + "。")
        result = cls._apply(state, node.id, choice.id)
        state.story_choices[node.id] = choice.id
        state.story_completed.append(node.id)
        state.story_history.append(f"第{node.chapter}章《{node.title}》｜{choice.label}｜{result}")
        state.story_history = state.story_history[-30:]
        state.pending_story_node = ""
        state.phase = "playing"
        next_node = cls.available_node(state)
        next_incomplete = next((item for item in NODES if item.id not in state.story_completed), None)
        state.main_quest = (
            next_node.title
            if next_node
            else str(state.story_ending.get("title", next_incomplete.title if next_incomplete else "灵潮真相待续"))
        )
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
        if (node_id, choice_id) == ("demon-seal", "summon"):
            p.reputation += 8; p.merit += 3; state.faction_strengths["青云宗"] = min(100, state.faction_strengths.get("青云宗", 70) + 5)
            return "声望 +8，功德 +3，青云宗实力 +5"
        if (node_id, choice_id) == ("abyss-tide", "shelter"):
            p.health = max(1, p.health - 10)
            p.merit += 4
            state.regional_prosperity["南疆"] = min(100, state.regional_prosperity.get("南疆", 50) + 7)
            state.world_tension = max(0, state.world_tension - 4)
            return "气血 -10，功德 +4，南疆民生 +7，天下局势 -4"
        if (node_id, choice_id) == ("abyss-tide", "delve"):
            p.health = max(1, p.health - 15)
            p.resources["魔髓晶核"] = p.resources.get("魔髓晶核", 0) + 1
            p.resources["道韵"] = p.resources.get("道韵", 0) + 1
            p.karma += 3
            state.world_tension += 5
            return "气血 -15，魔髓晶核×1，道韵×1，业力 +3，天下局势 +5"
        if (node_id, choice_id) == ("abyss-tide", "rally"):
            p.reputation += 5
            for region in state.regional_reputation:
                state.regional_reputation[region] += 2
            for faction in state.faction_strengths:
                state.faction_strengths[faction] = min(100, state.faction_strengths[faction] + 2)
            state.world_tension = max(0, state.world_tension - 2)
            return "声望 +5，五域声望 +2，四方势力 +2，天下局势 -2"
        if (node_id, choice_id) == ("nine-realms-council", "great-ward"):
            p.spirit_stones -= 200
            p.merit += 6
            for region in state.regional_prosperity:
                state.regional_prosperity[region] = min(100, state.regional_prosperity[region] + 2)
            state.world_tension = max(0, state.world_tension - 8)
            return "灵石 -200，功德 +6，五域民生 +2，天下局势 -8"
        if (node_id, choice_id) == ("nine-realms-council", "pierce-heaven"):
            p.health = max(1, p.health - 18)
            p.resources["道韵"] = p.resources.get("道韵", 0) + 2
            p.dao_heart += 1
            state.world_tension += 8
            return "气血 -18，道韵×2，道心 +1，天下局势 +8"
        if (node_id, choice_id) == ("nine-realms-council", "bind-oath"):
            p.reputation += 8
            for faction in state.faction_strengths:
                state.faction_strengths[faction] = min(100, state.faction_strengths[faction] + 4)
            state.world_tension = max(0, state.world_tension - 6)
            return "声望 +8，四方势力 +4，天下局势 -6"
        if node_id == "tide-conclusion":
            return StoryEngine._apply_ending(state, choice_id)
        raise ValueError("未知的主线因果。")

    @classmethod
    def _apply_ending(cls, state: GameState, choice_id: str) -> str:
        preview = cls.ending_preview(state, choice_id)
        perfected = bool(preview["perfected"])
        p = state.player
        if choice_id == "guard-world":
            shift = 30 if perfected else 18
            state.world_tension = max(0, state.world_tension - shift)
            p.merit += 10 if perfected else 5
            for region in state.regional_prosperity:
                state.regional_prosperity[region] = min(100, state.regional_prosperity[region] + (6 if perfected else 3))
            if perfected:
                p.health_max += 10
                p.health = min(p.health_max, p.health + 10)
            reward = f"天下局势 -{shift}，功德 +{10 if perfected else 5}，五域民生 +{6 if perfected else 3}"
        elif choice_id == "open-gate":
            p.resources["道韵"] = p.resources.get("道韵", 0) + (3 if perfected else 1)
            p.spirit_sense += 2 if perfected else 1
            p.dao_heart += 2 if perfected else 1
            state.world_tension += 5 if perfected else 12
            reward = f"道韵×{3 if perfected else 1}，神识 +{2 if perfected else 1}，道心 +{2 if perfected else 1}，天下局势 +{5 if perfected else 12}"
        else:
            p.reputation += 10 if perfected else 5
            for faction in state.faction_strengths:
                state.faction_strengths[faction] = min(100, state.faction_strengths[faction] + (8 if perfected else 4))
            for region in state.regional_reputation:
                state.regional_reputation[region] += 5 if perfected else 2
            shift = 20 if perfected else 10
            state.world_tension = max(0, state.world_tension - shift)
            reward = f"声望 +{10 if perfected else 5}，四方势力 +{8 if perfected else 4}，五域声望 +{5 if perfected else 2}，天下局势 -{shift}"
        legacy = str(preview["legacy"])
        if legacy not in p.destiny_traits:
            p.destiny_traits.append(legacy)
        state.world_era = str(preview["era"])
        milestone = f"天玄历 {state.calendar_year} 年｜灵潮终局·{preview['title']}"
        if milestone not in state.world_milestones:
            state.world_milestones.append(milestone)
        state.story_ending = {
            "id": choice_id,
            "title": preview["title"],
            "route": preview["route"],
            "route_label": ROUTE_LABELS[str(preview["route"])],
            "resonance": preview["resonance"],
            "quality": preview["quality"],
            "perfected": perfected,
            "epilogue": preview["epilogue"],
            "legacy": legacy,
            "year": state.calendar_year,
            "turn": state.turn,
        }
        return f"{preview['quality']}·{preview['title']}；{reward}；命格【{legacy}】"

    @classmethod
    def next_hint(cls, state: GameState) -> str:
        for node in NODES:
            if node.id not in state.story_completed:
                return f"下一章《{node.title}》尚未解锁：{node.locked_hint}"
        if state.story_ending:
            return str(state.story_ending.get("epilogue", "灵潮终局已经写入本世。"))
        return "灵潮六章已完成，终局因果已经写入本世。"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, object]:
        available = cls.available_node(state)
        pending_node = NODE_BY_ID.get(state.pending_story_node)
        choice_labels = {node.id: {choice.id: choice.label for choice in node.choices} for node in NODES}
        alignment_scores = cls.alignments(state)
        dominant_route = max(alignment_scores, key=alignment_scores.get) if any(alignment_scores.values()) else ""
        return {
            "title": pending_node.title if pending_node else available.title if available else state.main_quest,
            "completed": len(state.story_completed),
            "total": len(NODES),
            "available": available is not None,
            "begin_action": "推进主线",
            "next_hint": pending_node.summary if pending_node else available.summary if available else cls.next_hint(state),
            "pending": state.pending_story_node,
            "chapters": [{"id": n.id, "chapter": n.chapter, "act": 1 if n.chapter <= 3 else 2, "title": n.title, "summary": n.summary, "location": n.location, "completed": n.id in state.story_completed, "choice": choice_labels[n.id].get(state.story_choices.get(n.id, ""), ""), "unlocked": n.condition(state) or state.pending_story_node == n.id or n.id in state.story_completed, "locked_hint": n.locked_hint} for n in NODES],
            "alignments": [{"id": route, "label": ROUTE_LABELS[route], "value": alignment_scores[route], "dominant": route == dominant_route} for route in ROUTE_LABELS],
            "ending": dict(state.story_ending),
            "history": list(reversed(state.story_history)),
        }

    @classmethod
    def decision(cls, state: GameState) -> dict[str, object]:
        node = NODE_BY_ID.get(state.pending_story_node)
        if node is None:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        choices = []
        for choice in node.choices:
            available, reason = cls._choice_access(state, node.id, choice.id)
            summary = f"因果倾向：{ROUTE_LABELS[choice.route]}"
            tooltip = "本次选择会为对应因果倾向增加一重共鸣。"
            if node.id == "tide-conclusion":
                preview = cls.ending_preview(state, choice.id)
                summary = f"{ROUTE_LABELS[choice.route]}共鸣 {preview['resonance']}/5 · {preview['quality']}"
                tooltip = f"前五章中有 {preview['resonance']} 次选择与此终局相契；达到 3 次可获得圆满回报。"
            choices.append({
                "label": choice.label,
                "action": f"主线选择 {choice.id}",
                "summary": summary,
                "description": choice.description,
                "tooltip": tooltip,
                "tone": choice.tone,
                "disabled": not available,
                "disabled_reason": reason,
            })
        return {"eyebrow": f"主线第 {node.chapter} 章", "title": node.title, "hint": "此选择会推进一个月，并永久写入本世因果。", "exclusive": True, "choices": choices}

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        data = cls.snapshot(state)
        lines = [f"【主线卷宗 · {data['title']}】", f"篇章 {data['completed']}/{data['total']}｜{data['next_hint']}"]
        if data["available"]:
            lines.append("当前篇章可推进｜输入：推进主线")
        lines.append("【因果留痕】")
        lines.extend(data["history"] or ["尚未作出主线抉择。"])
        return "\n".join(str(line) for line in lines)
