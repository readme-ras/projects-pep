"""
Number Tree — CLI Game
──────────────────────
A number game built on a live Binary Search Tree.

Modes:
  1. FIND   — Spot the highlighted target node
  2. INSERT — Type the right number to insert
  3. DELETE — Remove the target node
  4. SORT   — Click nodes in inorder sequence
  5. RACE   — Insert as many numbers as possible before time runs out
"""

import os
import sys
import time
import threading

from game import GameState, Mode, Difficulty
from renderer import LevelRenderer, ASCIIRenderer


# ── Colour helpers ─────────────────────────────────────────────────────────────

R      = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
MAG    = "\033[95m"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def c(text, *codes):
    return "".join(codes) + str(text) + R

def hr(char="─", n=62, color=CYAN):
    return c(char * n, color)

def prompt(text=""):
    return input(c(f"  ❯ {text}", BOLD, CYAN)).strip()

def info(text):
    print(c(f"  {text}", DIM))


# ── Renderer ───────────────────────────────────────────────────────────────────

renderer = LevelRenderer()

def draw(state: GameState, extra: str = ""):
    clear()

    # Header
    print()
    print(c("  🌳  NUMBER TREE CHALLENGE", BOLD, YELLOW))
    print(f"  {c('Mode:', BOLD)} {c(state.mode.name, MAG)}  "
          f"{c('Diff:', BOLD)} {c(state.difficulty.value, BLUE)}  "
          f"{c('Score:', BOLD)} {c(state.score, GREEN)}  "
          f"{c('Lives:', BOLD)} {c('❤️ ' * state.lives, RED)}  "
          f"{c('Round:', BOLD)} {c(state.round, CYAN)}")

    if state.mode == Mode.RACE:
        remaining = state.time_remaining()
        bar_len = 30
        filled  = int(bar_len * remaining / 30)
        bar     = c("█" * filled, GREEN if remaining > 10 else RED) + c("░" * (bar_len - filled), DIM)
        print(f"  ⏱  {bar}  {c(remaining, BOLD)}s  "
              f"Inserted: {c(state.race_inserted, YELLOW)}")

    print(hr())

    # Tree
    print(renderer.render(state.bst))
    print(hr())

    # Message
    msg_color = GREEN if state.message_ok else RED
    print(f"\n  {c(state.message, BOLD, msg_color)}\n")

    if extra:
        print(f"  {c(extra, YELLOW)}")

    # Controls hint
    print(hr("─", 62, DIM))
    print(c("  [h]int  [s]tats  [log]  [q]uit", DIM))


def draw_stats(state: GameState):
    s = state.stats()
    print(f"\n{hr()}")
    print(c("  📊 STATS", BOLD))
    for k, v in s.items():
        print(f"  {c(k + ':', BOLD, DIM)} {v}")
    print(hr())


# ── Menu ───────────────────────────────────────────────────────────────────────

BANNER = f"""
{c('╔══════════════════════════════════════════════╗', CYAN, BOLD)}
{c('║', CYAN, BOLD)}   {c('🌳  NUMBER TREE CHALLENGE  🌳', YELLOW, BOLD)}          {c('║', CYAN, BOLD)}
{c('║', CYAN, BOLD)}   {c('A dynamic BST number game', DIM)}                {c('║', CYAN, BOLD)}
{c('╚══════════════════════════════════════════════╝', CYAN, BOLD)}
"""

def pick_mode() -> Mode:
    modes = list(Mode)
    descs = {
        Mode.FIND:   "🔍 FIND   — spot the highlighted target in the tree",
        Mode.INSERT: "➕ INSERT — type the correct number to insert",
        Mode.DELETE: "🗑️  DELETE — remove the marked node",
        Mode.SORT:   "📋 SORT   — click nodes in ascending (inorder) order",
        Mode.RACE:   "🏁 RACE   — insert numbers before the timer runs out",
    }
    print(c("\n  Choose a game mode:", BOLD))
    for i, m in enumerate(modes, 1):
        print(f"  {c(i, YELLOW)}. {descs[m]}")
    while True:
        try:
            choice = int(prompt("Mode number: "))
            if 1 <= choice <= len(modes):
                return modes[choice - 1]
        except ValueError:
            pass
        print(c("  Invalid choice.", RED))


def pick_difficulty() -> Difficulty:
    diffs = list(Difficulty)
    print(c("\n  Choose difficulty:", BOLD))
    for i, d in enumerate(diffs, 1):
        print(f"  {c(i, YELLOW)}. {d.value}")
    while True:
        try:
            choice = int(prompt("Difficulty: "))
            if 1 <= choice <= len(diffs):
                return diffs[choice - 1]
        except ValueError:
            pass
        print(c("  Invalid choice.", RED))


# ── Mode loops ─────────────────────────────────────────────────────────────────

def _handle_common(inp: str, state: GameState) -> bool:
    """Handle universal commands. Returns True if consumed."""
    if inp in ("q", "quit", "exit"):
        state.game_over = True
        state.message   = "Quit."
        return True
    if inp == "h":
        hint = state.hint()
        state.message    = hint
        state.message_ok = True
        draw(state)
        input(c("  (press Enter to continue)", DIM))
        return True
    if inp == "s":
        draw(state)
        draw_stats(state)
        input(c("  (press Enter to continue)", DIM))
        return True
    if inp == "log":
        draw(state)
        print(c("\n  📜 Event Log", BOLD))
        for line in state.history[-15:]:
            print(f"  {c(line, DIM)}")
        input(c("  (press Enter to continue)", DIM))
        return True
    return False


def run_find(state: GameState):
    while not state.game_over:
        draw(state, f"Click (type) a node value to guess where {c(state.target, RED, BOLD)} is:")
        inp = prompt()
        if _handle_common(inp, state):
            continue
        try:
            val = int(inp)
            state.guess_find(val)
        except ValueError:
            state.message    = "Please enter a number."
            state.message_ok = False


def run_insert(state: GameState):
    while not state.game_over:
        draw(state, f"Type the number to insert: {c(state.target, GREEN, BOLD)}")
        inp = prompt()
        if _handle_common(inp, state):
            continue
        try:
            val = int(inp)
            state.action_insert(val)
        except ValueError:
            state.message    = "Please enter a number."
            state.message_ok = False


def run_delete(state: GameState):
    while not state.game_over:
        draw(state, f"Type the number to delete: {c(state.target, RED, BOLD)}")
        inp = prompt()
        if _handle_common(inp, state):
            continue
        try:
            val = int(inp)
            state.action_delete(val)
        except ValueError:
            state.message    = "Please enter a number."
            state.message_ok = False


def run_sort(state: GameState):
    while not state.game_over:
        so_far = state.sort_answer
        draw(state, f"Selected so far: {c(so_far, BLUE)}  — type next node value:")
        inp = prompt()
        if _handle_common(inp, state):
            continue
        try:
            val = int(inp)
            result = state.action_sort_click(val)
            if result == "complete":
                draw(state)
                time.sleep(1.2)
        except ValueError:
            state.message    = "Please enter a number."
            state.message_ok = False


def run_race(state: GameState):
    """Race mode — player inserts numbers as fast as possible, timer ticks in background."""
    _stop = threading.Event()

    def timer_thread():
        while not _stop.is_set():
            time.sleep(1)
            if state.race_tick():
                _stop.set()

    t = threading.Thread(target=timer_thread, daemon=True)
    t.start()

    while not state.game_over and not _stop.is_set():
        queue_preview = state.race_queue[:4]
        extra = f"Queue: {c(queue_preview, YELLOW)} ...  Next: {c(state.target, GREEN, BOLD)}"
        draw(state, extra)
        inp = prompt()
        if _handle_common(inp, state):
            break
        try:
            val = int(inp)
            state.action_race_insert(val)
        except ValueError:
            state.message    = "Please enter a number."
            state.message_ok = False

    _stop.set()
    t.join(timeout=1)


# ── End screen ─────────────────────────────────────────────────────────────────

def end_screen(state: GameState):
    clear()
    print()
    if state.won:
        print(c("  🏆  YOU WIN!", BOLD, YELLOW))
    else:
        print(c("  💀  GAME OVER", BOLD, RED))
    print()
    print(f"  {c('Final Score:', BOLD)} {c(state.score, GREEN, BOLD)}")
    print(f"  {c('Rounds played:', BOLD)} {state.round}")
    s = state.stats()
    print(f"  {c('Tree size:', BOLD)} {s['size']}")
    print(f"  {c('Tree height:', BOLD)} {s['height']}")
    print(f"  {c('Inorder:', BOLD)} {s['inorder']}")
    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    while True:
        clear()
        print(BANNER)

        mode  = pick_mode()
        diff  = pick_difficulty()

        state = GameState()
        state.new_game(mode, diff)

        runners = {
            Mode.FIND:   run_find,
            Mode.INSERT: run_insert,
            Mode.DELETE: run_delete,
            Mode.SORT:   run_sort,
            Mode.RACE:   run_race,
        }
        runners[mode](state)

        end_screen(state)
        again = prompt("Play again? (y/n): ")
        if again.lower() not in ("y", "yes"):
            print(c("\n  Thanks for playing! 🌳\n", CYAN, BOLD))
            break


if __name__ == "__main__":
    main()
