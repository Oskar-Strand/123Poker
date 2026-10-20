from collections import Counter
from itertools import combinations

def rank_five(cards) -> tuple:
    ranks = sorted((card.rank for card in cards), reverse=True)
    counts = Counter(ranks)
    groups = sorted(((n, r ) for r, n in counts.items()), reverse=True)
    is_flush = len({card.suit for card in cards}) == 1
     # TODO: detect straight, including the wheel A-2-3-4-5
    # TODO: return (category, tiebreakers...) based on groups, flush, straight
    
def best_hand(seven_cards) -> tuple:
    return max(rank_five(combo) for combo in combinations(seven_cards, 5))