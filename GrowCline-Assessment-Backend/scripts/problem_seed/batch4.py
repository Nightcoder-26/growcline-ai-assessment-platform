"""Batch 4 – 11 User-Curated Problems."""
from typing import List, Dict, Any

BATCH4_PROBLEMS: List[Dict[str, Any]] = [
  {
    "slug": "duplicate_sensor_alert",
    "title": "Duplicate Sensor Alert",
    "topic": "Arrays & Hashing",
    "difficulty": "Easy",
    "tags": ["array", "hash-set", "frequency"],
    "domains": ["monitoring", "sensors"],
    "statement": "A monitoring system records sensor IDs that triggered an alert during a shift. Return the first sensor ID that appears at least twice. If no sensor ID is repeated, return -1.",
    "inputFormat": "The first line contains an integer N. The second line contains N integers representing sensor IDs in chronological order.",
    "outputFormat": "Print the first sensor ID whose second occurrence appears earliest. If every ID occurs once, print -1.",
    "constraints": "1 <= N <= 200000; 1 <= sensorID <= 10^9",
    "sampleTestCases": [
      {
        "input": "7\n12 5 8 12 5 9 8",
        "output": "12",
        "explanation": "Sensor 12 is the first ID to appear for the second time."
      },
      {
        "input": "5\n3 7 11 20 25",
        "output": "-1",
        "explanation": "No sensor ID is repeated."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Maintain a set of previously seen IDs and stop when an ID is encountered again.",
    "referenceSolution": "Read N and the array. Create an empty hash set. Scan left to right. If the current value is already in the set, print it and terminate. Otherwise insert it. If the scan finishes, print -1.",
    "bruteForceSolution": "For each position i, scan all earlier positions j < i and check whether a[j] equals a[i]. Print the first such a[i], otherwise print -1.",
    "inputGenerator": "Generate N uniformly between 1 and 200000. Generate IDs uniformly between 1 and 1000000000. With probability 0.7, select an earlier position and duplicate its value.",
    "inputValidator": "Parse N and exactly N integers. Verify 1 <= N <= 200000 and every ID is within [1, 1000000000].",
    "edgeCaseInputs": [
      "1\n42",
      "2\n7 7",
      "6\n1 2 3 4 5 1",
      "5\n9 9 9 9 9"
    ],
    "wrongSolutions": [
      {
        "name": "lastDuplicate",
        "description": "Scans the complete array and returns the last duplicated value instead of the value whose second occurrence comes first.",
        "code": "seen=set(); ans=-1\nfor x in a:\n    if x in seen: ans=x\n    seen.add(x)\nprint(ans)"
      },
      {
        "name": "sortThenScan",
        "description": "Sorts the IDs before searching for duplicates, destroying the required chronological order.",
        "code": "a.sort()\nfor i in range(1,n):\n    if a[i]==a[i-1]:\n        print(a[i]); break"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "log_token_frequency",
    "title": "Log Token Frequency",
    "topic": "Arrays & Hashing",
    "difficulty": "Medium",
    "tags": ["hash-map", "frequency", "strings"],
    "domains": ["logging", "observability"],
    "statement": "A log analyzer receives a sequence of lowercase tokens. Find the token with the highest frequency. If multiple tokens have the same maximum frequency, return the one whose first appearance occurs earliest.",
    "inputFormat": "The first line contains N. The second line contains N lowercase alphabetic tokens separated by spaces.",
    "outputFormat": "Print the token with maximum frequency. Break ties by earliest first appearance.",
    "constraints": "1 <= N <= 200000; each token length is 1 to 30; tokens contain only lowercase English letters.",
    "sampleTestCases": [
      {
        "input": "7\nerror info error warn info error warn",
        "output": "error",
        "explanation": "error occurs three times, more than any other token."
      },
      {
        "input": "6\nred blue green blue red green",
        "output": "red",
        "explanation": "All three tokens occur twice, so red wins because it appears first."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Track both frequency and first occurrence position for every token, then choose by descending frequency and ascending first position.",
    "referenceSolution": "Maintain a dictionary mapping each token to its frequency and first index. After processing all tokens, select the token maximizing frequency and, on ties, minimizing first index.",
    "bruteForceSolution": "For each distinct token, count its occurrences by scanning the entire input and record its first index. Choose the token using the required tie-breaking rule.",
    "inputGenerator": "Generate N between 1 and 200000. Create a pool of lowercase tokens with varying lengths and sample tokens from the pool. Include cases where several tokens have equal maximum frequency.",
    "inputValidator": "Verify N and exactly N tokens. Verify each token matches lowercase alphabetic characters and has length between 1 and 30.",
    "edgeCaseInputs": [
      "1\nalpha",
      "4\none two three four",
      "6\na b c a b c",
      "5\nsame same same same same"
    ],
    "wrongSolutions": [
      {
        "name": "lexicographicTie",
        "description": "Breaks equal-frequency ties lexicographically rather than by earliest appearance.",
        "code": "best=max(freq, key=lambda x:(freq[x],x))\nprint(best)"
      },
      {
        "name": "lastAppearanceTie",
        "description": "Uses the latest first occurrence or latest occurrence when resolving ties.",
        "code": "best=max(freq, key=lambda x:(freq[x],last[x]))\nprint(best)"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "nearest_service_pair",
    "title": "Nearest Service Pair",
    "topic": "Two Pointers",
    "difficulty": "Easy",
    "tags": ["two-pointers", "sorting", "closest-sum"],
    "domains": ["service-locations", "planning"],
    "statement": "Two service teams must choose locations whose combined coverage score is as close as possible to a target T without exceeding it. Given sorted coverage scores, return the maximum pair sum that is less than or equal to T. If no valid pair exists, return -1.",
    "inputFormat": "The first line contains N and T. The second line contains N sorted integers.",
    "outputFormat": "Print the largest sum of two distinct elements that does not exceed T, or -1 if no pair is valid.",
    "constraints": "2 <= N <= 200000; 1 <= scores[i] <= 10^9; scores are sorted nondecreasing; 1 <= T <= 2*10^9",
    "sampleTestCases": [
      {
        "input": "6 17\n1 4 6 8 11 14",
        "output": "15",
        "explanation": "The best valid pair is 1 + 14 = 15; no pair sums to 16 or 17."
      },
      {
        "input": "4 5\n3 4 8 10",
        "output": "-1",
        "explanation": "The smallest pair sum is 3 + 4 = 7, which exceeds the target."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Use two pointers at the smallest and largest values. If their sum is too large, move the right pointer down; otherwise record the sum and move the left pointer up.",
    "referenceSolution": "Set left=0 and right=N-1. While left < right, compute a[left]+a[right]. If the sum <= T, update the answer and increment left. Otherwise decrement right. Print the answer.",
    "bruteForceSolution": "Check every pair i < j and retain the largest sum that does not exceed T.",
    "inputGenerator": "Generate N between 2 and 200000, random positive scores, sort them, and choose T either inside or outside the attainable pair-sum range.",
    "inputValidator": "Verify N, T, exactly N scores, sorted order, positive bounds, and distinct pair positions are required.",
    "edgeCaseInputs": [
      "2 10\n3 7",
      "2 5\n3 7",
      "5 100\n10 20 30 40 50",
      "5 6\n1 1 1 1 1"
    ],
    "wrongSolutions": [
      {
        "name": "closestWithoutUpperBound",
        "description": "Finds the numerically closest pair sum even when that sum exceeds T.",
        "code": "best=min((abs(a[i]+a[j]-T),a[i]+a[j]) for i in range(n) for j in range(i+1,n))[1])\nprint(best)"
      },
      {
        "name": "allowSameIndex",
        "description": "Allows the same element to be selected twice.",
        "code": "for x in a:\n    if 2*x<=T: ans=max(ans,2*x)"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "longest_stable_signal",
    "title": "Longest Stable Signal",
    "topic": "Sliding Window",
    "difficulty": "Medium",
    "tags": ["sliding-window", "frequency", "array"],
    "domains": ["telemetry", "signal-analysis"],
    "statement": "A signal is considered stable if the difference between its maximum and minimum reading is at most K. Find the length of the longest contiguous stable segment.",
    "inputFormat": "The first line contains N and K. The second line contains N integer readings.",
    "outputFormat": "Print the maximum length of a contiguous segment whose maximum minus minimum is at most K.",
    "constraints": "1 <= N <= 200000; 0 <= K <= 10^9; -10^9 <= reading <= 10^9",
    "sampleTestCases": [
      {
        "input": "8 3\n2 4 5 3 8 7 6 5",
        "output": "4",
        "explanation": "The segment 8 7 6 5 has range 3 and length 4."
      },
      {
        "input": "5 0\n4 4 2 2 2",
        "output": "3",
        "explanation": "The longest segment containing only equal values is 2 2 2."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Maintain a window using two monotonic deques: one for the maximum and one for the minimum.",
    "referenceSolution": "Expand the right pointer and maintain decreasing and increasing deques of indices. While max-min exceeds K, increment the left pointer and remove expired indices. Track the largest valid window length.",
    "bruteForceSolution": "For every left endpoint, expand the right endpoint while maintaining the current minimum and maximum and update the answer whenever max-min <= K.",
    "inputGenerator": "Generate random readings with both smooth and high-variance sections. Choose K randomly, including K=0 and very large K.",
    "inputValidator": "Verify N, K, and exactly N readings within the stated bounds.",
    "edgeCaseInputs": [
      "1 0\n7",
      "5 0\n3 3 3 3 3",
      "5 1\n1 5 1 5 1",
      "6 1000000000\n-5 10 7 -9 20 3"
    ],
    "wrongSolutions": [
      {
        "name": "averageRange",
        "description": "Uses the average instead of the true maximum and minimum of the window.",
        "code": "if abs(sum(window)/len(window))<=k: ..."
      },
      {
        "name": "recomputeWindow",
        "description": "Uses an incorrect window update and fails to remove values leaving the left side.",
        "code": "while max(a[l:r+1])-min(a[l:r+1])>k: l+=1"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "balanced_bracket_prefix",
    "title": "Balanced Bracket Prefix",
    "topic": "Stack & Queue",
    "difficulty": "Easy",
    "tags": ["stack", "parentheses", "prefix"],
    "domains": ["parsing", "validation"],
    "statement": "Given a string containing only '(' and ')', find the length of the longest prefix that is still a valid bracket prefix: at every position, the number of closing brackets must never exceed the number of opening brackets. The prefix does not need to end with equal counts.",
    "inputFormat": "A single line containing the bracket string.",
    "outputFormat": "Print the length of the longest prefix satisfying the prefix condition.",
    "constraints": "1 <= |S| <= 200000; S contains only '(' and ')'.",
    "sampleTestCases": [
      {
        "input": "(()())())",
        "output": "7",
        "explanation": "The first seven characters never have more ')' than '('; the eighth character violates the condition."
      },
      {
        "input": ")))(((",
        "output": "0",
        "explanation": "The first character is already an invalid closing bracket."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Maintain a running balance, adding one for '(' and subtracting one for ')'. Stop when the balance becomes negative.",
    "referenceSolution": "Initialize balance=0. Scan the string. For '(' increment balance. For ')' decrement balance. If balance becomes negative, print the current index and stop. If it never becomes negative, print the full length.",
    "bruteForceSolution": "For each prefix, count opening and closing brackets and check every intermediate position for a negative balance. Return the first invalid position minus one, or the full length.",
    "inputGenerator": "Generate random parenthesis strings with a mixture of balanced, prefix-invalid, and heavily unbalanced patterns.",
    "inputValidator": "Verify the input contains exactly one nonempty line consisting only of '(' and ')'.",
    "edgeCaseInputs": [
      "(",
      ")",
      "()",
      "(((()",
      "))))"
    ],
    "wrongSolutions": [
      {
        "name": "finalBalanceOnly",
        "description": "Checks only the final balance and misses a prefix that becomes negative before later opening brackets restore it.",
        "code": "print(len(s) if s.count('(')>=s.count(')') else 0)"
      },
      {
        "name": "balancedPrefixOnly",
        "description": "Returns only the longest prefix with balance exactly zero rather than the longest prefix that never becomes negative.",
        "code": "ans=0; bal=0\nfor i,c in enumerate(s):\n    bal += 1 if c=='(' else -1\n    if bal==0: ans=i+1\nprint(ans)"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "next_higher_load",
    "title": "Next Higher Load",
    "topic": "Stack & Queue",
    "difficulty": "Medium",
    "tags": ["monotonic-stack", "next-greater-element"],
    "domains": ["servers", "capacity-planning"],
    "statement": "For every server load in a sequence, find the first later load that is strictly greater. If no later load is greater, output -1 for that position.",
    "inputFormat": "The first line contains N. The second line contains N integer loads.",
    "outputFormat": "Print N integers, where each value is the first strictly greater load to the right or -1.",
    "constraints": "1 <= N <= 200000; 0 <= load <= 10^9",
    "sampleTestCases": [
      {
        "input": "6\n4 7 3 6 5 8",
        "output": "7 8 6 8 8 -1",
        "explanation": "For example, the first load 4 is followed immediately by 7, while 7 waits until 8."
      },
      {
        "input": "5\n9 8 7 6 5",
        "output": "-1 -1 -1 -1 -1",
        "explanation": "No load has a strictly greater value later."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Use a decreasing monotonic stack of indices. When the current value exceeds the value at the stack top, it resolves that earlier position.",
    "referenceSolution": "Initialize answer with -1 and an empty stack. Scan from left to right. While the stack is nonempty and a[current] > a[stack[-1]], assign answer[stack.pop()] = a[current]. Push current index. Print the answer.",
    "bruteForceSolution": "For every index i, scan j from i+1 onward until finding a[j] > a[i].",
    "inputGenerator": "Generate increasing, decreasing, alternating, duplicate-heavy, and random load sequences.",
    "inputValidator": "Verify N and exactly N nonnegative loads, each at most 10^9.",
    "edgeCaseInputs": [
      "1\n5",
      "5\n1 2 3 4 5",
      "5\n5 5 5 5 5",
      "6\n10 1 10 1 10 1"
    ],
    "wrongSolutions": [
      {
        "name": "greaterOrEqual",
        "description": "Treats an equal later value as a valid answer even though the requirement is strictly greater.",
        "code": "while stack and a[i]>=a[stack[-1]]: ..."
      },
      {
        "name": "nearestOnly",
        "description": "Checks only the immediately following load rather than the first later strictly greater load.",
        "code": "ans[i]=a[i+1] if i+1<n and a[i+1]>a[i] else -1"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "minimum_shipping_capacity",
    "title": "Minimum Shipping Capacity",
    "topic": "Binary Search",
    "difficulty": "Medium",
    "tags": ["binary-search", "answer-space", "greedy"],
    "domains": ["logistics", "shipping"],
    "statement": "A warehouse must ship packages in their given order within D days. Each day can contain a contiguous sequence of packages whose total weight does not exceed the truck capacity. Find the minimum capacity that allows all packages to be shipped within D days.",
    "inputFormat": "The first line contains N and D. The second line contains N package weights.",
    "outputFormat": "Print the minimum truck capacity.",
    "constraints": "1 <= N <= 200000; 1 <= D <= N; 1 <= weight[i] <= 10^6",
    "sampleTestCases": [
      {
        "input": "5 3\n3 2 2 4 1",
        "output": "6",
        "explanation": "Capacity 6 can ship [3,2], [2,4], [1] in three days."
      },
      {
        "input": "3 1\n5 2 7",
        "output": "14",
        "explanation": "All packages must be shipped in one day, so capacity must equal their total weight."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Binary-search the capacity between the largest single package and the total weight. Greedily count how many days are required for each candidate capacity.",
    "referenceSolution": "Set low=max(weights), high=sum(weights). For each midpoint capacity, greedily load packages in order and count required days. If days <= D, move high down; otherwise move low up. Print low.",
    "bruteForceSolution": "Try every capacity from max(weights) through sum(weights), simulate the shipping schedule, and return the first capacity requiring at most D days.",
    "inputGenerator": "Generate N and D, then random weights. Include cases with one very large package, D=1, D=N, uniform weights, and highly varied weights.",
    "inputValidator": "Verify N, D, and exactly N positive weights within the specified bounds.",
    "edgeCaseInputs": [
      "1 1\n10",
      "4 4\n5 1 8 3",
      "4 1\n5 1 8 3",
      "6 2\n10 10 10 1 1 1"
    ],
    "wrongSolutions": [
      {
        "name": "averageCapacity",
        "description": "Uses total weight divided by D without respecting package ordering and indivisible package weights.",
        "code": "print((sum(w)+d-1)//d)"
      },
      {
        "name": "lowerBoundZero",
        "description": "Starts binary search below the largest package and can incorrectly accept capacities that cannot contain one package.",
        "code": "lo=0; hi=sum(w)"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "first_sufficient_batch",
    "title": "First Sufficient Batch",
    "topic": "Binary Search",
    "difficulty": "Hard",
    "tags": ["binary-search", "prefix-sum", "optimization"],
    "domains": ["manufacturing", "production"],
    "statement": "A production line has machines arranged in order. Machine i produces p[i] units per hour. For a chosen number k of consecutive machines starting at the first machine, determine the minimum number of hours needed to produce at least T units. Find the smallest k whose required production time is at most H hours.",
    "inputFormat": "The first line contains N, T, and H. The second line contains N positive production rates.",
    "outputFormat": "Print the smallest k for which ceil(T / sum(first k production rates)) <= H. If no such k exists, print -1.",
    "constraints": "1 <= N <= 200000; 1 <= T <= 10^18; 1 <= H <= 10^18; 1 <= p[i] <= 10^9",
    "sampleTestCases": [
      {
        "input": "5 100 5\n5 10 15 20 50",
        "output": "4",
        "explanation": "The first four machines produce 50 units/hour, requiring 2 hours, so actually k=3 already gives 30 units/hour and requires 4 hours; therefore the smallest valid k is 3."
      },
      {
        "input": "3 100 1\n10 20 30",
        "output": "-1",
        "explanation": "Even all three machines produce only 60 units/hour, which is insufficient to reach 100 units in one hour."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "The prefix production rate only increases as k grows, so feasibility is monotonic. Use prefix sums and binary search for the first feasible prefix.",
    "referenceSolution": "Build prefix sums. A prefix with rate S is feasible exactly when ceil(T/S) <= H, equivalently S*H >= T. Binary-search the smallest prefix whose sum multiplied by H reaches T.",
    "bruteForceSolution": "Build the prefix sum from left to right and return the first k for which prefix[k] * H >= T.",
    "inputGenerator": "Generate N up to 200000, production rates up to 10^9, T and H across wide ranges. Include impossible and immediately feasible cases.",
    "inputValidator": "Verify N, T, H and exactly N positive production rates within bounds.",
    "edgeCaseInputs": [
      "1 10 1\n10",
      "1 11 1\n10",
      "5 1 100\n1 1 1 1 1",
      "5 1000000000000 1\n1000000000 1000000000 1000000000 1000000000 1000000000"
    ],
    "wrongSolutions": [
      {
        "name": "strictHours",
        "description": "Uses T / rate <= H with floating-point comparisons and can introduce precision errors for large values.",
        "code": "if T/s <= H: ..."
      },
      {
        "name": "binarySearchFirstRate",
        "description": "Binary-searches production rates instead of the monotonic prefix sums.",
        "code": "lo=0; hi=n-1\n# tests p[mid] rather than prefix[mid+1]"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "xor_checkpoint_signature",
    "title": "XOR Checkpoint Signature",
    "topic": "Math & Bit Manipulation",
    "difficulty": "Easy",
    "tags": ["xor", "bitwise", "prefix"],
    "domains": ["telemetry", "identifiers"],
    "statement": "A system records integer checkpoint IDs. For each query [L,R], compute the XOR of all checkpoint IDs from L through R, inclusive.",
    "inputFormat": "The first line contains N and Q. The second line contains N nonnegative integers. Each of the next Q lines contains L and R using 1-based indexing.",
    "outputFormat": "For every query, print the XOR of the requested range on its own line.",
    "constraints": "1 <= N,Q <= 200000; 0 <= a[i] <= 10^9; 1 <= L <= R <= N",
    "sampleTestCases": [
      {
        "input": "5 3\n4 7 2 7 1\n1 3\n2 5\n4 4",
        "output": "1\n3\n7",
        "explanation": "4 XOR 7 XOR 2 = 1; 7 XOR 2 XOR 7 XOR 1 = 3; the fourth value is 7."
      },
      {
        "input": "3 2\n0 0 5\n1 2\n3 3",
        "output": "0\n5",
        "explanation": "XOR with zero leaves the other value unchanged."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Use a prefix XOR array. The XOR of [L,R] is prefix[R] XOR prefix[L-1].",
    "referenceSolution": "Build pref[0]=0 and pref[i]=pref[i-1]^a[i]. Answer each query with pref[R]^pref[L-1].",
    "bruteForceSolution": "For every query, iterate from L through R and XOR all values directly.",
    "inputGenerator": "Generate N and Q up to 200000, random values including zero and repeated values, then random valid ranges.",
    "inputValidator": "Verify N, Q, exactly N values, exactly Q queries, and every query satisfies 1 <= L <= R <= N.",
    "edgeCaseInputs": [
      "1 1\n42\n1 1",
      "5 3\n0 0 0 0 0\n1 5\n2 4\n3 3",
      "4 2\n1 2 3 4\n1 4\n2 3"
    ],
    "wrongSolutions": [
      {
        "name": "prefixSum",
        "description": "Uses arithmetic prefix sums instead of XOR prefix values.",
        "code": "pref[i]=pref[i-1]+a[i]"
      },
      {
        "name": "wrongBoundary",
        "description": "Fails to remove prefix[L-1] from the queried range.",
        "code": "print(pref[r])"
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "merge_time_blocks",
    "title": "Merge Time Blocks",
    "topic": "Sorting & Intervals",
    "difficulty": "Medium",
    "tags": ["sorting", "intervals", "merge"],
    "domains": ["scheduling", "operations"],
    "statement": "A system receives time blocks represented by inclusive integer intervals [start,end]. Merge every pair of overlapping or directly touching blocks and return the resulting disjoint intervals in increasing order.",
    "inputFormat": "The first line contains N. Each of the next N lines contains start and end.",
    "outputFormat": "Print the number of merged intervals, followed by one merged interval per line.",
    "constraints": "1 <= N <= 200000; 0 <= start <= end <= 10^9",
    "sampleTestCases": [
      {
        "input": "5\n1 3\n2 5\n7 9\n9 12\n15 16",
        "output": "3\n1 5\n7 12\n15 16",
        "explanation": "The first two intervals overlap. [7,9] and [9,12] touch at 9 and therefore merge."
      },
      {
        "input": "3\n5 5\n1 2\n3 4",
        "output": "1\n1 5",
        "explanation": "The intervals [1,2] and [3,4] touch because endpoints are integers and 2+1=3, so they merge; [5,5] then touches [3,4]."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Sort intervals by start and merge whenever the next start is at most currentEnd+1.",
    "referenceSolution": "Sort by start, initialize the current interval from the first item, and merge each following interval if its start <= currentEnd+1; otherwise emit the current interval and start a new one.",
    "bruteForceSolution": "Repeatedly scan the list for any pair of overlapping or touching intervals, merge them, and continue until no merge is possible.",
    "inputGenerator": "Generate random intervals with clusters of overlapping, touching, and separated blocks. Include duplicate intervals and single-point intervals.",
    "inputValidator": "Verify N and each interval has 0 <= start <= end <= 10^9.",
    "edgeCaseInputs": [
      "1\n5 5",
      "4\n1 1\n2 2\n3 3\n4 4",
      "3\n1 10\n2 3\n4 8",
      "4\n10 20\n1 2\n5 6\n30 40"
    ],
    "wrongSolutions": [
      {
        "name": "overlapOnly",
        "description": "Merges overlapping intervals but fails to merge directly touching integer intervals.",
        "code": "if start<=cur_end: cur_end=max(cur_end,end)"
      },
      {
        "name": "noSort",
        "description": "Attempts to merge intervals in input order without sorting.",
        "code": "for interval in intervals:\n    if interval[0]<=cur_end+1: ..."
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  },
  {
    "slug": "weighted_deadline_cutoff",
    "title": "Weighted Deadline Cutoff",
    "topic": "Sorting & Intervals",
    "difficulty": "Hard",
    "tags": ["sorting", "greedy", "deadlines", "heap"],
    "domains": ["project-planning", "scheduling"],
    "statement": "Each job has a positive processing time and a deadline. Jobs must run one at a time. A job is considered completed on time if its completion time is at most its deadline. Find the maximum number of jobs that can be completed on time.",
    "inputFormat": "The first line contains N. Each of the next N lines contains processing time P and deadline D.",
    "outputFormat": "Print the maximum number of jobs that can be completed on time.",
    "constraints": "1 <= N <= 200000; 1 <= P,D <= 10^9",
    "sampleTestCases": [
      {
        "input": "5\n3 4\n2 5\n4 6\n1 7\n2 10",
        "output": "4",
        "explanation": "A feasible selection can complete jobs with durations 3,2,1,2 by deadlines 4,5,7,10 respectively."
      },
      {
        "input": "4\n5 3\n4 4\n3 5\n2 6",
        "output": "2",
        "explanation": "At most two of the jobs can be scheduled before their deadlines."
      }
    ],
    "checker": "exact",
    "timeLimit": 2.0,
    "memoryLimit": 256,
    "coreIdea": "Sort jobs by deadline. Keep the selected jobs in a max-heap by processing time; whenever total processing exceeds the current deadline, remove the longest selected job.",
    "referenceSolution": "Sort jobs by deadline. Add each processing time to a running total and max-heap. If total exceeds the current deadline, remove the largest processing time and subtract it. The heap size at the end is the maximum number of on-time jobs.",
    "bruteForceSolution": "For small N, enumerate subsets of jobs. For each subset, sort selected jobs by deadline and check whether cumulative processing times meet every deadline. Return the largest feasible subset size.",
    "inputGenerator": "Generate random jobs with processing times and deadlines, including impossible jobs with processing time greater than deadline, tight deadline clusters, and loose deadlines.",
    "inputValidator": "Verify N and exactly N positive processing-time/deadline pairs within bounds.",
    "edgeCaseInputs": [
      "1\n5 3",
      "1\n3 5",
      "4\n1 1\n1 2\n1 3\n1 4",
      "4\n10 5\n9 6\n8 7\n1 100"
    ],
    "wrongSolutions": [
      {
        "name": "deadlineOnly",
        "description": "Schedules jobs solely by earliest deadline without removing expensive jobs when a deadline is violated.",
        "code": "jobs.sort(key=lambda x:x[1])\nt=0\nfor p,d in jobs:\n    t+=p\n    if t<=d: ans+=1"
      },
      {
        "name": "shortestFirst",
        "description": "Sorts only by processing time, which can miss the optimal deadline-aware schedule.",
        "code": "jobs.sort()\nt=0\nfor p,d in jobs: ..."
      }
    ],
    "hiddenTestPlan": {
      "small": 5,
      "edge": "all edgeCaseInputs",
      "large": 4,
      "weightSmall": 40,
      "weightLarge": 60
    },
    "source": "original",
    "license": "original-work",
    "status": "draft"
  }
]
