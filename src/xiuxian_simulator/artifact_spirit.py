from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class SpiritArchetype:
    id: str
    name: str
    title: str
    description: str
    personality: str
    default_name: str
    combat_skill_name: str
    combat_skill_desc: str
    skill_type: str  # "damage", "shield", "hybrid"
    skill_value: int
    attack_multiplier: float = 1.0
    defense_bonus: int = 0
    max_health_bonus: int = 0
    quotes: list[str] = field(default_factory=list)


SPIRIT_ARCHETYPES: dict[str, SpiritArchetype] = {
    "sword_fairy": SpiritArchetype(
        id="sword_fairy",
        name="素衣剑仙子",
        title="太古纯阳剑灵",
        description="一袭素白剑衣迎风飘拂，明眸如霜，由绝世锋芒灵韵凝化而成的清冷仙子。",
        personality="清冷高绝 · 剑心护主",
        default_name="青霜",
        combat_skill_name="青莲断空斩",
        combat_skill_desc="每隔一轮引动天地剑煞斩击敌方，造成真实伤害并破除护甲！",
        skill_type="damage",
        skill_value=50,
        attack_multiplier=1.15,
        quotes=[
            "剑随心动，主人剑锋所指，青霜长剑所向。",
            "九天之上寒风虽冽，有主人温养真元，青霜心念甚安。",
            "方才那一招剑气运转尚有三分滞涩，待闭关之时，青霜愿为主人演练周天剑法。",
            "莫怕那些邪修凶兽，青霜的剑罡定斩一切犯境之敌！",
        ],
    ),
    "thunder_child": SpiritArchetype(
        id="thunder_child",
        name="紫霄雷灵童",
        title="紫霄雷煞正灵",
        description="银发紫眸的小道童，身披紫电雷纹道袍，指尖跳跃着太古天劫雷芒。",
        personality="傲娇好胜 · 雷厉风行",
        default_name="雷霄",
        combat_skill_name="紫霄诛魔雷",
        combat_skill_desc="雷芒贯顶轰杀对手，附带天劫神雷麻痹效果！",
        skill_type="damage",
        skill_value=60,
        attack_multiplier=1.18,
        defense_bonus=10,
        quotes=[
            "哼！算你识货，本灵可是承接九天雷劫而生的天命神灵！",
            "喂，主人，什么时候去劈那几个讨厌的魔头？本座神雷早就饥渴难耐了！",
            "看在你每天按时喂我上品灵石的份上……今天就大发慈悲多替你挡几道劫雷吧！",
            "打架千万别逞强，躲在本座身后，雷法会替你解决一切！",
        ],
    ),
    "mirror_maiden": SpiritArchetype(
        id="mirror_maiden",
        name="玄镜雪姬",
        title="太虚阴阳镜灵",
        description="水蓝色广袖流仙裙，姿容温婉动人，眸如寒潭，镜波流转间可照见万物吉凶。",
        personality="温婉体贴 · 灵照乾坤",
        default_name="雪璃",
        combat_skill_name="玄阴水华镜障",
        combat_skill_desc="修士受创或气血危急时降下镜光护罩，抵御伤害并拂平气血！",
        skill_type="shield",
        skill_value=70,
        defense_bonus=25,
        max_health_bonus=60,
        quotes=[
            "仙途险恶，主人出门在外，雪璃时刻以镜光护住道心灵台。",
            "累了便在洞府歇歇吧，雪璃为你点上宁神清心香。",
            "镜中照出了主人明日的运势呢……紫气升腾，定有福缘降临。",
            "无论面对多可怖的敌人，雪璃都会化身坚不可摧的玄镜，护君周全。",
        ],
    ),
    "cauldron_spirit": SpiritArchetype(
        id="cauldron_spirit",
        name="八卦赤灵童",
        title="造化山海鼎灵",
        description="红袍小仙童，背负火葫芦，浑身散发着太古灵丹与三昧真火的馥郁异香。",
        personality="豪爽灵动 · 丹道奇才",
        default_name="赤火",
        combat_skill_name="三昧纯阳反震",
        combat_skill_desc="浑身燃烧纯阳三昧真火，反弹受创并焚烧敌方气血！",
        skill_type="hybrid",
        skill_value=45,
        defense_bonus=20,
        max_health_bonus=50,
        quotes=[
            "哈哈哈！开炉炼丹找本少爷准没错，三昧真火保准炼出极品天丹！",
            "嗝~ 刚才那颗聚气丹味道真不错，还有没有？再来十颗！",
            "谁敢招惹我主人？看本灵喷他一脸三昧真火，烧他个皮开肉绽！",
            "丹鼎合一，气血绵长，主人只管放开手脚大战三百回合！",
        ],
    ),
}


class ArtifactSpiritEngine:
    @classmethod
    def can_manifest(cls, state: GameState) -> tuple[bool, str]:
        """Check whether current state allows spirit manifestation."""
        bonded = state.bonded_artifact
        if not bonded:
            return False, "尚未祭炼【本命法宝】。需先在法宝谱中认主一件本命法宝。"

        record = state.artifact_refinements.get(bonded, {})
        resonance = int(record.get("resonance", 0))
        if resonance < 30:
            return False, f"与【{bonded}】器心契合度不足（当前 {resonance}/100，需达到 30 以上器灵方能觉醒化形）。"

        return True, ""

    @classmethod
    def manifest(
        cls,
        state: GameState,
        archetype_id: str = "sword_fairy",
        custom_name: str = "",
    ) -> dict[str, Any]:
        """Perform artifact spirit human manifestation."""
        can, reason = cls.can_manifest(state)
        if not can:
            raise ValueError(reason)

        bonded = state.bonded_artifact
        archetype = SPIRIT_ARCHETYPES.get(archetype_id, SPIRIT_ARCHETYPES["sword_fairy"])
        name = custom_name.strip() or archetype.default_name

        spirit_data = {
            "name": name,
            "artifact_name": bonded,
            "archetype_id": archetype.id,
            "archetype_name": archetype.name,
            "title": archetype.title,
            "description": archetype.description,
            "personality": archetype.personality,
            "level": 1,
            "intimacy": 60,
            "exp": 0,
            "is_active": True,
            "combat_skill_name": archetype.combat_skill_name,
            "combat_skill_desc": archetype.combat_skill_desc,
            "skill_value": archetype.skill_value,
            "attack_multiplier": archetype.attack_multiplier,
            "defense_bonus": archetype.defense_bonus,
            "max_health_bonus": archetype.max_health_bonus,
            "dialogue_history": [
                f"灵光化形！伴随着一声清越灵鸣，【{bonded}】器心深处的真灵幻化成人形：‘【{name}】拜见主人！愿与主人神魂相随，斩尽诸敌！’"
            ],
        }

        state.artifact_spirit = spirit_data
        event = f"本命法宝【{bonded}】真灵化形大成！诞出独立人形侍从【{name}】（{archetype.name}）！"
        state.remember(event)
        state.artifact_spirit_history.append(event)

        return {
            "spirit": spirit_data,
            "msg": f"【器灵独立化形】万道瑞彩贯通灵台，【{bonded}】器灵化作【{name}】显化于身旁！",
        }

    @classmethod
    def talk(cls, state: GameState, question: str = "") -> dict[str, Any]:
        """Converse with materialized artifact spirit."""
        spirit = state.artifact_spirit
        if not spirit or not spirit.get("name"):
            raise ValueError("当前尚未有化形器灵。可由【器灵化形】唤醒本命法宝真灵。")

        archetype = SPIRIT_ARCHETYPES.get(spirit.get("archetype_id", "sword_fairy"))
        quotes = archetype.quotes if archetype else [f"主人道心坚毅，{spirit['name']}定生死相随。"]

        # Deterministic or random quote selection
        idx = (state.turn + len(question)) % len(quotes)
        reply = quotes[idx]

        # Intimacy gain
        old_intimacy = spirit.get("intimacy", 60)
        spirit["intimacy"] = min(100, old_intimacy + 2)

        user_text = question.strip() or "器灵近来心境如何？本命温养可觉顺畅？"
        log_entry = f"与器灵【{spirit['name']}】交谈：\n你：“{user_text}”\n{spirit['name']}：“{reply}”（灵犀度 +2）"
        spirit["dialogue_history"].append(log_entry)
        spirit["dialogue_history"] = spirit["dialogue_history"][-15:]

        state.remember(f"与本命器灵【{spirit['name']}】心印交流，默契日深。")

        return {
            "spirit": spirit,
            "user_text": user_text,
            "reply": reply,
            "intimacy": spirit["intimacy"],
            "msg": f"【器灵心声 · {spirit['name']}】\n“{reply}”\n（灵犀默契升至 {spirit['intimacy']}/100）",
        }

    @classmethod
    def feed(cls, state: GameState, item_name: str = "聚气丹") -> dict[str, Any]:
        """Feed pill or material to nurture spirit and level up."""
        spirit = state.artifact_spirit
        if not spirit or not spirit.get("name"):
            raise ValueError("当前尚未有化形器灵。")

        valid_items = {
            "聚气丹": (20, 5),
            "筑基丹": (60, 10),
            "灵石": (1, 1),
            "天材地宝": (100, 20),
            "灵铁": (15, 3),
        }

        item = item_name.strip()
        if item == "灵石":
            if state.player.spirit_stones < 50:
                raise ValueError("灵石不足，喂养需至少 50 灵石。")
            state.player.spirit_stones -= 50
            exp_gain, int_gain = 50, 5
        else:
            if item not in valid_items:
                raise ValueError(f"器灵不喜食用此物。可选喂养：{'、'.join(valid_items.keys())}。")
            if state.player.resources.get(item, 0) < 1:
                raise ValueError(f"乾坤袋中没有【{item}】。")
            state.player.resources[item] -= 1
            if state.player.resources[item] <= 0:
                state.player.resources.pop(item, None)
            exp_gain, int_gain = valid_items[item]

        spirit["exp"] = spirit.get("exp", 0) + exp_gain
        spirit["intimacy"] = min(100, spirit.get("intimacy", 60) + int_gain)

        # Level up check (every 100 exp)
        leveled_up = False
        while spirit["exp"] >= spirit.get("level", 1) * 100 and spirit.get("level", 1) < 10:
            spirit["exp"] -= spirit["level"] * 100
            spirit["level"] += 1
            spirit["skill_value"] += 10
            leveled_up = True

        msg = f"以【{item}】喂养器灵【{spirit['name']}】：灵性经验 +{exp_gain}，灵犀度 +{int_gain}。"
        if leveled_up:
            msg += f" 器灵真身通达，晋升至 【{spirit['level']} 阶】！神通威能大幅强化！"

        state.remember(msg)
        return {
            "spirit": spirit,
            "item": item,
            "exp_gain": exp_gain,
            "intimacy_gain": int_gain,
            "leveled_up": leveled_up,
            "level": spirit["level"],
            "msg": msg,
        }

    @classmethod
    def toggle_active(cls, state: GameState) -> dict[str, Any]:
        """Toggle spirit companion active assistance status."""
        spirit = state.artifact_spirit
        if not spirit:
            raise ValueError("当前没有化形器灵。")
        spirit["is_active"] = not spirit.get("is_active", True)
        status_text = "出战相随" if spirit["is_active"] else "化为原形归位"
        msg = f"已令器灵【{spirit['name']}】{status_text}。"
        state.remember(msg)
        return {"spirit": spirit, "is_active": spirit["is_active"], "msg": msg}

    @classmethod
    def combat_assist(cls, state: GameState, round_num: int) -> dict[str, Any] | None:
        """Trigger artifact spirit combat assistance."""
        spirit = state.artifact_spirit
        if not spirit or not spirit.get("is_active", True):
            return None

        # Triggers on round 1 (opening) and odd rounds (1, 3, 5...)
        if round_num % 2 == 0:
            return None

        skill_name = spirit.get("combat_skill_name", "器灵破空斩")
        val = spirit.get("skill_value", 40)
        arch_id = spirit.get("archetype_id", "sword_fairy")

        combat = state.combat
        if not combat:
            return None

        if arch_id in ("sword_fairy", "thunder_child"):
            # Damage enemy
            combat["enemy_health"] = max(0, int(combat.get("enemy_health", 0)) - val)
            text = f"【本命器灵 · {spirit['name']}】显化飞剑斩出《{skill_name}》！剑芒雷动对敌人造成 {val} 点真实伤害！"
        else:
            # Shield / heal player
            heal = min(state.player.health_max - state.player.health, val)
            state.player.health += heal
            text = f"【本命器灵 · {spirit['name']}】宝光照彻催动《{skill_name}》！降下护灵宝障，回复气血 +{heal}！"

        return {
            "skill_name": skill_name,
            "value": val,
            "text": text,
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Snapshot for UI rendering."""
        bonded = state.bonded_artifact
        resonance = 0
        if bonded:
            resonance = int(state.artifact_refinements.get(bonded, {}).get("resonance", 0))
        can_man, reason = cls.can_manifest(state)

        archetypes_view = []
        for a in SPIRIT_ARCHETYPES.values():
            archetypes_view.append({
                "id": a.id,
                "name": a.name,
                "title": a.title,
                "description": a.description,
                "personality": a.personality,
                "default_name": a.default_name,
                "combat_skill_name": a.combat_skill_name,
                "combat_skill_desc": a.combat_skill_desc,
                "attack_multiplier": a.attack_multiplier,
                "defense_bonus": a.defense_bonus,
                "max_health_bonus": a.max_health_bonus,
            })

        return {
            "bonded_artifact": bonded,
            "resonance": resonance,
            "can_manifest": can_man,
            "manifest_reason": reason,
            "spirit": state.artifact_spirit or None,
            "archetypes": archetypes_view,
            "history": list(state.artifact_spirit_history[-10:]),
        }
