from app.game.cards import Card
from app.game.evaluator import (
    best_hand, HIGH_CARD, PAIR, TWO_PAIR, STRAIGHT, FLUSH,
    FULL_HOUSE, STRAIGHT_FLUSH,
)


def cards(s: str) -> list[Card]:
    return [Card.from_str(c) for c in s.split()]


def test_wheel_is_five_high_straight():
    assert best_hand(cards("Ah Kh 2c 3d 4s 5h 9c")) == (STRAIGHT, 5)


def test_six_high_straight_beats_wheel():
    wheel = best_hand(cards("Ah 2c 3d 4s 5h 9c Jd"))
    six_high = best_hand(cards("6h 2c 3d 4s 5h 9c Jd"))
    assert six_high > wheel


def test_straight_flush():
    assert best_hand(cards("9h Th Jh Qh Kh 2c 3d")) == (STRAIGHT_FLUSH, 13)


def test_flush_on_board_beats_pocket_pair():
    assert best_hand(cards("Ac Ad 2h 5h 8h Jh Kh")) == (FLUSH, 13, 11, 8, 5, 2)


def test_full_house_picks_best_pair():
    assert best_hand(cards("Kh Kd Ks 9h 9c 2h 2d")) == (FULL_HOUSE, 13, 9)


def test_two_pair_picks_top_two_and_best_kicker():
    assert best_hand(cards("Ah Ad Kh Kd 5c 5s 2h")) == (TWO_PAIR, 14, 13, 5)


def test_kicker_decides_same_pair():
    board = "As 7d 4c 9h 2s"
    king_kicker = best_hand(cards("Ah Kc " + board))
    queen_kicker = best_hand(cards("Ad Qc " + board))
    assert king_kicker[0] == queen_kicker[0] == PAIR
    assert king_kicker > queen_kicker


def test_board_plays_is_a_tie():
    board = "As Ks Qs Js Ts"
    assert best_hand(cards("2c 3d " + board)) == best_hand(cards("4h 7c " + board))


def test_high_card():
    assert best_hand(cards("Ah Jd 9c 7s 4h 3c 2d")) == (HIGH_CARD, 14, 11, 9, 7, 4)