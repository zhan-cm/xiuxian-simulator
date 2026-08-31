from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable

from .engine import GameEngine
from .narrator import LocalNarrator
from .save_manager import SaveManager
from .webapp import WebApplication
from .commissions import CommissionEngine
from .auctions import AuctionEngine
from .cave import CaveEngine
from .npc_lifecycle import NpcLifecycleEngine
from .npc_network import NpcNetworkEngine
from .story import StoryEngine
from .new_era import NewEraEngine
from .formations import FormationEngine
from .sect_library import SectLibraryEngine
from .artifact_growth import ArtifactGrowthEngine
from .recovery import RecoveryEngine
from .sect_foundation import SectFoundationEngine


PageSetup = Callable[[GameEngine, WebApplication], dict[str, Any]]


def _ready(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    app.perform_action("开始游戏")
    return app.perform_action("确认默认创角")


def _action(action: str) -> PageSetup:
    def setup(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
        _ready(engine, app)
        return app.perform_action(action)

    return setup


def _recovery(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.health = 38
    engine.state.player.spirit = 52
    engine.state.player.resources["疗伤丹"] = 2
    RecoveryEngine.register(engine.state, "flesh", 2, "青岳古道遭劫")
    RecoveryEngine.register(engine.state, "meridian", 1, "强行催动流火术")
    return app.perform_action("伤势")


def _legacy_ending(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    player = engine.state.player
    engine.state.turn = 148
    engine.state.calendar_year = 399
    engine.state.month = 5
    player.age = 28
    player.realm_index = 2
    player.stage_index = 2
    player.realm = "结晶·后期"
    player.sect = "青云宗"
    player.sect_rank = "真传弟子"
    player.reputation = 86
    player.condition = "陨落于古战场魔潮"
    engine.state.visited_regions = ["东洲", "南疆", "中州"]
    engine.state.completed_commissions = ["委-01", "委-02", "委-03", "委-04"]
    engine.state.story_completed = ["tide-whisper", "vein-rift", "demon-seal", "abyss-tide"]
    player.dao_levels = {"剑道": 2, "有情道": 1}
    engine.state.spirit_beasts = {"qingfeng-fox": {"name": "青风狐", "level": 3}}
    engine.state.bonded_artifact = "玄铁剑"
    engine.state.phase = "ended"
    return app.perform_action("评传")


def _relations(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.npc_relations = {
        "顾清玄": {"affinity": 74, "path": "道侣"},
        "云栖": {"affinity": 48, "path": "好友"},
        "墨尘": {"affinity": 22, "path": "相识"},
    }
    engine.state.dao_partners = ["顾清玄"]
    engine.state.player.resources["凝晶丹"] = 1
    record = NpcLifecycleEngine.world_record(engine.state, "顾清玄")
    record.update({"stage_index": 3, "realm": "筑基·圆满", "cultivation_progress": 220, "age": 191})
    NpcLifecycleEngine.prepare_guard_request(engine.state, "顾清玄", "寿元将尽")
    return app.perform_action("情缘")


def _network(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.npc_relations = {
        "顾清玄": {"affinity": 36, "path": "知己"},
        "谢无咎": {"affinity": 24, "path": "相识"},
    }
    engine.state.player.reputation = 22
    bond = NpcNetworkEngine.bond(engine.state, "顾清玄", "谢无咎")
    bond.update({"score": -28, "encounters": 3, "last_event": "二人在青岳灵地归属上各执一词。"})
    NpcNetworkEngine.create_dispute(engine.state, "顾清玄", "谢无咎", "青岳灵地归属")
    return app.perform_action("人脉")


def _battle(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.resources["疗伤丹"] = 2
    return app.perform_action("挑战 山野劫修")


def _breakthrough(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.stage_index = 3
    engine.state.player.realm = "炼气·圆满"
    engine.state.player.cultivation = engine.state.player.cultivation_required
    engine.state.player.resources["筑基丹"] = 1
    return app.perform_action("突破")


def _crafts(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.resources.update({"灵药": 12, "妖兽材料": 4, "灵铁": 7, "符纸": 5})
    return app.perform_action("技艺")


def _cave(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.spirit_stones = 1200
    engine.state.player.resources.update({"灵药": 3, "灵铁": 12, "五行灵珠": 1})
    engine.state.cave_facilities.update({"静室": 1, "丹房": 2, "灵田": 1, "聚灵阵": 1})
    engine.state.cave_spirit_energy = 31
    engine.state.cave_focus = "百艺轮转"
    CaveEngine.queue_recipe(engine.state, "聚气丹")
    return app.perform_action("洞府")


def _journey(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    app.perform_action("修炼")
    engine.state.player.resources["灵药"] = 2
    return app.perform_action("道途")


def _commissions(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    board = CommissionEngine.snapshot(engine.state)
    herb = next(item for item in board["offers"] if item["template_id"] == "herb-delivery")
    app.perform_action(str(herb["accept_action"]))
    engine.state.player.resources["灵药"] = 3
    return app.perform_action("委托")


def _story(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    return app.perform_action("推进主线")


def _prepare_story_finale(engine: GameEngine, app: WebApplication) -> None:
    _ready(engine, app)
    engine.state.story_completed = ["tide-whisper", "vein-rift", "demon-seal", "abyss-tide", "nine-realms-council"]
    engine.state.story_choices = {
        "tide-whisper": "observe",
        "vein-rift": "seal",
        "demon-seal": "guard",
        "abyss-tide": "shelter",
        "nine-realms-council": "great-ward",
    }
    engine.state.story_history = [
        "第5章《九州会盟》｜共筑天幕｜灵石 -200，功德 +6，天下局势 -8",
        "第4章《魔潮越界》｜守城安民｜气血 -10，功德 +4，南疆民生 +7",
    ]
    engine.state.player.realm_index = 2
    engine.state.player.realm = "结晶·初期"
    engine.state.player.location = "中州·登仙台"
    engine.state.visited_regions = ["东洲", "南疆", "中州"]


def _story_finale(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _prepare_story_finale(engine, app)
    return app.perform_action("推进主线")


def _story_ending(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _prepare_story_finale(engine, app)
    StoryEngine.begin(engine.state)
    StoryEngine.resolve(engine.state, "guard-world")
    return app.perform_action("主线")


def _prepare_new_era(engine: GameEngine, app: WebApplication) -> None:
    _prepare_story_finale(engine, app)
    StoryEngine.begin(engine.state)
    StoryEngine.resolve(engine.state, "guard-world")
    engine.state.player.spirit_stones = 1200


def _new_era_pending(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _prepare_new_era(engine, app)
    engine.state.next_new_era_turn = engine.state.turn
    NewEraEngine.tick(engine.state)
    return app.perform_action("处置余波")


def _new_era_chronicle(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _prepare_new_era(engine, app)
    for choice_id in ("stabilize", "investigate", "convene"):
        event = NewEraEngine.next_event(engine.state)
        assert event is not None
        engine.state.new_era_available_event = event.id
        NewEraEngine.begin(engine.state)
        NewEraEngine.resolve(engine.state, choice_id)
    return app.perform_action("新世")


def _dao_tree(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·初期"
    engine.state.player.dao_insight = 14
    engine.state.player.dao_points = 2
    engine.state.player.dao_levels = {"剑道": 2, "丹道": 1, "有情道": 1}
    engine.state.player.health_max = 105
    engine.state.player.health = 105
    engine.state.player.dao_history = [
        "第 18 回合｜与顾清玄论道｜感悟 +12",
        "第 24 回合｜点亮剑道第 2 层｜攻击威力累计 +10%",
        "第 31 回合｜闭关消化感悟｜悟道点 +2",
    ]
    return app.perform_action("悟道")


def _spirit_beasts(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.resources["妖兽材料"] = 3
    engine.state.player.dao_levels["御兽道"] = 1
    engine.state.spirit_beasts = {
        "qingfeng-fox": {
            "name": "青风狐", "level": 3, "experience": 18,
            "bond": 72, "vigor": 64, "obtained_turn": 8,
        },
        "stoneback-turtle": {
            "name": "玄甲灵龟", "level": 2, "experience": 7,
            "bond": 45, "vigor": 92, "obtained_turn": 19,
        },
    }
    engine.state.active_spirit_beast = "qingfeng-fox"
    engine.state.spirit_beast_history = [
        "第 8 回合｜收服青风狐（24/68）",
        "第 21 回合｜青风狐历练 +8，成长至 2 级",
        "第 34 回合｜喂养青风狐，羁绊 +12",
    ]
    return app.perform_action("御兽")


def _formations(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 2
    engine.state.player.realm = "结晶·初期"
    engine.state.player.resources.update({"灵铁": 5, "符纸": 4, "灵药": 4, "妖兽材料": 2, "五行灵珠": 1, "道韵": 1})
    engine.state.player.craft_skills["阵法"] = 2
    engine.state.player.dao_levels["阵道"] = 1
    engine.state.formation_arrays = {
        "ember-slaying": {"integrity": 55, "built_turn": 11, "activations": 3},
        "stone-ward": {"integrity": 100, "built_turn": 18, "activations": 1},
        "spirit-gathering": {"integrity": 88, "built_turn": 29, "activations": 2},
    }
    engine.state.active_formation = "spirit-gathering"
    engine.state.formation_history = [
        "第 11 回合｜炼成赤阳焚敌阵（32/84）",
        "第 18 回合｜炼成玄土结界阵（41/88）",
        "第 29 回合｜炼成青木聚灵阵（46/93）",
        "第 34 回合｜装配青木聚灵阵",
    ]
    assert FormationEngine.active(engine.state) is not None
    return app.perform_action("阵法")


def _sect_library(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.sect = "青云宗"
    engine.state.player.sect_rank = "真传弟子"
    engine.state.player.sect_contribution = 640
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·后期"
    engine.state.sect_library_claims = ["qingyun-evergreen"]
    engine.state.player.resources["青木长生诀残卷"] = 1
    engine.state.sect_library_history = [
        "第 8 回合｜以贡献 100 领取长生青简，所得 青木长生诀残卷×1",
        "第 19 回合｜接受青云宗年度传功，感悟 +18，修为 +14",
        "第 31 回合｜晋升真传后获准进入藏经阁上层",
    ]
    assert SectLibraryEngine.snapshot(engine.state)["member"]
    return app.perform_action("藏经阁")


def _sect_domain(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    player = engine.state.player
    player.realm_index = 3
    player.stage_index = 1
    player.realm = "金丹·中期"
    player.reputation = 92
    player.spirit_stones = 5200
    SectFoundationEngine.begin(engine.state, "青玄宗")
    SectFoundationEngine.found(engine.state, "harmony")
    sect = engine.state.founded_sect
    sect.update({"level": 3, "experience": 408, "renown": 67, "stability": 88, "treasury": 2860, "monthly_net": 42})
    sect["buildings"] = {"hall": 1, "academy": 2, "workshop": 1, "ward": 2}
    sect["focus"] = "elite"
    for offset in range(3, 7):
        engine.state.sect_disciples.append(SectFoundationEngine._make_disciple(engine.state, offset))
    for index, disciple in enumerate(engine.state.sect_disciples):
        disciple["progress"] = 18 + index * 9
        if index < 2:
            disciple.update({"realm_index": 1, "stage_index": index, "role": "亲传弟子"})
    engine.state.sect_foundation_history.extend([
        "天玄历389年3月｜百炼坊落成，山门月度库藏渐丰",
        "天玄历389年9月｜掌门开坛传法，六名门人皆有所得",
        "天玄历390年1月｜宗门晋为名动一域，九州声望渐起",
    ])
    engine.state.faction_strengths["青玄宗"] = 136
    return app.perform_action("宗门经营")


def _artifacts(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 2
    engine.state.player.realm = "结晶·后期"
    engine.state.player.spirit_stones = 920
    engine.state.player.resources.update({"玄铁剑": 1, "护身法袍": 1, "灵铁": 15, "妖兽材料": 8})
    engine.state.player.equipped_weapon = "玄铁剑"
    engine.state.player.equipped_armor = "护身法袍"
    engine.state.bonded_artifact = "玄铁剑"
    engine.state.artifact_refinements = {
        "玄铁剑": {"level": 2, "resonance": 68, "victories": 7, "refinements": 2, "last_nourished_turn": -3},
        "护身法袍": {"level": 1, "resonance": 0, "victories": 0, "refinements": 1, "last_nourished_turn": -3},
    }
    engine.state.artifact_history = [
        "第 12 回合｜立下本命法宝：玄铁剑，器心契合 10/100",
        "第 27 回合｜淬炼玄铁剑成功，升至二炼（38/76）",
        "第 36 回合｜温养玄铁剑，器心契合 +10",
    ]
    assert ArtifactGrowthEngine.snapshot(engine.state)["bonded_name"] == "玄铁剑"
    return app.perform_action("法宝谱")


def _art_mastery(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    player = engine.state.player
    player.known_techniques = ["聚气诀", "青木长生诀", "赤炎真经"]
    player.primary_technique = "青木长生诀"
    player.primary_technique_grade = "玄阶"
    player.equipped_auxiliary_techniques = ["赤炎真经"]
    player.known_spells = ["流火术", "青木缚灵术"]
    player.equipped_spell = "青木缚灵术"
    engine.state.technique_mastery = {"聚气诀": 480, "青木长生诀": 285, "赤炎真经": 145}
    engine.state.spell_mastery = {"流火术": 130, "青木缚灵术": 68}
    engine.state.art_mastery_history = [
        "第 14 回合｜聚气诀由大成晋至圆满（闭关）",
        "第 27 回合｜赤炎真经由小成晋至精通（随修）",
        "第 36 回合｜参研青木缚灵术，熟练度 +19",
    ]
    return app.perform_action("道法")


def _inventory(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.health = 62
    engine.state.player.spirit = 71
    engine.state.player.resources.update(
        {"青锋剑": 1, "护身法袍": 1, "疗伤丹": 2, "聚气丹": 3, "灵药": 7, "五行灵珠": 1, "火球符": 2}
    )
    engine.state.player.equipped_weapon = "青锋剑"
    return app.perform_action("背包")


def _auction(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.spirit_stones = 3600
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·初期"
    AuctionEngine.open(engine.state, duration=3)
    lot = next(item for item in engine.state.auction["lots"] if int(item["minimum_realm"]) <= 1)
    return app.perform_action(f"竞拍 {lot['id']}")


def _travel(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·初期"
    engine.state.player.spirit_stones = 1200
    return app.perform_action("前往 中州")


def _map(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·初期"
    engine.state.regional_reputation.update({"东洲": 28, "南疆": -8, "中州": 14})
    return app.perform_action("地图")


def _regional(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    _ready(engine, app)
    engine.state.player.realm_index = 1
    engine.state.player.realm = "筑基·初期"
    engine.state.player.location = "南疆·赤炎"
    engine.state.visited_regions.append("南疆")
    engine.state.regional_reputation["南疆"] = 18
    return app.perform_action("地方机缘")


SHOWCASE_PAGES: tuple[tuple[str, str, str, list[str], PageSetup], ...] = (
    ("home", "洞府主界面", "查看新版三栏结构、根基状态和自由行动入口。", ["核心事件应最醒目", "属性数值应一眼可读", "未开放行动需要灰化"], _ready),
    ("recovery", "伤势疗愈", "检查结构化伤势、真实惩罚、调养月份与两种恢复入口。", ["伤势入口应醒目但不挤占主面板", "四项实际惩罚与伤势缘起清楚", "巡览中的静养和服丹按钮必须禁用"], _recovery),
    ("legacy-ending", "仙途评传", "检查本世总结、道途评分、关键履历与下一世三道传承。", ["死亡结果必须收束成完整评传", "传承效果和选择状态清楚", "巡览中所有铭刻按钮必须禁用"], _legacy_ending),
    ("journey", "道途章程", "检查长期目标、完成状态和分章奖励。", ["主界面只显示紧凑进度", "展开后四章结构清楚", "巡览中的领取按钮必须禁用"], _journey),
    ("commissions", "东洲悬榜", "检查委托接取、真实进度、期限与交付报酬。", ["在途与可接委托清楚分层", "完成进度来自规则引擎", "巡览中所有操作必须禁用"], _commissions),
    ("story", "灵潮因果", "检查主线篇章、解锁条件与三项重大抉择。", ["篇章脉络应清楚", "抉择按钮接入真实状态机", "巡览中推进按钮必须禁用"], _story),
    ("story-finale", "潮汐终局", "检查前五章因果倾向与终章三条结局路线。", ["守世、问天、同道共鸣可比较", "结局完成度由前置选择推导", "巡览中的终局按钮必须禁用"], _story_finale),
    ("story-ending", "本世结局", "检查终章落定后的时代、命格与结局回顾。", ["结局卡突出但不遮挡六章卷宗", "时代与永久命格来自真实结算", "旧因果历史仍可回看"], _story_ending),
    ("new-era-pending", "新世余波", "检查结局驱动的新世事件、三项世界指标与真实资源门槛。", ["事件必须来自当前结局路线", "三项应对的长期后果清楚", "巡览中的余波选择必须禁用"], _new_era_pending),
    ("new-era-chronicle", "新世卷宗", "检查多轮余波之后的指标变化、阶段演化与永久历史。", ["三项指标不挤成一行文字", "每轮选择保留清晰记录", "三轮后形成新世纪里程碑"], _new_era_chronicle),
    ("dao-tree", "悟道九途", "检查感悟转化、九条永久道途、境界门槛与点亮状态。", ["九途必须使用独立小组件", "当前与下一层效果可快速比较", "巡览中的点亮与观想按钮必须禁用"], _dao_tree),
    ("spirit-beasts", "万灵兽苑", "检查战宠羁绊、精力、成长、出战位与喂养状态。", ["每只灵兽使用独立养成卡", "三条成长仪表一眼可读", "巡览中的探寻、出战与喂养必须禁用"], _spirit_beasts),
    ("formations", "五行阵图", "检查阵图研习、阵盘装配、阵基损耗与五类战术定位。", ["五卷阵图使用独立阵盘卡", "阵材、成功率与阵基可快速比较", "巡览中的炼制、装配与修复必须禁用"], _formations),
    ("art-mastery", "万法参研", "检查功法与法术的五重熟练境界、真实增益和参研门槛。", ["主修、辅修与配术状态清楚", "当前与下一境界效果可比较", "巡览中的参研按钮必须禁用"], _art_mastery),
    ("artifacts", "本命法宝", "检查法宝认主、境界淬炼上限、器心契合与真实战斗加成。", ["本命与普通法宝层级清楚", "淬炼成本、成功率和锁定原因可比较", "巡览中的认主、淬炼与温养必须禁用"], _artifacts),
    ("inventory", "乾坤万象", "检查物品分类、详情用途、装备槽位与真实操作状态。", ["品级与分类应清楚", "装备状态与槽位同步", "巡览中使用和装备按钮必须禁用"], _inventory),
    ("auction", "天机竞价", "检查限时拍品、对手情报、准入条件与竞价入口。", ["四件拍品层级清楚", "灵石或境界不足时自动锁定", "巡览中所有竞价入口必须禁用"], _auction),
    ("map", "九州舆图", "验证五域路线、区域商情、境界准入与当地探索。", ["当前所在地与已踏访状态明确", "高境界地域自动锁定", "特产、求购和行程可快速比较"], _map),
    ("travel", "跨域行旅", "检查远行方式、真实时间成本与风险说明。", ["商队与御风的成本清楚", "资源不足时自动锁定", "取消行程不会推进时间"], _travel),
    ("regional", "地方机缘", "检查五域声望、资源门槛和会被世界记住的地方抉择。", ["三项应对的后果清楚", "资源不足选项自动锁定", "巡览中的选择不会改动正式存档"], _regional),
    ("market", "青岳坊市", "验证分类货架、购买能力和持有数量。", ["货物不再堆成长文字", "买卖价格可直接比较", "灵石不足时按钮禁用"], _action("坊市")),
    ("sects", "宗门择路", "查看各宗门的独立身份卡与试炼入口。", ["宗门气质容易区分", "试炼后果有提示", "按钮接入真实行动"], _action("宗门")),
    ("sect-library", "宗门藏经阁", "检查贡献兑换、职位权限、年度传功与宗门专属传承。", ["职位阶序和解锁范围一眼可读", "贡献不足或已领取会明确锁定", "巡览中的兑换与传功必须禁用"], _sect_library),
    ("sect-domain", "开宗立派", "检查自立山门后的门人、库藏、道统方针与设施营造。", ["宗门经营使用独立组件而非文字长串", "收徒、传法、方针和营造状态清楚", "巡览中的所有经营操作必须禁用"], _sect_domain),
    ("relations", "浮生故人", "验证人物寿元、生平、护道抉择和关系路径。", ["年龄、境界与在世状态来自真实存档", "护道资源门槛与三种选择清楚", "故人生平不挤成一行"], _relations),
    ("network", "众生缘网", "验证人物彼此结交、嫌隙、往来履历与玩家介入。", ["关系方向和强度可快速辨认", "纷争介入有真实门槛与后果", "巡览中的所有介入按钮必须禁用"], _network),
    ("battle", "临阵抉择", "查看战前敌情和所有可点击战斗抉择。", ["敌我风险明确", "危险操作视觉统一", "选择按钮状态清楚"], _battle),
    ("realms", "九州秘境", "验证秘境危险度、准入境界和确认流程。", ["致命区域必须锁定", "描述与操作分层", "进入前仍有二次确认"], _action("秘境")),
    ("breakthrough", "筑基之门", "检查三条突破路线的材料和风险反馈。", ["路线选中态统一", "缺少材料明确灰化", "心魔雷劫概率可读"], _breakthrough),
    ("crafts", "修仙百艺", "验证配方材料、成功率和制作入口。", ["配方可快速比较", "缺少材料自动锁定", "制作会推进时间"], _crafts),
    ("cave", "洞天经营", "查看洞府灵蕴、运转方针、后台生产与设施营造。", ["灵蕴与月度产量清楚", "后台工坊展示真实工期", "设施、方针与配方分层收纳"], _cave),
    ("world", "九州天下", "检查势力、民生、世界阶段和大事记。", ["世界状态不挤占主剧情", "势力数值易比较", "旧事件按需展开"], _action("天下")),
    ("arts", "初悟道法", "查看新修士初始功法、法术和熟练度起点。", ["初始道法不再堆成长文字", "五重境界进度应清楚", "后续可直接参研成长"], _action("道法")),
)


def build_showcase(source: GameEngine, root: Path) -> list[dict[str, Any]]:
    """Build read-only showcase snapshots with isolated save directories."""
    pages: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="xiuxian-showcase-") as temp_dir:
        temp_root = Path(temp_dir)
        for index, (page_id, title, description, checklist, setup) in enumerate(SHOWCASE_PAGES):
            engine = GameEngine(
                source.rules,
                SaveManager(temp_root / f"page-{index:02d}"),
                LocalNarrator(),
                autosave_name="showcase",
            )
            app = WebApplication(engine, root / "web")
            snapshot = setup(engine, app)
            pages.append(
                {
                    "id": page_id,
                    "title": title,
                    "description": description,
                    "checklist": checklist,
                    "snapshot": snapshot,
                }
            )
    return pages
