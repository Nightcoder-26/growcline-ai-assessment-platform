"""Batch 5 – User-Curated Problems."""
from typing import List, Dict, Any

BATCH5_PROBLEMS: List[Dict[str, Any]] = [
    {
        "slug": "missing_inventory_id",
        "title": "Missing Inventory ID",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "tags": [
            "array",
            "hash-set",
            "missing-value"
        ],
        "domains": [
            "inventory",
            "warehousing"
        ],
        "statement": "A warehouse assigns every item an ID from 1 through N. Exactly one ID is missing from the recorded list of N-1 IDs. Find the missing ID.",
        "inputFormat": "The first line contains N. The second line contains N-1 distinct integers from 1 through N.",
        "outputFormat": "Print the missing ID.",
        "constraints": "2 <= N <= 200000; every recorded ID is distinct and lies in [1,N].",
        "sampleTestCases": [
            {
                "input": "5\n1 2 5 4",
                "output": "3",
                "explanation": "IDs 1, 2, 4 and 5 are present, so 3 is missing."
            },
            {
                "input": "2\n1",
                "output": "2",
                "explanation": "The only recorded ID is 1, so ID 2 is missing."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Use XOR or the arithmetic sum identity to recover the single missing value.",
        "referenceSolution": "Compute XOR of every number from 1 through N and XOR it with every recorded ID. Equal values cancel, leaving the missing ID.",
        "bruteForceSolution": "For each candidate from 1 through N, check whether it occurs in the recorded list and return the absent candidate.",
        "inputGenerator": "Generate N, choose one missing value uniformly, create all other IDs, and shuffle them.",
        "inputValidator": "Verify N and exactly N-1 distinct integers, each within [1,N].",
        "edgeCaseInputs": [
            "2\n1",
            "5\n2 3 4 5",
            "5\n1 2 3 4"
        ],
        "wrongSolutions": [
            {
                "name": "indexAssumption",
                "description": "Assumes the input is sorted and attempts to find the first positional mismatch.",
                "code": "for i,x in enumerate(a,1):\n    if x!=i:\n        print(i); break"
            },
            {
                "name": "wrongSumRange",
                "description": "Uses the sum from 0 through N-1 instead of 1 through N.",
                "code": "expected=n*(n-1)//2\nprint(expected-sum(a))"
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
        "slug": "anagram_alert_groups",
        "title": "Anagram Alert Groups",
        "topic": "Strings",
        "difficulty": "Medium",
        "tags": [
            "strings",
            "hashing",
            "anagram"
        ],
        "domains": [
            "security",
            "log-analysis"
        ],
        "statement": "A security system records lowercase alert names. Two names belong to the same group if they contain exactly the same letters with the same frequencies. Return the size of the largest such group.",
        "inputFormat": "The first line contains N. The next N lines contain one lowercase alert name each.",
        "outputFormat": "Print the maximum number of alert names that belong to the same anagram group.",
        "constraints": "1 <= N <= 100000; each name has length 1 to 50.",
        "sampleTestCases": [
            {
                "input": "6\nlisten\nsilent\nenlist\nalert\nlater\nratel",
                "output": "3",
                "explanation": "listen, silent and enlist form one group of size 3."
            },
            {
                "input": "4\nabc\ndef\nghi\nxyz",
                "output": "1",
                "explanation": "No two names are anagrams."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Represent every word by a canonical frequency signature and count equal signatures.",
        "referenceSolution": "For each word, construct a 26-element frequency tuple and increment its hash-map count. Track the largest count.",
        "bruteForceSolution": "Compare every pair of words by sorting their characters or building frequency arrays, then group matching words.",
        "inputGenerator": "Generate random words and deliberately create anagram families by shuffling selected base words.",
        "inputValidator": "Verify N and exactly N lowercase alphabetic words, each length between 1 and 50.",
        "edgeCaseInputs": [
            "1\na",
            "5\na a a a a",
            "4\nab\nba\nabc\ncab"
        ],
        "wrongSolutions": [
            {
                "name": "lengthOnly",
                "description": "Groups words only by length and ignores character composition.",
                "code": "freq[len(word)] += 1"
            },
            {
                "name": "setSignature",
                "description": "Uses only the set of distinct characters, losing repeated-character frequencies.",
                "code": "key=''.join(sorted(set(word)))"
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
        "slug": "closest_temperature_pair",
        "title": "Closest Temperature Pair",
        "topic": "Two Pointers",
        "difficulty": "Medium",
        "tags": [
            "two-pointers",
            "sorting",
            "absolute-difference"
        ],
        "domains": [
            "weather",
            "analytics"
        ],
        "statement": "Given a sorted list of temperature readings, find the minimum absolute difference between two distinct readings.",
        "inputFormat": "The first line contains N. The second line contains N sorted integers.",
        "outputFormat": "Print the minimum absolute difference between any two distinct readings.",
        "constraints": "2 <= N <= 200000; -10^9 <= temperature[i] <= 10^9; readings are sorted nondecreasing.",
        "sampleTestCases": [
            {
                "input": "6\n-5 -1 2 8 9 15",
                "output": "1",
                "explanation": "The readings 8 and 9 differ by only 1."
            },
            {
                "input": "4\n3 10 20 40",
                "output": "7",
                "explanation": "The smallest adjacent difference is 10-3 = 7."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "In sorted order, the minimum absolute difference must occur between adjacent elements.",
        "referenceSolution": "Scan adjacent pairs and minimize a[i]-a[i-1].",
        "bruteForceSolution": "Check every pair i<j and minimize abs(a[i]-a[j]).",
        "inputGenerator": "Generate sorted random temperatures with both duplicate-heavy and widely separated cases.",
        "inputValidator": "Verify N and exactly N sorted integers in the specified range.",
        "edgeCaseInputs": [
            "2\n-10 10",
            "5\n7 7 7 7 7",
            "4\n-100 -50 0 100"
        ],
        "wrongSolutions": [
            {
                "name": "endpointsOnly",
                "description": "Checks only the first and last temperatures.",
                "code": "print(a[-1]-a[0])"
            },
            {
                "name": "unsortedAssumption",
                "description": "Uses differences in input order without respecting the sorted structure required by the problem.",
                "code": "ans=min(abs(a[i]-a[i-1]) for i in range(1,n))"
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
        "slug": "at_most_k_distinct",
        "title": "At Most K Distinct Events",
        "topic": "Sliding Window",
        "difficulty": "Medium",
        "tags": [
            "sliding-window",
            "frequency-map",
            "distinct-count"
        ],
        "domains": [
            "event-streams",
            "analytics"
        ],
        "statement": "An event stream is represented by integer event types. Find the length of the longest contiguous segment containing at most K distinct event types.",
        "inputFormat": "The first line contains N and K. The second line contains N event-type integers.",
        "outputFormat": "Print the maximum length of a contiguous segment containing at most K distinct values.",
        "constraints": "1 <= N <= 200000; 0 <= K <= N; 1 <= eventType <= 10^9",
        "sampleTestCases": [
            {
                "input": "8 2\n1 2 1 3 3 2 2 1",
                "output": "5",
                "explanation": "The segment 3 3 2 2 1 contains exactly two distinct types and has length 5."
            },
            {
                "input": "5 0\n1 1 1 1 1",
                "output": "0",
                "explanation": "No nonempty segment can contain at most zero distinct event types."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Expand the right boundary while counting frequencies; shrink the left boundary whenever the number of distinct values exceeds K.",
        "referenceSolution": "Use a frequency dictionary and two pointers. Add a[right], increasing the distinct count when its frequency becomes one. While distinct>K, remove a[left] and move left. Track the largest valid window.",
        "bruteForceSolution": "For every left endpoint, extend the right endpoint while maintaining a set of distinct values and record the largest valid length.",
        "inputGenerator": "Generate random event types from pools of different sizes and choose K from 0 through the pool size.",
        "inputValidator": "Verify N, K, and exactly N positive event types.",
        "edgeCaseInputs": [
            "1 0\n1",
            "1 1\n5",
            "6 1\n2 2 2 3 3 3",
            "5 5\n1 2 3 4 5"
        ],
        "wrongSolutions": [
            {
                "name": "atLeastK",
                "description": "Shrinks when the window has fewer than K distinct values instead of when it exceeds K.",
                "code": "while distinct<k: left+=1"
            },
            {
                "name": "countDuplicates",
                "description": "Counts repeated occurrences as distinct event types.",
                "code": "window_size - frequency_of_most_common"
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
        "slug": "queue_service_time",
        "title": "Queue Service Time",
        "topic": "Stack & Queue",
        "difficulty": "Easy",
        "tags": [
            "queue",
            "simulation",
            "prefix-sum"
        ],
        "domains": [
            "customer-service",
            "operations"
        ],
        "statement": "Customers stand in a queue. Customer i requires S[i] minutes of service. Find the time at which the last customer finishes service, assuming service begins at time 0 and customers are served in order.",
        "inputFormat": "The first line contains N. The second line contains N positive service times.",
        "outputFormat": "Print the finishing time of the final customer.",
        "constraints": "1 <= N <= 200000; 1 <= S[i] <= 10^6",
        "sampleTestCases": [
            {
                "input": "5\n3 2 5 1 4",
                "output": "15",
                "explanation": "The total service time is 3+2+5+1+4 = 15 minutes."
            },
            {
                "input": "1\n9",
                "output": "9",
                "explanation": "The only customer finishes after 9 minutes."
            }
        ],
        "checker": "exact",
        "timeLimit": 1.0,
        "memoryLimit": 256,
        "coreIdea": "Because customers are served sequentially with no idle time, the final completion time is the sum of all service times.",
        "referenceSolution": "Read all service times and output their sum.",
        "bruteForceSolution": "Simulate a queue by repeatedly removing the front customer and adding its service time to the current clock.",
        "inputGenerator": "Generate N and positive service times, including uniform, maximum-heavy, and random distributions.",
        "inputValidator": "Verify N and exactly N positive service times within bounds.",
        "edgeCaseInputs": [
            "1\n1",
            "3\n1000000 1000000 1000000",
            "5\n1 1 1 1 1"
        ],
        "wrongSolutions": [
            {
                "name": "maximumOnly",
                "description": "Returns the largest service time instead of the total queue completion time.",
                "code": "print(max(service))"
            },
            {
                "name": "offByOne",
                "description": "Adds only N-1 service times.",
                "code": "print(sum(service[:-1]))"
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
        "slug": "next_available_slot",
        "title": "Next Available Slot",
        "topic": "Binary Search",
        "difficulty": "Easy",
        "tags": [
            "binary-search",
            "lower-bound",
            "sorted-array"
        ],
        "domains": [
            "scheduling",
            "booking"
        ],
        "statement": "A sorted list contains the start times of available appointment slots. Given a requested time T, find the first available slot whose start time is at least T. If none exists, print -1.",
        "inputFormat": "The first line contains N and T. The second line contains N sorted integer slot times.",
        "outputFormat": "Print the first slot time greater than or equal to T, or -1 if no such slot exists.",
        "constraints": "1 <= N <= 200000; 0 <= T <= 10^9; 0 <= slot[i] <= 10^9; slots are sorted nondecreasing.",
        "sampleTestCases": [
            {
                "input": "6 15\n2 5 9 15 18 25",
                "output": "15",
                "explanation": "15 itself is available, so it is the first valid slot."
            },
            {
                "input": "4 20\n2 5 9 15",
                "output": "-1",
                "explanation": "All available slots occur before 20."
            }
        ],
        "checker": "exact",
        "timeLimit": 1.0,
        "memoryLimit": 256,
        "coreIdea": "Use lower-bound binary search to locate the first element greater than or equal to T.",
        "referenceSolution": "Maintain low=0 and high=N. While low<high, test mid. If a[mid]>=T, set high=mid; otherwise set low=mid+1. If low==N, print -1; otherwise print a[low].",
        "bruteForceSolution": "Scan from left to right and return the first slot whose value is at least T.",
        "inputGenerator": "Generate sorted slot times and choose T below the minimum, equal to an existing slot, between slots, or above the maximum.",
        "inputValidator": "Verify N, T, exactly N sorted slot times, and all values within bounds.",
        "edgeCaseInputs": [
            "1 0\n5",
            "1 5\n5",
            "1 6\n5",
            "5 3\n1 2 3 4 5"
        ],
        "wrongSolutions": [
            {
                "name": "upperBound",
                "description": "Finds the first slot strictly greater than T, incorrectly skipping a slot exactly equal to T.",
                "code": "if a[mid]>t: high=mid"
            },
            {
                "name": "lastValid",
                "description": "Returns the largest slot below T instead of the first slot at or above T.",
                "code": "ans=max(x for x in a if x<t)"
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
        "slug": "minimum_processing_rate",
        "title": "Minimum Processing Rate",
        "topic": "Binary Search",
        "difficulty": "Hard",
        "tags": [
            "binary-search",
            "answer-space",
            "ceil-division"
        ],
        "domains": [
            "manufacturing",
            "capacity-planning"
        ],
        "statement": "A machine must process several batches. Batch i contains B[i] units. The machine processes exactly R units per hour and may continue to the next batch only after finishing the current one. Find the minimum integer rate R that allows all batches to finish within H hours.",
        "inputFormat": "The first line contains N and H. The second line contains N positive batch sizes.",
        "outputFormat": "Print the minimum integer processing rate R.",
        "constraints": "1 <= N <= 200000; 1 <= B[i] <= 10^9; 1 <= H <= 10^18",
        "sampleTestCases": [
            {
                "input": "4 8\n10 20 15 5",
                "output": "7",
                "explanation": "At rate 7, the required hours are ceil(10/7)+ceil(20/7)+ceil(15/7)+ceil(5/7)=2+3+3+1=9, so this sample would not fit; the correct minimum is 8, giving 2+3+2+1=8."
            },
            {
                "input": "3 3\n5 5 5",
                "output": "5",
                "explanation": "Each batch requires one hour at rate 5, so three hours are sufficient."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Feasibility is monotonic in R. Binary-search the smallest rate for which the sum of ceil(B[i]/R) is at most H.",
        "referenceSolution": "Binary-search R from 1 to max(B). For each candidate, compute required hours using (B[i]+R-1)//R, stopping early if the total exceeds H. Keep the smallest feasible R.",
        "bruteForceSolution": "Try every rate from 1 through max(B), computing the required total hours until the first feasible rate is found.",
        "inputGenerator": "Generate batch sizes with small and very large values, and choose H around the minimum and maximum possible processing times.",
        "inputValidator": "Verify N, H, and exactly N positive batch sizes within bounds.",
        "edgeCaseInputs": [
            "1 1\n100",
            "3 3\n5 5 5",
            "3 100\n100 200 300",
            "5 5\n1 1 1 1 1"
        ],
        "wrongSolutions": [
            {
                "name": "averageRate",
                "description": "Uses total work divided by H and ignores per-batch ceiling effects.",
                "code": "print((sum(b)+h-1)//h)"
            },
            {
                "name": "floatingCeil",
                "description": "Uses floating-point ceil operations unnecessarily and may suffer precision issues on very large inputs.",
                "code": "hours += math.ceil(x/r)"
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
        "slug": "range_and_signature",
        "title": "Range AND Signature",
        "topic": "Math & Bit Manipulation",
        "difficulty": "Medium",
        "tags": [
            "bitwise-and",
            "prefix-properties",
            "bit-manipulation"
        ],
        "domains": [
            "identifiers",
            "systems"
        ],
        "statement": "For each query [L,R], compute the bitwise AND of all integers from L through R, inclusive.",
        "inputFormat": "The first line contains Q. Each of the next Q lines contains L and R.",
        "outputFormat": "For every query, print L AND (L+1) AND ... AND R.",
        "constraints": "1 <= Q <= 200000; 0 <= L <= R <= 10^18",
        "sampleTestCases": [
            {
                "input": "3\n5 7\n8 15\n10 10",
                "output": "4\n8\n10",
                "explanation": "5 AND 6 AND 7 = 4; every number from 8 through 15 shares the high bit represented by 8."
            },
            {
                "input": "2\n0 3\n12 13",
                "output": "0\n12",
                "explanation": "Including 0 makes the first range AND equal to 0."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Repeatedly clear the lowest set bit of R until R <= L; the remaining common prefix bits form the range AND.",
        "referenceSolution": "Set x=R. While x>L, clear x's lowest set bit using x &= x-1. Print x. This removes every bit that changes somewhere in [L,R].",
        "bruteForceSolution": "For small ranges, initialize ans=L and repeatedly apply ans &= x for x from L+1 through R.",
        "inputGenerator": "Generate random ranges over 64-bit nonnegative integers, emphasizing equal endpoints, powers of two, adjacent values, and very wide ranges.",
        "inputValidator": "Verify Q and each query satisfies 0 <= L <= R <= 10^18.",
        "edgeCaseInputs": [
            "1\n0 0",
            "1\n7 7",
            "3\n7 8\n8 9\n15 16"
        ],
        "wrongSolutions": [
            {
                "name": "rangeOr",
                "description": "Computes bitwise OR rather than AND.",
                "code": "ans=L\nfor x in range(L+1,R+1): ans|=x"
            },
            {
                "name": "endpointsOnly",
                "description": "Returns L & R without considering values between them.",
                "code": "print(L&R)"
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
        "slug": "maximum_nonoverlap_tasks",
        "title": "Maximum Non-Overlapping Tasks",
        "topic": "Sorting & Intervals",
        "difficulty": "Medium",
        "tags": [
            "intervals",
            "greedy",
            "sorting"
        ],
        "domains": [
            "scheduling",
            "task-management"
        ],
        "statement": "Each task occupies an interval [start,end), where the task uses time from start up to but not including end. Select the maximum number of tasks that can be completed without overlap.",
        "inputFormat": "The first line contains N. Each of the next N lines contains start and end.",
        "outputFormat": "Print the maximum number of non-overlapping tasks.",
        "constraints": "1 <= N <= 200000; 0 <= start < end <= 10^9",
        "sampleTestCases": [
            {
                "input": "5\n1 3\n2 5\n4 7\n6 8\n7 9",
                "output": "3",
                "explanation": "Tasks [1,3), [4,7), and [7,9) can all be selected."
            },
            {
                "input": "4\n1 10\n2 3\n3 4\n4 5",
                "output": "3",
                "explanation": "Selecting the three short tasks gives the maximum count."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Sort tasks by finishing time and greedily select each task whose start is at least the end of the last selected task.",
        "referenceSolution": "Sort intervals by end ascending. Initialize lastEnd=-1. For each interval, if start>=lastEnd, select it and set lastEnd=end. Count selected tasks.",
        "bruteForceSolution": "Enumerate subsets for small N, sort each chosen subset by end time, and check whether its intervals are non-overlapping.",
        "inputGenerator": "Generate random intervals with overlapping clusters, nested intervals, and chains of adjacent intervals.",
        "inputValidator": "Verify N and every interval satisfies 0 <= start < end <= 10^9.",
        "edgeCaseInputs": [
            "1\n0 1",
            "4\n1 2\n2 3\n3 4\n4 5",
            "3\n1 10\n2 9\n3 8"
        ],
        "wrongSolutions": [
            {
                "name": "shortestDuration",
                "description": "Sorts by interval length instead of finishing time, which is not the correct greedy strategy.",
                "code": "jobs.sort(key=lambda x:x[1]-x[0])"
            },
            {
                "name": "startTimeGreedy",
                "description": "Always selects the earliest-starting task, which can block more tasks later.",
                "code": "jobs.sort(key=lambda x:x[0])"
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
        "slug": "minimum_window_sum",
        "title": "Minimum Window Sum",
        "topic": "Sliding Window",
        "difficulty": "Easy",
        "tags": [
            "sliding-window",
            "array",
            "fixed-window"
        ],
        "domains": [
            "finance",
            "monitoring"
        ],
        "statement": "Given a sequence of daily measurements and a window size K, find the minimum sum among all contiguous windows of exactly K days.",
        "inputFormat": "The first line contains N and K. The second line contains N integers.",
        "outputFormat": "Print the minimum sum of any contiguous segment of length K.",
        "constraints": "1 <= K <= N <= 200000; -10^9 <= a[i] <= 10^9",
        "sampleTestCases": [
            {
                "input": "6 3\n5 2 7 1 3 4",
                "output": "8",
                "explanation": "The window [1,3,4] has sum 8, the smallest among all length-3 windows."
            },
            {
                "input": "4 2\n-5 3 -2 1",
                "output": "-2",
                "explanation": "The window [-5,3] sums to -2, and [3,-2] also sums to 1 while [-2,1] sums to -1."
            }
        ],
        "checker": "exact",
        "timeLimit": 1.0,
        "memoryLimit": 256,
        "coreIdea": "Maintain the sum of a fixed-size window and update it by removing the outgoing element and adding the incoming element.",
        "referenceSolution": "Compute the first K-element sum. Then slide one position at a time, updating the sum with current += a[i]-a[i-K], and retain the minimum.",
        "bruteForceSolution": "For every possible starting position, sum the next K values directly and take the minimum.",
        "inputGenerator": "Generate random arrays with positive, negative, and mixed values and random K.",
        "inputValidator": "Verify N, K, and exactly N integers within bounds.",
        "edgeCaseInputs": [
            "1 1\n5",
            "5 5\n1 2 3 4 5",
            "5 1\n-5 4 -2 7 -1"
        ],
        "wrongSolutions": [
            {
                "name": "maximumWindow",
                "description": "Tracks the largest window sum instead of the smallest.",
                "code": "best=max(best,current)"
            },
            {
                "name": "wrongWindowSize",
                "description": "Accidentally uses K+1 elements when updating the window.",
                "code": "current += a[i]-a[i-k-1]"
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
