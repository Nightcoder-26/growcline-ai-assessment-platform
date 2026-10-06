"""
Curated Problems: Dynamic Programming, Greedy, and Sorting
Contains original problem statements, dual solutions, input generators, and mutation checks.
"""

DP_GREEDY_SORTING_PROBLEMS = [
    # ── 1. Climbing Stairs Steps ─────────────────────────────────────────────
    {
        "title": "Climbing Stairs Steps",
        "statement": "You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "inputFormat": "A single line containing the integer n.",
        "outputFormat": "A single integer denoting the number of distinct ways.",
        "constraints": "1 <= n <= 45",
        "topic": "Dynamic Programming",
        "category": "Dynamic Programming",
        "difficulty": "Easy",
        "tags": ["dynamic-programming", "math"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2", "output": "2"},
            {"input": "3", "output": "3"},
        ],
        "hiddenTestCases": [
            {"input": "1", "output": "1"},
            {"input": "4", "output": "5"},
            {"input": "5", "output": "8"},
            {"input": "10", "output": "89"},
            {"input": "20", "output": "10946"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().strip()
    if not raw: return
    n = int(raw)
    if n <= 2:
        print(n)
        return
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    n = int(sys.stdin.read().strip())
    def ways(step):
        if step > n: return 0
        if step == n: return 1
        return ways(step + 1) + ways(step + 2)
    print(ways(0) if n <= 25 else (ways(0) if n <= 25 else 0))
if __name__ == '__main__':
    raw = sys.stdin.read().strip()
    n = int(raw)
    dp = [0] * (n + 2)
    dp[1] = 1; dp[2] = 2
    for i in range(3, n + 1): dp[i] = dp[i-1] + dp[i-2]
    print(dp[n])
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return str(random.randint(4, 25))
""",
        "edgeCases": ["1", "2", "3", "45"],
        "mutations": [
            {
                "name": "return_n",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().strip())"
            }
        ]
    },

    # ── 2. House Robber Maximum Loot ─────────────────────────────────────────
    {
        "title": "House Robber Maximum Loot",
        "statement": "You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed. Adjacent houses have security systems connected and will automatically contact the police if two adjacent houses were broken into on the same night. Return the maximum amount of money you can rob tonight without alerting the police.",
        "inputFormat": "A single line containing space-separated non-negative integers.",
        "outputFormat": "A single integer denoting the maximum loot value.",
        "constraints": "1 <= nums.length <= 100\\n0 <= nums[i] <= 400",
        "topic": "Dynamic Programming",
        "category": "Dynamic Programming",
        "difficulty": "Medium",
        "tags": ["dynamic-programming", "arrays"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 1", "output": "4"},
            {"input": "2 7 9 3 1", "output": "12"},
        ],
        "hiddenTestCases": [
            {"input": "0", "output": "0"},
            {"input": "100", "output": "100"},
            {"input": "2 1 1 2", "output": "4"},
            {"input": "10 5 2 20", "output": "30"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print(0)
        return
    nums = [int(x) for x in raw]
    prev1, prev2 = 0, 0
    for x in nums:
        curr = max(prev1, prev2 + x)
        prev2 = prev1
        prev1 = curr
    print(prev1)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    nums = [int(x) for x in raw]
    n = len(nums)
    def rob(idx):
        if idx >= n: return 0
        return max(nums[idx] + rob(idx + 2), rob(idx + 1))
    print(rob(0))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(1, 50)) for _ in range(8))
""",
        "edgeCases": ["0", "5", "10 1", "1 10"],
        "mutations": [
            {
                "name": "sum_all",
                "type": "wrong_answer",
                "code": "import sys\nprint(sum(int(x) for x in sys.stdin.read().split()))"
            }
        ]
    },

    # ── 3. Coin Change Fewest Coins ──────────────────────────────────────────
    {
        "title": "Coin Change Fewest Coins",
        "statement": "You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.",
        "inputFormat": "Line 1: space-separated coin denominations.\\nLine 2: single integer amount.",
        "outputFormat": "A single integer denoting the minimum coins needed, or -1.",
        "constraints": "1 <= coins.length <= 12\\n1 <= coins[i] <= 2^31 - 1\\n0 <= amount <= 10^4",
        "topic": "Dynamic Programming",
        "category": "Dynamic Programming",
        "difficulty": "Medium",
        "tags": ["dynamic-programming", "bfs"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 5\\n11", "output": "3"},
            {"input": "2\\n3", "output": "-1"},
        ],
        "hiddenTestCases": [
            {"input": "1\\n0", "output": "0"},
            {"input": "1\\n1", "output": "1"},
            {"input": "1\\n2", "output": "2"},
            {"input": "2 5 10 1\\n27", "output": "4"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    coins = [int(x) for x in lines[0].split()]
    amount = int(lines[1].strip())
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if a - c >= 0:
                dp[a] = min(dp[a], dp[a - c] + 1)
    print(dp[amount] if dp[amount] != float('inf') else -1)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    coins = [int(x) for x in lines[0].split()]
    amount = int(lines[1].strip())
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if a >= c: dp[a] = min(dp[a], dp[a - c] + 1)
    print(dp[amount] if dp[amount] != float('inf') else -1)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return "1 5 10 25\\n47"
""",
        "edgeCases": ["1\\n0", "2\\n3", "5\\n5"],
        "mutations": [
            {
                "name": "greedy_only",
                "type": "wrong_answer",
                "code": "print(1)"
            }
        ]
    },

    # ── 4. Jump Game Reachability ────────────────────────────────────────────
    {
        "title": "Jump Game Reachability",
        "statement": "You are given an integer array nums. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position. Return 'true' if you can reach the last index, or 'false' otherwise.",
        "inputFormat": "A single line containing space-separated non-negative integers.",
        "outputFormat": "true or false",
        "constraints": "1 <= nums.length <= 10^4\\n0 <= nums[i] <= 10^5",
        "topic": "Greedy",
        "category": "Greedy",
        "difficulty": "Medium",
        "tags": ["greedy", "dynamic-programming"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2 3 1 1 4", "output": "true"},
            {"input": "3 2 1 0 4", "output": "false"},
        ],
        "hiddenTestCases": [
            {"input": "0", "output": "true"},
            {"input": "2 0 0", "output": "true"},
            {"input": "1 1 1 1", "output": "true"},
            {"input": "0 2 3", "output": "false"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    max_reach = 0
    n = len(nums)
    for i in range(n):
        if i > max_reach:
            print('false')
            return
        max_reach = max(max_reach, i + nums[i])
        if max_reach >= n - 1:
            print('true')
            return
    print('true')
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    nums = [int(x) for x in raw]
    n = len(nums)
    reachable = [False] * n
    reachable[0] = True
    for i in range(n):
        if reachable[i]:
            for j in range(1, nums[i] + 1):
                if i + j < n: reachable[i + j] = True
    print('true' if reachable[-1] else 'false')
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(1, 4)) for _ in range(8))
""",
        "edgeCases": ["0", "1 0", "0 1"],
        "mutations": [
            {
                "name": "always_true",
                "type": "wrong_answer",
                "code": "print('true')"
            }
        ]
    },

    # ── 5. Merge Overlapping Intervals ───────────────────────────────────────
    {
        "title": "Merge Overlapping Intervals",
        "statement": "Given an array of intervals where each interval is represented by start and end integers, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
        "inputFormat": "Each line contains two space-separated integers: start and end.",
        "outputFormat": "Print each merged interval on a new line as two space-separated integers, ordered by start time.",
        "constraints": "1 <= intervals.length <= 10^4\\n0 <= start_i <= end_i <= 10^4",
        "topic": "Sorting",
        "category": "Sorting",
        "difficulty": "Medium",
        "tags": ["sorting", "arrays"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 3\\n2 6\\n8 10\\n15 18", "output": "1 6\\n8 10\\n15 18"},
            {"input": "1 4\\n4 5", "output": "1 5"},
        ],
        "hiddenTestCases": [
            {"input": "1 4", "output": "1 4"},
            {"input": "1 4\\n0 4", "output": "0 4"},
            {"input": "1 4\\n2 3", "output": "1 4"},
            {"input": "2 3\\n4 5\\n6 7\\n1 10", "output": "1 10"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    intervals = []
    for l in lines:
        p = l.split()
        if len(p) >= 2:
            intervals.append([int(p[0]), int(p[1])])
    if not intervals: return
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for curr in intervals[1:]:
        prev = merged[-1]
        if curr[0] <= prev[1]:
            prev[1] = max(prev[1], curr[1])
        else:
            merged.append(curr)
    for iv in merged:
        print(f"{iv[0]} {iv[1]}")
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    intervals = [[int(x) for x in l.split()] for l in lines if len(l.split()) >= 2]
    intervals.sort(key=lambda x: x[0])
    res = []
    for iv in intervals:
        if not res or res[-1][1] < iv[0]:
            res.append(iv)
        else:
            res[-1][1] = max(res[-1][1], iv[1])
    for iv in res: print(f"{iv[0]} {iv[1]}")
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return "1 4\\n2 5\\n7 9\\n8 10"
""",
        "edgeCases": ["1 2", "1 5\\n2 3", "1 2\\n3 4"],
        "mutations": [
            {
                "name": "no_merging",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().strip())"
            }
        ]
    },

    # ── 6. Sort Colors Dutch Flag ────────────────────────────────────────────
    {
        "title": "Sort Colors Dutch Flag",
        "statement": "Given an array nums with n objects colored red, white, or blue, sort them in-place so that objects of the same color are adjacent, with the colors in the order red, white, and blue. We use the integers 0, 1, and 2 to represent the colors red, white, and blue, respectively.",
        "inputFormat": "A single line containing space-separated integers (only 0s, 1s, and 2s).",
        "outputFormat": "A single line containing the space-separated sorted integers.",
        "constraints": "1 <= nums.length <= 300\\nnums[i] is either 0, 1, or 2.",
        "topic": "Sorting",
        "category": "Sorting",
        "difficulty": "Medium",
        "tags": ["sorting", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2 0 2 1 1 0", "output": "0 0 1 1 2 2"},
            {"input": "2 0 1", "output": "0 1 2"},
        ],
        "hiddenTestCases": [
            {"input": "0", "output": "0"},
            {"input": "1", "output": "1"},
            {"input": "2 2 2", "output": "2 2 2"},
            {"input": "1 0 2 1 0", "output": "0 0 1 1 2"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
    print(' '.join(map(str, nums)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    nums = sorted(int(x) for x in raw)
    print(' '.join(map(str, nums)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(0, 2)) for _ in range(12))
""",
        "edgeCases": ["0", "1", "2", "2 1 0"],
        "mutations": [
            {
                "name": "reverse_sort",
                "type": "wrong_answer",
                "code": "import sys\nprint(' '.join(sorted(sys.stdin.read().split(), reverse=True)))"
            }
        ]
    }
]
