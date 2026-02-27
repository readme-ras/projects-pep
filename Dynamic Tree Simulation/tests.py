"""Tests for BST and game logic."""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from tree import BST
from game import GameState, Mode, Difficulty


# ── BST tests ──────────────────────────────────────────────────────────────────

def test_bst_insert_search():
    bst = BST()
    for v in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(v)
    assert bst.size == 7
    assert bst.search(4) is not None
    assert bst.search(99) is None
    assert bst.contains(1)
    print("✅ BST insert/search")


def test_bst_inorder():
    bst = BST()
    for v in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(v)
    assert bst.inorder() == [1, 3, 4, 5, 6, 7, 8]
    print("✅ BST inorder")


def test_bst_height():
    bst = BST()
    bst.insert(5)
    assert bst.height() == 1
    bst.insert(3); bst.insert(7)
    assert bst.height() == 2
    bst.insert(1)
    assert bst.height() == 3
    print("✅ BST height")


def test_bst_delete_leaf():
    bst = BST()
    for v in [5, 3, 7]:
        bst.insert(v)
    assert bst.delete(3)
    assert not bst.contains(3)
    assert bst.size == 2
    print("✅ BST delete leaf")


def test_bst_delete_one_child():
    bst = BST()
    for v in [5, 3, 7, 2]:
        bst.insert(v)
    bst.delete(3)
    assert not bst.contains(3)
    assert bst.contains(2)
    assert bst.inorder() == [2, 5, 7]
    print("✅ BST delete one-child node")


def test_bst_delete_two_children():
    bst = BST()
    for v in [5, 3, 7, 1, 4, 6, 8]:
        bst.insert(v)
    bst.delete(3)
    assert not bst.contains(3)
    assert bst.inorder() == [1, 4, 5, 6, 7, 8]
    print("✅ BST delete two-children node")


def test_bst_delete_root():
    bst = BST()
    for v in [5, 3, 7]:
        bst.insert(v)
    bst.delete(5)
    assert not bst.contains(5)
    assert sorted(bst.inorder()) == bst.inorder()  # still valid BST
    print("✅ BST delete root")


def test_bst_clear():
    bst = BST()
    for v in [5, 3, 7]:
        bst.insert(v)
    bst.clear()
    assert bst.size == 0
    assert bst.root is None
    print("✅ BST clear")


# ── Game logic tests ───────────────────────────────────────────────────────────

def test_game_find_correct():
    state = GameState()
    state.new_game(Mode.FIND, Difficulty.EASY)
    before_score = state.score
    result = state.guess_find(state.target)
    assert result is True
    assert state.score > before_score
    print("✅ Game FIND correct guess")


def test_game_find_wrong():
    state = GameState()
    state.new_game(Mode.FIND, Difficulty.EASY)
    before_lives = state.lives
    wrong_val = -999  # guaranteed wrong
    state.guess_find(wrong_val)
    assert state.lives == before_lives - 1
    print("✅ Game FIND wrong guess loses life")


def test_game_insert():
    state = GameState()
    state.new_game(Mode.INSERT, Difficulty.EASY)
    target = state.target
    before_score = state.score
    result = state.action_insert(target)
    assert result is True
    assert state.score > before_score
    print("✅ Game INSERT correct")


def test_game_delete():
    state = GameState()
    state.new_game(Mode.DELETE, Difficulty.EASY)
    target = state.target
    before_score = state.score
    result = state.action_delete(target)
    assert result is True
    assert state.score > before_score
    assert not state.bst.contains(target)
    print("✅ Game DELETE correct")


def test_game_sort():
    state = GameState()
    state.new_game(Mode.SORT, Difficulty.EASY)
    correct_seq = state.bst.inorder()
    # Click all values in order
    for val in correct_seq[:-1]:
        res = state.action_sort_click(val)
        assert res == "ok", f"Expected 'ok', got {res}"
    final = state.action_sort_click(correct_seq[-1])
    assert final == "complete"
    print("✅ Game SORT correct sequence")


def test_game_sort_wrong():
    state = GameState()
    state.new_game(Mode.SORT, Difficulty.EASY)
    correct_seq = state.bst.inorder()
    # click wrong value first
    wrong = -1
    res = state.action_sort_click(wrong)
    assert res == "wrong"
    assert state.lives == 2
    print("✅ Game SORT wrong click loses life and resets")


def test_game_hint_deducts():
    state = GameState()
    state.new_game(Mode.FIND, Difficulty.EASY)
    state.score = 20
    state.hint()
    assert state.score == 17
    print("✅ Hint deducts 3 points")


def test_game_double_hint():
    state = GameState()
    state.new_game(Mode.FIND, Difficulty.EASY)
    state.hint()
    msg = state.hint()
    assert "No more hints" in msg
    print("✅ Second hint blocked")


if __name__ == "__main__":
    test_bst_insert_search()
    test_bst_inorder()
    test_bst_height()
    test_bst_delete_leaf()
    test_bst_delete_one_child()
    test_bst_delete_two_children()
    test_bst_delete_root()
    test_bst_clear()
    test_game_find_correct()
    test_game_find_wrong()
    test_game_insert()
    test_game_delete()
    test_game_sort()
    test_game_sort_wrong()
    test_game_hint_deducts()
    test_game_double_hint()
    print("\n🎉 All tests passed!")
