from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .arts import ARTIFACTS
from .state import GameState


@dataclass(frozen=True, slots=True)
class ItemDefinition:
    name: str
    category: str
    rarity: str
    description: str
    usage: str
    effect: Callable[[GameState], str] | None = None


def _restore_health(amount: int) -> Callable[[GameState], str]:
    def apply(state: GameState) -> str:
        player = state.player
        if player.health >= player.health_max:
            raise ValueError("当前气血充盈，无需服用。")
        before = player.health
        player.health = min(player.health_max, player.health + amount)
        return f"气血恢复 {player.health - before} 点"

    return apply


def _restore_spirit(amount: int) -> Callable[[GameState], str]:
    def apply(state: GameState) -> str:
        player = state.player
        if player.spirit >= player.spirit_max:
            raise ValueError("当前灵力充盈，无需服用。")
        before = player.spirit
        player.spirit = min(player.spirit_max, player.spirit + amount)
        return f"灵力恢复 {player.spirit - before} 点"

    return apply


def _gain_cultivation(state: GameState) -> str:
    player = state.player
    if player.cultivation >= player.cultivation_required:
        raise ValueError("当前修为已经圆满，应先完成破境。")
    before = player.cultivation
    amount = 20 + player.realm_index * 5
    player.cultivation = min(player.cultivation_required, player.cultivation + amount)
    return f"修为增长 {player.cultivation - before} 点"


ITEMS: dict[str, ItemDefinition] = {
    "聚气丹": ItemDefinition("聚气丹", "丹药", "凡品", "温养经脉、凝聚灵气的入门丹药。", "服用后增加当前大境界修为。", _gain_cultivation),
    "疗伤丹": ItemDefinition("疗伤丹", "丹药", "良品", "以灵药炼成的疗伤丹，可缓解寻常伤势。", "非战斗时服用恢复 35 点气血；战斗中可通过斗法抉择服用。", _restore_health(35)),
    "灵果": ItemDefinition("灵果", "灵食", "凡品", "山野灵木所结，蕴含少量温和灵气。", "食用后恢复 15 点灵力。", _restore_spirit(15)),
    "烤肉": ItemDefinition("烤肉", "灵食", "凡品", "以灵火烤制的妖兽肉，足以补充体力。", "食用后恢复 12 点气血。", _restore_health(12)),
    "甜糕": ItemDefinition("甜糕", "灵食", "凡品", "坊市常见的精致糕点，也可作为访友薄礼。", "食用后恢复 8 点灵力。", _restore_spirit(8)),
    "清茶": ItemDefinition("清茶", "礼物", "凡品", "清香淡雅，适合论道访友。", "可作为人物赠礼；自己饮用可恢复 10 点灵力。", _restore_spirit(10)),
    "烈酒": ItemDefinition("烈酒", "礼物", "凡品", "酒性炽烈，部分豪迈修士颇为喜爱。", "主要用于人物赠礼。"),
    "剑穗": ItemDefinition("剑穗", "礼物", "凡品", "做工端正的剑饰，常赠予剑修。", "用于人物赠礼。"),
    "山水画卷": ItemDefinition("山水画卷", "礼物", "良品", "笔墨中藏有一缕山水意境。", "用于人物赠礼。"),
    "灵石匣": ItemDefinition("灵石匣", "礼物", "良品", "以温玉制成的灵石收纳匣，礼重而不俗。", "用于人物赠礼。"),
    "奇闻玉简": ItemDefinition("奇闻玉简", "礼物", "良品", "记载九州逸闻的玉简，适合爱好见闻之人。", "用于人物赠礼。"),
    "火球符": ItemDefinition("火球符", "符箓", "凡品", "封存一道火行术法的入门符箓。", "战斗中可直接激发，对敌造成火行伤害。"),
    "神行符": ItemDefinition("神行符", "符箓", "良品", "符中藏有轻身遁影之力。", "战斗遁走时可消耗一张，大幅提高成功率。"),
    "符纸": ItemDefinition("符纸", "材料", "凡品", "承载符文灵力的基础纸材。", "用于修仙百艺中的制符。"),
    "灵药": ItemDefinition("灵药", "材料", "凡品", "可入丹、可栽种的基础灵植。", "用于炼丹、灵田种植与部分委托。"),
    "妖兽材料": ItemDefinition("妖兽材料", "材料", "凡品", "妖兽身上的皮骨、内丹与灵性材料。", "用于炼器与部分委托。"),
    "灵铁": ItemDefinition("灵铁", "材料", "良品", "能够承载灵力的炼器矿材。", "用于炼器和洞府营造。"),
    "血玉": ItemDefinition("血玉", "材料", "良品", "蕴含精纯血气的赤色灵玉。", "可用于交易、赠礼与后续炼制。"),
    "冰莲": ItemDefinition("冰莲", "材料", "珍品", "生于寒潭深处的冰属性灵植。", "可用于交易、赠礼与高阶炼丹。"),
    "雪晶": ItemDefinition("雪晶", "材料", "良品", "凝结寒气的剔透晶石。", "可用于交易与后续炼制。"),
    "筑基丹": ItemDefinition("筑基丹", "破境", "珍品", "炼气修士筑就道基的重要丹药。", "用于人道或地道筑基，不可直接服用。"),
    "凝晶丹": ItemDefinition("凝晶丹", "破境", "珍品", "辅助筑基圆满修士凝结金丹。", "用于金丹大境界突破。"),
    "结丹灵药": ItemDefinition("结丹灵药", "破境", "珍品", "结丹时调和五行、稳定灵台的灵药。", "用于金丹大境界突破。"),
    "结婴丹": ItemDefinition("结婴丹", "破境", "灵品", "金丹化婴时护持神魂的宝丹。", "用于元婴大境界突破。"),
    "具灵丹": ItemDefinition("具灵丹", "破境", "灵品", "使元婴神识具现通灵的高阶丹药。", "用于化神之前的高阶突破。"),
    "化神丹": ItemDefinition("化神丹", "破境", "灵品", "蕴含化神契机的稀世丹药。", "用于化神大境界突破。"),
    "悟道丹": ItemDefinition("悟道丹", "破境", "仙品", "能令人短暂贴近大道脉络。", "用于更高境界突破。"),
    "羽化丹": ItemDefinition("羽化丹", "破境", "仙品", "传闻可洗炼凡躯、渐近羽化。", "用于羽化层次突破。"),
    "登仙丹": ItemDefinition("登仙丹", "破境", "仙品", "仅存于古籍记载的登仙宝丹。", "用于飞升前最后一道大境界。"),
    "天材地宝": ItemDefinition("天材地宝", "奇珍", "珍品", "天地孕育、难以量产的珍贵灵物。", "用于地道以上突破和洞府营造。"),
    "五行灵珠": ItemDefinition("五行灵珠", "奇珍", "灵品", "五行灵气在地脉裂隙中凝成的宝珠。", "用于天道突破和高阶洞府营造。"),
    "道韵": ItemDefinition("道韵", "奇珍", "仙品", "从天地异象中截取的一缕大道痕迹。", "用于最高规格的破境与悟道。"),
}


for artifact in ARTIFACTS.values():
    bonuses: list[str] = []
    if artifact.attack_multiplier != 1:
        bonuses.append(f"攻势 ×{artifact.attack_multiplier:g}")
    if artifact.defense_bonus:
        bonuses.append(f"防御 +{artifact.defense_bonus}")
    if artifact.speed_bonus:
        bonuses.append(f"遁速 {artifact.speed_bonus:+d}")
    if artifact.element:
        bonuses.append(f"{artifact.element}行")
    ITEMS[artifact.name] = ItemDefinition(
        artifact.name,
        "法宝",
        artifact.grade,
        f"{artifact.grade}{artifact.slot}，可纳入当前道法构筑。",
        "装备效果：" + "、".join(bonuses),
    )


class InventoryEngine:
    CATEGORY_ORDER = ("全部", "丹药", "灵食", "法宝", "符箓", "破境", "材料", "奇珍", "礼物", "其他")

    @staticmethod
    def _count(state: GameState, name: str) -> int:
        return state.player.resources.get(name, 0) + state.player.inventory.count(name)

    @staticmethod
    def _consume(state: GameState, name: str) -> None:
        count = state.player.resources.get(name, 0)
        if count > 0:
            if count == 1:
                state.player.resources.pop(name, None)
            else:
                state.player.resources[name] = count - 1
            return
        if name in state.player.inventory:
            state.player.inventory.remove(name)
            return
        raise ValueError(f"乾坤袋中没有{name}。")

    @classmethod
    def use(cls, state: GameState, name: str) -> str:
        definition = ITEMS.get(name)
        if not definition or definition.effect is None:
            raise ValueError(f"{name}不能直接使用；请查看物品详情中的用途。")
        if cls._count(state, name) < 1:
            raise ValueError(f"乾坤袋中没有{name}。")
        result = definition.effect(state)
        cls._consume(state, name)
        return result

    @staticmethod
    def unequip(state: GameState, name: str) -> str:
        player = state.player
        if player.equipped_weapon == name:
            player.equipped_weapon = ""
            return "武器"
        if player.equipped_armor == name:
            player.equipped_armor = ""
            return "护甲"
        raise ValueError(f"当前并未装备{name}。")

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        names = set(state.player.resources) | set(state.player.inventory)
        items: list[dict[str, Any]] = []
        player = state.player
        for name in names:
            count = cls._count(state, name)
            if count <= 0:
                continue
            definition = ITEMS.get(name, ItemDefinition(name, "其他", "凡品", "尚未鉴定的修行物品。", "等待进一步辨识用途。"))
            artifact = ARTIFACTS.get(name)
            equipped = name in {player.equipped_weapon, player.equipped_armor}
            action = ""
            action_label = ""
            disabled_reason = ""
            if artifact:
                action = f"卸下法宝 {name}" if equipped else f"装备法宝 {name}"
                action_label = "卸下" if equipped else "装备"
            elif definition.effect:
                action = f"使用 {name}"
                action_label = "使用"
                if name == "疗伤丹" and player.health >= player.health_max:
                    disabled_reason = "当前气血已满"
                elif name in {"灵果", "甜糕", "清茶"} and player.spirit >= player.spirit_max:
                    disabled_reason = "当前灵力已满"
                elif name == "烤肉" and player.health >= player.health_max:
                    disabled_reason = "当前气血已满"
                elif name == "聚气丹" and player.cultivation >= player.cultivation_required:
                    disabled_reason = "当前修为已圆满"
            items.append(
                {
                    "name": name,
                    "count": count,
                    "category": definition.category,
                    "rarity": definition.rarity,
                    "description": definition.description,
                    "usage": definition.usage,
                    "equipped": equipped,
                    "slot": artifact.slot if artifact else "",
                    "action": action,
                    "action_label": action_label,
                    "actionable": bool(action),
                    "disabled_reason": disabled_reason,
                }
            )
        rarity_rank = {"仙品": 5, "灵品": 4, "珍品": 3, "玄阶": 3, "良品": 2, "黄阶": 1, "凡品": 1}
        items.sort(key=lambda item: (-int(item["equipped"]), -rarity_rank.get(str(item["rarity"]), 0), str(item["category"]), str(item["name"])))
        categories = [category for category in cls.CATEGORY_ORDER if category == "全部" or any(item["category"] == category for item in items)]
        return {
            "items": items,
            "categories": categories,
            "total_types": len(items),
            "total_count": sum(int(item["count"]) for item in items),
            "equipped": {"weapon": player.equipped_weapon, "armor": player.equipped_armor},
        }
