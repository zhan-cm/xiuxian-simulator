from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .dao import DaoEngine
from .progression import ProgressionEngine
from .relationships import RelationshipEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class PartnerBlessing:
    name: str
    partner_name: str
    description: str
    duration_months: int
    attack_multiplier: float = 1.0
    defense_bonus: int = 0
    lifesteal_percent: float = 0.0
    stone_multiplier: float = 1.0
    max_health_bonus: int = 0
    dao_insight_bonus: int = 0
    heart_demon_resist: float = 0.0


PARTNER_BLESSINGS_PRESETS: dict[str, PartnerBlessing] = {
    "顾清玄": PartnerBlessing(
        name="青云剑罡印",
        partner_name="顾清玄",
        description="青云纯阳剑意入体，锋芒外显。战斗攻击穿透提升 20%，附带纯阳剑气伤害。",
        duration_months=6,
        attack_multiplier=1.20,
    ),
    "白凝霜": PartnerBlessing(
        name="玄冥冰魄印",
        partner_name="白凝霜",
        description="极北冰魄护持灵台，万寒不侵。受创减伤 +25 点，气血上限临时提升 30 点。",
        duration_months=6,
        defense_bonus=25,
        max_health_bonus=30,
    ),
    "云栖": PartnerBlessing(
        name="八方通宝印",
        partner_name="云栖",
        description="天机神算福禄齐天。坊市与行商收益提升 20%，外出探索拾得灵石提升 50%。",
        duration_months=6,
        stone_multiplier=1.50,
    ),
    "谢无咎": PartnerBlessing(
        name="修罗杀生印",
        partner_name="谢无咎",
        description="修罗血海战意焚天。全伤提升 25%，造成伤害的 15% 转化为自身气血。",
        duration_months=6,
        attack_multiplier=1.25,
        lifesteal_percent=0.15,
    ),
    "墨尘": PartnerBlessing(
        name="真龙狂骨印",
        partner_name="墨尘",
        description="太古古妖龙脉灌顶。肉身防御与体魄剧增，战斗防御 +30 点。",
        duration_months=6,
        defense_bonus=30,
    ),
    "洛浅浅": PartnerBlessing(
        name="素女妙真印",
        partner_name="洛浅浅",
        description="合欢神妙阴阳和合。神识感知通透，突破心魔概率降低 30%，闭关感悟速度大增。",
        duration_months=6,
        dao_insight_bonus=25,
        heart_demon_resist=0.30,
    ),
}

GENERIC_BLESSING = PartnerBlessing(
    name="太和双清印",
    partner_name="道侣",
    description="太和清气流转周天，身心安宁。全方位攻防提升 10%。",
    duration_months=6,
    attack_multiplier=1.10,
    defense_bonus=15,
)

PARTNER_MESSAGES_PRESETS: dict[str, list[dict[str, Any]]] = {
    "顾清玄": [
        {
            "text": "见字如面。青岳绝巅残雪方融，方才练剑时剑气引来双飞燕雀，不禁想起了道友。这是我在后山洗剑池边采得的【古剑残片】，愿能助你淬炼锋芒。",
            "gift_item": "古剑残片",
            "gift_count": 1,
            "gift_stones": 80,
        },
        {
            "text": "天道悠悠，唯剑与卿不可负。近日仙门大比风起云涌，道友在外历练切记顾全自身，若遇危难，清云剑下定不负卿。",
            "gift_item": "清茶",
            "gift_count": 2,
            "gift_stones": 50,
        },
    ],
    "白凝霜": [
        {
            "text": "北原夜深，极光照耀着千丈玄冰。指尖这枚同心印微微泛温，便知是你传讯而来。雪岭深处冰莲新发，附上一朵【冰莲】，莫要着了火煞之毒。",
            "gift_item": "冰莲",
            "gift_count": 1,
            "gift_stones": 100,
        },
        {
            "text": "万载风雪虽寒，知君心意自暖。若觉世事喧扰疲惫，随时可归极北与我同看万里霜花。",
            "gift_item": "雪晶",
            "gift_count": 2,
            "gift_stones": 60,
        },
    ],
    "云栖": [
        {
            "text": "哎呀！刚在天机阁核完上季度的灵石大账，心印就响了，真是心有灵犀~ 听闻你近日开销甚巨，喏，私库里偷偷给你支了 300 灵石，快收好！",
            "gift_item": "灵石匣",
            "gift_count": 1,
            "gift_stones": 300,
        },
        {
            "text": "九州商路滚滚红尘，但任凭赚尽天下奇珍，也抵不上收到你传音的那一瞬心跳。今晚天机阁后院设宴，不许推脱哦！",
            "gift_item": "甜糕",
            "gift_count": 3,
            "gift_stones": 120,
        },
    ],
    "谢无咎": [
        {
            "text": "哼，本君方才斩了一头四阶血煞凶蛟，周身杀气未褪，你的符印便亮了。算你还有良心！这批凶兽材料与血灵石收下，谁若惹你，本君灭他道统！",
            "gift_item": "妖兽材料",
            "gift_count": 3,
            "gift_stones": 200,
        },
        {
            "text": "仙门那些道貌岸然之徒若敢为难你，休要与他们废话，传信予我，血煞盟战部随你驱使！",
            "gift_item": "烈酒",
            "gift_count": 2,
            "gift_stones": 100,
        },
    ],
    "墨尘": [
        {
            "text": "哈哈哈！道友！我正带着狼群在十万大山抓火凤呢！你这传讯来得正是时候，接着！刚摘下的万年灵果，本少主特意留给你的！",
            "gift_item": "灵果",
            "gift_count": 3,
            "gift_stones": 150,
        },
        {
            "text": "古妖一族的性命，认定了就生生世世绝不反悔！在外面要是累了，随时回妖祖圣窟，我给你烤整头太古荒兽！",
            "gift_item": "烤肉",
            "gift_count": 3,
            "gift_stones": 80,
        },
    ],
    "洛浅浅": [
        {
            "text": "浅浅方才还在月下抚琴想念仙长的怀抱呢……指尖灵佩一烫，心尖儿也跟着颤了呢。这是浅浅特意备下的【聚气丹】，仙长可要快快修至更高境界才好呢~",
            "gift_item": "聚气丹",
            "gift_count": 2,
            "gift_stones": 150,
        },
        {
            "text": "红尘三千丈，合欢铃动相思意。待到重逢之日，仙长可得好好听听浅浅的心跳声，休想甩开我哦？",
            "gift_item": "灵药",
            "gift_count": 2,
            "gift_stones": 100,
        },
    ],
}

CHILD_NAMES = {
    "顾清玄": ("顾慕玄", "顾素心", "纯阳天灵根", "先天纯阳剑胎"),
    "白凝霜": ("白凌霜", "白若雪", "极北玄冰天灵根", "太古九阴玄魄体"),
    "云栖": ("云乘风", "云轻罗", "极品天水双灵根", "天机通灵宝骨"),
    "谢无咎": ("谢九渊", "谢冥月", "修罗暗血天灵根", "太古阿修罗魔体"),
    "墨尘": ("墨苍穹", "墨小蛮", "真龙古妖天灵根", "荒古真龙圣骨"),
    "洛浅浅": ("洛浮生", "洛相思", "玄阴妙法天灵根", "七窍玲珑欢喜体"),
}


class DaoPartnerEngine:
    @classmethod
    def get_preset_blessing(cls, partner_name: str) -> PartnerBlessing:
        return PARTNER_BLESSINGS_PRESETS.get(partner_name, GENERIC_BLESSING)

    @classmethod
    def dual_cultivate(cls, state: GameState, name: str) -> dict[str, Any]:
        """Deep dual cultivation with partner, granting blessing, cultivation, and intimacy."""
        if name not in state.dao_partners:
            raise ValueError(f"【尚未结契】{name}尚不是你的道侣。需好感达到 80 以上方可结契。")

        # Call existing relationship engine calculation
        base_gain, new_affinity = RelationshipEngine.dual_cultivate(state, name)

        # Grant Blessing
        blessing = cls.get_preset_blessing(name)
        state.active_partner_blessings[name] = {
            "name": blessing.name,
            "partner_name": name,
            "description": blessing.description,
            "remaining_months": blessing.duration_months,
            "attack_multiplier": blessing.attack_multiplier,
            "defense_bonus": blessing.defense_bonus,
            "lifesteal_percent": blessing.lifesteal_percent,
            "stone_multiplier": blessing.stone_multiplier,
            "max_health_bonus": blessing.max_health_bonus,
            "dao_insight_bonus": blessing.dao_insight_bonus,
            "heart_demon_resist": blessing.heart_demon_resist,
        }

        # Increment dual cultivation counter
        count = state.partner_dual_counts.get(name, 0) + 1
        state.partner_dual_counts[name] = count

        # Restore health and spirit
        state.player.health = state.player.health_max + blessing.max_health_bonus
        state.player.spirit = state.player.spirit_max

        # Epiphany check
        roll = ProgressionEngine.deterministic_roll(state, f"dual-epiphany:{state.turn}:{name}:{count}")
        epiphany = roll >= 80
        dao_gain = 1 if epiphany else 0
        if dao_gain:
            state.player.dao_points += dao_gain

        msg = f"与道侣【{name}】在合修静室阴阳交泰、性命双修：修为 +{base_gain}，气血灵力全复，凝结法印【{blessing.name}】（持续 {blessing.duration_months} 个月）！"
        if epiphany:
            msg += f" 二人道心通达触碰阴阳玄机，获得悟道点 +{dao_gain}！"

        state.remember(msg)

        return {
            "partner": name,
            "cultivation_gain": base_gain,
            "new_affinity": new_affinity,
            "blessing": blessing.name,
            "blessing_desc": blessing.description,
            "dual_count": count,
            "epiphany": epiphany,
            "dao_gain": dao_gain,
            "msg": msg,
        }

    @classmethod
    def send_message(cls, state: GameState, name: str, user_text: str = "") -> dict[str, Any]:
        """Send soul message to partner and receive heartfelt reply with gift."""
        if name not in state.dao_partners:
            raise ValueError(f"【心印未通】{name}尚未与你结为道侣，无法以本命心印千里传音。")

        templates = PARTNER_MESSAGES_PRESETS.get(name)
        if not templates:
            templates = [
                {
                    "text": f"收到道友传音，心中甚慰。天道虽远，你我同心同行，愿君道体安康。",
                    "gift_item": "灵石匣",
                    "gift_count": 1,
                    "gift_stones": 100,
                }
            ]

        # Pick template deterministically
        idx = (state.turn + len(name)) % len(templates)
        chosen = templates[idx]

        gift_item = chosen.get("gift_item", "")
        gift_count = chosen.get("gift_count", 0)
        gift_stones = chosen.get("gift_stones", 0)

        # Apply gift
        if gift_item and gift_count:
            state.player.resources[gift_item] = state.player.resources.get(gift_item, 0) + gift_count
        if gift_stones:
            state.player.spirit_stones += gift_stones

        record = {
            "turn": state.turn,
            "partner": name,
            "user_text": user_text or "道友近日安好？心印微温，甚是念卿。",
            "reply": chosen["text"],
            "gift_item": gift_item,
            "gift_count": gift_count,
            "gift_stones": gift_stones,
        }

        state.partner_message_history.append(record)
        state.partner_message_history = state.partner_message_history[-20:]

        gift_desc = []
        if gift_item and gift_count:
            gift_desc.append(f"【{gift_item}】×{gift_count}")
        if gift_stones:
            gift_desc.append(f"灵石 +{gift_stones}")
        gift_summary = ("，附赠随身回礼：" + "、".join(gift_desc)) if gift_desc else ""

        event = f"向道侣【{name}】心印传音。收到深情回书{gift_summary}。"
        state.remember(event)

        return {
            "partner": name,
            "user_text": record["user_text"],
            "reply": chosen["text"],
            "gift_item": gift_item,
            "gift_count": gift_count,
            "gift_stones": gift_stones,
            "msg": f"【{name}心印传音回响】\n“{chosen['text']}”\n" + (f"获得回礼：{'、'.join(gift_desc)}" if gift_desc else ""),
        }

    @classmethod
    def conceive_child(cls, state: GameState, name: str) -> dict[str, Any]:
        """Conceive a gifted child with partner when affinity and dual count are sufficient."""
        if name not in state.dao_partners:
            raise ValueError(f"【尚未结契】{name}尚不是你的道侣。")

        affinity = RelationshipEngine.affinity(state, name)
        if affinity < 100:
            raise ValueError(f"【心意未达】孕育仙胎需彼此生死相许（好感达 100 点）；当前与{name}好感为 {affinity}。")

        dual_count = state.partner_dual_counts.get(name, 0)
        if dual_count < 3:
            raise ValueError(f"【阴阳合道不足】孕育仙胎需二人阴阳互济合修至少 3 次；当前已合修 {dual_count} 次。")

        # Existing child with this partner check (max 2 per partner for balance)
        existing = [c for c in state.partner_children if c.get("partner") == name]
        if len(existing) >= 2:
            raise ValueError(f"你与{name}已育有二位仙家子嗣，天道造化已有圆满。")

        # Generate child traits
        naming = CHILD_NAMES.get(name, ("仙林儿", "仙灵儿", "极品五行灵根", "先天混元道骨"))
        is_female = len(existing) % 2 == 1
        child_name = naming[1] if is_female else naming[0]
        spiritual_root = naming[2]
        constitution = naming[3]

        child_id = f"child-{name}-{state.turn}"
        child_data = {
            "id": child_id,
            "name": child_name,
            "gender": "女" if is_female else "男",
            "partner": name,
            "parent_player": state.player.name,
            "birth_year": state.calendar_year,
            "birth_turn": state.turn,
            "age": 0,
            "stage": "凡胎·襁褓",
            "spiritual_root": spiritual_root,
            "constitution": constitution,
            "realm": "凡胎·初生",
            "cultivation": 0,
            "adventure_log": [],
        }

        state.partner_children.append(child_data)
        event = f"天降祥瑞，紫气东来！你与道侣【{name}】喜得麟儿【{child_name}】（{child_data['gender']} · {spiritual_root} · {constitution}）！"
        state.remember(event)

        return {
            "child": child_data,
            "msg": event,
        }

    @classmethod
    def grow_children(cls, state: GameState, months: int = 1) -> list[str]:
        """Advance children's growth every turn / months."""
        events: list[str] = []
        for child in state.partner_children:
            old_age = int(child.get("age", 0))
            # 1 year every 12 months
            child["age"] = (state.calendar_year - int(child.get("birth_year", state.calendar_year)))
            new_age = int(child["age"])

            # Evolve stages based on age
            if new_age < 4:
                child["stage"] = "凡胎·襁褓"
                child["realm"] = "凡胎·初生"
            elif new_age < 12:
                child["stage"] = "凡胎·童蒙"
                child["realm"] = "通灵引气"
            elif new_age < 16:
                child["stage"] = "束发修真"
                child["realm"] = f"练气·{min(9, new_age - 7)}层"
            else:
                child["stage"] = "筑基成道"
                child["realm"] = "筑基·初期"

            # When child turns 16, achieves筑基 and brings gift
            if old_age < 16 and new_age >= 16:
                child_name = child["name"]
                partner = child.get("partner", "")
                gift_stone = 200
                state.player.spirit_stones += gift_stone
                state.player.resources["天材地宝"] = state.player.resources.get("天材地宝", 0) + 1
                ev = f"仙家子嗣【{child_name}】（与{partner}所育）已年满十六，筑基大成！外出历练寻得【天材地宝】×1 与灵石 +{gift_stone} 孝敬双亲！"
                events.append(ev)
                state.remember(ev)

        return events

    @classmethod
    def tick_blessings(cls, state: GameState, months: int = 1) -> None:
        """Decrement blessing duration in GameState."""
        expired: list[str] = []
        for partner_name, blessing in list(state.active_partner_blessings.items()):
            blessing["remaining_months"] = blessing.get("remaining_months", 1) - months
            if blessing["remaining_months"] <= 0:
                expired.append(partner_name)

        for p in expired:
            b_name = state.active_partner_blessings.pop(p, {}).get("name", "道侣法印")
            state.remember(f"与【{p}】双修之【{b_name}】灵蕴消解，法印威能归于天地。")

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Snapshot for UI rendering."""
        partners_view = []
        for name in state.dao_partners:
            aff = RelationshipEngine.affinity(state, name)
            dual_count = state.partner_dual_counts.get(name, 0)
            blessing_info = state.active_partner_blessings.get(name)
            preset = cls.get_preset_blessing(name)
            can_conceive = aff >= 100 and dual_count >= 3 and len([c for c in state.partner_children if c.get("partner") == name]) < 2
            partners_view.append({
                "name": name,
                "affinity": aff,
                "dual_count": dual_count,
                "preset_blessing": {
                    "name": preset.name,
                    "description": preset.description,
                    "duration_months": preset.duration_months,
                    "attack_multiplier": preset.attack_multiplier,
                    "defense_bonus": preset.defense_bonus,
                    "lifesteal_percent": preset.lifesteal_percent,
                    "stone_multiplier": preset.stone_multiplier,
                },
                "active_blessing": blessing_info,
                "can_conceive": can_conceive,
            })

        return {
            "has_partners": len(state.dao_partners) > 0,
            "partners": partners_view,
            "children": list(state.partner_children),
            "messages": list(state.partner_message_history[-10:]),
            "active_blessings": dict(state.active_partner_blessings),
        }
