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
    sect: str = "散修"
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
    spirit_stones: int = 100
    merit: int = 0
    karma: int = 0
    reputation: int = 0
    alchemy_level: int = 0
    initial_affinity_bonus: int = 0
    condition: str = "无"
    location: str = "东洲·青岳"
    character_notes: str = "默认创角"
    inventory: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    modifiers: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class GameState:
    version: str = "0.2.0"
    phase: str = "new"
    turn: int = 0
    calendar_year: int = 387
    month: int = 1
    player: PlayerState = field(default_factory=PlayerState)
    main_quest: str = "灵气潮汐将至"
    history: list[str] = field(default_factory=list)
    rule_sha256: str = ""
    character_draft: dict[str, Any] = field(default_factory=dict)

    @property
    def time_label(self) -> str:
        return f"天玄历 {self.calendar_year} 年 · {MONTH_NAMES[self.month - 1]}"

    def advance_month(self, months: int = 1) -> None:
        for _ in range(months):
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.calendar_year += 1
                self.player.age += 1
            self.turn += 1

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
