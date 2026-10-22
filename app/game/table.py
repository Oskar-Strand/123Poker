import random
from dataclasses import dataclass, field
from enum import Enum

from app.game.cards import Card, Deck

class Phase(str,Enum):
    WAITING ="waiting"
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER ="river"
    SHOWDOWN = "showdown"

@dataclass
class Seat:
    player_id: str
    stack: int
    hole_cards: list[Card] = field(default_factory=list)
    bet: int = 0
    folded: bool = False
    acted: bool = False

class Table:
    def __init__(self, max_seats=8, small_blind=5, big_blind=10, rng: random.Random | None = None):
        if not 2 <= max_seats <= 8:
            raise ValueError("A table must have 2-8 seats taken")
        self.seats: list[Seat | None] = [None] * max_seats
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.rng = rng
        self.phase = Phase.WAITING
        self.button = -1
        self.to_act: int | None = None
        self.pot = 0
        self.current_bet = 0
        self.board: list[Card] = []
        self.deck: Deck | None = None

    def sit(self, player_id:str, stack:int, seat_index:int) -> None:
        if not 0 <= seat_index < len(self.seats):
            raise ValueError("No such seat")
        if self.seats[seat_index] is not None:
            raise ValueError("Seat is taken")
        if any(s and s.player_id == player_id for s in self.seats):
            raise ValueError("Player is already seated")
        if stack<=0:
            raise ValueError("Stack must be positive")
        self.seats[seat_index] = Seat(player_id, stack)

    def stand(self, player_id:str) -> None:
        if self.phase != Phase.WAITING:
            raise ValueError("Cannot leave during a hand")
        i = self._index_of(player_id)
        self.seats[i] = None

    def start_hand(self) -> None:
        if self.phase != Phase.WAITING:
            raise ValueError("A hand is already running")
        players = [i for i, s in enumerate(self.seats) if s and s.stack > 0]
        if len(players) < 2:
            raise ValueError("Need at least 2 players with chips")

        for s in self.seats:
            if s:
                s.hole_cards, s.bet, s.acted = [], 0, False
                s.folded = s.stack == 0   # broke players sit this hand out

        self.board, self.pot = [], 0
        self.button = self._next_seat(self.button, self._in_hand)

        if len(players) == 2:   # heads-up: the button posts the small blind
            sb = self.button
        else:
            sb = self._next_seat(self.button, self._in_hand)
        bb = self._next_seat(sb, self._in_hand)

        self._post(sb, self.small_blind)
        self._post(bb, self.big_blind)
        self.current_bet = self.big_blind

        self.deck = Deck(self.rng)
        for i in players:
            self.seats[i].hole_cards = self.deck.deal(2)

        self.phase = Phase.PREFLOP
        self.to_act = self._next_seat(bb, self._can_act)

    def _post(self, i: int, amount: int) -> None:
        seat = self.seats[i]
        amount = min(amount, seat.stack)   # short stack posts what it has
        seat.stack -= amount
        seat.bet += amount

    def _in_hand(self, seat: Seat | None) -> bool:
       
        return seat is not None and not seat.folded
    def _can_act(self, seat: Seat | None) -> bool:
        return self._in_hand(seat) and seat.stack > 0

    def _next_seat(self, start: int, predicate) -> int:
        n = len(self.seats)
        for step in range(1, n + 1):
            i = (start + step) % n
            if predicate(self.seats[i]):
                return i
        raise RuntimeError("No seat matches")

    def _index_of(self, player_id: str) -> int:
        for i, s in enumerate(self.seats):
            if s and s.player_id == player_id:
                return i
        raise ValueError("Player not at table")