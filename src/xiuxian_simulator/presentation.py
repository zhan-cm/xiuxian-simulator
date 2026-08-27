from __future__ import annotations

import re
from typing import Any


HEADER_PATTERN = re.compile(r"【([^】]+)】")
TIME_PATTERN = re.compile(r"^天玄历\s+\d+\s+年\s*·\s*[^\n]+$")
CHANGE_LINE_PATTERN = re.compile(r"^(修为|气血|灵力|灵石|好感|声望|贡献|功德|业力)\s*[+-]\d+")


METRICS = (
    ("cultivation", "修为", "修", "cultivation"),
    ("health", "气血", "命", "danger"),
    ("spirit", "灵力", "灵", "spirit"),
    ("spirit_stones", "灵石", "石", "wealth"),
    ("sect_contribution", "宗门贡献", "宗", "sect"),
    ("reputation", "声望", "名", "reputation"),
    ("merit", "功德", "德", "merit"),
    ("karma", "业力", "业", "danger"),
)


def _classify(action: str, output: str) -> tuple[str, str, str]:
    action_text = action.strip()
    if any(word in output for word in ("陨落", "坐化", "战败", "死亡")):
        return "劫", "danger", "道途生变"
    if any(action_text.startswith(word) for word in ("开战", "攻击", "战斗", "切磋", "约战", "施法", "防御", "蓄势", "绝技", "遁走", "拾取")):
        return "战", "combat", "斗法交锋"
    if action_text.startswith("突破") or action_text.startswith("选择 "):
        return "破", "breakthrough", "破境问道"
    if any(action_text.startswith(word) for word in ("情缘", "对话", "交谈", "送礼", "论道", "结为道侣", "双修", "确立关系", "回应")):
        return "缘", "relation", "红尘一念"
    if any(action_text.startswith(word) for word in ("秘境", "探索", "确认进入", "谨慎探索", "强行探索", "退出秘境")):
        return "游", "adventure", "山河游历"
    if any(action_text.startswith(word) for word in ("买 ", "卖 ", "坊市")):
        return "市", "trade", "坊市往来"
    if any(action_text.startswith(word) for word in ("修炼", "闭关", "参悟")):
        return "修", "cultivation", "静修问心"
    if any(action_text.startswith(word) for word in ("宗门", "加入", "宗门任务", "申请晋升", "宗门大比", "叛宗", "确认叛宗")):
        return "宗", "sect", "宗门因果"
    if action_text in {"开始游戏", "确认默认创角", "面板", "帮助", "存档", "读档"} or "=" in action_text:
        return "启", "system", "仙途初启"
    text = output[:500]
    if "突破" in text or "逆天改命" in text:
        return "破", "breakthrough", "破境问道"
    if any(word in text for word in ("敌方", "战利品", "战斗轮次")):
        return "战", "combat", "斗法交锋"
    return "道", "story", "天道推演"


def _split_output(output: str) -> tuple[list[str], list[dict[str, str]], str]:
    cleaned = output.strip()
    matches = list(HEADER_PATTERN.finditer(cleaned))
    lead = cleaned[: matches[0].start()].strip() if matches else cleaned
    paragraphs: list[str] = []
    lead_details: list[str] = []
    for raw_line in lead.splitlines():
        line = raw_line.strip()
        if not line or TIME_PATTERN.match(line):
            continue
        if line.startswith(("结算：", "判定：", "判定 ")) or CHANGE_LINE_PATTERN.match(line):
            lead_details.append(line)
        else:
            paragraphs.append(line)
    sections: list[dict[str, str]] = []
    details: list[str] = []

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(cleaned)
        content = cleaned[match.end() : end].strip()
        content_lines = [line.strip() for line in content.splitlines() if line.strip()]
        content_lines = [line for line in content_lines if not line.startswith("指令：")]
        content = "\n".join(content_lines)
        if title.startswith("状态卡") or title.startswith("洞府主界面"):
            if content:
                details.append(f"{title}\n{content}")
            continue
        sections.append(
            {
                "title": title,
                "body": content or "此事已由规则引擎结算。",
                "kind": _section_kind(title),
            }
        )

    if not paragraphs and not sections:
        paragraphs = ["当前状态已更新。"]
    detail_blocks = (["\n".join(lead_details)] if lead_details else []) + details
    return paragraphs[:5], sections[:5], "\n\n".join(detail_blocks)


def _section_kind(title: str) -> str:
    if any(word in title for word in ("警告", "失败", "陨落", "战败")):
        return "danger"
    if any(word in title for word in ("成功", "获胜", "完成", "收获")):
        return "success"
    if any(word in title for word in ("选择", "路线", "面板", "地图", "乾坤袋")):
        return "choice"
    return "note"


def _change(label: str, seal: str, value: int, tone: str) -> dict[str, str]:
    return {
        "label": label,
        "seal": seal,
        "value": f"{value:+d}",
        "tone": "danger" if value < 0 and tone not in {"karma"} else tone,
    }


def _state_changes(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    before_player = before.get("player", {})
    after_player = after.get("player", {})
    for key, label, seal, tone in METRICS:
        old = before_player.get(key, 0)
        new = after_player.get(key, 0)
        if isinstance(old, int) and isinstance(new, int) and old != new:
            changes.append(_change(label, seal, new - old, tone))

    old_resources = before_player.get("resources", {}) or {}
    new_resources = after_player.get("resources", {}) or {}
    for name in sorted(set(old_resources) | set(new_resources)):
        delta = int(new_resources.get(name, 0)) - int(old_resources.get(name, 0))
        if delta:
            changes.append(_change(name, "物", delta, "item"))

    old_relations = before.get("npc_relations", {}) or {}
    new_relations = after.get("npc_relations", {}) or {}
    for name in sorted(set(old_relations) | set(new_relations)):
        old_affinity = int((old_relations.get(name) or {}).get("affinity", 0))
        new_affinity = int((new_relations.get(name) or {}).get("affinity", 0))
        if old_affinity != new_affinity:
            changes.append(_change(f"{name}好感", "缘", new_affinity - old_affinity, "relation"))

    turn_delta = int(after.get("turn", 0)) - int(before.get("turn", 0))
    if turn_delta:
        changes.append({"label": "时间流逝", "seal": "时", "value": f"{turn_delta} 月", "tone": "time"})
    return changes[:10]


def present_action(
    action: str,
    output: str,
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    seal, tone, default_title = _classify(action, output)
    paragraphs, sections, hidden_details = _split_output(output)
    title = sections[0]["title"] if sections and len(sections[0]["title"]) <= 18 else default_title
    details = hidden_details or output.strip()
    return {
        "action": action,
        "title": title,
        "eyebrow": default_title,
        "seal": seal,
        "tone": tone,
        "paragraphs": paragraphs,
        "changes": _state_changes(before, after),
        "sections": sections,
        "details": details,
        "has_details": bool(details),
    }


def welcome_presentation() -> dict[str, Any]:
    return {
        "action": "",
        "title": "灵气潮汐将至",
        "eyebrow": "天道初启",
        "seal": "道",
        "tone": "story",
        "paragraphs": ["九州云海未定，你的长生路尚待落笔。", "点击下方的“开始游戏”，踏入这方修真世界。"],
        "changes": [],
        "sections": [],
        "details": "",
        "has_details": False,
    }
