# 🌳 Number Tree Challenge

A dynamic CLI number game built on a live Binary Search Tree.
The tree grows, shrinks, and updates in real time as you play.

## Run

```bash
python main.py   # start the game
python tests.py  # run all tests (no dependencies needed)
```

No external packages required — pure Python stdlib.

## Game Modes

| Mode | Description | Points |
|------|-------------|--------|
| 🔍 FIND | A number is highlighted — type it to claim you found it. Wrong guesses give BST hints (go left/right) | 10 |
| ➕ INSERT | A number is shown — type it to insert it into the correct BST position | 15 |
| 🗑️ DELETE | A node is marked — type its value to delete it (BST delete with successor replacement) | 15 |
| 📋 SORT | Type all node values in inorder (ascending) sequence | 20 |
| 🏁 RACE | Insert a queue of numbers into the tree before the timer runs out | 5/node |

## Difficulties

| | Nodes | Range | Race time |
|--|-------|-------|-----------|
| Easy   | 7  | 1–30  | 60s |
| Medium | 12 | 1–60  | 45s |
| Hard   | 18 | 1–99  | 30s |

## Project Structure

```
number-tree-game/
├── tree.py      # BST from scratch (insert, delete, search, traversals)
├── game.py      # GameState, 5 modes, scoring, lives, hints
├── renderer.py  # LevelRenderer (ANSI coloured tree), ASCIIRenderer
├── main.py      # CLI REPL, menus, mode runners, race timer thread
└── tests.py     # 16 unit tests (BST + game logic)
```

## Universal Commands (during any game)

- `h` — hint (costs 3 points)
- `s` — show stats panel
- `log` — show recent event log
- `q` — quit to menu
