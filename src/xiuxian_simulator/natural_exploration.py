from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .progression import ProgressionEngine, REALMS
from .state import GameState
from .travel import TravelEngine, REGIONS, DISTANCES


@dataclass(frozen=True, slots=True)
class KyushuLandmark:
    id: str
    province: str
    name: str
    title: str
    category: str
    required_realm: int
    scenery: str
    specialties: tuple[str, ...]
    ferry_name: str
    ferry_desc: str


KYUSHU_LANDMARKS: dict[str, KyushuLandmark] = {
    "东洲": KyushuLandmark(
        id="dz-sword-pool",
        province="东洲",
        name="青岳洗剑池",
        title="万剑通玄 · 洗剑清池",
        category="剑仙灵脉",
        required_realm=0,
        scenery="青岳绝巅，飞泉注玉。池底沉有上古万千名剑剑胚，剑气凌霄，波光若雪。",
        specialties=("灵泉玉液", "洗剑古砂", "古剑残片"),
        ferry_name="青岳灵渡",
        ferry_desc="东洲最大临海仙港，常驻巨型破浪楼船与御风灵舟。",
    ),
    "南疆": KyushuLandmark(
        id="nj-fire-cave",
        province="南疆",
        name="赤炎地肺火窟",
        title="万丈真火 · 地肺炎脉",
        category="极阳熔窟",
        required_realm=1,
        scenery="十万火山绵延不绝，赤红熔岩翻涌喷薄，纯阳炎气直冲斗牛。",
        specialties=("地心火晶", "赤炎芝", "真火源气"),
        ferry_name="天火赤渡",
        ferry_desc="建于南疆熔岩赤江入海口之仙港，浮空云舟可直跨中州与东海。",
    ),
    "西漠": KyushuLandmark(
        id="xm-buddha-caves",
        province="西漠",
        name="流沙鸣沙千佛窟",
        title="古佛遗音 · 菩提梵刹",
        category="佛门古迹",
        required_realm=2,
        scenery="金色瀚海深处，万仞古岩开凿三千石窟，梵音袅袅，菩提古树结金莲。",
        specialties=("菩提金叶", "鸣沙神香", "古佛舍利残片"),
        ferry_name="鸣沙古渡",
        ferry_desc="可停泊横渡流沙死海之巨型穿沙灵舶与飞天云舟。",
    ),
    "北原": KyushuLandmark(
        id="by-frost-abyss",
        province="北原",
        name="极北万载寒渊",
        title="玄冰封印 · 幽冥极光",
        category="极寒绝地",
        required_realm=3,
        scenery="终年罡风暴雪撕裂苍穹，万里玄冰天堑下涌动幽冥极光，太古雪兽蛰伏。",
        specialties=("万载玄冰", "极北寒髓", "雪魄灵晶"),
        ferry_name="雪鲸霜渡",
        ferry_desc="由极北通灵巨兽与破冰法舟护航的避雪仙渡。",
    ),
    "中州": KyushuLandmark(
        id="zz-celestial-pillar",
        province="中州",
        name="昆仑天柱仙台",
        title="仙阙浮云 · 天地之脊",
        category="登仙圣地",
        required_realm=1,
        scenery="通天巨峰上接九霄罡风，浮空金阙若隐若现，百代飞升大能留痕于此。",
        specialties=("太虚清气", "九天仙露", "通天道碑拓本"),
        ferry_name="通天帝渡",
        ferry_desc="九州行旅之核心总枢，日夜有浮空巨舰穿梭五域。",
    ),
    "云州": KyushuLandmark(
        id="yz-mirage-marsh",
        province="云州",
        name="云梦太虚蜃泽",
        title="太虚蜃气 · 浮生幻境",
        category="幻梦灵境",
        required_realm=4,
        scenery="八百里云梦浩瀚大泽，蜃气横生，庄周化蝶，真伪难辨。",
        specialties=("太虚梦蝶卵", "千幻云蜃珠", "雾隐仙萝"),
        ferry_name="蜃海迷渡",
        ferry_desc="唯有持定风珠与破妄法符之修士方敢登船的云海渡口。",
    ),
    "雷州": KyushuLandmark(
        id="lz-thunder-pool",
        province="雷州",
        name="九天紫霄雷池",
        title="万劫神雷 · 紫霄雷泽",
        category="太古禁域",
        required_realm=5,
        scenery="九霄雷云压顶，百道紫霄神雷同时劈落，天雷淬体，万古不灭。",
        specialties=("紫霄雷竹", "九天雷劫木", "辟邪神雷晶"),
        ferry_name="避劫雷渡",
        ferry_desc="以纯阳法阵为骨的御雷仙舟渡口。",
    ),
    "幽州": KyushuLandmark(
        id="yz-nether-river",
        province="幽州",
        name="忘川黄泉冥渊",
        title="冥河忘川 · 轮回天堑",
        category="九幽绝地",
        required_realm=6,
        scenery="死寂忘川河上红莲业火摇曳，九幽冥煞遮天蔽日，可勘破生死轮回奥义。",
        specialties=("忘川彼岸花", "玄冥重水", "黄泉幽魄石"),
        ferry_name="冥海引魂渡",
        ferry_desc="摆渡于阴阳两界的太古冥舟码头。",
    ),
    "瀛洲": KyushuLandmark(
        id="yz-penglai-isle",
        province="瀛洲",
        name="蓬莱不死仙岛",
        title="海外三山 · 不死仙药",
        category="海外仙墟",
        required_realm=6,
        scenery="深藏海天尽头无尽灵雾之中，仙鹤成群，古仙药圃长生药香飘荡十里。",
        specialties=("不死仙芝", "九品碧海珊瑚", "乘鸾仙羽"),
        ferry_name="凌虚仙舟渡",
        ferry_desc="可破开无尽迷仙阵的海外飞天宝舰渡口。",
    ),
}


class NaturalExplorationEngine:
    @classmethod
    def current_landmark(cls, state: GameState) -> KyushuLandmark:
        region = TravelEngine.current_region(state)
        return KYUSHU_LANDMARKS.get(region, KYUSHU_LANDMARKS["东洲"])

    @classmethod
    def get_landmark_by_id_or_province(cls, identifier: str) -> KyushuLandmark:
        ident = identifier.strip()
        for lm in KYUSHU_LANDMARKS.values():
            if ident in (lm.id, lm.name, lm.province) or ident.startswith(lm.province):
                return lm
        raise ValueError(f"未找到对应的名山胜境：{identifier}")

    @classmethod
    def meditate(cls, state: GameState, identifier: str = "") -> dict[str, Any]:
        """Player meditates in a natural wonder to absorb cosmic essence and cultivate."""
        landmark = cls.get_landmark_by_id_or_province(identifier) if identifier else cls.current_landmark(state)
        player = state.player

        if player.realm_index < landmark.required_realm:
            required = REALMS[min(landmark.required_realm, len(REALMS) - 1)]
            raise ValueError(f"道基未稳：{landmark.name}煞气沉重，需修至{required}境方可坐照观想。")

        # Gains based on realm, comprehension, and landmark aura
        cult_gain = 25 + player.realm_index * 15 + player.comprehension * 2
        roll = ProgressionEngine.deterministic_roll(state, f"meditate:{landmark.id}:{state.turn}")
        epiphany = roll >= 80

        dao_gain = 1 if epiphany else 0
        player.cultivation += cult_gain
        if dao_gain:
            player.dao_points += dao_gain

        # Recover health and spirit partially
        player.health = min(player.health_max, player.health + 20)
        player.spirit = min(player.spirit_max, player.spirit + 30)

        msg = f"在【{landmark.name}】坐照观想，吸纳天地灵机：修为 +{cult_gain}"
        if epiphany:
            msg += f"，福至心灵顿悟自然道理，悟道点 +{dao_gain}！"
        state.remember(msg)

        return {
            "landmark": landmark.name,
            "province": landmark.province,
            "cultivation_gain": cult_gain,
            "epiphany": epiphany,
            "dao_gain": dao_gain,
            "msg": msg,
        }

    @classmethod
    def harvest(cls, state: GameState, identifier: str = "") -> dict[str, Any]:
        """Player searches and harvests special natural herbs or minerals in the landmark."""
        landmark = cls.get_landmark_by_id_or_province(identifier) if identifier else cls.current_landmark(state)
        player = state.player

        if player.realm_index < landmark.required_realm:
            required = REALMS[min(landmark.required_realm, len(REALMS) - 1)]
            raise ValueError(f"胜境险峻：前往{landmark.name}搜山需至少{required}境界。")

        if player.spirit < 15:
            raise ValueError("灵力不足：搜山采灵需御使神识，需至少 15 点灵力。")

        player.spirit -= 15

        # Harvest success chance based on fortune, spirit sense, and speed
        chance = max(35, min(95, 55 + player.fortune * 2 + player.spirit_sense // 2))
        roll = ProgressionEngine.deterministic_roll(state, f"harvest:{landmark.id}:{state.turn}")
        success = roll <= chance

        harvested_item = ""
        harvested_count = 0
        stones_gain = 0
        rep_gain = 0

        if success:
            import random
            # Deterministic selection based on turn and id
            idx = (state.turn + len(landmark.id)) % len(landmark.specialties)
            harvested_item = landmark.specialties[idx]
            harvested_count = 1 if player.realm_index >= 3 else 2
            player.resources[harvested_item] = player.resources.get(harvested_item, 0) + harvested_count
            stones_gain = 40 + player.realm_index * 20
            rep_gain = 2
            player.spirit_stones += stones_gain
            player.reputation += rep_gain
            msg = f"巡行【{landmark.name}】：寻得天产灵珍【{harvested_item}】×{harvested_count}，采集伴生灵石 +{stones_gain}，声望 +{rep_gain}"
        else:
            msg = f"巡行【{landmark.name}】：云雾缭绕未遇通灵宝药，沿途采得少许灵花异草，空手而返。"

        state.remember(msg)

        return {
            "landmark": landmark.name,
            "province": landmark.province,
            "success": success,
            "item": harvested_item,
            "count": harvested_count,
            "stones": stones_gain,
            "reputation": rep_gain,
            "msg": msg,
        }

    @classmethod
    def explore_secret(cls, state: GameState, identifier: str = "") -> dict[str, Any]:
        """Player delves into the ancient sealed cave/ruin inside the landmark."""
        landmark = cls.get_landmark_by_id_or_province(identifier) if identifier else cls.current_landmark(state)
        player = state.player

        if player.realm_index < landmark.required_realm:
            required = REALMS[min(landmark.required_realm, len(REALMS) - 1)]
            raise ValueError(f"封印险绝：破解{landmark.name}深处禁制洞窟需修至{required}境。")

        # Secret exploration chance
        chance = max(25, min(92, 50 + player.realm_index * 8 + player.spirit_sense // 2 - landmark.required_realm * 6))
        roll = ProgressionEngine.deterministic_roll(state, f"secret:{landmark.id}:{state.turn}")
        success = roll <= chance

        if success:
            stones = 200 + player.realm_index * 60
            rep = 6
            player.spirit_stones += stones
            player.reputation += rep
            # Give a rare item
            rare_item = landmark.specialties[0]
            player.resources[rare_item] = player.resources.get(rare_item, 0) + 1
            msg = f"探秘【{landmark.name}】古仙洞窟：破除残存禁制，得灵石 +{stones}，声望 +{rep}，启获灵物【{rare_item}】！"
        else:
            damage = 15 + landmark.required_realm * 3
            player.health = max(1, player.health - damage)
            rep_loss = 1
            player.reputation = max(0, player.reputation - rep_loss)
            msg = f"探秘【{landmark.name}】古仙洞窟：触动上古残阵反震，气血 -{damage}，未能破禁。"

        state.remember(msg)

        return {
            "landmark": landmark.name,
            "province": landmark.province,
            "success": success,
            "msg": msg,
        }

    @classmethod
    def ferry_cloud_ship(cls, state: GameState, destination: str) -> dict[str, Any]:
        """Player takes a cross-province cloud ship ferry."""
        origin = TravelEngine.current_region(state)
        dest_norm = TravelEngine.normalize_destination(destination)
        if origin == dest_norm:
            raise ValueError(f"你已经身在{REGIONS[dest_norm].name}。")

        region = REGIONS[dest_norm]
        if state.player.realm_index < region.minimum_realm:
            required = REALMS[region.minimum_realm]
            raise ValueError(f"【渡海受阻】{region.name}天堑风暴强烈，仙舟要求登船者修为至少达{required}境。")

        distance = TravelEngine.distance(origin, dest_norm)
        months = max(1, distance - 1)
        cost_stones = months * 45

        player = state.player
        if player.spirit_stones < cost_stones:
            raise ValueError(f"船资不足：乘坐渡海灵舟需 {cost_stones} 灵石（{months} 个月航程），当前持有 {player.spirit_stones}。")

        player.spirit_stones -= cost_stones

        # High success rate due to ship ward array
        chance = max(40, min(98, 94 - region.danger // 10 + player.realm_index * 2))
        roll = ProgressionEngine.deterministic_roll(state, f"ferry:{origin}:{dest_norm}:{state.turn}")
        success = roll <= chance

        if success:
            event = f"渡海灵舟破浪穿云，船中阵法稳固。航行 {months} 个月后安然抵岸于{region.name}。"
        else:
            event = f"渡海灵舟航经凶险海域遭遇风暴海兽，剧烈颠簸中受了些许震荡，{months} 个月后抵达{region.name}。"
            player.health = max(1, player.health - 12)

        player.location = region.name
        if dest_norm not in state.visited_regions:
            state.visited_regions.append(dest_norm)

        record = f"{REGIONS[origin].name} → {region.name}｜渡海灵舟｜{months}月"
        state.travel_history.append(record)
        state.travel_history = state.travel_history[-30:]
        state.remember(event)

        return {
            "origin": origin,
            "destination": dest_norm,
            "months": months,
            "cost_stones": cost_stones,
            "success": success,
            "event": event,
        }

    @classmethod
    def ancient_teleport(cls, state: GameState, destination: str) -> dict[str, Any]:
        """Player uses an ancient teleportation array to traverse instantly (1 month)."""
        origin = TravelEngine.current_region(state)
        dest_norm = TravelEngine.normalize_destination(destination)
        if origin == dest_norm:
            raise ValueError(f"你已经身在{REGIONS[dest_norm].name}。")

        region = REGIONS[dest_norm]
        if state.player.realm_index < max(1, region.minimum_realm):
            raise ValueError("空间乱流极强：启动太古挪移大阵需至少筑基境道躯方可抗衡虚空拉扯。")

        distance = TravelEngine.distance(origin, dest_norm)
        cost_stones = 160 + distance * 30

        player = state.player
        if player.spirit_stones < cost_stones:
            raise ValueError(f"灵石不足：开启古挪移阵需 {cost_stones} 极品灵石作为阵基驱动，当前仅有 {player.spirit_stones}。")

        player.spirit_stones -= cost_stones
        player.location = region.name
        if dest_norm not in state.visited_regions:
            state.visited_regions.append(dest_norm)

        months = 1
        record = f"{REGIONS[origin].name} → {region.name}｜太古挪移｜1月"
        state.travel_history.append(record)
        state.travel_history = state.travel_history[-30:]

        event = f"太古阵台符光冲天，虚空震荡撕裂天幕！瞬息之间已跨越千山万壑，踏足{region.name}古阵坛！"
        state.remember(event)

        return {
            "origin": origin,
            "destination": dest_norm,
            "months": months,
            "cost_stones": cost_stones,
            "event": event,
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Snapshot of all Kyushu natural exploration data."""
        current_region = TravelEngine.current_region(state)
        player = state.player

        landmarks_view = []
        for key, lm in KYUSHU_LANDMARKS.items():
            is_current = (key == current_region)
            accessible = player.realm_index >= lm.required_realm
            req_label = "炼气可达" if lm.required_realm == 0 else f"{REALMS[min(lm.required_realm, len(REALMS) - 1)]}可达"
            landmarks_view.append({
                "id": lm.id,
                "province": lm.province,
                "name": lm.name,
                "title": lm.title,
                "category": lm.category,
                "required_realm": lm.required_realm,
                "requirement_label": req_label,
                "scenery": lm.scenery,
                "specialties": list(lm.specialties),
                "ferry_name": lm.ferry_name,
                "ferry_desc": lm.ferry_desc,
                "is_current": is_current,
                "accessible": accessible,
                "actions": {
                    "meditate": f"胜境悟道 {lm.id}",
                    "harvest": f"胜境采灵 {lm.id}",
                    "explore_secret": f"胜境探幽 {lm.id}",
                },
            })

        current_lm = KYUSHU_LANDMARKS.get(current_region, KYUSHU_LANDMARKS["东洲"])

        # Ferry destinations from current region
        ferry_routes = []
        for dest_key in ("东洲", "南疆", "西漠", "北原", "中州"):
            if dest_key != current_region:
                dist = TravelEngine.distance(current_region, dest_key)
                months = max(1, dist - 1)
                cost = months * 45
                reg = REGIONS[dest_key]
                can_travel = player.realm_index >= reg.minimum_realm and player.spirit_stones >= cost
                ferry_routes.append({
                    "destination": dest_key,
                    "destination_name": reg.name,
                    "months": months,
                    "cost_stones": cost,
                    "can_travel": can_travel,
                    "action": f"渡海灵舟 {dest_key}",
                })

        return {
            "current_region": current_region,
            "current_landmark": {
                "id": current_lm.id,
                "province": current_lm.province,
                "name": current_lm.name,
                "title": current_lm.title,
                "category": current_lm.category,
                "scenery": current_lm.scenery,
                "specialties": list(current_lm.specialties),
                "ferry_name": current_lm.ferry_name,
                "ferry_desc": current_lm.ferry_desc,
            },
            "landmarks": landmarks_view,
            "ferry_routes": ferry_routes,
            "player_realm_index": player.realm_index,
            "player_stones": player.spirit_stones,
        }
