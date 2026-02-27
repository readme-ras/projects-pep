"""
Binary Search Tree used as the game's core data structure.
Each node holds a value and tracks game-specific metadata.
"""


class TreeNode:
    def __init__(self, value: int, depth: int = 0):
        self.value    = value
        self.left     = None
        self.right    = None
        self.depth    = depth
        self.parent   = None
        self.is_target = False   # highlighted when it is the current target
        self.just_inserted = True  # flash animation flag

    def __repr__(self):
        return f"Node({self.value})"


class BST:
    def __init__(self):
        self.root   = None
        self.size   = 0
        self._nodes = []   # flat list for fast lookup

    # ── Insert ────────────────────────────────────────────────────────────────

    def insert(self, value: int) -> TreeNode:
        node = TreeNode(value)
        if self.root is None:
            self.root = node
            node.depth = 0
        else:
            self._insert_recursive(self.root, node)
        self.size += 1
        self._nodes.append(node)
        return node

    def _insert_recursive(self, current: TreeNode, node: TreeNode):
        node.depth = current.depth + 1
        if node.value < current.value:
            if current.left is None:
                current.left   = node
                node.parent    = current
            else:
                self._insert_recursive(current.left, node)
        else:
            if current.right is None:
                current.right  = node
                node.parent    = current
            else:
                self._insert_recursive(current.right, node)

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, value: int) -> TreeNode | None:
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node, value):
        if node is None or node.value == value:
            return node
        if value < node.value:
            return self._search_recursive(node.left, value)
        return self._search_recursive(node.right, value)

    def contains(self, value: int) -> bool:
        return self.search(value) is not None

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, value: int) -> bool:
        node = self.search(value)
        if node is None:
            return False
        self._delete_node(node)
        self._nodes = [n for n in self._nodes if n.value != value]
        self.size -= 1
        return True

    def _delete_node(self, node: TreeNode):
        # Case 1: leaf
        if node.left is None and node.right is None:
            self._replace(node, None)
        # Case 2: one child
        elif node.left is None:
            self._replace(node, node.right)
        elif node.right is None:
            self._replace(node, node.left)
        # Case 3: two children — replace with in-order successor
        else:
            successor = self._min_node(node.right)
            node.value = successor.value
            # re-sync flat list
            for n in self._nodes:
                if n is node:
                    n.value = successor.value
            self._delete_node(successor)
            return

    def _replace(self, node: TreeNode, replacement):
        if node.parent is None:
            self.root = replacement
        elif node.parent.left is node:
            node.parent.left = replacement
        else:
            node.parent.right = replacement
        if replacement:
            replacement.parent = node.parent

    def _min_node(self, node: TreeNode) -> TreeNode:
        while node.left:
            node = node.left
        return node

    # ── Traversals ────────────────────────────────────────────────────────────

    def inorder(self) -> list[int]:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)

    def height(self) -> int:
        return self._height(self.root)

    def _height(self, node) -> int:
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    def all_values(self) -> list[int]:
        return [n.value for n in self._nodes]

    def clear(self):
        self.root   = None
        self.size   = 0
        self._nodes = []
