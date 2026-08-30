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


PageSetup = Callable[[GameEngine, WebApplication], dict[str, Any]]


def _ready(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
    app.perform_action("开始游戏")
    return app.perform_action("确认默认创角")


def _action(action: str) -> PageSetup:
    def setup(engine: GameEngine, app: WebApplication) -> dict[str, Any]:
        _ready(engine, app)
        return app.perform_action(action)

    return setup


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
    ("journey", "道途章程", "检查长期目标、完成状态和分章奖励。", ["主界面只显示紧凑进度", "展开后四章结构清楚", "巡览中的领取按钮必须禁用"], _journey),
    ("commissions", "东洲悬榜", "检查委托接取、真实进度、期限与交付报酬。", ["在途与可接委托清楚分层", "完成进度来自规则引擎", "巡览中所有操作必须禁用"], _commissions),
    ("story", "灵潮因果", "检查主线篇章、解锁条件与三项重大抉择。", ["篇章脉络应清楚", "抉择按钮接入真实状态机", "巡览中推进按钮必须禁用"], _story),
    ("inventory", "乾坤万象", "检查物品分类、详情用途、装备槽位与真实操作状态。", ["品级与分类应清楚", "装备状态与槽位同步", "巡览中使用和装备按钮必须禁用"], _inventory),
    ("auction", "天机竞价", "检查限时拍品、对手情报、准入条件与竞价入口。", ["四件拍品层级清楚", "灵石或境界不足时自动锁定", "巡览中所有竞价入口必须禁用"], _auction),
    ("map", "九州舆图", "验证五域路线、区域商情、境界准入与当地探索。", ["当前所在地与已踏访状态明确", "高境界地域自动锁定", "特产、求购和行程可快速比较"], _map),
    ("travel", "跨域行旅", "检查远行方式、真实时间成本与风险说明。", ["商队与御风的成本清楚", "资源不足时自动锁定", "取消行程不会推进时间"], _travel),
    ("regional", "地方机缘", "检查五域声望、资源门槛和会被世界记住的地方抉择。", ["三项应对的后果清楚", "资源不足选项自动锁定", "巡览中的选择不会改动正式存档"], _regional),
    ("market", "青岳坊市", "验证分类货架、购买能力和持有数量。", ["货物不再堆成长文字", "买卖价格可直接比较", "灵石不足时按钮禁用"], _action("坊市")),
    ("sects", "宗门择路", "查看各宗门的独立身份卡与试炼入口。", ["宗门气质容易区分", "试炼后果有提示", "按钮接入真实行动"], _action("宗门")),
    ("relations", "浮生故人", "验证人物寿元、生平、护道抉择和关系路径。", ["年龄、境界与在世状态来自真实存档", "护道资源门槛与三种选择清楚", "故人生平不挤成一行"], _relations),
    ("network", "众生缘网", "验证人物彼此结交、嫌隙、往来履历与玩家介入。", ["关系方向和强度可快速辨认", "纷争介入有真实门槛与后果", "巡览中的所有介入按钮必须禁用"], _network),
    ("battle", "临阵抉择", "查看战前敌情和所有可点击战斗抉择。", ["敌我风险明确", "危险操作视觉统一", "选择按钮状态清楚"], _battle),
    ("realms", "九州秘境", "验证秘境危险度、准入境界和确认流程。", ["致命区域必须锁定", "描述与操作分层", "进入前仍有二次确认"], _action("秘境")),
    ("breakthrough", "筑基之门", "检查三条突破路线的材料和风险反馈。", ["路线选中态统一", "缺少材料明确灰化", "心魔雷劫概率可读"], _breakthrough),
    ("crafts", "修仙百艺", "验证配方材料、成功率和制作入口。", ["配方可快速比较", "缺少材料自动锁定", "制作会推进时间"], _crafts),
    ("cave", "洞天经营", "查看洞府灵蕴、运转方针、后台生产与设施营造。", ["灵蕴与月度产量清楚", "后台工坊展示真实工期", "设施、方针与配方分层收纳"], _cave),
    ("world", "九州天下", "检查势力、民生、世界阶段和大事记。", ["世界状态不挤占主剧情", "势力数值易比较", "旧事件按需展开"], _action("天下")),
    ("arts", "道法构筑", "查看主修、辅修、法术与装备信息。", ["构筑关系应结构化", "未装备内容不占大段文字", "后续可扩展装备详情"], _action("道法")),
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
