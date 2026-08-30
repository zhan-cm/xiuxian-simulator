from __future__ import annotations

from dataclasses import dataclass

from .progression import ProgressionEngine
from .state import GameState


SKILL_NAMES = ("炼丹", "炼器", "符箓", "阵法", "灵植")
SKILL_RANKS = ("初窥", "熟练", "精通", "大师", "宗师")
FACILITIES = ("静室", "丹房", "器坊", "灵田", "聚灵阵", "禁制")


@dataclass(frozen=True, slots=True)
class Recipe:
    name: str
    craft: str
    output: str
    output_count: int
    ingredients: dict[str, int]
    base_chance: int
    facility: str


@dataclass(frozen=True, slots=True)
class CraftResult:
    recipe: Recipe
    success: bool
    roll: int
    chance: int
    leveled_up: bool = False


RECIPES = {
    "聚气丹": Recipe("聚气丹", "炼丹", "聚气丹", 2, {"灵药": 2}, 82, "丹房"),
    "疗伤丹": Recipe("疗伤丹", "炼丹", "疗伤丹", 1, {"灵药": 3}, 75, "丹房"),
    "筑基丹": Recipe("筑基丹", "炼丹", "筑基丹", 1, {"灵药": 8, "妖兽材料": 2}, 48, "丹房"),
    "青锋剑": Recipe("青锋剑", "炼器", "青锋剑", 1, {"灵铁": 4, "妖兽材料": 1}, 75, "器坊"),
    "护身法袍": Recipe("护身法袍", "炼器", "护身法袍", 1, {"灵铁": 2, "妖兽材料": 2}, 68, "器坊"),
    "火球符": Recipe("火球符", "符箓", "火球符", 2, {"符纸": 3, "灵药": 1}, 85, "静室"),
    "神行符": Recipe("神行符", "符箓", "神行符", 1, {"符纸": 4, "妖兽材料": 1}, 70, "静室"),
}

FACILITY_COSTS = {
    "静室": (200, {"灵铁": 2}),
    "丹房": (250, {"灵铁": 2}),
    "器坊": (250, {"灵铁": 3}),
    "灵田": (150, {"灵药": 1}),
    "聚灵阵": (500, {"灵铁": 4, "五行灵珠": 1}),
    "禁制": (300, {"灵铁": 3}),
}


class CraftingEngine:
    @staticmethod
    def add_resource(state: GameState, name: str, count: int) -> None:
        state.player.resources[name] = state.player.resources.get(name, 0) + count

    @staticmethod
    def skill_rank(state: GameState, skill: str) -> str:
        level = max(0, min(4, state.player.craft_skills.get(skill, 0)))
        return SKILL_RANKS[level]

    @staticmethod
    def recipe_lines() -> list[str]:
        lines = []
        for recipe in RECIPES.values():
            ingredients = "、".join(f"{name}×{count}" for name, count in recipe.ingredients.items())
            lines.append(f"{recipe.craft} {recipe.name}｜{ingredients} → {recipe.output}×{recipe.output_count}")
        return lines

    @staticmethod
    def success_chance(state: GameState, recipe: Recipe, bonus: int = 0) -> int:
        skill_level = state.player.craft_skills.get(recipe.craft, 0)
        facility_level = state.cave_facilities.get(recipe.facility, 0)
        sense_bonus = (state.player.spirit_sense - 10) * 2
        return max(5, min(98, recipe.base_chance + skill_level * 8 + facility_level * 5 + sense_bonus + bonus))

    @classmethod
    def consume_ingredients(cls, state: GameState, recipe: Recipe) -> None:
        missing = [
            f"{item}×{count}"
            for item, count in recipe.ingredients.items()
            if state.player.resources.get(item, 0) < count
        ]
        if missing:
            raise ValueError("材料不足：" + "、".join(missing))
        for item, count in recipe.ingredients.items():
            state.player.resources[item] -= count
            if state.player.resources[item] <= 0:
                state.player.resources.pop(item, None)

    @classmethod
    def record_success(cls, state: GameState, recipe: Recipe) -> bool:
        cls.add_resource(state, recipe.output, recipe.output_count)
        skill_level = state.player.craft_skills.get(recipe.craft, 0)
        successes = state.player.craft_successes.get(recipe.craft, 0) + 1
        state.player.craft_successes[recipe.craft] = successes
        new_level = min(4, successes // 3)
        leveled_up = new_level > skill_level
        if leveled_up:
            state.player.craft_skills[recipe.craft] = new_level
        if recipe.craft == "炼丹":
            state.player.alchemy_level = state.player.craft_skills.get("炼丹", 0)
        return leveled_up

    @classmethod
    def craft(cls, state: GameState, craft: str, name: str) -> CraftResult:
        if name not in RECIPES or RECIPES[name].craft != craft:
            choices = [recipe.name for recipe in RECIPES.values() if recipe.craft == craft]
            raise ValueError(f"未知{craft}配方。可制作：" + "、".join(choices))
        recipe = RECIPES[name]
        cls.consume_ingredients(state, recipe)
        chance = cls.success_chance(state, recipe)
        roll = ProgressionEngine.deterministic_roll(state, f"craft:{craft}:{name}:{state.turn}")
        success = roll <= chance
        leveled_up = False
        if success:
            leveled_up = cls.record_success(state, recipe)
        return CraftResult(recipe, success, roll, chance, leveled_up)

    @staticmethod
    def upgrade_cost(state: GameState, facility: str) -> tuple[int, dict[str, int]]:
        if facility not in FACILITY_COSTS:
            raise ValueError("未知洞府设施。可升级：" + "、".join(FACILITIES))
        current = state.cave_facilities.get(facility, 0)
        if current >= 3:
            raise ValueError(f"{facility}已升至当前最高 3 级。")
        multiplier = current + 1
        base_stones, base_materials = FACILITY_COSTS[facility]
        return base_stones * multiplier, {name: count * multiplier for name, count in base_materials.items()}

    @classmethod
    def upgrade_facility(cls, state: GameState, facility: str) -> int:
        stones, materials = cls.upgrade_cost(state, facility)
        if state.player.spirit_stones < stones:
            raise ValueError(f"灵石不足：需要 {stones}，当前 {state.player.spirit_stones}。")
        missing = [
            f"{name}×{count}"
            for name, count in materials.items()
            if state.player.resources.get(name, 0) < count
        ]
        if missing:
            raise ValueError("升级材料不足：" + "、".join(missing))
        state.player.spirit_stones -= stones
        for name, count in materials.items():
            state.player.resources[name] -= count
            if state.player.resources[name] <= 0:
                state.player.resources.pop(name, None)
        new_level = state.cave_facilities.get(facility, 0) + 1
        state.cave_facilities[facility] = new_level
        if facility == "聚灵阵":
            state.aura_level = ("普通", "浓郁", "福地", "洞天")[new_level]
        return new_level

    @staticmethod
    def plant(state: GameState, crop: str) -> int:
        if crop != "灵药":
            raise ValueError("当前灵田只支持种植灵药。")
        level = state.cave_facilities.get("灵田", 0)
        if level < 1:
            raise ValueError("尚未建成灵田。")
        if crop in state.spirit_crops:
            raise ValueError("灵田中已有尚未收获的灵药。")
        if state.player.resources.get("灵药", 0) < 1:
            raise ValueError("缺少可作种苗的灵药×1。")
        state.player.resources["灵药"] -= 1
        if state.player.resources["灵药"] <= 0:
            state.player.resources.pop("灵药", None)
        ready_turn = state.turn + max(1, 4 - level)
        state.spirit_crops[crop] = ready_turn
        return ready_turn

    @classmethod
    def harvest(cls, state: GameState, crop: str) -> int:
        if crop not in state.spirit_crops:
            raise ValueError(f"灵田中没有可收获的{crop}。")
        ready_turn = state.spirit_crops[crop]
        if state.turn < ready_turn:
            raise ValueError(f"{crop}尚未成熟，还需 {ready_turn - state.turn} 个月。")
        level = state.cave_facilities.get("灵田", 0)
        count = 3 + level
        cls.add_resource(state, crop, count)
        state.spirit_crops.pop(crop, None)
        successes = state.player.craft_successes.get("灵植", 0) + 1
        state.player.craft_successes["灵植"] = successes
        state.player.craft_skills["灵植"] = min(4, successes // 3)
        return count
