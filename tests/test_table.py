import random
import pytest
from app.game.table import Table, Phase


def make_table(n_players, stack=1000):
    t = Table(rng=random.Random(1))
    for i in range(n_players):
        t.sit(f"p{i}", stack, i)
    return t


def test_three_players_blinds_and_first_to_act():
    t = make_table(3)
    t.start_hand()
    assert t.button == 0
    assert t.seats[1].bet == 5 and t.seats[2].bet == 10
    assert t.to_act == 0
    assert t.phase == Phase.PREFLOP


def test_heads_up_button_is_small_blind_and_acts_first():
    t = make_table(2)
    t.start_hand()
    assert t.seats[0].bet == 5 and t.seats[1].bet == 10
    assert t.to_act == 0


def test_everyone_gets_two_cards():
    t = make_table(6)
    t.start_hand()
    assert all(len(s.hole_cards) == 2 for s in t.seats if s)
    assert len(t.deck.cards) == 52 - 12


def test_cannot_take_occupied_seat():
    t = make_table(2)
    with pytest.raises(ValueError):
        t.sit("someone", 1000, 0)