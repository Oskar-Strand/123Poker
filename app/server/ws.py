from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.game.table import Phase
from app.server.sessions import BUY_IN, Room, registry

router = APIRouter()


def view_for(room: Room, token: str) -> dict:
    """Build the table state as seen by one player.

    Hole cards are only included for the viewer's own seat (or for every
    live seat at showdown). Other seats get a hidden-card count only.
    """
    t = room.table
    showdown = t.phase == Phase.SHOWDOWN
    seats = []
    for i, s in enumerate(t.seats):
        if not s:
            seats.append(None)
            continue
        mine = s.player_id == token
        reveal = mine or (showdown and not s.folded)
        seats.append({
            "name": room.tickets.get(s.player_id, "?"),
            "stack": s.stack, "bet": s.bet, "folded": s.folded,
            "me": mine,
            "cards": [str(c) for c in s.hole_cards] if reveal else None,
            "card_count": len(s.hole_cards),
        })
    return {
        "type": "state", "name": room.name, "phase": t.phase.value,
        "button": t.button, "to_act": t.to_act, "pot": t.pot,
        "board": [str(c) for c in t.board],
        "seats": seats, "my_seat": room.seat_of(token),
    }


async def broadcast(room: Room):
    for token, ws in list(room.sockets.items()):
        try:
            await ws.send_json(view_for(room, token))
        except Exception:
            room.sockets.pop(token, None)


@router.websocket("/ws/{table_id}")
async def table_ws(ws: WebSocket, table_id: str, token: str = ""):
    room = registry.rooms.get(table_id)
    if not room or token not in room.tickets:
        await ws.close(code=4403)
        return
    await ws.accept()
    room.sockets[token] = ws
    await broadcast(room)
    try:
        while True:
            msg = await ws.receive_json()
            err = None
            try:
                handle(room, token, msg)
            except (ValueError, KeyError, TypeError) as e:
                err = str(e)
            if err:
                await ws.send_json({"type": "error", "message": err})
            await broadcast(room)
    except WebSocketDisconnect:
        pass
    finally:
        room.sockets.pop(token, None)
        # Leave the seat if we're between hands; otherwise keep it for reconnect.
        if room.seat_of(token) is not None and room.table.phase == Phase.WAITING:
            room.table.stand(token)
        if not room.sockets and room.seated == 0:
            registry.rooms.pop(room.id, None)
        else:
            await broadcast(room)


def handle(room: Room, token: str, msg: dict) -> None:
    kind = msg.get("type")
    t = room.table
    if kind == "sit":
        t.sit(token, BUY_IN, int(msg["seat"]))
    elif kind == "stand":
        t.stand(token)
    elif kind == "start":
        if room.seat_of(token) is None:
            raise ValueError("Take a seat first")
        t.start_hand()
    elif kind == "reset":
        if room.seat_of(token) is None:
            raise ValueError("Only seated players can reset the hand")
        t.abort_hand()
    else:
        raise ValueError("Unknown action")
