from __future__ import annotations

from dataclasses import dataclass

from .dao import DaoEngine
from .progression import ProgressionEngine
from .state import GameState, PlayerState


GRADE_DIFFICULTY = {"黄阶": 95, "玄阶": 75, "地阶": 55, "天阶": 30, "仙阶": 10}


@dataclass(frozen=True, slots=True)
class Technique:
    name: str
    grade: str
    attack_multiplier: float = 1.0
    defense_bonus: int = 0
    description: str = ""


@dataclass(frozen=True, slots=True)
class Spell:
    name: str
    grade: str
    element: str
    spirit_cost: int
    power_multiplier: float
    description: str = ""


@dataclass(frozen=True, slots=True)
class Artifact:
    name: str
    grade: str
    slot: str
    attack_multiplier: float = 1.0
    defense_bonus: int = 0
    speed_bonus: int = 0
    element: str = ""


@dataclass(frozen=True, slots=True)
class LearningResult:
    name: str
    success: bool
    roll: int
    chance: int
    manual: str


TECHNIQUES = {
    "聚气诀": Technique("聚气诀", "黄阶", description="基础吐纳法门"),
    "青木长生诀": Technique("青木长生诀", "玄阶", defense_bonus=4, description="木行绵长，护体养生"),
    "赤炎真经": Technique("赤炎真经", "玄阶", attack_multiplier=1.15, description="火法威力更盛"),
    "太虚剑典": Technique("太虚剑典", "地阶", attack_multiplier=1.28, defense_bonus=3, description="剑意攻守一体"),
    "五行道藏": Technique("五行道藏", "天阶", attack_multiplier=1.4, defense_bonus=10, description="五行轮转，生克随心"),
}

SPELLS = {
    "流火术": Spell("流火术", "黄阶", "火", 20, 1.45, "凝火伤敌"),
    "青木缚灵术": Spell("青木缚灵术", "玄阶", "木", 18, 1.35, "木气缠身"),
    "庚金剑气": Spell("庚金剑气", "玄阶", "金", 25, 1.7, "锋锐破甲"),
    "玄水剑诀": Spell("玄水剑诀", "地阶", "水", 30, 1.95, "水势连绵"),
    "厚土印诀": Spell("厚土印诀", "地阶", "土", 35, 2.1, "重若山岳"),
}

ARTIFACTS = {
    "青锋剑": Artifact("青锋剑", "黄阶", "武器", attack_multiplier=1.1, element="金"),
    "玄铁剑": Artifact("玄铁剑", "玄阶", "武器", attack_multiplier=1.25, speed_bonus=-1, element="金"),
    "火云刃": Artifact("火云刃", "玄阶", "武器", attack_multiplier=1.22, element="火"),
    "护身法袍": Artifact("护身法袍", "黄阶", "护甲", defense_bonus=5),
    "流云衣": Artifact("流云衣", "玄阶", "护甲", defense_bonus=8, speed_bonus=3),
    "玄龟甲": Artifact("玄龟甲", "玄阶", "护甲", defense_bonus=16, speed_bonus=-2),
}


class ArtsEngine:
    @staticmethod
    def manual_name(name: str) -> str:
        return f"{name}残卷"

    @staticmethod
    def known(player: PlayerState, name: str) -> bool:
        return name in player.known_techniques or name in player.known_spells

    @classmethod
    def learn(cls, state: GameState, name: str) -> LearningResult:
        if name in TECHNIQUES:
            definition = TECHNIQUES[name]
            collection = state.player.known_techniques
        elif name in SPELLS:
            definition = SPELLS[name]
            collection = state.player.known_spells
        else:
            raise ValueError("未知功法或法术：" + name)
        if name in collection:
            raise ValueError(f"已经掌握{name}。")
        manual = cls.manual_name(name)
        if state.player.resources.get(manual, 0) < 1:
            raise ValueError(f"缺少参悟所需的{manual}。")
        state.player.resources[manual] -= 1
        if state.player.resources[manual] <= 0:
            state.player.resources.pop(manual, None)
        base = GRADE_DIFFICULTY[definition.grade]
        chance = max(5, min(99, base + (state.player.comprehension - 10) * 3))
        roll = ProgressionEngine.deterministic_roll(state, f"learn:{name}")
        success = roll <= chance
        if success:
            collection.append(name)
        return LearningResult(name, success, roll, chance, manual)

    @staticmethod
    def equip_main_technique(player: PlayerState, name: str) -> None:
        if name not in player.known_techniques:
            raise ValueError(f"尚未掌握功法：{name}")
        definition = TECHNIQUES[name]
        player.primary_technique = name
        player.primary_technique_grade = definition.grade
        player.equipped_auxiliary_techniques = [item for item in player.equipped_auxiliary_techniques if item != name]

    @staticmethod
    def equip_auxiliary_technique(player: PlayerState, name: str, slot: int | None = None) -> None:
        if name not in player.known_techniques:
            raise ValueError(f"尚未掌握功法：{name}")
        if name == player.primary_technique:
            raise ValueError("主修功法不能同时作为辅修。")
        auxiliary = player.equipped_auxiliary_techniques
        if name in auxiliary:
            raise ValueError(f"已经辅修{name}。")
        if slot is None:
            if len(auxiliary) >= 2:
                raise ValueError("两个辅修位均已占用，请指定替换位置 1 或 2。")
            auxiliary.append(name)
            return
        if slot not in {1, 2}:
            raise ValueError("辅修位置只能是 1 或 2。")
        while len(auxiliary) < slot:
            auxiliary.append("")
        auxiliary[slot - 1] = name
        player.equipped_auxiliary_techniques = [item for item in auxiliary if item]

    @staticmethod
    def equip_spell(player: PlayerState, name: str) -> None:
        if name not in player.known_spells:
            raise ValueError(f"尚未掌握法术：{name}")
        player.equipped_spell = name

    @staticmethod
    def equip_artifact(player: PlayerState, name: str) -> None:
        if name not in ARTIFACTS:
            raise ValueError(f"未知法宝：{name}")
        if player.resources.get(name, 0) < 1:
            raise ValueError(f"乾坤袋中没有{name}。")
        artifact = ARTIFACTS[name]
        if artifact.slot == "武器":
            player.equipped_weapon = name
        else:
            player.equipped_armor = name

    @staticmethod
    def spell(player: PlayerState, requested: str = "") -> Spell:
        name = requested or player.equipped_spell
        if not name:
            raise ValueError("尚未装备法术。")
        if name not in player.known_spells:
            raise ValueError(f"尚未掌握法术：{name}")
        return SPELLS[name]

    @staticmethod
    def attack_multiplier(player: PlayerState, state: GameState | None = None) -> float:
        main = TECHNIQUES.get(player.primary_technique, TECHNIQUES["聚气诀"])
        multiplier = main.attack_multiplier * (1 + DaoEngine.player_level(player, "剑道") * 0.05)
        if state is not None:
            from .art_mastery import ArtMasteryEngine

            multiplier *= ArtMasteryEngine.technique_combat_multiplier(state, main.name)
        for name in player.equipped_auxiliary_techniques:
            auxiliary = TECHNIQUES.get(name)
            if auxiliary:
                multiplier *= 1 + (auxiliary.attack_multiplier - 1) * 0.5
                if state is not None:
                    mastery = ArtMasteryEngine.technique_combat_multiplier(state, auxiliary.name)
                    multiplier *= 1 + (mastery - 1) * 0.5
        weapon = ARTIFACTS.get(player.equipped_weapon)
        if weapon:
            artifact_scale = 1 + DaoEngine.player_level(player, "器道") * 0.05
            growth = 0.0
            if state is not None:
                from .artifact_growth import ArtifactGrowthEngine

                growth = ArtifactGrowthEngine.attack_bonus(state, weapon.name)
            multiplier *= 1 + (weapon.attack_multiplier - 1) * artifact_scale + growth
        return multiplier

    @staticmethod
    def defense_bonus(player: PlayerState, state: GameState | None = None) -> int:
        main = TECHNIQUES.get(player.primary_technique, TECHNIQUES["聚气诀"])
        bonus = main.defense_bonus
        if state is not None:
            from .art_mastery import ArtMasteryEngine

            bonus += round(main.defense_bonus * (ArtMasteryEngine.technique_combat_multiplier(state, main.name) - 1))
        for name in player.equipped_auxiliary_techniques:
            auxiliary = TECHNIQUES.get(name)
            if auxiliary:
                bonus += auxiliary.defense_bonus // 2
                if state is not None:
                    bonus += round(auxiliary.defense_bonus * (ArtMasteryEngine.technique_combat_multiplier(state, name) - 1) * 0.5)
        armor = ARTIFACTS.get(player.equipped_armor)
        artifact_scale = 1 + DaoEngine.player_level(player, "器道") * 0.05
        growth = 0
        if armor and state is not None:
            from .artifact_growth import ArtifactGrowthEngine

            growth = ArtifactGrowthEngine.defense_bonus(state, armor.name)
        return bonus + (round(armor.defense_bonus * artifact_scale) if armor else 0) + growth

    @staticmethod
    def effective_speed(player: PlayerState, state: GameState | None = None) -> int:
        weapon = ARTIFACTS.get(player.equipped_weapon)
        armor = ARTIFACTS.get(player.equipped_armor)
        growth = 0
        if state is not None:
            from .artifact_growth import ArtifactGrowthEngine

            for artifact in (weapon, armor):
                if artifact:
                    growth += ArtifactGrowthEngine.speed_bonus(state, artifact.name)
        return player.speed + (weapon.speed_bonus if weapon else 0) + (armor.speed_bonus if armor else 0) + growth

    @staticmethod
    def attack_element(player: PlayerState, fallback: str) -> str:
        weapon = ARTIFACTS.get(player.equipped_weapon)
        return weapon.element if weapon and weapon.element else fallback
