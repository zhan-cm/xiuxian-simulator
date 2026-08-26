from __future__ import annotations

from abc import ABC, abstractmethod

from .state import GameState


class Narrator(ABC):
    """叙事扩展点：未来的大模型适配器只需实现 narrate。"""

    @abstractmethod
    def narrate(self, action: str, state: GameState) -> str:
        raise NotImplementedError


class LocalNarrator(Narrator):
    def narrate(self, action: str, state: GameState) -> str:
        return (
            f"你在{state.player.location}尝试“{action}”。天地依其逻辑回应，"
            "此事已记入经历；V0.1 本地叙事器暂不擅自生成额外数值奖励或惩罚。"
        )

