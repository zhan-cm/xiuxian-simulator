from __future__ import annotations

from .character_creation import BasicCharacter, CharacterCreationError, CharacterCreator
from .narrator import Narrator
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

        if self.state.phase == "new":
            return "世界尚未开启。请先输入“开始游戏”。"
        if self.state.phase in {"character_creation", "character_creation_basic"}:
            return self._handle_basic_creation(action)
        if self.state.phase == "character_creation_traits":
            return self._handle_trait_creation(action)
        if self.state.phase == "ended":
            return "此世已终。输入“开始游戏”可创建新的轮回。"
        if action == "修炼":
            return self._cultivate()
        if action == "突破":
            return self._breakthrough_hint()

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

    def _cultivate(self) -> str:
        player = self.state.player
        constitution_multiplier = player.modifiers.get("cultivation_multiplier", 1.0)
        gain = max(1, round(10 * (1 + player.aptitude * 0.05) * 1.3 * constitution_multiplier))
        before = player.cultivation
        player.cultivation = min(player.cultivation_required, before + gain)
        self.state.advance_month()
        self.state.remember(f"闭关修炼一月，修为 +{player.cultivation - before}")
        self._autosave()
        return (
            f"{self.state.time_label}\n你在石屋中吐纳一月，灵气沿经脉缓缓流转。\n"
            f"修为 +{player.cultivation - before}（{player.cultivation}/{player.cultivation_required}）\n\n"
            + self._status()
        )

    def _free_action(self, action: str) -> str:
        self.state.advance_month()
        narrative = self.narrator.narrate(action, self.state)
        self.state.remember(action)
        self._autosave()
        return f"{self.state.time_label}\n{narrative}\n\n{self._status()}"

    def _breakthrough_hint(self) -> str:
        player = self.state.player
        if player.cultivation < player.cultivation_required:
            return (
                f"修为尚未圆满：{player.cultivation}/{player.cultivation_required}。"
                "突破必须有失败与代价，V0.1 不会允许提前无风险破境。"
            )
        return "修为已圆满。人道、地道、天道三条突破路线的完整判定将在下一阶段实现；当前不会伪造成功。"

    def _status(self) -> str:
        p = self.state.player
        return (
            f"【状态卡 · 第 {self.state.turn} 回合 · {self.state.time_label}】\n"
            f"道号 {p.dao_name}｜姓名 {p.name}｜性别 {p.gender}｜年龄 {p.age}/{p.lifespan}\n"
            f"境界 {p.realm}｜宗门 {p.sect}｜所在地 {p.location}\n"
            f"出身 {p.background}｜道途 {p.dao_path}｜体质 {p.constitution}\n"
            f"资质 {p.aptitude} 悟性 {p.comprehension} 神识 {p.spirit_sense} "
            f"遁速 {p.speed} 道心 {p.dao_heart} 仙缘 {p.fortune}\n"
            f"灵根 {p.spiritual_root}｜气血 {p.health}/{p.health_max}｜"
            f"灵力 {p.spirit}/{p.spirit_max}｜修为 {p.cultivation}/{p.cultivation_required}\n"
            f"灵石 {p.spirit_stones}｜功德 {p.merit}｜业力 {p.karma}｜声望 {p.reputation}｜异常 {p.condition}\n"
            f"天赋：{'、'.join(p.talents) if p.talents else '无'}\n"
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
            "其余任何文字都视为自由行动；V0.1 本地叙事器会推进一个月并记录历史。"
        )
