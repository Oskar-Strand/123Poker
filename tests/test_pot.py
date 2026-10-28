from app.game.pot import build_pots, award, Pot

def test_no_all_in_single_pot():
    pots = build_pots({"A": 100, "B": 100, "C": 100}, folded=set())
    assert pots == [Pot(amount=300, eligible={"A", "B", "C"})]

def test_short_all_in_creates_side_pot():
    pots = build_pots({"A": 50, "B": 200, "C": 200}, folded=set())
    assert pots == [
        Pot(amount=150, eligible={"A", "B", "C"}),
        Pot(amount=300, eligible={"A", "C"})
    ]

def test_folded_chips_count_but_not_eligible():
    pots = build_pots({"A": 50, "B": 200, "C": 100}, folded={"C"})
    assert pots == [Pot(150, {"A", "B"}), Pot(200, {"B"})]


def test_short_stack_wins_only_main_pot():
    pots = build_pots({"A": 50, "B": 200, "C": 200}, folded=set())
    ranks = {"A": (8, 13), "B": (1, 10), "C": (0, 14)}
    assert award(pots, ranks, ["A", "B", "C"]) == {"A": 150, "B": 300}

def test_split_pot_odd_chip_goes_left_of_button():
    pots = [Pot(101, {"A", "B"})]
    ranks = {"A": (4, 10), "B": (4, 10)}
    assert award(pots, ranks, ["B", "A"]) == {"B": 51, "A": 50}


def test_everyone_folds_no_ranks_needed():
    pots = build_pots({"A": 10, "B": 5}, folded={"B"})
    assert award(pots, {}, ["A", "B"]) == {"A": 15}