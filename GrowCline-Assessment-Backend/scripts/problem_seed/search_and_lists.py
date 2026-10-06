"""
Curated Problems: Binary Search and Linked-List-Style (stdin/stdout)
Contains original problem statements, dual solutions, input generators, and mutation checks.
"""

SEARCH_AND_LISTS_PROBLEMS = [
    # ── 1. Classic Binary Search ─────────────────────────────────────────────
    {
        "title": "Classic Binary Search",
        "statement": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its 0-based index. Otherwise, return -1.",
        "inputFormat": "Line 1: space-separated sorted integers.\\nLine 2: single integer target.",
        "outputFormat": "A single integer denoting the index of target, or -1.",
        "constraints": "1 <= nums.length <= 10^5\\n-10^4 <= nums[i], target <= 10^4\\nAll integers in nums are unique.",
        "topic": "Binary Search",
        "category": "Binary Search",
        "difficulty": "Easy",
        "tags": ["binary-search", "arrays"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "-1 0 3 5 9 12\\n9", "output": "4"},
            {"input": "-1 0 3 5 9 12\\n2", "output": "-1"},
        ],
        "hiddenTestCases": [
            {"input": "5\\n5", "output": "0"},
            {"input": "1 3 5 7 9\\n1", "output": "0"},
            {"input": "1 3 5 7 9\\n9", "output": "4"},
            {"input": "2 4 6 8 10\\n7", "output": "-1"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] == target:
            print(m)
            return
        elif nums[m] < target:
            l = m + 1
        else:
            r = m - 1
    print(-1)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    for i, x in enumerate(nums):
        if x == target:
            print(i)
            return
    print(-1)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = sorted(random.sample(range(-100, 100), 12))
    target = random.choice(nums) if random.random() > 0.3 else 999
    return f"{' '.join(map(str, nums))}\\n{target}"
""",
        "edgeCases": ["10\\n10", "10\\n5", "-5 0 5\\n0"],
        "mutations": [
            {
                "name": "always_first",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    },

    # ── 2. Search in Rotated Sorted Array ─────────────────────────────────────
    {
        "title": "Search in Rotated Sorted Array",
        "statement": "There is an integer array nums sorted in ascending order with distinct values. Given the array nums possibly rotated at an unknown pivot index and a target value, return the 0-based index of target, or -1 if it is not in nums.",
        "inputFormat": "Line 1: space-separated integers representing the rotated array.\\nLine 2: single integer target.",
        "outputFormat": "A single integer denoting the index of target, or -1.",
        "constraints": "1 <= nums.length <= 10^5\\nAll values of nums are unique.\\nnums is guaranteed to be rotated at some pivot.",
        "topic": "Binary Search",
        "category": "Binary Search",
        "difficulty": "Medium",
        "tags": ["binary-search", "arrays"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "4 5 6 7 0 1 2\\n0", "output": "4"},
            {"input": "4 5 6 7 0 1 2\\n3", "output": "-1"},
        ],
        "hiddenTestCases": [
            {"input": "1\\n0", "output": "-1"},
            {"input": "3 1\\n1", "output": "1"},
            {"input": "5 1 3\\n5", "output": "0"},
            {"input": "6 7 1 2 3 4 5\\n3", "output": "4"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    l, r = 0, len(nums) - 1
    while l <= r:
        m = (l + r) // 2
        if nums[m] == target:
            print(m)
            return
        # Left half sorted
        if nums[l] <= nums[m]:
            if nums[l] <= target < nums[m]:
                r = m - 1
            else:
                l = m + 1
        else: # Right half sorted
            if nums[m] < target <= nums[r]:
                l = m + 1
            else:
                r = m - 1
    print(-1)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = [int(x) for x in lines[0].split()]
    target = int(lines[1].strip())
    for i, x in enumerate(nums):
        if x == target:
            print(i)
            return
    print(-1)
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = sorted(random.sample(range(1, 100), 10))
    k = random.randint(1, 8)
    rotated = nums[k:] + nums[:k]
    t = random.choice(rotated)
    return f"{' '.join(map(str, rotated))}\\n{t}"
""",
        "edgeCases": ["1\\n1", "2 1\\n2", "1 2 3\\n4"],
        "mutations": [
            {
                "name": "linear_first_only",
                "type": "wrong_answer",
                "code": "print(0)"
            }
        ]
    },

    # ── 3. Find Peak Element ─────────────────────────────────────────────────
    {
        "title": "Find Peak Element",
        "statement": "A peak element is an element that is strictly greater than its neighbors. Given a 0-indexed integer array nums, find a peak element, and return its index. You may imagine nums[-1] = nums[n] = -inf.",
        "inputFormat": "A single line containing space-separated integers.",
        "outputFormat": "A single integer denoting the index of any valid peak element.",
        "constraints": "1 <= nums.length <= 10^5\\nnums[i] != nums[i + 1] for all valid i.",
        "topic": "Binary Search",
        "category": "Binary Search",
        "difficulty": "Medium",
        "tags": ["binary-search", "arrays"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 1", "output": "2"},
            {"input": "1 2 1 3 5 6 4", "output": "5"},
        ],
        "hiddenTestCases": [
            {"input": "1", "output": "0"},
            {"input": "1 2", "output": "1"},
            {"input": "2 1", "output": "0"},
            {"input": "1 3 20 4 1 0", "output": "2"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw: return
    nums = [int(x) for x in raw]
    l, r = 0, len(nums) - 1
    while l < r:
        m = (l + r) // 2
        if nums[m] > nums[m + 1]:
            r = m
        else:
            l = m + 1
    print(l)
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    nums = [int(x) for x in raw]
    n = len(nums)
    if n == 1:
        print(0)
        return
    for i in range(n):
        left_ok = (i == 0 or nums[i] > nums[i - 1])
        right_ok = (i == n - 1 or nums[i] > nums[i + 1])
        if left_ok and right_ok:
            print(i)
            return
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = [1, 5, 2, 8, 4, 10, 3]
    return ' '.join(map(str, nums))
""",
        "edgeCases": ["5", "1 5", "5 1", "1 2 3 4 5"],
        "mutations": [
            {
                "name": "max_index",
                "type": "wrong_answer",
                "code": "import sys\nnums = [int(x) for x in sys.stdin.read().split()]\nprint(nums.index(max(nums)))"
            }
        ]
    },

    # ── 4. Reverse Linked Sequence ───────────────────────────────────────────
    {
        "title": "Reverse Linked Sequence",
        "statement": "Given the values of a singly linked list as space-separated integers, reverse the list and output the reversed values space-separated.",
        "inputFormat": "A single line of space-separated integers.",
        "outputFormat": "A single line of space-separated integers in reverse order.",
        "constraints": "0 <= number of nodes <= 5000\\n-5000 <= Node.val <= 5000",
        "topic": "Linked Lists",
        "category": "Linked Lists",
        "difficulty": "Easy",
        "tags": ["linked-lists", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 4 5", "output": "5 4 3 2 1"},
            {"input": "1 2", "output": "2 1"},
        ],
        "hiddenTestCases": [
            {"input": "", "output": ""},
            {"input": "42", "output": "42"},
            {"input": "10 20 30", "output": "30 20 10"},
            {"input": "-1 -2 -3", "output": "-3 -2 -1"},
        ],
        "referenceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print("")
        return
    print(' '.join(reversed(raw)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    raw = sys.stdin.read().split()
    if not raw:
        print('')
        return
    res = []
    for x in raw:
        res.insert(0, x)
    print(' '.join(res))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    return ' '.join(str(random.randint(1, 100)) for _ in range(8))
""",
        "edgeCases": ["", "1", "1 2", "1 1 1"],
        "mutations": [
            {
                "name": "no_reversal",
                "type": "wrong_answer",
                "code": "import sys\nprint(' '.join(sys.stdin.read().split()))"
            }
        ]
    },

    # ── 5. Merge Two Sorted Sequences ────────────────────────────────────────
    {
        "title": "Merge Two Sorted Sequences",
        "statement": "Given two sorted sequences of integers representing two sorted linked lists, merge them into a single sorted sequence and print the result.",
        "inputFormat": "Line 1: space-separated sorted integers of list 1.\\nLine 2: space-separated sorted integers of list 2.",
        "outputFormat": "A single line containing the merged sorted integers.",
        "constraints": "0 <= list1.length, list2.length <= 50\\n-100 <= Node.val <= 100",
        "topic": "Linked Lists",
        "category": "Linked Lists",
        "difficulty": "Easy",
        "tags": ["linked-lists", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 4\\n1 3 4", "output": "1 1 2 3 4 4"},
            {"input": "\\n0", "output": "0"},
        ],
        "hiddenTestCases": [
            {"input": "\\n", "output": ""},
            {"input": "5 10 15\\n2 8 20", "output": "2 5 8 10 15 20"},
            {"input": "-10 -5\\n-8 0 5", "output": "-10 -8 -5 0 5"},
            {"input": "1 3 5\\n2 4 6", "output": "1 2 3 4 5 6"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().split('\\n')
    l1 = [int(x) for x in lines[0].split()] if len(lines) > 0 and lines[0].strip() else []
    l2 = [int(x) for x in lines[1].split()] if len(lines) > 1 and lines[1].strip() else []
    i, j = 0, 0
    res = []
    while i < len(l1) and j < len(l2):
        if l1[i] <= l2[j]:
            res.append(l1[i])
            i += 1
        else:
            res.append(l2[j])
            j += 1
    res.extend(l1[i:])
    res.extend(l2[j:])
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().split('\\n')
    l1 = [int(x) for x in lines[0].split()] if len(lines) > 0 and lines[0].strip() else []
    l2 = [int(x) for x in lines[1].split()] if len(lines) > 1 and lines[1].strip() else []
    res = sorted(l1 + l2)
    print(' '.join(map(str, res)))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    s1 = sorted(random.sample(range(1, 50), 4))
    s2 = sorted(random.sample(range(1, 50), 5))
    return f"{' '.join(map(str, s1))}\\n{' '.join(map(str, s2))}"
""",
        "edgeCases": ["\\n", "1\\n", "\\n1", "1\\n1"],
        "mutations": [
            {
                "name": "first_list_only",
                "type": "wrong_answer",
                "code": "import sys\nprint(sys.stdin.read().split('\\n')[0])"
            }
        ]
    },

    # ── 6. Remove Nth Node From End of Sequence ──────────────────────────────
    {
        "title": "Remove Nth Node From End of Sequence",
        "statement": "Given a sequence representing a linked list and an integer n, remove the n-th node from the end of the list and return the remaining elements space-separated.",
        "inputFormat": "Line 1: space-separated integers.\\nLine 2: single integer n.",
        "outputFormat": "A single line containing the remaining elements after deletion.",
        "constraints": "1 <= sz <= 30\\n0 <= Node.val <= 100\\n1 <= n <= sz",
        "topic": "Linked Lists",
        "category": "Linked Lists",
        "difficulty": "Medium",
        "tags": ["linked-lists", "two-pointers"],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "sampleTestCases": [
            {"input": "1 2 3 4 5\\n2", "output": "1 2 3 5"},
            {"input": "1\\n1", "output": ""},
        ],
        "hiddenTestCases": [
            {"input": "1 2\\n1", "output": "1"},
            {"input": "1 2\\n2", "output": "2"},
            {"input": "10 20 30 40\\n4", "output": "20 30 40"},
            {"input": "5 10 15\\n2", "output": "5 15"},
        ],
        "referenceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    if len(lines) < 2: return
    nums = lines[0].split()
    n = int(lines[1].strip())
    remove_idx = len(nums) - n
    nums.pop(remove_idx)
    print(' '.join(nums))
if __name__ == '__main__': solve()
""",
        "bruteForceSolution": """import sys
def solve():
    lines = sys.stdin.read().strip().split('\\n')
    nums = lines[0].split()
    n = int(lines[1].strip())
    del nums[len(nums) - n]
    print(' '.join(nums))
if __name__ == '__main__': solve()
""",
        "inputGenerator": """def generate(seed: int) -> str:
    import random
    random.seed(seed)
    nums = [str(x) for x in range(1, 7)]
    n = random.randint(1, len(nums))
    return f"{' '.join(nums)}\\n{n}"
""",
        "edgeCases": ["1\\n1", "1 2\\n1", "1 2\\n2"],
        "mutations": [
            {
                "name": "remove_first_always",
                "type": "wrong_answer",
                "code": "import sys\nprint(' '.join(sys.stdin.read().split('\\n')[0].split()[1:]))"
            }
        ]
    }
]
