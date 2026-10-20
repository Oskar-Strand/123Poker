from collections import Counter
from itertools import combinations

HIGH_CARD, ONE_PAIR, TWO_PAIR, THREE_OF_A_KIND, STRAIGHT, FLUSH, FULL_HOUSE, FOUR_OF_A_KIND, STRAIGHT_FLUSH = range(9)

# Hand categories are ordered so rank tuples compare by category before tie-breakers.
def rank_five(cards) -> tuple:
    ranks = sorted((card.rank for card in cards), reverse=True)
    counts = Counter(ranks)
    # Sort by multiplicity, then rank, to order both the hand pattern and its tie-breakers.
    groups = sorted(((n, r ) for r, n in counts.items()), reverse=True)
    group_ranks = [r for n, r in groups]
    shape = [n for n, r in groups]


    is_flush = len({card.suit for card in cards}) == 1
    straight_high = is_straight(ranks)

    if is_flush and straight_high is not None:
        return (STRAIGHT_FLUSH, straight_high)
    if shape == [4, 1]:
        return (FOUR_OF_A_KIND, *group_ranks)
    if shape == [3, 2]:
        return (FULL_HOUSE, *group_ranks)
    if is_flush:
        return (FLUSH, *ranks)
    if straight_high is not None:
        return (STRAIGHT, straight_high)
    if shape == [3, 1, 1]:
        return (THREE_OF_A_KIND, *group_ranks)
    if shape == [2, 2, 1]:
        return (TWO_PAIR, *group_ranks)
    if shape == [2, 1, 1, 1]:
        return (PAIR, *group_ranks)
    return (HIGH_CARD, *ranks)


def best_hand(seven_cards) -> tuple:
    # Evaluate every five-card combination and keep the strongest comparable rank tuple.
    return max(rank_five(combo) for combo in combinations(seven_cards, 5))

def is_straight(ranks) -> int | None:
    unique_ranks = set(ranks)
    # A repeated rank prevents a five-card straight.
    if len(unique_ranks) != 5:
        return None

    # In the wheel (A-2-3-4-5), ace is low and five is the high card.
    if unique_ranks == {14, 5, 4, 3, 2}:
        return 5

    # Return the high card for ordinary straights so they can break ties.
    if max(unique_ranks) - min(unique_ranks) == 4:
        return max(unique_ranks)

    return None