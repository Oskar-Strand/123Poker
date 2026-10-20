from collections import Counter
from itertools import combinations

def rank_five(cards) -> tuple:
    # Scores exactly 5 cards. The result is a tuple like (category, tiebreaker1, tiebreaker2, ...).
    # Python compares tuples left to right, so a higher tuple always means a better hand.

    # The five ranks as numbers, highest first, e.g. [14, 10, 9, 5, 2]
    ranks = sorted((card.rank for card in cards), reverse=True)

    # How many times each rank appears, e.g. a pair of kings -> {13: 2, ...}
    counts = Counter(ranks)

    # (count, rank) pairs sorted high to low. Bigger groups come first, and ties in
    # group size are broken by rank. Pair of 9s + pair of 4s + a king -> [(2, 9), (2, 4), (1, 13)]
    # This ordering is exactly the order tiebreakers should be compared in.
    groups = sorted(((n, r ) for r, n in counts.items()), reverse=True)

    # A flush is when all five cards share one suit (the set of suits has size 1)
    is_flush = len({card.suit for card in cards}) == 1

    # TODO: detect a straight.
    #   - You need 5 DIFFERENT ranks (len(counts) == 5), otherwise it can't be a straight.
    #   - Then check that the highest rank minus the lowest rank == 4 (e.g. 9 - 5 == 4).
    #   - Special case, the "wheel" A-2-3-4-5: the ace counts as LOW here. The ranks look
    #     like [14, 5, 4, 3, 2]. Check for that exact list, and treat the straight as
    #     5-high (so the ace must NOT count as the top card for tiebreaking).
    #   - Tip: store the straight's high card in a variable (5 for the wheel, ranks[0]
    #     otherwise). You'll need it as the tiebreaker later.

    # TODO: return (category, tiebreakers...) based on groups, flush, straight.
    #   Pick a number for each hand category, higher = better. For example:
    #     8 straight flush, 7 four of a kind, 6 full house, 5 flush, 4 straight,
    #     3 three of a kind, 2 two pair, 1 one pair, 0 high card
    #   Check from the best category down and return on the first match:
    #     - straight AND flush       -> (8, straight_high)
    #     - groups[0][0] == 4        -> (7, quad_rank, kicker_rank)
    #     - groups == trips + pair   -> (6, trips_rank, pair_rank)
    #     - flush                    -> (5, *ranks)
    #     - straight                 -> (4, straight_high)
    #     - groups[0][0] == 3        -> (3, trips_rank, *kickers)
    #     - two groups with count 2  -> (2, high_pair, low_pair, kicker)
    #     - groups[0][0] == 2        -> (1, pair_rank, *kickers)
    #     - otherwise                -> (0, *ranks)
    #   Hint: because `groups` is already sorted, the tiebreaker ranks are just
    #   [r for n, r in groups], so you often don't need to pick them out by hand.
    #   For the pair/trips/quads categories this list already puts the grouped
    #   rank(s) first and the kickers after, in the right order.

def best_hand(seven_cards) -> tuple:
    # Finds the best 5-card hand out of 7 cards (2 hole cards + 5 board cards).
    # combinations(seven_cards, 5) produces all 21 possible 5-card subsets, each one
    # is scored with rank_five, and max() keeps the highest-scoring tuple.
    return max(rank_five(combo) for combo in combinations(seven_cards, 5))
