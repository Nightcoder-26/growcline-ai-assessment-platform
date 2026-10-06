"""
Curated Problems: Arrays, Strings, and Hashing
Contains original problem statements, sample & hidden test cases,
reference solutions, brute force solutions, input generators, edge cases, and mutations.
"""

ARRAYS_AND_STRINGS_PROBLEMS = [
    # ── 1. Maximum Contiguous Subarray Sum (Kadane's) ─────────────────────────
    {
        "title": "Maximum Contiguous Subarray Sum",
        "statement": "Given an integer array, determine the maximum possible sum of any contiguous, non-empty subarray.",
        "inputFormat": "A single line containing space-separated integers.",
        "outputFormat": "A single integer denoting the maximum contiguous subarray sum.",
        "constraints": "1 <= N <= 10^5\n-10^4 <= A[i] <= 10^4",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Easy",
        "tags": ["arrays", "kadane", "dynamic-programming"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "-2 1 -3 4 -1 2 1 -5 4", "output": "6"},
            {"input": "1", "output": "1"},
        ],
        "hiddenTestCases": [
            {"input": "5 4 -1 7 8", "output": "23"},
            {"input": "-5 -2 -8 -1 -9", "output": "-1"},
            {"input": "-10 0 10", "output": "10"},
            {"input": "100 -200 300 -100 400", "output": "600"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        return
    nums = [int(x) for x in raw]
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    print(max_so_far)
if __name__ == '__main__':
    solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    n = len(nums)
    best = -float('inf')
    for i in range(n):
        s = 0
        for j in range(i, min(n, i + 500)):
            s += nums[j]
            if s > best: best = s
    print(best)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    n = random.randint(10, 50)
    return ' '.join(str(random.randint(-100, 100)) for _ in range(n))
""",
        "edgeCases": ["-1", "0", "-5 -5 -5", "10000"],
        "mutations": [
            {
                "name": "off_by_one",
                "type": "wrong_answer",
                "code": "import sys\nnums = [int(x) for x in sys.stdin.read().split()]\nprint(max(nums[1:]) if len(nums) > 1 else nums[0])"
            },
            {
                "name": "always_zero",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    },

    # ── 2. Majority Element Finder ───────────────────────────────────────────
    {
        "title": "Majority Element Finder",
        "statement": "Given an array of size n, identify the element that appears strictly more than floor(n / 2) times. You may assume that the majority element always exists.",
        "inputFormat": "A single line of space-separated integers.",
        "outputFormat": "A single integer representing the majority element.",
        "constraints": "1 <= n <= 10^5\n-10^9 <= A[i] <= 10^9",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Easy",
        "tags": ["arrays", "voting-algorithm", "hashing"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "3 2 3", "output": "3"},
            {"input": "2 2 1 1 1 2 2", "output": "2"},
        ],
        "hiddenTestCases": [
            {"input": "7", "output": "7"},
            {"input": "1 1 1 1 2 3 1", "output": "1"},
            {"input": "9 9 9 1 2 9 9", "output": "9"},
            {"input": "-1 -1 -1 2 -1", "output": "-1"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    cand = None
    count = 0
    for x in nums:
        if count == 0:
            cand = x
            count = 1
        elif x == cand:
            count += 1
        else:
            count -= 1
    print(cand)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
from collections import Counter
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    c = Counter(nums)
    n = len(nums)
    for k, v in c.items():
        if v > n // 2:
            print(k)
            return
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    maj = random.randint(1, 100)
    other = [random.randint(1, 100) for _ in range(10)]
    arr = [maj] * 12 + other
    random.shuffle(arr)
    return ' '.join(map(str, arr))
""",
        "edgeCases": ["42", "1 1 2", "-5 -5 0 -5"],
        "mutations": [
            {
                "name": "return_first",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().split()[0])"
            }
        ]
    },

    # ── 3. Product of Array Except Self ──────────────────────────────────────
    {
        "title": "Product of Array Except Self",
        "statement": "Given an array of integers nums, return an array output such that output[i] is equal to the product of all elements of nums except nums[i]. Do not use the division operation.",
        "inputFormat": "A single line containing space-separated integers.",
        "outputFormat": "A single line of space-separated integers representing the prefix-suffix products.",
        "constraints": "2 <= nums.length <= 10^5\n-30 <= nums[i] <= 30",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Medium",
        "tags": ["arrays", "prefix-sum"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 4", "output": "24 12 8 6"},
            {"input": "-1 1 0 -3 3", "output": "0 0 9 0 0"},
        ],
        "hiddenTestCases": [
            {"input": "2 3", "output": "3 2"},
            {"input": "0 0", "output": "0 0"},
            {"input": "1 -1 1 -1", "output": "-1 1 -1 1"},
            {"input": "2 2 2 2", "output": "8 8 8 8"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    n = len(nums)
    res = [1] * n
    prefix = 1
    for i in range(n):
        res[i] = prefix
        prefix *= nums[i]
    postfix = 1
    for i in range(n - 1, -1, -1):
        res[i] *= postfix
        postfix *= nums[i]
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    n = len(nums)
    res = []
    for i in range(n):
        prod = 1
        for j in range(n):
            if i != j: prod *= nums[j]
        res.append(prod)
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    n = random.randint(3, 8)
    return ' '.join(str(random.randint(-5, 5)) for _ in range(n))
""",
        "edgeCases": ["5 10", "0 5 2", "-1 -2 -3"],
        "mutations": [
            {
                "name": "include_self",
                "type": "wrong_answer",
                "code": "import sys\nnums = [int(x) for x in sys.stdin.read().split()]\np = 1\nfor x in nums: p *= x\nprint(' '.join(str(p) for _ in nums))"
            }
        ]
    },

    # ── 4. Rotate Array Right by K Steps ─────────────────────────────────────
    {
        "title": "Rotate Array Right by K Steps",
        "statement": "Given an integer array nums and an integer k, rotate the array to the right by k steps, where k is non-negative.",
        "inputFormat": "Line 1: space-separated array integers.\nLine 2: single integer k.",
        "outputFormat": "Single line of space-separated integers after rotation.",
        "constraints": "1 <= nums.length <= 10^5\n0 <= k <= 10^5",
        "topic": "Arrays",
        "category": "Arrays",
        "difficulty": "Medium",
        "tags": ["arrays", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 4 5 6 7\n3", "output": "5 6 7 1 2 3 4"},
            {"input": "-1 -100 3 99\n2", "output": "3 99 -1 -100"},
        ],
        "hiddenTestCases": [
            {"input": "1 2\n3", "output": "2 1"},
            {"input": "10\n5", "output": "10"},
            {"input": "1 2 3\n0", "output": "1 2 3"},
            {"input": "4 5 6 7\n4", "output": "4 5 6 7"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if not lines or not lines[0].strip(): return
    nums = [int(x) for x in lines[0].split()]
    k = int(lines[1].strip()) if len(lines) > 1 else 0
    n = len(nums)
    if n == 0: return
    k %= n
    rotated = nums[n - k:] + nums[:n - k]
    print(' '.join(map(str, rotated)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = [int(x) for x in lines[0].split()]
    k = int(lines[1]) % len(nums)
    for _ in range(k):
        nums = [nums[-1]] + nums[:-1]
    print(' '.join(map(str, nums)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    n = random.randint(4, 10)
    arr = ' '.join(str(random.randint(1, 50)) for _ in range(n))
    k = random.randint(1, 20)
    return f"{arr}\\n{k}"
""",
        "edgeCases": ["1\\n10", "1 2\\n0", "1 2 3 4\\n8"],
        "mutations": [
            {
                "name": "no_modulo",
                "type": "wrong_answer",
                "code": "print(' '.join(reversed(sys.stdin.read().split()[0].split())))"
            }
        ]
    },

    # ── 5. String Anagram Grouping ───────────────────────────────────────────
    {
        "title": "String Anagram Grouping",
        "statement": "Given an array of strings, group the anagrams together. For deterministic output, output each group sorted alphabetically on a separate line, and sort the groups themselves by their first element.",
        "inputFormat": "A single line of space-separated lowercase words.",
        "outputFormat": "Each grouped set of anagrams printed on a new line with space-separated words.",
        "constraints": "1 <= words.length <= 10^4\n0 <= words[i].length <= 100",
        "topic": "Strings",
        "category": "Strings",
        "difficulty": "Medium",
        "tags": ["strings", "hashing"],
        "checker": "unordered_lines",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "eat tea tan ate nat bat", "output": "bat\nate eat tea\nnat tan"},
            {"input": "a", "output": "a"},
        ],
        "hiddenTestCases": [
            {"input": "ab ba abc cba bca", "output": "ab ba\nabc bca cba"},
            {"input": "listen silent enlist google", "output": "google\nenlist listen silent"},
            {"input": "cat dog bird", "output": "bird\ncat\ndog"},
        ],
        "referenceSolution": """import sys
from collections import defaultdict
def solve():
    words = sys.stdin.read().split()
    groups = defaultdict(list)
    for w in words:
        key = ''.join(sorted(w))
        groups[key].append(w)
    lines = []
    for g in groups.values():
        lines.append(' '.join(sorted(g)))
    lines.sort()
    for l in lines:
        print(l)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
from collections import defaultdict
def solve():
    words = sys.stdin.read().split()
    groups = defaultdict(list)
    for w in words:
        key = ''.join(sorted(w))
        groups[key].append(w)
    lines = [ ' '.join(sorted(g)) for g in groups.values() ]
    lines.sort()
    for l in lines: print(l)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    bases = ['stop', 'pots', 'tops', 'post', 'spot', 'act', 'cat', 'tac', 'dog', 'god']
    return ' '.join(random.sample(bases, 6))
""",
        "edgeCases": ["word", "a b c d", "aa aa aa"],
        "mutations": [
            {
                "name": "no_grouping",
                "type": "wrong_answer",
                "code": "import sys\nfor w in sys.stdin.read().split(): print(w)"
            }
        ]
    },

    # ── 6. Longest Common Prefix ─────────────────────────────────────────────
    {
        "title": "Longest Common Prefix",
        "statement": "Write a function to find the longest common prefix string amongst an array of strings. If there is no common prefix, return an empty line.",
        "inputFormat": "A single line containing space-separated words.",
        "outputFormat": "The longest common prefix string, or an empty line if none exists.",
        "constraints": "1 <= words.length <= 200\n0 <= words[i].length <= 200",
        "topic": "Strings",
        "category": "Strings",
        "difficulty": "Easy",
        "tags": ["strings", "trie"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "flower flow flight", "output": "fl"},
            {"input": "dog racecar car", "output": ""},
        ],
        "hiddenTestCases": [
            {"input": "interspecies interstellar interstate", "output": "inters"},
            {"input": "throne throne", "output": "throne"},
            {"input": "prefix", "output": "prefix"},
            {"input": "a b c", "output": ""},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print("")
        return
    prefix = raw[0]
    for w in raw[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                break
    print(prefix)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print('')
        return
    res = []
    for chars in zip(*raw):
        if len(set(chars)) == 1:
            res.append(chars[0])
        else:
            break
    print(''.join(res))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    p = 'test'
    return f"{p}alpha {p}beta {p}gamma"
""",
        "edgeCases": ["lone", "a b", "same same same"],
        "mutations": [
            {
                "name": "take_whole_word",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().split()[0])"
            }
        ]
    },

    # ── 7. Longest Consecutive Sequence ──────────────────────────────────────
    {
        "title": "Longest Consecutive Sequence",
        "statement": "Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence. The algorithm must run in O(n) time complexity.",
        "inputFormat": "A single line containing space-separated integers.",
        "outputFormat": "A single integer denoting the length of the longest consecutive sequence.",
        "constraints": "0 <= nums.length <= 10^5\n-10^9 <= nums[i] <= 10^9",
        "topic": "Hashing",
        "category": "Hashing",
        "difficulty": "Medium",
        "tags": ["hashing", "arrays", "union-find"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "100 4 200 1 3 2", "output": "4"},
            {"input": "0 3 7 2 5 8 4 6 0 1", "output": "9"},
        ],
        "hiddenTestCases": [
            {"input": "", "output": "0"},
            {"input": "10", "output": "1"},
            {"input": "1 2 0 1", "output": "3"},
            {"input": "9 1 4 7 3 -1 0 5 8 -1 6", "output": "7"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print(0)
        return
    nums = set(int(x) for x in raw)
    longest = 0
    for x in nums:
        if x - 1 not in nums:
            curr = x
            streak = 1
            while curr + 1 in nums:
                curr += 1
                streak += 1
            if streak > longest:
                longest = streak
    print(longest)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print(0)
        return
    nums = sorted(set(int(x) for x in raw))
    longest = 1
    curr = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            curr += 1
            longest = max(longest, curr)
        else:
            curr = 1
    print(longest)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    base = list(range(10, 20)) + [100, 200, 300]
    random.shuffle(base)
    return ' '.join(map(str, base))
""",
        "edgeCases": ["", "5", "1 1 1 1", "-3 -2 -1 0 1"],
        "mutations": [
            {
                "name": "sort_length",
                "type": "wrong_answer",
                "code": "print(len(sys.stdin.read().split()))"
            }
        ]
    },

    # ── 8. First Non-Repeating Character ─────────────────────────────────────
    {
        "title": "First Non-Repeating Character",
        "statement": "Given a string s, find the first non-repeating character in it and print its 0-based index. If no such character exists, print -1.",
        "inputFormat": "A single line containing the string s.",
        "outputFormat": "A single integer denoting the index of the first unique character, or -1.",
        "constraints": "1 <= s.length <= 10^5\ns consists of only lowercase English letters.",
        "topic": "Hashing",
        "category": "Hashing",
        "difficulty": "Easy",
        "tags": ["hashing", "strings"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "leetcode", "output": "0"},
            {"input": "loveleetcode", "output": "2"},
        ],
        "hiddenTestCases": [
            {"input": "aabb", "output": "-1"},
            {"input": "z", "output": "0"},
            {"input": "swiss", "output": "1"},
            {"input": "abacabad", "output": "7"},
        ],
        "referenceSolution": """import sys
from collections import Counter
def solve():
    s = sys.stdin.read().strip()
    if not s:
        print(-1)
        return
    c = Counter(s)
    for i, ch in enumerate(s):
        if c[ch] == 1:
            print(i)
            return
    print(-1)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    s = sys.stdin.read().strip()
    for i in range(len(s)):
        if s.count(s[i]) == 1:
            print(i)
            return
    print(-1)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ''.join(random.choices('abcdef', k=15)) + 'z'
""",
        "edgeCases": ["a", "aa", "abc", "aba"],
        "mutations": [
            {
                "name": "always_first",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    }
]
