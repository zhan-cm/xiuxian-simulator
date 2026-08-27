from __future__ import annotations

from dataclasses import dataclass, field

from .arts import ArtsEngine
from .progression import ProgressionEngine, REALMS, STAGES
from .state import GameState


ELEMENT_OVERCOMES = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}


@dataclass(frozen=True, slots=True)
class EnemyTemplate:
    name: str
    realm_index: int
    stage_index: int
    health: int
    speed: int
    power: int
    defense: int
    element: str
    loot: dict[str, int] = field(default_factory=dict)
    spirit_stones: int = 0


ENEMIES = {
    "噬灵獾": EnemyTemplate("噬灵獾", 0, 0, 70, 8, 17, 3, "土", {"妖兽材料": 1}),
    "铁甲妖狼": EnemyTemplate("铁甲妖狼", 0, 2, 120, 14, 24, 7, "金", {"妖兽材料": 2}),
    "雾隐妖蟒": EnemyTemplate("雾隐妖蟒", 1, 1, 220, 12, 38, 15, "水", {"天材地宝": 1}, 80),
    "阴煞尸傀": EnemyTemplate("阴煞尸傀", 2, 1, 360, 8, 58, 26, "土", {"五行灵珠": 1}, 160),
    "山野劫修": EnemyTemplate("山野劫修", 0, 1, 90, 10, 21, 5, "火", {"聚气丹": 1}, 60),
    "青云宗外门弟子": EnemyTemplate("青云宗外门弟子", 0, 2, 105, 12, 23, 6, "木"),
    "筑基客卿": EnemyTemplate("筑基客卿", 1, 1, 210, 15, 40, 16, "金", {"筑基丹": 1}, 120),
    "金丹真人": EnemyTemplate("金丹真人", 3, 0, 520, 18, 82, 40, "火", {"结丹灵药": 1}, 500),
}


@dataclass(frozen=True, slots=True)
class StrikeResult:
    hit: bool
    hit_roll: int
    hit_chance: int
    critical: bool
    damage: int
    realm_multiplier: float
    element_multiplier: float


@dataclass(frozen=True, slots=True)
class CombatRoundResult:
    action: str
    player_text: str
    enemy_text: str
    escaped: bool = False
    victory: bool = False
    defeat: bool = False
    fatal: bool = False


class CombatEngine:
    @staticmethod
    def player_element(state: GameState) -> str:
        for element in "金木水火土":
            if element in state.player.spiritual_root:
                return element
        return "木"

    @staticmethod
    def realm_multiplier(attacker_realm: int, attacker_stage: int, defender_realm: int, defender_stage: int) -> float:
        difference = attacker_realm - defender_realm
        if difference <= -2:
            return 0.05
        if difference == -1:
            return 0.4
        if difference == 0:
            return max(0.7, min(1.35, 1.0 + (attacker_stage - defender_stage) * 0.12))
        if difference == 1:
            return 1.8
        return 3.5

    @staticmethod
    def element_multiplier(attacker: str, defender: str) -> float:
        if ELEMENT_OVERCOMES.get(attacker) == defender:
            return 1.3
        if ELEMENT_OVERCOMES.get(defender) == attacker:
            return 0.8
        return 1.0

    @staticmethod
    def threat_text(state: GameState) -> str:
        combat = state.combat
        difference = int(combat["enemy_realm_index"]) - state.player.realm_index
        if difference >= 2:
            return "对方高出至少两个大境界，你的全力几乎无法伤及对方；正面开战近乎送死。"
        if difference == 1:
            return "正面交手胜算极低，对方威压令你窒息；除非另有克制手段，应优先遁走。"
        if difference == 0:
            stage_difference = int(combat["enemy_stage_index"]) - state.player.stage_index
            return "同境尚可一战，但胜负取决于遁速、五行克制与临场选择。" if stage_difference <= 1 else "同一大境界但对方修为明显更深，胜算偏低。"
        return "你占据境界优势，仍需防备对方的法术与逃命手段。"

    @classmethod
    def prepare(cls, state: GameState, enemy_name: str, mode: str = "生死", source: str = "challenge") -> None:
        if enemy_name not in ENEMIES:
            raise ValueError("未知对手。可选择：" + "、".join(ENEMIES))
        enemy = ENEMIES[enemy_name]
        state.combat = {
            "enemy_name": enemy.name,
            "enemy_realm_index": enemy.realm_index,
            "enemy_stage_index": enemy.stage_index,
            "enemy_health": enemy.health,
            "enemy_health_max": enemy.health,
            "enemy_speed": enemy.speed,
            "enemy_power": enemy.power,
            "enemy_defense": enemy.defense,
            "enemy_element": enemy.element,
            "mode": mode,
            "source": source,
            "round": 0,
            "player_observed": False,
            "player_charge": 0,
            "loot": dict(enemy.loot),
            "loot_spirit_stones": enemy.spirit_stones,
        }
        state.phase = "combat_ready"

    @staticmethod
    def enemy_realm_label(state: GameState) -> str:
        combat = state.combat
        return f"{REALMS[int(combat['enemy_realm_index'])]}·{STAGES[int(combat['enemy_stage_index'])]}"

    @classmethod
    def enemy_panel(cls, state: GameState) -> str:
        combat = state.combat
        return (
            f"【敌情面板 · {combat['enemy_name']}】\n"
            f"境界 {cls.enemy_realm_label(state)}｜气血 {combat['enemy_health']}/{combat['enemy_health_max']}｜"
            f"遁速 {combat['enemy_speed']}｜五行 {combat['enemy_element']}\n"
            f"胜算：{cls.threat_text(state)}\n"
            "选择：开战／遁走／离开（主动挑战时可离开）"
        )

    @classmethod
    def start(cls, state: GameState) -> str:
        if state.phase != "combat_ready" or not state.combat:
            raise ValueError("当前没有待确认的战斗。")
        state.phase = "combat"
        state.combat["round"] = 1
        return cls.combat_panel(state)

    @classmethod
    def combat_panel(cls, state: GameState) -> str:
        combat = state.combat
        return (
            f"【战斗 · 第 {combat['round']} 轮】\n"
            f"你：气血 {state.player.health}/{state.player.health_max}｜灵力 {state.player.spirit}/{state.player.spirit_max}｜"
            f"蓄势 {combat['player_charge']}/2｜法术 {state.player.equipped_spell or '无'}\n"
            f"{combat['enemy_name']}：气血 {combat['enemy_health']}/{combat['enemy_health_max']}｜"
            f"境界 {cls.enemy_realm_label(state)}\n"
            "指令：攻击／施法／防御／冷静观察／蓄势／绝技／遁走／用丹"
        )

    @classmethod
    def _player_strike(
        cls,
        state: GameState,
        power_multiplier: float,
        purpose: str,
        element_override: str = "",
    ) -> StrikeResult:
        player = state.player
        combat = state.combat
        observed = bool(combat.get("player_observed"))
        player_speed = ArtsEngine.effective_speed(player)
        hit_chance = 100 if observed else max(15, min(95, 75 + (player_speed - int(combat["enemy_speed"])) * 3))
        hit_roll = ProgressionEngine.deterministic_roll(state, f"combat-player-hit:{purpose}:{combat['round']}")
        if hit_roll > hit_chance:
            combat["player_observed"] = False
            return StrikeResult(False, hit_roll, hit_chance, False, 0, 1.0, 1.0)
        realm = cls.realm_multiplier(
            player.realm_index,
            player.stage_index,
            int(combat["enemy_realm_index"]),
            int(combat["enemy_stage_index"]),
        )
        attack_element = element_override or ArtsEngine.attack_element(player, cls.player_element(state))
        element = cls.element_multiplier(attack_element, str(combat["enemy_element"]))
        critical_roll = ProgressionEngine.deterministic_roll(state, f"combat-player-critical:{purpose}:{combat['round']}")
        critical = critical_roll <= max(5, min(35, 5 + player.fortune))
        critical_multiplier = 1.5 if critical else 1.0
        base = 14 + player.aptitude + player.realm_index * 14 + player.stage_index * 3
        arts_multiplier = ArtsEngine.attack_multiplier(player)
        damage = max(
            1,
            round(base * power_multiplier * arts_multiplier * realm * element * critical_multiplier - int(combat["enemy_defense"])),
        )
        combat["enemy_health"] = max(0, int(combat["enemy_health"]) - damage)
        combat["player_observed"] = False
        return StrikeResult(True, hit_roll, hit_chance, critical, damage, realm, element)

    @classmethod
    def _enemy_strike(cls, state: GameState, defending: bool) -> StrikeResult:
        player = state.player
        combat = state.combat
        player_speed = ArtsEngine.effective_speed(player)
        hit_chance = max(15, min(95, 75 + (int(combat["enemy_speed"]) - player_speed) * 3))
        hit_roll = ProgressionEngine.deterministic_roll(state, f"combat-enemy-hit:{combat['round']}")
        if hit_roll > hit_chance:
            return StrikeResult(False, hit_roll, hit_chance, False, 0, 1.0, 1.0)
        realm = cls.realm_multiplier(
            int(combat["enemy_realm_index"]),
            int(combat["enemy_stage_index"]),
            player.realm_index,
            player.stage_index,
        )
        element = cls.element_multiplier(str(combat["enemy_element"]), cls.player_element(state))
        critical_roll = ProgressionEngine.deterministic_roll(state, f"combat-enemy-critical:{combat['round']}")
        critical = critical_roll <= 10
        raw_damage = round(int(combat["enemy_power"]) * realm * element * (1.5 if critical else 1.0))
        damage = max(1, raw_damage - ArtsEngine.defense_bonus(player))
        if defending:
            damage = max(1, round(damage * 0.5))
        player.health = max(0, player.health - damage)
        return StrikeResult(True, hit_roll, hit_chance, critical, damage, realm, element)

    @staticmethod
    def _strike_text(actor: str, strike: StrikeResult) -> str:
        if not strike.hit:
            return f"{actor}攻击落空（命中 {strike.hit_roll}/{strike.hit_chance}）"
        critical = "，触发暴击" if strike.critical else ""
        return (
            f"{actor}造成 {strike.damage} 点伤害{critical}"
            f"（境界×{strike.realm_multiplier:g}，五行×{strike.element_multiplier:g}）"
        )

    @classmethod
    def act(cls, state: GameState, action: str) -> CombatRoundResult:
        if state.phase != "combat" or not state.combat:
            raise ValueError("当前不在战斗中。")
        combat = state.combat
        player = state.player
        action = action.strip()
        defending = False
        player_text = ""

        if action == "遁走":
            difference = int(combat["enemy_realm_index"]) - player.realm_index
            player_speed = ArtsEngine.effective_speed(player)
            chance = max(5, min(95, 55 + (player_speed - int(combat["enemy_speed"])) * 5 - max(0, difference) * 20))
            roll = ProgressionEngine.deterministic_roll(state, f"combat-escape:{combat['round']}")
            if roll <= chance:
                player_text = f"遁走成功（{roll}/{chance}）"
                return CombatRoundResult(action, player_text, "对手未能追上。", escaped=True)
            player_text = f"遁走失败（{roll}/{chance}），被对手截住"
        elif action == "攻击":
            player_text = cls._strike_text("你", cls._player_strike(state, 1.0, "attack"))
        elif action.startswith("施法"):
            requested = action.removeprefix("施法").strip()
            spell = ArtsEngine.spell(player, requested)
            if player.spirit < spell.spirit_cost:
                raise ValueError(f"灵力不足：{spell.name}需要 {spell.spirit_cost} 点灵力。")
            player.spirit -= spell.spirit_cost
            strike = cls._player_strike(state, spell.power_multiplier, f"spell:{spell.name}", spell.element)
            player_text = cls._strike_text(f"你施展{spell.name}", strike) + f"，灵力 -{spell.spirit_cost}"
        elif action == "防御":
            defending = True
            player_text = "你收束灵力护住周身，本轮所受伤害减半"
        elif action == "冷静观察":
            combat["player_observed"] = True
            player_text = "你看清对手灵力运转，下次攻击必定命中"
        elif action == "蓄势":
            combat["player_charge"] = min(2, int(combat["player_charge"]) + 1)
            player_text = f"你顶着攻势蓄力，绝技准备 {combat['player_charge']}/2"
        elif action == "绝技":
            if int(combat["player_charge"]) < 2:
                raise ValueError("绝技尚未完成两轮蓄势。")
            combat["player_charge"] = 0
            player_text = cls._strike_text("你施展绝技", cls._player_strike(state, 2.6, "ultimate"))
        elif action == "用丹":
            if player.resources.get("疗伤丹", 0) < 1:
                raise ValueError("乾坤袋中没有疗伤丹。")
            before = player.health
            player.resources["疗伤丹"] -= 1
            if player.resources["疗伤丹"] <= 0:
                player.resources.pop("疗伤丹", None)
            player.health = min(player.health_max, player.health + 40)
            player_text = f"你服下疗伤丹，气血 +{player.health - before}"
        else:
            raise ValueError("战斗中请选择：攻击、施法、防御、冷静观察、蓄势、绝技、遁走或用丹。")

        if int(combat["enemy_health"]) <= 0:
            return CombatRoundResult(action, player_text, f"{combat['enemy_name']}失去战力。", victory=True)

        enemy_strike = cls._enemy_strike(state, defending)
        enemy_text = cls._strike_text(str(combat["enemy_name"]), enemy_strike)
        if player.health <= 0:
            mode = str(combat["mode"])
            if mode == "切磋":
                player.health = 1
                player.condition = "切磋重伤"
                return CombatRoundResult(action, player_text, enemy_text, defeat=True, fatal=False)
            death_chance = max(35, min(95, 45 + (int(combat["enemy_realm_index"]) - player.realm_index) * 25))
            death_roll = ProgressionEngine.deterministic_roll(state, f"combat-defeat:{combat['round']}")
            fatal = death_roll <= death_chance
            if fatal:
                player.condition = f"陨落于{combat['enemy_name']}之手"
                state.phase = "ended"
            else:
                player.health = 1
                player.condition = "战败重伤"
                player.spirit_stones = max(0, player.spirit_stones - min(100, player.spirit_stones))
            return CombatRoundResult(action, player_text, enemy_text, defeat=True, fatal=fatal)

        combat["round"] = int(combat["round"]) + 1
        return CombatRoundResult(action, player_text, enemy_text)

    @classmethod
    def finish_victory(cls, state: GameState) -> None:
        combat = state.combat
        if combat.get("mode") == "切磋":
            state.player.reputation += 3
            state.phase = "playing"
            state.combat = {}
            return
        state.player.karma += 5
        state.pending_loot = dict(combat.get("loot", {}))
        stones = int(combat.get("loot_spirit_stones", 0))
        if stones:
            state.pending_loot["灵石"] = stones
        state.phase = "combat_loot"

    @staticmethod
    def collect_loot(state: GameState) -> dict[str, int]:
        loot = dict(state.pending_loot)
        stones = loot.pop("灵石", 0)
        state.player.spirit_stones += stones
        for name, count in loot.items():
            state.player.resources[name] = state.player.resources.get(name, 0) + count
        state.pending_loot = {}
        state.combat = {}
        state.phase = "playing"
        return {**loot, **({"灵石": stones} if stones else {})}

    @staticmethod
    def leave_loot(state: GameState) -> None:
        state.pending_loot = {}
        state.combat = {}
        state.phase = "playing"
