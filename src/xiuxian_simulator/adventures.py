from __future__ import annotations

from dataclasses import dataclass, field

from .dao import DaoEngine
from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class SecretRealm:
    name: str
    minimum_realm: int
    danger: int
    description: str
    resource: str


SECRET_REALMS = {
    "通灵秘境": SecretRealm("通灵秘境", 0, 20, "林海灵雾终年不散，适合初入仙途者历练。", "灵药"),
    "上古洞府": SecretRealm("上古洞府", 1, 35, "残阵与机关仍在运转，洞府深处藏有前人遗珍。", "灵铁"),
    "心魔幻境": SecretRealm("心魔幻境", 2, 50, "所见皆由执念而生，道心不坚者容易迷失。", "道韵"),
    "虚空裂缝": SecretRealm("虚空裂缝", 4, 70, "空间乱流吞噬万物，具灵以下踏入几无生还可能。", "天材地宝"),
}

RANDOM_EVENTS = (
    "神秘老者赠丹",
    "秘境入口忽现",
    "天降灵雨",
    "上古残碑共鸣",
    "妖兽袭村",
    "陌生传音符",
    "被人认错身份",
    "心魔暗生",
)


@dataclass(frozen=True, slots=True)
class AdventureResult:
    success: bool
    roll: int
    chance: int
    stage: int
    completed: bool = False
    health_loss: int = 0
    fatal: bool = False
    rewards: dict[str, int] = field(default_factory=dict)
    spirit_stones: int = 0


@dataclass(frozen=True, slots=True)
class RandomEncounter:
    triggered: bool
    roll: int
    title: str = ""
    description: str = ""


class AdventureEngine:
    STAGE_NAMES = ("秘境外围", "阵法核心", "传承深处")

    @staticmethod
    def list_lines() -> list[str]:
        lines = []
        for realm in SECRET_REALMS.values():
            requirement = "炼气可入" if realm.minimum_realm == 0 else f"至少{realm.minimum_realm + 1}阶大境界"
            lines.append(f"{realm.name}｜{requirement}｜危险度 {realm.danger}｜{realm.description}")
        return lines

    @classmethod
    def prepare(cls, state: GameState, name: str) -> SecretRealm:
        if name not in SECRET_REALMS:
            raise ValueError("未知秘境。可选：" + "、".join(SECRET_REALMS))
        realm = SECRET_REALMS[name]
        if state.player.realm_index < realm.minimum_realm:
            raise ValueError(
                f"【致命危险】{name}至少需要第 {realm.minimum_realm + 1} 大境界；"
                f"当前仅为{state.player.realm}，入口威压已足以致命。"
            )
        state.adventure = {
            "name": name,
            "stage": 0,
            "rewards": {},
            "spirit_stones": 0,
            "started_turn": state.turn,
        }
        state.phase = "adventure_ready"
        return realm

    @staticmethod
    def confirm(state: GameState) -> None:
        if state.phase != "adventure_ready" or not state.adventure:
            raise ValueError("当前没有等待确认的秘境。")
        state.phase = "adventure"

    @staticmethod
    def cancel(state: GameState) -> None:
        state.adventure = {}
        state.phase = "playing"

    @staticmethod
    def chance(state: GameState, mode: str) -> int:
        if mode not in {"谨慎探索", "强行探索"}:
            raise ValueError("秘境中请选择“谨慎探索”或“强行探索”。")
        realm = SECRET_REALMS[state.adventure["name"]]
        base = 86 if mode == "谨慎探索" else 66
        advantage = max(0, state.player.realm_index - realm.minimum_realm) * 8
        fortune = state.player.fortune - 10
        stage_penalty = int(state.adventure.get("stage", 0)) * 4
        dao_bonus = DaoEngine.adventure_bonus(state)
        return max(5, min(95, base - realm.danger // 5 + advantage + fortune + dao_bonus - stage_penalty))

    @classmethod
    def resolve(cls, state: GameState, mode: str) -> AdventureResult:
        if state.phase != "adventure" or not state.adventure:
            raise ValueError("当前不在秘境探索中。")
        realm = SECRET_REALMS[state.adventure["name"]]
        stage_index = int(state.adventure.get("stage", 0))
        if stage_index >= len(cls.STAGE_NAMES):
            raise ValueError("此秘境已经探索完毕。")
        chance = cls.chance(state, mode)
        roll = ProgressionEngine.deterministic_roll(
            state, f"secret-realm:{realm.name}:{stage_index}:{mode}"
        )
        if roll > chance:
            health_loss = max(8, realm.danger // 2 + stage_index * 5 + (8 if mode == "强行探索" else 0))
            state.player.health = max(0, state.player.health - health_loss)
            fatal = state.player.health <= 0
            state.player.condition = "秘境重伤" if not fatal else "陨落于秘境"
            state.adventure = {}
            state.phase = "ended" if fatal else "playing"
            return AdventureResult(False, roll, chance, stage_index + 1, health_loss=health_loss, fatal=fatal)

        multiplier = 2 if mode == "强行探索" else 1
        reward_count = (stage_index + 1) * multiplier
        stones = (20 + realm.danger // 2) * multiplier
        pending = state.adventure.setdefault("rewards", {})
        pending[realm.resource] = int(pending.get(realm.resource, 0)) + reward_count
        state.adventure["spirit_stones"] = int(state.adventure.get("spirit_stones", 0)) + stones
        state.adventure["stage"] = stage_index + 1
        completed = state.adventure["stage"] >= len(cls.STAGE_NAMES)
        rewards = {realm.resource: reward_count}
        if completed:
            bonus_item = f"{realm.name}传承"
            state.adventure["rewards"][bonus_item] = 1
            state.adventure["spirit_stones"] += 50 + realm.danger
            rewards[bonus_item] = 1
            cls._secure_pending(state)
            state.adventure = {}
            state.phase = "playing"
        return AdventureResult(True, roll, chance, stage_index + 1, completed, rewards=rewards, spirit_stones=stones)

    @classmethod
    def leave(cls, state: GameState) -> tuple[dict[str, int], int]:
        if state.phase != "adventure" or not state.adventure:
            raise ValueError("当前不在秘境探索中。")
        rewards = dict(state.adventure.get("rewards", {}))
        stones = int(state.adventure.get("spirit_stones", 0))
        cls._secure_pending(state)
        state.adventure = {}
        state.phase = "playing"
        return rewards, stones

    @staticmethod
    def _secure_pending(state: GameState) -> None:
        for item, count in state.adventure.get("rewards", {}).items():
            if count > 0:
                state.player.resources[item] = state.player.resources.get(item, 0) + int(count)
        state.player.spirit_stones += int(state.adventure.get("spirit_stones", 0))

    @staticmethod
    def random_encounter(state: GameState, context: str) -> RandomEncounter:
        roll = ProgressionEngine.deterministic_roll(state, f"random-encounter:{state.turn}:{context}")
        if roll > 20:
            return RandomEncounter(False, roll)
        title = RANDOM_EVENTS[(roll - 1) % len(RANDOM_EVENTS)]
        player = state.player
        if title == "神秘老者赠丹":
            player.resources["聚气丹"] = player.resources.get("聚气丹", 0) + 1
            description = "一位神秘老者留下聚气丹一枚，转眼消失在人群中。"
        elif title == "秘境入口忽现":
            description = "山壁间浮现短暂的空间涟漪，似乎在提醒你留意附近秘境。"
        elif title == "天降灵雨":
            gain = min(20, max(0, player.cultivation_required - player.cultivation))
            player.cultivation += gain
            description = f"灵雨洗涤经脉，修为增长 {gain} 点。"
        elif title == "上古残碑共鸣":
            player.comprehension = min(30, player.comprehension + 1)
            insight = DaoEngine.gain_insight(state, 10, "上古残碑共鸣")
            description = f"残碑道纹一闪即逝，你的悟性永久提升 1 点，感悟 +{insight}。"
        elif title == "妖兽袭村":
            player.health = max(1, player.health - 8)
            player.reputation += 2
            description = "你协助村民击退妖兽，气血 -8，声望 +2。"
        elif title == "陌生传音符":
            before = player.spirit
            player.spirit = min(player.spirit_max, player.spirit + 20)
            description = f"传音符中藏有凝神法门，灵力恢复 {player.spirit - before} 点。"
        elif title == "被人认错身份":
            player.spirit_stones += 15
            description = "一场误会最终化解，对方留下 15 枚灵石赔礼。"
        else:
            player.condition = "心魔波动"
            description = "旧念忽然翻涌，道心蒙尘；异常状态变为“心魔波动”。"
        return RandomEncounter(True, roll, title, description)
