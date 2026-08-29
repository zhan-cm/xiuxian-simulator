from __future__ import annotations

import re
from typing import Any

from .crafting import FACILITY_COSTS, RECIPES
from .progression import REALMS


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
    if any(action_text.startswith(word) for word in ("情缘", "情劫", "对话", "交谈", "送礼", "论道", "结为道侣", "双修", "确立关系", "回应")):
        return "缘", "relation", "红尘一念"
    if any(action_text.startswith(word) for word in ("秘境", "探索", "确认进入", "谨慎探索", "强行探索", "退出秘境")):
        return "游", "adventure", "山河游历"
    if any(action_text.startswith(word) for word in ("买 ", "卖 ", "坊市")):
        return "市", "trade", "坊市往来"
    if any(action_text.startswith(word) for word in ("修炼", "闭关", "参悟")):
        return "修", "cultivation", "静修问心"
    if any(action_text.startswith(word) for word in ("宗门", "加入", "宗门任务", "申请晋升", "宗门大比", "护宗战", "驰援前线", "固守山门", "闭关不出", "叛宗", "确认叛宗")):
        return "宗", "sect", "宗门因果"
    if any(action_text.startswith(word) for word in ("天下", "干预天下", "扶持宗门", "赈济苍生", "探查灵脉", "暂不干预")):
        return "世", "story", "九州大势"
    if (
        action_text in {"开始游戏", "确认默认创角", "面板", "帮助"}
        or action_text.startswith(("存档", "读档"))
        or "=" in action_text
    ):
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


PEOPLE_SECTION_TITLES = ("人物与情缘", "九州人物动态")
PASSIVE_SECTION_TITLES = ("最近动态",)
BUTTON_BACKED_SECTION_TITLES = ("情劫抉择", "大境界突破路线", "逆天改命 · 三选一")
COLLECTION_SECTION_TITLES = (
    "东洲宗门",
    "九州秘境",
    "可交手目标",
    "道法构筑",
    "修仙百艺",
    "已知配方",
    "近期大事记",
    "势力盛衰",
    "五域民生",
    "指令大全",
)
TECHNICAL_PREFIXES = ("判定", "结算", "成功率", "尘缘波澜", "当前好感", "贡献：", "权限：")
MAP_SECTION_TITLES = ("东洲探索地图",)
SECRET_REALM_SECTION_TITLES = ("九州秘境",)
MARKET_SECTION_TITLES = ("青岳坊市",)
CAVE_SECTION_TITLES = ("洞府",)


def _section_lines(section: dict[str, str]) -> list[str]:
    return [line.strip() for line in section.get("body", "").splitlines() if line.strip()]


def _is_people_section(title: str) -> bool:
    return any(word in title for word in PEOPLE_SECTION_TITLES)


def _is_collection_section(title: str) -> bool:
    return any(title.startswith(word) for word in COLLECTION_SECTION_TITLES)


def _is_map_section(title: str) -> bool:
    return any(title.startswith(word) for word in MAP_SECTION_TITLES)


def _is_secret_realm_section(title: str) -> bool:
    return any(title.startswith(word) for word in SECRET_REALM_SECTION_TITLES)


def _is_market_section(title: str) -> bool:
    return any(title.startswith(word) for word in MARKET_SECTION_TITLES)


def _is_cave_section(title: str) -> bool:
    return any(title.startswith(word) for word in CAVE_SECTION_TITLES)


def _is_technical_line(line: str) -> bool:
    return line.startswith(TECHNICAL_PREFIXES) or bool(CHANGE_LINE_PATTERN.match(line))


def _fact_items(lines: list[str]) -> list[dict[str, str]]:
    facts: list[dict[str, str]] = []
    for line in lines:
        for token in (part.strip() for part in line.split("｜") if part.strip()):
            colon = re.match(r"^([^：:]{1,14})[：:]\s*(.+)$", token)
            if colon:
                facts.append({"label": colon.group(1).strip(), "value": colon.group(2).strip()})
                continue
            verdict = re.match(r"^(判定)\s+(.+)$", token)
            if verdict:
                facts.append({"label": verdict.group(1), "value": verdict.group(2).strip()})
                continue
            metric = re.match(r"^(.{1,12}?)\s+([+-]?\d+(?:/\d+)?%?)$", token)
            if metric:
                facts.append({"label": metric.group(1).strip(), "value": metric.group(2)})
    return facts[:12]


def _person_items(lines: list[str], priority_names: set[str]) -> list[dict[str, str]]:
    people: list[dict[str, str]] = []
    for line in lines:
        parts = [part.strip() for part in line.split("｜") if part.strip()]
        if len(parts) < 2:
            people.append(
                {
                    "name": line,
                    "gender": "",
                    "age": "",
                    "identity": "",
                    "descriptor": "",
                    "realm": "",
                    "relation": "",
                    "affinity": "",
                    "location": "",
                }
            )
            continue
        affinity = next((part for part in parts if part.startswith("好感 ")), "")
        affinity_match = re.search(r"好感\s*(-?\d+)(?:（([^）]+)）)?", affinity)
        role = parts[2] if len(parts) > 2 else ""
        identity, _, descriptor = role.partition("·")
        people.append(
            {
                "name": parts[0],
                "gender": parts[1] if len(parts) > 1 else "",
                "age": next((part for part in parts if part.endswith("岁")), ""),
                "identity": identity,
                "descriptor": descriptor,
                "realm": next((part for part in parts if any(word in part for word in ("炼气", "筑基", "金丹", "元婴", "化神"))), ""),
                "relation": affinity_match.group(2) if affinity_match and affinity_match.group(2) else "缘分未定",
                "affinity": affinity_match.group(1) if affinity_match else "",
                "location": next((part.removeprefix("所在地 ") for part in parts if part.startswith("所在地 ")), ""),
            }
        )
    return sorted(people, key=lambda person: (person["name"] not in priority_names, -int(person["affinity"] or 0)))


def _danger_profile(value: int) -> tuple[str, str, str]:
    if value <= 15:
        return "低危", "safe", "适合炼气修士初次探索，仍可能遭遇意外。"
    if value <= 25:
        return "寻常", "normal", "存在明确风险，建议气血与灵力充足后前往。"
    if value <= 35:
        return "高危", "warning", "容易受伤或遭遇强敌，不宜在境界不足时冒险。"
    return "绝境", "danger", "可能致命，仅建议准备充分的高境界修士进入。"


def _minimum_realm(requirement: str) -> int:
    if "炼气" in requirement:
        return 0
    match = re.search(r"(?:至少)?第?\s*(\d+)\s*(?:阶|大境界)", requirement)
    return max(0, int(match.group(1)) - 1) if match else 0


def _location_items(lines: list[str], state: dict[str, Any], action_prefix: str = "探索") -> list[dict[str, Any]]:
    locations: list[dict[str, Any]] = []
    player = state.get("player", {}) or {}
    player_realm = int(player.get("realm_index", 0) or 0)
    current_location = str(player.get("location", ""))
    history = [str(entry) for entry in (state.get("history", []) or [])]
    for line in lines:
        if line.startswith(("输入：", "指令：")):
            continue
        parts = [part.strip() for part in line.split("｜") if part.strip()]
        danger_part = next((part for part in parts if part.startswith("危险度 ")), "")
        danger_match = re.search(r"危险度\s*(\d+)", danger_part)
        if len(parts) < 2 or not danger_match:
            continue
        danger = int(danger_match.group(1))
        label, tone, help_text = _danger_profile(danger)
        minimum_realm = _minimum_realm(parts[1])
        realm_name = REALMS[min(minimum_realm, len(REALMS) - 1)]
        accessible = player_realm >= minimum_realm
        locations.append(
            {
                "name": parts[0],
                "requirement": parts[1],
                "requirement_label": f"{realm_name}境",
                "minimum_realm": minimum_realm,
                "accessible": accessible,
                "locked_reason": "" if accessible else f"需要达到{realm_name}境才可进入",
                "visited": parts[0] in current_location or any(f"探索{parts[0]}" in entry for entry in history),
                "description": parts[3] if len(parts) > 3 else help_text,
                "action": f"{action_prefix} {parts[0]}",
                "danger": danger,
                "danger_label": label,
                "tone": tone,
                "help": help_text,
                "danger_help": f"危险度 {danger}：数值越高，越容易遭遇强敌与不利事件；提升境界可以降低部分风险。",
            }
        )
    return locations


def _market_category(name: str) -> str:
    if name.endswith("丹"):
        return "丹药"
    if "残卷" in name:
        return "功法残卷"
    if any(word in name for word in ("剑", "刃", "衣", "甲", "法袍")):
        return "法器"
    if any(word in name for word in ("符", "符纸")):
        return "符箓"
    if any(word in name for word in ("茶", "酒", "画卷", "剑穗", "灵果", "烤肉", "甜糕", "玉简", "灵石匣")):
        return "礼物"
    return "材料"


def _market_items(lines: list[str], state: dict[str, Any]) -> list[dict[str, Any]]:
    player = state.get("player", {}) or {}
    stones = int(player.get("spirit_stones", 0) or 0)
    resources = player.get("resources", {}) or {}
    inventory = [str(item) for item in (player.get("inventory", []) or [])]
    items: list[dict[str, Any]] = []
    for line in lines:
        match = re.match(r"^(.+?)：买\s*(\d+)／卖\s*(\d+)\s*灵石$", line)
        if not match:
            continue
        name, buy, sell = match.group(1), int(match.group(2)), int(match.group(3))
        owned = int(resources.get(name, 0) or 0) + inventory.count(name)
        items.append(
            {
                "name": name,
                "category": _market_category(name),
                "buy": buy,
                "sell": sell,
                "owned": owned,
                "affordable": stones >= buy,
                "buy_action": f"买 {name}",
                "sell_action": f"卖 {name}",
            }
        )
    return items


def _facility_items(lines: list[str], state: dict[str, Any]) -> list[dict[str, Any]]:
    player = state.get("player", {}) or {}
    stones = int(player.get("spirit_stones", 0) or 0)
    resources = player.get("resources", {}) or {}
    items: list[dict[str, Any]] = []
    for line in lines:
        match = re.match(r"^([^：]+)：(\d+)\s*级$", line)
        if not match or match.group(1) not in FACILITY_COSTS:
            continue
        name, level = match.group(1), int(match.group(2))
        multiplier = level + 1
        base_stones, base_materials = FACILITY_COSTS[name]
        cost_stones = base_stones * multiplier
        materials = {material: count * multiplier for material, count in base_materials.items()}
        missing = [f"{material}×{count}" for material, count in materials.items() if int(resources.get(material, 0) or 0) < count]
        maxed = level >= 3
        affordable = not maxed and stones >= cost_stones and not missing
        items.append(
            {
                "name": name,
                "level": level,
                "max_level": 3,
                "cost_stones": cost_stones,
                "materials": materials,
                "affordable": affordable,
                "disabled_reason": "已达当前最高等级" if maxed else ("缺少 " + "、".join(missing) if missing else (f"需要灵石 {cost_stones}" if stones < cost_stones else "")),
                "action": f"升级洞府 {name}",
            }
        )
    return items


def _recipe_items(lines: list[str], state: dict[str, Any]) -> list[dict[str, Any]]:
    resources = (state.get("player", {}) or {}).get("resources", {}) or {}
    items: list[dict[str, Any]] = []
    for line in lines:
        command, _, result = line.partition("｜")
        parts = command.split(maxsplit=1)
        if len(parts) != 2 or parts[1] not in RECIPES:
            continue
        craft, name = parts
        recipe = RECIPES[name]
        missing = [f"{material}×{count}" for material, count in recipe.ingredients.items() if int(resources.get(material, 0) or 0) < count]
        action_craft = "制符" if craft == "符箓" else craft
        items.append(
            {
                "name": name,
                "craft": craft,
                "ingredients": recipe.ingredients,
                "result": result.strip(),
                "chance": recipe.base_chance,
                "available": not missing,
                "disabled_reason": "缺少 " + "、".join(missing) if missing else "",
                "action": f"{action_craft} {name}",
            }
        )
    return items


def _sect_items(lines: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in lines:
        if line.startswith(("输入：", "指令：")):
            continue
        name, _, description = line.partition("｜")
        if not name:
            continue
        items.append(
            {
                "name": name.strip(),
                "description": description.strip() or "宗门山门常年招收有缘弟子。",
                "action": f"拜入 {name.strip()}",
            }
        )
    return items


def _meter_block(title: str, line: str) -> dict[str, Any] | None:
    match = re.search(r"(-?\d+)\s*/\s*(\d+)", line)
    if not match:
        return None
    summary = line.split("｜", 1)[1].strip() if "｜" in line else ""
    return {
        "type": "meter",
        "mark": title[:1] or "势",
        "title": title,
        "value": int(match.group(1)),
        "max": max(1, int(match.group(2))),
        "summary": summary,
    }


def _default_summary(action: str, tone: str) -> str:
    if tone == "relation":
        return "人物关系已经更新，与你此刻相关的信息已整理如下。"
    if tone == "combat":
        return "本轮交锋已经结算，战局变化已记录。"
    if tone == "cultivation":
        return "本次修行已经结束，修炼所得已计入道途。"
    if tone == "trade":
        return "本次坊市往来已经结算。"
    if tone == "sect":
        return "宗门事务已经推进，相关影响已记录。"
    if action.startswith(("天下", "世情", "干预天下")):
        return "九州局势已经更新，重要变化已归纳如下。"
    return "本次行动已经结算，重要信息已整理如下。"


def _semantic_blocks(
    action: str,
    tone: str,
    paragraphs: list[str],
    sections: list[dict[str, str]],
    changes: list[dict[str, str]],
    state: dict[str, Any],
) -> tuple[list[str], list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    priority_names = {
        change["label"].removesuffix("好感")
        for change in changes
        if change.get("label", "").endswith("好感")
    }
    first_consumed = False
    has_tension_section = any(section["title"].startswith("尘缘波澜") for section in sections[1:])
    if sections:
        first = sections[0]
        first_title = first["title"]
        first_lines = _section_lines(first)
        if (
            not _is_people_section(first_title)
            and not _is_collection_section(first_title)
            and not _is_map_section(first_title)
            and not _is_secret_realm_section(first_title)
            and not _is_market_section(first_title)
            and not _is_cave_section(first_title)
        ):
            narrative = [line for line in first_lines if not _is_technical_line(line)]
            if not paragraphs and narrative:
                paragraphs = narrative[:2]
            technical = [line for line in first_lines if line not in narrative]
            tension_lines = [line for line in technical if line.startswith("尘缘波澜")]
            facts = _fact_items([line for line in technical if line not in tension_lines])
            if facts:
                blocks.append({"type": "facts", "mark": "判", "title": "本次判定", "items": facts})
            if tension_lines and not has_tension_section:
                meter = _meter_block("尘缘波澜", tension_lines[0])
                if meter:
                    blocks.append(meter)
            first_consumed = True

    if not paragraphs:
        paragraphs = [_default_summary(action, tone)]

    for index, section in enumerate(sections):
        if index == 0 and first_consumed:
            continue
        title = section["title"]
        lines = _section_lines(section)
        if not lines or any(title.startswith(word) for word in PASSIVE_SECTION_TITLES + BUTTON_BACKED_SECTION_TITLES):
            continue
        if title.startswith("尘缘波澜"):
            meter = _meter_block(title, lines[0])
            if meter:
                blocks.append(meter)
            continue
        if _is_market_section(title):
            items = _market_items(lines, state)
            if items:
                blocks.append(
                    {
                        "type": "market",
                        "mark": "市",
                        "title": title,
                        "items": items,
                        "currency": int((state.get("player", {}) or {}).get("spirit_stones", 0) or 0),
                    }
                )
            continue
        if _is_cave_section(title):
            items = _facility_items(lines, state)
            crop_line = next((line.removeprefix("灵田：") for line in lines if line.startswith("灵田：") and not re.match(r"^灵田：\d+\s*级$", line)), "无作物")
            if items:
                blocks.append(
                    {
                        "type": "facilities",
                        "mark": "府",
                        "title": title,
                        "items": items,
                        "aura": str(state.get("aura_level", "普通")),
                        "crops": crop_line,
                    }
                )
            continue
        if _is_map_section(title):
            items = _location_items(lines, state)
            if items:
                blocks.append(
                    {
                        "type": "locations",
                        "mark": "图",
                        "title": title,
                        "items": items,
                        "legend": "危险度表示遭遇强敌与不利事件的风险，不是奖励点数；境界不足的地点会自动锁定。",
                    }
                )
            continue
        if _is_secret_realm_section(title):
            items = _location_items(lines, state, action_prefix="进入秘境")
            if items:
                blocks.append(
                    {
                        "type": "locations",
                        "mark": "境",
                        "title": title,
                        "items": items,
                        "legend": "秘境危险度越高，失败时损失越重；进入前仍会要求你亲自确认。",
                    }
                )
            continue
        if title.startswith("已知配方"):
            items = _recipe_items(lines, state)
            if items:
                blocks.append({"type": "recipes", "mark": "艺", "title": title, "items": items})
            continue
        if title.startswith("东洲宗门"):
            items = _sect_items(lines)
            if items:
                blocks.append({"type": "sects", "mark": "宗", "title": title, "items": items})
            continue
        if _is_people_section(title):
            named_in_action = {line.split("｜", 1)[0].strip() for line in lines if line.split("｜", 1)[0].strip() in action}
            items = _person_items(lines, priority_names | named_in_action)
            blocks.append({"type": "people", "mark": "人", "title": "相关人物", "items": items, "preview": 2})
            continue
        facts = _fact_items(lines)
        if facts and len(facts) >= min(2, len(lines)):
            blocks.append({"type": "facts", "mark": title[:1], "title": title, "items": facts})
            continue
        blocks.append(
            {
                "type": "list",
                "mark": title[:1],
                "title": title,
                "items": [{"text": line} for line in lines],
                "preview": 3,
                "collapsed": title.startswith(("近期大事记", "指令大全", "已知配方")),
            }
        )
    return paragraphs[:3], blocks[:5]


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
    changes = _state_changes(before, after)
    paragraphs, blocks = _semantic_blocks(action, tone, paragraphs, sections, changes, after)
    title = sections[0]["title"] if sections and len(sections[0]["title"]) <= 18 else default_title
    details = hidden_details or output.strip()
    return {
        "action": action,
        "title": title,
        "eyebrow": default_title,
        "seal": seal,
        "tone": tone,
        "paragraphs": paragraphs,
        "changes": changes,
        "sections": sections,
        "blocks": blocks,
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
        "blocks": [],
        "details": "",
        "has_details": False,
    }
