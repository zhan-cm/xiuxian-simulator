from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class SectTreasure:
    id: str
    name: str
    cost_stones: int
    category: str
    reputation_req: int
    count: int
    summary: str


@dataclass(frozen=True, slots=True)
class SectBounty:
    id: str
    title: str
    risk: str
    chance_base: int
    reward_stones: int
    reward_reputation: int
    reward_items: dict[str, int]
    summary: str


@dataclass(frozen=True, slots=True)
class SectGateProfile:
    name: str
    province: str
    mark: str
    doctrine: str
    motto: str
    description: str
    welcome_gift: str
    welcome_gift_count: int
    treasures: tuple[SectTreasure, ...]
    bounties: tuple[SectBounty, ...]


SECT_PROFILES: dict[str, SectGateProfile] = {
    "青云宗": SectGateProfile(
        name="青云宗",
        province="东洲青岳",
        mark="云",
        doctrine="正道名门 · 剑道通玄",
        motto="清正持剑，守望东洲",
        description="雄踞东洲青岳群峰之巅，云蒸霞蔚，剑阁高耸。门风端严，历代护持凡尘安宁。",
        welcome_gift="青云剑穗",
        welcome_gift_count=1,
        treasures=(
            SectTreasure("qy-pill", "聚气丹", 180, "丹药", 10, 3, "青云灵药圃秘炼聚气丹，温润纯和。"),
            SectTreasure("qy-sword", "青锋剑", 350, "法宝", 30, 1, "青云洗剑池淬砺上品法剑，锋锐不折。"),
            SectTreasure("qy-pendant", "青云佩", 600, "奇珍", 60, 1, "聚青岳千年浩气，可宁心避劫。"),
        ),
        bounties=(
            SectBounty("qy-bounty-1", "清剿青岳外围妖狼", "普通", 75, 200, 10, {"妖兽材料": 2}, "扫荡潜入青岳灵脉边缘的嗜血妖狼群。"),
            SectBounty("qy-bounty-2", "诛灭东洲魔道逆徒", "凶险", 62, 450, 25, {"魔道余烬": 1, "灵石": 100}, "斩杀残害乡里的魔修逆徒，取回被掠宗门法册。"),
        ),
    ),
    "丹霞谷": SectGateProfile(
        name="丹霞谷",
        province="南荒丹霞",
        mark="丹",
        doctrine="万火归元 · 济世丹道",
        motto="丹火养生，济世求真",
        description="深藏南荒十万群山之中，地肺真火万载不绝。百草芬芳，天下灵药多出其门。",
        welcome_gift="回春灵泉",
        welcome_gift_count=2,
        treasures=(
            SectTreasure("dx-herb", "灵药", 120, "材料", 10, 4, "丹霞药圃肥土灌溉的高品灵草。"),
            SectTreasure("dx-healing", "疗伤丹", 220, "丹药", 20, 2, "深谙药理之长老亲手开炉炼制，回春奇效。"),
            SectTreasure("dx-purify", "洗髓丹", 800, "丹药", 70, 1, "伐毛洗髓脱胎换骨之无上圣丹。"),
        ),
        bounties=(
            SectBounty("dx-bounty-1", "采撷绝壁龙血芝", "稳健", 80, 220, 12, {"灵药": 3}, "前往赤霞万丈绝壁采摘悬生灵芝。"),
            SectBounty("dx-bounty-2", "护送百草灵舟", "凶险", 65, 500, 25, {"灵药": 5, "疗伤丹": 1}, "护卫载满各洲紧缺丹药的飞舟穿过毒雾瘴林。"),
        ),
    ),
    "玄剑门": SectGateProfile(
        name="玄剑门",
        province="西漠千峰",
        mark="剑",
        doctrine="唯剑极道 · 生死试锋",
        motto="以战磨剑，锋芒证道",
        description="屹立西漠千仞绝壁，终年剑罡呼啸。门人崇尚极意杀伐，门下弟子皆以剑为命。",
        welcome_gift="淬剑灵砂",
        welcome_gift_count=2,
        treasures=(
            SectTreasure("xj-iron", "灵铁", 160, "材料", 10, 5, "地火万锻玄铁，坚固异凡。"),
            SectTreasure("xj-blade", "玄铁剑", 400, "法宝", 35, 1, "玄剑门真传弟子制式重刃，煞气凝重。"),
            SectTreasure("xj-stone", "太玄剑石", 750, "奇珍", 75, 1, "上古剑修留痕的顽石，暗蕴通天剑意。"),
        ),
        bounties=(
            SectBounty("xj-bounty-1", "斩杀荒漠赤尾蝎王", "普通", 70, 260, 15, {"妖兽材料": 3}, "斩杀荒漠中肆虐商路的毒蝎巨妖。"),
            SectBounty("xj-bounty-2", "夺取天外陨铁石", "凶险", 60, 550, 30, {"灵铁": 6}, "深入西漠绝境古裂谷，击退争夺者夺取陨铁。"),
        ),
    ),
    "合欢宗": SectGateProfile(
        name="合欢宗",
        province="中州万象",
        mark="欢",
        doctrine="阴阳和合 · 极乐心印",
        motto="天地同情，落英飞花",
        description="中州桃源秘境之中，桃花纷坠，丝竹悦耳。门人修习阴阳和合妙术，眼波流转勾魂摄魄。",
        welcome_gift="合欢香囊",
        welcome_gift_count=1,
        treasures=(
            SectTreasure("hh-wine", "桃花醉", 150, "灵物", 10, 2, "百年灵桃古树花蕊酿制，解百愁增好感。"),
            SectTreasure("hh-robe", "护身法袍", 380, "法宝", 30, 1, "天蚕冰丝与七彩云霞所织，轻盈无匹。"),
            SectTreasure("hh-pendant", "相思引", 680, "奇珍", 65, 1, "情丝千缠百转之宝，佩之可护神魂不坠。"),
        ),
        bounties=(
            SectBounty("hh-bounty-1", "搜集千年落英凝露", "稳健", 82, 200, 12, {"灵药": 2}, "清晨在仙谷采摘带有灵气的桃花朝露。"),
            SectBounty("hh-bounty-2", "抚平中州情海孽缘", "凶险", 66, 480, 24, {"灵石": 200}, "化解名门弟子与魔道修士的生死死仇纠葛。"),
        ),
    ),
    "古妖山": SectGateProfile(
        name="古妖山",
        province="十万祖山",
        mark="妖",
        doctrine="蛮荒血脉 · 龙骨通天",
        motto="百兽为宗，万妖独尊",
        description="隐于崇山密林尽头，万峰盘虬，群妖啸月。妖修天生肉身强横，崇尚强者为尊之蛮荒法则。",
        welcome_gift="蛮荒兽骨",
        welcome_gift_count=2,
        treasures=(
            SectTreasure("gy-bone", "妖兽材料", 150, "材料", 10, 4, "大荒蛮兽坚韧骨牙，为炼器上选。"),
            SectTreasure("gy-blood", "万妖真血", 450, "奇珍", 40, 1, "淬炼肉身皮膜之无上灵液，力能拔山。"),
            SectTreasure("gy-scale", "苍龙逆鳞", 850, "法宝", 80, 1, "相传上古龙族遗留之厚重鳞片，刀枪不入。"),
        ),
        bounties=(
            SectBounty("gy-bounty-1", "平息莽荒暴动幼兽", "稳健", 78, 240, 14, {"妖兽材料": 2}, "安抚因灵气躁动而狂怒的大荒灵兽幼崽。"),
            SectBounty("gy-bounty-2", "猎杀千丈深谷虺龙", "凶险", 58, 600, 35, {"妖兽材料": 5, "灵铁": 4}, "深入祖山毒瘴深渊，击杀为祸一方的恶蛟。"),
        ),
    ),
    "血魔宗": SectGateProfile(
        name="血魔宗",
        province="北原雪岭",
        mark="煞",
        doctrine="血煞九幽 · 杀伐无量",
        motto="顺我者生，逆我者戮",
        description="坐落北原极寒深渊绝壁，血海翻浪，魔雾横空。信奉杀伐掠夺，门人冷酷绝情、嗜血如狂。",
        welcome_gift="血煞幽晶",
        welcome_gift_count=1,
        treasures=(
            SectTreasure("xm-shard", "煞气结晶", 180, "材料", 10, 3, "万载血池凝结之阴煞奇石。"),
            SectTreasure("xm-pill", "化血丹", 380, "丹药", 35, 1, "燃血爆发暴击之霸道魔丹，短时实力暴涨。"),
            SectTreasure("xm-orb", "九幽嗜血珠", 780, "法宝", 75, 1, "吸食天地煞气凝聚而成的杀伐重宝。"),
        ),
        bounties=(
            SectBounty("xm-bounty-1", "清剿雪原白骨魔窟", "普通", 72, 280, 16, {"煞气结晶": 2}, "扫清潜伏在雪山暗穴中的失控骨魔。"),
            SectBounty("xm-bounty-2", "截杀魔门叛逃使者", "凶险", 60, 520, 30, {"化血丹": 1, "灵石": 150}, "追猎携带门派血经逃亡的叛徒执事。"),
        ),
    ),
}


class SectVisitEngine:
    GIFT_COST_STONES = 50

    @classmethod
    def get_profile(cls, sect_name: str) -> SectGateProfile:
        profile = SECT_PROFILES.get(sect_name)
        if not profile:
            raise ValueError(f"未知宗门：{sect_name}")
        return profile

    @classmethod
    def visit(cls, state: GameState, sect_name: str) -> dict[str, Any]:
        """Player pays formal visit to a sect mountain gate."""
        profile = cls.get_profile(sect_name)
        player = state.player
        if player.spirit_stones < cls.GIFT_COST_STONES:
            raise ValueError(f"拜山递帖需备好灵石礼物（{cls.GIFT_COST_STONES} 灵石），当前仅有 {player.spirit_stones}。")

        player.spirit_stones -= cls.GIFT_COST_STONES

        # Success chance based on charisma, comprehension and reputation
        chance = max(25, min(95, 55 + player.comprehension + player.spirit_sense // 2 + player.reputation // 5))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-visit:{sect_name}:{state.turn}")
        success = roll <= chance

        rep_gain = 8 if success else 2
        cult_gain = max(2, player.realm_index * 2) if success else 1
        player.reputation += rep_gain
        player.cultivation += cult_gain

        gift_awarded = False
        if success and profile.welcome_gift:
            player.resources[profile.welcome_gift] = (
                player.resources.get(profile.welcome_gift, 0) + profile.welcome_gift_count
            )
            gift_awarded = True

        state.remember(
            f"登门拜访{sect_name}：{'知客长老欣然接见并论道' if success else '守山弟子礼貌奉还金帖'}，声望 +{rep_gain}，修为 +{cult_gain}"
        )

        return {
            "sect": sect_name,
            "success": success,
            "roll": roll,
            "chance": chance,
            "reputation_gain": rep_gain,
            "cultivation_gain": cult_gain,
            "gift": profile.welcome_gift if gift_awarded else "",
            "gift_count": profile.welcome_gift_count if gift_awarded else 0,
        }

    @classmethod
    def acquire_treasure(cls, state: GameState, sect_name: str, treasure_id: str) -> dict[str, Any]:
        """Player requests / buys treasure from sect mountain gate."""
        profile = cls.get_profile(sect_name)
        treasure = next((t for t in profile.treasures if t.id == treasure_id), None)
        if not treasure:
            raise ValueError(f"在{sect_name}找不到该宝物。")

        player = state.player
        if player.spirit_stones < treasure.cost_stones:
            raise ValueError(f"灵石不足：需 {treasure.cost_stones} 灵石，当前仅有 {player.spirit_stones}。")
        if player.reputation < treasure.reputation_req:
            raise ValueError(
                f"在修仙界声望不足以求得该秘宝：需声望 {treasure.reputation_req}，当前为 {player.reputation}。"
            )

        player.spirit_stones -= treasure.cost_stones
        player.resources[treasure.name] = player.resources.get(treasure.name, 0) + treasure.count

        state.remember(f"在{sect_name}藏宝阁求得{treasure.name}×{treasure.count}，消耗灵石 {treasure.cost_stones}")

        return {
            "sect": sect_name,
            "treasure": treasure.name,
            "count": treasure.count,
            "cost": treasure.cost_stones,
        }

    @classmethod
    def spar_arena(cls, state: GameState) -> dict[str, Any]:
        """Player spars on sect arena."""
        # Arena logic
        pass

    @classmethod
    def spar(cls, state: GameState, sect_name: str) -> dict[str, Any]:
        """Player enters sect martial arts arena for a friendly sparring match."""
        profile = cls.get_profile(sect_name)
        player = state.player

        # Sparring chance based on combat ability, realm and attributes
        chance = max(20, min(92, 45 + player.realm_index * 10 + player.stage_index * 4 + player.speed // 2 + player.comprehension // 2))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-spar:{sect_name}:{state.turn}")
        success = roll <= chance

        reward_stones = 150 + player.realm_index * 50 if success else 30
        rep_gain = 6 if success else 1
        player.spirit_stones += reward_stones
        player.reputation += rep_gain

        state.remember(
            f"在{sect_name}山门演武台比试：{'技压群雄获胜' if success else '点到为止惜败'}，获灵石 +{reward_stones}，声望 +{rep_gain}"
        )

        return {
            "sect": sect_name,
            "success": success,
            "roll": roll,
            "chance": chance,
            "reward_stones": reward_stones,
            "reputation_gain": rep_gain,
        }

    @classmethod
    def take_bounty(cls, state: GameState, sect_name: str, bounty_id: str) -> dict[str, Any]:
        """Player undertakes an external affairs bounty for a sect."""
        profile = cls.get_profile(sect_name)
        bounty = next((b for b in profile.bounties if b.id == bounty_id), None)
        if not bounty:
            raise ValueError(f"找不到该宗门悬赏：{bounty_id}")

        player = state.player
        chance = max(20, min(95, bounty.chance_base + player.realm_index * 8 + player.speed // 2))
        roll = ProgressionEngine.deterministic_roll(state, f"sect-bounty:{bounty_id}:{state.turn}")
        success = roll <= chance

        if success:
            player.spirit_stones += bounty.reward_stones
            player.reputation += bounty.reward_reputation
            for item, count in bounty.reward_items.items():
                player.resources[item] = player.resources.get(item, 0) + count
            reward_desc = f"灵石 +{bounty.reward_stones}，声望 +{bounty.reward_reputation}"
            state.remember(f"完成{sect_name}外务委托【{bounty.title}】：{reward_desc}")
        else:
            player.reputation = max(0, player.reputation - 2)
            player.health = max(1, player.health - 20)
            state.remember(f"执行{sect_name}外务委托【{bounty.title}】未果，气血轻微受损。")

        return {
            "sect": sect_name,
            "title": bounty.title,
            "success": success,
            "roll": roll,
            "chance": chance,
            "reward_stones": bounty.reward_stones if success else 0,
            "reward_reputation": bounty.reward_reputation if success else 0,
            "reward_items": dict(bounty.reward_items) if success else {},
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Returns structured data for all Kyushu sects."""
        gates = []
        player = state.player
        for name, profile in SECT_PROFILES.items():
            treasures_view = []
            for t in profile.treasures:
                affordable = player.spirit_stones >= t.cost_stones and player.reputation >= t.reputation_req
                reason = ""
                if player.spirit_stones < t.cost_stones:
                    reason = f"灵石不足（需 {t.cost_stones}）"
                elif player.reputation < t.reputation_req:
                    reason = f"声望不足（需 {t.reputation_req}）"

                treasures_view.append(
                    {
                        "id": t.id,
                        "name": t.name,
                        "cost_stones": t.cost_stones,
                        "category": t.category,
                        "reputation_req": t.reputation_req,
                        "count": t.count,
                        "summary": t.summary,
                        "available": affordable,
                        "disabled_reason": reason,
                        "action": f"求丹借宝 {name} {t.id}",
                    }
                )

            bounties_view = []
            for b in profile.bounties:
                chance = max(20, min(95, b.chance_base + player.realm_index * 8 + player.speed // 2))
                bounties_view.append(
                    {
                        "id": b.id,
                        "title": b.title,
                        "risk": b.risk,
                        "chance": chance,
                        "reward_stones": b.reward_stones,
                        "reward_reputation": b.reward_reputation,
                        "reward_items": dict(b.reward_items),
                        "summary": b.summary,
                        "action": f"山门历练 {name} {b.id}",
                    }
                )

            can_visit = player.spirit_stones >= cls.GIFT_COST_STONES
            spar_chance = max(20, min(92, 45 + player.realm_index * 10 + player.stage_index * 4 + player.speed // 2 + player.comprehension // 2))

            gates.append(
                {
                    "name": name,
                    "province": profile.province,
                    "mark": profile.mark,
                    "doctrine": profile.doctrine,
                    "motto": profile.motto,
                    "description": profile.description,
                    "welcome_gift": profile.welcome_gift,
                    "welcome_gift_count": profile.welcome_gift_count,
                    "can_visit": can_visit,
                    "visit_action": f"拜山 {name}",
                    "spar_chance": spar_chance,
                    "spar_action": f"山门演武 {name}",
                    "treasures": treasures_view,
                    "bounties": bounties_view,
                }
            )

        return {
            "gift_cost": cls.GIFT_COST_STONES,
            "gates": gates,
            "player_sect": player.sect,
            "player_stones": player.spirit_stones,
            "player_reputation": player.reputation,
        }
