from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state import GameState


@dataclass(frozen=True, slots=True)
class EraChoice:
    id: str
    label: str
    description: str
    tone: str
    route: str


@dataclass(frozen=True, slots=True)
class EraEvent:
    id: str
    title: str
    summary: str
    location: str
    region: str
    choices: tuple[EraChoice, ...]


SCORE_INFO = {
    "stability": ("山河安定", "守", "百姓、灵脉与五域民生能否承受新世变化。"),
    "discovery": ("天机求索", "问", "九州对天门、灵潮与上界真相的理解。"),
    "unity": ("九州同盟", "同", "宗门与五域共同承担风险、分享机缘的程度。"),
}

EVENTS_BY_ROUTE: dict[str, tuple[EraEvent, ...]] = {
    "guard": (
        EraEvent(
            "wandering-veins", "灵脉迁徙", "封天之后，新生灵脉开始穿过凡城与旧宗山门，谁都想先划下界限。", "东洲·青岳", "东洲",
            (
                EraChoice("stabilize", "安置迁脉", "投入灵石引导灵脉绕过凡城，先保住百姓与田土。", "safe", "stability"),
                EraChoice("investigate", "剖析新脉", "亲入灵脉深处辨明潮汐规律，为后来者留下完整图谱。", "danger", "discovery"),
                EraChoice("convene", "五域共议", "召集宗门与地方代表，共同订立新灵脉的开采章程。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "sealed-sky-quake", "封天余震", "闭合的天门投下最后一道震波，中州阵基与数座凡城同时告急。", "中州·天阙台", "中州",
            (
                EraChoice("stabilize", "固守阵基", "用灵石修补天幕阵眼，把余震挡在城外。", "safe", "stability"),
                EraChoice("investigate", "追摄余光", "冒险截取天门余光，查明封天是否真的断绝飞升。", "danger", "discovery"),
                EraChoice("convene", "分镇九州", "请五域共同承担阵眼，让封天不再只由一人维系。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "mountain-spirits", "山河生灵", "灵潮融入山河后，草木精怪骤增，人与新生灵族第一次争夺栖身之地。", "北原·雪境", "北原",
            (
                EraChoice("stabilize", "划界安民", "先划出安全界线，避免边城与灵族继续冲突。", "safe", "stability"),
                EraChoice("investigate", "问灵寻源", "走入雪境与新生灵族交谈，追索它们苏醒的根源。", "danger", "discovery"),
                EraChoice("convene", "立山河约", "让修士、凡民与灵族共同立约，承认彼此的生存边界。", "primary", "unity"),
            ),
        ),
    ),
    "seek": (
        EraEvent(
            "heavenly-echo", "天门回声", "断裂天门再度传来陌生神念，它似乎知道飞升路为何断绝。", "中州·登仙台", "中州",
            (
                EraChoice("stabilize", "封存回声", "先用阵法隔绝神念，避免它侵入凡人梦境。", "safe", "stability"),
                EraChoice("investigate", "神识应答", "以神识回应门后存在，换取第一段上界坐标。", "danger", "discovery"),
                EraChoice("convene", "诸宗共听", "公开回声，让九州共同辨别其中真伪。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "void-visitor", "虚空来客", "一艘破损古舟坠入西漠，舟中修士自称来自另一座早已枯竭的世界。", "西漠·流沙海", "西漠",
            (
                EraChoice("stabilize", "隔离古舟", "安置来客并封锁泄漏的虚空气息。", "safe", "stability"),
                EraChoice("investigate", "同舟问界", "登上古舟查阅星图，验证九州是否只是诸界之一。", "danger", "discovery"),
                EraChoice("convene", "九州会审", "请五域共同接待来客，避免秘密被一宗独占。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "lost-immortal-text", "失落仙简", "北原冰层下出土一卷仙简，记载的飞升法却会抽干整片雪原。", "北原·玄冰谷", "北原",
            (
                EraChoice("stabilize", "镇封仙简", "暂封禁法，先保全北原生灵与冰脉。", "safe", "stability"),
                EraChoice("investigate", "逆演仙法", "承担反噬拆解禁法，寻找不牺牲一域的飞升可能。", "danger", "discovery"),
                EraChoice("convene", "公示诸宗", "把仙简拓本交给九州共同研究与监督。", "primary", "unity"),
            ),
        ),
    ),
    "unite": (
        EraEvent(
            "oath-fracture", "盟誓裂痕", "首轮灵潮资源分配后，数个宗门指责中州偏袒旧盟，九州盟誓出现裂纹。", "中州·天阙台", "中州",
            (
                EraChoice("stabilize", "平抑争端", "拿出灵石补足受损宗门，先让争端停下来。", "safe", "stability"),
                EraChoice("investigate", "清查旧账", "追查盟约账册中的异常流向，承担触怒大宗的风险。", "danger", "discovery"),
                EraChoice("convene", "重议盟约", "召集五域重新表决资源章程，让盟誓接受公开检验。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "five-realm-tithe", "五域灵税", "为维持跨域大阵，盟会提出统一灵税，散修与小宗却担心再无立足之地。", "南疆·赤炎岭", "南疆",
            (
                EraChoice("stabilize", "减税济民", "以个人灵石填补缺口，减轻凡城与散修负担。", "safe", "stability"),
                EraChoice("investigate", "核验阵耗", "亲查大阵损耗，确认灵税是否真的不可削减。", "danger", "discovery"),
                EraChoice("convene", "分阶共担", "推动按宗门实力分阶纳税，让弱者保有生路。", "primary", "unity"),
            ),
        ),
        EraEvent(
            "shared-frontier", "边境共守", "魔潮残部冲击西漠边境，首支跨宗联合队伍即将接受真正考验。", "西漠·流沙海", "西漠",
            (
                EraChoice("stabilize", "固守边城", "投入物资加固城防，确保战火不越过聚落。", "safe", "stability"),
                EraChoice("investigate", "追入魔踪", "越过边线追查魔潮残部，寻找其最后巢穴。", "danger", "discovery"),
                EraChoice("convene", "联军轮守", "建立五域轮守制度，让共同防线不因一战而散。", "primary", "unity"),
            ),
        ),
    ),
}

EVENT_BY_ID = {event.id: event for events in EVENTS_BY_ROUTE.values() for event in events}


class NewEraEngine:
    INTERVAL_MONTHS = 6

    @classmethod
    def activate(cls, state: GameState) -> None:
        if not state.story_ending or state.new_era_scores:
            return
        route = str(state.story_ending.get("route", "guard"))
        baselines = {
            "guard": {"stability": 62, "discovery": 24, "unity": 36},
            "seek": {"stability": 34, "discovery": 62, "unity": 24},
            "unite": {"stability": 42, "discovery": 30, "unity": 62},
        }
        state.new_era_scores = dict(baselines.get(route, baselines["guard"]))
        state.next_new_era_turn = state.turn + 3
        state.new_era_history.append(f"【{state.story_ending.get('title', state.world_era)}】之后，新世余波开始在九州显现。")

    @classmethod
    def _route(cls, state: GameState) -> str:
        route = str(state.story_ending.get("route", "guard"))
        return route if route in EVENTS_BY_ROUTE else "guard"

    @classmethod
    def next_event(cls, state: GameState) -> EraEvent | None:
        if not state.story_ending:
            return None
        events = EVENTS_BY_ROUTE[cls._route(state)]
        return events[state.new_era_counter % len(events)]

    @classmethod
    def tick(cls, state: GameState) -> str:
        if not state.story_ending or state.phase == "ended":
            return ""
        cls.activate(state)
        if state.pending_new_era_event or state.new_era_available_event or state.turn < state.next_new_era_turn:
            return ""
        event = cls.next_event(state)
        if event is None:
            return ""
        state.new_era_available_event = event.id
        message = f"新世余波《{event.title}》在{event.location}显现，等待你亲自处置。"
        state.last_world_event = message
        state.world_events.append(f"天玄历 {state.calendar_year} 年·{state.month}月｜{message}")
        state.world_events = state.world_events[-100:]
        return message

    @classmethod
    def begin(cls, state: GameState) -> EraEvent:
        if not state.story_ending:
            raise ValueError("灵潮终局尚未落定，新世余波还未开启。")
        cls.activate(state)
        event = EVENT_BY_ID.get(state.new_era_available_event)
        if event is None:
            remaining = max(0, state.next_new_era_turn - state.turn)
            raise ValueError(f"当前没有需要处置的新世余波；预计 {remaining} 个月后出现新的变局。")
        state.pending_new_era_event = event.id
        state.new_era_available_event = ""
        state.phase = "new_era_choice"
        return event

    @staticmethod
    def _choice_access(state: GameState, choice: EraChoice) -> tuple[bool, str]:
        if choice.id == "stabilize" and state.player.spirit_stones < 80:
            return False, "安定山河需要 80 灵石"
        if choice.id == "investigate" and state.player.spirit < 20:
            return False, "追索天机需要 20 灵力"
        return True, ""

    @staticmethod
    def _adjust_score(state: GameState, key: str, amount: int) -> None:
        state.new_era_scores[key] = max(0, min(100, int(state.new_era_scores.get(key, 0)) + amount))

    @classmethod
    def resolve(cls, state: GameState, choice_id: str) -> tuple[EraEvent, EraChoice, str]:
        event = EVENT_BY_ID.get(state.pending_new_era_event)
        if event is None:
            raise ValueError("当前没有等待抉择的新世余波。")
        choice = next((item for item in event.choices if item.id == choice_id), None)
        if choice is None:
            raise ValueError("请选择当前余波中列出的应对方式。")
        available, reason = cls._choice_access(state, choice)
        if not available:
            raise ValueError(reason + "。")

        p = state.player
        region = event.region
        if choice.id == "stabilize":
            p.spirit_stones -= 80
            p.merit += 2
            cls._adjust_score(state, "stability", 10)
            cls._adjust_score(state, "unity", 2)
            state.world_tension = max(0, state.world_tension - 3)
            state.regional_prosperity[region] = min(100, int(state.regional_prosperity.get(region, 50)) + 5)
            outcome = f"灵石 -80，功德 +2，山河安定 +10，九州同盟 +2，{region}民生 +5"
        elif choice.id == "investigate":
            p.spirit -= 20
            p.karma += 1
            p.resources["新世道纹"] = p.resources.get("新世道纹", 0) + 1
            cls._adjust_score(state, "discovery", 10)
            cls._adjust_score(state, "stability", -2)
            state.world_tension = min(100, state.world_tension + 3)
            outcome = "灵力 -20，业力 +1，新世道纹×1，天机求索 +10，山河安定 -2，天下局势 +3"
        else:
            p.reputation += 2
            cls._adjust_score(state, "unity", 10)
            cls._adjust_score(state, "stability", 3)
            state.regional_reputation[region] = int(state.regional_reputation.get(region, 0)) + 3
            for faction in state.faction_strengths:
                state.faction_strengths[faction] = min(100, int(state.faction_strengths[faction]) + 1)
            outcome = f"声望 +2，九州同盟 +10，山河安定 +3，{region}声望 +3，四方势力 +1"

        cycle = state.new_era_counter + 1
        state.new_era_counter = cycle
        record: dict[str, Any] = {
            "cycle": cycle,
            "event": event.id,
            "title": event.title,
            "choice": choice.id,
            "choice_label": choice.label,
            "route": choice.route,
            "year": state.calendar_year,
            "turn": state.turn,
        }
        state.new_era_choices.append(record)
        state.new_era_choices = state.new_era_choices[-30:]
        state.new_era_history.append(f"第{cycle}轮《{event.title}》｜{choice.label}｜{outcome}")
        state.new_era_history = state.new_era_history[-40:]
        state.pending_new_era_event = ""
        state.next_new_era_turn = state.turn + cls.INTERVAL_MONTHS
        state.phase = "playing"
        if cycle % 3 == 0:
            milestone = f"天玄历{state.calendar_year}年｜新世第{cycle // 3}纪落定：{cls.stage(state)}。"
            state.world_milestones.append(milestone)
            state.world_milestones = state.world_milestones[-50:]
        return event, choice, outcome

    @staticmethod
    def stage(state: GameState) -> str:
        if state.new_era_counter == 0:
            return "新世将启"
        if state.new_era_counter < 3:
            return "余波初定"
        if state.new_era_counter < 6:
            return "新世奠基"
        return "世局渐成"

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["active"]:
            return "【新世卷宗】灵潮终局尚未落定。"
        score_lines = "\n".join(f"{item['label']}：{item['value']}/100" for item in snapshot["scores"])
        event = snapshot["event"]
        if snapshot["pending"]:
            event_line = f"待决余波：《{event['title']}》｜{event['location']}"
        elif snapshot["available"]:
            event_line = f"新余波：《{event['title']}》｜输入“处置余波”"
        else:
            event_line = f"下一轮余波：约 {snapshot['next_in']} 个月后"
        history = "\n".join(snapshot["history"][-5:]) or "尚无余波处置记录。"
        return f"【新世卷宗 · {snapshot['stage']}】\n{score_lines}\n{event_line}\n\n【近世留痕】\n{history}"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        if not state.story_ending:
            return {
                "active": False, "title": "新世未启", "stage": "灵潮未定", "completed": 0,
                "available": False, "pending": "", "next_in": 0, "begin_action": "处置余波",
                "scores": [], "event": {}, "history": [], "ending_route": "",
            }
        scores = state.new_era_scores or {"stability": 0, "discovery": 0, "unity": 0}
        maximum = max(scores.values()) if scores else 0
        event_id = state.pending_new_era_event or state.new_era_available_event
        event = EVENT_BY_ID.get(event_id) or cls.next_event(state)
        event_payload = {}
        if event:
            event_payload = {
                "id": event.id, "title": event.title, "summary": event.summary,
                "location": event.location, "region": event.region,
            }
        return {
            "active": True,
            "title": str(state.story_ending.get("title", state.world_era)) + "之后",
            "stage": cls.stage(state),
            "completed": state.new_era_counter,
            "available": bool(state.new_era_available_event),
            "pending": state.pending_new_era_event,
            "next_in": max(0, state.next_new_era_turn - state.turn),
            "begin_action": "处置余波",
            "scores": [
                {
                    "id": key, "label": info[0], "mark": info[1], "help": info[2],
                    "value": int(scores.get(key, 0)), "dominant": int(scores.get(key, 0)) == maximum,
                }
                for key, info in SCORE_INFO.items()
            ],
            "event": event_payload,
            "history": list(state.new_era_history[-12:]),
            "ending_route": str(state.story_ending.get("route", "")),
        }

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        event = EVENT_BY_ID.get(state.pending_new_era_event)
        if event is None:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        choices = []
        summaries = {
            "stabilize": "灵石 -80 · 山河安定 +10 · 当地民生 +5",
            "investigate": "灵力 -20 · 天机求索 +10 · 新世道纹×1",
            "convene": "九州同盟 +10 · 山河安定 +3 · 地方声望 +3",
        }
        for choice in event.choices:
            available, reason = cls._choice_access(state, choice)
            choices.append(
                {
                    "label": choice.label,
                    "action": f"新世选择 {choice.id}",
                    "summary": summaries[choice.id],
                    "description": choice.description,
                    "tooltip": f"此选择会推进一个月，并永久改变新世指标。{summaries[choice.id]}。",
                    "tone": choice.tone,
                    "disabled": not available,
                    "disabled_reason": reason,
                }
            )
        return {
            "eyebrow": f"新世第 {state.new_era_counter + 1} 轮",
            "title": event.title,
            "hint": f"{event.location} · 此次应对会成为新世长期历史的一部分。",
            "exclusive": True,
            "choices": choices,
        }
