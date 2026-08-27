from __future__ import annotations

from .character_creation import BasicCharacter, CharacterCreationError, CharacterCreator
from .economy import AREAS, SECTS, SECT_TASKS, EconomyEngine
from .narrator import Narrator
from .progression import ProgressionEngine
from .rules import RuleBook
from .save_manager import SaveManager
from .state import GameState


COMMANDS = "面板 修炼 突破 悟道 洞府 地图 背包 坊市 宗门 技艺 情缘 对话 存档 帮助"


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
        if action.startswith("存档"):
            return self._save(action)
        if action.startswith("读档"):
            return self._load(action)

        if self.state.phase == "breakthrough_talent_choice":
            return self._handle_destiny_choice(action)

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
        trade = EconomyEngine.parse_trade(action)
        if trade is not None:
            return self._trade(*trade)
        if action == "坊市":
            return self._market()
        if action == "宗门":
            return self._sect()
        if action.startswith("拜入"):
            return self._join_sect(action)
        if action.startswith("宗门任务"):
            return self._sect_task(action)

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
        died_of_age = self.state.advance_month(months_used)
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
        died_of_age = self.state.advance_month()
        if died_of_age:
            self.state.phase = "ended"
            self.state.remember("寿元耗尽，坐化")
            self._autosave()
            return f"{self.state.time_label}\n你在行动途中寿元耗尽。\n【坐化结局】享年 {self.state.player.age} 岁。"
        narrative = self.narrator.narrate(action, self.state)
        self.state.remember(action)
        self._autosave()
        return f"{self.state.time_label}\n{narrative}\n\n{self._status()}"

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
            self.state.advance_month()
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
        died_of_age = self.state.advance_month()
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
        died_of_age = self.state.advance_month()
        rewards = [f"灵石 +{result.spirit_stones}"] if result.spirit_stones else []
        rewards.extend(f"{name} +{count}" for name, count in result.rewards.items())
        if result.health_loss:
            rewards.append(f"气血 -{result.health_loss}")
        reward_text = "、".join(rewards) if rewards else "无"
        self.state.remember(f"探索{result.area}：{result.event}；收获 {reward_text}")
        if died_of_age and not result.fatal:
            self.state.phase = "ended"
            self.state.player.condition = "寿元耗尽"
        self._autosave()
        if self.state.phase == "ended":
            ending = "寿元耗尽，坐化荒野" if died_of_age and not result.fatal else result.event
            return f"{self.state.time_label}\n{ending}。\n【陨落结局】道途止于 {result.area}。"
        return (
            f"{self.state.time_label}\n【探索 · {result.area}】\n{result.event}\n"
            f"判定：1d100={result.roll}｜收获：{reward_text}\n\n{self._status()}"
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
        return (
            f"【{player.sect} · {player.sect_rank}】\n贡献：{player.sect_contribution}\n"
            f"任务：{'、'.join(SECT_TASKS)}\n输入：宗门任务 采药"
        )

    def _join_sect(self, action: str) -> str:
        sect = action.removeprefix("拜入").strip()
        try:
            success, roll, chance = EconomyEngine.join_sect(self.state, sect)
        except ValueError as exc:
            return str(exc)
        died_of_age = self.state.advance_month()
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
        died_of_age = self.state.advance_month()
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

    @staticmethod
    def _help() -> str:
        return (
            "【指令大全 · 问道长生】\n"
            "开始游戏｜面板｜修炼｜突破｜存档 [名称]｜读档 [名称]\n"
            "退出：退出／quit／Ctrl+C\n"
            "闭关｜闭关3月｜闭关2年：按修炼公式结算并推进岁月\n"
            "地图｜探索 [地点]｜坊市｜买/卖 [物品] [数量]\n"
            "宗门｜拜入 [宗门]｜宗门任务 [采药/巡逻/猎妖/护送/镇守]\n"
            "其余任何文字都视为自由行动；本地叙事器会推进一个月并记录历史。"
        )
