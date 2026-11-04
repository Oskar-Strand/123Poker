import secrets

from fastapi import APIRouter, HTTPException

from app.schemas import CreateTable, JoinTable
from app.server.sessions import registry

router = APIRouter(prefix="/api")


@router.get("/tables")
def list_tables():
    return registry.summaries()


@router.post("/tables", status_code=201)
def create_table(body: CreateTable):
    try:
        room = registry.create(body.name.strip(), body.max_seats, body.private, body.password)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"id": room.id}


@router.post("/tables/{table_id}/join")
def join_table(table_id: str, body: JoinTable):
    room = registry.rooms.get(table_id)
    if not room:
        raise HTTPException(404, "No such table")
    if not room.check_password(body.password):
        raise HTTPException(403, "Wrong password")
    token = secrets.token_urlsafe(16)
    room.tickets[token] = body.name.strip()
    return {"token": token}
