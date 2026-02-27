"""
Game logic — Number Tree Challenge

Modes:
  FIND    — a target number is highlighted; player must find it via BST traversal guesses
  INSERT  — player picks where to insert a shown number
  DELETE  — player must delete a target node
  SORT    — player reads the inorder sequence from the tree
  RACE    — insert numbers as fast as possible before time runs out
"""

import random
import time
from enum import Enum, auto
from tree import BST


class Mode(Enum):
    FIND   = auto()
    INSERT = auto()
    DELETE = auto()
    SORT   = auto()
    RACE   = auto()


class Difficulty(Enum):
    EASY   = "Easy"
    MEDIUM = "Medium"
    HARD   = "Hard"


DIFF_SETTINGS = {
    Difficulty.EASY:   {"nodes": 7,  "range": (1, 30),  "time": 60, "race_count": 5},
    Difficulty.MEDIUM: {"nodes": 12, "range": (1, 60),  "time": 45, "race_count": 8},
    Difficulty.HARD:   {"nodes": 18, "range": (1, 99),  "time": 30, "race_count": 12},
}

# Points awarded per mode
POINTS = {
    Mode.FIND:   10,
    Mode.INSERT: 15,
    Mode.DELETE: 15,
    Mode.SORT:   20,
    Mode.RACE:   5,    # per node in race
}


class GameState:
    def __init__(self):
        self.bst        = BST()
        self.mode       = Mode.FIND
        self.difficulty = Difficulty.MEDIUM
        self.score      = 0
        self.lives      = 3
        self.round      = 0
        self.target     = None        # current target value
        self.hint_used  = False
        self.guesses    = 0
        self.start_time = None
        self.message    = ""
        self.message_ok = True        # True=green, False=red
        self.game_over  = False
        self.won        = False
        self.race_inserted = 0
        self.race_queue = []          # numbers left to insert in RACE mode
        self.sort_answer: list[int] = []  # player's sort answer so far
        self.history: list[str] = []  # log of events

    # ── Setup ──────────────────────────────────────────────────────────────────

    def new_game(self, mode: Mode, difficulty: Difficulty):
        self.bst        = BST()
        self.mode       = mode
        self.difficulty = difficulty
        self.score      = 0
        self.lives      = 3
        self.round      = 0
        self.game_over  = False
        self.won        = False
        self.history    = []
        self._setup_round()

    def _setup_round(self):
        cfg = DIFF_SETTINGS[self.difficulty]
        self.round     += 1
        self.hint_used  = False
        self.guesses    = 0
        self.start_time = time.time()
        self.sort_answer = []

        if self.mode == Mode.FIND:
            self._reset_tree()
            self.target = random.choice(self.bst.all_values())
            node = self.bst.search(self.target)
            if node:
                node.is_target = True
            self.message = f"🔍 Round {self.round}: Find the number  {self.target}  in the tree!"
            self.message_ok = True

        elif self.mode == Mode.INSERT:
            self._reset_tree()
            lo, hi = cfg["range"]
            # pick a number not already in the tree
            existing = set(self.bst.all_values())
            candidates = [v for v in range(lo, hi + 1) if v not in existing]
            self.target = random.choice(candidates)
            self.message = f"➕ Round {self.round}: Insert  {self.target}  into the tree!"
            self.message_ok = True

        elif self.mode == Mode.DELETE:
            self._reset_tree()
            self.target = random.choice(self.bst.all_values())
            node = self.bst.search(self.target)
            if node:
                node.is_target = True
            self.message = f"🗑️  Round {self.round}: Delete  {self.target}  from the tree!"
            self.message_ok = True

        elif self.mode == Mode.SORT:
            self._reset_tree()
            self.sort_answer = []
            self.message = (f"📋 Round {self.round}: Click nodes in ascending (inorder) order! "
                            f"({self.bst.size} numbers)")
            self.message_ok = True

        elif self.mode == Mode.RACE:
            lo, hi = cfg["range"]
            race_count = cfg["race_count"]
            self.race_queue = random.sample(range(lo, hi + 1), race_count)
            self.race_inserted = 0
            self.bst.clear()
            # Seed with a couple of nodes so there's a root
            seed_vals = random.sample(range(lo, hi + 1), 3)
            for v in seed_vals:
                if v not in self.race_queue:
                    self.bst.insert(v)
            self.target = self.race_queue[0] if self.race_queue else None
            self.message = (f"🏁 RACE! Insert as many numbers as you can in "
                            f"{cfg['time']}s! Next: {self.target}")
            self.message_ok = True

    def _reset_tree(self):
        cfg  = DIFF_SETTINGS[self.difficulty]
        lo, hi = cfg["range"]
        count   = cfg["nodes"]
        self.bst.clear()
        vals = random.sample(range(lo, hi + 1), count)
        for v in vals:
            self.bst.insert(v)
        # clear animation flags after initial build
        for node in self.bst._nodes:
            node.just_inserted = False

    # ── Player actions ─────────────────────────────────────────────────────────

    def guess_find(self, value: int) -> bool:
        """Player clicks a node claiming it is the target."""
        self.guesses += 1
        if value == self.target:
            pts = max(POINTS[Mode.FIND] - self.guesses + 1, 1)
            self.score += pts
            self._log(f"✅ Found {self.target} in {self.guesses} guess(es)! +{pts}pts")
            self.message = f"✅ Correct! +{pts} points"
            self.message_ok = True
            # Clear target highlight
            node = self.bst.search(self.target)
            if node:
                node.is_target = False
            self._next_or_end()
            return True
        else:
            self.lives -= 1
            hint = "Too low — go right!" if value < self.target else "Too high — go left!"
            self.message = f"❌ {value} is wrong. {hint}  (Lives: {self.lives})"
            self.message_ok = False
            self._log(f"❌ Guessed {value}, target={self.target}")
            if self.lives <= 0:
                self._end_game(won=False)
            return False

    def action_insert(self, value: int) -> bool:
        """Player types a value to insert."""
        if value != self.target:
            self.lives -= 1
            self.message = f"❌ Wrong! You need to insert {self.target}, not {value}. (Lives: {self.lives})"
            self.message_ok = False
            self._log(f"❌ Inserted {value}, expected {self.target}")
            if self.lives <= 0:
                self._end_game(won=False)
            return False
        node = self.bst.insert(value)
        node.just_inserted = True
        self.score += POINTS[Mode.INSERT]
        self.message = f"✅ Inserted {value}! +{POINTS[Mode.INSERT]} points"
        self.message_ok = True
        self._log(f"✅ Inserted {value} | Tree height: {self.bst.height()}")
        self._next_or_end()
        return True

    def action_delete(self, value: int) -> bool:
        """Player types a value to delete."""
        if value != self.target:
            self.lives -= 1
            self.message = f"❌ Wrong! Delete {self.target}, not {value}. (Lives: {self.lives})"
            self.message_ok = False
            self._log(f"❌ Tried to delete {value}, target={self.target}")
            if self.lives <= 0:
                self._end_game(won=False)
            return False
        # Clear highlight before delete
        node = self.bst.search(value)
        if node:
            node.is_target = False
        self.bst.delete(value)
        self.score += POINTS[Mode.DELETE]
        self.message = f"✅ Deleted {value}! +{POINTS[Mode.DELETE]} points"
        self.message_ok = True
        self._log(f"✅ Deleted {value} | Remaining: {self.bst.inorder()}")
        self._next_or_end()
        return True

    def action_sort_click(self, value: int) -> str:
        """Player clicks nodes for SORT mode. Returns status string."""
        correct_seq = self.bst.inorder()
        expected    = correct_seq[len(self.sort_answer)]
        if value == expected:
            self.sort_answer.append(value)
            if self.sort_answer == correct_seq:
                self.score += POINTS[Mode.SORT]
                self.message = f"✅ Perfect inorder traversal! +{POINTS[Mode.SORT]} points"
                self.message_ok = True
                self._log(f"✅ SORT correct: {correct_seq}")
                self._next_or_end()
                return "complete"
            return "ok"
        else:
            self.lives -= 1
            self.sort_answer = []
            self.message = (f"❌ Wrong! Expected {expected}, got {value}. "
                            f"Restarting sequence. (Lives: {self.lives})")
            self.message_ok = False
            self._log(f"❌ SORT wrong: expected {expected}, got {value}")
            if self.lives <= 0:
                self._end_game(won=False)
            return "wrong"

    def action_race_insert(self, value: int) -> bool:
        """Player inserts a value in RACE mode."""
        if not self.race_queue:
            return False
        expected = self.race_queue[0]
        if value != expected:
            self.message = f"❌ Next to insert is {expected}!"
            self.message_ok = False
            return False
        node = self.bst.insert(value)
        node.just_inserted = True
        self.race_queue.pop(0)
        self.race_inserted += 1
        self.score += POINTS[Mode.RACE]
        if self.race_queue:
            self.target = self.race_queue[0]
            self.message = f"✅ Inserted {value}! Next: {self.target}  (+{POINTS[Mode.RACE]}pts)"
        else:
            self.message = "🏆 All numbers inserted!"
            self.target = None
        self.message_ok = True
        self._log(f"✅ RACE inserted {value} ({self.race_inserted} total)")
        return True

    def race_tick(self) -> bool:
        """Call every second in RACE mode. Returns True if time is up."""
        cfg     = DIFF_SETTINGS[self.difficulty]
        elapsed = time.time() - self.start_time
        if elapsed >= cfg["time"]:
            self._end_game(won=self.race_inserted > 0)
            return True
        return False

    def time_remaining(self) -> int:
        if self.mode != Mode.RACE or self.start_time is None:
            return 0
        cfg = DIFF_SETTINGS[self.difficulty]
        return max(0, int(cfg["time"] - (time.time() - self.start_time)))

    def hint(self) -> str:
        """Return a hint for the current puzzle."""
        if self.hint_used:
            return "No more hints this round!"
        self.hint_used = True
        self.score     = max(0, self.score - 3)

        if self.mode in (Mode.FIND, Mode.DELETE):
            node   = self.bst.search(self.target)
            depth  = node.depth if node else "?"
            side   = "left subtree" if (node and node.parent and node.parent.right is not node) else "right subtree"
            return f"💡 Hint: {self.target} is at depth {depth}, in the {side}. (-3 pts)"
        if self.mode == Mode.INSERT:
            root_val = self.bst.root.value if self.bst.root else "?"
            direction = "left" if self.target < root_val else "right"
            return f"💡 Hint: {self.target} goes to the {direction} of root ({root_val}). (-3 pts)"
        if self.mode == Mode.SORT:
            seq = self.bst.inorder()
            return f"💡 Hint: The inorder sequence starts with {seq[:3]}... (-3 pts)"
        return "No hint available."

    # ── Internal ───────────────────────────────────────────────────────────────

    def _next_or_end(self):
        cfg      = DIFF_SETTINGS[self.difficulty]
        max_rounds = cfg["nodes"]    # one round per node roughly
        if self.round >= max_rounds or self.mode == Mode.RACE:
            self._end_game(won=True)
        else:
            self._setup_round()

    def _end_game(self, won: bool):
        self.game_over = True
        self.won       = won
        if won:
            self.message = f"🏆 Game Over! You win! Final score: {self.score}"
        else:
            self.message = f"💀 Game Over! Final score: {self.score}"
        self.message_ok = won
        self._log(f"=== GAME OVER | Score: {self.score} | Won: {won} ===")

    def _log(self, event: str):
        ts = time.strftime("%H:%M:%S")
        self.history.append(f"[{ts}] {event}")

    def stats(self) -> dict:
        return {
            "score":    self.score,
            "lives":    self.lives,
            "round":    self.round,
            "height":   self.bst.height(),
            "size":     self.bst.size,
            "inorder":  self.bst.inorder(),
        }
