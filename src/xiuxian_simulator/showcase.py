from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Callable

from .engine import GameEngine
from .narrator import LocalNarrator
from .save_manager import SaveManager
from .webapp import WebApplication
from .commissions import CommissionEngine


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
    return app.perform_action("情缘")


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
    engine.state.cave_facilities.update({"静室": 1, "灵田": 1})
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


SHOWCASE_PAGES: tuple[tuple[str, str, str, list[str], PageSetup], ...] = (
    ("home", "洞府主界面", "查看新版三栏结构、根基状态和自由行动入口。", ["核心事件应最醒目", "属性数值应一眼可读", "未开放行动需要灰化"], _ready),
    ("journey", "道途章程", "检查长期目标、完成状态和分章奖励。", ["主界面只显示紧凑进度", "展开后四章结构清楚", "巡览中的领取按钮必须禁用"], _journey),
    ("commissions", "东洲悬榜", "检查委托接取、真实进度、期限与交付报酬。", ["在途与可接委托清楚分层", "完成进度来自规则引擎", "巡览中所有操作必须禁用"], _commissions),
    ("map", "东洲探索", "验证地点风险、境界准入和响应式地图卡。", ["危险度含义明确", "高境界地点自动锁定", "地点增加后自动换行"], _action("地图")),
    ("market", "青岳坊市", "验证分类货架、购买能力和持有数量。", ["货物不再堆成长文字", "买卖价格可直接比较", "灵石不足时按钮禁用"], _action("坊市")),
    ("sects", "宗门择路", "查看各宗门的独立身份卡与试炼入口。", ["宗门气质容易区分", "试炼后果有提示", "按钮接入真实行动"], _action("宗门")),
    ("relations", "人物牵绊", "验证人物组件、好感和关系路径。", ["人物信息拆成小组件", "关系层级清楚", "长身份不挤成一行"], _relations),
    ("battle", "临阵抉择", "查看战前敌情和所有可点击战斗抉择。", ["敌我风险明确", "危险操作视觉统一", "选择按钮状态清楚"], _battle),
    ("realms", "九州秘境", "验证秘境危险度、准入境界和确认流程。", ["致命区域必须锁定", "描述与操作分层", "进入前仍有二次确认"], _action("秘境")),
    ("breakthrough", "筑基之门", "检查三条突破路线的材料和风险反馈。", ["路线选中态统一", "缺少材料明确灰化", "心魔雷劫概率可读"], _breakthrough),
    ("crafts", "修仙百艺", "验证配方材料、成功率和制作入口。", ["配方可快速比较", "缺少材料自动锁定", "制作会推进时间"], _crafts),
    ("cave", "洞府营造", "查看设施等级、升级消耗和灵田操作。", ["设施等级组件化", "升级条件真实计算", "灵田操作集中展示"], _cave),
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
