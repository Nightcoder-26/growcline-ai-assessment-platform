"""
User-Curated Problem Bank — 10 Reviewed Problems
All problems contain:
  - referenceSolution: human-authored, correct, efficient
  - bruteForceSolution: simpler but slower, used for stress testing
  - inputGenerator: parametric generator (seed, mode) for random tests
  - inputValidator: validates constraints before judging
  - edgeCaseInputs: corner cases to always include in the hidden test suite
  - wrongSolutions: known-wrong programs for mutation testing (TPR/TNR checks)
  - hiddenTestPlan: test-case budget breakdown
Status is set to "draft" here; the seed script promotes to "approved".
"""

from typing import List, Dict, Any

USER_CURATED_PROBLEMS: List[Dict[str, Any]] = [
    # ── 1. Parcel Ledger Balance ──────────────────────────────────────────────
    {
        "slug": "parcel_balance_check",
        "title": "Parcel Ledger Balance",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "tags": ["hashing", "frequency-map"],
        "domains": ["logistics", "backend"],
        "statement": (
            "A sorting hub receives a list of parcel IDs recorded by an intake scanner "
            "and another list recorded by the dispatch scanner. Every parcel that leaves "
            "should correspond to exactly one parcel that arrived. Determine whether the "
            "two records contain the same multiset of parcel IDs. IDs may repeat, and "
            "order does not matter."
        ),
        "inputFormat": (
            "Line 1 contains an integer n. "
            "Line 2 contains n integers describing the intake parcel IDs. "
            "Line 3 contains n integers describing the dispatch parcel IDs."
        ),
        "outputFormat": (
            "Print YES if the two records contain exactly the same IDs with the same "
            "multiplicities; otherwise print NO."
        ),
        "constraints": "1 <= n <= 200000. Each parcel ID is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "5\n12 7 12 4 9\n9 12 4 12 7\n",
                "output": "YES",
                "explanation": "Both records contain two 12s and one each of 7, 4, and 9.",
            },
            {
                "input": "4\n3 8 8 2\n3 8 2 2\n",
                "output": "NO",
                "explanation": "The first record has two 8s while the second has two 2s.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Count every ID in one record and cancel those counts using the other record.",
        "referenceSolution": (
            "import sys\n\n"
            "a=list(map(int,sys.stdin.buffer.read().split())); n=a[0]; x=a[1:1+n]; y=a[1+n:1+2*n]\n"
            "d={}\n"
            "for v in x:d[v]=d.get(v,0)+1\n"
            "for v in y:\n"
            "    d[v]=d.get(v,0)-1\n"
            "print('YES' if all(v==0 for v in d.values()) else 'NO')"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split())); n=a[0]; x=a[1:1+n]; y=a[1+n:1+2*n]\n"
            "print('YES' if sorted(x)==sorted(y) else 'NO')"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1])); m=sys.argv[2]\n"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30)); x=[r.randint(-10,10) for _ in range(n)]\n"
            "y=x[:]; r.shuffle(y)\n"
            "if m=='edge' and n==1:y[0]=x[0]+1\n"
            "elif m=='small' and r.random()<.5:y[r.randrange(n)]+=1\n"
            "print(n); print(*x); print(*y)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split())); n=a[0]\n"
            " assert 1<=n<=200000 and len(a)==1+2*n\n"
            " assert all(-10**9<=x<=10**9 for x in a[1:])\n"
            "except: sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\n0\n0\n",
            "1\n-1000000000\n1000000000\n",
            "5\n7 7 7 7 7\n7 7 7 7 7\n",
            "5\n1 2 3 4 5\n5 4 3 2 1\n",
            "6\n1 1 2 2 3 3\n1 2 1 3 2 3\n",
            "4\n-2 -2 -1 0\n-2 -1 0 0\n",
        ],
        "wrongSolutions": [
            {
                "name": "set_only",
                "description": "Ignores multiplicities by comparing sets.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
                    "print('YES' if set(a[1:1+n])==set(a[1+n:1+2*n]) else 'NO')"
                ),
            },
            {
                "name": "position_compare",
                "description": "Incorrectly requires the records to have identical order.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
                    "print('YES' if a[1:1+n]==a[1+n:1+2*n] else 'NO')"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Repeatedly searches and removes from a list, making worst-case time quadratic.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0]; x=a[1:1+n]; y=a[1+n:1+2*n]\n"
                    "for v in y:\n"
                    " try:x.remove(v)\n"
                    " except ValueError: print('NO');sys.exit()\n"
                    "print('YES' if not x else 'NO')"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 2. Shelf Label Audit ──────────────────────────────────────────────────
    {
        "slug": "inventory_unique_labels",
        "title": "Shelf Label Audit",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "tags": ["hashing", "duplicates"],
        "domains": ["ecommerce", "data"],
        "statement": (
            "A warehouse prints one label for each shelf position. The audit requires every "
            "printed label to be unique. Given the labels in their printed order, determine "
            "whether any label appears more than once."
        ),
        "inputFormat": "Line 1 contains n. Line 2 contains n integer labels.",
        "outputFormat": "Print YES if every label occurs exactly once; otherwise print NO.",
        "constraints": "1 <= n <= 200000. Each label is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "5\n18 4 27 9 31\n",
                "output": "YES",
                "explanation": "All five labels are different.",
            },
            {
                "input": "6\n2 8 4 2 9 7\n",
                "output": "NO",
                "explanation": "Label 2 appears twice.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Insert labels into a set and reject as soon as an already-seen label appears.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];"
            "print('YES' if len(set(x))==n else 'NO')"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n]\n"
            "for i in range(n):\n"
            " for j in range(i):\n"
            "  if x[i]==x[j]:print('NO');sys.exit()\n"
            "print('YES')"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));"
            "x=list(range(n));r.shuffle(x)\n"
            "if m!='large':x=[v-10 for v in x]\n"
            "if m=='small' and n>1 and r.random()<.5:x[-1]=x[0]\n"
            "print(n);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
            "assert 1<=n<=200000 and len(a)==n+1;assert all(-10**9<=x<=10**9 for x in a[1:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\n0\n",
            "2\n-1000000000 1000000000\n",
            "5\n7 7 7 7 7\n",
            "5\n1 2 3 4 5\n",
            "6\n1 2 1 3 4 5\n",
            "4\n-3 -2 -1 0\n",
        ],
        "wrongSolutions": [
            {
                "name": "adjacent_only",
                "description": "Only compares neighboring labels, so nonadjacent duplicates are missed.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];"
                    "print('NO' if any(x[i]==x[i-1] for i in range(1,n)) else 'YES')"
                ),
            },
            {
                "name": "set_length_off",
                "description": "Accidentally permits one duplicate by checking the wrong threshold.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];"
                    "print('YES' if len(set(x))>=n-1 else 'NO')"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Checks every pair and is quadratic.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n]\n"
                    "for i in range(n):\n"
                    " for j in range(i):\n"
                    "  if x[i]==x[j]:print('NO');sys.exit()\n"
                    "print('YES')"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 3. Sensor Signal Leader ───────────────────────────────────────────────
    {
        "slug": "most_active_sensor",
        "title": "Sensor Signal Leader",
        "topic": "Arrays & Hashing",
        "difficulty": "Medium",
        "tags": ["hashing", "frequency-map", "tie-breaking"],
        "domains": ["devops", "data"],
        "statement": (
            "A monitoring service receives integer sensor codes in chronological order. "
            "The most active sensor is the code appearing most often. If several codes have "
            "the same highest frequency, choose the smallest code. Report that code."
        ),
        "inputFormat": "Line 1 contains n. Line 2 contains n integer sensor codes.",
        "outputFormat": "Print the smallest sensor code among those with maximum frequency.",
        "constraints": "1 <= n <= 200000. Each sensor code is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "7\n5 2 5 9 2 5 9\n",
                "output": "5",
                "explanation": "Code 5 appears three times, more than every other code.",
            },
            {
                "input": "6\n8 4 8 4 6 6\n",
                "output": "4",
                "explanation": "Codes 4, 6, and 8 each occur twice, so the smallest code, 4, wins.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Maintain frequencies and update the winner using frequency first and numeric value as the tie-breaker.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];d={}\n"
            "for x in a[1:1+n]:d[x]=d.get(x,0)+1\n"
            "print(min(d,key=lambda x:(-d[x],x)))"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];best=None;bf=-1\n"
            "for v in x:\n"
            " c=x.count(v)\n"
            " if c>bf or (c==bf and (best is None or v<best)):best,bf=v,c\n"
            "print(best)"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,35));"
            "x=[r.randint(-20,20) for _ in range(n)]\n"
            "if m=='edge':x=[-1000000000]*n\n"
            "print(n);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
            "assert 1<=n<=200000 and len(a)==n+1;assert all(-10**9<=x<=10**9 for x in a[1:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\n42\n",
            "5\n-1000000000 -1000000000 1 2 3\n",
            "6\n7 7 7 7 7 7\n",
            "5\n1 2 3 4 5\n",
            "6\n1 2 1 2 3 3\n",
            "7\n-2 -1 -2 -1 0 0 1\n",
        ],
        "wrongSolutions": [
            {
                "name": "last_winner",
                "description": "Uses the latest tied value instead of the smallest tied value.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];d={}\n"
                    "for x in a[1:1+n]:d[x]=d.get(x,0)+1\n"
                    "print(max(d,key=d.get))"
                ),
            },
            {
                "name": "first_occurrence_tie",
                "description": "Breaks ties by first appearance rather than smallest numeric code.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];d={};best=x[0]\n"
                    "for v in x:d[v]=d.get(v,0)+1\n"
                    "for v in x:\n"
                    " if d[v]>d[best]:best=v\n"
                    "print(best)"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Counts each value by scanning the entire list, causing quadratic work.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];best=None;bf=-1\n"
                    "for v in x:\n"
                    " c=x.count(v)\n"
                    " if c>bf or (c==bf and (best is None or v<best)):best,bf=v,c\n"
                    "print(best)"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 4. Badge Code Mirror ──────────────────────────────────────────────────
    {
        "slug": "badge_code_mirror",
        "title": "Badge Code Mirror",
        "topic": "Strings",
        "difficulty": "Easy",
        "tags": ["strings", "two-pointers"],
        "domains": ["backend", "general"],
        "statement": (
            "An access terminal accepts a badge code when it reads identically from the left "
            "and from the right. The code contains only lowercase English letters and digits. "
            "Determine whether the complete code is such a mirror."
        ),
        "inputFormat": "Line 1 contains an integer n. Line 2 contains a string of exactly n lowercase English letters and digits.",
        "outputFormat": "Print YES if the string reads the same in reverse; otherwise print NO.",
        "constraints": "1 <= n <= 200000. The string contains only characters a-z and 0-9.",
        "sampleTestCases": [
            {
                "input": "7\nab12cba\n",
                "output": "NO",
                "explanation": "Reversed: 'abc21ba' which differs from 'ab12cba'.",
            },
            {
                "input": "6\n4abba4\n",
                "output": "YES",
                "explanation": "Each character has the same character at the symmetric position.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Compare symmetric characters while moving inward from both ends.",
        "referenceSolution": (
            "import sys\n"
            "a=sys.stdin.buffer.read().split();s=a[1].decode();print('YES' if s==s[::-1] else 'NO')"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=sys.stdin.buffer.read().split();s=a[1].decode();"
            "print('YES' if all(s[i]==s[len(s)-1-i] for i in range(len(s))) else 'NO')"
        ),
        "inputGenerator": (
            "import sys,random,string\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,40));"
            "s=''.join(r.choice(string.ascii_lowercase+'0123456789') for _ in range(n))\n"
            "if m=='edge':s='a'*n\n"
            "if m=='small' and n>1 and r.random()<.5:s=s[:n//2]+('a' if s[-1]!='a' else 'b')+s[n//2+1:]\n"
            "print(n);print(s)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=sys.stdin.read().split();assert len(a)==2;n=int(a[0]);s=a[1];"
            "assert 1<=n<=200000 and len(s)==n and all(c.isdigit() or 'a'<=c<='z' for c in s)\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\na\n",
            "2\n00\n",
            "6\nabcdef\n",
            "7\nracecar\n",
            "5\naaaaa\n",
            "8\nabccbaaa\n",
        ],
        "wrongSolutions": [
            {
                "name": "case_insensitive",
                "description": "Irrelevant for the stated lowercase-only alphabet and can hide an invalid assumption.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();s=a[1].lower();print('YES' if s==s[::-1] else 'NO')"
                ),
            },
            {
                "name": "half_only",
                "description": "Checks only the first half against the wrong shifted positions.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();s=a[1];n=len(s);"
                    "print('YES' if all(s[i]==s[n-i] for i in range(n//2)) else 'NO')"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Repeated string construction makes the algorithm unnecessarily quadratic.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();s=a[1];ok=True\n"
                    "for i in range(len(s)):\n"
                    " if s[:i+1][::-1]!=s[len(s)-1-i:]:ok=False;break\n"
                    "print('YES' if ok else 'NO')"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 5. Log Token Rotation ─────────────────────────────────────────────────
    {
        "slug": "log_token_rotation",
        "title": "Log Token Rotation",
        "topic": "Strings",
        "difficulty": "Medium",
        "tags": ["strings", "frequency-map"],
        "domains": ["devops", "backend"],
        "statement": (
            "A service emits a token made only from lowercase letters. Before storage, the "
            "service may cyclically rotate the token: a prefix is moved unchanged to the end. "
            "Given two recorded tokens, determine whether the second could have been produced "
            "from the first by one cyclic rotation."
        ),
        "inputFormat": "Line 1 contains an integer n. Line 2 contains the first token. Line 3 contains the second token.",
        "outputFormat": "Print YES if the second token is a cyclic rotation of the first; otherwise print NO.",
        "constraints": "1 <= n <= 200000. Both tokens contain exactly n lowercase English letters.",
        "sampleTestCases": [
            {
                "input": "6\nserver\nverser\n",
                "output": "NO",
                "explanation": "No cut of 'server' produces 'verser'.",
            },
            {
                "input": "6\nabcdef\ncdefab\n",
                "output": "YES",
                "explanation": "Moving the first two characters 'ab' to the end gives 'cdefab'.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "A rotation of s occurs as a length-n substring of s+s, so search for the second token there.",
        "referenceSolution": (
            "import sys\n"
            "a=sys.stdin.buffer.read().split();s=a[1];t=a[2];"
            "print('YES' if len(s)==len(t) and t in s+s else 'NO')"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=sys.stdin.buffer.read().split();n=int(a[0]);s=a[1].decode();t=a[2].decode();"
            "print('YES' if any(s[i:]+s[:i]==t for i in range(n)) else 'NO')"
        ),
        "inputGenerator": (
            "import sys,random,string\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));"
            "s=''.join(r.choice(string.ascii_lowercase) for _ in range(n))\n"
            "if m=='edge':t=s\n"
            "elif m=='small' and r.random()<.6:i=r.randrange(n);t=s[i:]+s[:i]\n"
            "else:t=''.join(r.choice(string.ascii_lowercase) for _ in range(n))\n"
            "print(n);print(s);print(t)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=sys.stdin.read().split();assert len(a)==3;n=int(a[0]);s,t=a[1],a[2];"
            "assert 1<=n<=200000 and len(s)==n and len(t)==n and all('a'<=c<='z' for c in s+t)\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\na\na\n",
            "2\nab\nba\n",
            "5\naaaaa\naaaaa\n",
            "6\nabcdef\nabcdef\n",
            "6\nabcdef\ncdefab\n",
            "7\nabcabca\ncabcaab\n",
        ],
        "wrongSolutions": [
            {
                "name": "prefix_suffix",
                "description": "Checks only whether the first and last characters match rather than full rotational structure.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();s,t=a[1],a[2];"
                    "print('YES' if s[0]==t[-1] and s[-1]==t[0] else 'NO')"
                ),
            },
            {
                "name": "sort_compare",
                "description": "Accepts strings with the same character counts even when their order cannot be rotated.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();print('YES' if sorted(a[1])==sorted(a[2]) else 'NO')"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Explicitly constructs every rotation, requiring quadratic time and memory churn.",
                "code": (
                    "import sys\n"
                    "a=sys.stdin.read().split();s,t=a[1],a[2]\n"
                    "print('YES' if any(s[i:]+s[:i]==t for i in range(len(s))) else 'NO')"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 6. Balanced Loading Belts ─────────────────────────────────────────────
    {
        "slug": "paired_loading_belts",
        "title": "Balanced Loading Belts",
        "topic": "Two Pointers",
        "difficulty": "Easy",
        "tags": ["two-pointers", "sorting"],
        "domains": ["logistics", "ecommerce"],
        "statement": (
            "A loading station has packages whose weights are known. Each truck trip can carry "
            "at most two packages, and the combined weight of those two packages must not exceed "
            "the truck limit. Find the maximum number of trips needed to load every package when "
            "packages may be paired optimally; a trip may also carry one package."
        ),
        "inputFormat": "Line 1 contains n and the weight limit L. Line 2 contains n package weights.",
        "outputFormat": "Print the minimum number of trips required to load all packages.",
        "constraints": "1 <= n <= 200000. 1 <= L <= 10^9. 1 <= each weight <= L.",
        "sampleTestCases": [
            {
                "input": "5 10\n2 5 4 8 1\n",
                "output": "3",
                "explanation": "Pairs (2,8), (4,5), and package 1 use three trips.",
            },
            {
                "input": "4 7\n4 4 3 2\n",
                "output": "2",
                "explanation": "Pair (4+3)=7 and pair (4+2)=6 — two trips cover all four packages.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "After sorting, pair the lightest package with the heaviest whenever they fit; otherwise the heaviest must travel alone.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=sorted(a[2:2+n]);i,j=0,n-1;ans=0\n"
            "while i<=j:\n"
            " ans+=1\n"
            " if i<j and x[i]+x[j]<=L:i+=1\n"
            " j-=1\n"
            "print(ans)"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "# Exact brute force for small tests via subset DP.\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];dp=[99]*(1<<n);dp[0]=0\n"
            "for m in range(1<<n):\n"
            " if dp[m]>=99:continue\n"
            " i=next((k for k in range(n) if not(m>>k&1)),None)\n"
            " if i is None:continue\n"
            " dp[m|1<<i]=min(dp[m|1<<i],dp[m]+1)\n"
            " for j in range(i+1,n):\n"
            "  if not(m>>j&1) and x[i]+x[j]<=L:dp[m|1<<i|1<<j]=min(dp[m|1<<i|1<<j],dp[m]+1)\n"
            "print(dp[-1])"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,16));"
            "L=r.randint(1,100) if m!='large' else 10**9;x=[r.randint(1,L) for _ in range(n)];"
            "print(n,L);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];"
            "assert 1<=n<=200000 and 1<=L<=10**9 and len(a)==n+2;assert all(1<=x<=L for x in a[2:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1 5\n5\n",
            "2 10\n5 5\n",
            "5 10\n5 5 5 5 5\n",
            "4 10\n1 2 3 4\n",
            "5 10\n9 8 7 6 1\n",
            "6 7\n1 1 1 6 6 6\n",
        ],
        "wrongSolutions": [
            {
                "name": "heaviest_with_heaviest",
                "description": "Pairs the two heaviest packages first, which can waste pairing opportunities.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=sorted(a[2:2+n]);ans=0\n"
                    "while x:\n"
                    " j=x.pop();ans+=1\n"
                    " if x and x[-1]+j<=L:x.pop()\n"
                    "print(ans)"
                ),
            },
            {
                "name": "unlimited_capacity",
                "description": "Treats every fitting group as potentially containing more than two packages.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=sorted(a[2:2+n]);ans=0;s=0\n"
                    "for v in x:\n"
                    " if s+v>L:ans+=1;s=0\n"
                    " s+=v\n"
                    "print(ans+(s>0))"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Uses subset dynamic programming and is exponential.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];dp=[99]*(1<<n);dp[0]=0\n"
                    "for m in range(1<<n):\n"
                    " if dp[m]>=99:continue\n"
                    " i=next((k for k in range(n) if not(m>>k&1)),None)\n"
                    " if i is None:continue\n"
                    " dp[m|1<<i]=min(dp[m|1<<i],dp[m]+1)\n"
                    " for j in range(i+1,n):\n"
                    "  if not(m>>j&1) and x[i]+x[j]<=L:dp[m|1<<i|1<<j]=min(dp[m|1<<i|1<<j],dp[m]+1)\n"
                    "print(dp[-1])"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 7. Closest Calibration Pair ───────────────────────────────────────────
    {
        "slug": "closest_temperature_pair",
        "title": "Closest Calibration Pair",
        "topic": "Two Pointers",
        "difficulty": "Medium",
        "tags": ["two-pointers", "sorting", "absolute-difference"],
        "domains": ["data", "devops"],
        "statement": (
            "A calibration team has recorded integer temperatures from sensors. Two readings "
            "are considered closely matched when their absolute difference is smallest. Find "
            "the minimum possible absolute difference between any two distinct readings."
        ),
        "inputFormat": "Line 1 contains n. Line 2 contains n integer temperature readings.",
        "outputFormat": "Print the minimum absolute difference between two distinct readings.",
        "constraints": "2 <= n <= 200000. Each reading is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "6\n12 3 18 7 9 20\n",
                "output": "2",
                "explanation": "The closest pair is 7 and 9.",
            },
            {
                "input": "5\n-8 4 -8 12 20\n",
                "output": "0",
                "explanation": "The reading -8 occurs twice.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Sorting places the closest pair next to each other, so only adjacent differences need to be examined.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=sorted(a[1:1+n]);"
            "print(min(x[i]-x[i-1] for i in range(1,n)))"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=10**30\n"
            "for i in range(n):\n"
            " for j in range(i):ans=min(ans,abs(x[i]-x[j]))\n"
            "print(ans)"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (2 if m=='edge' else r.randint(2,30));"
            "x=[r.randint(-100,100) for _ in range(n)];print(n);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
            "assert 2<=n<=200000 and len(a)==n+1;assert all(-10**9<=x<=10**9 for x in a[1:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "2\n0 0\n",
            "2\n-1000000000 1000000000\n",
            "5\n7 7 7 7 7\n",
            "5\n1 2 3 4 5\n",
            "6\n9 1 8 2 7 3\n",
            "4\n-5 -2 -3 10\n",
        ],
        "wrongSolutions": [
            {
                "name": "first_pair",
                "description": "Reports the difference of the first two input values instead of the closest pair.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));print(abs(a[1]-a[2]))"
                ),
            },
            {
                "name": "max_gap",
                "description": "Accidentally searches for the largest adjacent gap after sorting.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=sorted(a[1:]);"
                    "print(max(x[i]-x[i-1] for i in range(2,n+1)))"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Checks every pair and takes quadratic time.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=10**30\n"
                    "for i in range(n):\n"
                    " for j in range(i):ans=min(ans,abs(x[i]-x[j]))\n"
                    "print(ans)"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 8. Rolling Alert Counter ──────────────────────────────────────────────
    {
        "slug": "rolling_alert_count",
        "title": "Rolling Alert Counter",
        "topic": "Sliding Window",
        "difficulty": "Easy",
        "tags": ["sliding-window", "arrays", "counting"],
        "domains": ["devops", "backend"],
        "statement": (
            "A monitoring dashboard receives one alert severity value per minute. For every "
            "consecutive block of k minutes, count how many alerts have severity at least a "
            "chosen threshold. Return the largest such count among all blocks."
        ),
        "inputFormat": "Line 1 contains n, k, and threshold t. Line 2 contains n integer severity values.",
        "outputFormat": "Print the maximum number of values at least t in any consecutive block of exactly k values.",
        "constraints": "1 <= k <= n <= 200000. -10^9 <= t <= 10^9. Each severity value is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "7 3 5\n2 8 6 1 5 9 3\n",
                "output": "2",
                "explanation": "Blocks contain at most two values at least 5; for example, 8,6,1 has two.",
            },
            {
                "input": "5 5 10\n4 7 8 9 2\n",
                "output": "0",
                "explanation": "The only block contains no severity at least 10.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Keep the count of qualifying values in the current window and update it when one value leaves and another enters.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];x=a[3:3+n];"
            "c=sum(v>=t for v in x[:k]);ans=c\n"
            "for i in range(k,n):c+=x[i]>=t;c-=x[i-k]>=t;ans=max(ans,c)\n"
            "print(ans)"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];x=a[3:3+n];"
            "print(max(sum(v>=t for v in x[i:i+k]) for i in range(n-k+1)))"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,35));"
            "k=n if m=='edge' else r.randint(1,n);t=r.randint(-10,10);"
            "x=[r.randint(-15,15) for _ in range(n)];print(n,k,t);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];"
            "assert 1<=k<=n<=200000 and len(a)==n+3;assert -10**9<=t<=10**9 and all(-10**9<=x<=10**9 for x in a[3:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1 1 0\n0\n",
            "5 1 10\n10 9 11 2 10\n",
            "5 5 3\n3 3 3 3 3\n",
            "6 3 0\n-3 -2 -1 0 1 2\n",
            "7 4 5\n5 5 5 5 1 1 1\n",
            "4 2 -5\n-10 -9 -8 -7\n",
        ],
        "wrongSolutions": [
            {
                "name": "fixed_first_window",
                "description": "Counts only the first window.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];"
                    "print(sum(v>=t for v in a[3:3+k]))"
                ),
            },
            {
                "name": "minimum_count",
                "description": "Returns the smallest qualifying count rather than the largest.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];x=a[3:3+n];"
                    "print(min(sum(v>=t for v in x[i:i+k]) for i in range(n-k+1)))"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Recounts every window from scratch.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n,k,t=a[:3];x=a[3:3+n];"
                    "print(max(sum(v>=t for v in x[i:i+k]) for i in range(n-k+1)))"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 9. Service Elevator Route ─────────────────────────────────────────────
    {
        "slug": "elevator_floor_simulation",
        "title": "Service Elevator Route",
        "topic": "Simulation",
        "difficulty": "Easy",
        "tags": ["simulation", "arrays"],
        "domains": ["general", "backend"],
        "statement": (
            "A service elevator starts on floor 0. It receives a sequence of signed floor "
            "movements: a positive value moves upward and a negative value moves downward. "
            "The building has floors 0 through H, and every command is guaranteed to keep "
            "the elevator inside the building. Determine the final floor."
        ),
        "inputFormat": "Line 1 contains n and H. Line 2 contains n integer movements.",
        "outputFormat": "Print the final floor after applying all movements in order.",
        "constraints": "1 <= n <= 200000. 1 <= H <= 10^9. Each movement is an integer from -H to H. The prefix sum of movements is always between 0 and H.",
        "sampleTestCases": [
            {
                "input": "5 20\n4 7 -3 2 -5\n",
                "output": "5",
                "explanation": "Starting from 0, the floors are 4, 11, 8, 10, and finally 5.",
            },
            {
                "input": "4 10\n6 -2 -4 8\n",
                "output": "8",
                "explanation": "The elevator visits 6, 4, 0, then ends at 8.",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "The elevator state is completely determined by accumulating each movement in sequence.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];print(sum(a[2:2+n]))"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));n,H=a[:2];p=0\n"
            "for v in a[2:2+n]:p+=v\n"
            "print(p)"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));"
            "H=10**9 if m=='large' else r.randint(1,50);p=0;x=[]\n"
            "for _ in range(n):\n"
            " lo=-p;hi=H-p;v=r.randint(lo,hi);x.append(v);p+=v\n"
            "print(n,H);print(*x)"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));n,H=a[:2];x=a[2:];"
            "assert 1<=n<=200000 and 1<=H<=10**9 and len(x)==n;assert all(-H<=v<=H for v in x);"
            "p=0\n"
            " for v in x:p+=v;assert 0<=p<=H\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1 1\n0\n",
            "1 10\n10\n",
            "4 10\n10 -10 10 -10\n",
            "5 20\n0 0 0 0 0\n",
            "5 10\n3 3 -6 10 -10\n",
            "6 7\n7 -7 7 -7 7 -7\n",
        ],
        "wrongSolutions": [
            {
                "name": "absolute_movements",
                "description": "Adds absolute movement sizes instead of signed movements.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];"
                    "print(sum(abs(v) for v in a[2:2+n]))"
                ),
            },
            {
                "name": "last_command",
                "description": "Outputs only the final movement rather than the accumulated floor.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];print(a[1+n])"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Repeatedly recomputes the prefix sum from the beginning.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[2:2+n];p=0\n"
                    "for i in range(n):p=sum(x[:i+1])\n"
                    "print(p)"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },

    # ── 10. Control Panel Parity ──────────────────────────────────────────────
    {
        "slug": "binary_switch_parity",
        "title": "Control Panel Parity",
        "topic": "Math & Bit Manipulation",
        "difficulty": "Medium",
        "tags": ["bit-manipulation", "parity"],
        "domains": ["backend", "general"],
        "statement": (
            "A control panel represents its active switches as a non-negative integer. Each "
            "1-bit represents an active switch. The panel is balanced when it has an even "
            "number of active switches. Determine whether the supplied panel state is balanced."
        ),
        "inputFormat": "Line 1 contains an integer q, the number of panel states. Each of the next q lines contains one non-negative integer x.",
        "outputFormat": (
            "For each state, print YES if x has an even number of set bits in its binary "
            "representation; otherwise print NO. Print one answer per line."
        ),
        "constraints": "1 <= q <= 200000. 0 <= x < 2^60.",
        "sampleTestCases": [
            {
                "input": "4\n0\n3\n7\n10\n",
                "output": "YES\nYES\nNO\nYES",
                "explanation": "0 has 0 set bits (even→YES); 3=11b has 2 set bits (even→YES); 7=111b has 3 set bits (odd→NO); 10=1010b has 2 set bits (even→YES).",
            },
            {
                "input": "3\n1\n12\n15\n",
                "output": "NO\nYES\nYES",
                "explanation": "1 has 1 set bit (odd→NO); 12=1100 has 2 set bits (even→YES); 15=1111 has 4 set bits (even→YES).",
            },
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Repeatedly remove the lowest set bit with x &= x-1 and toggle parity.",
        "referenceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));q=a[0];out=[]\n"
            "for x in a[1:1+q]:\n"
            " p=0\n"
            " while x:x&=x-1;p^=1\n"
            " out.append('YES' if p==0 else 'NO')\n"
            "print('\\n'.join(out))"
        ),
        "bruteForceSolution": (
            "import sys\n"
            "a=list(map(int,sys.stdin.buffer.read().split()));q=a[0];"
            "print('\\n'.join('YES' if bin(x).count('1')%2==0 else 'NO' for x in a[1:1+q]))"
        ),
        "inputGenerator": (
            "import sys,random\n"
            "r=random.Random(int(sys.argv[1]));m=sys.argv[2];"
            "q=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));"
            "x=[r.randrange(1<<60) for _ in range(q)];print(q);print(*x,sep='\\n')"
        ),
        "inputValidator": (
            "import sys\n"
            "try:\n"
            " a=list(map(int,sys.stdin.buffer.read().split()));q=a[0];"
            "assert 1<=q<=200000 and len(a)==q+1;assert all(0<=x<2**60 for x in a[1:])\n"
            "except:sys.exit(1)\n"
            "sys.exit(0)"
        ),
        "edgeCaseInputs": [
            "1\n0\n",
            "1\n1\n",
            "1\n1152921504606846975\n",
            "4\n3\n3\n3\n3\n",
            "4\n1\n2\n4\n8\n",
            "3\n0\n7\n15\n",
        ],
        "wrongSolutions": [
            {
                "name": "odd_check",
                "description": "Checks whether the numeric value itself is even rather than whether its bit-count is even.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));"
                    "print('\\n'.join('YES' if x%2==0 else 'NO' for x in a[1:]))"
                ),
            },
            {
                "name": "lowest_bit_only",
                "description": "Uses only the lowest set bit and ignores the remaining bits.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));"
                    "print('\\n'.join('YES' if x==0 or (x&(x-1))==0 else 'NO' for x in a[1:]))"
                ),
            },
            {
                "name": "too_slow_but_correct",
                "description": "Converts every value to a binary string and scans it character by character; intentionally inefficient at scale.",
                "code": (
                    "import sys\n"
                    "a=list(map(int,sys.stdin.buffer.read().split()));out=[]\n"
                    "for x in a[1:]:\n"
                    " s=bin(x)[2:];c=0\n"
                    " for ch in s:c+=ch=='1'\n"
                    " out.append('YES' if c%2==0 else 'NO')\n"
                    "print('\\n'.join(out))"
                ),
            },
        ],
        "hiddenTestPlan": {"small": 5, "edge": "all edgeCaseInputs", "large": 4, "weightSmall": 40, "weightLarge": 60},
        "source": "original",
        "status": "draft",
    },
]
