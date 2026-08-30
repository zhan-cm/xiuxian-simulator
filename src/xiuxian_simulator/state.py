from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MONTH_NAMES = ("春一月", "春二月", "春三月", "夏四月", "夏五月", "夏六月", "秋七月", "秋八月", "秋九月", "冬十月", "冬十一月", "冬十二月")


@dataclass(slots=True)
class PlayerState:
    name: str = "沈砚"
    dao_name: str = "清微"
    gender: str = "自定义"
    age: int = 16
    lifespan: int = 100
    realm: str = "炼气·初期"
    realm_index: int = 0
    stage_index: int = 0
    sect: str = "散修"
    sect_rank: str = "无"
    sect_contribution: int = 0
    aptitude: int = 10
    comprehension: int = 10
    spirit_sense: int = 10
    speed: int = 10
    dao_heart: int = 10
    fortune: int = 10
    appearance: str = "清秀"
    appearance_description: str = "眉目清秀，神情沉静"
    background: str = "农家子"
    dao_path: str = "问道飞升"
    spiritual_root: str = "木火双灵根"
    constitution: str = "凡体"
    talents: list[str] = field(default_factory=list)
    health: int = 100
    health_max: int = 100
    spirit: int = 100
    spirit_max: int = 100
    cultivation: int = 0
    cultivation_required: int = 100
    primary_technique: str = "聚气诀"
    primary_technique_grade: str = "黄阶"
    known_techniques: list[str] = field(default_factory=lambda: ["聚气诀"])
    equipped_auxiliary_techniques: list[str] = field(default_factory=list)
    known_spells: list[str] = field(default_factory=lambda: ["流火术"])
    equipped_spell: str = "流火术"
    equipped_weapon: str = ""
    equipped_armor: str = ""
    breakthrough_cooldown_months: int = 0
    breakthrough_quality: dict[int, str] = field(default_factory=dict)
    destiny_traits: list[str] = field(default_factory=list)
    spirit_stones: int = 100
    merit: int = 0
    karma: int = 0
    reputation: int = 0
    alchemy_level: int = 0
    craft_skills: dict[str, int] = field(default_factory=dict)
    craft_successes: dict[str, int] = field(default_factory=dict)
    initial_affinity_bonus: int = 0
    condition: str = "无"
    location: str = "东洲·青岳"
    character_notes: str = "默认创角"
    inventory: list[str] = field(default_factory=list)
    resources: dict[str, int] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    modifiers: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class GameState:
    version: str = "0.38.0"
    phase: str = "new"
    turn: int = 0
    calendar_year: int = 387
    month: int = 1
    player: PlayerState = field(default_factory=PlayerState)
    main_quest: str = "灵气潮汐将至"
    history: list[str] = field(default_factory=list)
    rule_sha256: str = ""
    character_draft: dict[str, Any] = field(default_factory=dict)
    aura_level: str = "普通"
    rng_seed: int = 20260827
    rng_counter: int = 0
    pending_choices: list[str] = field(default_factory=list)
    combat: dict[str, Any] = field(default_factory=dict)
    pending_loot: dict[str, int] = field(default_factory=dict)
    cave_facilities: dict[str, int] = field(default_factory=dict)
    spirit_crops: dict[str, int] = field(default_factory=dict)
    npc_relations: dict[str, dict[str, Any]] = field(default_factory=dict)
    dao_partners: list[str] = field(default_factory=list)
    relationship_tension: int = 0
    relationship_events: list[str] = field(default_factory=list)
    pending_heart_trial: dict[str, Any] = field(default_factory=dict)
    adventure: dict[str, Any] = field(default_factory=dict)
    npc_world: dict[str, dict[str, Any]] = field(default_factory=dict)
    npc_invitations: dict[str, dict[str, Any]] = field(default_factory=dict)
    npc_event_log: list[str] = field(default_factory=list)
    last_npc_event: str = ""
    sect_privileges: list[str] = field(default_factory=list)
    sect_tournament_results: dict[str, str] = field(default_factory=dict)
    world_events: list[str] = field(default_factory=list)
    world_event_keys: list[str] = field(default_factory=list)
    last_world_event: str = ""
    world_tension: int = 0
    faction_strengths: dict[str, int] = field(
        default_factory=lambda: {"青云宗": 70, "丹霞谷": 64, "玄剑门": 68, "血煞盟": 66}
    )
    active_sect_war: dict[str, Any] = field(default_factory=dict)
    sect_war_history: list[str] = field(default_factory=list)
    fallen_factions: list[str] = field(default_factory=list)
    regional_prosperity: dict[str, int] = field(
        default_factory=lambda: {"东洲": 65, "南疆": 52, "西漠": 46, "北原": 48, "中州": 72}
    )
    world_era: str = "灵潮前夜"
    world_milestones: list[str] = field(default_factory=list)
    last_world_evolution_year: int = 0
    world_interventions: dict[str, str] = field(default_factory=dict)
    journey_points: int = 0
    journey_claims: list[str] = field(default_factory=list)
    journey_counters: dict[str, int] = field(default_factory=dict)
    active_commissions: dict[str, dict[str, Any]] = field(default_factory=dict)
    completed_commissions: list[str] = field(default_factory=list)
    commission_history: list[str] = field(default_factory=list)
    commission_renown: int = 0
    story_completed: list[str] = field(default_factory=list)
    story_choices: dict[str, str] = field(default_factory=dict)
    story_history: list[str] = field(default_factory=list)
    pending_story_node: str = ""
    auction: dict[str, Any] = field(default_factory=dict)
    auction_history: list[str] = field(default_factory=list)
    pending_travel: dict[str, Any] = field(default_factory=dict)
    visited_regions: list[str] = field(default_factory=lambda: ["东洲"])
    travel_history: list[str] = field(default_factory=list)
    trade_cargo: dict[str, dict[str, int]] = field(default_factory=dict)
    trade_profit: int = 0

    @property
    def time_label(self) -> str:
        return f"天玄历 {self.calendar_year} 年 · {MONTH_NAMES[self.month - 1]}"

    def advance_month(self, months: int = 1) -> bool:
        died_of_age = False
        for _ in range(months):
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.calendar_year += 1
                self.player.age += 1
                if self.player.age >= self.player.lifespan:
                    died_of_age = True
            self.turn += 1
            if self.player.breakthrough_cooldown_months > 0:
                self.player.breakthrough_cooldown_months -= 1
        return died_of_age

    def remember(self, event: str) -> None:
        self.history.append(f"第 {self.turn} 回合｜{self.time_label}｜{event}")
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameState":
        data = dict(payload)
        data["player"] = PlayerState(**data.get("player", {}))
        return cls(**data)
