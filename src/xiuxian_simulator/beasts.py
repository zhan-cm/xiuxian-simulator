from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dao import DaoEngine
from .progression import ProgressionEngine, REALMS
from .state import GameState
from .travel import TravelEngine


@dataclass(frozen=True, slots=True)
class SpiritBeastTemplate:
    id: str
    name: str
    mark: str
    region: str
    element: str
    role: str
    minimum_realm: int
    difficulty: int
    base_power: int
    summary: str
    talent: str


SPIRIT_BEASTS: dict[str, SpiritBeastTemplate] = {
    "qingfeng-fox": SpiritBeastTemplate(
        "qingfeng-fox", "青风狐", "狐", "东洲", "木", "迅袭", 0, 42, 11,
        "生于青岳林海，能借草木气息藏匿身形。", "同行时遁速提高；召唤后撕开敌方破绽。",
    ),
    "stoneback-turtle": SpiritBeastTemplate(
        "stoneback-turtle", "玄甲灵龟", "龟", "东洲", "土", "守御", 0, 48, 8,
        "背甲如玄石，性情沉稳，极少主动伤人。", "同行时提高防御；召唤后替主人承受部分攻势。",
    ),
    "ember-lizard": SpiritBeastTemplate(
        "ember-lizard", "赤焰灵蜥", "蜥", "南疆", "火", "攻伐", 1, 56, 17,
        "栖于赤炎地脉，以火晶与熔岩灵气为食。", "同行时增强攻伐；召唤后喷吐灼热灵焰。",
    ),
    "sand-hawk": SpiritBeastTemplate(
        "sand-hawk", "流沙玄鹰", "鹰", "西漠", "金", "洞察", 2, 62, 20,
        "双翼掠过沙海时不留半点痕迹，目力可穿风障。", "提高命中与遁速；召唤后令下一击必定命中。",
    ),
    "frost-crane": SpiritBeastTemplate(
        "frost-crane", "霜羽灵鹤", "鹤", "北原", "水", "护生", 3, 68, 22,
        "羽落成霜，鸣声能安定气血与紊乱灵机。", "召唤时恢复气血，并减轻本轮所受伤害。",
    ),
    "thunder-cat": SpiritBeastTemplate(
        "thunder-cat", "雷纹灵猫", "猫", "中州", "雷", "奇袭", 1, 64, 19,
        "常卧天阙檐角，动念时雷纹才会沿脊背亮起。", "提高暴击机缘；召唤后以雷爪奇袭。",
    ),
}


class SpiritBeastEngine:
    MAX_LEVEL = 5
    MAX_VIGOR = 100
    SUMMON_SPIRIT_COST = 12
    SUMMON_VIGOR_COST = 15

    @staticmethod
    def template(beast_id: str) -> SpiritBeastTemplate:
        try:
            return SPIRIT_BEASTS[beast_id]
        except KeyError as exc:
            raise ValueError("未知灵兽。") from exc

    @staticmethod
    def owned_id_by_name(state: GameState, name: str) -> str:
        for beast_id, beast in state.spirit_beasts.items():
            if beast_id == name or str(beast.get("name", "")) == name:
                return beast_id
        raise ValueError("尚未收服这只灵兽。")

    @classmethod
    def active(cls, state: GameState) -> tuple[str, dict[str, Any]] | None:
        beast_id = state.active_spirit_beast
        beast = state.spirit_beasts.get(beast_id)
        return (beast_id, beast) if beast_id and beast else None

    @staticmethod
    def _level_up(beast: dict[str, Any]) -> list[int]:
        levels: list[int] = []
        while int(beast.get("level", 1)) < SpiritBeastEngine.MAX_LEVEL:
            level = int(beast.get("level", 1))
            required = level * 20
            if int(beast.get("experience", 0)) < required:
                break
            beast["experience"] = int(beast.get("experience", 0)) - required
            beast["level"] = level + 1
            levels.append(level + 1)
        return levels

    @classmethod
    def record(cls, state: GameState, text: str) -> None:
        state.spirit_beast_history.append(f"第 {state.turn} 回合｜{text}")
        state.spirit_beast_history = state.spirit_beast_history[-30:]

    @classmethod
    def search_candidates(cls, state: GameState) -> list[SpiritBeastTemplate]:
        region = TravelEngine.current_region(state)
        candidates = [beast for beast in SPIRIT_BEASTS.values() if beast.region == region]
        return candidates or [SPIRIT_BEASTS["qingfeng-fox"]]

    @classmethod
    def can_search(cls, state: GameState) -> tuple[bool, str]:
        if state.phase != "playing":
            return False, "请先完成当前抉择"
        if state.player.spirit < 10:
            return False, "探寻兽踪需要至少 10 点灵力"
        candidates = [item for item in cls.search_candidates(state) if item.minimum_realm <= state.player.realm_index]
        if not candidates:
            return False, "当前境界不足以接近本域灵兽"
        return True, ""

    @classmethod
    def search(cls, state: GameState) -> SpiritBeastTemplate:
        allowed, reason = cls.can_search(state)
        if not allowed:
            raise ValueError(reason)
        candidates = [item for item in cls.search_candidates(state) if item.minimum_realm <= state.player.realm_index]
        index = int(state.spirit_beast_searches) % len(candidates)
        beast = candidates[index]
        state.spirit_beast_searches += 1
        state.player.spirit -= 10
        state.pending_spirit_beast = {"id": beast.id, "found_turn": state.turn}
        state.phase = "beast_taming"
        cls.record(state, f"在{beast.region}寻得{beast.name}踪迹")
        return beast

    @classmethod
    def tame_chance(cls, state: GameState, approach: str) -> int:
        pending_id = str(state.pending_spirit_beast.get("id", ""))
        beast = cls.template(pending_id)
        approach_bonus = 20 if approach == "soothe" else 0
        affinity_bonus = 12 if "灵兽亲和" in state.player.destiny_traits else 0
        dao_bonus = DaoEngine.level(state, "御兽道") * 6
        realm_bonus = max(0, state.player.realm_index - beast.minimum_realm) * 10
        return max(
            8,
            min(
                95,
                48 + state.player.spirit_sense * 2 + state.player.fortune + dao_bonus
                + affinity_bonus + realm_bonus + approach_bonus - beast.difficulty,
            ),
        )

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        if state.phase != "beast_taming" or not state.pending_spirit_beast:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}
        beast = cls.template(str(state.pending_spirit_beast["id"]))
        bind_chance = cls.tame_chance(state, "bind")
        soothe_chance = cls.tame_chance(state, "soothe")
        has_material = state.player.resources.get("妖兽材料", 0) >= 1
        return {
            "eyebrow": "灵兽相逢",
            "title": f"{beast.name}正在试探你的气息",
            "hint": "收服会进行真实神识判定；失败可能受伤，放归则不承担风险。",
            "exclusive": True,
            "choices": [
                {
                    "label": "结印收服",
                    "action": "收服灵兽 结印",
                    "summary": f"成功率 {bind_chance}% · 灵力 20",
                    "description": "以神识结下契印；失败会遭到反噬。",
                    "tone": "primary",
                    "disabled": state.player.spirit < 20,
                    "disabled_reason": "需要 20 点灵力" if state.player.spirit < 20 else "",
                },
                {
                    "label": "灵材安抚",
                    "action": "收服灵兽 安抚",
                    "summary": f"成功率 {soothe_chance}% · 妖兽材料×1",
                    "description": "先以同源灵材消除戒心，成功后初始羁绊更深。",
                    "tone": "safe",
                    "disabled": not has_material,
                    "disabled_reason": "缺少 妖兽材料×1" if not has_material else "",
                },
                {
                    "label": "放归山林",
                    "action": "放归灵兽",
                    "description": "不强求这段缘法，功德略有增长。",
                    "tone": "quiet",
                },
            ],
        }

    @classmethod
    def resolve_taming(cls, state: GameState, approach: str) -> dict[str, Any]:
        if state.phase != "beast_taming" or not state.pending_spirit_beast:
            raise ValueError("当前没有等待收服的灵兽。")
        beast_id = str(state.pending_spirit_beast["id"])
        template = cls.template(beast_id)
        if approach == "release":
            state.player.merit += 1
            state.pending_spirit_beast = {}
            state.phase = "playing"
            cls.record(state, f"放归{template.name}，功德 +1")
            return {"success": False, "released": True, "name": template.name, "merit": 1}
        if approach not in {"bind", "soothe"}:
            raise ValueError("请选择结印、安抚或放归。")
        if approach == "bind":
            if state.player.spirit < 20:
                raise ValueError("结印收服需要 20 点灵力。")
            state.player.spirit -= 20
        else:
            if state.player.resources.get("妖兽材料", 0) < 1:
                raise ValueError("安抚灵兽需要 妖兽材料×1。")
            state.player.resources["妖兽材料"] -= 1
            if state.player.resources["妖兽材料"] <= 0:
                state.player.resources.pop("妖兽材料", None)
        chance = cls.tame_chance(state, approach)
        roll = ProgressionEngine.deterministic_roll(state, f"spirit-beast-tame:{beast_id}:{approach}:{state.spirit_beast_searches}")
        success = roll <= chance
        state.pending_spirit_beast = {}
        state.phase = "playing"
        if success:
            existing = state.spirit_beasts.get(beast_id)
            if existing:
                existing["bond"] = min(100, int(existing.get("bond", 0)) + (18 if approach == "soothe" else 10))
                existing["experience"] = int(existing.get("experience", 0)) + 10
                levels = cls._level_up(existing)
            else:
                state.spirit_beasts[beast_id] = {
                    "name": template.name,
                    "level": 1,
                    "experience": 0,
                    "bond": 30 if approach == "soothe" else 20,
                    "vigor": cls.MAX_VIGOR,
                    "obtained_turn": state.turn,
                }
                levels = []
            if not state.active_spirit_beast:
                state.active_spirit_beast = beast_id
            cls.record(state, f"收服{template.name}（{roll}/{chance}）")
            return {"success": True, "released": False, "name": template.name, "roll": roll, "chance": chance, "levels": levels}
        health_loss = 6 + template.minimum_realm * 4
        state.player.health = max(1, state.player.health - health_loss)
        state.player.condition = "御兽反噬" if state.player.health <= max(20, state.player.health_max // 4) else state.player.condition
        cls.record(state, f"收服{template.name}失败（{roll}/{chance}），气血 -{health_loss}")
        return {
            "success": False, "released": False, "name": template.name,
            "roll": roll, "chance": chance, "health_loss": health_loss,
        }

    @classmethod
    def deploy(cls, state: GameState, name: str) -> str:
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择，再调整随行战宠。")
        beast_id = cls.owned_id_by_name(state, name)
        state.active_spirit_beast = beast_id
        template = cls.template(beast_id)
        cls.record(state, f"令{template.name}随行")
        return template.name

    @classmethod
    def feed(cls, state: GameState, name: str) -> dict[str, Any]:
        if state.phase != "playing":
            raise ValueError("请先完成当前抉择，再喂养灵兽。")
        beast_id = cls.owned_id_by_name(state, name)
        if state.player.resources.get("妖兽材料", 0) < 1:
            raise ValueError("喂养需要 妖兽材料×1。")
        state.player.resources["妖兽材料"] -= 1
        if state.player.resources["妖兽材料"] <= 0:
            state.player.resources.pop("妖兽材料", None)
        beast = state.spirit_beasts[beast_id]
        before_bond = int(beast.get("bond", 0))
        before_vigor = int(beast.get("vigor", cls.MAX_VIGOR))
        beast["bond"] = min(100, before_bond + 12)
        beast["vigor"] = min(cls.MAX_VIGOR, before_vigor + 30)
        beast["experience"] = int(beast.get("experience", 0)) + 8
        levels = cls._level_up(beast)
        cls.record(state, f"喂养{beast['name']}，羁绊 +{int(beast['bond']) - before_bond}")
        return {
            "name": beast["name"], "bond_gain": int(beast["bond"]) - before_bond,
            "vigor_gain": int(beast["vigor"]) - before_vigor, "levels": levels,
        }

    @classmethod
    def tick_month(cls, state: GameState) -> None:
        for beast in state.spirit_beasts.values():
            beast["vigor"] = min(cls.MAX_VIGOR, int(beast.get("vigor", cls.MAX_VIGOR)) + 8)

    @classmethod
    def gain_victory(cls, state: GameState) -> str:
        active = cls.active(state)
        if not active:
            return ""
        _, beast = active
        gain = 8 if state.combat.get("beast_summoned") else 4
        beast["experience"] = int(beast.get("experience", 0)) + gain
        beast["bond"] = min(100, int(beast.get("bond", 0)) + 1)
        levels = cls._level_up(beast)
        text = f"{beast['name']}历练 +{gain}"
        if levels:
            text += f"，成长至 {levels[-1]} 级"
        cls.record(state, text)
        return text

    @classmethod
    def injure_active(cls, state: GameState) -> None:
        active = cls.active(state)
        if not active:
            return
        _, beast = active
        beast["vigor"] = max(0, int(beast.get("vigor", cls.MAX_VIGOR)) - 25)

    @classmethod
    def attack_multiplier(cls, state: GameState) -> float:
        active = cls.active(state)
        if not active or int(active[1].get("vigor", 0)) <= 0:
            return 1.0
        template = cls.template(active[0])
        if template.role not in {"攻伐", "奇袭"}:
            return 1.0
        return 1.0 + 0.03 + int(active[1].get("level", 1)) * 0.02

    @classmethod
    def defense_bonus(cls, state: GameState) -> int:
        active = cls.active(state)
        if not active or int(active[1].get("vigor", 0)) <= 0:
            return 0
        return 2 + int(active[1].get("level", 1)) * 2 if cls.template(active[0]).role == "守御" else 0

    @classmethod
    def speed_bonus(cls, state: GameState) -> int:
        active = cls.active(state)
        if not active or int(active[1].get("vigor", 0)) <= 0:
            return 0
        return int(active[1].get("level", 1)) + 1 if cls.template(active[0]).role in {"迅袭", "洞察"} else 0

    @classmethod
    def summon(cls, state: GameState) -> str:
        if state.phase != "combat" or not state.combat:
            raise ValueError("只有战斗中才能召唤战宠。")
        if state.combat.get("beast_summoned"):
            raise ValueError("本场战斗已经召唤过战宠。")
        active = cls.active(state)
        if not active:
            raise ValueError("当前没有随行战宠。")
        beast_id, beast = active
        if int(beast.get("vigor", 0)) < cls.SUMMON_VIGOR_COST:
            raise ValueError("战宠精力不足，需要休养或喂养。")
        if state.player.spirit < cls.SUMMON_SPIRIT_COST:
            raise ValueError(f"召唤战宠需要 {cls.SUMMON_SPIRIT_COST} 点灵力。")
        state.player.spirit -= cls.SUMMON_SPIRIT_COST
        beast["vigor"] = int(beast.get("vigor", 0)) - cls.SUMMON_VIGOR_COST
        state.combat["beast_summoned"] = True
        template = cls.template(beast_id)
        level = int(beast.get("level", 1))
        if template.role == "护生":
            before = state.player.health
            state.player.health = min(state.player.health_max, state.player.health + 15 + level * 5)
            state.combat["beast_guard"] = True
            return f"{template.name}鸣声凝霜，气血 +{state.player.health - before}，并护住本轮"
        if template.role in {"洞察", "迅袭"}:
            state.combat["player_observed"] = True
        if template.role == "守御":
            state.combat["beast_guard"] = True
        damage = max(1, template.base_power + level * 5 - int(state.combat.get("enemy_defense", 0)) // 3)
        state.combat["enemy_health"] = max(0, int(state.combat["enemy_health"]) - damage)
        extra = "，下一击必中" if template.role in {"洞察", "迅袭"} else "，本轮受到的伤害降低" if template.role == "守御" else ""
        return f"{template.name}施展灵兽天赋，造成 {damage} 点伤害{extra}"

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        active = cls.active(state)
        beasts: list[dict[str, Any]] = []
        for beast_id, beast in state.spirit_beasts.items():
            template = cls.template(beast_id)
            level = int(beast.get("level", 1))
            required = level * 20 if level < cls.MAX_LEVEL else 0
            beasts.append(
                {
                    "id": beast_id,
                    "name": template.name,
                    "mark": template.mark,
                    "element": template.element,
                    "role": template.role,
                    "level": level,
                    "max_level": cls.MAX_LEVEL,
                    "experience": int(beast.get("experience", 0)),
                    "experience_required": required,
                    "bond": int(beast.get("bond", 0)),
                    "vigor": int(beast.get("vigor", cls.MAX_VIGOR)),
                    "vigor_max": cls.MAX_VIGOR,
                    "summary": template.summary,
                    "talent": template.talent,
                    "active": active is not None and active[0] == beast_id,
                    "deploy_action": f"出战灵兽 {template.name}",
                    "can_deploy": state.phase == "playing",
                    "deploy_reason": "" if state.phase == "playing" else "请先完成当前抉择",
                    "feed_action": f"喂养灵兽 {template.name}",
                    "can_feed": state.phase == "playing" and state.player.resources.get("妖兽材料", 0) >= 1,
                    "feed_reason": (
                        "请先完成当前抉择"
                        if state.phase != "playing"
                        else ("缺少 妖兽材料×1" if state.player.resources.get("妖兽材料", 0) < 1 else "")
                    ),
                }
            )
        beasts.sort(key=lambda item: (not item["active"], -int(item["level"]), str(item["name"])))
        pending: dict[str, Any] = {}
        if state.pending_spirit_beast:
            template = cls.template(str(state.pending_spirit_beast["id"]))
            pending = {
                "id": template.id,
                "name": template.name,
                "mark": template.mark,
                "element": template.element,
                "role": template.role,
                "summary": template.summary,
                "talent": template.talent,
                "minimum_realm": REALMS[template.minimum_realm],
            }
        can_search, search_reason = cls.can_search(state)
        return {
            "count": len(beasts),
            "active_id": active[0] if active else "",
            "active_name": cls.template(active[0]).name if active else "",
            "beasts": beasts,
            "pending": pending,
            "search_action": "探寻灵兽",
            "can_search": can_search,
            "search_reason": search_reason,
            "materials": state.player.resources.get("妖兽材料", 0),
            "history": list(reversed(state.spirit_beast_history[-8:])),
            "summon_cost": cls.SUMMON_SPIRIT_COST,
        }

    @classmethod
    def panel_text(cls, state: GameState) -> str:
        snapshot = cls.snapshot(state)
        if not snapshot["beasts"]:
            roster = "尚无战宠；可输入“探寻灵兽”追索本域兽踪。"
        else:
            roster = "\n".join(
                f"{item['name']}｜{item['level']}级｜羁绊 {item['bond']}｜精力 {item['vigor']}/{item['vigor_max']}"
                f"｜{item['role']}{'｜随行' if item['active'] else ''}"
                for item in snapshot["beasts"]
            )
        return (
            f"【万灵兽苑】\n随行：{snapshot['active_name'] or '无'}｜妖兽材料 {snapshot['materials']}\n{roster}\n"
            "指令：探寻灵兽／出战灵兽 [名称]／喂养灵兽 [名称]；战斗中可召唤战宠"
        )
