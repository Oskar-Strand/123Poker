import random
from dataclasses import dataclass

RANKS = "23456789TJQKA"
SUITS = "cdhs"

@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    @classmethod
    def from_str(cls, s:str) -> "Card":
        return cls(RANKS.index(s[0])+ 2, s[1])

    def __str__(self) -> str:
        return RANKS[self.rank - 2] + self.suit

class Deck:
    def __init__(self, rng: random.Random | None = None):
        self.cards = [Card(rank, suit) for rank in range(2, 15) for suit in SUITS]
        (rng or random.SystemRandom()).shuffle(self.cards)

    def deal(self,n: int = 1) -> list[Card]:
        dealt, self.cards = self.cards[:n], self.cards[n:]
        return dealt