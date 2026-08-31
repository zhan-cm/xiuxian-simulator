from __future__ import annotations

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .choices import DecisionCatalog
from .engine import GameEngine
from .presentation import present_action, welcome_presentation
from .relationships import NPCS
from .npc_lifecycle import NpcLifecycleEngine
from .npc_network import NpcNetworkEngine
from .state import GameState
from .journey import JourneyEngine
from .commissions import CommissionEngine
from .story import StoryEngine
from .new_era import NewEraEngine
from .dao import DaoEngine
from .items import InventoryEngine
from .auctions import AuctionEngine
from .travel import TravelEngine
from .regional import RegionalEngine
from .cave import CaveEngine
from .beasts import SpiritBeastEngine
from .formations import FormationEngine
from .sect_library import SectLibraryEngine
from .artifact_growth import ArtifactGrowthEngine
from .art_mastery import ArtMasteryEngine
from .recovery import RecoveryEngine
from .legacy import LegacyEngine


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


class WebApplication:
    def __init__(self, engine: GameEngine, web_root: Path, decisions: DecisionCatalog | None = None) -> None:
        self.engine = engine
        self.web_root = web_root.resolve()
        self.decisions = decisions or DecisionCatalog.load(self.web_root.parent / "data" / "content" / "decision_choices.json")
        self._lock = threading.Lock()
        self._presentation = welcome_presentation()

    def snapshot(self) -> dict[str, Any]:
        life_state = GameState.from_dict(self.engine.state.to_dict())
        npc_lives = NpcLifecycleEngine.snapshot(life_state)
        npc_network = NpcNetworkEngine.snapshot(life_state)
        life_by_name = {item["name"]: item for item in npc_lives["profiles"]}
        npc_profiles = {
            name: {
                "name": npc.name,
                "gender": npc.gender,
                "identity": npc.identity,
                "age": life_by_name[name]["age"],
                "lifespan": life_by_name[name]["lifespan"],
                "realm": life_by_name[name]["realm"],
                "location": life_by_name[name]["location"],
                "likes": list(npc.likes),
                "dislikes": list(npc.dislikes),
                "greeting": npc.greeting,
                "affinity": int(self.engine.state.npc_relations.get(name, {}).get("affinity", 0)),
                "relation": life_by_name[name]["relation"],
                "alive": life_by_name[name]["alive"],
                "status": life_by_name[name]["status"],
            }
            for name, npc in NPCS.items()
        }
        return {
            "state": self.engine.state.to_dict(),
            "narrator": self.engine.narrator.name,
            "save_names": self.engine.saves.list_names(),
            "save_summaries": self.engine.saves.list_summaries(),
            "presentation": self._presentation,
            "decision": self.decisions.for_state(self.engine.state),
            "npc_profiles": npc_profiles,
            "journey": JourneyEngine.snapshot(self.engine.state),
            "commissions": CommissionEngine.snapshot(self.engine.state),
            "story": StoryEngine.snapshot(self.engine.state),
            "new_era": NewEraEngine.snapshot(self.engine.state),
            "dao": DaoEngine.snapshot(self.engine.state),
            "spirit_beasts": SpiritBeastEngine.snapshot(self.engine.state),
            "formations": FormationEngine.snapshot(self.engine.state),
            "sect_library": SectLibraryEngine.snapshot(self.engine.state),
            "artifacts": ArtifactGrowthEngine.snapshot(self.engine.state),
            "art_mastery": ArtMasteryEngine.snapshot(self.engine.state),
            "recovery": RecoveryEngine.snapshot(self.engine.state),
            "legacy": LegacyEngine.snapshot(self.engine.state),
            "inventory": InventoryEngine.snapshot(self.engine.state),
            "auction": AuctionEngine.snapshot(self.engine.state),
            "travel": TravelEngine.snapshot(self.engine.state),
            "regional": RegionalEngine.snapshot(self.engine.state),
            "cave": CaveEngine.snapshot(self.engine.state),
            "npc_lives": npc_lives,
            "npc_network": npc_network,
        }

    def perform_action(self, action: str) -> dict[str, Any]:
        """Run one validated action and return the shared UI snapshot.

        Both the stable HTML interface and the modern FastAPI interface use this
        method so they cannot drift into separate rule or presentation paths.
        """
        normalized = action.strip()
        with self._lock:
            before = self.engine.state.to_dict()
            output = self.engine.process(normalized)
            after = self.engine.state.to_dict()
            self._presentation = present_action(normalized, output, before, after)
            snapshot = self.snapshot()
        return {"output": output, **snapshot}

    @staticmethod
    def _json(payload: dict[str, Any], status: int = 200) -> tuple[int, str, bytes]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return status, "application/json; charset=utf-8", body

    def dispatch(self, method: str, raw_path: str, body: bytes = b"") -> tuple[int, str, bytes]:
        path = urlparse(raw_path).path
        if method == "GET" and path == "/api/state":
            return self._json(self.snapshot())
        if method == "POST" and path == "/api/action":
            if len(body) > 65536:
                return self._json({"error": "请求内容过长。"}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            try:
                payload = json.loads(body.decode("utf-8"))
                action = payload.get("action", "") if isinstance(payload, dict) else ""
            except (UnicodeDecodeError, json.JSONDecodeError):
                return self._json({"error": "请求不是有效 JSON。"}, HTTPStatus.BAD_REQUEST)
            if not isinstance(action, str) or not action.strip():
                return self._json({"error": "请输入行动。"}, HTTPStatus.BAD_REQUEST)
            if len(action) > 2000:
                return self._json({"error": "单次行动不能超过 2000 个字符。"}, HTTPStatus.BAD_REQUEST)
            return self._json(self.perform_action(action))
        if method != "GET":
            return self._json({"error": "不支持此请求。"}, HTTPStatus.METHOD_NOT_ALLOWED)

        asset = "index.html" if path == "/" else path.removeprefix("/")
        if asset not in {"index.html", "app.css", "app.js", "showcase.js"}:
            return self._json({"error": "页面不存在。"}, HTTPStatus.NOT_FOUND)
        destination = (self.web_root / asset).resolve()
        if destination.parent != self.web_root or not destination.is_file():
            return self._json({"error": "页面不存在。"}, HTTPStatus.NOT_FOUND)
        content_type = CONTENT_TYPES.get(destination.suffix, "application/octet-stream")
        return HTTPStatus.OK, content_type, destination.read_bytes()


def make_handler(app: WebApplication) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "XiuxianSimulator/0.52"

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            length = min(int(self.headers.get("Content-Length", "0") or 0), 65537)
            self._dispatch("POST", self.rfile.read(length))

        def _dispatch(self, method: str, body: bytes = b"") -> None:
            status, content_type, payload = app.dispatch(method, self.path, body)
            self.send_response(int(status))
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store" if self.path.startswith("/api/") else "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    return Handler


def run_web_server(
    engine: GameEngine,
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    app = WebApplication(engine, root / "web")
    server = ThreadingHTTPServer((host, port), make_handler(app))
    url = f"http://{host}:{port}/"
    print(f"问道长生网页版已启动：{url}")
    print("关闭此窗口即可停止游戏服务。")
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
