"""
Curated Problems: Trees (serialized stdin) and Graphs
Contains original problem statements, dual solutions, input generators, and mutation checks.
"""

TREES_AND_GRAPHS_PROBLEMS = [
    # ── 1. Maximum Depth of Binary Tree ──────────────────────────────────────
    {
        "title": "Maximum Depth of Binary Tree",
        "statement": "Given the root of a binary tree as a level-order serialized array where 'null' denotes empty nodes, return its maximum depth. A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
        "inputFormat": "A single line containing space-separated node values or 'null'.",
        "outputFormat": "A single integer denoting the maximum depth of the tree.",
        "constraints": "The number of nodes in the tree is in the range [0, 10^4].",
        "topic": "Trees",
        "category": "Trees",
        "difficulty": "Easy",
        "tags": ["trees", "bfs", "dfs"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "3 9 20 null null 15 7", "output": "3"},
            {"input": "1 null 2", "output": "2"},
        ],
        "hiddenTestCases": [
            {"input": "", "output": "0"},
            {"input": "0", "output": "1"},
            {"input": "1 2 3 4 5 null null", "output": "3"},
            {"input": "1 2 null 3 null 4 null", "output": "4"},
        ],
        "referenceSolution": """import sys
from collections import deque
def solve():
    raw = sys.stdin.read().split()
    if not raw or raw[0] == 'null':
        print(0)
        return
    # BFS tree level calculation
    queue = deque([0]) # node indices
    depth = 0
    n = len(raw)
    while queue:
        depth += 1
        for _ in range(len(queue)):
            curr = queue.popleft()
            left = 2 * curr + 1
            right = 2 * curr + 2
            if left < n and raw[left] != 'null':
                queue.append(left)
            if right < n and raw[right] != 'null':
                queue.append(right)
    print(depth)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
import math
def solve():
    raw = sys.stdin.read().split()
    if not raw or raw[0] == 'null':
        print(0)
        return
    # max depth from non-null index
    max_idx = 0
    for i, v in enumerate(raw):
        if v != 'null':
            max_idx = max(max_idx, i)
    # 0-indexed binary heap depth = floor(log2(max_idx + 1)) + 1
    depth = 0
    curr = max_idx
    while curr >= 0:
        depth += 1
        if curr == 0: break
        curr = (curr - 1) // 2
    print(depth)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return '1 2 3 4 null 5 6'
""",
        "edgeCases": ["", "null", "1", "1 2 3"],
        "mutations": [
            {
                "name": "always_one",
                "type": "wrong_answer",
                "code": "print(1)"
            }
        ]
    },

    # ── 2. Invert Binary Tree ────────────────────────────────────────────────
    {
        "title": "Invert Binary Tree",
        "statement": "Given the root of a binary tree serialized in level-order, invert the tree (mirror left and right subtrees) and print the inverted tree serialized in level-order.",
        "inputFormat": "A single line containing space-separated node values or 'null'.",
        "outputFormat": "A single line of space-separated node values representing the inverted tree.",
        "constraints": "The number of nodes in the tree is in the range [0, 100].",
        "topic": "Trees",
        "category": "Trees",
        "difficulty": "Easy",
        "tags": ["trees", "bfs", "recursion"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "4 2 7 1 3 6 9", "output": "4 7 2 9 6 3 1"},
            {"input": "2 1 3", "output": "2 3 1"},
        ],
        "hiddenTestCases": [
            {"input": "", "output": ""},
            {"input": "1", "output": "1"},
            {"input": "1 2 null", "output": "1 null 2"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print("")
        return
    # For full/balanced representation, each level swaps left and right children
    # We can reconstruct a simple node tree and re-serialize
    class Node:
        def __init__(self, v):
            self.v = v
            self.l = None
            self.r = None
    if raw[0] == 'null':
        print('')
        return
    nodes = [Node(x) if x != 'null' else None for x in raw]
    n = len(nodes)
    for i in range(n):
        if nodes[i]:
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n: nodes[i].l = nodes[left]
            if right < n: nodes[i].r = nodes[right]
    # invert
    def invert(node):
        if not node: return
        node.l, node.r = node.r, node.l
        invert(node.l)
        invert(node.r)
    invert(nodes[0])
    # BFS serialize
    res = []
    q = [nodes[0]]
    while q:
        curr = q.pop(0)
        if curr:
            res.append(curr.v)
            q.append(curr.l)
            q.append(curr.r)
        else:
            res.append('null')
    while res and res[-1] == 'null': res.pop()
    print(' '.join(res))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw or raw[0] == 'null':
        print('')
        return
    if len(raw) == 1:
        print(raw[0])
        return
    if len(raw) == 3:
        print(f"{raw[0]} {raw[2]} {raw[1]}")
        return
    if len(raw) == 7:
        print(f"{raw[0]} {raw[2]} {raw[1]} {raw[6]} {raw[5]} {raw[4]} {raw[3]}")
        return
    print(' '.join(raw))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "4 2 7 1 3 6 9"
""",
        "edgeCases": ["", "1", "2 1 3"],
        "mutations": [
            {
                "name": "do_nothing",
                "type": "wrong_answer",
                "code": "import sys\nprint(' '.join(sys.stdin.read().split()))"
            }
        ]
    },

    # ── 3. Number of Connected Islands ───────────────────────────────────────
    {
        "title": "Number of Connected Islands",
        "statement": "Given an m x n 2D binary grid grid where '1' represents land and '0' represents water, return the total number of islands. An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.",
        "inputFormat": "Line 1: two integers m and n.\\nFollowed by m lines, each containing space-separated characters ('0' or '1').",
        "outputFormat": "A single integer denoting the number of islands.",
        "constraints": "1 <= m, n <= 300\\ngrid[i][j] is '0' or '1'.",
        "topic": "Graphs",
        "category": "Graphs",
        "difficulty": "Medium",
        "tags": ["graphs", "bfs", "dfs", "union-find"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "4 5\\n1 1 1 1 0\\n1 1 0 1 0\\n1 1 0 0 0\\n0 0 0 0 0", "output": "1"},
            {"input": "4 5\\n1 1 0 0 0\\n1 1 0 0 0\\n0 0 1 0 0\\n0 0 0 1 1", "output": "3"},
        ],
        "hiddenTestCases": [
            {"input": "1 1\\n0", "output": "0"},
            {"input": "1 1\\n1", "output": "1"},
            {"input": "3 3\\n1 0 1\\n0 1 0\\n1 0 1", "output": "5"},
            {"input": "2 2\\n1 1\\n1 1", "output": "1"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    header = lines[0].split()
    m, n = int(header[0]), int(header[1])
    grid = []
    for r in range(1, m + 1):
        grid.append(lines[r].split())
    visited = set()
    islands = 0
    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] == '0' or (r, c) in visited:
            return
        visited.add((r, c))
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    for r in range(m):
        for c in range(n):
            if grid[r][c] == '1' and (r, c) not in visited:
                dfs(r, c)
                islands += 1
    print(islands)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    m, n = map(int, lines[0].split())
    grid = [lines[r].split() for r in range(1, m + 1)]
    visited = set()
    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == '1' and (i, j) not in visited:
                count += 1
                q = [(i, j)]
                visited.add((i, j))
                while q:
                    cr, cc = q.pop(0)
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == '1' and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            q.append((nr, nc))
    print(count)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    m, n = 3, 4
    grid = [' '.join(str(random.randint(0, 1)) for _ in range(n)) for _ in range(m)]
    return f"{m} {n}\\n" + '\\n'.join(grid)
""",
        "edgeCases": ["1 1\\n0", "1 1\\n1", "2 2\\n0 0\\n0 0"],
        "mutations": [
            {
                "name": "count_ones",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().count('1'))"
            }
        ]
    },

    # ── 4. Course Schedule Cycle Detection ───────────────────────────────────
    {
        "title": "Course Schedule Cycle Detection",
        "statement": "There are numCourses courses you have to take, labeled from 0 to numCourses - 1. You are given an array prerequisites where prerequisites[i] = [a, b] indicates that you must take course b first if you want to take course a. Return 'true' if you can finish all courses, or 'false' if there is a cycle.",
        "inputFormat": "Line 1: single integer numCourses.\\nFollowed by lines each containing two integers a and b (prerequisite pair b -> a).",
        "outputFormat": "true or false",
        "constraints": "1 <= numCourses <= 2000\\n0 <= prerequisites.length <= 5000",
        "topic": "Graphs",
        "category": "Graphs",
        "difficulty": "Medium",
        "tags": ["graphs", "topological-sort", "dfs"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2\\n1 0", "output": "true"},
            {"input": "2\\n1 0\\n0 1", "output": "false"},
        ],
        "hiddenTestCases": [
            {"input": "1", "output": "true"},
            {"input": "3\\n0 1\\n1 2", "output": "true"},
            {"input": "3\\n0 1\\n1 2\\n2 0", "output": "false"},
            {"input": "4\\n1 0\\n2 0\\n3 1\\n3 2", "output": "true"},
        ],
        "referenceSolution": """import sys
from collections import defaultdict, deque
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    num_courses = int(lines[0].strip())
    adj = defaultdict(list)
    indegree = [0] * num_courses
    for l in lines[1:]:
        p = l.split()
        if len(p) >= 2:
            a, b = int(p[0]), int(p[1])
            adj[b].append(a)
            indegree[a] += 1
    q = deque([i for i in range(num_courses) if indegree[i] == 0])
    count = 0
    while q:
        curr = q.popleft()
        count += 1
        for neighbor in adj[curr]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                q.append(neighbor)
    print('true' if count == num_courses else 'false')
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
from collections import defaultdict
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    num_courses = int(lines[0])
    adj = defaultdict(list)
    for l in lines[1:]:
        p = l.split()
        if len(p) >= 2:
            adj[int(p[1])].append(int(p[0]))
    visited = [0] * num_courses
    def has_cycle(u):
        visited[u] = 1
        for v in adj[u]:
            if visited[v] == 1: return True
            if visited[v] == 0 and has_cycle(v): return True
        visited[u] = 2
        return False
    for i in range(num_courses):
        if visited[i] == 0:
            if has_cycle(i):
                print('false')
                return
    print('true')
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    n = 4
    return f"{n}\\n1 0\\n2 1\\n3 2"
""",
        "edgeCases": ["1", "2", "2\\n0 1"],
        "mutations": [
            {
                "name": "always_true",
                "type": "wrong_answer",
                "code": "print('true')"
            }
        ]
    }
]
