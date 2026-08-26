from __future__ import annotations

import re
from dataclasses import dataclass

from .state import PlayerState


BACKGROUNDS = (
    "农家子",
    "猎户之后",
    "商贾之家",
    "官宦子弟",
    "将门之后",
    "没落世家",
    "市井孤儿",
    "书香门第",
    "方外遗孤",
    "妖族后裔",
)

DAO_PATHS = (
    "问道飞升",
    "逍遥长生",
    "快意恩仇",
    "守护所爱",
    "问鼎天下",
    "随心所欲",
)

CONSTITUTIONS = (
    "先天道体",
    "剑灵体",
    "九阳圣体",
    "冰魄灵体",
    "玄阴体",
    "纯阳体",
    "混沌体",
    "凡体",
)

ATTRIBUTES = {
    "资质": "aptitude",
    "悟性": "comprehension",
    "神识": "spirit_sense",
    "遁速": "speed",
    "道心": "dao_heart",
    "仙缘": "fortune",
}

TALENTS = {
    "天资聪颖": ("aptitude", 3),
    "过目不忘": ("comprehension", 3),
    "身轻如燕": ("speed", 3),
    "天生道心": ("dao_heart", 3),
    "气运加身": ("fortune", 3),
    "神识过人": ("spirit_sense", 3),
    "百脉俱通": ("spirit_max", 50),
    "钢筋铁骨": ("health_max", 80),
    "药理通神": ("alchemy_level", 1),
    "桃花运": ("initial_affinity_bonus", 20),
    "体弱多病": ("health_max", -50),
}

DAO_NAMES = {
    "问道飞升": "清微",
    "逍遥长生": "长闲",
    "快意恩仇": "照胆",
    "守护所爱": "守一",
    "问鼎天下": "凌霄",
    "随心所欲": "无拘",
}


class CharacterCreationError(ValueError):
    pass


def parse_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for part in re.split(r"[;；\n]+", text.strip()):
        item = part.strip()
        if not item:
            continue
        match = re.match(r"^\s*([^:=：=]+?)\s*[:=：]\s*(.+?)\s*$", item)
        if not match:
            raise CharacterCreationError(f"无法识别“{item}”，请使用“字段=内容”并以分号分隔。")
        fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def resolve_choice(value: str, choices: tuple[str, ...], label: str) -> str:
    normalized = value.strip()
    if normalized.isdigit():
        index = int(normalized)
        if 1 <= index <= len(choices):
            return choices[index - 1]
    if normalized in choices:
        return normalized
    raise CharacterCreationError(f"{label}“{value}”无效，可选：{'／'.join(choices)}")


@dataclass(frozen=True, slots=True)
class BasicCharacter:
    name: str
    gender: str
    age: int
    appearance_description: str
    background: str
    dao_path: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "appearance_description": self.appearance_description,
            "background": self.background,
            "dao_path": self.dao_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "BasicCharacter":
        return cls(
            name=str(data["name"]),
            gender=str(data["gender"]),
            age=int(data["age"]),
            appearance_description=str(data["appearance_description"]),
            background=str(data["background"]),
            dao_path=str(data["dao_path"]),
        )


class CharacterCreator:
    BASIC_REQUIRED = ("姓名", "性别", "年龄", "相貌", "出身", "道途")
    TRAIT_REQUIRED = ("灵根", "体质", *ATTRIBUTES.keys(), "天赋")

    @classmethod
    def parse_basic(cls, text: str) -> BasicCharacter:
        fields = parse_fields(text)
        missing = [name for name in cls.BASIC_REQUIRED if name not in fields]
        if missing:
            raise CharacterCreationError("第一面缺少字段：" + "、".join(missing))

        name = fields["姓名"].strip()
        if not 1 <= len(name) <= 12:
            raise CharacterCreationError("姓名长度应为 1~12 个字符。")
        gender = fields["性别"].strip()
        if not gender:
            raise CharacterCreationError("性别不可为空，可填写男、女或自定义。")
        try:
            age = int(fields["年龄"])
        except ValueError as exc:
            raise CharacterCreationError("年龄必须是 16~60 的整数。") from exc
        if not 16 <= age <= 60:
            raise CharacterCreationError("年龄必须在 16~60 之间。")

        return BasicCharacter(
            name=name,
            gender=gender,
            age=age,
            appearance_description=fields["相貌"],
            background=resolve_choice(fields["出身"], BACKGROUNDS, "出身"),
            dao_path=resolve_choice(fields["道途"], DAO_PATHS, "道途"),
        )

    @classmethod
    def finish(cls, basic: BasicCharacter, text: str) -> PlayerState:
        fields = parse_fields(text)
        missing = [name for name in cls.TRAIT_REQUIRED if name not in fields]
        if missing:
            raise CharacterCreationError("第二面缺少字段：" + "、".join(missing))

        constitution = resolve_choice(fields["体质"], CONSTITUTIONS, "体质")
        values: dict[str, int] = {}
        for label, attribute in ATTRIBUTES.items():
            try:
                value = int(fields[label])
            except ValueError as exc:
                raise CharacterCreationError(f"{label}必须是 1~15 的整数。") from exc
            if not 1 <= value <= 15:
                raise CharacterCreationError(f"{label}必须在 1~15 之间。")
            values[attribute] = value
        if sum(values.values()) != 60:
            raise CharacterCreationError(f"六维初始值合计必须为 60，当前为 {sum(values.values())}。")

        talents = [item.strip() for item in re.split(r"[、/|，,]+", fields["天赋"]) if item.strip()]
        unknown = [talent for talent in talents if talent not in TALENTS]
        if unknown:
            raise CharacterCreationError("未知天赋：" + "、".join(unknown))
        if len(set(talents)) != len(talents):
            raise CharacterCreationError("同一天赋不可重复选择。")
        talent_cost = sum(-2 if talent == "体弱多病" else 1 for talent in talents)
        if talent_cost != 5:
            raise CharacterCreationError(f"天赋点必须正好使用 5 点，当前使用 {talent_cost} 点。")

        player = PlayerState(
            name=basic.name,
            dao_name=DAO_NAMES[basic.dao_path],
            gender=basic.gender,
            age=basic.age,
            appearance=cls._appearance_level(basic.appearance_description),
            appearance_description=basic.appearance_description,
            background=basic.background,
            dao_path=basic.dao_path,
            spiritual_root=fields["灵根"],
            constitution=constitution,
            talents=talents,
            character_notes=f"{basic.background}；{basic.dao_path}",
            **values,
        )
        cls._apply_background(player)
        cls._apply_talents(player)
        cls._apply_constitution(player)
        cls._cap_attributes(player)
        player.health = player.health_max
        player.spirit = player.spirit_max
        return player

    @staticmethod
    def default_player() -> PlayerState:
        basic = BasicCharacter("沈砚", "自定义", 16, "眉目清秀，神情沉静", "农家子", "问道飞升")
        return CharacterCreator.finish(
            basic,
            "灵根=木火双灵根；体质=凡体；资质=10；悟性=10；神识=10；"
            "遁速=10；道心=10；仙缘=10；天赋=天资聪颖、过目不忘、身轻如燕、天生道心、气运加身",
        )

    @staticmethod
    def _appearance_level(description: str) -> str:
        for level in ("仙姿", "超凡", "出众", "清秀", "凡姿"):
            if level in description:
                return level
        return "清秀"

    @staticmethod
    def _apply_background(player: PlayerState) -> None:
        if player.background == "农家子":
            player.dao_heart += 2
        elif player.background == "猎户之后":
            player.health_max += 20
        elif player.background == "商贾之家":
            player.spirit_stones += 300
            player.fortune += 1
        elif player.background == "官宦子弟":
            player.reputation += 20
        elif player.background == "将门之后":
            player.dao_heart += 1
            player.comprehension += 1
        elif player.background == "没落世家":
            player.inventory.append("先祖残卷（随机玄阶功法）")
        elif player.background == "市井孤儿":
            player.speed += 2
        elif player.background == "书香门第":
            player.comprehension += 3
        elif player.background == "方外遗孤":
            player.aptitude += 2
        elif player.background == "妖族后裔":
            player.tags.append("半妖之身")

    @staticmethod
    def _apply_talents(player: PlayerState) -> None:
        for talent in player.talents:
            attribute, delta = TALENTS[talent]
            setattr(player, attribute, getattr(player, attribute) + delta)

    @staticmethod
    def _apply_constitution(player: PlayerState) -> None:
        if player.constitution == "先天道体":
            player.modifiers["cultivation_multiplier"] = 1.5
        elif player.constitution == "九阳圣体":
            player.modifiers["fire_damage_multiplier"] = 1.3
        elif player.constitution == "冰魄灵体":
            player.modifiers["ice_damage_multiplier"] = 1.3
        elif player.constitution == "剑灵体":
            player.tags.append("剑道亲和")
        elif player.constitution in {"玄阴体", "纯阳体"}:
            player.tags.append("双修增益")
        elif player.constitution == "混沌体":
            player.tags.append("五行皆通")

    @staticmethod
    def _cap_attributes(player: PlayerState) -> None:
        for attribute in ATTRIBUTES.values():
            setattr(player, attribute, min(20, max(1, getattr(player, attribute))))

