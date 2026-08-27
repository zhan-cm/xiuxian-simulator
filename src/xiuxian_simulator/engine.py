from __future__ import annotations

from .character_creation import BasicCharacter, CharacterCreationError, CharacterCreator
from .adventures import AdventureEngine, SECRET_REALMS
from .arts import ARTIFACTS, ArtsEngine
from .combat import ENEMIES, CombatEngine
from .crafting import FACILITIES, RECIPES, SKILL_NAMES, CraftingEngine
from .relationships import NPCS, RelationshipEngine
from .economy import AREAS, SECTS, SECT_TASKS, EconomyEngine
from .ecology import NpcEcologyEngine
from .world import SectProgressionEngine, WorldTimelineEngine
from .narrator import Narrator
from .progression import ProgressionEngine
from .rules import RuleBook
from .save_manager import SaveManager
from .state import GameState


COMMANDS = "面板 修炼 突破 悟道 洞府 地图 秘境 背包 坊市 宗门 天下 战斗 技艺 情缘 情劫 世情 对话 存档 帮助"


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

        if self.state.phase == "new":
            return "世界尚未开启。请先输入“开始游戏”。"
        if self.state.phase in {"character_creation", "character_creation_basic"}:
            return self._handle_basic_creation(action)
        if self.state.phase == "character_creation_traits":
            return self._handle_trait_creation(action)
        if self.state.phase == "ended":
            return "此世已终。输入“开始游戏”可创建新的轮回。"
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
        if action == "地图":
            return self._map()
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
        if action == "宗门":
            return self._sect()
        if action == "申请晋升":
            return self._sect_promotion()
        if action == "宗门大比":
            return self._sect_tournament()
        if action == "叛宗":
            return self._prepare_defection()
        if action.startswith("拜入"):
            return self._join_sect(action)
        if action.startswith("宗门任务"):
            return self._sect_task(action)
        if action in {"天下", "大事记"}:
            return self._world_timeline()
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
        if action.startswith("回应"):
            return self._respond_invitation(action)
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
        died_of_age = self._advance_time(months_used)
        mode = "闭关" if retreat else "吐纳"
        self.state.remember(f"{mode}修炼 {months_used} 月，修为 +{gain}")
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
            f"结算：{breakdown.summary()}／月\n\n"
            + self._status()
        )

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
        return f"【乾坤袋 · 突破资源】\n{lines}\n普通物品：{'、'.join(self.state.player.inventory) if self.state.player.inventory else '无'}"

    @staticmethod
    def _map() -> str:
        lines = []
        for name, (minimum_realm, danger) in AREAS.items():
            realm_hint = "炼气可入" if minimum_realm == 0 else f"至少第 {minimum_realm + 1} 大境界"
            lines.append(f"{name}｜{realm_hint}｜危险度 {danger}")
        return "【东洲探索地图】\n" + "\n".join(lines) + "\n输入：探索 青岳山麓（不写地点时默认青岳山麓）"

    def _explore(self, action: str) -> str:
        area = action.removeprefix("探索").strip() or "青岳山麓"
        try:
            result = EconomyEngine.explore(self.state, area)
        except ValueError as exc:
            return str(exc)
        died_of_age = self._advance_time()
        rewards = [f"灵石 +{result.spirit_stones}"] if result.spirit_stones else []
        rewards.extend(f"{name} +{count}" for name, count in result.rewards.items())
        if result.health_loss:
            rewards.append(f"气血 -{result.health_loss}")
        reward_text = "、".join(rewards) if rewards else "无"
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
        return (
            f"{self.state.time_label}\n【探索 · {result.area}】\n{result.event}\n"
            f"判定：1d100={result.roll}｜收获：{reward_text}\n\n{self._status()}"
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

    @staticmethod
    def _market() -> str:
        return (
            "【青岳坊市】\n"
            + "\n".join(EconomyEngine.market_lines())
            + "\n输入：买 筑基丹／卖 灵药 2（买卖本身不推进月份）"
        )

    def _trade(self, operation: str, item: str, count: int) -> str:
        try:
            stone_change, item_change = EconomyEngine.trade(self.state, operation, item, count)
        except ValueError as exc:
            return str(exc)
        self.state.remember(f"坊市{operation}{item}×{count}，灵石变动 {stone_change:+d}")
        self._autosave()
        direction = "+" if item_change > 0 else ""
        return (
            f"【坊市成交】{operation}{item}×{count}\n"
            f"灵石 {stone_change:+d}｜{item} {direction}{item_change}\n"
            f"当前灵石：{self.state.player.spirit_stones}"
        )

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
        return (
            f"【九州天下 · 局势 {self.state.world_tension}】\n{schedule}\n\n"
            f"【近期大事记】\n{recent}"
        )

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
                    f"杀伐业力 +5\n【待取战利品】{loot}\n选择：拾取全部／离开"
                )
            return f"【切磋获胜】声望 +3\n{result.player_text}\n{result.enemy_text}\n\n{self._status()}"

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
        facilities = "\n".join(f"{name}：{self.state.cave_facilities.get(name, 0)} 级" for name in FACILITIES)
        crops = []
        for name, ready_turn in self.state.spirit_crops.items():
            remaining = max(0, ready_turn - self.state.turn)
            crops.append(f"{name}：{'可收获' if remaining == 0 else f'{remaining}个月后成熟'}")
        return (
            f"【洞府】灵气：{self.state.aura_level}\n{facilities}\n"
            f"灵田：{'、'.join(crops) if crops else '无作物'}\n"
            "指令：升级洞府 [设施]／种植 灵药／收获 灵药"
        )

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
        elapsed_years = max(0, self.state.calendar_year - 387)
        for npc in NPCS.values():
            affinity = RelationshipEngine.affinity(self.state, npc.name)
            relation = RelationshipEngine.relation(self.state, npc.name)
            bond = RelationshipEngine.bond_label(
                affinity, npc.name in self.state.dao_partners, str(relation.get("path", ""))
            )
            world = NpcEcologyEngine.world_record(self.state, npc.name)
            lines.append(
                f"{npc.name}｜{npc.gender}｜{npc.identity}｜{npc.age + elapsed_years}岁｜"
                f"{npc.realm}｜好感 {affinity}（{bond}）｜所在地 {world['location']}"
            )
        recent_trial = self.state.relationship_events[-1] if self.state.relationship_events else "尚无情劫记录"
        return (
            "【人物与情缘】\n"
            + "\n".join(lines)
            + f"\n\n【尘缘波澜】{self.state.relationship_tension}/100｜{recent_trial}"
            + "\n指令：对话/论道 [姓名]／送礼 [姓名] [物品]／确立关系 [姓名] [类型]／结为道侣/双修 [姓名]"
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
            injury = "负伤" if world.get("wounded") else "安然"
            lines.append(f"{name}｜{world['location']}｜{world['activity']}｜{injury}{invite_text}")
        recent = "\n".join(self.state.npc_event_log[-5:]) or "尚无人物动态"
        return (
            "【九州人物动态】\n" + "\n".join(lines) + "\n\n【最近动态】\n" + recent
            + "\n指令：回应 [姓名] 接受／回应 [姓名] 婉拒"
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
        try:
            line, affinity = RelationshipEngine.talk(self.state, name)
        except ValueError as exc:
            return str(exc)
        died = self._finish_social_action(f"与{name}交谈，好感升至{affinity}")
        if died:
            return "交谈之后，你在归途中寿元耗尽。\n【坐化结局】"
        return f"{self.state.time_label}\n【{name}】“{line}”\n好感 +2，当前 {affinity}。\n\n{self._relationships()}"

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
        try:
            success, roll, chance, affinity = RelationshipEngine.discuss_dao(self.state, name)
        except ValueError as exc:
            return str(exc)
        verdict = "彼此印证所得，修为有所精进，好感 +6" if success else "道途分歧，只作浅谈，好感 +1"
        died = self._finish_social_action(f"与{name}论道：{'成功' if success else '未能契合'}，好感{affinity}")
        if died:
            return "论道之后，你的寿元走到尽头。\n【坐化结局】"
        return f"{self.state.time_label}\n【与{name}论道】{verdict}\n判定 {roll}/{chance}｜当前好感 {affinity}。\n\n{self._status()}"

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
            f"主修 {p.primary_technique}｜法术 {p.equipped_spell or '无'}｜武器 {p.equipped_weapon or '无'}｜护甲 {p.equipped_armor or '无'}\n"
            f"道侣：{'、'.join(self.state.dao_partners) if self.state.dao_partners else '无'}\n"
            f"尘缘波澜：{self.state.relationship_tension}/100｜情劫记录 {len(self.state.relationship_events)}\n"
            f"人物动态：{self.state.last_npc_event or '众生各循其道'}\n"
            f"天下大势：{self.state.last_world_event or '灵气潮汐尚在暗中酝酿'}｜局势 {self.state.world_tension}\n"
            f"主线：{self.state.main_quest}\n指令：{COMMANDS}"
        )

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
        return "读档完成。\n\n" + self._status()

    def _autosave(self) -> None:
        self.saves.save(self.autosave_name, self.state)

    def _advance_time(self, months: int = 1) -> bool:
        died_of_age = False
        for _ in range(months):
            died_of_age = self.state.advance_month() or died_of_age
            NpcEcologyEngine.tick(self.state)
            WorldTimelineEngine.tick(self.state)
        return died_of_age

    @staticmethod
    def _help() -> str:
        return (
            "【指令大全 · 问道长生】\n"
            "开始游戏｜面板｜修炼｜突破｜存档 [名称]｜读档 [名称]\n"
            "退出：退出／quit／Ctrl+C\n"
            "闭关｜闭关3月｜闭关2年：按修炼公式结算并推进岁月\n"
            "地图｜探索 [地点]｜坊市｜买/卖 [物品] [数量]\n"
            "秘境｜进入秘境 [名称]｜确认进入；秘境内可谨慎探索、强行探索或退出秘境\n"
            "宗门｜拜入 [宗门]｜宗门任务 [类型]｜申请晋升｜宗门大比｜叛宗\n"
            "天下｜查看升仙大会、宗门大比、猎魔大会、拍卖会与灵气潮汐时间线\n"
            "战斗｜挑战 [对手]｜切磋 [对手]；战斗内可攻击、防御、施法、蓄势、绝技或遁走\n"
            "道法｜参悟 [功法/法术]｜装备功法/法术/法宝 [名称]｜辅修功法 [名称]\n"
            "技艺｜炼丹/炼器/制符 [名称]｜洞府｜升级洞府 [设施]｜种植/收获 灵药\n"
            "情缘｜对话/论道 [姓名]｜送礼 [姓名] [物品]｜结为道侣/双修 [姓名]\n"
            "情劫｜当两段以上暧昧或道侣关系交汇时，可选择坦诚相告、暂避锋芒或一心问道\n"
            "世情｜回应 [姓名] 接受/婉拒｜确立关系 [姓名] [纯友谊/结义/师徒/宿敌]\n"
            "其余任何文字都视为自由行动；本地叙事器会推进一个月并记录历史。"
        )
