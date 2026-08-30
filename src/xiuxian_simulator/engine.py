from __future__ import annotations

from .character_creation import BasicCharacter, CharacterCreationError, CharacterCreator
from .adventures import AdventureEngine, SECRET_REALMS
from .arts import ARTIFACTS, ArtsEngine
from .combat import ENEMIES, CombatEngine
from .crafting import FACILITIES, RECIPES, SKILL_NAMES, CraftingEngine
from .relationships import NPCS, RelationshipEngine
from .economy import AREA_DESCRIPTIONS, AREA_REGIONS, AREAS, SECTS, SECT_TASKS, EconomyEngine
from .ecology import NpcEcologyEngine
from .npc_lifecycle import NpcLifecycleEngine
from .npc_network import NpcNetworkEngine
from .world import SectProgressionEngine, SectWarEngine, WorldEvolutionEngine, WorldTimelineEngine
from .narrator import Narrator
from .journey import JourneyEngine
from .commissions import CommissionEngine
from .story import StoryEngine
from .new_era import NewEraEngine
from .dao import DaoEngine
from .items import InventoryEngine
from .auctions import AuctionEngine
from .travel import REGIONS, TravelEngine
from .regional import RegionalEngine
from .cave import CaveEngine
from .progression import ProgressionEngine
from .rules import RuleBook
from .save_manager import SaveManager
from .state import GameState


COMMANDS = "面板 主线 新世 道途 委托 修炼 突破 悟道 洞府 地图 九州 行旅 地方 秘境 背包 坊市 宗门 护宗战 天下 干预天下 战斗 技艺 情缘 情劫 世情 人脉 对话 存档 帮助"


class GameEngine:
    def __init__(
        self,
        rules: RuleBook,
        saves: SaveManager,
        narrator: Narrator,
        autosave_name: str = "autosave",
    ) -> None:
        self.rules = rules
        self.saves = saves
        self.narrator = narrator
        self.autosave_name = autosave_name
        self.state = GameState(rule_sha256=rules.sha256)

    def process(self, raw_action: str) -> str:
        action = raw_action.strip()
        if not action:
            return "请输入行动；也可输入“帮助”查看指令。"

        if action == "开始游戏":
            return self._start_game()
        if action in {"帮助", "指令"}:
            return self._help()
        if action == "面板":
            return self._status()
        if action == "叙事器":
            return f"当前叙事器：{self.narrator.name}"
        if action.startswith("存档"):
            return self._save(action)
        if action.startswith("读档"):
            return self._load(action)

        if self.state.phase == "combat_ready":
            return self._combat_ready(action)
        if self.state.phase == "combat":
            return self._combat_action(action)
        if self.state.phase == "combat_loot":
            return self._combat_loot(action)
        if self.state.phase == "major_breakthrough_choice":
            return self._major_breakthrough_choice(action)
        if self.state.phase == "breakthrough_talent_choice":
            return self._handle_destiny_choice(action)
        if self.state.phase == "adventure_ready":
            return self._adventure_ready(action)
        if self.state.phase == "adventure":
            return self._adventure_action(action)
        if self.state.phase == "sect_defection_ready":
            return self._sect_defection_ready(action)
        if self.state.phase == "heart_trial_choice":
            return self._heart_trial_choice(action)
        if self.state.phase == "sect_war_choice":
            return self._sect_war_choice(action)
        if self.state.phase == "world_intervention_choice":
            return self._world_intervention_choice(action)
        if self.state.phase == "main_story_choice":
            return self._story_choice(action)
        if self.state.phase == "new_era_choice":
            return self._new_era_choice(action)
        if self.state.phase == "auction_choice":
            return self._auction_choice(action)
        if self.state.phase == "travel_choice":
            return self._travel_choice(action)
        if self.state.phase == "regional_choice":
            return self._regional_choice(action)

        if self.state.phase == "new":
            return "世界尚未开启。请先输入“开始游戏”。"
        if self.state.phase in {"character_creation", "character_creation_basic"}:
            return self._handle_basic_creation(action)
        if self.state.phase == "character_creation_traits":
            return self._handle_trait_creation(action)
        if self.state.phase == "ended":
            return "此世已终。输入“开始游戏”可创建新的轮回。"
        if action in {"道途", "章程", "历练"}:
            return JourneyEngine.panel_text(self.state)
        if action in {"主线", "因果", "主线卷宗"}:
            return StoryEngine.panel_text(self.state)
        if action == "推进主线":
            return self._begin_story()
        if action in {"新世", "新世卷宗", "灵潮余波"}:
            return NewEraEngine.panel_text(self.state)
        if action == "处置余波":
            return self._begin_new_era_event()
        if action in {"悟道", "悟道树", "悟道九途", "大道"}:
            return DaoEngine.panel_text(self.state)
        if action == "观想":
            return self._contemplate()
        if action in {"闭关悟道", "消化感悟"}:
            return self._digest_insight()
        if action.startswith("点亮"):
            return self._enlighten_dao(action)
        if action.startswith("领取道途奖励"):
            return self._claim_journey(action)
        if action in {"委托", "悬赏", "悬榜"}:
            return CommissionEngine.panel_text(self.state)
        if action.startswith("接取委托"):
            return self._accept_commission(action)
        if action.startswith("交付委托"):
            return self._deliver_commission(action)
        if action.startswith("放弃委托"):
            return self._abandon_commission(action)
        if action == "修炼":
            return self._cultivate(retreat=False)
        if action == "闭关":
            return self._cultivate(retreat=True)
        retreat_months = ProgressionEngine.parse_retreat_months(action)
        if retreat_months is not None:
            return self._cultivate(retreat=True, months=retreat_months)
        if action.startswith("突破"):
            return self._breakthrough(action)
        if action in {"背包", "资源"}:
            return self._resources()
        if action.startswith("使用"):
            return self._use_item(action)
        if action in {"地图", "九州", "行旅"}:
            return self._map()
        if action in {"地方", "声望", "五域声名"}:
            return RegionalEngine.panel_text(self.state)
        if action in {"地方机缘", "触发机缘"}:
            return self._begin_regional_encounter()
        if action.startswith("前往 "):
            return self._prepare_travel(action)
        if action.startswith("探索"):
            return self._explore(action)
        if action == "秘境":
            return self._secret_realms()
        if action.startswith("进入秘境"):
            return self._prepare_adventure(action)
        trade = EconomyEngine.parse_trade(action)
        if trade is not None:
            return self._trade(*trade)
        if action == "坊市":
            return self._market()
        if action in {"拍卖会", "天机拍卖", "拍卖"}:
            return AuctionEngine.panel_text(self.state)
        if action.startswith("竞拍"):
            return self._begin_auction_bid(action)
        if action == "宗门":
            return self._sect()
        if action == "申请晋升":
            return self._sect_promotion()
        if action == "宗门大比":
            return self._sect_tournament()
        if action == "叛宗":
            return self._prepare_defection()
        if action in {"护宗战", "宗门战"}:
            return self._prepare_sect_war()
        if action.startswith("拜入"):
            return self._join_sect(action)
        if action.startswith("宗门任务"):
            return self._sect_task(action)
        if action in {"天下", "大事记"}:
            return self._world_timeline()
        if action == "干预天下":
            return self._prepare_world_intervention()
        if action in {"道法", "功法", "法术", "法宝"}:
            return self._arts()
        if action.startswith("参悟"):
            return self._learn_art(action)
        if action.startswith("装备功法"):
            return self._equip_main_technique(action)
        if action.startswith("辅修功法"):
            return self._equip_auxiliary_technique(action)
        if action.startswith("装备法术"):
            return self._equip_spell(action)
        if action.startswith("装备法宝"):
            return self._equip_artifact(action)
        if action.startswith("卸下法宝"):
            return self._unequip_artifact(action)
        if action == "技艺":
            return self._crafts()
        if action.startswith("炼丹"):
            return self._craft(action, "炼丹", "炼丹")
        if action.startswith("炼器"):
            return self._craft(action, "炼器", "炼器")
        if action.startswith("制符"):
            return self._craft(action, "制符", "符箓")
        if action == "洞府":
            return self._cave()
        if action.startswith("洞府方针"):
            return self._set_cave_focus(action)
        if action.startswith("洞府生产"):
            return self._queue_cave_production(action)
        if action.startswith("取消洞府生产"):
            return self._cancel_cave_production(action)
        if action == "洞府调息":
            return self._cave_recuperate()
        if action.startswith("升级洞府"):
            return self._upgrade_cave(action)
        if action.startswith("种植"):
            return self._plant(action)
        if action.startswith("收获"):
            return self._harvest(action)
        if action in {"情缘", "人物"}:
            return self._relationships()
        if action == "情劫":
            return self._prepare_heart_trial()
        if action in {"世情", "人物动态"}:
            return self._npc_world()
        if action in {"人脉", "缘网", "众生缘网"}:
            return self._npc_network()
        if action.startswith("介入人情"):
            return self._intervene_network(action)
        if action.startswith("回应"):
            return self._respond_invitation(action)
        if action.startswith("护道"):
            return self._guard_npc(action)
        if action.startswith("确立关系"):
            return self._set_relation_path(action)
        if action.startswith("对话"):
            return self._talk(action)
        if action.startswith("送礼"):
            return self._gift(action)
        if action.startswith("论道"):
            return self._discuss_dao(action)
        if action.startswith("结为道侣"):
            return self._become_partners(action)
        if action.startswith("双修"):
            return self._dual_cultivate(action)
        if action == "战斗":
            return self._combatants()
        if action.startswith("挑战"):
            return self._prepare_combat(action, "生死")
        if action.startswith("切磋"):
            return self._prepare_combat(action, "切磋")

        return self._free_action(action)

    def _start_game(self) -> str:
        self.state = GameState(phase="character_creation_basic", turn=1, rule_sha256=self.rules.sha256)
        self.state.remember("九州仙途开启，等待创角")
        self._autosave()
        return (
            "天玄历 387 年 · 春\n\n"
            "灵气潮汐将至，九州诸宗暗流涌动。你尚是芸芸众生之一，长生路从今日起。\n\n"
            "【创角大面板 · 第一面｜作者：雾见川】\n"
            "基础：姓名、性别、年龄、相貌\n"
            "出身：山野遗孤／修仙世家／凡人皇族／商贾之家／宗门弃徒等\n"
            "道途：问道飞升／逍遥长生／快意恩仇／守护所爱／问鼎天下／随心所欲\n\n"
            "【创角大面板 · 第二面】\n"
            "灵根、体质、六维 60 点、天赋 5 点\n\n"
            "输入“确认默认创角”快速试玩；自定义请按以下格式填写第一面：\n"
            "姓名=林渡；性别=女；年龄=18；相貌=清冷出众；出身=8；道途=问道飞升"
        )

    def _handle_basic_creation(self, action: str) -> str:
        if action == "确认默认创角":
            self.state.player = CharacterCreator.default_player()
            return self._complete_character_creation("默认创角")
        try:
            basic = CharacterCreator.parse_basic(action)
        except CharacterCreationError as exc:
            return f"【创角校验未通过】{exc}\n请修正第一面后重新提交。"
        self.state.character_draft = basic.to_dict()
        self.state.phase = "character_creation_traits"
        self._autosave()
        return (
            f"第一面已确认：{basic.name}，{basic.gender}，{basic.age} 岁，{basic.background}，道途“{basic.dao_path}”。\n\n"
            "【创角大面板 · 第二面】\n"
            "灵根：天/地/真/伪/变异灵根，可写具体属性\n"
            "体质：先天道体／剑灵体／九阳圣体／冰魄灵体／玄阴体／纯阳体／混沌体／凡体\n"
            "六维：资质、悟性、神识、遁速、道心、仙缘；单项 1~15，合计必须为 60\n"
            "天赋：正面天赋各耗 1 点；体弱多病返还 2 点；最终必须正好使用 5 点\n\n"
            "示例：灵根=木火双灵根；体质=凡体；资质=10；悟性=10；神识=10；"
            "遁速=10；道心=10；仙缘=10；天赋=天资聪颖、过目不忘、身轻如燕、天生道心、气运加身"
        )

    def _handle_trait_creation(self, action: str) -> str:
        try:
            basic = BasicCharacter.from_dict(self.state.character_draft)
            self.state.player = CharacterCreator.finish(basic, action)
        except (CharacterCreationError, KeyError, TypeError, ValueError) as exc:
            return f"【创角校验未通过】{exc}\n请修正第二面后重新提交。"
        return self._complete_character_creation("自定义创角")

    def _complete_character_creation(self, source: str) -> str:
        self.state.phase = "playing"
        self.state.character_draft = {}
        self.state.remember(f"创角完成：{source}；{self.state.player.character_notes}")
        self._autosave()
        return (
            "创角完成。出身、体质与天赋加成已写入结构化状态。\n\n"
            + self._status()
            + "\n\n【洞府主界面】\n石屋一间，灵气普通，设施尚无。你可修炼、外出或自由行动。"
        )

    def _cultivate(self, retreat: bool, months: int = 1) -> str:
        player = self.state.player
        gain, breakdown, months_used = ProgressionEngine.cultivate(self.state, months=months, retreat=retreat)
        if months_used == 0:
            return f"修为已圆满：{player.cultivation}/{player.cultivation_required}。请先尝试突破。"
        dao_points = DaoEngine.digest(self.state, limit=months_used, required=False) if retreat else 0
        CommissionEngine.mark(self.state, "cultivation_month", months_used)
        died_of_age = self._advance_time(months_used)
        mode = "闭关" if retreat else "吐纳"
        dao_note = f"，悟道点 +{dao_points}" if dao_points else ""
        self.state.remember(f"{mode}修炼 {months_used} 月，修为 +{gain}{dao_note}")
        if died_of_age:
            self.state.phase = "ended"
            self.state.remember("寿元耗尽，坐化")
        self._autosave()
        if died_of_age:
            return (
                f"{self.state.time_label}\n岁月无声，你在闭关中走到了寿元尽头。\n"
                f"【坐化结局】享年 {player.age} 岁，境界 {player.realm}。"
            )
        early_stop = "，修为圆满后自动出关" if months_used < months else ""
        return (
            f"{self.state.time_label}\n你在石屋中{mode}{months_used}月{early_stop}，灵气沿经脉缓缓流转。\n"
            f"修为 +{gain}（{player.cultivation}/{player.cultivation_required}）\n"
            + (f"感悟化真：悟道点 +{dao_points}\n" if dao_points else "")
            + f"结算：{breakdown.summary()}／月\n\n"
            + self._status()
        )

    def _contemplate(self) -> str:
        try:
            gain = DaoEngine.contemplate(self.state)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        self.state.remember(f"静坐观想，感悟 +{gain}")
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "观想中寿元耗尽"
        self._autosave()
        if died_of_age:
            return "你在天地道韵中坐忘此身，寿元也在此刻走到尽头。\n【坐化结局】"
        return (
            f"{self.state.time_label}\n【静坐观想】灵力 -10，感悟 +{gain}，"
            f"当前 {self.state.player.dao_insight}/{20}。\n\n{DaoEngine.panel_text(self.state)}"
        )

    def _digest_insight(self) -> str:
        try:
            points = DaoEngine.digest(self.state, limit=3)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        self.state.remember(f"闭关消化感悟，悟道点 +{points}")
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "悟道中寿元耗尽"
        self._autosave()
        if died_of_age:
            return "大道似有所得，你却已走到此世尽头。\n【坐化结局】"
        return f"{self.state.time_label}\n感悟凝成悟道点 +{points}。\n\n{DaoEngine.panel_text(self.state)}"

    def _enlighten_dao(self, action: str) -> str:
        branch = action.removeprefix("点亮").strip()
        try:
            level = DaoEngine.enlighten(self.state, branch)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"点亮{branch}第 {level} 层")
        self._autosave()
        return f"【悟道有成】{branch}已达第 {level} 层。\n\n{DaoEngine.panel_text(self.state)}"

    def _free_action(self, action: str) -> str:
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.remember("寿元耗尽，坐化")
            self._autosave()
            return f"{self.state.time_label}\n你在行动途中寿元耗尽。\n【坐化结局】享年 {self.state.player.age} 岁。"
        narrative = self.narrator.narrate(action, self.state)
        encounter = AdventureEngine.random_encounter(self.state, action)
        event_text = ""
        if encounter.triggered:
            event_text = f"\n\n【随机奇遇 · {encounter.title}】\n{encounter.description}\n判定：1d100={encounter.roll}（20%触发）"
        self.state.remember(action + (f"；奇遇：{encounter.title}" if encounter.triggered else ""))
        self._autosave()
        return f"{self.state.time_label}\n{narrative}{event_text}\n\n{self._status()}"

    def _breakthrough(self, action: str) -> str:
        player = self.state.player
        ProgressionEngine.sync_realm(player)
        if player.breakthrough_cooldown_months > 0:
            return f"突破反噬尚未平复，还需休养 {player.breakthrough_cooldown_months} 个月。"
        if player.stage_index == 3:
            parts = action.split(maxsplit=1)
            if len(parts) == 1:
                lines = []
                for route in ("人道", "地道", "天道"):
                    requirements = ProgressionEngine.major_requirements(player, route)
                    needs = "、".join(f"{name}×{count}" for name, count in requirements.items())
                    lines.append(f"{route}：{needs}")
                self.state.phase = "major_breakthrough_choice"
                self._autosave()
                return "【大境界突破路线】\n" + "\n".join(lines) + "\n输入：突破 人道／突破 地道／突破 天道"
            route = parts[1].strip()
            try:
                result = ProgressionEngine.major_breakthrough(self.state, route)
            except ValueError as exc:
                return str(exc)
            self._advance_time()
            if result.success:
                choices = ProgressionEngine.destiny_choices(self.state)
                self.state.pending_choices = choices
                self.state.phase = "breakthrough_talent_choice"
                self.state.remember(f"{route}突破成功：{result.old_realm} → {result.new_realm}")
                self._autosave()
                options = "\n".join(f"{index}. {trait}" for index, trait in enumerate(choices, 1))
                return (
                    f"{self.state.time_label}\n{route}突破成功：{result.old_realm} → {result.new_realm}\n"
                    f"心魔劫 {result.heart_roll}/{result.heart_chance}｜雷劫 {result.thunder_roll}/{result.thunder_chance}\n\n"
                    f"【逆天改命 · 三选一】\n{options}\n输入：选择 1（或直接输入天资名称）"
                )
            self.state.remember(
                f"{route}突破失败：{result.failure_type}；心魔 {result.heart_roll}/{result.heart_chance}；"
                f"雷劫 {result.thunder_roll}/{result.thunder_chance}"
            )
            self._autosave()
            if result.fatal:
                return (
                    f"{self.state.time_label}\n{route}突破失败，{result.failure_type}将你吞没。\n"
                    f"【陨落结局】{result.old_realm}，道途止于此地。"
                )
            return (
                f"{self.state.time_label}\n{route}突破失败：败于{result.failure_type}。\n"
                f"心魔劫 {result.heart_roll}/{result.heart_chance}｜雷劫 {result.thunder_roll}/{result.thunder_chance}\n\n"
                + self._status()
            )
        try:
            result = ProgressionEngine.small_breakthrough(self.state)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.remember("突破期间寿元耗尽，坐化")
            self._autosave()
            return f"突破尚未落定，你已寿元耗尽。\n【坐化结局】享年 {player.age} 岁。"
        if result.success:
            message = f"突破成功：{result.old_realm} → {result.new_realm}，修为归零。"
        else:
            message = f"突破失败：修为跌回 70%，当前 {result.cultivation_after}/{player.cultivation_required}。"
        self.state.remember(f"{message} 掷骰 {result.roll}/{result.chance}")
        self._autosave()
        return f"{self.state.time_label}\n{message}\n判定：1d100={result.roll}，成功率 {result.chance}%\n\n{self._status()}"

    def _major_breakthrough_choice(self, action: str) -> str:
        if action == "取消突破":
            self.state.phase = "playing"
            self._autosave()
            return "你暂且收拢灵力，没有消耗任何破境资源。\n\n" + self._status()
        if action not in {"突破 人道", "突破 地道", "突破 天道"}:
            return "请选择人道、地道或天道路线，也可选择“取消突破”。"
        self.state.phase = "playing"
        return self._breakthrough(action)

    def _handle_destiny_choice(self, action: str) -> str:
        text = action.strip()
        selected = ""
        number = text.removeprefix("选择").strip()
        if number.isdigit():
            index = int(number)
            if 1 <= index <= len(self.state.pending_choices):
                selected = self.state.pending_choices[index - 1]
        elif text in self.state.pending_choices:
            selected = text
        if not selected:
            options = "、".join(f"{index}.{trait}" for index, trait in enumerate(self.state.pending_choices, 1))
            return f"请选择本次逆天改命：{options}"
        ProgressionEngine.apply_destiny_trait(self.state.player, selected)
        self.state.pending_choices = []
        self.state.phase = "playing"
        self.state.remember(f"获得逆天改命：{selected}")
        self._autosave()
        return f"你选择了逆天改命【{selected}】。\n\n{self._status()}"

    def _resources(self) -> str:
        resources = self.state.player.resources
        lines = "\n".join(f"{name} × {count}" for name, count in sorted(resources.items())) or "暂无突破资源"
        return (
            f"【乾坤袋 · 万象藏品】\n{lines}\n"
            f"普通物品：{'、'.join(self.state.player.inventory) if self.state.player.inventory else '无'}\n"
            "可在乾坤袋详情中查看用途并直接使用、装备或卸下。"
        )

    def _use_item(self, action: str) -> str:
        name = action.removeprefix("使用").strip()
        if not name:
            return "请选择要使用的物品。"
        try:
            result = InventoryEngine.use(self.state, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"使用{name}：{result}")
        self._autosave()
        return f"【使用 · {name}】\n{result}\n\n{self._status()}"

    def _map(self) -> str:
        current_region = TravelEngine.current_region(self.state)
        region = REGIONS[current_region]
        atlas = "\n".join(TravelEngine.atlas_lines(self.state))
        lines = []
        for name, (minimum_realm, danger) in AREAS.items():
            if AREA_REGIONS[name] != current_region:
                continue
            realm_hint = TravelEngine.requirement_label(minimum_realm)
            lines.append(f"{name}｜{realm_hint}｜危险度 {danger}｜{AREA_DESCRIPTIONS[name]}")
        return (
            f"【九州舆图】\n{atlas}\n输入：前往 中州（随后选择商队或御风）\n\n"
            f"【当地探索 · {region.name}】\n" + "\n".join(lines) + f"\n输入：探索 {lines and lines[0].split('｜', 1)[0] or '当地'}"
        )

    def _prepare_travel(self, action: str) -> str:
        destination = action.removeprefix("前往").strip()
        try:
            route = TravelEngine.prepare(self.state, destination)
        except ValueError as exc:
            return str(exc)
        origin = REGIONS[str(route["origin"])].name
        target = REGIONS[str(route["destination"])].name
        self.state.remember(f"规划跨域行程：{origin} → {target}")
        self._autosave()
        return (
            f"【行旅抉择 · {origin}至{target}】\n"
            f"直线行程约 {route['distance']} 个月；远行期间寿元、委托期限与天下局势都会照常推进。\n"
            "可随商队同行求稳，也可御风独行赶路；请亲自选择。"
        )

    def _travel_choice(self, action: str) -> str:
        raw = action.removeprefix("行旅选择").strip() if action.startswith("行旅选择") else action
        aliases = {"随商队同行": "caravan", "商队": "caravan", "御风独行": "swift", "御风": "swift", "暂不启程": "cancel", "取消": "cancel"}
        method = aliases.get(raw, raw)
        try:
            result = TravelEngine.resolve(self.state, method)
        except ValueError as exc:
            return str(exc)
        if result is None:
            self.state.remember("取消跨域行程")
            self._autosave()
            return "你收起舆图，暂时留在原地；没有消耗时间或资源。\n\n" + self._status()

        died_of_age = self._advance_time(result.months)
        if died_of_age and not result.fatal:
            self.state.phase = "ended"
            self.state.player.condition = "跨域途中寿元耗尽"
        cost = f"灵石 -{result.stone_cost}" if result.stone_cost else f"灵力 -{result.spirit_cost}"
        injury = f"｜气血 -{result.health_loss}" if result.health_loss else ""
        destination = REGIONS[result.destination].name
        event = f"跨域抵达{destination}：{result.method}，历时{result.months}月，{cost}{injury}"
        if died_of_age and not result.fatal:
            self.state.player.location = f"{REGIONS[result.origin].name}至{destination}商路"
            self.state.remember(f"跨域途中寿元耗尽：{REGIONS[result.origin].name} → {destination}")
            self._autosave()
            return f"【跨域行旅 · 坐化】\n你未能走到{destination}，寿元已在漫长旅途中耗尽。"
        if result.fatal:
            self.state.remember(f"跨域途中陨落：{REGIONS[result.origin].name} → {destination}")
            self._autosave()
            return (
                f"【跨域行旅 · 陨落】\n{result.event}\n"
                f"判定 {result.roll}/{result.chance}｜气血 -{result.health_loss}\n道途止于商路荒野。"
            )
        CommissionEngine.mark(self.state, "cross_region_travel")
        arrival_reputation = RegionalEngine.record_arrival(self.state, result.destination, result.first_visit)
        regional_event = RegionalEngine.prepare(self.state, result.destination)
        self.state.remember(event)
        self._autosave()
        reputation_text = f"｜{result.destination}声望 +{arrival_reputation}" if arrival_reputation else ""
        encounter_text = f"\n\n{RegionalEngine.encounter_text(self.state, result.destination)}" if regional_event else ""
        return (
            f"{self.state.time_label}\n【跨域行旅 · 抵达{destination}】\n"
            f"{result.method}｜历时 {result.months} 月｜{cost}{reputation_text}\n"
            f"{result.event}\n判定 {result.roll}/{result.chance}{injury}\n\n"
            f"【当地行情】\n特产：{'、'.join(REGIONS[result.destination].specialties)}\n"
            f"求购：{'、'.join(REGIONS[result.destination].demands)}\n"
            "可打开坊市比较价格，或查看地图探索当地险地。"
            f"{encounter_text}"
        )

    def _begin_regional_encounter(self) -> str:
        event = RegionalEngine.prepare(self.state)
        if event is None:
            return RegionalEngine.panel_text(self.state)
        region = RegionalEngine.current_region(self.state)
        self.state.remember(f"{region}地方机缘《{event['title']}》浮现")
        self._autosave()
        return RegionalEngine.encounter_text(self.state, region)

    def _regional_choice(self, action: str) -> str:
        raw = action.removeprefix("地方选择").strip() if action.startswith("地方选择") else action
        try:
            result = RegionalEngine.resolve(self.state, raw)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        effect_text = "、".join(result.effects)
        self.state.remember(f"{result.region}《{result.title}》选择{result.choice}：{effect_text}")
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "地方机缘后寿元耗尽"
        self._autosave()
        ending = "\n你在此事落定后寿元耗尽，道途止于此地。" if died_of_age else ""
        return (
            f"{self.state.time_label}\n【地方机缘 · {result.title}】\n"
            f"你选择了“{result.choice}”。\n结算：{effect_text}\n"
            f"当前{result.region}评价：{RegionalEngine.rank(self.state, result.region)} "
            f"({RegionalEngine.reputation(self.state, result.region):+d}){ending}"
        )

    def _explore(self, action: str) -> str:
        area = action.removeprefix("探索").strip()
        if not area:
            current_region = TravelEngine.current_region(self.state)
            area = next(name for name in AREAS if AREA_REGIONS[name] == current_region)
        region_key = TravelEngine.current_region(self.state)
        reputation_before = RegionalEngine.reputation(self.state, region_key)
        try:
            result = EconomyEngine.explore(self.state, area)
        except ValueError as exc:
            return str(exc)
        CommissionEngine.mark(self.state, "exploration")
        died_of_age = self._advance_time()
        rewards = [f"灵石 +{result.spirit_stones}"] if result.spirit_stones else []
        rewards.extend(f"{name} +{count}" for name, count in result.rewards.items())
        if result.health_loss:
            rewards.append(f"气血 -{result.health_loss}")
        reward_text = "、".join(rewards) if rewards else "无"
        reputation_change = RegionalEngine.reputation(self.state, region_key) - reputation_before
        if reputation_change:
            reward_text += f"、{region_key}声望 {reputation_change:+d}"
        self.state.remember(f"探索{result.area}：{result.event}；收获 {reward_text}")
        if died_of_age and not result.fatal:
            self.state.phase = "ended"
            self.state.player.condition = "寿元耗尽"
        if result.encounter and self.state.phase != "ended":
            CombatEngine.prepare(self.state, result.encounter, mode="生死", source="exploration")
            self._autosave()
            return (
                f"{self.state.time_label}\n【探索 · {result.area}】\n{result.event}\n"
                f"判定：1d100={result.roll}\n\n{CombatEngine.enemy_panel(self.state)}"
            )
        self._autosave()
        if self.state.phase == "ended":
            ending = "寿元耗尽，坐化荒野" if died_of_age and not result.fatal else result.event
            return f"{self.state.time_label}\n{ending}。\n【陨落结局】道途止于 {result.area}。"
        regional_event = RegionalEngine.prepare(self.state, region_key)
        if regional_event:
            self._autosave()
        encounter_text = f"\n\n{RegionalEngine.encounter_text(self.state, region_key)}" if regional_event else ""
        return (
            f"{self.state.time_label}\n【探索 · {result.area}】\n{result.event}\n"
            f"判定：1d100={result.roll}｜收获：{reward_text}\n\n{self._status()}{encounter_text}"
        )

    @staticmethod
    def _secret_realms() -> str:
        return (
            "【九州秘境】\n"
            + "\n".join(AdventureEngine.list_lines())
            + "\n输入：进入秘境 通灵秘境。进入前会再次显示危险并要求确认。"
        )

    def _prepare_adventure(self, action: str) -> str:
        name = action.removeprefix("进入秘境").strip()
        try:
            realm = AdventureEngine.prepare(self.state, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"抵达{realm.name}入口，尚待决定是否进入")
        self._autosave()
        return (
            f"【秘境入口 · {realm.name}】\n{realm.description}\n"
            f"危险度 {realm.danger}｜共三阶段：外围、阵法核心、传承深处。\n"
            "进入后每次探索推进一个月；失败会重伤或陨落，强行探索奖励更高但成功率更低。\n"
            "输入“确认进入”踏入秘境，或输入“离开”返回。"
        )

    def _adventure_ready(self, action: str) -> str:
        if action == "离开":
            name = self.state.adventure.get("name", "秘境")
            AdventureEngine.cancel(self.state)
            self.state.remember(f"在{name}入口选择离开")
            self._autosave()
            return "你审慎退离秘境入口，本次没有推进时间。\n\n" + self._status()
        if action != "确认进入":
            return "秘境入口尚待抉择：输入“确认进入”或“离开”。"
        name = self.state.adventure["name"]
        AdventureEngine.confirm(self.state)
        self.state.remember(f"确认进入{name}")
        self._autosave()
        return (
            f"你踏入{name}，身后的入口随即闭合。\n"
            f"当前阶段：{AdventureEngine.STAGE_NAMES[0]}。\n"
            "输入“谨慎探索”“强行探索”或“退出秘境”。"
        )

    def _adventure_action(self, action: str) -> str:
        name = self.state.adventure.get("name", "秘境")
        if action == "退出秘境":
            rewards, stones = AdventureEngine.leave(self.state)
            reward_text = "、".join(f"{item}×{count}" for item, count in rewards.items()) or "无"
            self.state.remember(f"从{name}中途退出，带回{reward_text}与灵石{stones}")
            self._autosave()
            return f"你激活退路离开{name}。\n带回：{reward_text}｜灵石 +{stones}。\n\n{self._status()}"
        if action not in {"谨慎探索", "强行探索"}:
            return "秘境中只能选择“谨慎探索”“强行探索”或“退出秘境”。"
        stage_name = AdventureEngine.STAGE_NAMES[int(self.state.adventure.get("stage", 0))]
        result = AdventureEngine.resolve(self.state, action)
        died_of_age = self._advance_time()
        if died_of_age and not result.fatal:
            self.state.phase = "ended"
            self.state.player.condition = "寿元耗尽"
        if result.success:
            reward_text = "、".join(f"{item}+{count}" for item, count in result.rewards.items())
            event = f"{name}{stage_name}{action}成功，获得{reward_text}与灵石{result.spirit_stones}"
        else:
            event = f"{name}{stage_name}{action}失败，气血-{result.health_loss}"
        self.state.remember(event)
        self._autosave()
        if died_of_age and not result.fatal:
            return f"{self.state.time_label}\n你在秘境中耗尽寿元。\n【坐化结局】"
        if not result.success:
            ending = "\n【陨落结局】秘境吞没了你的道途。" if result.fatal else "\n你被秘境排斥而出，尚可养伤再来。"
            return (
                f"{self.state.time_label}\n【{stage_name} · 失败】判定 {result.roll}/{result.chance}\n"
                f"气血 -{result.health_loss}，当前 {self.state.player.health}/{self.state.player.health_max}。{ending}"
            )
        reward_text = "、".join(f"{item}+{count}" for item, count in result.rewards.items())
        if result.completed:
            return (
                f"{self.state.time_label}\n【{stage_name} · 秘境通关】判定 {result.roll}/{result.chance}\n"
                f"本阶段：{reward_text}、灵石 +{result.spirit_stones}；全部积累已安全收入乾坤袋。\n\n{self._status()}"
            )
        next_stage = AdventureEngine.STAGE_NAMES[result.stage]
        return (
            f"{self.state.time_label}\n【{stage_name} · 成功】判定 {result.roll}/{result.chance}\n"
            f"本阶段暂存：{reward_text}、灵石 +{result.spirit_stones}。\n"
            f"下一阶段：{next_stage}。可继续谨慎/强行探索，或退出秘境带走已有收获。"
        )

    def _market(self) -> str:
        region_key = TravelEngine.current_region(self.state)
        region = REGIONS[region_key]
        specialties, demands, profit, standing = EconomyEngine.market_context(self.state)
        return (
            f"【{region.name}坊市】\n"
            f"本地特产：{specialties}｜热门求购：{demands}｜商路盈亏：{profit} 灵石｜地方声望：{standing}\n"
            + "\n".join(EconomyEngine.market_lines(self.state))
            + "\n输入：买 筑基丹／卖 灵药 2（买卖本身不推进月份）"
        )

    def _trade(self, operation: str, item: str, count: int) -> str:
        profit_before = self.state.trade_profit
        region_key = TravelEngine.current_region(self.state)
        reputation_before = RegionalEngine.reputation(self.state, region_key)
        try:
            stone_change, item_change = EconomyEngine.trade(self.state, operation, item, count)
        except ValueError as exc:
            return str(exc)
        CommissionEngine.mark(self.state, "market_trade")
        region = REGIONS[region_key].name
        profit_change = self.state.trade_profit - profit_before
        profit_text = f"｜商路盈亏 {profit_change:+d}" if profit_change else ""
        reputation_change = RegionalEngine.reputation(self.state, region_key) - reputation_before
        reputation_text = f"｜{region_key}声望 {reputation_change:+d}" if reputation_change else ""
        self.state.remember(f"在{region}坊市{operation}{item}×{count}，灵石变动 {stone_change:+d}{profit_text}{reputation_text}")
        self._autosave()
        direction = "+" if item_change > 0 else ""
        return (
            f"【坊市成交】{operation}{item}×{count}\n"
            f"地点 {region}｜灵石 {stone_change:+d}｜{item} {direction}{item_change}{profit_text}{reputation_text}\n"
            f"当前灵石：{self.state.player.spirit_stones}"
        )

    def _begin_auction_bid(self, action: str) -> str:
        lot_id = action.removeprefix("竞拍").strip()
        if not lot_id:
            return "请选择要参与竞拍的拍品。"
        try:
            lot = AuctionEngine.begin(self.state, lot_id)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"为《{lot['name']}》举起竞价玉牌")
        self._autosave()
        return (
            f"【天机竞价 · {lot['name']}】\n"
            f"底价 {lot['reserve']} 灵石｜每次加价 {lot['increment']} 灵石\n"
            f"主要对手：{self.state.auction['competitor']}｜{self.state.auction['competitor_style']}\n"
            "请选择稳健举牌、强势压场或退出竞价。"
        )

    def _auction_choice(self, action: str) -> str:
        strategy = action.removeprefix("拍卖选择").strip() if action.startswith("拍卖选择") else ""
        try:
            lot, won, offer, roll, chance = AuctionEngine.resolve(self.state, strategy)
        except ValueError as exc:
            return str(exc)
        if strategy == "withdraw":
            result = f"你放下竞价玉牌；{lot['winner']}以 {lot['price']} 灵石拍得《{lot['name']}》。"
        elif won:
            reward = "、".join(f"{name}×{count}" for name, count in lot["rewards"].items())
            result = f"落槌成交。你以 {offer} 灵石拍得《{lot['name']}》，所得 {reward} 已收入乾坤袋。\n判定：1d100={roll}，成交机会 {chance}%"
        else:
            result = f"竞价失利。{lot['winner']}以 {lot['price']} 灵石拍得《{lot['name']}》，你没有损失灵石。\n判定：1d100={roll}，成交机会 {chance}%"
        self.state.remember(result.splitlines()[0])
        self._autosave()
        return f"【天机拍卖 · 落槌】\n{result}\n\n{AuctionEngine.panel_text(self.state)}"

    def _sect(self) -> str:
        player = self.state.player
        if player.sect == "散修":
            return (
                "【东洲宗门】\n"
                + "\n".join(f"{sect}｜入门试炼" for sect in SECTS)
                + "\n输入：拜入 青云宗（试炼会推进一个月，可能失败）"
            )
        target, contribution, minimum_realm = SectProgressionEngine.promotion_requirements(self.state)
        promotion = (
            f"下一职位 {target}｜贡献要求 {contribution}｜境界要求 第{minimum_realm + 1}大境界"
            if target
            else "已位列掌门"
        )
        tournament = "本年可参加" if SectProgressionEngine.tournament_available(self.state) else "本年未开放"
        privileges = "、".join(self.state.sect_privileges) or "暂无"
        return (
            f"【{player.sect} · {player.sect_rank}】\n贡献：{player.sect_contribution}｜权限：{privileges}\n"
            f"晋升：{promotion}\n宗门大比：{tournament}\n"
            f"任务：{'、'.join(SECT_TASKS)}\n"
            "指令：宗门任务 采药／申请晋升／宗门大比／叛宗"
        )

    def _sect_promotion(self) -> str:
        try:
            result = SectProgressionEngine.promote(self.state)
        except ValueError as exc:
            return str(exc)
        died = self._advance_time()
        verdict = f"晋升为{result.new_rank}" if result.success else "晋升试炼未获认可"
        self.state.remember(f"宗门晋升：{verdict}；判定{result.roll}/{result.chance}")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "晋升试炼后寿元耗尽"
        self._autosave()
        if died:
            return "晋升试炼结束后，你的寿元也走到尽头。\n【坐化结局】"
        return (
            f"{self.state.time_label}\n【宗门晋升试炼】{verdict}\n"
            f"判定：1d100={result.roll}，成功率 {result.chance}%\n\n{self._sect()}"
        )

    def _sect_tournament(self) -> str:
        try:
            result = SectProgressionEngine.tournament(self.state)
        except ValueError as exc:
            return str(exc)
        died = self._advance_time()
        verdict = "夺得魁首" if result.success else "止步本届大比"
        reward = f"、{result.reward} +1" if result.reward else ""
        self.state.remember(
            f"宗门大比{verdict}；贡献+{result.contribution}、声望+{result.reputation}{reward}"
        )
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "宗门大比后寿元耗尽"
        self._autosave()
        if died:
            return "大比落幕后，你在众人注视中寿元耗尽。\n【坐化结局】"
        return (
            f"{self.state.time_label}\n【宗门大比】{verdict}\n"
            f"判定：1d100={result.roll}，胜率 {result.chance}%｜"
            f"贡献 +{result.contribution}｜声望 +{result.reputation}{reward}\n\n{self._sect()}"
        )

    def _prepare_defection(self) -> str:
        if self.state.player.sect == "散修":
            return "你本就是散修，无宗可叛。"
        self.state.phase = "sect_defection_ready"
        self._autosave()
        return (
            f"【叛宗警告】你将离开{self.state.player.sect}，清空宗门贡献，声望 -30、业力 +5，"
            "并留下可能被追杀的叛宗标记。\n输入“确认叛宗”承担后果，或输入“取消”。"
        )

    def _sect_defection_ready(self, action: str) -> str:
        if action == "取消":
            self.state.phase = "playing"
            self._autosave()
            return "你收回叛宗之念，此事尚未传出。\n\n" + self._sect()
        if action != "确认叛宗":
            return "叛宗是重大决定：请输入“确认叛宗”或“取消”。"
        try:
            old_sect = SectProgressionEngine.defect(self.state)
        except ValueError as exc:
            self.state.phase = "playing"
            return str(exc)
        self.state.phase = "playing"
        died = self._advance_time()
        self.state.remember(f"叛离{old_sect}，成为散修")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "叛宗途中寿元耗尽"
        self._autosave()
        if died:
            return "你逃出宗门，却在荒野中寿元耗尽。\n【坐化结局】"
        return f"{self.state.time_label}\n你已叛离{old_sect}，从此重归散修。\n\n{self._status()}"

    def _world_timeline(self) -> str:
        schedule = "\n".join(WorldTimelineEngine.schedule_lines(self.state))
        recent = "\n".join(self.state.world_events[-8:]) or "尚无足以载入史册的大事"
        factions = "｜".join(
            f"{name} {strength}{'（覆灭）' if name in self.state.fallen_factions else ''}"
            for name, strength in self.state.faction_strengths.items()
        )
        war = self.state.active_sect_war
        war_text = (
            f"{war['attacker']} 对 {war['defender']}｜持续 {war['months']} 月｜声势 {war['momentum']:+d}"
            if war
            else "当前无大规模宗门战争"
        )
        return (
            f"【九州天下 · {self.state.world_era} · 局势 {self.state.world_tension}】\n{schedule}\n\n"
            f"【势力盛衰】\n{factions}\n【宗门战局】{war_text}\n\n"
            f"【五域民生】\n" + "｜".join(f"{name} {value}" for name, value in self.state.regional_prosperity.items()) + "\n\n"
            f"【近期大事记】\n{recent}"
        )

    def _prepare_world_intervention(self) -> str:
        if self.state.player.realm_index < 1:
            return "至少达到筑基境，才有能力干预天下局势。"
        if str(self.state.calendar_year) in self.state.world_interventions:
            return "你本年已经干预过一次天下局势。"
        self.state.phase = "world_intervention_choice"
        self._autosave()
        return (
            f"【干预天下 · {self.state.world_era}】\n"
            "你已不再是只能随波逐流的无名修士。此番可以扶持宗门、赈济苍生，或探查新生灵脉。"
        )

    def _world_intervention_choice(self, action: str) -> str:
        if action == "暂不干预":
            self.state.phase = "playing"
            self._autosave()
            return "你暂且按下此念，继续观察九州局势。\n\n" + self._world_timeline()
        try:
            result = WorldEvolutionEngine.intervene(self.state, action)
        except ValueError as exc:
            return str(exc)
        self.state.phase = "playing"
        died = self._advance_time()
        self.state.remember(f"干预天下：{result.choice}")
        if died:
            self.state.phase = "ended"
        self._autosave()
        return f"{self.state.time_label}\n【干预天下 · {result.choice}】\n{result.description}\n\n{self._world_timeline()}"

    def _prepare_sect_war(self) -> str:
        war = self.state.active_sect_war
        if not war:
            return "当前九州并无正在进行的大规模宗门战争。"
        if self.state.player.sect not in {war.get("attacker"), war.get("defender")}:
            return f"{war['attacker']}与{war['defender']}正在交战，但你的宗门并非参战方。"
        if war.get("player_acted"):
            return "你已经为本次宗门战争作出过选择。"
        self.state.phase = "sect_war_choice"
        self._autosave()
        return (
            f"【护宗战 · {war['attacker']} 对 {war['defender']}】\n"
            f"战事已持续 {war['months']} 月，当前声势 {war['momentum']:+d}。\n"
            "你可以驰援前线、固守山门，或闭关不出避开杀劫。"
        )

    def _sect_war_choice(self, action: str) -> str:
        try:
            result = SectWarEngine.participate(self.state, action)
        except ValueError as exc:
            return str(exc)
        self.state.phase = "playing"
        died = self._advance_time()
        self.state.remember(f"护宗战选择{result.choice}，战局声势{result.momentum:+d}")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "护宗战后寿元耗尽"
        self._autosave()
        if died:
            return result.description + "\n【坐化结局】战火落幕后，你也走完了此生。"
        verdict = "" if result.chance == 100 else f"\n判定：1d100={result.roll}，成功率 {result.chance}%"
        return f"{self.state.time_label}\n【护宗战 · {result.choice}】\n{result.description}{verdict}\n\n{self._world_timeline()}"

    def _join_sect(self, action: str) -> str:
        sect = action.removeprefix("拜入").strip()
        try:
            success, roll, chance = EconomyEngine.join_sect(self.state, sect)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "寿元耗尽"
        message = f"通过入门试炼，成为{sect}外门弟子" if success else f"入门试炼落选，仍为散修"
        self.state.remember(f"{message}；判定 {roll}/{chance}")
        self._autosave()
        if died_of_age:
            return f"试炼尚未结束，你已寿元耗尽。\n【坐化结局】享年 {self.state.player.age} 岁。"
        return f"{self.state.time_label}\n{message}。\n判定：1d100={roll}，成功率 {chance}%\n\n{self._sect()}"

    def _sect_task(self, action: str) -> str:
        task = action.removeprefix("宗门任务").strip()
        try:
            result = EconomyEngine.sect_task(self.state, task)
        except ValueError as exc:
            return str(exc)
        if result.success:
            CommissionEngine.mark(self.state, "sect_task_success")
        died_of_age = self._advance_time()
        rewards = []
        if result.spirit_stones:
            rewards.append(f"灵石 +{result.spirit_stones}")
        if result.contribution:
            rewards.append(f"贡献 +{result.contribution}")
        rewards.extend(f"{name} +{count}" for name, count in result.rewards.items())
        if result.health_loss:
            rewards.append(f"气血 -{result.health_loss}")
        reward_text = "、".join(rewards) if rewards else "无"
        verdict = "任务完成" if result.success else "任务失败"
        self.state.remember(f"宗门{result.task}{verdict}；{reward_text}")
        if died_of_age and not result.fatal:
            self.state.phase = "ended"
            self.state.player.condition = "寿元耗尽"
        self._autosave()
        if self.state.phase == "ended":
            return f"{self.state.time_label}\n宗门任务途中陨落。\n【陨落结局】道途止于{result.task}任务。"
        return (
            f"{self.state.time_label}\n【宗门任务 · {result.task}】{verdict}\n"
            f"判定：1d100={result.roll}，成功率 {result.chance}%｜结算：{reward_text}\n\n{self._status()}"
        )

    @staticmethod
    def _combatants() -> str:
        lines = []
        for enemy in ENEMIES.values():
            lines.append(f"{enemy.name}｜{enemy.realm_index + 1}境·{enemy.stage_index + 1}阶｜五行 {enemy.element}")
        return (
            "【可交手目标】\n"
            + "\n".join(lines)
            + "\n输入：挑战 山野劫修（生死）／切磋 青云宗外门弟子"
        )

    def _prepare_combat(self, action: str, mode: str) -> str:
        prefix = "挑战" if mode == "生死" else "切磋"
        enemy_name = action.removeprefix(prefix).strip()
        if not enemy_name:
            return self._combatants()
        try:
            CombatEngine.prepare(self.state, enemy_name, mode=mode, source="challenge")
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"遭遇{enemy_name}，等待决定是否{mode}")
        self._autosave()
        return CombatEngine.enemy_panel(self.state)

    def _combat_ready(self, action: str) -> str:
        if action == "开战":
            panel = CombatEngine.start(self.state)
            self.state.remember(f"与{self.state.combat['enemy_name']}开战")
            self._autosave()
            return panel
        if action == "离开":
            if self.state.combat.get("source") != "challenge":
                return "这是探索途中被拦截的遭遇，无法直接离开；可选择“遁走”或“开战”。"
            enemy = str(self.state.combat["enemy_name"])
            self.state.combat = {}
            self.state.phase = "playing"
            self.state.remember(f"避开与{enemy}交手")
            self._autosave()
            return f"你没有贸然出手，转身离开了{enemy}。\n\n{self._status()}"
        if action.startswith("遁走"):
            CombatEngine.start(self.state)
            return self._combat_action(action)
        return CombatEngine.enemy_panel(self.state)

    def _advance_combat_time(self) -> bool:
        if self.state.combat.get("source") == "challenge" and not self.state.combat.get("time_advanced"):
            self.state.combat["time_advanced"] = True
            return self._advance_time()
        return False

    def _combat_action(self, action: str) -> str:
        round_number = int(self.state.combat["round"])
        try:
            result = CombatEngine.act(self.state, action)
        except ValueError as exc:
            return str(exc) + "\n\n" + CombatEngine.combat_panel(self.state)
        enemy = str(self.state.combat["enemy_name"])
        self.state.remember(f"对战{enemy}：{result.player_text}；{result.enemy_text}")

        if result.escaped:
            died_of_age = self._advance_combat_time()
            self.state.combat = {}
            self.state.phase = "ended" if died_of_age else "playing"
            if died_of_age:
                self.state.player.condition = "逃出生天后寿元耗尽"
            self._autosave()
            if died_of_age:
                return "你甩开追兵，却在归途中寿元耗尽。\n【坐化结局】"
            return f"{result.player_text}。\n{result.enemy_text}\n\n{self._status()}"

        if result.victory:
            JourneyEngine.mark(self.state, "combat_victory")
            insight = DaoEngine.gain_insight(self.state, 8, f"战胜{enemy}")
            died_of_age = self._advance_combat_time()
            if died_of_age:
                self.state.phase = "ended"
                self.state.player.condition = "战后寿元耗尽"
                self._autosave()
                return f"你击败了{enemy}，却在战后寿元耗尽。\n【坐化结局】"
            CombatEngine.finish_victory(self.state)
            self._autosave()
            if self.state.phase == "combat_loot":
                loot = "、".join(f"{name}×{count}" for name, count in self.state.pending_loot.items()) or "无"
                return (
                    f"【胜利】{result.player_text}\n{result.enemy_text}\n"
                    f"杀伐业力 +5｜实战感悟 +{insight}\n【待取战利品】{loot}\n选择：拾取全部／离开"
                )
            return f"【切磋获胜】声望 +3｜实战感悟 +{insight}\n{result.player_text}\n{result.enemy_text}\n\n{self._status()}"

        if result.defeat:
            died_of_age = self._advance_combat_time()
            fatal = result.fatal or died_of_age
            self.state.phase = "ended" if fatal else "playing"
            if not fatal:
                self.state.combat = {}
            self._autosave()
            ending = "【陨落结局】" if fatal else "你侥幸留得性命，但已身受重伤。"
            return f"【战败】{result.player_text}\n{result.enemy_text}\n{ending}"

        self._autosave()
        return (
            f"【战斗 · 第 {round_number} 轮结算】\n{result.player_text}\n{result.enemy_text}\n\n"
            + CombatEngine.combat_panel(self.state)
        )

    def _combat_loot(self, action: str) -> str:
        if action == "拾取全部":
            loot = CombatEngine.collect_loot(self.state)
            text = "、".join(f"{name} +{count}" for name, count in loot.items()) or "无"
            self.state.remember(f"拾取战利品：{text}")
            self._autosave()
            return f"已拾取：{text}\n\n{self._status()}"
        if action == "离开":
            CombatEngine.leave_loot(self.state)
            self.state.remember("放弃战利品，离开战场")
            self._autosave()
            return f"你没有触碰尸身，径直离开。\n\n{self._status()}"
        loot = "、".join(f"{name}×{count}" for name, count in self.state.pending_loot.items()) or "无"
        return f"【待取战利品】{loot}\n请选择：拾取全部／离开"

    def _arts(self) -> str:
        player = self.state.player
        artifacts = [name for name in ARTIFACTS if player.resources.get(name, 0) > 0]
        auxiliary = "、".join(player.equipped_auxiliary_techniques) if player.equipped_auxiliary_techniques else "无"
        return (
            "【道法构筑】\n"
            f"主修：{player.primary_technique}（{player.primary_technique_grade}）\n"
            f"辅修：{auxiliary}\n"
            f"已悟功法：{'、'.join(player.known_techniques)}\n"
            f"当前法术：{player.equipped_spell or '无'}｜已悟法术：{'、'.join(player.known_spells)}\n"
            f"武器：{player.equipped_weapon or '无'}｜护甲：{player.equipped_armor or '无'}\n"
            f"持有法宝：{'、'.join(artifacts) if artifacts else '无'}\n"
            "指令：参悟 [名称]／装备功法 [名称]／辅修功法 [名称] [1或2]／"
            "装备法术 [名称]／装备法宝 [名称]"
        )

    def _learn_art(self, action: str) -> str:
        name = action.removeprefix("参悟").strip()
        if not name:
            return "请输入要参悟的功法或法术名称；参悟需要对应残卷。"
        try:
            result = ArtsEngine.learn(self.state, name)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "参悟中寿元耗尽"
        verdict = "参悟成功" if result.success else "参悟失败，残卷损毁"
        self.state.remember(f"参悟{result.name}：{verdict}；判定 {result.roll}/{result.chance}")
        self._autosave()
        if died_of_age:
            return f"你在参悟{result.name}时寿元耗尽。\n【坐化结局】"
        return (
            f"{self.state.time_label}\n【参悟 · {result.name}】{verdict}\n"
            f"判定：1d100={result.roll}，成功率 {result.chance}%\n\n{self._arts()}"
        )

    def _equip_main_technique(self, action: str) -> str:
        name = action.removeprefix("装备功法").strip()
        try:
            ArtsEngine.equip_main_technique(self.state.player, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"将{name}设为主修功法")
        self._autosave()
        return f"主修功法已更换为{name}，修炼品级同步为{self.state.player.primary_technique_grade}。\n\n{self._arts()}"

    def _equip_auxiliary_technique(self, action: str) -> str:
        text = action.removeprefix("辅修功法").strip()
        parts = text.rsplit(maxsplit=1)
        slot = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else None
        name = parts[0] if slot is not None else text
        try:
            ArtsEngine.equip_auxiliary_technique(self.state.player, name, slot)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"辅修功法：{name}")
        self._autosave()
        return f"已将{name}纳入辅修。\n\n{self._arts()}"

    def _equip_spell(self, action: str) -> str:
        name = action.removeprefix("装备法术").strip()
        try:
            ArtsEngine.equip_spell(self.state.player, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"装备法术：{name}")
        self._autosave()
        return f"当前战斗法术已更换为{name}。\n\n{self._arts()}"

    def _equip_artifact(self, action: str) -> str:
        name = action.removeprefix("装备法宝").strip()
        try:
            ArtsEngine.equip_artifact(self.state.player, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"装备法宝：{name}")
        self._autosave()
        return f"已装备{name}。\n\n{self._arts()}"

    def _unequip_artifact(self, action: str) -> str:
        name = action.removeprefix("卸下法宝").strip()
        if not name:
            return "请选择要卸下的法宝。"
        try:
            slot = InventoryEngine.unequip(self.state, name)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"卸下{slot}：{name}")
        self._autosave()
        return f"已卸下{name}，{slot}槽位现已空出。\n\n{self._arts()}"

    def _crafts(self) -> str:
        skill_lines = [
            f"{skill}：{CraftingEngine.skill_rank(self.state, skill)}（成功 {self.state.player.craft_successes.get(skill, 0)} 次）"
            for skill in SKILL_NAMES
        ]
        return (
            "【修仙百艺】\n"
            + "\n".join(skill_lines)
            + "\n\n【已知配方】\n"
            + "\n".join(CraftingEngine.recipe_lines())
            + "\n指令：炼丹 [丹药]／炼器 [法宝]／制符 [符箓]"
        )

    def _craft(self, action: str, prefix: str, craft: str) -> str:
        name = action.removeprefix(prefix).strip()
        try:
            result = CraftingEngine.craft(self.state, craft, name)
        except ValueError as exc:
            return str(exc)
        if result.success:
            CommissionEngine.mark(self.state, "craft_success")
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = f"{craft}时寿元耗尽"
        verdict = f"成功获得{result.recipe.output}×{result.recipe.output_count}" if result.success else "失败，投入材料尽毁"
        rank_up = f"；{craft}提升至{CraftingEngine.skill_rank(self.state, craft)}" if result.leveled_up else ""
        self.state.remember(f"{craft}{name}：{verdict}{rank_up}")
        self._autosave()
        if died_of_age:
            return f"你在{craft}途中寿元耗尽。\n【坐化结局】"
        return (
            f"{self.state.time_label}\n【{craft} · {name}】{verdict}{rank_up}\n"
            f"判定：1d100={result.roll}，成功率 {result.chance}%\n\n{self._crafts()}"
        )

    def _cave(self) -> str:
        cave = CaveEngine.snapshot(self.state)
        facilities = "\n".join(f"{name}：{self.state.cave_facilities.get(name, 0)} 级" for name in FACILITIES)
        crops = []
        for name, ready_turn in self.state.spirit_crops.items():
            remaining = max(0, ready_turn - self.state.turn)
            crops.append(f"{name}：{'可收获' if remaining == 0 else f'{remaining}个月后成熟'}")
        return (
            f"【洞府】{cave['name']}｜灵气：{self.state.aura_level}\n"
            f"灵蕴：{cave['spirit_energy']}/{cave['spirit_energy_cap']}｜每月 +{cave['monthly_generation']}｜方针：{cave['focus']}\n"
            f"工坊：{cave['active_jobs']}/{cave['capacity']} 项进行中\n{facilities}\n"
            f"灵田：{'、'.join(crops) if crops else '无作物'}\n"
            "指令：洞府方针 [名称]／洞府生产 [配方]／洞府调息／升级洞府 [设施]／种植/收获 灵药"
        )

    def _set_cave_focus(self, action: str) -> str:
        focus = action.removeprefix("洞府方针").strip()
        try:
            CaveEngine.set_focus(self.state, focus)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"洞府运转方针改为{focus}")
        self._autosave()
        return f"洞府已经改按“{focus}”运转；从下个月起按新方针结算。\n\n{self._cave()}"

    def _queue_cave_production(self, action: str) -> str:
        name = action.removeprefix("洞府生产").strip()
        try:
            job = CaveEngine.queue_recipe(self.state, name)
        except ValueError as exc:
            return str(exc)
        ingredients = "、".join(f"{item}×{count}" for item, count in dict(job["ingredients"]).items())
        self.state.remember(f"安排洞府后台制作{name}，预留{ingredients}")
        self._autosave()
        return (
            f"【洞府生产已安排】{name}\n"
            f"工坊：{job['facility']}｜工期：{job['duration']} 个月｜成功率：{job['chance']}%\n"
            f"预留材料：{ingredients}；你可照常修炼、游历或处理其他事务。\n\n{self._cave()}"
        )

    def _cancel_cave_production(self, action: str) -> str:
        job_id = action.removeprefix("取消洞府生产").strip()
        try:
            job = CaveEngine.cancel_job(self.state, job_id)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"取消洞府生产{job_id}，取回全部预留材料")
        self._autosave()
        return f"已取消{job.get('recipe', '该项生产')}，预留材料已全部放回乾坤袋。\n\n{self._cave()}"

    def _cave_recuperate(self) -> str:
        try:
            health, spirit, cost = CaveEngine.recuperate(self.state)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "洞府调息时寿元耗尽"
        self.state.remember(f"洞府调息消耗灵蕴{cost}，气血+{health}、灵力+{spirit}")
        self._autosave()
        if died_of_age:
            return "你在静室调息时寿元耗尽。\n【坐化结局】"
        return f"{self.state.time_label}\n【洞府调息】气血 +{health}｜灵力 +{spirit}｜灵蕴 -{cost}\n\n{self._cave()}"

    def _upgrade_cave(self, action: str) -> str:
        facility = action.removeprefix("升级洞府").strip()
        try:
            stones, materials = CraftingEngine.upgrade_cost(self.state, facility)
            level = CraftingEngine.upgrade_facility(self.state, facility)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "修建洞府时寿元耗尽"
        material_text = "、".join(f"{name}×{count}" for name, count in materials.items())
        self.state.remember(f"升级洞府{facility}至{level}级，消耗灵石{stones}、{material_text}")
        self._autosave()
        if died_of_age:
            return "洞府设施尚未落成，你已寿元耗尽。\n【坐化结局】"
        return f"{self.state.time_label}\n{facility}已升至 {level} 级。\n消耗：灵石 {stones}、{material_text}\n\n{self._cave()}"

    def _plant(self, action: str) -> str:
        crop = action.removeprefix("种植").strip()
        try:
            ready_turn = CraftingEngine.plant(self.state, crop)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "耕作时寿元耗尽"
        self.state.remember(f"种下{crop}，预计第{ready_turn}回合成熟")
        self._autosave()
        if died_of_age:
            return "你在灵田劳作时寿元耗尽。\n【坐化结局】"
        return f"已种下{crop}，还需 {max(0, ready_turn - self.state.turn)} 个月成熟。\n\n{self._cave()}"

    def _harvest(self, action: str) -> str:
        crop = action.removeprefix("收获").strip()
        try:
            count = CraftingEngine.harvest(self.state, crop)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "收获时寿元耗尽"
        self.state.remember(f"灵田收获{crop}×{count}")
        self._autosave()
        if died_of_age:
            return "收获之后，你在灵田边寿元耗尽。\n【坐化结局】"
        return f"灵田收获：{crop} +{count}。\n\n{self._cave()}"

    def _relationships(self) -> str:
        lines = []
        for npc in NPCS.values():
            affinity = RelationshipEngine.affinity(self.state, npc.name)
            relation = RelationshipEngine.relation(self.state, npc.name)
            bond = RelationshipEngine.bond_label(
                affinity, npc.name in self.state.dao_partners, str(relation.get("path", ""))
            )
            world = NpcEcologyEngine.world_record(self.state, npc.name)
            life = "已故" if not world.get("alive", True) else str(world.get("status", "安然"))
            lines.append(
                f"{npc.name}｜{npc.gender}｜{npc.identity}｜{world['age']}岁（寿元 {world['lifespan']}）｜"
                f"{world['realm']}｜好感 {affinity}（{bond}）｜所在地 {world['location']}｜近况 {life}"
            )
        pending = "、".join(f"{name}·{event['kind']}" for name, event in self.state.pending_npc_life_events.items()) or "无"
        recent_trial = self.state.relationship_events[-1] if self.state.relationship_events else "尚无情劫记录"
        return (
            "【人物与情缘】\n"
            + "\n".join(lines)
            + f"\n\n【尘缘波澜】{self.state.relationship_tension}/100｜{recent_trial}"
            + f"\n【待回应护道书】{pending}"
            + "\n指令：对话/论道 [姓名]／送礼 [姓名] [物品]／护道 [姓名] [赠丹/护持/守候]／确立关系 [姓名] [类型]／结为道侣/双修 [姓名]"
        )

    def _prepare_heart_trial(self) -> str:
        try:
            names, tension = RelationshipEngine.begin_heart_trial(self.state)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"情劫浮现：{'、'.join(names)}，波澜{tension}")
        self._autosave()
        return (
            "【情劫浮现】\n"
            f"牵涉之人：{'、'.join(names) if names else '旧缘未散'}\n"
            f"尘缘波澜：{tension}/100\n"
            "几段心意在同一刻交汇，你必须亲自选择面对之法。\n\n"
            "【情劫抉择】\n"
            "坦诚相告：以道心和诚意承担风险，成功可修复关系。\n"
            "暂避锋芒：降低风波，但所有相关人物的好感略有下降。\n"
            "一心问道：主动斩断所有暧昧与道侣之契，换取道心成长。\n"
            "请选择：情劫 坦诚相告／情劫 暂避锋芒／情劫 一心问道"
        )

    def _heart_trial_choice(self, action: str) -> str:
        choice = action.removeprefix("情劫").strip()
        try:
            result = RelationshipEngine.resolve_heart_trial(self.state, choice)
        except ValueError as exc:
            return str(exc)
        died = self._advance_time()
        self.state.remember(f"情劫选择{result.choice}，波澜降至{result.tension}")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "情劫后寿元耗尽"
        self._autosave()
        if died:
            return f"{result.description}\n【坐化结局】你在情劫落幕后走完此生。"
        verdict = "" if result.chance == 100 else f"\n判定：1d100={result.roll}，成功率 {result.chance}%"
        return (
            f"{self.state.time_label}\n【情劫 · {result.choice}】\n{result.description}{verdict}\n"
            f"尘缘波澜：{result.tension}/100\n\n{self._relationships()}"
        )

    def _npc_world(self) -> str:
        lines = []
        for name in NPCS:
            world = NpcEcologyEngine.world_record(self.state, name)
            invitation = self.state.npc_invitations.get(name)
            invite_text = f"｜待回应：{invitation['kind']}" if invitation else ""
            injury = "已故" if not world.get("alive", True) else ("负伤" if world.get("wounded") else str(world.get("status", "安然")))
            lines.append(f"{name}｜{world['realm']}｜{world['age']}/{world['lifespan']}岁｜{world['location']}｜{world['activity']}｜{injury}{invite_text}")
        recent = "\n".join(self.state.npc_event_log[-5:]) or "尚无人物动态"
        lives = "\n".join(self.state.npc_lifecycle_log[-5:]) or "尚无生平变故"
        return (
            "【九州人物动态】\n" + "\n".join(lines) + "\n\n【最近动态】\n" + recent
            + "\n\n【浮生录】\n" + lives
            + "\n指令：回应 [姓名] 接受／回应 [姓名] 婉拒／护道 [姓名] [赠丹/护持/守候]"
        )

    def _npc_network(self) -> str:
        network = NpcNetworkEngine.snapshot(self.state)
        lines = [
            f"{item['left']} ↔ {item['right']}｜{item['label']} {int(item['score']):+d}｜{item['last_event']}"
            for item in network["bonds"]
        ]
        pending = network["pending"]
        pending_text = "当前没有需要你表态的人物纷争。"
        if pending:
            pending_text = (
                f"{pending['left']}与{pending['right']}因【{pending['cause']}】相持不下，"
                f"还可在 {pending['expires_in']} 个月内介入。"
            )
        return (
            "【众生因缘网】\n"
            + "\n".join(lines)
            + f"\n\n【缘网概览】相连人物 {network['connected_count']}｜结缘 {network['allied_count']}｜嫌隙 {network['rival_count']}"
            + f"\n【待决人情】{pending_text}"
            + "\n指令：介入人情 调停／介入人情 偏袒 [姓名]／介入人情 旁观"
        )

    def _intervene_network(self, action: str) -> str:
        parts = action.removeprefix("介入人情").strip().split()
        if not parts:
            return "格式：介入人情 调停／介入人情 偏袒 [姓名]／介入人情 旁观。"
        choice = parts[0]
        favored = parts[1] if len(parts) == 2 and choice == "偏袒" else ""
        if choice not in {"调停", "偏袒", "旁观"} or (choice == "偏袒" and not favored) or len(parts) > 2:
            return "格式：介入人情 调停／介入人情 偏袒 [姓名]／介入人情 旁观。"
        try:
            result = NpcNetworkEngine.intervene(self.state, choice, favored)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        self.state.remember(f"介入人物纷争：{result.choice}；{'成功' if result.success else '未成'}")
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "调停人情后寿元耗尽"
        self._autosave()
        verdict = ""
        if result.chance:
            verdict = f"\n判定：1d100={result.roll}，成功率 {result.chance}%"
        cost = f"｜灵力 -{result.spirit_cost}" if result.spirit_cost else ""
        ending = "\n【坐化结局】你在人情风波落定后走完此生。" if died_of_age else ""
        return (
            f"{self.state.time_label}\n【人情介入 · {result.choice}】\n{result.description}{verdict}{cost}{ending}\n\n"
            + self._npc_network()
        )

    def _guard_npc(self, action: str) -> str:
        parts = action.removeprefix("护道").strip().split()
        if len(parts) != 2:
            return "格式：护道 [姓名] [赠丹/护持/守候]。"
        name, choice = parts
        try:
            result = NpcLifecycleEngine.resolve(self.state, name, choice)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        self.state.remember(
            f"为{name}护道：{result.choice}，{'破境成功' if result.success else '未能破境'}；判定{result.roll}/{result.chance}"
        )
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "为故人护道后寿元耗尽"
        self._autosave()
        consequence = "" if not result.cost or result.cost == "无" else f"｜消耗 {result.cost}"
        ending = "\n【坐化结局】你护住故人此劫，自己的寿元却在归途中走到尽头。" if died_of_age else ""
        return (
            f"{self.state.time_label}\n【故人护道 · {name}】\n{result.description}\n"
            f"判定 {result.roll}/{result.chance}{consequence}{ending}\n\n{self._relationships()}"
        )

    def _respond_invitation(self, action: str) -> str:
        parts = action.removeprefix("回应").strip().split()
        if len(parts) != 2:
            return "格式：回应 [姓名] 接受／回应 [姓名] 婉拒。"
        name, decision = parts
        try:
            kind, affinity, text = NpcEcologyEngine.respond(self.state, name, decision)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"回应{name}的{kind}邀约：{decision}，好感{affinity}")
        if died:
            return "赴约归来后，你的寿元走到尽头。\n【坐化结局】"
        return f"{self.state.time_label}\n{text}\n\n{self._relationships()}"

    def _set_relation_path(self, action: str) -> str:
        parts = action.removeprefix("确立关系").strip().split()
        if len(parts) != 2:
            return "格式：确立关系 [姓名] [纯友谊/结义/师徒/宿敌]。"
        name, path = parts
        try:
            path, affinity = NpcEcologyEngine.set_relation_path(self.state, name, path)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"与{name}确立{path}关系")
        self._autosave()
        return f"你与{name}正式确立【{path}】关系，当前好感 {affinity}。\n\n{self._relationships()}"

    def _finish_social_action(self, event: str) -> bool:
        died_of_age = self._advance_time()
        self.state.remember(event)
        if died_of_age:
            self.state.phase = "ended"
            self.state.player.condition = "交游途中寿元耗尽"
        self._autosave()
        return died_of_age

    def _talk(self, action: str) -> str:
        name = action.removeprefix("对话").strip()
        affinity_before = RelationshipEngine.affinity(self.state, name) if name in NPCS else 0
        try:
            line, affinity = RelationshipEngine.talk(self.state, name)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"与{name}交谈，好感升至{affinity}")
        if died:
            return "交谈之后，你在归途中寿元耗尽。\n【坐化结局】"
        change = affinity - affinity_before
        return f"{self.state.time_label}\n【{name}】“{line}”\n好感 {change:+d}，当前 {affinity}。\n\n{self._relationships()}"

    def _gift(self, action: str) -> str:
        parts = action.removeprefix("送礼").strip().split()
        if len(parts) != 2:
            return "格式：送礼 [姓名] [物品]。"
        name, item = parts
        try:
            change, affinity = RelationshipEngine.gift(self.state, name, item)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"赠予{name}{item}，好感{change:+d}至{affinity}")
        if died:
            return "赠礼之后，你在归途中寿元耗尽。\n【坐化结局】"
        reaction = "十分喜欢" if change >= 10 else ("并不喜欢" if change < 0 else "礼貌收下")
        return f"{self.state.time_label}\n{name}{reaction}{item}。\n好感 {change:+d}，当前 {affinity}。\n\n{self._relationships()}"

    def _discuss_dao(self, action: str) -> str:
        name = action.removeprefix("论道").strip()
        insight_before = self.state.player.dao_insight
        affinity_before = RelationshipEngine.affinity(self.state, name) if name in NPCS else 0
        try:
            success, roll, chance, affinity = RelationshipEngine.discuss_dao(self.state, name)
        except ValueError as exc:
            return str(exc)
        affinity_change = affinity - affinity_before
        verdict = f"彼此印证所得，修为有所精进，好感 {affinity_change:+d}" if success else f"道途分歧，只作浅谈，好感 {affinity_change:+d}"
        died = self._finish_social_action(f"与{name}论道：{'成功' if success else '未能契合'}，好感{affinity}")
        if died:
            return "论道之后，你的寿元走到尽头。\n【坐化结局】"
        insight = self.state.player.dao_insight - insight_before
        return f"{self.state.time_label}\n【与{name}论道】{verdict}\n判定 {roll}/{chance}｜当前好感 {affinity}｜感悟 +{insight}。\n\n{self._status()}"

    def _become_partners(self, action: str) -> str:
        name = action.removeprefix("结为道侣").strip()
        try:
            affinity = RelationshipEngine.become_partners(self.state, name)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"与{name}结为道侣")
        if died:
            return "结契之后，你的寿元却已走到尽头。\n【坐化结局】"
        return f"{self.state.time_label}\n你与{name}自愿结下道侣之契。\n当前好感 {affinity}（道侣）。\n\n{self._relationships()}"

    def _dual_cultivate(self, action: str) -> str:
        name = action.removeprefix("双修").strip()
        try:
            gain, affinity = RelationshipEngine.dual_cultivate(self.state, name)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"与{name}双修，修为+{gain}，好感{affinity}")
        if died:
            return "双修结束后，你安然坐化。\n【坐化结局】"
        return f"{self.state.time_label}\n你与{name}合修一月。\n修为 +{gain}｜好感 +3，当前 {affinity}。\n\n{self._status()}"

    def _status(self) -> str:
        p = self.state.player
        return (
            f"【状态卡 · 第 {self.state.turn} 回合 · {self.state.time_label}】\n"
            f"道号 {p.dao_name}｜姓名 {p.name}｜性别 {p.gender}｜年龄 {p.age}/{p.lifespan}\n"
            f"境界 {p.realm}｜宗门 {p.sect}·{p.sect_rank}｜贡献 {p.sect_contribution}｜所在地 {p.location}\n"
            f"出身 {p.background}｜道途 {p.dao_path}｜体质 {p.constitution}\n"
            f"资质 {p.aptitude} 悟性 {p.comprehension} 神识 {p.spirit_sense} "
            f"遁速 {p.speed} 道心 {p.dao_heart} 仙缘 {p.fortune}\n"
            f"灵根 {p.spiritual_root}｜气血 {p.health}/{p.health_max}｜"
            f"灵力 {p.spirit}/{p.spirit_max}｜修为 {p.cultivation}/{p.cultivation_required}\n"
            f"灵石 {p.spirit_stones}｜功德 {p.merit}｜业力 {p.karma}｜声望 {p.reputation}｜异常 {p.condition}\n"
            f"天赋：{'、'.join(p.talents) if p.talents else '无'}\n"
            f"逆天改命：{'、'.join(p.destiny_traits) if p.destiny_traits else '无'}｜突破冷却 {p.breakthrough_cooldown_months} 月\n"
            f"悟道：感悟 {p.dao_insight}/20｜悟道点 {p.dao_points}｜已点亮 {sum(p.dao_levels.values())} 层\n"
            f"主修 {p.primary_technique}｜法术 {p.equipped_spell or '无'}｜武器 {p.equipped_weapon or '无'}｜护甲 {p.equipped_armor or '无'}\n"
            f"道侣：{'、'.join(self.state.dao_partners) if self.state.dao_partners else '无'}\n"
            f"尘缘波澜：{self.state.relationship_tension}/100｜情劫记录 {len(self.state.relationship_events)}\n"
            f"人物动态：{self.state.last_npc_event or '众生各循其道'}\n"
            f"天下大势：{self.state.last_world_event or '灵气潮汐尚在暗中酝酿'}｜局势 {self.state.world_tension}\n"
            f"主线：{self.state.main_quest}\n指令：{COMMANDS}"
        )

    def _claim_journey(self, action: str) -> str:
        claim_id = action.removeprefix("领取道途奖励").strip()
        if not claim_id:
            return JourneyEngine.panel_text(self.state)
        try:
            reward = JourneyEngine.claim(self.state, claim_id)
        except ValueError as exc:
            return str(exc) + "\n\n" + JourneyEngine.panel_text(self.state)
        self.state.remember(f"领取道途奖励：{reward}")
        self._autosave()
        return f"【道途奖励】{reward}\n\n" + JourneyEngine.panel_text(self.state)

    def _begin_story(self) -> str:
        try:
            node = StoryEngine.begin(self.state)
        except ValueError as exc:
            return str(exc) + "\n\n" + StoryEngine.panel_text(self.state)
        self.state.remember(f"主线第{node.chapter}章《{node.title}》浮现")
        self._autosave()
        choices = "\n".join(f"{choice.label}｜{choice.description}" for choice in node.choices)
        return f"【主线第 {node.chapter} 章 · {node.title}】\n{node.summary}\n地点：{node.location}\n\n【因果抉择】\n{choices}"

    def _story_choice(self, action: str) -> str:
        if not action.startswith("主线选择"):
            return "当前主线因果尚待决定，请从页面列出的三项抉择中选择。"
        choice_id = action.removeprefix("主线选择").strip()
        try:
            node, choice, result = StoryEngine.resolve(self.state, choice_id)
        except ValueError as exc:
            return str(exc)
        died = self._advance_time()
        self.state.remember(f"主线《{node.title}》选择{choice.label}：{result}")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "主线因果落定后寿元耗尽"
        self._autosave()
        if died:
            return f"{result}\n【坐化结局】你在因果落定后走完此生。"
        return f"{self.state.time_label}\n【{node.title} · {choice.label}】\n{choice.description}\n结算：{result}\n\n{StoryEngine.panel_text(self.state)}"

    def _begin_new_era_event(self) -> str:
        try:
            event = NewEraEngine.begin(self.state)
        except ValueError as exc:
            return str(exc) + "\n\n" + NewEraEngine.panel_text(self.state)
        self.state.remember(f"新世第{self.state.new_era_counter + 1}轮《{event.title}》等待处置")
        self._autosave()
        choices = "\n".join(f"{choice.label}｜{choice.description}" for choice in event.choices)
        return f"【新世余波 · {event.title}】\n{event.summary}\n地点：{event.location}\n\n【新世抉择】\n{choices}"

    def _new_era_choice(self, action: str) -> str:
        if not action.startswith("新世选择"):
            return "当前新世余波尚待决定，请从页面列出的三项应对中选择。"
        choice_id = action.removeprefix("新世选择").strip()
        try:
            event, choice, result = NewEraEngine.resolve(self.state, choice_id)
        except ValueError as exc:
            return str(exc)
        died = self._advance_time()
        self.state.remember(f"新世《{event.title}》选择{choice.label}：{result}")
        if died:
            self.state.phase = "ended"
            self.state.player.condition = "新世余波落定后寿元耗尽"
        self._autosave()
        if died:
            return f"{result}\n【坐化结局】你在新世余波落定后走完此生。"
        return f"{self.state.time_label}\n【{event.title} · {choice.label}】\n{choice.description}\n结算：{result}\n\n{NewEraEngine.panel_text(self.state)}"

    def _accept_commission(self, action: str) -> str:
        instance_id = action.removeprefix("接取委托").strip()
        if not instance_id:
            return CommissionEngine.panel_text(self.state)
        try:
            result = CommissionEngine.accept(self.state, instance_id)
        except ValueError as exc:
            return str(exc) + "\n\n" + CommissionEngine.panel_text(self.state)
        self.state.remember(result)
        self._autosave()
        return f"【接取委托】{result}\n\n" + CommissionEngine.panel_text(self.state)

    def _deliver_commission(self, action: str) -> str:
        instance_id = action.removeprefix("交付委托").strip()
        if not instance_id:
            return CommissionEngine.panel_text(self.state)
        try:
            result = CommissionEngine.deliver(self.state, instance_id)
        except ValueError as exc:
            self._autosave()
            return str(exc) + "\n\n" + CommissionEngine.panel_text(self.state)
        self.state.remember(result)
        self._autosave()
        return f"【委托交付】{result}\n\n" + CommissionEngine.panel_text(self.state)

    def _abandon_commission(self, action: str) -> str:
        instance_id = action.removeprefix("放弃委托").strip()
        if not instance_id:
            return CommissionEngine.panel_text(self.state)
        try:
            result = CommissionEngine.abandon(self.state, instance_id)
        except ValueError as exc:
            return str(exc) + "\n\n" + CommissionEngine.panel_text(self.state)
        self.state.remember(result)
        self._autosave()
        return f"【委托撤下】{result}\n\n" + CommissionEngine.panel_text(self.state)

    def _save(self, action: str) -> str:
        parts = action.split(maxsplit=1)
        name = parts[1] if len(parts) == 2 else self.autosave_name
        path = self.saves.save(name, self.state)
        return f"已存档：{path.name}（第 {self.state.turn} 回合）"

    def _load(self, action: str) -> str:
        parts = action.split(maxsplit=1)
        if len(parts) == 1:
            names = self.saves.list_names()
            return "可用存档：" + ("、".join(names) if names else "无")
        try:
            loaded = self.saves.load(parts[1])
        except FileNotFoundError as exc:
            return str(exc)
        if loaded.rule_sha256 and loaded.rule_sha256 != self.rules.sha256:
            return "存档所用规则与当前 DOCX 不一致，已拒绝直接载入；请先备份并迁移存档。"
        self.state = loaded
        NewEraEngine.activate(self.state)
        return "读档完成。\n\n" + self._status()

    def _autosave(self) -> None:
        self.saves.save(self.autosave_name, self.state)

    def _advance_time(self, months: int = 1) -> bool:
        died_of_age = False
        NpcLifecycleEngine.ensure_all(self.state)
        for _ in range(months):
            previous_year = self.state.calendar_year
            died_of_age = self.state.advance_month() or died_of_age
            expired_life_events = NpcLifecycleEngine.expire_pending(self.state)
            for result in expired_life_events:
                self.state.remember(f"{result.name}的护道书逾期：{result.description}")
            expired_network_event = NpcNetworkEngine.expire_pending(self.state)
            if expired_network_event:
                self.state.remember(f"众生缘网：{expired_network_event}")
            if self.state.calendar_year != previous_year:
                for event in NpcLifecycleEngine.advance_year(self.state):
                    self.state.remember(f"浮生录：{event}")
            NpcEcologyEngine.tick(self.state)
            network_event = NpcNetworkEngine.tick(self.state)
            if network_event:
                self.state.remember(f"众生缘网：{network_event}")
            WorldTimelineEngine.tick(self.state)
            new_era_event = NewEraEngine.tick(self.state)
            if new_era_event:
                self.state.remember(new_era_event)
            CommissionEngine.expire_overdue(self.state)
            AuctionEngine.expire(self.state)
            cave_tick = CaveEngine.tick(self.state)
            for event in cave_tick.events:
                self.state.remember(f"洞府月报：{event}")
        return died_of_age

    @staticmethod
    def _help() -> str:
        return (
            "【指令大全 · 问道长生】\n"
            "开始游戏｜面板｜修炼｜突破｜存档 [名称]｜读档 [名称]\n"
            "主线｜查看灵潮因果；推进主线后从三项行动中亲自选择\n"
            "道途｜查看四章成长目标；领取道途奖励 [编号]\n"
            "委托｜查看东洲悬榜；接取/交付/放弃委托 [编号]；悬榜每三个月轮换\n"
            "退出：退出／quit／Ctrl+C\n"
            "闭关｜闭关3月｜闭关2年：按修炼公式结算并推进岁月\n"
            "悟道｜观想积累感悟｜闭关悟道凝成悟道点｜点亮 [剑道/丹道等九途]\n"
            "地图/九州｜前往 [地域]｜选择商队或御风｜探索 [当地地点]\n"
            "地方｜查看五域声名与礼遇｜地方机缘后从三项应对中亲自选择\n"
            "坊市｜区域价格会随特产、求购、民生与地方声望变化｜买/卖 [物品] [数量]\n"
            "拍卖会｜竞拍 [拍品编号]；竞价时可稳健举牌、强势压场或退出\n"
            "秘境｜进入秘境 [名称]｜确认进入；秘境内可谨慎探索、强行探索或退出秘境\n"
            "宗门｜拜入 [宗门]｜宗门任务 [类型]｜申请晋升｜宗门大比｜护宗战｜叛宗\n"
            "天下｜查看时代、势力、民生与时间线｜干预天下可主动改变局势\n"
            "战斗｜挑战 [对手]｜切磋 [对手]；战斗内可攻击、防御、施法、蓄势、绝技或遁走\n"
            "背包｜使用 [丹药/灵食]｜装备法宝/卸下法宝 [名称]\n"
            "道法｜参悟 [功法/法术]｜装备功法/法术/法宝 [名称]｜辅修功法 [名称]\n"
            "技艺｜炼丹/炼器/制符 [名称]｜洞府｜洞府方针/生产/调息｜升级洞府 [设施]｜种植/收获 灵药\n"
            "情缘｜对话/论道 [姓名]｜送礼 [姓名] [物品]｜结为道侣/双修 [姓名]\n"
            "情劫｜当两段以上暧昧或道侣关系交汇时，可选择坦诚相告、暂避锋芒或一心问道\n"
            "世情｜回应 [姓名] 接受/婉拒｜确立关系 [姓名] [纯友谊/结义/师徒/宿敌]\n"
            "故人护道｜护道 [姓名] [赠丹/护持/守候]；人物会真实老去、破境与辞世\n"
            "人脉｜查看人物之间的结交与嫌隙｜介入人情 [调停/偏袒 姓名/旁观]\n"
            "其余任何文字都视为自由行动；本地叙事器会推进一个月并记录历史。"
        )
