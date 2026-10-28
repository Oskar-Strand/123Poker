from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Pot:
    amount: int
    eligible: set[str]

def build_pots(contributions: dict[str, int], folded: set[str]) -> list[Pot]:
    levels = sorted({c for p, c in contributions.items()
                     if p not in folded and c > 0})
    pots: list[Pot] = []
    prev = 0
    for level in levels:
        amount = sum(min(c, level) - min(c, prev) for c in contributions.values())
        eligible = {p for p, c in contributions.items()
                    if p not in folded and c >= level}
        pots.append(Pot(amount, eligible))
        prev = level
    return pots

def award(pots: list[Pot], hand_ranks: dict[str, tuple], seat_order: list[str]) -> dict[str, int]:
    winnings: dict[str, int] = defaultdict(int)
    for pot in pots:
        if len(pot.eligible) == 1:
            winners = list(pot.eligible)
        else:
            best = max((hand_ranks[p] for p in pot.eligible))
            winners = [p for p in seat_order if p in pot.eligible and hand_ranks[p] == best]
            share, remainder = divmod(pot.amount, len(winners))
            for w in winners:
                winnings[w] += share
            for w in winners[:remainder]:
                winnings[w] += 1
    return dict(winnings)