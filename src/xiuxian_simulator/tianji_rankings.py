from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .progression import ProgressionEngine, REALMS, STAGES
from .state import GameState


@dataclass(frozen=True, slots=True)
class ProdigyTemplate:
    id: str
    name: str
    dao_name: str
    sect: str
    province: str
    realm_index: int
    stage_index: int
    base_power: int
    title: str
    specialty: str
    description: str
    is_npc: bool = False
    npc_name: str = ""
    personality: str = "沉稳"


PRODIGY_TEMPLATES: list[ProdigyTemplate] = [
    ProdigyTemplate(
        id="prodigy-gu-qingxuan",
        name="顾清玄",
        dao_name="青云剑子",
        sect="青云宗",
        province="东洲",
        realm_index=3,
        stage_index=2,
        base_power=1480,
        title="青岳第一剑 · 纯阳通玄",
        specialty="太乙分光剑阵",
        description="青云宗掌门关门弟子，十岁纳气，二十铸就天道金丹，性情温润却剑意逼人。",
        is_npc=True,
        npc_name="顾清玄",
        personality="温润守礼",
    ),
    ProdigyTemplate(
        id="prodigy-xie-wujiu",
        name="谢无咎",
        dao_name="血幽冥",
        sect="血魔宗",
        province="北原",
        realm_index=3,
        stage_index=2,
        base_power=1460,
        title="十方魔君 · 杀伐修罗",
        specialty="九幽化血真煞",
        description="血魔宗少主，眉心天生暗红魔纹，行事狠戾果决，视天下伪正道如刍狗。",
        is_npc=True,
        npc_name="谢无咎",
        personality="孤绝狂傲",
    ),
    ProdigyTemplate(
        id="prodigy-bai-ningshuang",
        name="白凝霜",
        dao_name="玄冰仙子",
        sect="雪族古脉",
        province="北原",
        realm_index=3,
        stage_index=1,
        base_power=1410,
        title="雪岭玄女 · 霜华寂照",
        specialty="九天玄冰封魄神光",
        description="极北冰渊雪族天生圣女，三千白发若寒江凝霜，不涉凡尘因果，心如止水。",
        is_npc=True,
        npc_name="白凝霜",
        personality="清冷出尘",
    ),
    ProdigyTemplate(
        id="prodigy-mo-chen",
        name="墨尘",
        dao_name="黑龙少主",
        sect="古妖山",
        province="南疆",
        realm_index=3,
        stage_index=1,
        base_power=1390,
        title="万妖天尊 · 荒古龙裔",
        specialty="九霄龙吟崩天劲",
        description="古妖山万妖殿少主，身负太古黑龙残血，桀骜不驯，拳劲可断岳裂石。",
        is_npc=True,
        npc_name="墨尘",
        personality="桀骜勇武",
    ),
    ProdigyTemplate(
        id="prodigy-luo-qianqian",
        name="洛浅浅",
        dao_name="天魅仙子",
        sect="合欢宗",
        province="中州",
        realm_index=3,
        stage_index=0,
        base_power=1320,
        title="百花迷魂 · 天魔妙姝",
        specialty="颠倒阴阳幻魔遁",
        description="合欢宗妙姝，身法若落花乘风，笑靥惑人道心，实则心智玲珑谋定后动。",
        is_npc=True,
        npc_name="洛浅浅",
        personality="娇媚慧黠",
    ),
    ProdigyTemplate(
        id="prodigy-ye-linfeng",
        name="叶临风",
        dao_name="纯阳丹尊",
        sect="丹霞谷",
        province="南疆",
        realm_index=2,
        stage_index=3,
        base_power=1180,
        title="青帝传人 · 悬壶济世",
        specialty="三味真火控灵诀",
        description="丹霞谷大弟子，精研上古丹经，一手灵火出神入化，备受各方敬重。",
        personality="严谨端方",
    ),
    ProdigyTemplate(
        id="prodigy-chu-kuangtu",
        name="楚狂徒",
        dao_name="断江客",
        sect="玄剑门",
        province="西漠",
        realm_index=2,
        stage_index=3,
        base_power=1160,
        title="西漠狂剑 · 万剑独行",
        specialty="大荒破山七绝斩",
        description="玄剑门第一狂人，常背一柄门板阔剑横渡流沙死海，嗜战如命。",
        personality="豪迈好战",
    ),
    ProdigyTemplate(
        id="prodigy-zhuge-tiangong",
        name="诸葛天工",
        dao_name="百炼生",
        sect="天机阁",
        province="中州",
        realm_index=2,
        stage_index=2,
        base_power=1080,
        title="机巧无双 · 天衍神算",
        specialty="九宫遁甲傀儡阵",
        description="天机阁精修奇门遁甲的机关奇才，常随身携带三具金丹级重甲玄铁傀儡。",
        personality="精明机巧",
    ),
    ProdigyTemplate(
        id="prodigy-miaoyin",
        name="妙音仙子",
        dao_name="素心琴客",
        sect="云梦仙宗",
        province="云州",
        realm_index=2,
        stage_index=1,
        base_power=980,
        title="天籁摄魂 · 浮生幻曲",
        specialty="太古清心普善咒",
        description="隐世云梦蜃泽之琴修，玉指拨弦可定凶兽神魂，音律通玄入化。",
        personality="恬淡静美",
    ),
    ProdigyTemplate(
        id="prodigy-situ-you",
        name="司徒幽",
        dao_name="白骨郎君",
        sect="幽冥散修",
        province="幽州",
        realm_index=2,
        stage_index=0,
        base_power=890,
        title="冥河游魂 · 幽魄夺命",
        specialty="白骨煞魔手",
        description="常年徘徊于幽州冥河之畔的苦修散人，精研尸傀鬼道，行踪莫测。",
        personality="阴鸷冷漠",
    ),
    ProdigyTemplate(
        id="prodigy-lei-zhenzi",
        name="雷烈",
        dao_name="雷霆真子",
        sect="九天雷极门",
        province="雷州",
        realm_index=1,
        stage_index=3,
        base_power=780,
        title="引雷铸骨 · 纯阳霸躯",
        specialty="紫霄引雷霸体",
        description="肉身生来亲近雷电，曾在雷州雷池中沐浴天雷百日不死，道基极为坚固。",
        personality="粗豪直爽",
    ),
    ProdigyTemplate(
        id="prodigy-penglai-ke",
        name="柳青漪",
        dao_name="沧海钓客",
        sect="蓬莱仙阁",
        province="瀛洲",
        realm_index=1,
        stage_index=2,
        base_power=690,
        title="碧波凌虚 · 乘鸾钓鳌",
        specialty="惊涛碧波掌",
        description="海外瀛洲三山修士，一柄钓竿泛舟惊涛骇浪之中，灵动非凡。",
        personality="随性豁达",
    ),
    ProdigyTemplate(
        id="prodigy-qingyun-wa门",
        name="苏明远",
        dao_name="青岳客",
        sect="青云宗",
        province="东洲",
        realm_index=1,
        stage_index=1,
        base_power=580,
        title="青岳后起 · 疾风快剑",
        specialty="回风拂柳剑",
        description="青云宗内门精英，剑招轻灵迅疾，为人谦逊勤勉。",
        personality="沉着坚毅",
    ),
    ProdigyTemplate(
        id="prodigy-sanxiu-tie",
        name="铁狂徒",
        dao_name="覆地手",
        sect="东洲散修盟",
        province="东洲",
        realm_index=1,
        stage_index=0,
        base_power=490,
        title="草莽豪侠 · 重拳无锋",
        specialty="开山崩岩拳",
        description="起于市井凡尘的散修壮汉，仗义疏财，拳风刚猛。",
        personality="热忱率真",
    ),
]

OVERLORD_RANKINGS: list[dict[str, Any]] = [
    {
        "rank": 1,
        "name": "青云子",
        "dao_name": "天阳真人",
        "sect": "青云宗",
        "realm": "化神·圆满",
        "power": 9800,
        "title": "九州正道之首 · 万剑至尊",
        "legend": "一柄青天古剑威震神州八百载，曾一剑平定东海妖海狂潮。",
    },
    {
        "rank": 2,
        "name": "血煞魔尊",
        "dao_name": "厉九幽",
        "sect": "血魔宗",
        "realm": "化神·后期",
        "power": 9650,
        "title": "九幽极凶 · 血海巨擘",
        "legend": "执掌北原冥煞血泉，杀伐成道，令北原诸族闻风丧胆。",
    },
    {
        "rank": 3,
        "name": "天狐老祖",
        "dao_name": "白素真",
        "sect": "古妖山",
        "realm": "化神·后期",
        "power": 9400,
        "title": "十万大山万妖圣祖",
        "legend": "九尾天狐化形大能，寿元逾三千载，上古妖族底蕴深不可测。",
    },
    {
        "rank": 4,
        "name": "百草天仙",
        "dao_name": "药尘子",
        "sect": "丹霞谷",
        "realm": "化神·中期",
        "power": 9150,
        "title": "通天丹圣 · 纯阳生机",
        "legend": "曾开炉炼制九转还魂天丹，引来三劫雷云，救治天下修士无数。",
    },
    {
        "rank": 5,
        "name": "太玄剑主",
        "dao_name": "李独孤",
        "sect": "玄剑门",
        "realm": "化神·中期",
        "power": 9100,
        "title": "西漠剑圣 · 破虚求道",
        "legend": "独创万剑归虚古谱，剑意锋芒撕裂虚空，纵横大漠无敌手。",
    },
    {
        "rank": 6,
        "name": "天极道君",
        "dao_name": "诸葛玄",
        "sect": "天机阁",
        "realm": "化神·初期",
        "power": 8900,
        "title": "天机百晓 · 算尽因果",
        "legend": "居天机通天浮空道阁，执掌天机阴阳鉴，知晓三千界古往今来。",
    },
]

SECT_PRESTIGE_RANKINGS: list[dict[str, Any]] = [
    {
        "rank": 1,
        "name": "青云宗",
        "province": "东洲青岳",
        "doctrine": "清正持剑 · 守望正道",
        "prestige": 9850,
        "trend": "鼎盛",
        "leader": "青云子",
    },
    {
        "rank": 2,
        "name": "血魔宗",
        "province": "北原雪岭",
        "doctrine": "杀伐无量 · 唯我独尊",
        "prestige": 9320,
        "trend": "凶威",
        "leader": "厉九幽",
    },
    {
        "rank": 3,
        "name": "天机阁",
        "province": "中州天阙",
        "doctrine": "天道自然 · 勘定乾坤",
        "prestige": 9100,
        "trend": "超然",
        "leader": "诸葛玄",
    },
    {
        "rank": 4,
        "name": "古妖山",
        "province": "南疆十万祖山",
        "doctrine": "蛮荒血脉 · 弱肉强食",
        "prestige": 8800,
        "trend": "稳固",
        "leader": "白素真",
    },
    {
        "rank": 5,
        "name": "丹霞谷",
        "province": "南疆丹霞峰",
        "doctrine": "济世丹道 · 仁者长生",
        "prestige": 8650,
        "trend": "祥和",
        "leader": "药尘子",
    },
    {
        "rank": 6,
        "name": "玄剑门",
        "province": "西漠流沙千峰",
        "doctrine": "千锤百炼 · 生死试锋",
        "prestige": 8400,
        "trend": "昂扬",
        "leader": "李独孤",
    },
]

TIANJI_TREASURES: list[dict[str, Any]] = [
    {
        "id": "tj-amulet",
        "name": "天机避劫符",
        "category": "道门神符",
        "token_cost": 30,
        "effect": "突破大境界时佩戴，可定心抚煞，降低天劫走火入魔几率",
        "summary": "天机阁长老以极品紫霄辰砂绘制的天道避灾灵符。",
    },
    {
        "id": "tj-pill",
        "name": "太虚蕴灵丹",
        "category": "玄品丹药",
        "token_cost": 45,
        "effect": "服下后洗涤体内经络灵池，即刻增长 150 点纯正修为",
        "summary": "天机阁百草药圃以太虚清气凝炼的上乘增功灵丹。",
    },
    {
        "id": "tj-iron",
        "name": "天工万象铁",
        "category": "炼器奇材",
        "token_cost": 40,
        "effect": "铸炼本命法宝或洞府器坊锻淬，大幅提升法宝锋锐与灵性",
        "summary": "天机阁千机堂以地心真火锻打九千九百锤所得之灵铁天材。",
    },
    {
        "id": "tj-tea",
        "name": "悟道九龙茶",
        "category": "极品灵茶",
        "token_cost": 25,
        "effect": "品茗参详自然造化，恢复满额灵力并获悟性经验",
        "summary": "采自中州昆仑天柱仙台万载仙古茶树之尖嫩清茗。",
    },
    {
        "id": "tj-box",
        "name": "天机万象盒",
        "category": "远古遗珍",
        "token_cost": 60,
        "effect": "开启后随机获得灵石 300~800 及罕见天材地宝",
        "summary": "从太古洞天深处发掘出的未知符文锦盒，机缘玄妙。",
    },
    {
        "id": "tj-scroll",
        "name": "通天机密卷",
        "category": "名望典籍",
        "token_cost": 50,
        "effect": "研读九州古今秘辛，名扬五域，修仙声望 +15",
        "summary": "记录九州名门兴衰与天骄战记的绝密手抄风云卷帙。",
    },
]


class TianjiRankingsEngine:
    @classmethod
    def calculate_player_power(cls, state: GameState) -> int:
        player = state.player
        power = (
            player.health_max // 2
            + player.spirit_max // 2
            + player.realm_index * 320
            + player.stage_index * 80
            + player.cultivation // 10
            + player.aptitude * 6
            + player.comprehension * 8
            + player.spirit_sense * 6
            + player.speed * 6
            + player.dao_heart * 6
            + len(player.inventory) * 8
        )
        if state.bonded_artifact:
            rec = state.artifact_refinements.get(state.bonded_artifact, {})
            power += int(rec.get("level", 0)) * 45 + int(rec.get("resonance", 0)) * 2 + len(rec.get("inscriptions", [])) * 30
        return max(100, power)

    @classmethod
    def get_player_rank(cls, state: GameState) -> int:
        rank = state.player.resources.get("天机排位", 0)
        if rank > 0:
            return rank
        # Default starting rank based on realm
        power = cls.calculate_player_power(state)
        # If early player, put at 15th
        rank = 15
        for i, t in enumerate(PRODIGY_TEMPLATES):
            if power > t.base_power:
                rank = i + 1
                break
        return max(1, min(len(PRODIGY_TEMPLATES) + 1, rank))

    @classmethod
    def set_player_rank(cls, state: GameState, rank: int) -> None:
        state.player.resources["天机排位"] = max(1, rank)

    @classmethod
    def get_prodigies_ladder(cls, state: GameState) -> list[dict[str, Any]]:
        player = state.player
        player_power = cls.calculate_player_power(state)
        player_rank = cls.get_player_rank(state)

        # Build list of candidates
        items: list[dict[str, Any]] = []
        for i, tmpl in enumerate(PRODIGY_TEMPLATES):
            realm_name = REALMS[min(tmpl.realm_index, len(REALMS) - 1)]
            stage_name = STAGES[min(tmpl.stage_index, len(STAGES) - 1)]
            full_realm = f"{realm_name}·{stage_name}"
            items.append({
                "id": tmpl.id,
                "name": tmpl.name,
                "dao_name": tmpl.dao_name,
                "sect": tmpl.sect,
                "province": tmpl.province,
                "realm": full_realm,
                "realm_index": tmpl.realm_index,
                "power": tmpl.base_power,
                "title": tmpl.title,
                "specialty": tmpl.specialty,
                "description": tmpl.description,
                "is_npc": tmpl.is_npc,
                "npc_name": tmpl.npc_name,
                "personality": tmpl.personality,
                "is_player": False,
            })

        # Insert player at player_rank (1-based index)
        player_entry = {
            "id": "player-self",
            "name": player.name,
            "dao_name": player.dao_name,
            "sect": player.sect,
            "province": state.player.location.split("·")[0] if "·" in state.player.location else state.player.location,
            "realm": player.realm,
            "realm_index": player.realm_index,
            "power": player_power,
            "title": "潜龙在渊 · 仙道求索",
            "specialty": player.equipped_spell or "流火术",
            "description": f"{player.name}，道号【{player.dao_name}】，身怀{player.spiritual_root}，于九州求索长生大道。",
            "is_npc": False,
            "npc_name": "",
            "personality": "道心坚定",
            "is_player": True,
        }

        insert_idx = min(len(items), max(0, player_rank - 1))
        items.insert(insert_idx, player_entry)

        # Assign final rank 1..N
        for idx, item in enumerate(items):
            item["rank"] = idx + 1
            can_challenge = not item["is_player"] and (item["rank"] < player_rank or abs(item["rank"] - player_rank) <= 3)
            item["can_challenge"] = can_challenge
            item["challenge_action"] = f"登榜问剑 {item['id']}"

        return items

    @classmethod
    def challenge_prodigy(cls, state: GameState, target_id: str) -> dict[str, Any]:
        """Player challenges a prodigy on the Tianji rankings."""
        ladder = cls.get_prodigies_ladder(state)
        target = next((item for item in ladder if item["id"] == target_id), None)
        if not target:
            raise ValueError(f"天机榜未见此修士踪迹：{target_id}")

        if target["is_player"]:
            raise ValueError("不可向自身论道问剑。")

        player = state.player
        if player.health < 25:
            raise ValueError("真气溃散、气血衰竭，需至少持有 25 点气血方可登台问剑。")

        player_power = cls.calculate_player_power(state)
        target_power = int(target["power"])

        # Determine win probability based on power ratio and comprehension
        ratio = player_power / max(1, target_power)
        # Ratio around 1.0 gives ~55% base chance
        base_chance = int(55 + (ratio - 1.0) * 45 + player.comprehension // 2)
        chance = max(15, min(95, base_chance))

        roll = ProgressionEngine.deterministic_roll(state, f"tianji_challenge:{target_id}:{state.turn}")
        success = roll <= chance

        tokens_held = player.resources.get("天机令", 0)
        curr_player_rank = cls.get_player_rank(state)
        target_rank = target["rank"]

        if success:
            # Swap or climb up!
            new_rank = min(curr_player_rank, target_rank)
            cls.set_player_rank(state, new_rank)
            token_gain = max(10, 35 - new_rank // 2)
            stone_gain = 120 + (len(PRODIGY_TEMPLATES) - new_rank) * 20
            rep_gain = 5

            player.resources["天机令"] = tokens_held + token_gain
            player.spirit_stones += stone_gain
            player.reputation += rep_gain

            msg = (
                f"【登榜问剑 · 扬名九州】你登临天机演武台挑战【{target['name']}】（{target['title']}）！"
                f"剑芒激荡破开其【{target['specialty']}】，战而胜之！"
                f"风云榜位晋升至第 {new_rank} 名！斩获天机令 +{token_gain}，灵石 +{stone_gain}，声望 +{rep_gain}！"
            )
        else:
            damage = 18 + target["realm_index"] * 4
            player.health = max(1, player.health - damage)
            cult_gain = 20 + player.comprehension * 2
            player.cultivation += cult_gain
            msg = (
                f"【登榜问剑 · 棋差一着】你与【{target['name']}】演武论剑三十合，"
                f"为其绝学【{target['specialty']}】所震，气血 -{damage}。但观摩高妙道法，修为顿悟 +{cult_gain}！"
            )

        state.remember(msg)

        return {
            "success": success,
            "target": target["name"],
            "target_rank": target_rank,
            "player_rank": cls.get_player_rank(state),
            "msg": msg,
        }

    @classmethod
    def redeem_treasure(cls, state: GameState, treasure_id: str) -> dict[str, Any]:
        """Player redeems an item from Tianji Treasure Vault using Tianji Tokens."""
        treasure = next((t for t in TIANJI_TREASURES if t["id"] == treasure_id), None)
        if not treasure:
            raise ValueError(f"天机宝库未收录此宝：{treasure_id}")

        player = state.player
        tokens = player.resources.get("天机令", 0)
        cost = treasure["token_cost"]

        if tokens < cost:
            raise ValueError(f"天机令不足：兑换【{treasure['name']}】需 {cost} 枚天机令，当前仅持有 {tokens} 枚。")

        player.resources["天机令"] = tokens - cost

        # Apply treasure effect
        if treasure["id"] == "tj-amulet":
            player.resources["天机避劫符"] = player.resources.get("天机避劫符", 0) + 1
        elif treasure["id"] == "tj-pill":
            player.cultivation += 150
            player.health = player.health_max
        elif treasure["id"] == "tj-iron":
            player.resources["天工万象铁"] = player.resources.get("天工万象铁", 0) + 1
        elif treasure["id"] == "tj-tea":
            player.spirit = player.spirit_max
            player.comprehension += 1
        elif treasure["id"] == "tj-box":
            import random
            gain = 450 + (state.turn % 7) * 45
            player.spirit_stones += gain
            player.resources["天材地宝"] = player.resources.get("天材地宝", 0) + 1
        elif treasure["id"] == "tj-scroll":
            player.reputation += 15

        msg = f"消耗 {cost} 枚天机令，成功于天机宝阁启封灵珍【{treasure['name']}】！"
        state.remember(msg)

        return {
            "treasure": treasure["name"],
            "cost": cost,
            "remaining_tokens": player.resources["天机令"],
            "msg": msg,
        }

    @classmethod
    def get_news(cls, state: GameState) -> list[str]:
        base_news = [
            "天机阁快讯：东洲青岳洗剑池剑气冲霄，顾清玄悟出通天剑意，潜龙榜位巍然不动！",
            "天机阁快讯：西漠大漠狂徒楚狂徒孤身斩灭化形沙蟒，战力暴涨五十分！",
            "天机阁快讯：合欢宗洛浅浅踏足中州万象坊市，引得数位世家天骄争相奉赠仙宝。",
            "天机阁快讯：北原雪渊极寒风暴大盛，据传谢无咎与白凝霜于天堑渊畔短暂对峙交手！",
            "天机阁快讯：天机宝库近日启封一批太古避劫神符，引得九州各宗门真传争相叩关。",
        ]
        # Rotate dynamically
        offset = state.turn % len(base_news)
        return base_news[offset:] + base_news[:offset]

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        player = state.player
        tokens = player.resources.get("天机令", 0)
        player_rank = cls.get_player_rank(state)
        player_power = cls.calculate_player_power(state)
        ladder = cls.get_prodigies_ladder(state)

        treasures_view = []
        for t in TIANJI_TREASURES:
            affordable = tokens >= t["token_cost"]
            treasures_view.append({
                "id": t["id"],
                "name": t["name"],
                "category": t["category"],
                "token_cost": t["token_cost"],
                "effect": t["effect"],
                "summary": t["summary"],
                "affordable": affordable,
                "action": f"天机兑换 {t['id']}",
            })

        return {
            "player_rank": player_rank,
            "player_power": player_power,
            "tokens": tokens,
            "prodigies": ladder,
            "overlords": OVERLORD_RANKINGS,
            "sects": SECT_PRESTIGE_RANKINGS,
            "treasures": treasures_view,
            "news": cls.get_news(state),
        }
