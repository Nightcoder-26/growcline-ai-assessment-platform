"""
Fixes and populates sampleTestCases and hiddenTestCases for all questions in `coding_questions`.
Ensures active assessments (like Anirudh's) have working sample and hidden test cases.
"""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.database import Database

# Comprehensive test case dictionary for all 39 classic questions
CLASSIC_TEST_CASES = {
    "Valid Parentheses String": {
        "sample": [
            {"input": "()[]{}\n", "output": "true", "explanation": "All brackets match and close properly."},
            {"input": "(]\n", "output": "false", "explanation": "Mismatched bracket types."},
            {"input": "([)]\n", "output": "false", "explanation": "Incorrect closing order."},
        ],
        "hidden": [
            {"input": "{[]}\n", "output": "true"},
            {"input": "(\n", "output": "false"},
            {"input": ")\n", "output": "false"},
            {"input": "(([]){})\n", "output": "true"},
            {"input": "()()\n", "output": "true"},
        ],
        "checker": "exact",
    },
    "Two Sum Target": {
        "sample": [
            {"input": "2 7 11 15\n9\n", "output": "0 1", "explanation": "nums[0] + nums[1] = 2 + 7 = 9."},
            {"input": "3 2 4\n6\n", "output": "1 2", "explanation": "nums[1] + nums[2] = 2 + 4 = 6."},
        ],
        "hidden": [
            {"input": "3 3\n6\n", "output": "0 1"},
            {"input": "1 5 8 12\n13\n", "output": "0 3"},
            {"input": "-3 4 3 90\n0\n", "output": "0 2"},
        ],
        "checker": "exact",
    },
    "Two Sum": {
        "sample": [
            {"input": "2 7 11 15\n9\n", "output": "0 1"},
            {"input": "3 2 4\n6\n", "output": "1 2"},
        ],
        "hidden": [
            {"input": "3 3\n6\n", "output": "0 1"},
            {"input": "1 2 3 4 5\n9\n", "output": "3 4"},
        ],
        "checker": "exact",
    },
    "Contains Duplicate Check": {
        "sample": [
            {"input": "1 2 3 1\n", "output": "true"},
            {"input": "1 2 3 4\n", "output": "false"},
        ],
        "hidden": [
            {"input": "1 1 1 3 3 4 3 2 4 2\n", "output": "true"},
            {"input": "42\n", "output": "false"},
            {"input": "-1 -2 -3 -1\n", "output": "true"},
        ],
        "checker": "exact",
    },
    "Valid Anagram Check": {
        "sample": [
            {"input": "anagram\nnagaram\n", "output": "true"},
            {"input": "rat\ncar\n", "output": "false"},
        ],
        "hidden": [
            {"input": "a\na\n", "output": "true"},
            {"input": "ab\na\n", "output": "false"},
            {"input": "listen\nsilent\n", "output": "true"},
        ],
        "checker": "exact",
    },
    "Reverse Words in String": {
        "sample": [
            {"input": "the sky is blue\n", "output": "blue is sky the"},
            {"input": "  hello world  \n", "output": "world hello"},
        ],
        "hidden": [
            {"input": "a good   example\n", "output": "example good a"},
            {"input": "word\n", "output": "word"},
        ],
        "checker": "exact",
    },
    "Palindrome Substring Longest": {
        "sample": [
            {"input": "babad\n", "output": "bab"},
            {"input": "cbbd\n", "output": "bb"},
        ],
        "hidden": [
            {"input": "a\n", "output": "a"},
            {"input": "ac\n", "output": "a"},
            {"input": "racecar\n", "output": "racecar"},
        ],
        "checker": "exact",
    },
    "Longest Substring Without Repeating": {
        "sample": [
            {"input": "abcabcbb\n", "output": "3"},
            {"input": "bbbbb\n", "output": "1"},
        ],
        "hidden": [
            {"input": "pwwkew\n", "output": "3"},
            {"input": " \n", "output": "1"},
            {"input": "au\n", "output": "2"},
        ],
        "checker": "exact",
    },
    "Longest Substring Without Repeating Characters": {
        "sample": [
            {"input": "abcabcbb\n", "output": "3"},
            {"input": "bbbbb\n", "output": "1"},
        ],
        "hidden": [
            {"input": "pwwkew\n", "output": "3"},
            {"input": "dvdf\n", "output": "3"},
        ],
        "checker": "exact",
    },
    "Minimum Window Substring": {
        "sample": [
            {"input": "ADOBECODEBANC\nABC\n", "output": "BANC"},
            {"input": "a\na\n", "output": "a"},
        ],
        "hidden": [
            {"input": "a\naa\n", "output": ""},
            {"input": "ab\nb\n", "output": "b"},
        ],
        "checker": "exact",
    },
    "Container With Most Water": {
        "sample": [
            {"input": "1 8 6 2 5 4 8 3 7\n", "output": "49"},
            {"input": "1 1\n", "output": "1"},
        ],
        "hidden": [
            {"input": "4 3 2 1 4\n", "output": "16"},
            {"input": "1 2 1\n", "output": "2"},
        ],
        "checker": "exact",
    },
    "3Sum Zero Triplets": {
        "sample": [
            {"input": "-1 0 1 2 -1 -4\n", "output": "-1 -1 2\n-1 0 1"},
            {"input": "0 1 1\n", "output": ""},
        ],
        "hidden": [
            {"input": "0 0 0\n", "output": "0 0 0"},
        ],
        "checker": "exact",
    },
    "Trapping Rain Water": {
        "sample": [
            {"input": "0 1 0 2 1 0 1 3 2 1 2 1\n", "output": "6"},
            {"input": "4 2 0 3 2 5\n", "output": "9"},
        ],
        "hidden": [
            {"input": "0 0 0\n", "output": "0"},
            {"input": "3 0 0 2 0 4\n", "output": "10"},
        ],
        "checker": "exact",
    },
    "Binary Search in Rotated Array": {
        "sample": [
            {"input": "4 5 6 7 0 1 2\n0\n", "output": "4"},
            {"input": "4 5 6 7 0 1 2\n3\n", "output": "-1"},
        ],
        "hidden": [
            {"input": "1\n0\n", "output": "-1"},
            {"input": "1\n1\n", "output": "0"},
            {"input": "3 1\n1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Binary Search in Rotated Sorted Array": {
        "sample": [
            {"input": "4 5 6 7 0 1 2\n0\n", "output": "4"},
            {"input": "4 5 6 7 0 1 2\n3\n", "output": "-1"},
        ],
        "hidden": [
            {"input": "1\n0\n", "output": "-1"},
            {"input": "3 1\n1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Find Minimum in Rotated Array": {
        "sample": [
            {"input": "3 4 5 1 2\n", "output": "1"},
            {"input": "4 5 6 7 0 1 2\n", "output": "0"},
        ],
        "hidden": [
            {"input": "11 13 15 17\n", "output": "11"},
            {"input": "2 1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Median of Two Sorted Arrays": {
        "sample": [
            {"input": "1 3\n2\n", "output": "2.0"},
            {"input": "1 2\n3 4\n", "output": "2.5"},
        ],
        "hidden": [
            {"input": "0 0\n0 0\n", "output": "0.0"},
            {"input": "\n1\n", "output": "1.0"},
        ],
        "checker": "exact",
    },
    "Daily Temperatures Next Warmer": {
        "sample": [
            {"input": "73 74 75 71 69 72 76 73\n", "output": "1 1 4 2 1 1 0 0"},
            {"input": "30 40 50 60\n", "output": "1 1 1 0"},
        ],
        "hidden": [
            {"input": "30 60 90\n", "output": "1 1 0"},
            {"input": "50\n", "output": "0"},
        ],
        "checker": "exact",
    },
    "Largest Rectangle in Histogram": {
        "sample": [
            {"input": "2 1 5 6 2 3\n", "output": "10"},
            {"input": "2 4\n", "output": "4"},
        ],
        "hidden": [
            {"input": "1\n", "output": "1"},
            {"input": "0 9\n", "output": "9"},
        ],
        "checker": "exact",
    },
    "Merge Two Sorted Linked Lists": {
        "sample": [
            {"input": "1 2 4\n1 3 4\n", "output": "1 1 2 3 4 4"},
            {"input": "\n0\n", "output": "0"},
        ],
        "hidden": [
            {"input": "\n\n", "output": ""},
            {"input": "2 5 7\n1 3 4 6 8\n", "output": "1 2 3 4 5 6 7 8"},
        ],
        "checker": "exact",
    },
    "Reverse Linked List": {
        "sample": [
            {"input": "1 2 3 4 5\n", "output": "5 4 3 2 1"},
            {"input": "1 2\n", "output": "2 1"},
        ],
        "hidden": [
            {"input": "\n", "output": ""},
            {"input": "42\n", "output": "42"},
        ],
        "checker": "exact",
    },
    "Detect Cycle in Linked List": {
        "sample": [
            {"input": "3 2 0 -4\n1\n", "output": "true"},
            {"input": "1 2\n0\n", "output": "true"},
        ],
        "hidden": [
            {"input": "1\n-1\n", "output": "false"},
        ],
        "checker": "exact",
    },
    "Find Middle of Linked List": {
        "sample": [
            {"input": "1 2 3 4 5\n", "output": "3 4 5"},
            {"input": "1 2 3 4 5 6\n", "output": "4 5 6"},
        ],
        "hidden": [
            {"input": "1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Invert Binary Tree": {
        "sample": [
            {"input": "4 2 7 1 3 6 9\n", "output": "4 7 2 9 6 3 1"},
            {"input": "2 1 3\n", "output": "2 3 1"},
        ],
        "hidden": [
            {"input": "\n", "output": ""},
        ],
        "checker": "exact",
    },
    "Validate Binary Search Tree": {
        "sample": [
            {"input": "2 1 3\n", "output": "true"},
            {"input": "5 1 4 null null 3 6\n", "output": "false"},
        ],
        "hidden": [
            {"input": "1\n", "output": "true"},
        ],
        "checker": "exact",
    },
    "Lowest Common Ancestor BST": {
        "sample": [
            {"input": "6 2 8 0 4 7 9\n2 8\n", "output": "6"},
            {"input": "6 2 8 0 4 7 9\n2 4\n", "output": "2"},
        ],
        "hidden": [
            {"input": "2 1\n2 1\n", "output": "2"},
        ],
        "checker": "exact",
    },
    "Lowest Common Ancestor in Binary Tree": {
        "sample": [
            {"input": "3 5 1 6 2 0 8 null null 7 4\n5 1\n", "output": "3"},
            {"input": "3 5 1 6 2 0 8 null null 7 4\n5 4\n", "output": "5"},
        ],
        "hidden": [
            {"input": "1 2\n1 2\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Number of Islands Grid": {
        "sample": [
            {"input": "1 1 0 0\n1 1 0 0\n0 0 1 0\n0 0 0 1\n", "output": "3"},
            {"input": "1 1 1\n0 1 0\n1 1 1\n", "output": "1"},
        ],
        "hidden": [
            {"input": "0 0\n0 0\n", "output": "0"},
            {"input": "1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Clone Graph Deep Copy": {
        "sample": [
            {"input": "[[2,4],[1,3],[2,4],[1,3]]\n", "output": "[[2,4],[1,3],[2,4],[1,3]]"},
        ],
        "hidden": [
            {"input": "[[]]\n", "output": "[[]]"},
        ],
        "checker": "exact",
    },
    "Climbing Stairs Count Ways": {
        "sample": [
            {"input": "2\n", "output": "2"},
            {"input": "3\n", "output": "3"},
        ],
        "hidden": [
            {"input": "4\n", "output": "5"},
            {"input": "5\n", "output": "8"},
            {"input": "10\n", "output": "89"},
        ],
        "checker": "exact",
    },
    "Climbing Stairs Ways": {
        "sample": [
            {"input": "2\n", "output": "2"},
            {"input": "3\n", "output": "3"},
        ],
        "hidden": [
            {"input": "4\n", "output": "5"},
            {"input": "5\n", "output": "8"},
        ],
        "checker": "exact",
    },
    "Coin Change Minimum Coins": {
        "sample": [
            {"input": "1 2 5\n11\n", "output": "3"},
            {"input": "2\n3\n", "output": "-1"},
        ],
        "hidden": [
            {"input": "1\n0\n", "output": "0"},
            {"input": "1\n2\n", "output": "2"},
        ],
        "checker": "exact",
    },
    "Longest Increasing Subsequence": {
        "sample": [
            {"input": "10 9 2 5 3 7 101 18\n", "output": "4"},
            {"input": "0 1 0 3 2 3\n", "output": "4"},
        ],
        "hidden": [
            {"input": "7 7 7 7 7 7 7\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Word Break Dictionary": {
        "sample": [
            {"input": "leetcode\nleet,code\n", "output": "true"},
            {"input": "applepenapple\napple,pen\n", "output": "true"},
        ],
        "hidden": [
            {"input": "catsandog\ncats,dog,sand,and,cat\n", "output": "false"},
        ],
        "checker": "exact",
    },
    "Unique Paths Grid Count": {
        "sample": [
            {"input": "3 7\n", "output": "28"},
            {"input": "3 2\n", "output": "3"},
        ],
        "hidden": [
            {"input": "1 1\n", "output": "1"},
            {"input": "7 3\n", "output": "28"},
        ],
        "checker": "exact",
    },
    "Kth Largest Element": {
        "sample": [
            {"input": "3 2 1 5 6 4\n2\n", "output": "5"},
            {"input": "3 2 3 1 2 4 5 5 6\n4\n", "output": "4"},
        ],
        "hidden": [
            {"input": "1\n1\n", "output": "1"},
        ],
        "checker": "exact",
    },
    "Merge K Sorted Lists": {
        "sample": [
            {"input": "1 4 5\n1 3 4\n2 6\n", "output": "1 1 2 3 4 4 5 6"},
        ],
        "hidden": [
            {"input": "\n", "output": ""},
        ],
        "checker": "exact",
    },
    "Subsets Power Set": {
        "sample": [
            {"input": "1 2 3\n", "output": "[]\n[1]\n[2]\n[1,2]\n[3]\n[1,3]\n[2,3]\n[1,2,3]"},
            {"input": "0\n", "output": "[]\n[0]"},
        ],
        "hidden": [
            {"input": "1\n", "output": "[]\n[1]"},
        ],
        "checker": "exact",
    },
    "Combination Sum Target": {
        "sample": [
            {"input": "2 3 6 7\n7\n", "output": "[2,2,3]\n[7]"},
            {"input": "2 3 5\n8\n", "output": "[2,2,2,2]\n[2,3,3]\n[3,5]"},
        ],
        "hidden": [
            {"input": "2\n1\n", "output": ""},
        ],
        "checker": "exact",
    },
    "Word Search Grid": {
        "sample": [
            {"input": "ABCEFG\nSFCS\nADEE\nSEE\n", "output": "true"},
            {"input": "ABCEFG\nSFCS\nADEE\nABCB\n", "output": "false"},
        ],
        "hidden": [
            {"input": "a\na\n", "output": "true"},
        ],
        "checker": "exact",
    },
    "Product of Array Except Self": {
        "sample": [
            {"input": "1 2 3 4\n", "output": "24 12 8 6"},
            {"input": "-1 1 0 -3 3\n", "output": "0 0 9 0 0"},
        ],
        "hidden": [
            {"input": "2 3\n", "output": "3 2"},
            {"input": "0 0\n", "output": "0 0"},
        ],
        "checker": "exact",
    },
    "Top K Frequent Elements": {
        "sample": [
            {"input": "1 1 1 2 2 3\n2\n", "output": "1 2"},
            {"input": "1\n1\n", "output": "1"},
        ],
        "hidden": [
            {"input": "4 4 4 6 6 8\n2\n", "output": "4 6"},
        ],
        "checker": "exact",
    },
    "Group Anagrams Together": {
        "sample": [
            {"input": "eat,tea,tan,ate,nat,bat\n", "output": "eat tea ate\ntan nat\nbat"},
            {"input": "\n", "output": ""},
        ],
        "hidden": [
            {"input": "a\n", "output": "a"},
        ],
        "checker": "exact",
    },
}


def run_fix():
    db = Database.get_db()
    col = db.coding_questions

    updated = 0
    total = col.count_documents({})
    print(f"Total coding_questions to process: {total}")

    for doc in col.find():
        title = doc.get("title", "")
        # Find matching definition
        match = None
        for key, val in CLASSIC_TEST_CASES.items():
            if key.lower() == title.lower() or key.lower() in title.lower() or title.lower() in key.lower():
                match = val
                break

        if match:
            sample_tcs = match["sample"]
            hidden_tcs = match["hidden"]
            checker = match.get("checker", "exact")
            si = sample_tcs[0]["input"] if sample_tcs else ""
            so = sample_tcs[0]["output"] if sample_tcs else ""

            col.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "sampleTestCases": sample_tcs,
                    "testCases": sample_tcs,
                    "hiddenTestCases": hidden_tcs,
                    "sampleInput": si,
                    "sampleOutput": so,
                    "checker": checker,
                    "timeLimit": doc.get("timeLimit") or 2.0,
                    "memoryLimit": doc.get("memoryLimit") or 256,
                    "updatedAt": datetime.now(timezone.utc),
                }}
            )
            updated += 1
            print(f"  [FIXED] '{title}' ({doc['_id']}) -> {len(sample_tcs)} sample, {len(hidden_tcs)} hidden cases")
        else:
            # If doc already has sampleInput/sampleOutput, convert to sampleTestCases
            si = doc.get("sampleInput", "")
            so = doc.get("sampleOutput", "")
            if si:
                sample_tcs = [{"input": si, "output": so}]
                col.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {
                        "sampleTestCases": sample_tcs,
                        "testCases": sample_tcs,
                        "updatedAt": datetime.now(timezone.utc),
                    }}
                )
                updated += 1
                print(f"  [SYNCSAMPLE] '{title}' ({doc['_id']}) -> 1 sample case from sampleInput")
            else:
                print(f"  [UNMATCHED] '{title}' ({doc['_id']})")

    print(f"\n[+] Backfill completed: {updated}/{total} questions updated with valid test cases!")


if __name__ == "__main__":
    run_fix()
