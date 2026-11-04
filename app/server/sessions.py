import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field

from app.game.table import Table

BUY_IN = 1000


def _hash(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)


@dataclass
class Room:
    id: str
    name: str
    private: bool
    table: Table
    salt: bytes = b""
    pw_hash: bytes = b""
    tickets: dict[str, str] = field(default_factory=dict)   # token -> player name
    sockets: dict[str, object] = field(default_factory=dict)  # token -> websocket

    def check_password(self, password: str | None) -> bool:
        if not self.private:
            return True
        return hmac.compare_digest(_hash(password or "", self.salt), self.pw_hash)

    @property
    def seated(self) -> int:
        return sum(1 for s in self.table.seats if s)

    def seat_of(self, token: str) -> int | None:
        for i, s in enumerate(self.table.seats):
            if s and s.player_id == token:
                return i
        return None


class Registry:
    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def create(self, name, max_seats, private, password) -> Room:
        if private and not password:
            raise ValueError("A private table needs a password")
        room = Room(secrets.token_urlsafe(6), name, private, Table(max_seats=max_seats))
        if private:
            room.salt = os.urandom(16)
            room.pw_hash = _hash(password, room.salt)
        self.rooms[room.id] = room
        return room

    def summaries(self) -> list[dict]:
        return [
            {"id": r.id, "name": r.name, "private": r.private,
             "seated": r.seated, "max_seats": len(r.table.seats),
             "in_hand": r.table.phase.value != "waiting"}
            for r in self.rooms.values()
        ]


registry = Registry()
