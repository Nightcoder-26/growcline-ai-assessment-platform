"""
Curated Problems: Matrix, Strings, Stacks, Binary Search, Trees, and DP
Expands problem bank to ensure over 40+ high quality classic challenges.
"""

ADVANCED_CURATED_PROBLEMS = [
    # ── 1. Spiral Matrix Traversal ───────────────────────────────────────────
    {
        "title": "Spiral Matrix Traversal",
        "statement": "Given an m x n matrix, return all elements of the matrix in spiral order (clockwise starting from top-left).",
        "inputFormat": "Line 1: two integers m and n.\\nFollowed by m lines, each containing n space-separated integers.",
        "outputFormat": "A single line containing all matrix elements traversed in clockwise spiral order.",
        "constraints": "1 <= m, n <= 20\\n-100 <= matrix[i][j] <= 100",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Medium",
        "tags": ["arrays", "matrix", "simulation"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "3 3\\n1 2 3\\n4 5 6\\n7 8 9", "output": "1 2 3 6 9 8 7 4 5"},
            {"input": "3 4\\n1 2 3 4\\n5 6 7 8\\n9 10 11 12", "output": "1 2 3 4 8 12 11 10 9 5 6 7"},
        ],
        "hiddenTestCases": [
            {"input": "1 1\\n42", "output": "42"},
            {"input": "1 3\\n1 2 3", "output": "1 2 3"},
            {"input": "3 1\\n1\\n2\\n3", "output": "1 2 3"},
            {"input": "2 2\\n1 2\\n3 4", "output": "1 2 4 3"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    header = lines[0].split()
    m, n = int(header[0]), int(header[1])
    matrix = []
    for r in range(1, m + 1):
        matrix.append([int(x) for x in lines[r].split()])
    res = []
    top, bottom, left, right = 0, m - 1, 0, n - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                res.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    m, n = map(int, lines[0].split())
    mat = [[int(x) for x in lines[r].split()] for r in range(1, m + 1)]
    res = []
    top, bottom, left, right = 0, m - 1, 0, n - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1): res.append(mat[top][j])
        top += 1
        for i in range(top, bottom + 1): res.append(mat[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1): res.append(mat[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1): res.append(mat[i][left])
            left += 1
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    m, n = 3, 3
    rows = [' '.join(str(random.randint(1, 9)) for _ in range(n)) for _ in range(m)]
    return f"{m} {n}\\n" + '\\n'.join(rows)
""",
        "edgeCases": ["1 1\\n9", "2 2\\n1 2\\n3 4"],
        "mutations": [
            {
                "name": "flat_read",
                "type": "wrong_answer",
                "code": "import sys\nlines = sys.stdin.read().strip().split('\\n')\nprint(' '.join(' '.join(lines[1:]).split()))"
            }
        ]
    },

    # ── 2. Rotate Matrix 90 Degrees Clockwise ────────────────────────────────
    {
        "title": "Rotate Matrix 90 Degrees Clockwise",
        "statement": "You are given an n x n 2D matrix representing an image. Rotate the matrix by 90 degrees in-place (clockwise) and print the resulting matrix row by row.",
        "inputFormat": "Line 1: single integer n.\\nFollowed by n lines, each with n space-separated integers.",
        "outputFormat": "n lines representing the rotated matrix rows.",
        "constraints": "1 <= n <= 20\\n-1000 <= matrix[i][j] <= 1000",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Medium",
        "tags": ["arrays", "matrix"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "3\\n1 2 3\\n4 5 6\\n7 8 9", "output": "7 4 1\\n8 5 2\\n9 6 3"},
            {"input": "2\\n1 2\\n3 4", "output": "3 1\\n4 2"},
        ],
        "hiddenTestCases": [
            {"input": "1\\n5", "output": "5"},
            {"input": "4\\n5 1 9 11\\n2 4 8 10\\n13 3 6 7\\n15 14 12 16", "output": "15 13 2 5\\n14 3 4 1\\n12 6 8 9\\n16 7 10 11"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    n = int(lines[0].strip())
    mat = []
    for r in range(1, n + 1):
        mat.append([int(x) for x in lines[r].split()])
    # Transpose
    for i in range(n):
        for j in range(i + 1, n):
            mat[i][j], mat[j][i] = mat[j][i], mat[i][j]
    # Reverse rows
    for i in range(n):
        mat[i].reverse()
    for row in mat:
        print(' '.join(map(str, row)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    n = int(lines[0])
    mat = [[int(x) for x in lines[r].split()] for r in range(1, n + 1)]
    rot = [[mat[n - 1 - j][i] for j in range(n)] for i in range(n)]
    for r in rot: print(' '.join(map(str, r)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "3\\n1 2 3\\n4 5 6\\n7 8 9"
""",
        "edgeCases": ["1\\n10", "2\\n1 2\\n3 4"],
        "mutations": [
            {
                "name": "do_nothing",
                "type": "wrong_answer",
                "code": "import sys\nlines = sys.stdin.read().strip().split('\\n')\nfor l in lines[1:]: print(l)"
            }
        ]
    },

    # ── 3. Valid Palindrome Ignore Non-Alphanumeric ───────────────────────────
    {
        "title": "Valid Palindrome Ignore Non-Alphanumeric",
        "statement": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Return 'true' or 'false'.",
        "inputFormat": "A single line containing the phrase.",
        "outputFormat": "true or false",
        "constraints": "1 <= s.length <= 2 * 10^5",
        "topic": "Strings",
        "category": "Strings",
        "difficulty": "Easy",
        "tags": ["strings", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "A man, a plan, a canal: Panama", "output": "true"},
            {"input": "race a car", "output": "false"},
        ],
        "hiddenTestCases": [
            {"input": " ", "output": "true"},
            {"input": "0P", "output": "false"},
            {"input": "ab_a", "output": "true"},
            {"input": "Was it a car or a cat I saw?", "output": "true"},
        ],
        "referenceSolution": """import sys
def solve():
    s = sys.stdin.read().rstrip('\\r\\n')
    filtered = [ch.lower() for ch in s if ch.isalnum()]
    print('true' if filtered == filtered[::-1] else 'false')
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    s = sys.stdin.read().rstrip('\\r\\n')
    f = ''.join(c.lower() for c in s if c.isalnum())
    print('true' if f == f[::-1] else 'false')
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "No 'x' in Nixon"
""",
        "edgeCases": ["", " ", "a", "a."],
        "mutations": [
            {
                "name": "case_sensitive",
                "type": "wrong_answer",
                "code": "import sys\ns = [c for c in sys.stdin.read() if c.isalnum()]\nprint('true' if s == s[::-1] else 'false')"
            }
        ]
    },

    # ── 4. String Compression Run Length ─────────────────────────────────────
    {
        "title": "String Compression Run Length",
        "statement": "Given an array of characters chars, compress it using the following algorithm: For each group of consecutive repeating characters, write the character followed by the group's length if length > 1. Output the compressed string.",
        "inputFormat": "A single line of space-separated single characters.",
        "outputFormat": "A single string representing the compressed representation.",
        "constraints": "1 <= chars.length <= 2000",
        "topic": "Strings",
        "category": "Strings",
        "difficulty": "Medium",
        "tags": ["strings", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "a a b b c c c", "output": "a2b2c3"},
            {"input": "a", "output": "a"},
        ],
        "hiddenTestCases": [
            {"input": "a b b b b b b b b b b b", "output": "ab11"},
            {"input": "a a a a a", "output": "a5"},
            {"input": "x y z", "output": "xyz"},
        ],
        "referenceSolution": """import sys
def solve():
    chars = sys.stdin.read().split()
    if not chars: return
    res = []
    i = 0
    n = len(chars)
    while i < n:
        ch = chars[i]
        count = 0
        while i < n and chars[i] == ch:
            count += 1
            i += 1
        res.append(ch)
        if count > 1:
            res.append(str(count))
    print(''.join(res))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
from itertools import groupby
def solve():
    chars = sys.stdin.read().split()
    res = []
    for k, g in groupby(chars):
        c = len(list(g))
        res.append(k)
        if c > 1: res.append(str(c))
    print(''.join(res))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "a a a b b c c c c"
""",
        "edgeCases": ["a", "a a", "a b c"],
        "mutations": [
            {
                "name": "include_ones",
                "type": "wrong_answer",
                "code": "print('a1')"
            }
        ]
    },

    # ── 5. Evaluate Reverse Polish Notation ──────────────────────────────────
    {
        "title": "Evaluate Reverse Polish Notation",
        "statement": "Evaluate the value of an arithmetic expression in Reverse Polish Notation. Valid operators are +, -, *, and /. Each operand may be an integer or another expression. Division between two integers truncates toward zero.",
        "inputFormat": "A single line containing space-separated tokens.",
        "outputFormat": "A single integer denoting the expression result.",
        "constraints": "1 <= tokens.length <= 10^4\\ntokens[i] is either an operator or an integer.",
        "topic": "Stacks",
        "category": "Stacks",
        "difficulty": "Medium",
        "tags": ["stacks", "math"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2 1 + 3 *", "output": "9"},
            {"input": "4 13 5 / +", "output": "6"},
        ],
        "hiddenTestCases": [
            {"input": "10 6 9 3 + -11 * / * 17 + 5 +", "output": "22"},
            {"input": "3", "output": "3"},
            {"input": "5 1 -", "output": "4"},
            {"input": "0 3 /", "output": "0"},
        ],
        "referenceSolution": """import sys
def solve():
    tokens = sys.stdin.read().split()
    if not tokens: return
    stack = []
    ops = {'+', '-', '*', '/'}
    for t in tokens:
        if t not in ops:
            stack.append(int(t))
        else:
            b = stack.pop()
            a = stack.pop()
            if t == '+': stack.append(a + b)
            elif t == '-': stack.append(a - b)
            elif t == '*': stack.append(a * b)
            elif t == '/': stack.append(int(a / b))
    print(stack[0])
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    tokens = sys.stdin.read().split()
    stack = []
    for t in tokens:
        if t == '+': stack.append(stack.pop(-2) + stack.pop())
        elif t == '-': stack.append(stack.pop(-2) - stack.pop())
        elif t == '*': stack.append(stack.pop(-2) * stack.pop())
        elif t == '/': stack.append(int(stack.pop(-2) / stack.pop()))
        else: stack.append(int(t))
    print(stack[0])
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "3 4 + 2 * 7 /"
""",
        "edgeCases": ["42", "1 1 +", "6 2 /"],
        "mutations": [
            {
                "name": "float_div",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    },

    # ── 6. Search a 2D Matrix ────────────────────────────────────────────────
    {
        "title": "Search a 2D Matrix",
        "statement": "Write an efficient algorithm that searches for a value target in an m x n integer matrix. Integers in each row are sorted from left to right, and the first integer of each row is greater than the last integer of the previous row. Return 'true' or 'false'.",
        "inputFormat": "Line 1: m n target\\nFollowed by m lines of n space-separated integers.",
        "outputFormat": "true or false",
        "constraints": "m == matrix.length\\nn == matrix[i].length\\n1 <= m, n <= 100",
        "topic": "Binary Search",
        "category": "Binary Search",
        "difficulty": "Medium",
        "tags": ["binary-search", "matrix"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "3 4 3\\n1 3 5 7\\n10 11 16 20\\n23 30 34 60", "output": "true"},
            {"input": "3 4 13\\n1 3 5 7\\n10 11 16 20\\n23 30 34 60", "output": "false"},
        ],
        "hiddenTestCases": [
            {"input": "1 1 1\\n1", "output": "true"},
            {"input": "1 1 2\\n1", "output": "false"},
            {"input": "1 2 5\\n1 5", "output": "true"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    header = lines[0].split()
    m, n, target = int(header[0]), int(header[1]), int(header[2])
    matrix = []
    for r in range(1, m + 1):
        matrix.append([int(x) for x in lines[r].split()])
    l, r = 0, m * n - 1
    while l <= r:
        mid = (l + r) // 2
        val = matrix[mid // n][mid % n]
        if val == target:
            print('true')
            return
        elif val < target:
            l = mid + 1
        else:
            r = mid - 1
    print('false')
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    header = lines[0].split()
    m, n, target = int(header[0]), int(header[1]), int(header[2])
    found = False
    for r in range(1, m + 1):
        for x in lines[r].split():
            if int(x) == target: found = True
    print('true' if found else 'false')
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "2 2 4\\n1 2\\n3 4"
""",
        "edgeCases": ["1 1 1\\n1", "1 1 2\\n1"],
        "mutations": [
            {
                "name": "always_true",
                "type": "wrong_answer",
                "code": "print('true')"
            }
        ]
    },

    # ── 7. Lowest Common Ancestor in BST ──────────────────────────────────────
    {
        "title": "Lowest Common Ancestor in BST",
        "statement": "Given a binary search tree (BST) in level-order and two node values p and q, find the lowest common ancestor (LCA) node value of the two given nodes in the BST.",
        "inputFormat": "Line 1: space-separated BST values in level-order (with 'null' for missing).\\nLine 2: two integers p and q.",
        "outputFormat": "A single integer denoting the LCA value.",
        "constraints": "The number of nodes in the tree is in the range [2, 10^5].\\nAll Node.val are unique.",
        "topic": "Trees",
        "category": "Trees",
        "difficulty": "Easy",
        "tags": ["trees", "bst"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "6 2 8 0 4 7 9 null null 3 5\\n2 8", "output": "6"},
            {"input": "6 2 8 0 4 7 9 null null 3 5\\n2 4", "output": "2"},
        ],
        "hiddenTestCases": [
            {"input": "2 1\\n2 1", "output": "2"},
            {"input": "5 3 6 2 4 null null 1\\n1 4", "output": "3"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    raw = lines[0].split()
    pq = [int(x) for x in lines[1].split()]
    p, q = pq[0], pq[1]
    # Reconstruct BST
    curr_idx = 0
    curr_val = int(raw[0])
    while True:
        if p < curr_val and q < curr_val:
            curr_idx = 2 * curr_idx + 1
        elif p > curr_val and q > curr_val:
            curr_idx = 2 * curr_idx + 2
        else:
            print(curr_val)
            return
        if curr_idx < len(raw) and raw[curr_idx] != 'null':
            curr_val = int(raw[curr_idx])
        else:
            print(curr_val)
            return
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    raw = lines[0].split()
    p, q = map(int, lines[1].split())
    idx = 0
    v = int(raw[0])
    while True:
        if p < v and q < v and 2*idx+1 < len(raw) and raw[2*idx+1] != 'null':
            idx = 2*idx + 1
            v = int(raw[idx])
        elif p > v and q > v and 2*idx+2 < len(raw) and raw[2*idx+2] != 'null':
            idx = 2*idx + 2
            v = int(raw[idx])
        else:
            print(v)
            return
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "6 2 8 0 4 7 9\\n2 8"
""",
        "edgeCases": ["2 1\\n2 1", "5 3 7\\n3 7"],
        "mutations": [
            {
                "name": "return_p",
                "type": "wrong_answer",
                "code": "print(sys.stdin.read().split('\\n')[1].split()[0])"
            }
        ]
    },

    # ── 8. Longest Common Subsequence ────────────────────────────────────────
    {
        "title": "Longest Common Subsequence",
        "statement": "Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.",
        "inputFormat": "Line 1: string text1\\nLine 2: string text2",
        "outputFormat": "A single integer denoting the LCS length.",
        "constraints": "1 <= text1.length, text2.length <= 1000\\nStrings consist of lowercase English characters only.",
        "topic": "Dynamic Programming",
        "category": "Dynamic Programming",
        "difficulty": "Medium",
        "tags": ["dynamic-programming", "strings"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "abcde\\nace", "output": "3"},
            {"input": "abc\\nabc", "output": "3"},
        ],
        "hiddenTestCases": [
            {"input": "abc\\ndef", "output": "0"},
            {"input": "ezupkr\\nubmrapg", "output": "2"},
            {"input": "oxcp\\np", "output": "1"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2:
        print(0)
        return
    s1 = lines[0].strip()
    s2 = lines[1].strip()
    m, n = len(s1), len(s2)
    dp = [0] * (n + 1)
    for i in range(1, m + 1):
        prev = 0
        for j in range(1, n + 1):
            tmp = dp[j]
            if s1[i - 1] == s2[j - 1]:
                dp[j] = prev + 1
            else:
                dp[j] = max(dp[j], dp[j - 1])
            prev = tmp
    print(dp[n])
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    s1, s2 = lines[0].strip(), lines[1].strip()
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]: dp[i][j] = dp[i-1][j-1] + 1
            else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    print(dp[m][n])
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    return "abcdef\\nacdf"
""",
        "edgeCases": ["a\\na", "a\\nb", "ab\\nba"],
        "mutations": [
            {
                "name": "min_length",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    }
]
