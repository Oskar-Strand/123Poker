from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.server import lobby, ws

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="123Poker")
app.include_router(lobby.router)
app.include_router(ws.router)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC / "lobby.html")


@app.get("/table")
def table_page():
    return FileResponse(STATIC / "table.html")
