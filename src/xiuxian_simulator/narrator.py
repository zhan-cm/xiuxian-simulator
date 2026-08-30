from __future__ import annotations

from abc import ABC, abstractmethod
import json
from collections.abc import Callable
from urllib import error, request

from .state import GameState


class Narrator(ABC):
    """叙事扩展点：未来的大模型适配器只需实现 narrate。"""

    @abstractmethod
    def narrate(self, action: str, state: GameState) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class LocalNarrator(Narrator):
    def narrate(self, action: str, state: GameState) -> str:
        return (
            f"你在{state.player.location}尝试“{action}”。天地依其逻辑回应，"
            "此事已记入经历；本地叙事器不会擅自生成额外数值奖励或惩罚。"
        )


class NarrationError(RuntimeError):
    pass


Transport = Callable[[str, dict[str, str], dict[str, object], float], dict[str, object]]


class OpenAINarrator(Narrator):
    """Responses API 叙事适配器；只生成文字，不接管数值结算。"""

    def __init__(
        self,
        api_key: str,
        model: str,
        instructions: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 45.0,
        transport: Transport | None = None,
    ) -> None:
        if not api_key.strip():
            raise ValueError("使用 OpenAI 叙事器必须设置 OPENAI_API_KEY。")
        self._api_key = api_key.strip()
        self.model = model.strip() or "gpt-5.4"
        self.instructions = instructions.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._transport = transport or self._post_json

    @property
    def name(self) -> str:
        return f"OpenAI Responses API · {self.model}"

    def narrate(self, action: str, state: GameState) -> str:
        player = state.player
        compact_state = {
            "time": state.time_label,
            "turn": state.turn,
            "player": {
                "name": player.name,
                "dao_name": player.dao_name,
                "realm": player.realm,
                "sect": player.sect,
                "sect_rank": player.sect_rank,
                "location": player.location,
                "health": f"{player.health}/{player.health_max}",
                "spirit": f"{player.spirit}/{player.spirit_max}",
                "condition": player.condition,
                "dao": player.dao_levels,
            },
            "main_quest": state.main_quest,
            "last_npc_event": state.last_npc_event,
            "last_world_event": state.last_world_event,
            "recent_history": state.history[-8:],
        }
        payload: dict[str, object] = {
            "model": self.model,
            "instructions": self.instructions,
            "input": (
                "请根据以下已结算状态，仅为玩家的自由行动生成 1～3 句修仙叙事。"
                "不得宣布新的数值变化、掉落、死亡、突破、结道侣或替玩家作决定。\n"
                f"玩家行动：{action}\n"
                f"当前状态：{json.dumps(compact_state, ensure_ascii=False, separators=(',', ':'))}"
            ),
            "max_output_tokens": 320,
            "store": False,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = self._transport(f"{self.base_url}/responses", headers, payload, self.timeout)
        except Exception as exc:
            raise NarrationError(f"OpenAI 叙事请求失败：{exc}") from exc
        text = self._output_text(response)
        if not text:
            raise NarrationError("OpenAI 响应中没有可用的 output_text。")
        return text.strip()

    @staticmethod
    def _output_text(response: dict[str, object]) -> str:
        direct = response.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct
        pieces: list[str] = []
        output = response.get("output", [])
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content", [])
                if not isinstance(content, list):
                    continue
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "output_text" and isinstance(part.get("text"), str):
                        pieces.append(str(part["text"]))
        return "\n".join(pieces)

    @staticmethod
    def _post_json(
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout: float,
    ) -> dict[str, object]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        api_request = request.Request(url, data=body, headers=headers, method="POST")
        try:
            with request.urlopen(api_request, timeout=timeout) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise NarrationError(f"HTTP {exc.code}：{detail}") from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise NarrationError(str(exc)) from exc
        if not isinstance(decoded, dict):
            raise NarrationError("API 返回格式不是 JSON 对象。")
        return decoded


class FallbackNarrator(Narrator):
    def __init__(self, primary: Narrator, fallback: Narrator) -> None:
        self.primary = primary
        self.fallback = fallback
        self.last_error = ""

    @property
    def name(self) -> str:
        return f"{self.primary.name}（失败时自动本地回退）"

    def narrate(self, action: str, state: GameState) -> str:
        try:
            self.last_error = ""
            return self.primary.narrate(action, state)
        except Exception as exc:
            self.last_error = str(exc)
            return "【云端叙事暂不可用，已自动切换本地叙事】\n" + self.fallback.narrate(action, state)
