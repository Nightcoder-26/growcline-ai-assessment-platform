"""
Curated Problems: Two Pointers, Sliding Window, and Stacks
Contains original problem statements, dual solutions, input generators, and mutation checks.
"""

POINTERS_AND_WINDOWS_PROBLEMS = [
    # ── 1. Two Sum in Sorted Array ───────────────────────────────────────────
    {
        "title": "Two Sum in Sorted Array",
        "statement": "Given a 1-indexed sorted integer array numbers and an integer target, find two numbers such that they add up to target. Print their 1-based indices space-separated.",
        "inputFormat": "Line 1: space-separated sorted integers.\\nLine 2: single integer target.",
        "outputFormat": "Two space-separated 1-based indices.",
        "constraints": "2 <= numbers.length <= 10^5\\nnumbers is sorted in non-decreasing order.\\nExact one solution exists.",
        "topic": "Two Pointers",
        "category": "Two Pointers",
        "difficulty": "Easy",
        "tags": ["two-pointers", "binary-search"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2 7 11 15\\n9", "output": "1 2"},
            {"input": "2 3 4\\n6", "output": "1 3"},
        ],
        "hiddenTestCases": [
            {"input": "-1 0\\n-1", "output": "1 2"},
            {"input": "1 2 3 4 4 9\\n8", "output": "4 5"},
            {"input": "-10 -5 0 3 7\\n-2", "output": "2 4"},
            {"input": "5 25 75\\n100", "output": "2 3"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    l, r = 0, len(nums) - 1
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            print(f"{l+1} {r+1}")
            return
        elif s < target:
            l += 1
        else:
            r -= 1
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                print(f"{i+1} {j+1}")
                return
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = sorted(random.sample(range(-50, 100), 10))
    t = nums[2] + nums[7]
    return f"{' '.join(map(str, nums))}\\n{t}"
""",
        "edgeCases": ["1 2\\n3", "-5 5\\n0", "0 0\\n0"],
        "mutations": [
            {
                "name": "zero_based",
                "type": "wrong_answer",
                "code": "import sys\nprint('0 1')"
            }
        ]
    },

    # ── 2. Container With Most Water ─────────────────────────────────────────
    {
        "title": "Container With Most Water",
        "statement": "Given n non-negative integers representing heights of vertical lines, find two lines that together with the x-axis form a container that holds the most water. Output the maximum water volume.",
        "inputFormat": "A single line containing space-separated non-negative integers.",
        "outputFormat": "A single integer representing the maximum water container capacity.",
        "constraints": "2 <= n <= 10^5\\n0 <= height[i] <= 10^4",
        "topic": "Two Pointers",
        "category": "Two Pointers",
        "difficulty": "Medium",
        "tags": ["two-pointers", "greedy"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 8 6 2 5 4 8 3 7", "output": "49"},
            {"input": "1 1", "output": "1"},
        ],
        "hiddenTestCases": [
            {"input": "4 3 2 1 4", "output": "16"},
            {"input": "1 2 1", "output": "2"},
            {"input": "2 3 4 5 18 17 6", "output": "17"},
            {"input": "0 2", "output": "0"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    h = [int(x) for x in raw]
    l, r = 0, len(h) - 1
    max_area = 0
    while l < r:
        area = min(h[l], h[r]) * (r - l)
        if area > max_area: max_area = area
        if h[l] < h[r]:
            l += 1
        else:
            r -= 1
    print(max_area)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    h = [int(x) for x in raw]
    n = len(h)
    ans = 0
    for i in range(n):
        for j in range(i + 1, n):
            ans = max(ans, min(h[i], h[j]) * (j - i))
    print(ans)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(1, 50)) for _ in range(12))
""",
        "edgeCases": ["5 5", "1 100 1", "0 0 0 0"],
        "mutations": [
            {
                "name": "fixed_ends",
                "type": "wrong_answer",
                "code": "import sys\nh = [int(x) for x in sys.stdin.read().split()]\nprint(min(h[0], h[-1]) * (len(h) - 1))"
            }
        ]
    },

    # ── 3. Trapping Rain Water ───────────────────────────────────────────────
    {
        "title": "Trapping Rain Water",
        "statement": "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
        "inputFormat": "A single line containing space-separated integers representing the elevation heights.",
        "outputFormat": "A single integer denoting the total units of trapped rain water.",
        "constraints": "1 <= n <= 10^5\\n0 <= height[i] <= 10^5",
        "topic": "Two Pointers",
        "category": "Two Pointers",
        "difficulty": "Hard",
        "tags": ["two-pointers", "stack", "dynamic-programming"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "0 1 0 2 1 0 1 3 2 1 2 1", "output": "6"},
            {"input": "4 2 0 3 2 5", "output": "9"},
        ],
        "hiddenTestCases": [
            {"input": "3 0 0 2 0 4", "output": "10"},
            {"input": "1 2 3 4 5", "output": "0"},
            {"input": "5 4 3 2 1", "output": "0"},
            {"input": "2 0 2", "output": "2"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print(0)
        return
    h = [int(x) for x in raw]
    l, r = 0, len(h) - 1
    left_max, right_max = 0, 0
    water = 0
    while l < r:
        if h[l] < h[r]:
            if h[l] >= left_max:
                left_max = h[l]
            else:
                water += left_max - h[l]
            l += 1
        else:
            if h[r] >= right_max:
                right_max = h[r]
            else:
                water += right_max - h[r]
            r -= 1
    print(water)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print(0)
        return
    h = [int(x) for x in raw]
    n = len(h)
    water = 0
    for i in range(n):
        l_max = max(h[:i+1])
        r_max = max(h[i:])
        water += min(l_max, r_max) - h[i]
    print(water)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(0, 10)) for _ in range(15))
""",
        "edgeCases": ["0", "5", "0 0 0", "1 0 1"],
        "mutations": [
            {
                "name": "always_zero",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    },

    # ── 4. Longest Substring Without Repeating Characters ────────────────────
    {
        "title": "Longest Substring Without Repeating Characters",
        "statement": "Given a string s, find the length of the longest substring without repeating characters.",
        "inputFormat": "A single line containing string s (may contain spaces).",
        "outputFormat": "A single integer denoting the length of the longest unique character substring.",
        "constraints": "0 <= s.length <= 10^5",
        "topic": "Sliding Window",
        "category": "Sliding Window",
        "difficulty": "Medium",
        "tags": ["sliding-window", "hashing", "strings"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "abcabcbb", "output": "3"},
            {"input": "bbbbb", "output": "1"},
        ],
        "hiddenTestCases": [
            {"input": "pwwkew", "output": "3"},
            {"input": "", "output": "0"},
            {"input": "au", "output": "2"},
            {"input": "dvdf", "output": "3"},
        ],
        "referenceSolution": """import sys
def solve():
    s = sys.stdin.read().rstrip('\\r\\n')
    char_map = {}
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in char_map and char_map[ch] >= left:
            left = char_map[ch] + 1
        char_map[ch] = right
        if (right - left + 1) > max_len:
            max_len = right - left + 1
    print(max_len)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    s = sys.stdin.read().rstrip('\\r\\n')
    n = len(s)
    ans = 0
    for i in range(n):
        seen = set()
        for j in range(i, n):
            if s[j] in seen: break
            seen.add(s[j])
            ans = max(ans, j - i + 1)
    print(ans)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ''.join(random.choices('abcdefgh', k=20))
""",
        "edgeCases": ["", "a", "abcdef", "abba"],
        "mutations": [
            {
                "name": "set_length",
                "type": "wrong_answer",
                "code": "import sys\nprint(len(set(sys.stdin.read().strip())))"
            }
        ]
    },

    # ── 5. Minimum Size Subarray Sum ─────────────────────────────────────────
    {
        "title": "Minimum Size Subarray Sum",
        "statement": "Given an array of positive integers nums and a positive integer target, return the minimal length of a contiguous subarray whose sum is greater than or equal to target. If no such subarray exists, return 0.",
        "inputFormat": "Line 1: space-separated positive integers.\\nLine 2: single integer target.",
        "outputFormat": "A single integer denoting the minimum subarray length, or 0.",
        "constraints": "1 <= target <= 10^9\\n1 <= nums.length <= 10^5\\n1 <= nums[i] <= 10^4",
        "topic": "Sliding Window",
        "category": "Sliding Window",
        "difficulty": "Medium",
        "tags": ["sliding-window", "binary-search"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "2 3 1 2 4 3\\n7", "output": "2"},
            {"input": "1 4 4\\n4", "output": "1"},
        ],
        "hiddenTestCases": [
            {"input": "1 1 1 1 1 1 1 1\\n11", "output": "0"},
            {"input": "5 1 3 5 10 7 4 9 2 8\\n15", "output": "2"},
            {"input": "1 2 3 4 5\\n15", "output": "5"},
            {"input": "10\\n10", "output": "1"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    l = 0
    curr_sum = 0
    min_len = float('inf')
    for r in range(len(nums)):
        curr_sum += nums[r]
        while curr_sum >= target:
            if (r - l + 1) < min_len:
                min_len = r - l + 1
            curr_sum -= nums[l]
            l += 1
    print(min_len if min_len != float('inf') else 0)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    n = len(nums)
    ans = float('inf')
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s >= target:
                ans = min(ans, j - i + 1)
                break
    print(ans if ans != float('inf') else 0)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = [random.randint(1, 10) for _ in range(10)]
    t = random.randint(10, 30)
    return f"{' '.join(map(str, nums))}\\n{t}"
""",
        "edgeCases": ["1\\n2", "5\\n5", "1 2 3\\n100"],
        "mutations": [
            {
                "name": "return_one",
                "type": "wrong_answer",
                "code": "print(1)"
            }
        ]
    },

    # ── 6. Balanced Parentheses Validator ────────────────────────────────────
    {
        "title": "Balanced Parentheses Validator",
        "statement": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. Open brackets must be closed by the same type of brackets in the correct order. Output 'true' or 'false'.",
        "inputFormat": "A single line containing the bracket string.",
        "outputFormat": "true or false",
        "constraints": "1 <= s.length <= 10^5",
        "topic": "Stacks",
        "category": "Stacks",
        "difficulty": "Easy",
        "tags": ["stacks", "strings"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "()[]{}", "output": "true"},
            {"input": "(]", "output": "false"},
        ],
        "hiddenTestCases": [
            {"input": "([])", "output": "true"},
            {"input": "([)]", "output": "false"},
            {"input": "{[]}", "output": "true"},
            {"input": "(((", "output": "false"},
        ],
        "referenceSolution": """import sys
def solve():
    s = sys.stdin.read().strip()
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in mapping:
            top = stack.pop() if stack else '#'
            if mapping[ch] != top:
                print('false')
                return
        else:
            stack.append(ch)
    print('true' if not stack else 'false')
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    s = sys.stdin.read().strip()
    while '()' in s or '[]' in s or '{}' in s:
        s = s.replace('()', '').replace('[]', '').replace('{}', '')
    print('true' if len(s) == 0 else 'false')
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    pairs = ['()', '[]', '{}']
    s = ''
    for _ in range(5):
        p = random.choice(pairs)
        s = p[0] + s + p[1]
    return s
""",
        "edgeCases": ["[", "]", "()", "{{{{}}}}"],
        "mutations": [
            {
                "name": "check_length_only",
                "type": "wrong_answer",
                "code": "import sys\nprint('true' if len(sys.stdin.read().strip()) % 2 == 0 else 'false')"
            }
        ]
    },

    # ── 7. Daily Temperatures Warmer Days ────────────────────────────────────
    {
        "title": "Daily Temperatures Warmer Days",
        "statement": "Given an array of integers temperatures representing daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the i-th day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0.",
        "inputFormat": "A single line containing space-separated integers.",
        "outputFormat": "A single line of space-separated integers representing days to wait.",
        "constraints": "1 <= temperatures.length <= 10^5\\n30 <= temperatures[i] <= 100",
        "topic": "Stacks",
        "category": "Stacks",
        "difficulty": "Medium",
        "tags": ["stacks", "monotonic-stack"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "73 74 75 71 69 72 76 73", "output": "1 1 4 2 1 1 0 0"},
            {"input": "30 40 50 60", "output": "1 1 1 0"},
        ],
        "hiddenTestCases": [
            {"input": "30 60 90", "output": "1 1 0"},
            {"input": "80 70 60 50", "output": "0 0 0 0"},
            {"input": "50", "output": "0"},
            {"input": "50 50 50 51", "output": "3 2 1 0"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    t = [int(x) for x in raw]
    n = len(t)
    res = [0] * n
    stack = []
    for i in range(n):
        while stack and t[i] > t[stack[-1]]:
            prev = stack.pop()
            res[prev] = i - prev
        stack.append(i)
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    t = [int(x) for x in raw]
    n = len(t)
    res = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if t[j] > t[i]:
                res[i] = j - i
                break
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(40, 85)) for _ in range(10))
""",
        "edgeCases": ["70", "70 70", "30 90 30"],
        "mutations": [
            {
                "name": "all_zeros",
                "type": "wrong_answer",
                "code": "import sys\nprint(' '.join(['0'] * len(sys.stdin.read().split())))"
            }
        ]
    }
]
