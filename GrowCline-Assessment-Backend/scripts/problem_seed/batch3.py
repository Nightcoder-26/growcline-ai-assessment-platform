"""Batch 3 – User-Curated Problems."""
from typing import List, Dict, Any

BATCH3_PROBLEMS: List[Dict[str, Any]] = [
    {
        "slug": "warehouse_gap_marker",
        "title": "Warehouse Gap Marker",
        "topic": "Arrays & Hashing",
        "difficulty": "Easy",
        "tags": [
            "hashing",
            "arrays",
            "frequency-map"
        ],
        "domains": [
            "ecommerce",
            "data"
        ],
        "statement": "A warehouse scanner records integer shelf labels. Exactly one label from the expected range 1 through n is missing from the scan, while every other label in that range appears exactly once. Find the missing shelf label.",
        "inputFormat": "Line 1 contains n. Line 2 contains n-1 distinct integers from 1 through n.",
        "outputFormat": "Print the missing integer.",
        "constraints": "2 <= n <= 200000. Every value on the second line is an integer from 1 through n, and all listed values are distinct.",
        "sampleTestCases": [
            {
                "input": "5\n1 2 5 3\n",
                "output": "4",
                "explanation": "The labels 1, 2, 3, and 5 are present, so 4 is missing."
            },
            {
                "input": "6\n6 1 2 3 4\n",
                "output": "5",
                "explanation": "Every label except 5 appears."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Subtract the sum of the scanned labels from the arithmetic sum of 1 through n.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:];print(n*(n+1)//2-sum(x))",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=set(a[1:]);print(next(v for v in range(1,n+1) if v not in x))",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (2 if m=='edge' else r.randint(2,30));miss=r.randint(1,n);x=[v for v in range(1,n+1) if v!=miss];r.shuffle(x);print(n);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:];assert 2<=n<=200000 and len(x)==n-1;assert all(1<=v<=n for v in x) and len(set(x))==n-1\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "2\n1\n",
            "2\n2\n",
            "6\n2 3 4 5 6\n",
            "6\n1 2 3 4 5\n",
            "7\n7 6 5 4 3 1\n",
            "5\n1 2 3 5\n"
        ],
        "wrongSolutions": [
            {
                "name": "zero_based",
                "description": "Computes a missing value as if the expected labels were 0 through n-1.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];print((n-1)*n//2-sum(a[1:]))"
            },
            {
                "name": "max_label",
                "description": "Incorrectly assumes the missing label is always n.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));print(a[0])"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Searches the range and rebuilds a membership list for every candidate.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:]\nfor v in range(1,n+1):\n if v not in x:print(v);break"
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
        "slug": "sensor_name_compression",
        "title": "Sensor Name Compression",
        "topic": "Strings",
        "difficulty": "Easy",
        "tags": [
            "strings",
            "scanning",
            "run-length"
        ],
        "domains": [
            "devops",
            "data"
        ],
        "statement": "A sensor gateway receives a lowercase status string. Consecutive identical status letters are redundant, so the gateway keeps only the first letter of each consecutive run. Produce the resulting compressed status string.",
        "inputFormat": "Line 1 contains n. Line 2 contains a lowercase English string of exactly n characters.",
        "outputFormat": "Print the string obtained by replacing every maximal run of equal characters with one copy of that character.",
        "constraints": "1 <= n <= 200000. The string contains only lowercase English letters.",
        "sampleTestCases": [
            {
                "input": "11\naaabccddddab\n",
                "output": "abcdab",
                "explanation": "The runs are aaa, b, cc, dddd, a, b, so one character from each run remains."
            },
            {
                "input": "7\nzzzzzzz\n",
                "output": "z",
                "explanation": "All seven characters form one run."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Append a character only when it differs from the immediately preceding character.",
        "referenceSolution": "import sys\na=sys.stdin.read().split();s=a[1];out=[]\nfor c in s:\n if not out or out[-1]!=c:out.append(c)\nprint(''.join(out))",
        "bruteForceSolution": "import sys\na=sys.stdin.read().split();s=a[1];ans=''\nfor i,c in enumerate(s):\n if i==0 or s[i-1]!=c:ans+=c\nprint(ans)",
        "inputGenerator": "import sys,random,string\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,35));s=''.join(r.choice(string.ascii_lowercase) for _ in range(n));print(n);print(s)",
        "inputValidator": "import sys\ntry:\n a=sys.stdin.read().split();assert len(a)==2;n=int(a[0]);s=a[1];assert 1<=n<=200000 and len(s)==n and s.isalpha() and s.islower()\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\na\n",
            "7\nzzzzzzz\n",
            "6\nabcdef\n",
            "8\naabbccdd\n",
            "9\nabbbbaaaa\n",
            "5\nabcaa\n"
        ],
        "wrongSolutions": [
            {
                "name": "distinct_only",
                "description": "Keeps each letter only once globally instead of once per consecutive run.",
                "code": "import sys\na=sys.stdin.read().split();print(''.join(dict.fromkeys(a[1])))"
            },
            {
                "name": "last_of_run",
                "description": "Produces the same compression for ordinary runs, but incorrectly removes a character when a run starts after a repeated pattern.",
                "code": "import sys\na=sys.stdin.read().split();s=a[1];print(''.join(s[i] for i in range(len(s)) if i==len(s)-1 or s[i]!=s[i+1]))"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Repeatedly concatenates strings, causing excessive copying for very long inputs.",
                "code": "import sys\na=sys.stdin.read().split();s=a[1];ans=''\nfor i,c in enumerate(s):\n if i==0 or s[i-1]!=c:ans+=c\nprint(ans)"
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
        "slug": "battery_pair_balance",
        "title": "Battery Pair Balance",
        "topic": "Two Pointers",
        "difficulty": "Easy",
        "tags": [
            "two-pointers",
            "sorting",
            "pair-counting"
        ],
        "domains": [
            "general",
            "data"
        ],
        "statement": "A repair station has batteries with integer charge levels. Two batteries can be installed together when their combined charge is exactly target T. Each battery can be used in at most one installation. Find the maximum number of installations that can be formed.",
        "inputFormat": "Line 1 contains n and target T. Line 2 contains n integer charge levels.",
        "outputFormat": "Print the maximum number of disjoint pairs whose charge levels sum to T.",
        "constraints": "2 <= n <= 200000. 0 <= T <= 10^9. Each charge level is an integer from 0 to 10^9.",
        "sampleTestCases": [
            {
                "input": "7 10\n2 8 4 6 5 5 1\n",
                "output": "3",
                "explanation": "The pairs 2+8, 4+6, and 5+5 can be formed."
            },
            {
                "input": "5 7\n1 2 3 4 5\n",
                "output": "2",
                "explanation": "The pairs 2+5 and 3+4 are possible."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "After sorting, move inward when the two values sum to T, otherwise move the pointer whose value makes the sum too small or too large.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];x=sorted(a[2:2+n]);i,j=0,n-1;ans=0\nwhile i<j:\n s=x[i]+x[j]\n if s==T:ans+=1;i+=1;j-=1\n elif s<T:i+=1\n else:j-=1\nprint(ans)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];x=a[2:2+n];used=[False]*n;ans=0\nfor i in range(n):\n if used[i]:continue\n for j in range(i+1,n):\n  if not used[j] and x[i]+x[j]==T:used[i]=used[j]=True;ans+=1;break\nprint(ans)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (2 if m=='edge' else r.randint(2,30));T=r.randint(0,100) if m!='large' else 10**9;x=[r.randint(0,T) for _ in range(n)];print(n,T);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];assert 2<=n<=200000 and 0<=T<=10**9 and len(a)==n+2;assert all(0<=x<=10**9 for x in a[2:])\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "2 0\n0 0\n",
            "2 10\n0 10\n",
            "5 10\n5 5 5 5 5\n",
            "6 10\n1 2 8 9 1 8\n",
            "5 7\n1 2 3 4 5\n",
            "6 1000000000\n0 1000000000 1 999999999 2 3\n"
        ],
        "wrongSolutions": [
            {
                "name": "adjacent_only",
                "description": "Counts only adjacent pairs in the original input.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];x=a[2:2+n];print(sum(x[i]+x[i+1]==T for i in range(n-1)))"
            },
            {
                "name": "overlapping_pairs",
                "description": "Counts every value pair without consuming batteries, allowing one battery to be reused.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];x=a[2:2+n];print(sum(1 for i in range(n) for j in range(i+1,n) if x[i]+x[j]==T))"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Checks every possible pair and marks used batteries, which is quadratic.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,T=a[:2];x=a[2:2+n];used=[False]*n;ans=0\nfor i in range(n):\n if used[i]:continue\n for j in range(i+1,n):\n  if not used[j] and x[i]+x[j]==T:used[i]=used[j]=True;ans+=1;break\nprint(ans)"
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
        "slug": "rainfall_window_limit",
        "title": "Rainfall Window Limit",
        "topic": "Sliding Window",
        "difficulty": "Medium",
        "tags": [
            "sliding-window",
            "two-pointers",
            "prefix-sum"
        ],
        "domains": [
            "data",
            "general"
        ],
        "statement": "A weather station records non-negative rainfall amounts once per hour. Find the longest consecutive period whose total rainfall does not exceed a supplied limit L.",
        "inputFormat": "Line 1 contains n and L. Line 2 contains n non-negative integer rainfall amounts.",
        "outputFormat": "Print the maximum number of consecutive readings whose sum is at most L. If even one reading exceeds L, the answer may still be 0.",
        "constraints": "1 <= n <= 200000. 0 <= L <= 10^14. 0 <= each rainfall amount <= 10^9.",
        "sampleTestCases": [
            {
                "input": "7 10\n2 3 5 6 1 2 4\n",
                "output": "3",
                "explanation": "The period 1,2,4 has length 3 and sum 7; no length-4 period has sum at most 10."
            },
            {
                "input": "5 5\n8 1 2 7 1\n",
                "output": "2",
                "explanation": "The pair 1,2 fits the limit, while the 8 and 7 readings must stand alone and the final 7,1 exceeds the limit."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Because all readings are non-negative, expand the right endpoint and shrink the left endpoint whenever the window sum exceeds L.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];left=0;s=0;ans=0\nfor right,v in enumerate(x):\n s+=v\n while left<=right and s>L:s-=x[left];left+=1\n ans=max(ans,right-left+1)\nprint(ans)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];ans=0\nfor i in range(n):\n s=0\n for j in range(i,n):\n  s+=x[j]\n  if s<=L:ans=max(ans,j-i+1)\nprint(ans)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,35));L=r.randint(0,100) if m!='large' else 10**14;x=[r.randint(0,30) for _ in range(n)];print(n,L);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];assert 1<=n<=200000 and 0<=L<=10**14 and len(a)==n+2;assert all(0<=x<=10**9 for x in a[2:])\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1 0\n0\n",
            "1 5\n6\n",
            "5 5\n1 1 1 1 1\n",
            "6 0\n0 0 0 0 0 0\n",
            "7 10\n6 4 0 0 5 5 1\n",
            "5 3\n5 1 1 5 1\n"
        ],
        "wrongSolutions": [
            {
                "name": "negative_assumption",
                "description": "Uses a prefix-sum binary search strategy that relies on a broken monotonic update and misses zero-length windows.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];best=0\nfor i in range(n):\n s=0\n for j in range(i,n):\n  s+=x[j]\n  if s<=L:best=max(best,j-i+1)\n  else:break\nprint(best)"
            },
            {
                "name": "strict_limit",
                "description": "Treats a sum equal to L as invalid.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];l=0;s=0;ans=0\nfor r,v in enumerate(x):\n s+=v\n while l<=r and s>=L:s-=x[l];l+=1\n ans=max(ans,r-l+1)\nprint(ans)"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Enumerates every start and extends it until the limit is exceeded, which is quadratic in zero-heavy cases.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,L=a[:2];x=a[2:2+n];ans=0\nfor i in range(n):\n s=0\n for j in range(i,n):\n  s+=x[j]\n  if s<=L:ans=max(ans,j-i+1)\n  else:break\nprint(ans)"
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
        "slug": "undoable_counter",
        "title": "Undoable Counter",
        "topic": "Stack & Queue",
        "difficulty": "Easy",
        "tags": [
            "stack",
            "simulation"
        ],
        "domains": [
            "frontend",
            "general"
        ],
        "statement": "A dashboard counter starts at zero. An ADD x command increases it by x, while UNDO cancels the most recent ADD command that has not already been cancelled. UNDO is never issued when there is nothing to cancel. Print the final counter value.",
        "inputFormat": "Line 1 contains n. Each of the next n lines contains either \"ADD x\" where x is an integer, or \"UNDO\".",
        "outputFormat": "Print the final counter value.",
        "constraints": "1 <= n <= 200000. For every ADD command, -10^9 <= x <= 10^9. The accumulated counter and all intermediate sums fit in signed 64-bit range. UNDO is guaranteed valid.",
        "sampleTestCases": [
            {
                "input": "6\nADD 8\nADD -3\nUNDO\nADD 5\nUNDO\nADD 2\n",
                "output": "10",
                "explanation": "The active additions are 8 and 2, giving 10."
            },
            {
                "input": "5\nADD 4\nADD 7\nUNDO\nUNDO\nADD -2\n",
                "output": "-2",
                "explanation": "Both positive additions are cancelled before -2 is added."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Store active ADD values on a stack so UNDO can remove exactly the most recent uncancelled addition.",
        "referenceSolution": "import sys\na=sys.stdin.read().splitlines();n=int(a[0]);st=[];ans=0\nfor line in a[1:n+1]:\n p=line.split()\n if p[0]=='ADD':v=int(p[1]);st.append(v);ans+=v\n else:ans-=st.pop()\nprint(ans)",
        "bruteForceSolution": "import sys\na=sys.stdin.read().splitlines();n=int(a[0]);hist=[];active=[]\nfor line in a[1:n+1]:\n p=line.split()\n if p[0]=='ADD':active.append(int(p[1]))\n else:active.pop()\nprint(sum(active))",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));depth=0;lines=[]\nfor _ in range(n):\n if depth and r.random()<.35:lines.append('UNDO');depth-=1\n else:lines.append('ADD '+str(r.randint(-100,100)));depth+=1\nprint(n);print('\\n'.join(lines))",
        "inputValidator": "import sys\ntry:\n a=sys.stdin.read().splitlines();n=int(a[0]);assert 1<=n<=200000 and len(a)==n+1;d=0\n for line in a[1:]:\n  p=line.split();assert p[0] in ('ADD','UNDO')\n  if p[0]=='ADD':assert len(p)==2 and -10**9<=int(p[1])<=10**9;d+=1\n  else:assert len(p)==1 and d>0;d-=1\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\nADD 0\n",
            "2\nADD 5\nUNDO\n",
            "5\nADD 7\nADD 7\nUNDO\nUNDO\nADD -1\n",
            "6\nADD -5\nADD -4\nUNDO\nADD 10\nUNDO\nADD 3\n",
            "5\nADD 1000000000\nADD 1000000000\nUNDO\nADD -1000000000\nUNDO\n",
            "4\nADD 1\nUNDO\nADD 2\nUNDO\n"
        ],
        "wrongSolutions": [
            {
                "name": "undo_first",
                "description": "Cancels the oldest active ADD instead of the most recent one.",
                "code": "import sys\na=sys.stdin.read().splitlines();n=int(a[0]);q=[]\nfor line in a[1:]:\n p=line.split()\n if p[0]=='ADD':q.append(int(p[1]))\n else:q.pop(0)\nprint(sum(q))"
            },
            {
                "name": "undo_as_negative",
                "description": "Treats UNDO as subtracting the most recent value but keeps it available for a later UNDO.",
                "code": "import sys\na=sys.stdin.read().splitlines();n=int(a[0]);st=[];ans=0\nfor line in a[1:]:\n p=line.split()\n if p[0]=='ADD':st.append(int(p[1]));ans+=st[-1]\n else:ans-=st[-1]\nprint(ans)"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Recomputes the sum of the whole active stack after every command.",
                "code": "import sys\na=sys.stdin.read().splitlines();n=int(a[0]);st=[]\nfor line in a[1:]:\n p=line.split()\n if p[0]=='ADD':st.append(int(p[1]))\n else:st.pop()\n ans=sum(st)\nprint(ans)"
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
        "slug": "next_warmer_checkpoint",
        "title": "Next Warmer Checkpoint",
        "topic": "Stack & Queue",
        "difficulty": "Hard",
        "tags": [
            "monotonic-stack",
            "stack",
            "arrays"
        ],
        "domains": [
            "data",
            "general"
        ],
        "statement": "A route planner records the temperature at each checkpoint. For every checkpoint, find the distance to the nearest later checkpoint whose temperature is strictly higher. If no later checkpoint is warmer, output 0 for that checkpoint.",
        "inputFormat": "Line 1 contains n. Line 2 contains n integer temperatures.",
        "outputFormat": "Print n integers. The i-th value is the number of positions from i to the nearest later position with a strictly higher temperature, or 0 if none exists.",
        "constraints": "1 <= n <= 200000. Each temperature is an integer from -10^9 to 10^9.",
        "sampleTestCases": [
            {
                "input": "7\n18 20 19 21 17 22 22\n",
                "output": "1 2 1 2 1 0 0",
                "explanation": "From 18, the next warmer value is 20 one step away; from 20 it is 21 two steps away, and so on."
            },
            {
                "input": "5\n5 4 3 2 1\n",
                "output": "0 0 0 0 0",
                "explanation": "The temperatures never increase later in the sequence."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Maintain a decreasing stack of unresolved indices and resolve an index when a later temperature is strictly higher.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[0]*n;st=[]\nfor i,v in enumerate(x):\n while st and x[st[-1]]<v:\n  j=st.pop();ans[j]=i-j\n st.append(i)\nprint(*ans)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n d=0\n for j in range(i+1,n):\n  if x[j]>x[i]:d=j-i;break\n ans.append(d)\nprint(*ans)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));x=[r.randint(-20,20) for _ in range(n)];print(n);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];assert 1<=n<=200000 and len(a)==n+1;assert all(-10**9<=x<=10**9 for x in a[1:])\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n5\n",
            "5\n1 2 3 4 5\n",
            "5\n5 4 3 2 1\n",
            "6\n7 7 7 7 7 7\n",
            "7\n3 1 2 1 4 2 5\n",
            "6\n-5 -4 -6 -7 -2 -3\n"
        ],
        "wrongSolutions": [
            {
                "name": "greater_or_equal",
                "description": "Treats an equal temperature as warmer, violating the strict comparison.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n d=0\n for j in range(i+1,n):\n  if x[j]>=x[i]:d=j-i;break\n ans.append(d)\nprint(*ans)"
            },
            {
                "name": "next_only",
                "description": "Checks only the immediately following checkpoint.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];print(*[(1 if i+1<n and x[i+1]>x[i] else 0) for i in range(n)])"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Scans all later checkpoints for every position, giving quadratic worst-case time.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n d=0\n for j in range(i+1,n):\n  if x[j]>x[i]:d=j-i;break\n ans.append(d)\nprint(*ans)"
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
        "slug": "first_bad_build",
        "title": "First Failed Build",
        "topic": "Binary Search",
        "difficulty": "Easy",
        "tags": [
            "binary-search",
            "monotonic-condition"
        ],
        "domains": [
            "devops",
            "backend"
        ],
        "statement": "A deployment pipeline tests builds in increasing version order. Once a build fails, every later build also fails because the same regression remains. Given the pass/fail results, find the first failing build. If every build passes, print 0.",
        "inputFormat": "Line 1 contains n. Line 2 contains n integers, each either 0 or 1, where 0 means the build passed and 1 means it failed. The sequence is guaranteed to consist of zero or more 0s followed by one or more 1s, or all 0s.",
        "outputFormat": "Print the 1-based index of the first failing build, or 0 if all builds pass.",
        "constraints": "1 <= n <= 200000. Every value is 0 or 1, and the sequence is nondecreasing.",
        "sampleTestCases": [
            {
                "input": "8\n0 0 0 0 1 1 1 1\n",
                "output": "5",
                "explanation": "Build 5 is the first build marked as failed."
            },
            {
                "input": "5\n0 0 0 0 0\n",
                "output": "0",
                "explanation": "No build fails."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Binary search for the first position whose value is 1 in the monotone pass/fail sequence.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];l=0;r=n\nwhile l<r:\n m=(l+r)//2\n if x[m]:r=m\n else:l=m+1\nprint(l+1 if l<n else 0)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n]\nprint(next((i+1 for i,v in enumerate(x) if v),0))",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,35));p=0 if m=='edge' else r.randint(0,n);x=[0]*p+[1]*(n-p);print(n);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:];assert 1<=n<=200000 and len(x)==n;assert all(v in (0,1) for v in x);assert all(x[i]<=x[i+1] for i in range(n-1))\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n0\n",
            "1\n1\n",
            "6\n0 0 0 0 0 1\n",
            "6\n1 1 1 1 1 1\n",
            "5\n0 0 0 0 0\n",
            "7\n0 0 1 1 1 1 1\n"
        ],
        "wrongSolutions": [
            {
                "name": "last_failure",
                "description": "Returns the last failing build instead of the first.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];print(n-x[::-1].index(1) if 1 in x else 0)"
            },
            {
                "name": "zero_based",
                "description": "Outputs the zero-based position of the first failure.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));x=a[1:];print(x.index(1) if 1 in x else 0)"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Linearly scans all builds, which is correct but intentionally does not use the required logarithmic search.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];print(next((i+1 for i,v in enumerate(x) if v),0))"
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
        "slug": "minimum_capacity_route",
        "title": "Minimum Route Capacity",
        "topic": "Binary Search",
        "difficulty": "Medium",
        "tags": [
            "binary-search",
            "greedy-check",
            "arrays"
        ],
        "domains": [
            "logistics",
            "ecommerce"
        ],
        "statement": "A delivery van must carry packages in their given order. It can make at most d trips, and each trip has one fixed capacity C. Find the smallest capacity that allows every package to be delivered within d trips.",
        "inputFormat": "Line 1 contains n and d. Line 2 contains n positive integer package weights in delivery order.",
        "outputFormat": "Print the minimum possible trip capacity.",
        "constraints": "1 <= d <= n <= 200000. 1 <= each package weight <= 10^9. The total weight fits in signed 64-bit range.",
        "sampleTestCases": [
            {
                "input": "5 3\n4 2 7 3 5\n",
                "output": "9",
                "explanation": "Capacity 9 permits trips [4,2,3], [7], and [5]; capacity 8 cannot complete the route in three trips."
            },
            {
                "input": "6 2\n5 5 4 4 3 3\n",
                "output": "14",
                "explanation": "The first three packages total 14 and the last three total 10, so 14 is feasible."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Binary-search the capacity and greedily pack consecutive packages until adding another would exceed it.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];x=a[2:2+n]\ndef ok(c):\n trips=1;s=0\n for v in x:\n  if s+v>c:trips+=1;s=v\n  else:s+=v\n return trips<=d\nl=max(x);r=sum(x)\nwhile l<r:\n m=(l+r)//2\n if ok(m):r=m\n else:l=m+1\nprint(l)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];x=a[2:2+n]\nfor c in range(max(x),sum(x)+1):\n trips=1;s=0\n for v in x:\n  if s+v>c:trips+=1;s=v\n  else:s+=v\n if trips<=d:print(c);break",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,25));d=1 if m=='edge' else r.randint(1,n);x=[r.randint(1,100) for _ in range(n)];print(n,d);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];x=a[2:];assert 1<=d<=n<=200000 and len(x)==n;assert all(1<=v<=10**9 for v in x)\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1 1\n7\n",
            "5 1\n1 2 3 4 5\n",
            "5 5\n1 2 3 4 5\n",
            "6 3\n10 10 10 10 10 10\n",
            "7 3\n4 2 7 3 5 1 6\n",
            "4 2\n1000000000 1 1 1000000000\n"
        ],
        "wrongSolutions": [
            {
                "name": "average_capacity",
                "description": "Uses total weight divided by the number of trips without respecting package boundaries or the largest package.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];print((sum(a[2:])+d-1)//d)"
            },
            {
                "name": "allow_reordering",
                "description": "Sorts packages, which changes the required delivery order.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];x=sorted(a[2:]);lo=max(x);hi=sum(x)\ndef ok(c):\n t=1;s=0\n for v in x:\n  if s+v>c:t+=1;s=v\n  else:s+=v\n return t<=d\nwhile lo<hi:\n m=(lo+hi)//2\n if ok(m):hi=m\n else:lo=m+1\nprint(lo)"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Tests every integer capacity between the minimum package and total weight.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,d=a[:2];x=a[2:]\nfor c in range(max(x),sum(x)+1):\n t=1;s=0\n for v in x:\n  if s+v>c:t+=1;s=v\n  else:s+=v\n if t<=d:print(c);break"
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
        "slug": "largest_safe_batch",
        "title": "Largest Safe Batch",
        "topic": "Binary Search",
        "difficulty": "Hard",
        "tags": [
            "binary-search",
            "feasibility",
            "integer-search"
        ],
        "domains": [
            "ecommerce",
            "backend"
        ],
        "statement": "An order-processing service has n queues, with a known number of orders already waiting in each queue. It wants to process exactly one batch size B for every queue, using as many complete batches as possible. A batch consumes B orders from one queue. Given a required minimum total of m batches, find the largest B for which the queues can collectively provide at least m complete batches.",
        "inputFormat": "Line 1 contains n and m. Line 2 contains n non-negative integers representing orders waiting in each queue.",
        "outputFormat": "Print the largest positive integer B for which the sum of floor(queue[i] / B) over all queues is at least m. If even B = 1 cannot produce m batches, print 0.",
        "constraints": "1 <= n <= 200000. 1 <= m <= 10^14. 0 <= queue[i] <= 10^9. The total number of orders is at most 2*10^14.",
        "sampleTestCases": [
            {
                "input": "4 7\n20 14 9 7\n",
                "output": "6",
                "explanation": "At B=6 the queues provide 3+2+1+1 = 7 batches. At B=7 they provide only 2+2+1+1 = 6."
            },
            {
                "input": "3 10\n3 3 3\n",
                "output": "0",
                "explanation": "Even B=1 produces only 9 complete batches, so no positive batch size satisfies the requirement."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "The number of obtainable batches decreases monotonically as B grows, so binary-search the largest feasible batch size.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:2+n]\ndef ok(b):\n return sum(v//b for v in x)>=m\nif sum(x)<m:print(0);sys.exit()\nl=1;r=max(x)\nwhile l<r:\n mid=(l+r+1)//2\n if ok(mid):l=mid\n else:r=mid-1\nprint(l)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:2+n]\nfor b in range(max(x),0,-1):\n if sum(v//b for v in x)>=m:print(b);break\nelse:print(0)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,18));x=[r.randint(0,100) for _ in range(n)];total=sum(x);need=total+1 if m=='edge' else r.randint(1,max(1,total));print(n,need);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:];assert 1<=n<=200000 and 1<=m<=10**14 and len(x)==n;assert all(0<=v<=10**9 for v in x);assert sum(x)<=2*10**14\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1 1\n1\n",
            "1 2\n1\n",
            "4 7\n20 14 9 7\n",
            "3 10\n3 3 3\n",
            "5 1\n0 0 0 0 100\n",
            "6 6\n6 6 6 6 6 6\n"
        ],
        "wrongSolutions": [
            {
                "name": "average_guess",
                "description": "Uses total orders divided by the required batch count, which ignores the per-queue floor operation.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:2+n];print(sum(x)//m if sum(x)>=m else 0)"
            },
            {
                "name": "lower_bound_variant",
                "description": "Binary-searches for the smallest feasible size rather than the largest.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:2+n]\nif sum(x)<m:print(0);sys.exit()\nl,r=1,max(x)\nwhile l<r:\n q=(l+r)//2\n if sum(v//q for v in x)>=m:r=q\n else:l=q+1\nprint(l)"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Tests every possible batch size from the maximum down to one.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,m=a[:2];x=a[2:2+n]\nfor b in range(max(x),0,-1):\n if sum(v//b for v in x)>=m:print(b);break\nelse:print(0)"
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
        "slug": "bitwise_range_signature",
        "title": "Bitwise Range Signature",
        "topic": "Math & Bit Manipulation",
        "difficulty": "Easy",
        "tags": [
            "bit-manipulation",
            "xor",
            "prefix-pattern"
        ],
        "domains": [
            "backend",
            "general"
        ],
        "statement": "A diagnostic tool assigns each integer its binary switch pattern. For a query interval [L,R], it combines all integers in the interval using bitwise XOR. Compute the resulting signature for every query.",
        "inputFormat": "Line 1 contains q. Each of the next q lines contains two integers L and R with 0 <= L <= R.",
        "outputFormat": "For each query, print the bitwise XOR of all integers from L through R, one answer per line.",
        "constraints": "1 <= q <= 200000. 0 <= L <= R <= 10^18.",
        "sampleTestCases": [
            {
                "input": "3\n0 3\n5 5\n2 6\n",
                "output": "0\n5\n1",
                "explanation": "0^1^2^3 is 0, the single value 5 gives 5, and 2^3^4^5^6 is 1."
            },
            {
                "input": "2\n1 4\n10 13\n",
                "output": "4\n0",
                "explanation": "1^2^3^4 equals 4, while 10^11^12^13 equals 0."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Use the repeating XOR prefix pattern of 0 through n, where the result depends only on n modulo 4.",
        "referenceSolution": "import sys\ndef px(n):\n if n<0:return 0\n r=n%4\n return [n,1,n+1,0][r]\na=list(map(int,sys.stdin.buffer.read().split()));q=a[0];out=[]\nfor i in range(q):\n l,r=a[1+2*i:3+2*i];out.append(str(px(r)^px(l-1)))\nprint('\\n'.join(out))",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));q=a[0];out=[]\nfor i in range(q):\n l,r=a[1+2*i:3+2*i];v=0\n for x in range(l,r+1):v^=x\n out.append(str(v))\nprint('\\n'.join(out))",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];q=200000 if m=='large' else (1 if m=='edge' else r.randint(1,25));print(q)\nfor _ in range(q):\n if m=='edge':l=0;rng=0\n else:l=r.randint(0,10**6);rng=r.randint(l,l+100)\n print(l,rng)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));q=a[0];assert 1<=q<=200000 and len(a)==1+2*q\n for i in range(q):\n  l,r=a[1+2*i:3+2*i];assert 0<=l<=r<=10**18\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n0 0\n",
            "1\n0 3\n",
            "1\n0 1000000000000000000\n",
            "3\n1 1\n2 2\n3 3\n",
            "4\n0 4\n4 7\n8 11\n12 15\n",
            "2\n999999999999999999 1000000000000000000\n"
        ],
        "wrongSolutions": [
            {
                "name": "sum_range",
                "description": "Uses arithmetic addition instead of bitwise XOR.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));q=a[0]\nfor i in range(q):\n l,r=a[1+2*i:3+2*i];print((l+r)*(r-l+1)//2)"
            },
            {
                "name": "wrong_cycle",
                "description": "Uses an incorrect period table for the XOR prefix.",
                "code": "import sys\ndef p(n):\n if n<0:return 0\n return [0,n,n+1,1][n%4]\na=list(map(int,sys.stdin.buffer.read().split()));q=a[0]\nfor i in range(q):\n l,r=a[1+2*i:3+2*i];print(p(r)^p(l-1))"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Loops through every integer in every query interval.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));q=a[0]\nfor i in range(q):\n l,r=a[1+2*i:3+2*i];v=0\n for x in range(l,r+1):v^=x\n print(v)"
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
        "slug": "deadline_slot_sort",
        "title": "Deadline Slot Planner",
        "topic": "Sorting & Intervals",
        "difficulty": "Medium",
        "tags": [
            "sorting",
            "greedy",
            "scheduling"
        ],
        "domains": [
            "backend",
            "general"
        ],
        "statement": "A studio has one machine and a collection of jobs. Each job takes exactly one unit of time and must be completed no later than its integer deadline to earn its reward. Choose jobs to maximize the total reward.",
        "inputFormat": "Line 1 contains n. Each of the next n lines contains two integers deadline and reward for one job.",
        "outputFormat": "Print the maximum total reward obtainable.",
        "constraints": "1 <= n <= 200000. 1 <= deadline <= 200000. 0 <= reward <= 10^9.",
        "sampleTestCases": [
            {
                "input": "5\n2 50\n1 20\n2 40\n3 70\n1 10\n",
                "output": "160",
                "explanation": "Jobs with rewards 20, 40, and 70 can be scheduled by deadlines 1, 2, and 3, giving 130; instead choosing 50, 40, and 70 gives 160."
            },
            {
                "input": "4\n1 10\n1 50\n1 30\n2 20\n",
                "output": "70",
                "explanation": "Only one job can use slot 1, so reward 50 is selected there, followed by reward 20 at slot 2."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Process jobs by deadline and keep the highest rewards that fit into the available deadline slots using a min-heap.",
        "referenceSolution": "import sys,heapq\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];jobs=[(a[1+2*i],a[2+2*i]) for i in range(n)];jobs.sort();h=[]\nfor d,r in jobs:\n heapq.heappush(h,r)\n if len(h)>d:heapq.heappop(h)\nprint(sum(h))",
        "bruteForceSolution": "import sys\n# Exact subset enumeration for small stress tests.\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];jobs=[(a[1+2*i],a[2+2*i]) for i in range(n)];best=0\nfor mask in range(1<<n):\n chosen=[jobs[i] for i in range(n) if mask>>i&1]\n chosen.sort()\n if all(i+1<=d for i,(d,_) in enumerate(chosen)):best=max(best,sum(r for _,r in chosen))\nprint(best)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,18));lines=[]\nfor _ in range(n):lines.append((r.randint(1,n),r.randint(0,100)))\nprint(n);print('\\n'.join(f'{d} {v}' for d,v in lines))",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];assert 1<=n<=200000 and len(a)==1+2*n\n for i in range(n):\n  d,r=a[1+2*i:3+2*i];assert 1<=d<=200000 and 0<=r<=10**9\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n1 5\n",
            "3\n1 10\n1 20\n1 30\n",
            "4\n1 5\n2 6\n3 7\n4 8\n",
            "5\n5 1\n5 2\n5 3\n5 4\n5 5\n",
            "6\n1 100\n2 1\n2 90\n3 2\n3 80\n1 70\n",
            "4\n1 0\n1 0\n2 0\n3 0\n"
        ],
        "wrongSolutions": [
            {
                "name": "highest_rewards",
                "description": "Chooses the largest rewards without respecting deadlines.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];r=sorted((a[2+2*i] for i in range(n)),reverse=True);print(sum(r[:n]))"
            },
            {
                "name": "deadline_sum",
                "description": "Treats all jobs whose deadlines are feasible as independently schedulable.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];print(sum(a[2+2*i] for i in range(n)))"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Enumerates every subset of jobs and is exponential.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];jobs=[(a[1+2*i],a[2+2*i]) for i in range(n)];best=0\nfor mask in range(1<<n):\n c=[jobs[i] for i in range(n) if mask>>i&1];c.sort()\n if all(i+1<=d for i,(d,_) in enumerate(c)):best=max(best,sum(r for _,r in c))\nprint(best)"
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
        "slug": "bounded_inventory_delta",
        "title": "Bounded Inventory Delta",
        "topic": "Binary Search",
        "difficulty": "Medium",
        "tags": [
            "binary-search",
            "prefix-sum",
            "feasibility"
        ],
        "domains": [
            "ecommerce",
            "data"
        ],
        "statement": "A store records daily inventory changes as integers: positive values are received units and negative values are sold units. For a chosen starting stock S, the stock after every day must stay at least zero. Find the smallest starting stock that makes the entire recorded sequence valid.",
        "inputFormat": "Line 1 contains n. Line 2 contains n integer daily inventory changes.",
        "outputFormat": "Print the smallest non-negative starting stock that keeps the stock non-negative after every day.",
        "constraints": "1 <= n <= 200000. -10^9 <= each change <= 10^9. The answer fits in signed 64-bit range.",
        "sampleTestCases": [
            {
                "input": "6\n-4 3 -7 2 -1 5\n",
                "output": "8",
                "explanation": "The cumulative changes reach a minimum of -8, so starting with 8 is necessary and sufficient."
            },
            {
                "input": "5\n3 -1 2 -2 4\n",
                "output": "0",
                "explanation": "The running stock never falls below zero when starting from zero."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "The required starting stock is the negation of the minimum prefix sum whenever that minimum is negative.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];s=0;mn=0\nfor v in a[1:1+n]:s+=v;mn=min(mn,s)\nprint(-mn)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n]\nfor start in range(0,sum(-v for v in x if v<0)+1):\n s=start\n if all((s:=s+v)>=0 for v in x):print(start);break",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));x=[r.randint(-100,100) for _ in range(n)];print(n);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];assert 1<=n<=200000 and len(a)==n+1;assert all(-10**9<=x<=10**9 for x in a[1:])\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n0\n",
            "1\n-1000000000\n",
            "5\n1 1 1 1 1\n",
            "5\n-1 -2 -3 -4 -5\n",
            "6\n5 -10 2 3 -4 1\n",
            "7\n-3 5 -2 -10 8 1 -1\n"
        ],
        "wrongSolutions": [
            {
                "name": "total_negative",
                "description": "Adds all negative changes instead of finding the worst cumulative prefix.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));print(-sum(v for v in a[1:] if v<0))"
            },
            {
                "name": "minimum_element",
                "description": "Uses only the most negative individual day instead of the minimum prefix sum.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));print(max(0,-min(a[1:])))"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Tries starting stocks one by one until a valid one is found, which can require a huge number of trials.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n]\nfor st in range(sum(-v for v in x if v<0)+1):\n s=st\n ok=True\n for v in x:\n  s+=v\n  if s<0:ok=False;break\n if ok:print(st);break"
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
        "slug": "weighted_task_cutoff",
        "title": "Weighted Task Cutoff",
        "topic": "Stack & Queue",
        "difficulty": "Hard",
        "tags": [
            "monotonic-stack",
            "stack",
            "weighted-events"
        ],
        "domains": [
            "backend",
            "data"
        ],
        "statement": "A workflow contains tasks with integer effort values in sequence. For each task, determine how many consecutive tasks immediately after it can be included before encountering the first later task whose effort is strictly smaller. If no smaller task appears later, use the distance to the end of the sequence.",
        "inputFormat": "Line 1 contains n. Line 2 contains n positive integer effort values.",
        "outputFormat": "Print n integers. For position i, print the number of consecutive positions starting at i and ending immediately before the first later position with a strictly smaller effort. If there is no smaller later value, print n-i+1.",
        "constraints": "1 <= n <= 200000. 1 <= each effort value <= 10^9.",
        "sampleTestCases": [
            {
                "input": "7\n5 5 7 6 8 4 4\n",
                "output": "5 4 1 1 1 2 1",
                "explanation": "For the first task, the first smaller effort is 4 at position 6, so five positions from 1 through 5 are included. Equal values do not stop the range."
            },
            {
                "input": "5\n1 2 3 4 5\n",
                "output": "5 4 3 2 1",
                "explanation": "No later effort is smaller than any task, so each task extends to the end."
            }
        ],
        "checker": "exact",
        "timeLimit": 2.0,
        "memoryLimit": 256,
        "coreIdea": "Scan from right to left with a monotonic increasing stack to find the nearest strictly smaller later value for every position.",
        "referenceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[0]*n;st=[]\nfor i in range(n-1,-1,-1):\n while st and x[st[-1]]>=x[i]:st.pop()\n ans[i]=(st[-1]-i) if st else (n-i)\n st.append(i)\nprint(*ans)",
        "bruteForceSolution": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n j=i+1\n while j<n and x[j]>=x[i]:j+=1\n ans.append(j-i)\nprint(*ans)",
        "inputGenerator": "import sys,random\nr=random.Random(int(sys.argv[1]));m=sys.argv[2];n=200000 if m=='large' else (1 if m=='edge' else r.randint(1,30));x=[r.randint(1,20) for _ in range(n)];print(n);print(*x)",
        "inputValidator": "import sys\ntry:\n a=list(map(int,sys.stdin.buffer.read().split()));n=a[0];assert 1<=n<=200000 and len(a)==n+1;assert all(1<=x<=10**9 for x in a[1:])\nexcept:sys.exit(1)\nsys.exit(0)",
        "edgeCaseInputs": [
            "1\n5\n",
            "5\n1 2 3 4 5\n",
            "5\n5 4 3 2 1\n",
            "6\n7 7 7 7 7 7\n",
            "7\n5 5 7 6 8 4 4\n",
            "6\n10 1 10 1 10 1\n"
        ],
        "wrongSolutions": [
            {
                "name": "equal_stops",
                "description": "Treats an equal effort as a stopping point even though only strictly smaller values should stop the range.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n j=i+1\n while j<n and x[j]>x[i]:j+=1\n ans.append(j-i)\nprint(*ans)"
            },
            {
                "name": "next_smaller_only",
                "description": "Checks only the immediately following task instead of searching for the first later smaller task.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];print(*[1 if i==n-1 or x[i+1]<x[i] else n-i for i in range(n)])"
            },
            {
                "name": "too_slow_but_correct",
                "description": "Scans forward independently for every task, creating quadratic worst-case behavior.",
                "code": "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n=a[0];x=a[1:1+n];ans=[]\nfor i in range(n):\n j=i+1\n while j<n and x[j]>=x[i]:j+=1\n ans.append(j-i)\nprint(*ans)"
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
