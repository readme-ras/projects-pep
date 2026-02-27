"""
Two renderers:
  1. ASCIIRenderer  — pure-text tree (always works)
  2. RichRenderer   — colorful terminal tree using the `rich` library
"""

from tree import BST, TreeNode


# ── ANSI colours (no deps) ────────────────────────────────────────────────────

R = "\033[0m"      # reset
BOLD  = "\033[1m"
DIM   = "\033[2m"
RED   = "\033[91m"
GREEN = "\033[92m"
YELLOW= "\033[93m"
BLUE  = "\033[94m"
CYAN  = "\033[96m"
MAG   = "\033[95m"


def _node_str(node: TreeNode) -> str:
    val = str(node.value).center(4)
    if node.is_target:
        return f"{RED}{BOLD}[{val}]{R}"
    if node.just_inserted:
        return f"{GREEN}{BOLD}({val}){R}"
    return f"{CYAN}{BOLD} {val} {R}"


# ── ASCII renderer ─────────────────────────────────────────────────────────────

class ASCIIRenderer:
    """
    Renders a BST as a 2-D grid using a level-order layout.
    Works for trees up to height ~6 before it gets wide.
    """

    def render(self, bst: BST, width: int = 80) -> str:
        if bst.root is None:
            return f"{DIM}  (empty tree){R}"

        lines = []
        self._build_lines(bst.root, lines, "", is_left=True)
        return "\n".join(lines)

    def _build_lines(self, node: TreeNode | None, lines: list, prefix: str, is_left: bool):
        if node is None:
            return
        # Right child first (prints on top)
        self._build_lines(node.right, lines, prefix + ("│   " if is_left else "    "), False)

        connector = "└── " if is_left else "┌── "
        lines.append(prefix + connector + _node_str(node))

        # Left child
        self._build_lines(node.left, lines, prefix + ("    " if is_left else "│   "), True)


# ── Compact level-order renderer ──────────────────────────────────────────────

class LevelRenderer:
    """
    Renders the tree level by level with branch lines.
    Better for displaying the actual structure visually.
    """

    def render(self, bst: BST) -> str:
        if bst.root is None:
            return f"{DIM}  (empty tree){R}"

        from collections import deque

        # Collect nodes level by level
        levels: list[list] = []
        q = deque([(bst.root, 0)])
        while q:
            node, lvl = q.popleft()
            while len(levels) <= lvl:
                levels.append([])
            if node:
                levels[lvl].append(node)
                q.append((node.left,  lvl + 1))
                q.append((node.right, lvl + 1))
            else:
                levels[lvl].append(None)

        # Trim trailing None-only levels
        while levels and all(n is None for n in levels[-1]):
            levels.pop()

        max_w  = 70
        output = []
        n_levels = len(levels)

        for lvl, nodes in enumerate(levels):
            # Spacing: exponentially shrink as we go deeper
            slot  = max_w // (2 ** (lvl + 1)) if lvl < 5 else 3
            slot  = max(slot, 4)
            parts = []
            for node in nodes:
                if node:
                    parts.append(_node_str(node).center(slot + 10))  # +10 for ANSI codes
                else:
                    parts.append(" " * slot)
            output.append("".join(parts))

            # Draw branch lines
            if lvl < n_levels - 1:
                branch_line = []
                for node in nodes:
                    left_b  = "/" if (node and node.left)  else " "
                    right_b = "\\" if (node and node.right) else " "
                    inner = max(slot - 2, 1)
                    branch_line.append(
                        f"{DIM}{left_b}{' ' * inner}{right_b}{R}".center(slot + 10)
                    )
                output.append("".join(branch_line))

        header = (
            f"{BOLD}{CYAN}{'─'*60}{R}\n"
            f"{BOLD}  BST  "
            f"{DIM}│ Size:{R} {YELLOW}{bst.size}{R}  "
            f"{DIM}│ Height:{R} {YELLOW}{bst.height()}{R}  "
            f"{DIM}│ Inorder: {R}{BLUE}{bst.inorder()}{R}\n"
            f"{BOLD}{CYAN}{'─'*60}{R}"
        )
        legend = (
            f"\n  {RED}{BOLD}[  ]{R} = target   "
            f"{GREEN}{BOLD}(  ){R} = just inserted   "
            f"{CYAN} value {R} = normal"
        )
        return header + "\n" + "\n".join(output) + legend
