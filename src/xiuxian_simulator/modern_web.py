from __future__ import annotations

import json
import threading
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
import uvicorn

from . import __version__
from .engine import GameEngine
from .save_manager import MAX_PORTABLE_SAVE_BYTES, SaveImportError
from .showcase import build_showcase
from .webapp import WebApplication


class ActionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action: str = Field(min_length=1, max_length=2000)


class HealthResponse(BaseModel):
    status: str
    version: str
    interface: str


class SaveImportRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    data: dict[str, Any]
    preferred_name: str = Field(default="", max_length=48)
    overwrite: bool = False


def create_modern_app(engine: GameEngine, root: Path) -> FastAPI:
    """Create the versioned API and serve the compiled React application."""
    root = root.resolve()
    dist_root = root / "frontend" / "dist"
    index_file = dist_root / "index.html"
    if not index_file.is_file():
        raise FileNotFoundError(
            "新版界面尚未构建。请先在 frontend 目录运行 npm install 和 npm run build。"
        )

    game = WebApplication(engine, root / "web")
    app = FastAPI(
        title="问道长生本地接口",
        version=__version__,
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
    )

    @app.middleware("http")
    async def local_security_headers(request: Request, call_next: Any) -> Any:
        raw_length = request.headers.get("content-length", "0")
        try:
            content_length = int(raw_length)
        except ValueError:
            response = JSONResponse({"detail": "请求长度无效。"}, status_code=400)
        else:
            if content_length < 0:
                response = JSONResponse({"detail": "请求长度无效。"}, status_code=400)
            elif content_length > MAX_PORTABLE_SAVE_BYTES + 65_536:
                response = JSONResponse({"detail": "请求内容超过 2 MB 安全上限。"}, status_code=413)
            else:
                response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; script-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; font-src 'self'"
        )
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
        return response

    @app.get("/api/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__, interface="react")

    @app.get("/api/v1/state")
    def state() -> dict[str, Any]:
        return game.snapshot()

    @app.post("/api/v1/actions")
    def action(request: ActionRequest) -> dict[str, Any]:
        try:
            return game.perform_action(request.action)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/v1/saves/export")
    def export_save(name: str) -> Response:
        try:
            payload = game.export_save(name)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        safe_name = str(payload["name"])
        filename = f"{safe_name}-问道长生存档.json"
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
        return Response(
            content=body,
            media_type="application/json",
            headers={
                "Content-Disposition": (
                    "attachment; filename=\"Wendao-Changsheng-save.json\"; "
                    f"filename*=UTF-8''{quote(filename)}"
                ),
            },
        )

    @app.post("/api/v1/saves/import")
    def import_save(request: SaveImportRequest) -> dict[str, Any]:
        try:
            return game.import_save(
                request.data,
                preferred_name=request.preferred_name,
                overwrite=request.overwrite,
            )
        except SaveImportError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/v1/showcase")
    def showcase() -> dict[str, Any]:
        return {"pages": build_showcase(engine, root)}

    assets = dist_root / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str = "") -> FileResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="接口不存在")
        return FileResponse(index_file)

    return app


def run_modern_server(
    engine: GameEngine,
    root: Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    app = create_modern_app(engine, root)
    url = f"http://{host}:{port}/"
    print(f"问道长生 V{__version__} 新版界面已启动：{url}")
    print("关闭此窗口即可停止游戏服务。")
    if open_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")
