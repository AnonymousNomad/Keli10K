#!/usr/bin/env python3
"""
Keli10K Chunk Extension — Generators for Chunks 6-15
Each chunk: ~100K training examples across N categories.
Each example: (input, plan, think, exec_, cognitive_level, domain)
"""

import random
from chunk_generator import pick

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════
# Chunk 6: Advanced Algorithms & Data Structures
# ═══════════════════════════════════════════════════════════════════════════

SORTING_PROBLEMS = [
    ("sort 10 million integers with memory constraint of 64MB", "external merge sort", "split into 64MB chunks, sort each, merge with k-way heap"),
    ("sort a nearly-sorted array where each element is at most k positions away", "insertion sort with sliding window of size k", "maintain min-heap of k elements, extract min repeatedly"),
    ("sort strings by their reversed value without creating reversed copies", "custom comparator with reverse iteration", "two-pointer string reversal check within comparator"),
    ("sort an array of 1 million distinct integers from 1 to 1 million", "counting sort", "mark present in boolean array, iterate in order"),
    ("sort a linked list in O(n log n) with O(1) extra space", "bottom-up merge sort on linked list", "split into runs of power-of-two, merge iteratively"),
    ("sort 10 billion records with only 1GB RAM available", "distributed sorting with MapReduce", "partition by key ranges, sort partitions remotely, merge"),
    ("sort an array where 99 percent is already sorted but the rest is random", "adaptive sort (Timsort)", "identify natural runs, merge with galloping mode"),
]

def _sorting_gen():
    while True:
        for problem, technique, hint in SORTING_PROBLEMS:
            inp = pick(
                f"Design an algorithm to {problem}. Analyze time and space complexity.",
                f"Algorithm design: {problem}. Which sorting approach works best?",
                f"Sorting challenge: {problem}. Implement and analyze your solution.",
                f"Given: {problem}. Choose the optimal sorting algorithm and justify.",
            )
            plan = pick(
                f"<PLAN>Analyze constraints: input size, memory limit, data characteristics. {technique} is appropriate because {hint}. Plan: (1) Determine if comparison-based or distribution-based. (2) Consider stability requirements. (3) Evaluate time: best/average/worst case. (4) Evaluate space: in-place vs aux memory. (5) Implement with edge case handling. (6) Verify with extreme inputs.</PLAN>",
                f"<PLAN>Solve {problem}: First characterize data distribution and constraints. {technique} addresses key issues because {hint}. Approach: (1) Partition problem into manageable phases. (2) Use appropriate data structure (heap, buffer, array). (3) Ensure complexity matches constraints. (4) Handle I/O efficiently if external sorting. (5) Test with diverse datasets including edge cases.</PLAN>",
                f"<PLAN>Algorithm for {problem}: Identify bottleneck: memory, comparison count, or data movement. {technique} with {hint}. Steps: (1) Preprocess data if needed. (2) Apply divide-and-conquer or distribution strategy. (3) Merge/combine results. (4) Optimize for cache locality. (5) Profile and verify correctness on random, sorted, reversed, and duplicate inputs.</PLAN>",
            )
            think = pick(
                f"<THINK>For {problem}: The key constraint suggests {technique}. {hint} indicates we must optimize for the limiting factor. Comparison-based sorts are bounded by O(n log n); distribution-based sorts (counting, radix) can achieve linear time. Memory constraints force external or in-place algorithms. Cache-oblivious algorithms help with hierarchical memory. The optimal choice depends on stability, adaptivity, and predictable performance needs. I will implement {technique} because it optimally addresses the constraints while maintaining correctness guarantees.</THINK>",
                f"<THINK>Analyzing {problem}: Input characteristics suggest {technique}. Comparison-based sorts waste comparisons on structured data; distribution sorts exploit patterns. Memory constraints force careful memory management. {technique} handles this by {hint}. Important edge cases: all elements equal, already sorted, reverse sorted, single element, two elements. Each may trigger worst-case behavior in naive implementations. I will handle these with randomization or adaptive detection.</THINK>",
                f"<THINK>Designing sorting for {problem}: The fundamental trade-off is between comparison count and data movement. {technique} optimizes for {hint}. Time complexity: O(n log n). Space: in-place or O(n/k) buffers. Stability: conditional. Adaptivity: detects near-sorted input for optimization. For the specific constraint of large data volume, I/O cost dominates. {technique} minimizes passes over data. Verification: random input, sorted, reverse sorted, duplicates, and worst-case permutation all tested.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Algorithm: {technique} for {problem}. Complexity: O(n log n) time, O(n)/O(1) space. Implementation: (1) Handle base case; (2) Partition/merge with {hint}; (3) Combine results. Test: random arrays, sorted, reverse, duplicates, single element, large input profile. Verified correct on all cases. Memory usage within specified limits. Optimization: iterative over recursive if stack depth concerns.</EXEC>",
                f"<EXEC>Solution: {technique}. For {problem}, {hint}. Analysis: best/average/worst case within limits. Memory: satisfies constraint. Stability: conditional. Adaptivity: detects near-sorted input. Implementation completes in O(n log n) or better. All edge cases: empty array, single element, duplicates. Verified: output sorted, same length as input, contains same multiset of elements.</EXEC>",
                f"<EXEC>Sorting approach: {technique}. Problem: {problem}. {hint}. Time O(n log n), space within budget. Implementation avoids recursion depth issues, handles duplicates correctly, and maintains stability if required. Tested against standard library sort. Memory profile measured. Recommendation: use {technique} for this specific constraint set.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

GRAPH_PROBLEMS = [
    ("find shortest paths between all pairs in a graph with 10000 nodes and negative edges", "Floyd-Warshall or repeated Bellman-Ford", "negative edges prevent Dijkstra; Floyd-Warshall handles all pairs natively"),
    ("find the minimum spanning tree of a dense graph with 1 million nodes", "Prim algorithm with Fibonacci heap", "dense graphs favor Prim O(V log V) with heap"),
    ("detect cycles in a directed graph of 500K nodes with adjacency list", "DFS with three-color marking (white/gray/black)", "Tarjan algorithm detects cycles via back edges in DFS tree"),
    ("find the longest path in a directed acyclic graph", "topological sort plus DP relaxation", "DAG property enables DP: for each node in topo order, relax outgoing edges"),
    ("compute maximum flow in a network with 100K nodes and 500K edges", "Dinic algorithm with scaling", "Dinic with level graph and blocking flow is O(E sqrt(V)) for unit capacities"),
    ("find connected components in a graph too large for memory", "external memory BFS or MapReduce connected components", "partition graph, find components locally, merge across partitions"),
    ("compute PageRank for a web graph with 1 billion pages", "iterative power method with sparse matrix multiplication", "power iteration converges to principal eigenvector, handle dangling nodes"),
]

def _graph_gen():
    while True:
        for problem, technique, hint in GRAPH_PROBLEMS:
            inp = pick(
                f"Graph algorithm: {problem}. Design and analyze the solution.",
                f"Given: {problem}. What algorithm and data structures are optimal?",
                f"Graph theory problem: {problem}. Propose an efficient algorithm.",
                f"Solve: {problem}. Consider scale and constraints in your design.",
            )
            plan = pick(
                f"<PLAN>Graph problem: {problem}. {technique} because {hint}. Steps: (1) Model problem as graph with appropriate representation (adjacency matrix/list, edge list). (2) Choose traversal strategy (BFS/DFS/topological). (3) Apply {technique} with optimizations. (4) Handle edge cases: disconnected, zero-weight edges, self-loops. (5) Analyze complexity in terms of V and E. (6) Verify with small examples then scale.</PLAN>",
                f"<PLAN>Solve {problem}: Graph has V nodes and E edges. Constraints dictate {technique} because {hint}. Plan: (1) Construct graph efficiently (lazy or streaming). (2) Initialize data structures (distances, visited, heap, queue). (3) Run main algorithm. (4) Post-process results. (5) Optimize for cache locality. (6) Profile to identify bottlenecks.</PLAN>",
                f"<PLAN>Approach for {problem}: Use {technique}. {hint}. Implementation plan: (1) Graph representation depends on density. (2) Algorithmic skeleton: initialization, main loop, result extraction. (3) Data structure choices: priority queue, union-find, queue. (4) Handle large scale with external memory or distributed processing. (5) Verify correctness with invariants.</PLAN>",
            )
            think = pick(
                f"<THINK>Analyzing {problem}: The graph has many nodes. {technique} is appropriate because {hint}. Key considerations: (1) Graph density determines representation. (2) Edge weights may be positive, negative, or unit. (3) Negative weights rule out Dijkstra. (4) Large scale may require approximation or distributed algorithms. (5) Memory hierarchy matters. The algorithm must handle worst-case inputs. I will implement {technique} with proper data structures and test on edge cases.</THINK>",
                f"<THINK>For {problem}: Scale makes algorithm choice critical. {technique} with {hint} provides optimal complexity. Runtime analysis: preprocessing O(V+E), main algorithm appropriate bound, post-processing O(V). Memory: O(V+E) for adjacency, O(V) for aux structures. Bottleneck is typically edge relaxation or priority queue operations. Optimizations: adjacency list with arrays, pairing heap, bidirectional search. I must consider parallelization potential.</THINK>",
                f"<THINK>Designing solution for {problem}: {technique}. {hint}. Theoretical foundation: graph algorithms rely on relaxation, greedy choice, or DP. For shortest paths: triangle inequality ensures correctness. For MST: cut property guarantees optimality. For flow: max-flow min-cut theorem. For connectivity: union-find with path compression gives nearly O(1) operations. Each invariant must hold after every step. I will handle edge cases and verify correctness.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Solution: {technique} for {problem}. Complexity: appropriate bound. Implementation uses {hint}. Graph represented as adjacency list for sparse or matrix for dense. Tested on small cases, random medium graphs, and large-scale benchmark. Correctness verified: algorithm invariants hold, output matches brute-force on small cases. Memory usage O(V+E). Optimizations: cache-friendly traversal, efficient priority queue, early termination.</EXEC>",
                f"<EXEC>Graph algorithm complete: {problem} -> {technique}. {hint}. Runtime within expected bounds on test graphs. Memory O(V+E). Edge cases: empty graph, single node, disconnected components, zero-weight edges, negative cycles all handled. Verified against reference implementation.</EXEC>",
                f"<EXEC>Algorithm: {technique}. Problem: {problem}. Approach: {hint}. Test results: passes unit tests, integration tests, and stress tests. Performance scales as expected. Correctness relies on proven invariants. Implementation clean with proper abstraction.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "algorithms")

DP_PROBLEMS = [
    ("find the longest common subsequence of two strings of length 5000", "2D DP with O(n*m) table or Hirschberg space-optimized", "LCS has optimal substructure: dp[i][j] = dp[i-1][j-1]+1 if match else max(dp[i-1][j], dp[i][j-1])"),
    ("partition an array of 1000 integers into two subsets with minimal sum difference", "subset sum DP with bitmask optimization", "DP up to total_sum/2 using boolean array or bitset"),
    ("find the minimum number of coins to make change for any amount up to 100000", "1D DP with coin denominations", "dp[i] = min(dp[i - coin] + 1) for each coin"),
    ("compute the edit distance between two strings of length 2000", "Levenshtein distance with O(min(n,m)) space", "classic DP with two rolling rows"),
    ("find the maximum sum subarray in an array with both positive and negative numbers", "Kadane algorithm O(n)", "DP: max_ending_here = max(num, max_ending_here + num)"),
    ("count the number of ways to climb n stairs taking 1, 2, or 3 steps at a time", "linear DP O(n) with constant space", "dp[i] = dp[i-1] + dp[i-2] + dp[i-3], three variables"),
    ("find the longest palindromic subsequence in a string of length 3000", "interval DP or Manacher algorithm", "dp[i][j] = 2 + dp[i+1][j-1] if match else max(dp[i+1][j], dp[i][j-1])"),
    ("compute the minimum cost to multiply a chain of 500 matrices", "DP for optimal parenthesization", "dp[i][j] = min(dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1])"),
]

def _dp_gen():
    while True:
        for problem, technique, hint in DP_PROBLEMS:
            inp = pick(
                f"Dynamic programming: {problem}. Design the recurrence and implement.",
                f"DP problem: {problem}. Define states, transitions, and base cases.",
                f"Solve using dynamic programming: {problem}. Optimize space if possible.",
                f"Given: {problem}. Formulate as DP. What is the optimal substructure?",
            )
            plan = pick(
                f"<PLAN>DP approach for {problem}: (1) Define state: what subproblem am I solving? (2) Base case: smallest subproblem answer. (3) Recurrence: how to combine subproblem solutions. (4) Order: bottom-up or top-down with memoization. (5) {technique}. (6) Extract final answer. Key: optimal substructure and overlapping subproblems must exist.</PLAN>",
                f"<PLAN>Design DP for {problem}: Identify decision variables and constraints. {technique} handles complexity. Steps: (1) State definition with clear semantics. (2) Base cases at boundaries. (3) Transition from problem structure: {hint}. (4) Iteration order ensures subproblems solved before use. (5) Space optimization where possible. (6) Reconstruct solution via parent pointers.</PLAN>",
                f"<PLAN>DP formulation for {problem}: {technique}. {hint}. Plan: (1) Characterize optimal substructure. (2) Define dp dimensions. (3) Write recurrence formally. (4) Choose iteration order. (5) Implement with array/hash map. (6) Optimize memory: rolling array. (7) Verify on small cases against brute force.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing DP for {problem}: The key insight is optimal substructure -- the optimal solution contains optimal solutions to subproblems. {technique}. {hint}. Overlapping subproblems mean we solve each once and cache. State dimensions depend on problem parameters. Complexity: O(states * transitions). Space: O(states) reduced by observing which previous states are needed. For bottom-up: ensure correct order. For top-down: memoization cache. Recurrence derivation: at each decision point, options lead to smaller subproblems. Choose the best. Base case when problem minimal.</THINK>",
                f"<THINK>Formulating DP for {problem}: {technique} because {hint}. State space: dp[i] or dp[i][j] represents solution to subproblem. Transition: extends subproblem by one step. Base: trivial subproblem result. For {hint}, the recurrence captures the optimal choice at each step. Order: left to right or by increasing length. Common pitfalls: off-by-one, empty subproblem, wrong initialization, missing base case, unreachable states. I will address each with careful indexing.</THINK>",
                f"<THINK>DP analysis for {problem}: The problem exhibits optimal substructure because a solution builds from smaller independent subproblems. {technique}. {hint}. Let me trace the recurrence on a small example. For the transition: at each step, choices lead to different subproblems. DP computes optimal value for each state. Complexity: state count * choices per state. Space: base O(n*m) optimized to O(min(n,m)). Reconstruction requires parent pointers or divide-and-conquer.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>DP solution for {problem}. Technique: {technique}. Recurrence: {hint}. Complexity: O(states * transitions) time, optimized space. Implementation: bottom-up with correct ordering. Verified against brute force for small inputs. Space optimization: rolling array. Solution reconstruction available. All edge cases handled.</EXEC>",
                f"<EXEC>DP complete: {problem}. Method: {technique}. {hint}. State definition clear, recurrence correct, base cases comprehensive. Time O(n*m) or O(n), space optimized. Tested on random cases against naive solution. Performance within expected bounds. Optimal value computed with optional reconstruction path.</EXEC>",
                f"<EXEC>Dynamic programming: {problem}. State transition derived, complexity analyzed, space optimized. {technique} with {hint}. Handles edge cases: empty, single, all equal. Recurrence verified via invariant checking. Optimal value computed and optionally reconstructed.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

STRING_PROBLEMS = [
    ("find all occurrences of a pattern of length 100 in a text of length 10 million", "KMP (Knuth-Morris-Pratt) O(n+m)", "KMP computes failure function to avoid backtracking in text"),
    ("find the longest repeated substring in a genome of length 1 million", "suffix array plus LCP array or suffix tree", "LCP array gives longest common prefix between adjacent suffixes"),
    ("check if two strings are anagrams without sorting", "frequency count array of size 256", "increment for s1, decrement for s2, check all zero"),
    ("find the shortest palindrome by adding characters to the front", "KMP-based or Manacher algorithm", "find longest palindromic prefix using KMP on s + separator + reverse(s)"),
    ("compute the Levenshtein distance between two strings with custom operation weights", "weighted edit distance DP", "similar to standard edit distance with custom costs for insert/delete/replace"),
    ("find all distinct palindromic substrings in a string of length 5000", "expand around center O(n^2) or Manacher O(n)", "Manacher computes all palindrome radii in linear time"),
    ("convert a string to a valid palindrome by removing minimum characters", "LCS between string and its reverse", "minimum deletions = n - longest palindromic subsequence length"),
]

def _string_gen():
    while True:
        for problem, technique, hint in STRING_PROBLEMS:
            inp = pick(
                f"String algorithm: {problem}. Design and implement the optimal solution.",
                f"Given: {problem}. Use {technique}. Explain why this is optimal.",
                f"String processing: {problem}. Solve with efficient algorithm.",
                f"Algorithm needed: {problem}. What string matching/manipulation technique?",
            )
            plan = pick(
                f"<PLAN>String algorithm for {problem}: {technique} because {hint}. Plan: (1) Preprocess pattern/string if needed. (2) Main algorithm phase. (3) Post-process results. (4) Handle edge cases: empty strings, single character, unicode. (5) Analyze complexity. (6) Test on diverse inputs including worst-case adversarial patterns.</PLAN>",
                f"<PLAN>Solve {problem} with {technique}: {hint}. Steps: (1) Choose data representation (character array or string slice). (2) Build auxiliary structures. (3) Execute main algorithm. (4) Extract results. (5) Optimize memory. (6) Verify correctness with random tests.</PLAN>",
                f"<PLAN>String solution: {problem}. {technique}. {hint}. Approach: (1) Understand string properties: length, alphabet size. (2) Select algorithm based on constraints. (3) Implement with attention to indexing. (4) Consider unicode vs ASCII. (5) Profile and optimize. (6) Add property-based tests.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing {technique} for {problem}: {hint}. The naive approach would be O(n*m) but {technique} achieves O(n+m) by avoiding redundant comparisons. Key insight: when a mismatch occurs, we have already matched a prefix of the pattern; we can shift by more than 1 using precomputed information. For suffix arrays: sorting suffixes efficiently uses doubling algorithm O(n log n) or SA-IS O(n). LCP array built via Kasai algorithm O(n). For palindrome problems: Manacher exploits symmetry -- previously computed radii help skip unnecessary expansions. All these techniques trade preprocessing time for query efficiency. For the given constraints, this is optimal asymptotically.</THINK>",
                f"<THINK>Applying {technique} to {problem}: {hint}. String algorithms often require careful indexing. The failure function in KMP maps each position to the longest proper prefix that is also a suffix. This takes O(m) to compute and enables O(n) search. For palindrome problems: expanding around center gives O(n^2) worst case for n=5000 but not for larger. Manacher O(n) uses mirror positions to eliminate redundant comparisons. For suffix arrays: doubling sort uses rank pairs for stable sort. For frequency checks: array indexing must handle the full character range. Unicode needs normalization.</THINK>",
                f"<THINK>Analyzing {problem}: The constraint of large input suggests {technique}. {hint}. Comparison-based approaches would be too slow. {technique} achieves O(n) or O(n log n). Preprocessing builds data structures. Main algorithm scans once. Edge cases: empty pattern matches everywhere; pattern longer than text means no matches; all characters same triggers maximum shifts; unicode combining characters. I will handle each and verify against naive implementation on random small inputs.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>String algorithm: {technique} for {problem}. Complexity: O(n+m) time, O(m) space. {hint}. Handles ASCII and Unicode, empty strings, adversarial patterns. Verified against naive algorithm. Performance: linear scaling. Edge cases: pattern longer than text, empty pattern, single character, all same characters.</EXEC>",
                f"<EXEC>Solution: {technique}. Problem: {problem}. {hint}. Proper preprocessing and efficient main algorithm. Tested on diverse inputs: random, worst-case, binary, unicode. Correctness: all matches found. Performance within limits. Memory within budget.</EXEC>",
                f"<EXEC>String processing complete: {problem}. Algorithm: {technique}. {hint}. Preprocessing O(m), search O(n). Handles edge cases. Verified correct. Implementation optimized for cache efficiency. Ready for large-scale string data.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

TREE_PROBLEMS = [
    ("determine if a binary tree is height-balanced", "recursive DFS returning height or -1 for unbalanced", "check balance at each node: left_height - right_height <= 1"),
    ("find the lowest common ancestor of two nodes in a binary tree", "recursive post-order traversal", "if node matches either target, propagate up; LCA is where matches converge"),
    ("serialize and deserialize a binary tree to a string", "preorder traversal with null markers", "null markers preserve tree structure; reconstruct recursively"),
    ("find the diameter of a binary tree (longest path between any two nodes)", "DFS computing height and tracking max diameter", "diameter at a node = left_height + right_height; track global max"),
    ("convert a binary search tree to a sorted doubly linked list in place", "inorder traversal with prev pointer tracking", "process left, adjust pointers, process right; keep prev reference"),
    ("count the number of distinct BSTs that can be formed from n distinct keys", "Catalan numbers DP: dp[n] = sum(dp[i-1]*dp[n-i])", "each root splits remaining keys into left * right subtrees"),
    ("find all root-to-leaf paths in a binary tree", "DFS with backtracking, add path when leaf reached", "carry current path as list, add copy to results at leaf nodes"),
    ("check if two binary trees are identical structurally and by value", "simultaneous DFS comparing nodes", "both null: True; one null: False; values differ: False; else recurse left and right"),
]

def _tree_gen():
    while True:
        for problem, technique, hint in TREE_PROBLEMS:
            inp = pick(
                f"Tree algorithm: {problem}. Implement with appropriate traversal.",
                f"Given: {problem}. Choose the right tree traversal and solve.",
                f"Binary tree problem: {problem}. Design recursive or iterative solution.",
                f"Tree data structure: {problem}. What traversal order is needed?",
            )
            plan = pick(
                f"<PLAN>Tree problem: {problem}. {technique}. {hint}. Plan: (1) Determine traversal order. (2) Decide recursive vs iterative. (3) Implement base case (null node). (4) Recursive case with {technique}. (5) Handle edge cases: empty tree, single node, skewed tree. (6) Verify with diverse tree shapes.</PLAN>",
                f"<PLAN>Tree solution for {problem}: {technique} because {hint}. Steps: (1) Choose traversal matching problem. (2) Define state. (3) Base case returns trivial value. (4) Combine left and right results. (5) Update global accumulator if needed. (6) Ensure recursion depth safe; consider iterative alternative.</PLAN>",
                f"<PLAN>Solve {problem} with tree traversal: {technique}. {hint}. Approach: (1) Use explicit stack for iterative. (2) Define helper function for recursive. (3) Ensure correct visitor order. (4) For {technique}: proper state management. (5) Test on balanced, skewed, degenerate trees.</PLAN>",
            )
            think = pick(
                f"<THINK>Solving {problem}: Recursive tree structure naturally suggests {technique}. {hint}. Traversal choice: post-order for subtree information, in-order for BST, pre-order for serialization. Recursive is elegant but risks stack overflow on deep trees (depth > 1000). Iterative uses explicit stack. For {technique}: maintain per-call state including current node and accumulated values. Each recursive call handles one node, combining left/right results. Base case returns neutral value.</THINK>",
                f"<THINK>Analyzing {problem} on binary trees: {technique} with {hint}. Tree height: O(log n) balanced to O(n) skewed. Recursive depth matches height; iterative avoids overflow for skewed trees. Each node visited once, O(n) time. For {technique}: compute per-node values from children. Edge cases: empty tree returns base; single node is leaf; two-node tree tests recursion pattern.</THINK>",
                f"<THINK>Tree problem: {problem}. {technique} is appropriate. {hint}. Recursive depth worst-case O(n) for skewed. If n > 10000, use iterative. For post-order iterative: two stacks or stack with visited flag. Correctness: by induction, base at leaf works, children computed correctly ensures parent computation correct. Complexity: O(n) time, O(h) stack space.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Tree solution: {problem}. Traversal: {technique}. {hint}. Complexity: O(n) time, O(h) space. Recursive with proper base case. Tested on empty, single, balanced, skewed, random trees. All edge cases pass. Recursion depth safe. Iterative alternative available.</EXEC>",
                f"<EXEC>Algorithm complete: {problem}. Method: {technique}. {hint}. O(n) time. Recursive implementation correct. Test suite covers all tree shapes. Correctness proven by induction. Results match brute-force verification on small trees.</EXEC>",
                f"<EXEC>Tree algorithm: {problem}. {technique} with {hint}. O(n) time O(h) space. Handles recursion depth limits. Verified on all tree shapes. Edge cases: null root, leaf, left-skewed, right-skewed, complete tree. All tests pass.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

GREEDY_PROBLEMS = [
    ("schedule maximum number of non-overlapping meetings given start and end times", "earliest finish time first", "sort by end time, greedily pick non-conflicting meetings"),
    ("find minimum number of coins to make a given amount (unlimited coins of each denomination)", "always use largest denomination first if canonical coin system", "greedy works for standard coin systems; counterexample exists for non-canonical"),
    ("fractional knapsack: maximize value with weight limit, items can be split", "sort by value/weight ratio, take highest ratio first", "greedy optimal for fractional because we can take any portion"),
    ("minimum number of platforms needed for train schedules", "sweep line: sort arrivals and departures, count concurrent trains", "track net change at each event, max concurrent = min platforms"),
    ("Huffman coding: build optimal prefix-free binary code for character frequencies", "repeatedly merge two smallest frequency nodes", "greedy choice: merging smallest frequencies gives minimum weighted path length"),
    ("jump game: minimum jumps to reach end of array where each value is max jump length", "BFS-like greedy: track current and next farthest reachable", "greedy: at each step, compute farthest reachable within current jump range"),
    ("assign cookies to children: each child has greed factor, each cookie has size", "sort both, assign smallest cookie that satisfies each child", "greedy: smallest sufficient cookie leaves larger ones for greedier children"),
]

def _greedy_gen():
    while True:
        for problem, technique, hint in GREEDY_PROBLEMS:
            inp = pick(
                f"Greedy algorithm: {problem}. Prove optimality of the greedy choice.",
                f"Given: {problem}. Design a greedy algorithm. When is greedy optimal?",
                f"Optimization problem: {problem}. Apply greedy strategy and justify.",
                f"Solve: {problem}. Use a greedy approach and prove correctness.",
            )
            plan = pick(
                f"<PLAN>Greedy solution for {problem}: {technique}. {hint}. Plan: (1) Define the greedy choice. (2) Show optimal substructure: after greedy choice, remaining problem is same type but smaller. (3) Prove greedy choice property: there exists an optimal solution that makes the greedy choice. (4) Implement with sorting if needed. (5) Verify with counterexample search. (6) Analyze complexity.</PLAN>",
                f"<PLAN>Design greedy algorithm for {problem}: {technique} because {hint}. Steps: (1) Identify greedy decision. (2) Sort/order items appropriately. (3) Make greedy choice, update state. (4) Repeat until done. (5) Proof: exchange argument showing any optimal solution can be transformed to greedy. (6) Implementation with appropriate data structures.</PLAN>",
                f"<PLAN>Greedy approach for {problem}: {technique}. {hint}. Plan: (1) Characterize problem structure. (2) Define objective function. (3) Greedy selection rule. (4) Proof of optimality: exchange argument or matroid theory. (5) Implement efficiently. (6) Test on standard and edge cases. (7) Identify cases where greedy fails.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing greedy for {problem}: The greedy choice is {technique}. {hint}. The proof relies on exchange argument: take any optimal solution, if it does not use the greedy choice, we can swap it with greedy choice without making the solution worse. This works because the problem has optimal substructure and greedy choice property. For {technique}: correctness hinges on {hint}. Counterexample: greedy fails for non-canonical coin systems like denominations 1, 3, 4 making 6 -- greedy picks 4+1+1 but optimal is 3+3. I verify greedy optimality for this instance.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. The greedy paradigm makes locally optimal choices hoping for globally optimal solution. This works when: (1) Greedy choice property -- greedy choice is part of some optimal solution. (2) Optimal substructure -- remaining subproblem can be solved similarly. For {technique}: the exchange argument shows optimality. Implementation: sort O(n log n) then linear scan O(n). Edge cases: empty, single item, all same, already optimal.</THINK>",
                f"<THINK>Greedy formulation for {problem}: {technique}. {hint}. Key insight: the problem has natural ordering yielding optimality. For scheduling: earliest finish time maximizes remaining time. For coin change: large denominations first works for canonical systems. For Huffman: merging smallest frequencies gives minimum weighted path length. For each: greedy choice is safe due to matroid/greedoid structure. Counterexample awareness is crucial. Proof by exchange demonstrates optimality.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Greedy solution: {problem}. Strategy: {technique}. {hint}. Complexity: O(n log n) sort then O(n) greedy. Proof: exchange argument shows greedy choice property holds. Implementation: sort by key, iterate making greedy decisions. Edge cases: empty input, single item, equal priorities. Tested against brute force for small n to verify optimality.</EXEC>",
                f"<EXEC>Greedy algorithm: {problem}. Approach: {technique}. {hint}. Complexity O(n log n). Correctness proven via exchange argument. Implementation clean with comparator and linear scan. Verification: random cases against brute force (n small) confirm optimality. Edge cases handled.</EXEC>",
                f"<EXEC>Greedy complete: {problem}. Method: {technique}. {hint}. Time O(n log n), space O(1)/O(n). Greedy choice proved optimal via exchange. Implementation: sort, scan, accumulate. Verified against exhaustive search for small cases. Identified where greedy would fail if constraints changed.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

RECURSION_PROBLEMS = [
    ("generate all permutations of a string of length n", "backtracking with swap-based recursion", "swap each position with all subsequent, recurse, backtrack"),
    ("solve the Tower of Hanoi with 10 disks", "recursive: move n-1 to aux, move largest to dest, move n-1 to dest", "T(n) = 2*T(n-1) + 1 = 2^n - 1 moves"),
    ("compute the N-th Fibonacci number efficiently", "recursion with memoization or tail-recursive accumulators", "naive recursion is O(2^n); memoization gives O(n)"),
    ("find all subsets of a set that sum to a target value", "backtracking with pruning: sort, skip duplicates, bound if sum exceeds target", "subset sum with branch and bound; exponential worst-case but pruned in practice"),
    ("generate all valid parentheses combinations for n pairs", "recursive with open/close counts, only add close if close < open", "Catalan numbers: C_n = (2n)!/((n+1)!n!)"),
    ("solve N-Queens for N=8 and generalize to N", "backtracking: place queen per row, check column and diagonal conflicts", "O(N!) worst-case but heavily pruned by constraint propagation"),
    ("compute power(x, n) in O(log n) time", "exponentiation by squaring: x^n = (x^(n/2))^2 if even else x * x^(n-1)", "divide and conquer halves problem size each step"),
    ("generate all binary strings of length n without consecutive 1s", "recursive with last_digit parameter to enforce constraint", "at each position, can add 0 always, can add 1 only if last was 0"),
]

def _recursion_gen():
    while True:
        for problem, technique, hint in RECURSION_PROBLEMS:
            inp = pick(
                f"Recursive algorithm: {problem}. Design with base case and recurrence.",
                f"Given: {problem}. Solve using recursion. What is the recursive structure?",
                f"Recursion problem: {problem}. Implement with backtracking if applicable.",
                f"Design a recursive solution for {problem}. Analyze time and space complexity.",
            )
            plan = pick(
                f"<PLAN>Recursive solution for {problem}: {technique}. {hint}. Plan: (1) Define base case(s). (2) Recursive case: reduce problem size, combine results. (3) If backtracking: make choice, recurse, undo. (4) Optimize with memoization. (5) Consider tail recursion. (6) Analyze recursion tree depth and branching factor.</PLAN>",
                f"<PLAN>Recursive approach: {problem}. {technique}. {hint}. Steps: (1) Identify smaller identical subproblem. (2) Define how solutions combine. (3) Base case stops recursion. (4) For backtracking: state representation, valid moves, goal test. (5) Pruning: cut branches that cannot yield solutions. (6) Complexity: O(branching_factor^depth).</PLAN>",
                f"<PLAN>Design recursion for {problem}: {technique}. {hint}. Plan: (1) Parameters that change per call. (2) Return values. (3) Base case at minimal parameter. (4) Recursive: call with modified parameters, combine results. (5) Memoization table. (6) Convert to iterative if depth exceeds limits.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing recursion for {problem}: The recursive structure is {technique}. {hint}. Base case: problem size 0 or 1 returns trivial answer. Recursive case: reduce to smaller instance(s). For backtracking: decision tree where each level makes one choice. Pruning reduces search space. For {technique}: branching factor is choices at each step; depth is problem size n. Complexity: O(b^d) without pruning. Base cases handle all minimal forms. Stack depth equals n; for n > 1000, iterative safer. Memoization transforms exponential to polynomial for problems with overlapping subproblems.</THINK>",
                f"<THINK>Analyzing recursive solution for {problem}: {technique}. {hint}. Recursion tree: each call branches into sub-calls. For generate problems: build solutions incrementally, pruning invalid paths. For compute problems: reduce size, combine results. Key property: self-similarity at smaller scales. For {technique}: parameters encode partial solution and remaining input. Base case signals complete solution. Complexity: if each call reduces size by 1 and branches b ways, O(b^n) calls. With memoization, O(n) or O(n^2).</THINK>",
                f"<THINK>Solving {problem} recursively: Core insight is {technique}. {hint}. For generate problems: backtracking explores decision space systematically. Make choices and backtrack. For value problems: divide and conquer reduces size. Recursion tree for Fibonacci without memo: depth n, O(2^n). With memo: O(n). For power: depth log n, O(log n). For Towers of Hanoi: 2^n - 1 calls. For N-Queens: n rows, constrained branching. State space is decision tree; recursive DFS explores depth-first. Space: O(depth) for call stack.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Recursive solution: {problem}. Method: {technique}. {hint}. Base case defined, recurrence correct. Complexity as analyzed. Implementation: clean recursion with proper base case and inductive step. Tested on small inputs matching brute force. Stack depth within safe limits. Memoization applied where beneficial.</EXEC>",
                f"<EXEC>Recursion complete: {problem}. Approach: {technique}. {hint}. Implementation uses recursion with backtracking and pruning. Correctness verified by exhaustive testing on small cases. Performance acceptable for expected input sizes. Space: recursion stack O(depth). Edge cases handled.</EXEC>",
                f"<EXEC>Recursive algorithm: {problem}. Technique: {technique}. {hint}. Implementation: base case, recursion, optional memoization and pruning. Tested correct on all sample cases. Recursion depth bounded. Iterative alternative available for deep recursion. Code is self-documenting.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

SEARCH_PROBLEMS = [
    ("find a value in a sorted array of 1 billion elements", "binary search O(log n)", "repeatedly halve the search range by comparing middle element"),
    ("find the peak element in an array where neighbors are distinct", "modified binary search O(log n)", "compare mid with mid+1; go toward the larger neighbor"),
    ("search for an element in a rotated sorted array", "modified binary search with rotation detection", "determine which half is sorted, check if target is in that half"),
    ("find the square root of an integer with given precision", "binary search on real numbers with epsilon tolerance", "search range [0, n] or [0, 1] for n < 1; stop when high-low < epsilon"),
    ("search in a 2D matrix where rows and columns are sorted", "start from top-right corner, eliminate row or column each step", "if target < current, move left; if target > current, move down"),
    ("find the k-th smallest element in two sorted arrays", "binary search on partition sizes O(log(m+n))", "partition both arrays such that left parts are k elements and max(left) <= min(right)"),
    ("find first and last position of a target in a sorted array with duplicates", "binary search leftmost then rightmost separately", "modify binary search: do not stop on match, continue left for first"),
]

def _search_gen():
    while True:
        for problem, technique, hint in SEARCH_PROBLEMS:
            inp = pick(
                f"Search algorithm: {problem}. Design the optimal search strategy.",
                f"Given: {problem}. What search technique works? Analyze complexity.",
                f"Efficient search: {problem}. Implement with {technique}.",
                f"Search problem: {problem}. How to locate the target efficiently?",
            )
            plan = pick(
                f"<PLAN>Search approach: {problem}. {technique} because {hint}. Plan: (1) Determine if array is sorted or has special structure. (2) Choose search strategy. (3) Implement with correct invariants and termination. (4) Handle edge cases: target not found, duplicates, empty array. (5) Consider integer overflow in mid calculation. (6) Test on diverse inputs.</PLAN>",
                f"<PLAN>Search solution for {problem}: {technique}. {hint}. Steps: (1) Define search space. (2) While search space non-empty: compute mid, compare, narrow. (3) Return index or indicate not found. (4) For modified: adjust comparison logic per problem. (5) Ensure termination. (6) Verify invariants hold throughout.</PLAN>",
                f"<PLAN>Efficient search: {problem}. {technique}. {hint}. Approach: (1) Identify exploitable structure. (2) Apply divide and conquer. (3) Implementation with custom predicate. (4) Edge cases: single, two elements, all same, boundaries. (5) Complexity: O(log n). (6) Test against linear search.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing search for {problem}: {technique} because {hint}. Binary search is the fundamental divide-and-conquer technique for sorted data. Key invariant: target (if present) is in [low, high]. Maintain by narrowing to correct half. Mid: low + (high - low) // 2 avoids overflow. For rotated arrays: detect sorted half by comparing arr[mid] with arr[low]. For 2D: start from top-right, each step eliminates row or column. For partition: binary search on partition index in smaller array ensures O(log(min(m,n))). For real-valued: continue until high-low < epsilon. For first/last: continue left for first occurrence, right for last.</THINK>",
                f"<THINK>Analyzing search in {problem}: {technique}. {hint}. The search space is large. Linear search O(n) too slow; binary search O(log n) required. Binary search properties: (1) Requires random access. (2) Data must be sorted or monotonic. (3) Predicate must be monotonic. For {technique}: modification to standard binary search is {hint}. Implementation pitfalls: off-by-one, infinite loops when low=mid, integer overflow, incorrect predicate monotonicity. Standard pattern: while low <= high for index search; while high - low > eps for value search.</THINK>",
                f"<THINK>Search design for {problem}: {technique} leverages {hint}. The search space has monotonic property. For standard binary search: sorted order. For rotated: one half is fully sorted. For peak: array increases then decreases. For 2D: rows and columns sorted. For partition: cumulative sorted property across arrays. Each modifies comparison logic but retains O(log n). Key to correctness: invariant maintained after each iteration. Edge cases: empty -> -1; single -> 0 if match; all same -> first/last correctly.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Search solution: {problem}. Algorithm: {technique}. {hint}. Complexity: O(log n) or O(m+n). Implementation with correct invariants. Tested: random arrays against linear search, edge cases (empty, single, duplicates, not found). No integer overflow. All tests pass.</EXEC>",
                f"<EXEC>Search complete: {problem}. Method: {technique}. {hint}. O(log n) time, O(1) space. Handles all edge cases. Verified on sorted, rotated, special structure arrays. Invariants documented. Mid computed safely. Not found handled gracefully.</EXEC>",
                f"<EXEC>Search algorithm: {problem}. Technique: {technique}. {hint}. Complexity: O(log n). Implementation clean with clear invariants. Test suite covers all input shapes. All pass. Binary search variant correctly adapted to problem structure.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

MATH_PROBLEMS = [
    ("determine if a number is prime, for numbers up to 10^12", "trial division up to sqrt(n) or Miller-Rabin probabilistic test", "check divisibility by 2, 3, then numbers of form 6k +/- 1 up to sqrt"),
    ("compute the greatest common divisor of two large numbers efficiently", "Euclidean algorithm: gcd(a,b) = gcd(b, a mod b)", "repeatedly replace larger by remainder; O(log min(a,b))"),
    ("find all prime factors of a number up to 10^12", "trial division with wheel factorization up to sqrt(n)", "check 2, 3, then 6k+/-1; after dividing, remaining > 1 is prime factor"),
    ("compute n choose k modulo a large prime efficiently", "precompute factorials and inverse factorials using Fermat little theorem", "nCk = n! * inv(k!) * inv((n-k)!) mod p via pow"),
    ("find the n-th Fibonacci number modulo 10^9+7 in O(log n)", "matrix exponentiation: [[1,1],[1,0]]^n", "exponentiation by squaring on 2x2 matrix, O(log n) multiplications"),
    ("compute modular exponentiation for base up to 10^18 and exponent up to 10^18", "binary exponentiation by squaring", "square and multiply: process each bit of exponent"),
    ("solve a linear Diophantine equation ax + by = c", "extended Euclidean algorithm", "if c % gcd(a,b) != 0: no solution; else x0 = x * c/g, y0 = y * c/g"),
]

def _math_algo_gen():
    while True:
        for problem, technique, hint in MATH_PROBLEMS:
            inp = pick(
                f"Mathematical algorithm: {problem}. Design and analyze the solution.",
                f"Number theory: {problem}. What algorithm gives the answer?",
                f"Computational math: {problem}. Implement efficient solution.",
                f"Given: {problem}. Use {technique}. Explain number-theoretic basis.",
            )
            plan = pick(
                f"<PLAN>Math algorithm for {problem}: {technique}. {hint}. Plan: (1) Understand the mathematical foundation. (2) Choose efficient algorithm based on input size. (3) Handle integer overflow with modular arithmetic. (4) Implement with proper termination and edge cases. (5) Verify on known values. (6) Analyze time complexity in bit operations.</PLAN>",
                f"<PLAN>Solve {problem} with {technique}: {hint}. Steps: (1) Input preprocessing. (2) Core algorithm implementation. (3) Handle special cases. (4) Use appropriate integer types. (5) For primality: deterministic for n < 2^64. (6) Verify on known examples.</PLAN>",
                f"<PLAN>Computational math: {problem}. {technique}. {hint}. Approach: (1) Mathematical formulation. (2) Algorithm design with invariants. (3) Implementation with overflow/precision care. (4) Modular arithmetic to keep numbers bounded. (5) Edge cases: n=0, n=1, large inputs, negatives. (6) Complexity in bit operations.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing math algorithm for {problem}: {technique}. {hint}. Euclidean algorithm relies on gcd(a,b) = gcd(b, a mod b). Numbers decrease geometrically, O(log min(a,b)) steps. For primality testing up to 10^12: trial division to sqrt(n) = 10^6 divisions, acceptable. For larger, Miller-Rabin gives probabilistic guarantees. For exponentiation: binary method processes each bit, O(log exp) multiplications. For matrix exponentiation of Fibonacci: same complexity with 2x2 matrices. Key insight: exploit mathematical structure to reduce complexity from O(n) to O(log n). For combinatorial: precomputation amortizes cost.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Number-theoretic algorithms exploit structure of integer operations. GCD: Euclidean reduces exponentially. Extended GCD adds Bezout coefficients, enabling modular inverses and Diophantine solutions. Primality: sqrt(n) is max possible factor; wheel factorization reduces checks by 2/3. Modular arithmetic: Fermat a^(p-1) = 1 (mod p) gives modular inverse a^(-1) = a^(p-2) (mod p). Exponentiation: binary method reduces O(exp) to O(log exp). Ensure careful with 0 and negative inputs.</THINK>",
                f"<THINK>Computing solution for {problem}: {technique}. {hint}. Algorithm relies on mathematical identities. For GCD: gcd(a,b) = gcd(b, a mod b). For primality: compositeness detected by factor <= sqrt(n). For exponentiation: x^y = (x^(y/2))^2 if y even. These recurrences reduce problem size by half, giving O(log n). For Fibonacci: matrix representation linearizes recurrence. Each demonstrates: mathematical insight enables exponentially faster algorithms. Implement with edge case handling.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Math algorithm: {problem}. Method: {technique}. {hint}. Complexity: O(log n) or O(sqrt(n)). Handles edge cases (zero, negative, large). Uses appropriate integer sizes. Avoids overflow with modular arithmetic. Tested on known values and random inputs against brute force.</EXEC>",
                f"<EXEC>Solution: {technique} for {problem}. {hint}. Complexity as analyzed. Correct edge case handling. Verified against brute force for small inputs. Large input performance confirmed. Mathematical invariants hold.</EXEC>",
                f"<EXEC>Computational math: {problem}. Algorithm: {technique}. {hint}. Logarithmic complexity. Clean implementation. Verified on standard test cases. Invariants maintained. Termination guaranteed.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "algorithms")

GEO_PROBLEMS = [
    ("determine if two line segments intersect", "orientation test plus general position check", "compute orientation of triplets; check if opposite signs and collinear cases"),
    ("compute the convex hull of a set of 100000 points", "Graham scan O(n log n) or monotone chain", "sort by angle/polar, then scan maintaining clockwise turns"),
    ("find the closest pair of points among 1 million points", "divide and conquer O(n log n)", "split by median x, recurse left/right, merge strip of width delta"),
    ("check if a point lies inside a simple polygon", "ray casting: count intersections of horizontal ray with polygon edges", "odd number of intersections means inside; handle vertex and edge cases"),
    ("compute the area of a simple polygon given its vertices", "shoelace formula: sum(x_i * y_{i+1} - x_{i+1} * y_i) / 2", "cross product sum around polygon gives twice the signed area"),
    ("find the Delaunay triangulation of a set of points", "Bowyer-Watson incremental O(n^2) or Fortune O(n log n)", "insert points one by one, flip edges to maintain Delaunay property"),
    ("determine the intersection of two convex polygons", "rotating calipers O(n+m) or divide and conquer", "sweep around both polygons tracking intersection boundaries"),
]

def _geo_gen():
    while True:
        for problem, technique, hint in GEO_PROBLEMS:
            inp = pick(
                f"Computational geometry: {problem}. Design the algorithm.",
                f"Geometry problem: {problem}. Use {technique}.",
                f"Given: {problem}. Implement with careful handling of edge cases.",
                f"Geometric algorithm: {problem}. Analyze numerical precision issues.",
            )
            plan = pick(
                f"<PLAN>Computational geometry: {problem}. {technique} because {hint}. Plan: (1) Define point/line primitives. (2) Handle floating-point precision. (3) Main algorithm implementation. (4) Handle degenerate cases. (5) Analyze complexity. (6) Test with known configurations and random data.</PLAN>",
                f"<PLAN>Geometry solution for {problem}: {technique}. {hint}. Steps: (1) Represent geometric primitives. (2) Implement elementary operations. (3) Apply {technique}. (4) Use epsilon tolerance. (5) Test on degenerate inputs. (6) Visual verification where possible.</PLAN>",
                f"<PLAN>Solve {problem}: {technique}. {hint}. Approach: (1) Input representation with epsilon. (2) Sort/order points. (3) Apply algorithm with predicates. (4) Handle special cases explicitly. (5) Complexity: O(n log n). (6) Test on random, grid, collinear, clustered sets.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing geometric algorithm for {problem}: {technique}. {hint}. The fundamental challenge is floating-point precision. Orientation test (cross product): cross = (b.x - a.x)*(c.y - a.y) - (b.y - a.y)*(c.x - a.x). Compare to epsilon. For {technique}: {hint}. Degenerate cases: (1) All collinear -- hull is segment. (2) Duplicates -- deduplicate. (3) Self-intersecting polygons. (4) Same x -- angle sort fails, use cross comparator. (5) Vertical lines. For large n: O(n log n) essential. Use epsilon = 1e-9 for double.</THINK>",
                f"<THINK>Analyzing {problem}: {technique}. {hint}. Geometry algorithms rely on fundamental predicates: orientation (cross product), between (dot product), distance (squared to avoid sqrt). For convex hull: Graham scan sorts by angle, uses left-turn test. Monotone chain sorts by x,y, builds upper/lower hulls. For closest pair: divide by x, find min delta in halves, check strip. Packing argument: at most 6 points in any delta x delta rectangle. For point-in-polygon: ray casting works for simple polygons; handle vertices with epsilon. Area: shoelace for any simple polygon.</THINK>",
                f"<THINK>Solving {problem} computationally: {technique}. {hint}. Key implementation details: (1) Cross product for turn/area; avoid slope. (2) Squared distances to avoid sqrt. (3) Sort by x then y lexicographically. (4) Parametric form for line intersection. (5) EPS = 1e-9; is_zero(x) = abs(x) < EPS. (6) For exact integer coordinates, use 128-bit. Robustness is primary challenge; algorithm may be O(n log n) in theory but incorrect due to numerical issues. Test against brute force for small n.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Geometry algorithm: {problem}. Technique: {technique}. {hint}. Complexity: O(n log n). Robust predicates with epsilon. Degenerate cases handled. Tested on random, collinear, grid, clustered inputs. Verified against brute force for small n.</EXEC>",
                f"<EXEC>Computational geometry: {problem}. Method: {technique}. {hint}. Complexity within bounds. Epsilon-safe comparisons. Degenerate case detection. Visual validation. Numerical stability with stress tests.</EXEC>",
                f"<EXEC>Geometry solution: {problem}. Algorithm: {technique}. {hint}. Epsilon-based comparisons. Edge cases handled. Verified against reference implementations. Performance O(n log n) confirmed.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "algorithms")

def chunk_6_gen():
    gens = [_sorting_gen(), _graph_gen(), _dp_gen(), _string_gen(), _tree_gen(),
            _greedy_gen(), _recursion_gen(), _search_gen(), _math_algo_gen(), _geo_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════════════════════════════════════════════════════════
# Chunk 7: Systems & Low-Level Programming
# ═══════════════════════════════════════════════════════════════════════════

MEMORY_TOPICS = [
    ("design a custom memory allocator that reduces fragmentation", "segregated free lists with size classes", "pre-allocate blocks of popular sizes, use buddy system for larger allocations"),
    ("implement a garbage collector for a managed runtime", "mark-sweep with tri-color abstraction or generational collection", "roots -> mark reachable objects, sweep unmarked, compact optionally"),
    ("detect and fix a memory leak in a long-running server process", "use valgrind/ASAN, track reference counts, add leak detection instrumentation", "periodic heap profiling, check reference cycles, ensure deallocation in all paths"),
    ("implement a memory pool for fixed-size allocations in real-time systems", "pre-allocate slab of pages, maintain free list, O(1) alloc/dealloc", "request contiguous virtual memory, carve into fixed-size blocks, linked list of free blocks"),
    ("optimize cache usage in a data-intensive application", "cache-aware data structures, blocking/tiling, prefetching", "reorganize data for sequential access, align to cache lines, use cache-oblivious algorithms"),
    ("implement virtual memory paging with demand loading", "page table with TLB, handle page faults, LRU/clock replacement", "map virtual to physical pages, trap on fault, evict using approximate LRU"),
    ("manage NUMA memory affinity for multi-socket systems", "bind memory to local node, interleave for bandwidth, migrate pages dynamically", "first-touch policy, use libnuma for explicit placement, balance across nodes"),
    ("implement stack overflow detection and handling", "guard pages, stack probing, alternative signal handling", "place unmapped page at stack bottom, stack probe allocates pages progressively"),
]

def _memory_gen():
    while True:
        for problem, technique, hint in MEMORY_TOPICS:
            inp = pick(
                f"Memory management: {problem}. Propose and explain your design.",
                f"Low-level memory: {problem}. How would you implement this?",
                f"Systems programming: {problem}. Describe the implementation approach.",
                f"Memory subsystem design: {problem}. Handle performance and correctness.",
            )
            plan = pick(
                f"<PLAN>Memory management design: {problem}. {technique}: {hint}. Plan: (1) Define requirements: throughput, latency, fragmentation tolerance, concurrency. (2) Design core data structures. (3) Specify allocation/deallocation paths. (4) Handle edge cases: out-of-memory, concurrent access, alignment. (5) Add debugging/tracking support. (6) Test with adversarial allocation patterns.</PLAN>",
                f"<PLAN>Systems approach for {problem}: Use {technique} because {hint}. Steps: (1) Analyze current memory behavior. (2) Identify pain points. (3) Design solution. (4) Implement with careful low-level coding. (5) Validate with stress testing and leak detection. (6) Benchmark before/after.</PLAN>",
                f"<PLAN>Memory system: {problem}. {technique}. {hint}. Plan: (1) Interface design. (2) Internal bookkeeping. (3) Thread safety. (4) Debug support. (5) Integration with OS page allocation. (6) Performance tuning with actual workloads.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing memory subsystem: {problem}. Key challenges: fragmentation, allocation latency, cache performance. {technique} addresses these by {hint}. For allocators: segregated lists maintain pools of common sizes. Buddy system splits large blocks cleanly. Metadata overhead: store inline before user pointer. Thread caching reduces contention. For GC: tri-color abstraction (white/gray/black) ensures correctness. White = unreachable, gray = reachable but children not scanned, black = fully scanned. Generational collection exploits weak generational hypothesis. For virtual memory: demand paging with LRU/Clock balances memory pressure. Working set size key metric; thrashing when working set exceeds physical memory.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Memory management at user/kernel boundary (mmap, brk). Allocator must balance: (1) Speed. (2) Fragmentation (internal/external). (3) Memory overhead. (4) Scalability. For {technique}: {hint} directly addresses these. Size classes reduce internal fragmentation to at most 50%. Free lists store next pointers in free memory itself. Per-thread caches avoid locks. For detection: valgrind uses synthetic CPU; ASAN uses red zones. For NUMA: first-touch policy determines node. For stacks: guard pages trigger SIGSEGV on overflow. All require deep understanding of hardware and OS memory models.</THINK>",
                f"<THINK>Deep dive into {problem}: Memory hierarchy (L1/L2/L3 cache, RAM, swap) has vastly different latencies. {technique} optimizes for {hint}. Cache lines are 64 bytes; false sharing occurs when threads modify different data on same cache line. Solutions: align hot data, pad structs, per-thread data. Slab allocator (Linux kernel) provides O(1) allocation for common sizes. For GC: generational collection scans only young generation most collections. Concurrent GC runs most work in parallel with mutator. For virtual memory: huge pages (2MB, 1GB) reduce TLB pressure. For stack: guard pages at bottom trigger fault on overflow. Each technique requires low-level implementation with bit manipulation and atomic operations.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Memory system: {problem}. Design: {technique}. {hint}. Implementation: core allocator/collector, thread safety, debugging support. Tested: adversarial patterns, concurrent stress, leak detection. Performance: improved fragmentation/throughput/latency. Edge cases: OOM handled, alignment guaranteed, metadata overhead minimized.</EXEC>",
                f"<EXEC>{problem} solved with {technique}. {hint}. Allocator with bookkeeping, thread safety, debug support. Throughput high, fragmentation low. Tested with stress tests, leak detection, concurrent workloads. Edge cases handled.</EXEC>",
                f"<EXEC>Memory management: {problem}. Approach: {technique}. {hint}. Data structures for free list management, thread synchronization, OS integration. Performance validated. Correctness with ASAN/valgrind. Production-ready.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

PROCESS_TOPICS = [
    ("implement a context switch between user-level threads", "saving/restoring registers and stack pointer with setjmp/longjmp or inline assembly", "save callee-saved registers, swap stack pointers, restore registers of next thread"),
    ("design a process scheduler for a real-time embedded system", "fixed-priority preemptive scheduling with rate monotonic analysis", "shorter period tasks get higher priority; priority inheritance to prevent inversion"),
    ("implement copy-on-write semantics for process forking", "share pages with read-only mapping, duplicate on write fault", "fork creates child with shared pages; page fault on write triggers copy"),
    ("handle the thundering herd problem in event-driven servers", "use edge-triggered epoll with level-triggered fallback or accept mutex", "wake only one worker per event; use SO_REUSEPORT for kernel-level load balancing"),
    ("implement a spinlock vs mutex decision for different contention levels", "spinlocks for short critical sections, mutexes for longer waits", "spinlocks burn CPU while waiting but low latency; mutexes sleep but waste no CPU"),
    ("design a wait-free concurrent data structure", "use CAS (compare-and-swap) loops with hazard pointers or RCU", "lock-free: at least one thread makes progress; wait-free: all threads make progress in bounded steps"),
    ("implement inter-process signaling with real-time signals", "use sigaction with SA_SIGINFO to receive data payload", "sigqueue sends signal with payload; real-time signals are queued and ordered"),
]

def _process_gen():
    while True:
        for problem, technique, hint in PROCESS_TOPICS:
            inp = pick(
                f"Process/scheduling: {problem}. Design the implementation.",
                f"Systems programming: {problem}. Low-level implementation approach.",
                f"OS concept: {problem}. How would you implement this in C?",
                f"Given: {problem}. Design the mechanism and handle edge cases.",
            )
            plan = pick(
                f"<PLAN>OS mechanism: {problem}. {technique}: {hint}. Plan: (1) Understand hardware and OS primitives. (2) Design data structures. (3) Implement core logic. (4) Handle preemption and interrupt safety. (5) Test with concurrent workloads. (6) Profile and optimize.</PLAN>",
                f"<PLAN>Systems design for {problem}: Use {technique}. {hint}. Steps: (1) Define interfaces. (2) Implement low-level primitives. (3) Add scheduling logic. (4) Ensure correctness invariants. (5) Handle edge cases. (6) Benchmark overhead.</PLAN>",
                f"<PLAN>Process mechanism: {problem}. {technique}. {hint}. Plan: (1) Resource requirements. (2) Context switch sequence. (3) Synchronization. (4) Preemption. (5) IPC integration. (6) Stress testing.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing {problem}: Core challenge is saving/restoring execution state. {technique}: {hint}. Context switch: CPU registers define thread state. Callee-saved registers (rbx, rbp, r12-r15 on x86-64) must be preserved. Stack pointer (rsp) defines thread stack. Instruction pointer implicit via return address. For user-level threads: entirely in user space, faster switches. For kernel threads: OS handles privilege level and TLB flush. For COW: share pages read-only, copy on write fault. For scheduler: preemptive requires timer interrupt; cooperative yields explicitly. Priority inheritance solves inversion.</THINK>",
                f"<THINK>Analyzing {problem}: {technique}. {hint}. Implementation handles concurrency, interrupts, hardware specifics. On x86-64, context switch saves: R15, R14, R13, R12, RBX, RBP, RSP, return address. Atomicity: block signals during switch. For spinlocks: atomic CAS loop with pause instruction. For mutexes: futex (fast userspace mutex) optimizes uncontended case. For wait-free: helping mechanism ensures bounded progress. Hazard pointers track accessed objects. RCU defers reclamation.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. The thread/process abstraction: sequential execution stream with private stack, registers, scheduling state. For user-level threads: private stack from heap. Scheduler runs as normal function. On x86-64, context switch: push callee-saved regs; switch stacks; pop callee-saved regs; return. About 10-20 instructions, 50-100ns. For kernel threads: switch involves entering kernel mode, switching address spaces, TLB flush. For COW: fork marks writable pages read-only; page fault handler detects COW, copies page. For scheduling: O(1) with separate run queues per priority; CFS uses red-black tree keyed by vruntime.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>{problem} implemented. Technique: {technique}. {hint}. Context switch in assembly. Scheduler with appropriate algorithm. Tested: concurrent threads, edge cases. Overhead measured. Correctness: no lost wakeups, no deadlock, fair scheduling. Preemption safe.</EXEC>",
                f"<EXEC>Systems mechanism: {problem}. Implementation: {technique}. {hint}. Core logic in assembly/C with atomics. Proper memory ordering. Tested under heavy concurrency. No races detected. Performance measured. Edge cases handled.</EXEC>",
                f"<EXEC>Process/scheduling solution: {problem}. Design: {technique}. {hint}. Context save/restore, scheduling policy, synchronization. Verified: no deadlock, no starvation, fair CPU distribution. Production-grade.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

IPC_TOPICS = [
    ("implement a shared memory ring buffer for producer-consumer", "lock-free ring buffer with atomic head/tail pointers", "producer advances head, consumer advances tail; detect full/empty with wrap counters"),
    ("design a message-passing system with bounded buffers", "channel with send/recv operations using condition variables", "sender blocks on full; receiver blocks on empty; both notify on state change"),
    ("implement a D-Bus style inter-process communication bus", "Unix domain sockets with SCM_RIGHTS for fd passing", "use AF_UNIX SOCK_STREAM; serialize messages with header + body + fds"),
    ("design a distributed shared memory system", "page-based DSM with invalidate/update protocol", "each node caches pages; coherence protocol like MESI maintains consistency"),
    ("implement semaphores from mutexes and condition variables", "count protected by mutex, wait/signal on condition variable", "down: if count==0 wait else count--; up: count++, signal one waiter"),
    ("design a zero-copy IPC mechanism between producer and consumer processes", "shared memory with ring buffer, mmap with MAP_SHARED", "producer writes directly into shared buffer; consumer reads in place; avoid kernel copy"),
    ("implement remote procedure call (RPC) stubs and marshaling", "generate client stub and server skeleton from IDL", "marshal arguments into buffer, send, unmarshal, call, marshal reply back"),
]

def _ipc_gen():
    while True:
        for problem, technique, hint in IPC_TOPICS:
            inp = pick(
                f"IPC design: {problem}. How would you implement this inter-process communication?",
                f"Inter-process communication: {problem}. Design for performance and correctness.",
                f"Systems programming: {problem}. Implement the IPC mechanism.",
                f"Given: {problem}. Handle synchronization, buffering, and edge cases.",
            )
            plan = pick(
                f"<PLAN>IPC design: {problem}. {technique}: {hint}. Plan: (1) Choose transport. (2) Define protocol. (3) Implement synchronization. (4) Handle buffering. (5) Address security. (6) Test with concurrent producers/consumers, stress, edge cases.</PLAN>",
                f"<PLAN>IPC mechanism for {problem}: {technique}. {hint}. Steps: (1) Allocate shared resources. (2) Implement data transfer. (3) Add synchronization. (4) Define message protocol. (5) Handle process death. (6) Benchmark throughput and latency.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Resource setup. (2) Core algorithm. (3) Synchronization. (4) Edge cases. (5) Performance optimization. (6) Test with concurrent access and crashes.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing IPC: {problem}. {technique}: {hint}. Processes have isolated address spaces; IPC must cross this boundary. For shared memory: processes map same physical pages via mmap MAP_SHARED. Ring buffer uses atomic head/tail. Memory ordering: producer writes data then advances head (release); consumer reads head then reads data (acquire). On x86, sequential consistency is default; on ARM/POWER, explicit barriers needed. Buffer full when (head - tail) == capacity; empty when head == tail. Power-of-two sizes enable fast modulo with AND. For message passing: channels use monitor pattern (mutex + condition variable). For zero-copy: data never copied between kernel/user space. For all: process death during IPC leaves shared resources in inconsistent state. Use robust mutexes, heartbeats, or timeouts.</THINK>",
                f"<THINK>Analyzing {problem} for IPC: {technique}. {hint}. Choice between shared memory and sockets: (1) Latency -- shared memory sub-microsecond, Unix sockets 1-10 us, TCP 10-100 us. (2) Security -- sockets better isolation. (3) Simplicity -- sockets easier. For ring buffer: cache line padding crucial. Head and tail on different cache lines to avoid false sharing. Buffer slots cache-line-sized. Write combining: batch writes to amortize atomics. For RPC: serialization (protobuf, flatbuffers). IDL compiler generates stubs handling marshaling. For semaphores: mutex protects count; condition variable for blocking. For all: timeout handling critical.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. SPSC queue can be entirely lock-free with two atomics. MPMC requires CAS on head. For SPSC: Producer writes slot[head % N], store release head+1. Consumer load acquire head, while tail < head: read slot[tail % N], store release tail+1. No CAS needed. For blocking: futex avoids spinning. For shared memory: pointers must be relative offsets because processes map at different virtual addresses. For D-Bus: protocol header with endianness, type, flags, body length, serial. FDs via ancillary data. For RPC: stub generation creates functions that look local but marshal args, send, wait, unmarshal.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>IPC implementation: {problem}. Technique: {technique}. {hint}. Shared memory/socket ring buffer with synchronization. Throughput high, latency low. Tested: concurrent producers/consumers, crash recovery, full/empty. Memory ordering correct. Cache false sharing avoided. Edge cases handled.</EXEC>",
                f"<EXEC>IPC mechanism: {problem}. Design: {technique}. {hint}. Lock-free ring buffer with atomics. Cache-line aligned, false sharing prevented. Blocking via futex/condvar. Tested under stress. Protocol: framed messages. Performance near line rate.</EXEC>",
                f"<EXEC>{problem} implemented. Approach: {technique}. {hint}. Shared ring buffer or socket transport. Correctness: no lost messages, no races, proper cleanup. Benchmark results meet requirements. Production-quality with timeout handling.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

FILEIO_TOPICS = [
    ("implement an efficient buffered reader that minimizes system calls", "read-ahead buffer of 8KB/16KB, satisfy small reads from buffer", "read large blocks from file into buffer, serve byte-by-byte from buffer"),
    ("design a write-ahead log for crash consistency", "append-only log with checksums, fsync after each commit, checkpoint periodically", "write data to log, fsync, then update metadata; on recovery replay log"),
    ("implement memory-mapped I/O for large file access", "mmap with MAP_SHARED, let OS handle paging, use madvise for hints", "map file into virtual address space, access via pointers, OS handles page faults"),
    ("design a file system journaling mechanism", "journal metadata writes before applying to main FS, replay on mount after crash", "journal transaction: write intent log, write data, commit record; on recovery replay"),
    ("implement asynchronous I/O with io_uring on modern Linux", "set up submission/completion queues in shared memory", "IORING_SETUP_SQPOLL for polling mode; supports buffered and direct I/O"),
    ("design a reliable file synchronization protocol for network file systems", "rsync-style delta transfer or NFS with close-to-open consistency", "detect changes by mtime/size/hash, transfer only changed blocks"),
    ("implement a file descriptor pool with caching for high-throughput servers", "keep frequently used fds open, reuse for similar files, LRU eviction", "table of open fds with reference count, access frequency tracking, background eviction"),
]

def _fileio_gen():
    while True:
        for problem, technique, hint in FILEIO_TOPICS:
            inp = pick(
                f"File I/O: {problem}. Design for performance and reliability.",
                f"Systems I/O: {problem}. Implement with efficient buffering.",
                f"Storage systems: {problem}. How would you implement this?",
                f"Given: {problem}. Handle crash recovery, buffering, large files.",
            )
            plan = pick(
                f"<PLAN>File I/O design: {problem}. {technique}: {hint}. Plan: (1) Understand access pattern. (2) Design buffering/caching. (3) Implement consistency mechanism. (4) Handle edge cases: partial writes, concurrent access, disk full. (5) Test with power-loss simulation.</PLAN>",
                f"<PLAN>I/O system for {problem}: {technique}. {hint}. Steps: (1) Choose API. (2) Implement buffer management. (3) Add consistency guarantees. (4) Add error recovery. (5) Benchmark throughput. (6) Tune OS parameters.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Data structures. (2) Core I/O path. (3) Consistency: ordered writes, crash recovery. (4) Performance: read-ahead, write coalescing. (5) Edge cases. (6) Test with fault injection.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing I/O for {problem}: {technique}: {hint}. The gap between CPU speed (ns) and disk speed (ms HDD, 10-100 us SSD) is enormous. Buffered reader: user-space buffer of 4-64KB reduces syscalls from n to n/buffer_size. Async I/O: io_uring uses ring buffers in shared memory for communication without syscalls. Write-ahead logging: before modifying data, write change to log. fsync log. Then apply. On recovery, replay completed entries. Journaling file systems: same principle for metadata. Memory-mapped I/O: maps file pages directly into virtual memory. Access triggers page faults. Modified pages written back by kernel. For io_uring: write SQEs to submission queue, kernel writes CQEs with results. SQPOLL eliminates syscalls entirely.</THINK>",
                f"<THINK>Analyzing I/O for {problem}: {technique}: {hint}. Storage stack: application -> libc -> VFS -> file system -> block layer -> driver -> device. Each layer adds overhead. Direct I/O (O_DIRECT) bypasses page cache, useful for databases with own caching. Buffered: page cache aggregates disk I/O. Read-ahead detects sequential access. Write buffering: writes go to page cache, written back asynchronously. fsync forces dirty pages to stable storage. WAL ensures log entry reaches disk before data change. On recovery: find last valid log entry (checksum/sequence number), apply it. io_uring: allocate SQ and CQ rings, register with kernel via io_uring_setup. For each I/O: fill SQE, advance tail. Optionally call io_uring_enter (not needed with SQPOLL). Process CQEs.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}: {hint}. Buffering strategies: (1) Read: buffer size should match typical request size, page-aligned (4096). Too small: excessive syscalls. Too large: wastes memory. Streaming: 64KB-1MB typical. (2) Write: coalesce small writes. For WAL: each record: sequence number, transaction ID, operation type, data, checksum. Protocol: (1) Write record to WAL buffer. (2) fsync WAL. (3) Apply to main storage. (4) Update checkpoint. On recovery: (1) Read WAL from last checkpoint. (2) Apply unapplied records. (3) Skip incomplete. For mmap: MAP_SHARED for file modification. msync(MS_SYNC) for synchronization. MAP_PRIVATE for COW. For io_uring: fixed files (register fds once), fixed buffers, polling, link chains with IOSQE_IO_LINK.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>I/O system: {problem}. Design: {technique}. {hint}. Implementation: buffering, consistency, crash recovery. Tested: power-loss simulation, concurrent access, large files. Throughput high, cache hit rate good. Edge cases handled.</EXEC>",
                f"<EXEC>File I/O: {problem}. Approach: {technique}. {hint}. Buffered with configurable buffer, WAL for consistency, io_uring for async. Benchmarked. Recovery tested with simulated crashes. Performance near device max.</EXEC>",
                f"<EXEC>I/O implementation: {problem}. {technique}. {hint}. Read-ahead, write coalescing, journaling, mmap access. fsync ordering, checksums, atomic rename. Tested with fault injection. Recovery proven correct.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

CONCURRENCY_TOPICS = [
    ("design a thread pool for a web server handling 100K requests/second", "work-stealing thread pool with per-thread task queues", "each thread has a deque; idle threads steal from others tails to distribute load"),
    ("implement a concurrent hash map with high throughput", "lock striping: partition table into independently locked segments", "striped locks reduce contention: hash to segment, lock only that segment"),
    ("implement a reader-writer lock that prioritizes readers or writers", "rwlock with fairness: mutex plus condition variables plus counters", "track active readers, pending writers; if fairness: new readers block if writers waiting"),
    ("implement a barrier for synchronizing N threads at a checkpoint", "sensing barrier or tree barrier for scalability", "each thread arrives, atomically decrements count; last thread wakes all others"),
    ("implement a work queue with backpressure for producer-consumer", "bounded queue with blocking on full/empty, optional overflow strategies", "blocking: offer blocks if full, poll blocks if empty; alternatives: drop, backpressure signal"),
    ("design a concurrent counter with high scalability", "thread-local counters with periodic global aggregation", "each thread increments local cache-line-aligned counter; reader sums all local counters"),
    ("implement a lock-free stack using CAS with ABA prevention", "linked list with hazard pointers or tagged pointers for ABA", "CAS on top pointer; ABA: use double-tagged pointer or deferred reclamation"),
]

def _concurrency_gen():
    while True:
        for problem, technique, hint in CONCURRENCY_TOPICS:
            inp = pick(
                f"Concurrency: {problem}. Design the concurrent data structure.",
                f"Concurrent programming: {problem}. Handle scalability and correctness.",
                f"Systems concurrency: {problem}. Implement with proper synchronization.",
                f"Given: {problem}. Design for high throughput and thread safety.",
            )
            plan = pick(
                f"<PLAN>Concurrency design: {problem}. {technique}: {hint}. Plan: (1) Define correctness requirements. (2) Choose synchronization primitive. (3) Design data structure with minimal contention. (4) Handle memory ordering. (5) Test with TSan and stress tests. (6) Benchmark scalability.</PLAN>",
                f"<PLAN>Concurrent system for {problem}: {technique}. {hint}. Steps: (1) Analyze contention points. (2) Design granularity. (3) Implement with atomics and barriers. (4) Handle ABA, false sharing, deadlock. (5) Add backpressure if needed. (6) Profile and optimize.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Data layout: cache-line-aligned, no false sharing. (2) Algorithm: lock-based or lock-free. (3) Progress guarantees. (4) Test: 1-256 threads, invariants after each operation. (5) Optimize critical sections.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing concurrent {problem}: {technique}: {hint}. Key challenge: coordinating access to shared state without bottlenecks. Amdahl law limits speedup by serial portions. For thread pools: work stealing balances load naturally. Each thread has deque. Owner pushes/pops one end (LIFO, good cache); thieves steal from other end (FIFO, fairness). For hash map: lock striping divides table into N segments with independent locks. Parallelism up to N. For rwlock: multiple readers can proceed simultaneously. Writer excludes all. Fair version blocks new readers if writer waiting. For barriers: sensing barrier uses count and sense flag. Last thread resets and toggles sense. For lock-free stack: tagged pointer (pointer + version counter) prevents ABA. Hazard pointers track accessed objects.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Concurrency correctness: (1) Safety -- invariants hold, no data races. (2) Liveness -- no deadlock, starvation. (3) Fairness. Memory ordering on weakly-ordered architectures: acquire prevents reordering after; release prevents reordering before. On x86, most ops are acquire/release implicitly. For work-stealing: owner uses non-atomic ops for local deque; only top/bottom indices atomic. For lock striping: number of stripes should be power of two for fast modulo. For rwlock: write-preference avoids writer starvation. For barriers: tree barrier reduces O(N) hot spot to O(log N). For backpressure: credit-based flow control limits in-flight work.</THINK>",
                f"<THINK>Deep implementation of concurrent {problem}: {technique}: {hint}. Cache coherence (MESI/MOESI) means write to cache line invalidates it on all other cores. Key to scalability: threads write to different cache lines. For thread pool: deque layout: bottom (u64, local), top (AtomicU64, shared), tasks array. Bottom/top on separate cache lines. For hash map: segment locks padded to 64 bytes. For concurrent counter: each thread counter at unique cache line (stride = 64 * (threads+1)). For lock-free stack: tagged pointer implemented as 16-byte CAS (CMPXCHG16B) on x86. Testing: ThreadSanitizer, stress tests, model checking.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Concurrent system: {problem}. Design: {technique}. {hint}. Thread-safe, scalable, proper memory ordering. Tested 1-256 threads, TSan clean, no deadlock. Near-linear scaling. Cache contention minimized with per-thread data. ABA handled. Production-ready.</EXEC>",
                f"<EXEC>Concurrency: {problem}. Approach: {technique}. {hint}. Lock-free + lock-based hybrid. All atomics correct ordering. False sharing eliminated. Stress tests pass. Throughput scales with thread count. Edge cases handled.</EXEC>",
                f"<EXEC>Concurrent implementation: {problem}. Method: {technique}. {hint}. Cache-line aligned data structures. Minimal critical sections. Work stealing for balance. TSan validated. Performance: X ops/sec with N threads.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

NETWORKING_TOPICS = [
    ("implement a TCP server that handles 100K concurrent connections", "event-driven architecture with epoll/kqueue/IOCP", "non-blocking sockets, edge-triggered epoll, accept in loop, connection state per fd"),
    ("design a UDP-based reliable transport protocol", "add sequence numbers, ACKs, retransmission, congestion control", "similar to TCP but in userspace; selective ACKs, fast retransmit, CUBIC/BBR congestion"),
    ("implement connection pooling for database access", "maintain pool of persistent connections, acquire/release with timeout", "bounded pool of pre-established connections, thread-safe acquire, health checks"),
    ("design a zero-copy network path from NIC to application", "kernel bypass with DPDK or XDP, or use sendfile/splice", "DPDK: userspace driver, poll for packets, zero-copy; XDP: eBPF at driver level"),
    ("implement TLS handshake and record layer for secure communication", "asymmetric key exchange (ECDHE), symmetric encryption (AES-GCM), HMAC", "handshake: ClientHello -> ServerHello+Cert+KeyExchange -> ClientKeyExchange -> Finished"),
    ("design a consistent hashing ring for distributed key-value store", "hash keys onto ring of virtual nodes, replicas on successors", "keys hash to positions; each node handles range from predecessor to itself; virtual nodes balance load"),
    ("implement TCP congestion control from scratch (Reno/NewReno/CUBIC)", "slow start, congestion avoidance, fast retransmit, fast recovery", "AIMD: additive increase until loss, multiplicative decrease; CUBIC uses cubic function"),
]

def _networking_gen():
    while True:
        for problem, technique, hint in NETWORKING_TOPICS:
            inp = pick(
                f"Networking: {problem}. Design and implement the solution.",
                f"Network systems: {problem}. Handle scale and performance.",
                f"Systems networking: {problem}. Describe your architecture.",
                f"Given: {problem}. Design for reliability and high throughput.",
            )
            plan = pick(
                f"<PLAN>Network design: {problem}. {technique}: {hint}. Plan: (1) Choose I/O model. (2) Define protocol. (3) Implement event loop. (4) Handle buffer management, backpressure, timeouts. (5) Add security. (6) Test with high load, packet loss.</PLAN>",
                f"<PLAN>Network system for {problem}: {technique}. {hint}. Steps: (1) Socket setup. (2) Event loop. (3) Read/write buffering. (4) Protocol parsing. (5) Timeout and error handling. (6) Graceful shutdown. (7) Benchmark.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Data structures. (2) System calls. (3) Edge vs level trigger. (4) Non-blocking I/O. (5) Load balancing. (6) Testing.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing network system: {problem}. {technique}: {hint}. C10K problem evolved to C10M. One thread per connection does not scale beyond few thousand. Event-driven uses small number of threads managing many connections via epoll. Epoll: interest set of fds, wait for events. Edge-triggered: notified only on state change. Must read until EAGAIN. Level-triggered: notified while data available. For 100K connections: single thread or thread per NUMA node. Each connection: receive buffer, send buffer, state machine. Accept: SO_REUSEPORT for kernel-level accept distribution. For reliable UDP: sequence numbers, ACKs, retransmission timer, congestion control. SACK for reporting multiple lost packets. For TLS: ECDHE provides forward secrecy. AES-GCM for authenticated encryption. Handshake: negotiate cipher, exchange keys, switch to encrypted.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Network protocols operate in layers. For reliable UDP: custom transport. Sender maintains send window, sequence numbers. On timeout, retransmit. Handle duplicates, out-of-order. For consistent hashing: hash space partitioned among nodes. Each node handles range to predecessor. Node join/leave remaps O(K/N) keys. Virtual nodes improve balance. For TCP congestion: Reno uses AIMD. Slow start doubles window per RTT until ssthresh. On loss: ssthresh = cwnd/2, cwnd = 1 or ssthresh+3. CUBIC: cubic function of time since loss, RTT-independent. For TLS: handshake establishes shared secret via asymmetric crypto, switches to symmetric. ECDHE ephemeral provides forward secrecy.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}: {hint}. Network optimization: (1) Buffer management: pre-allocate, slab allocator. (2) Vectored I/O: readv/writev. (3) TCP_NODELAY disable Nagle. (4) TCP_DEFER_ACCEPT delay until data. (5) TSO/GSO: NIC segmentation. For epoll: EPOLLONESHOT for edge-triggered to ensure one thread per fd. Re-arm after processing. For DPDK: PMD in userspace, directly access NIC registers. Zero-copy from NIC to app. Polls RX ring, processes, places on TX ring. Requires dedicated cores. XDP: eBPF program at NIC driver level. XDP_DROP achieves 10-20M packets/s for simple DDoS filtering.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Network system: {problem}. Architecture: {technique}. {hint}. Event-driven with epoll, non-blocking I/O, state machines. Tested: 100K connections, throughput X Gbps, p99 latency Y ms. Edge cases: slow clients, partial reads, EAGAIN handled.</EXEC>",
                f"<EXEC>Networking solution: {problem}. Design: {technique}. {hint}. Protocol with state machines. Scalable event loop. Buffer management. Connection pooling. Security: TLS. Benchmarked. Production-ready.</EXEC>",
                f"<EXEC>{problem} implemented. Approach: {technique}. {hint}. Features: reliable transport/secure communication/server. Performance: X connections, Y req/sec. Reliability: retry with backoff, health checks. Tested under failure.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

ASM_TOPICS = [
    ("optimize a hot loop by hand-rolling SIMD assembly", "use SSE/AVX vector instructions to process 4/8/16 elements at once", "load aligned data into XMM/YMM registers, perform packed operations, store results"),
    ("write an efficient memcpy implementation in assembly", "use movdqa/movntdq for aligned large copies, rep movsb for small", "process in forward order with prefetch; non-temporal stores to avoid cache pollution"),
    ("implement a context switch function using inline assembly", "save/restore callee-saved registers, swap stack pointer, manipulate return address", "push r15..rbx, rbp; push return addr; switch rsp; pop return addr; pop rbx..r15; ret"),
    ("write an atomic compare-and-swap with proper memory ordering", "CMPXCHG instruction with LOCK prefix; C11 atomic_compare_exchange_strong", "LOCK CMPXCHG [addr], reg; returns old value and sets ZF if equal"),
    ("implement a spinlock using assembly for x86-64", "LOCK XCHG for acquire, plain store for release; PAUSE in spin loop", "lock: mov 1, eax; lock xchg [lock], eax; test eax, eax; jnz spin; unlock: mov [lock], 0"),
    ("write a fast integer-to-string conversion routine in assembly", "divide by 10 repeatedly storing remainders, then reverse", "for each digit: div r10d; push dx on stack; when quotient 0, pop and convert to ASCII"),
    ("implement a function prologue and epilogue compatible with System V AMD64 ABI", "push rbp; mov rbp, rsp; sub rsp, N; ... ; mov rsp, rbp; pop rbp; ret", "stack frame setup/teardown, align stack to 16 bytes, preserve callee-saved registers"),
]

def _asm_gen():
    while True:
        for problem, technique, hint in ASM_TOPICS:
            inp = pick(
                f"Assembly optimization: {problem}. Write the assembly implementation.",
                f"Low-level assembly: {problem}. Implement with optimal instruction choice.",
                f"Systems programming: {problem}. Hand-write in assembly for performance.",
                f"Given: {problem}. Design for correctness and optimal performance.",
            )
            plan = pick(
                f"<PLAN>Assembly implementation: {problem}. {technique}: {hint}. Plan: (1) Understand x86-64 ISA and ABI. (2) Map problem to instructions. (3) Handle register allocation. (4) Instruction scheduling. (5) Alignment and cache effects. (6) Test with inline asm in C, verify with disassembly.</PLAN>",
                f"<PLAN>Assembly design for {problem}: {technique}. {hint}. Steps: (1) Define function signature. (2) Prologue save regs. (3) Core loop. (4) Epilogue restore. (5) Optimize: minimize instructions, avoid stalls. (6) Benchmark against compiler output.</PLAN>",
                f"<PLAN>Low-level implementation: {problem}. {technique}. {hint}. Plan: (1) Register usage. (2) Instruction selection. (3) Control flow. (4) Memory access. (5) Inline asm constraints. (6) Test with various sizes.</PLAN>",
            )
            think = pick(
                f"<THINK>Writing assembly for {problem}: {technique}. {hint}. x86-64: 16 GPRs (RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP, R8-R15). Calling convention: RDI, RSI, RDX, RCX, R8, R9 for integer args. Return in RAX. Callee-saved: RBX, RBP, R12-R15. SIMD: 16 XMM (128-bit SSE) or YMM (256-bit AVX). For memcpy: movdqa for aligned, movdqu for unaligned. movntdq bypasses cache. Prefetch (prefetcht0). For context switch: save/restore callee-saved registers and stack pointer. System V red zone: 128 bytes below RSP that signal handlers may not clobber. For atomics: LOCK prefix makes instruction atomic on multi-processor systems. CMPXCHG compares and conditionally exchanges. For spinlock: LOCK XCHG provides atomic test-and-set. PAUSE instruction hints CPU were spinning.</THINK>",
                f"<THINK>Analyzing assembly for {problem}: {technique}. {hint}. x86-64 instruction encoding: instructions can be 1-15 bytes. REX prefix for extended registers. VEX prefix for AVX. Memory addressing: [base + index*scale + displacement]. For SIMD: data alignment critical -- movdqa requires 16-byte alignment; movdqu tolerates unaligned but slower. For memcpy: align destination to 16 bytes, copy in 16-byte chunks. For large copies ( > 1MB), use non-temporal stores to avoid cache pollution. For context switch: must handle red zone (128 bytes below RSP). Use 32-byte alignment per ABI. For stack frames: push rbp; mov rbp, rsp; sub rsp, N (allocate frame). After body: mov rsp, rbp; pop rbp; ret. Must maintain 16-byte stack alignment before call.</THINK>",
                f"<THINK>Deep assembly implementation of {problem}: {technique}. {hint}. Optimization techniques: (1) Instruction selection: use fastest instruction for task. (2) Scheduling: interleave independent instructions to hide latency. (3) Loop unrolling: reduce loop overhead, enable SIMD. (4) Register allocation: keep frequently used values in registers. (5) Memory access: align data, prefetch, use streaming stores. For SIMD: loop vectorization processes multiple elements per iteration. Remaining elements (if n not multiple of vector width) handled with scalar loop. For context switch: Assembly is required because C cannot express register save/restore precisely. The switch function: takes pointers to current and next context blocks. Saves all callee-saved registers into current. Loads from next. Returns -- but returns to the instruction after the call that saved next context.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Assembly implementation: {problem}. {technique}. {hint}. Instructions selected for optimal performance. Proper calling convention and register usage. Tested with various inputs. Performance measured against compiler output. Correctness verified with exhaustive testing.</EXEC>",
                f"<EXEC>Assembly complete: {problem}. Method: {technique}. {hint}. Optimized instruction selection and scheduling. Register allocation efficient. Memory access aligned. ABI compliant. Performance: X% faster than compiler output for this specific case.</EXEC>",
                f"<EXEC>Low-level implementation: {problem}. {technique}. {hint}. Assembly with proper prologue/epilogue. All edge cases handled. Tested for correctness and performance. Instruction cache optimized. Ready for production use in performance-critical path.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

PROFILING_TOPICS = [
    ("identify a performance bottleneck in a CPU-bound application", "use perf stat/record/report to sample CPU cycles and identify hot functions", "run perf record -F 99 -g ./app; perf report to see call graph; focus on hottest paths"),
    ("detect memory allocation hotspots causing GC pressure", "use heap profiling (perf record with probe, jemalloc heap profiling, or Valgrind massif)", "track malloc/free call stacks; identify frequent allocations; optimize with object pooling"),
    ("analyze cache miss rates and propose data layout improvements", "use perf stat -e cache-misses,cache-references,L1-dcache-load-misses", "high miss rates suggest poor spatial/temporal locality; reorganize structs for sequential access"),
    ("find lock contention in a multi-threaded application", "use perf record with lock events or Thread Sanitizer, or mutrace for POSIX threads", "identify highly contended locks; consider lock striping, RCU, or lock-free data structures"),
    ("trace system call overhead in I/O-bound workloads", "use strace -c for syscall summary or perf trace for per-syscall timing", "count syscalls per operation; batch small I/Os; use io_uring for zero-syscall I/O"),
    ("profile memory bandwidth usage and NUMA effects", "use perf stat -e instructions,cycles,ref-cycles,mem-loads,mem-stores", "compare local vs remote memory access latency; bind memory and threads to same NUMA node"),
]

def _profiling_gen():
    while True:
        for problem, technique, hint in PROFILING_TOPICS:
            inp = pick(
                f"Profiling: {problem}. Use profiling tools to identify the issue.",
                f"Performance analysis: {problem}. What tools and metrics to use?",
                f"Systems profiling: {problem}. How to locate and fix the bottleneck?",
                f"Given: {problem}. Profile and propose optimization strategies.",
            )
            plan = pick(
                f"<PLAN>Profiling approach: {problem}. {technique}: {hint}. Plan: (1) Define performance baseline. (2) Choose profiling tool. (3) Collect performance data. (4) Identify bottleneck from metrics. (5) Form hypothesis and implement fix. (6) Re-profile to verify improvement.</PLAN>",
                f"<PLAN>Performance analysis: {problem}. {technique}. {hint}. Steps: (1) Run profiler with appropriate events. (2) Analyze output: hot functions, call graphs, event counts. (3) Correlate with source code. (4) Propose optimization. (5) Implement and measure. (6) Repeat if new bottleneck emerges.</PLAN>",
                f"<PLAN>Profile and optimize: {problem}. {technique}. {hint}. Plan: (1) Setup profiling environment. (2) Collect samples. (3) Analyze bottleneck. (4) Design fix. (5) Implement. (6) Validate improvement with same profiling setup.</PLAN>",
            )
            think = pick(
                f"<THINK>Profiling {problem}: {technique}. {hint}. Performance analysis is iterative. First: establish baseline metrics. For CPU-bound: perf record samples program counter at frequency (e.g., 99 Hz). Collect call stacks with --call-graph dwarf. perf report shows functions consuming most CPU. Hot loops, tight functions, and cache-miss-heavy code appear at top. For memory: massif (Valgrind) tracks heap usage over time. Peak memory, allocation frequency, and call stacks of largest allocations. jemalloc profiling shows per-size-class stats. For cache: perf stat -e cache-misses gives miss rate. High L1 miss rates ( > 10%) indicate poor data locality. LLC miss rates ( > 5%) indicate working set exceeds cache. For lock contention: mutrace tracks mutex contention. High contention means threads spend time waiting. strace -c summarizes syscall counts and times. High count means excessive kernel crossings. Profile-guided optimization: use real workloads, not microbenchmarks. Profile in production-like environment.</THINK>",
                f"<THINK>Analyzing {problem}: {technique}. {hint}. Perf tools: perf stat (aggregate counts), perf record (sampling), perf report (browser), perf annotate (instruction-level), perf top (live). For memory: perf mem records memory accesses and latency. For scheduler: perf sched records scheduling events. For tracing: ftrace, eBPF, bpftrace. Key metrics: IPC (instructions per cycle) -- low IPC indicates stalls (cache misses, branch mispredicts, dependency chains). Branch misprediction rate -- >5% hurts. TLB misses -- high TLB miss rate indicates large working set; use huge pages. For NUMA: remote access latency is 1.5-2x local. Use numactl to bind. For GC pressure: number of allocations per transaction, survival rate, pause times. Reduce allocation rate with object pools, stack allocation, value types. For I/O: IOPS, throughput, latency percentiles, queue depth. The bottleneck could be at any level; profile top-down from application to hardware.</THINK>",
                f"<THINK>Deep profiling of {problem}: {technique}. {hint}. Profiling methodology: (1) Ask the right question: is it CPU, memory, I/O, or lock contention? (2) Choose the right tool: perf for CPU/memory, strace for syscalls, mutrace for locks, flamegraph for visualization. (3) Collect data with minimal perturbation (perf sampling has low overhead; strace is expensive). (4) Statistical profiling: perf stat -d gives detailed hardware event counts. perf record -e cache-misses records samples on cache miss events. (5) Bottleneck identification: the function consuming most CPU, the lock with highest contention, the syscall with most invocations. (6) Use Amdahl law: optimize the biggest bottleneck first. After optimization, the next bottleneck emerges. (7) Validate: the fix should improve the metric by the expected amount. If not, revisit hypothesis. Continuous profiling in production (like Google's CPPROF) catches regressions early.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Profiling analysis: {problem}. Used {technique}. {hint}. Bottleneck identified: top function/syscall/lock consuming X% of resources. Optimization implemented. Re-profile shows Y% improvement. Metrics: cycles, cache misses, IPC, lock contention all improved.</EXEC>",
                f"<EXEC>Performance profile: {problem}. Tools: {technique}. {hint}. Hot path identified at specific function/module. Root cause determined and fixed. Before/after comparison shows significant improvement in key metric. Bottleneck shifted to next subsystem.</EXEC>",
                f"<EXEC>Profiling complete: {problem}. Method: {technique}. {hint}. Key findings: CPU hotspots, cache misses, lock contention, I/O bottlenecks quantified. Fixes applied and re-validated. Performance improvement: X% reduction in latency or Y% increase in throughput.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

CFFI_TOPICS = [
    ("call a C library function from Python efficiently", "use ctypes or cffi module; pre-declare function signatures and types", "create FFI object, load .so, declare arg/return types for performance"),
    ("design a Python C extension module for numerical computation", "write C code with Python C API (PyObject, PyArg_ParseTuple, Py_BuildValue)", "implement compute function, create module definition, handle reference counting"),
    ("pass large numpy arrays between Python and C without copying", "use numpy C API or buffer protocol; share memory via pointer", "retrieve data pointer from numpy array, pass to C, manipulate in place"),
    ("handle memory management when mixing Python and C allocations", "use PyMem_Malloc/PyMem_Free for Python-managed memory; document ownership", "Python objects created in C must be reference counted; C allocations must be freed by C"),
    ("implement a callback function in Python that C code can invoke", "define PyObject* callback; use PyObject_CallObject to invoke; thread safety", "store callable as PyObject*, increment ref count, call with args tuple"),
]

def _cffi_gen():
    while True:
        for problem, technique, hint in CFFI_TOPICS:
            inp = pick(
                f"C FFI integration: {problem}. Design the interop layer.",
                f"Python-C bridge: {problem}. Implement with proper memory management.",
                f"Foreign function interface: {problem}. Handle cross-language concerns.",
                f"Given: {problem}. Design for performance and correctness.",
            )
            plan = pick(
                f"<PLAN>C FFI: {problem}. {technique}: {hint}. Plan: (1) Define C API surface. (2) Choose binding method (ctypes, cffi, Cython, Pybind11). (3) Declare types and function signatures. (4) Handle memory ownership. (5) Manage reference counting for Python objects. (6) Test with valgrind for leaks.</PLAN>",
                f"<PLAN>FFI design for {problem}: {technique}. {hint}. Steps: (1) Load shared library. (2) Define argument/return types. (3) Allocate buffers appropriately. (4) Call C function. (5) Convert results. (6) Clean up resources. (7) Handle errors from C side.</PLAN>",
                f"<PLAN>Python-C interop: {problem}. {technique}. {hint}. Plan: (1) Interface design. (2) Data marshaling strategy. (3) Memory ownership protocol. (4) Error propagation. (5) Thread safety. (6) Testing for memory leaks and crashes.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing C FFI for {problem}: {technique}. {hint}. Python-C interop requires careful memory management. Python uses reference counting; C uses malloc/free. The boundary must be explicit about ownership. For ctypes: declare argtypes and restype for each function; this enables type checking and conversion. For numpy: the buffer protocol exposes the underlying data pointer. Py_buffer structure gives pointer, shape, strides. C code can read/write directly, avoiding copies. For callbacks: C code needs a function pointer; ctypes creates one from a Python callable. The callback receives raw C types; Python converts them. Thread safety: the GIL protects Python objects, but C code may release the GIL. Must re-acquire GIL (PyGILState_Ensure) when calling Python from C. For C extensions: the module definition struct specifies name, methods, doc. Each method receives PyObject* self and PyObject* args. PyArg_ParseTuple extracts C values. Return values: PyLong_FromLong, PyFloat_FromDouble, Py_BuildValue for tuples. Exception handling: return NULL with PyErr_SetString. Reference counting: INCREF when storing, DECREF when done. Memory management is the primary source of bugs in FFI.</THINK>",
                f"<THINK>Analyzing FFI for {problem}: {technique}. {hint}. Performance considerations: (1) Minimize crossings: batch calls instead of per-element. (2) Type conversion overhead: ctypes converts every argument; for arrays, use pointer passing. (3) Buffer allocation: pre-allocate and reuse buffers. (4) GIL management: release GIL in long-running C functions for parallelism. For large numpy arrays: retrieve pointer via ndarray.ctypes.data or PyArray_DATA macro. The C function receives void* and dimensions. It operates in place or writes to output array. For callbacks: Python function called from C must be slowed by: (1) Acquiring GIL. (2) Creating Python arguments from C values. (3) Calling function. (4) Decoding return value. For hot callbacks, consider batch processing or rewriting in C. For Cython: generates C code from Python-like syntax. Supports typed variables for zero-overhead loops. Easier than manual C API for numerical work. For pybind11: C++ binding with automatic type conversion and STL support. Header-only, modern C++11.</THINK>",
                f"<THINK>Deep FFI implementation for {problem}: {technique}. {hint}. The FFI boundary is where crashes and leaks most often occur. Memory ownership rules: (1) If C allocates and returns, Python should free via C's free function. (2) If Python passes pointer to C, C should not store it beyond the call unless documented. (3) Python objects created in C: return with +1 reference (caller owns). (4) C callbacks that store Python objects must INCREF. The PyObject lifecycle: created (refcount=1), passed around (refcount++ on store, -- on discard), destroyed (refcount hits 0). Every INCREF needs matching DECREF. For C extensions: the tp_dealloc slot handles object destruction. Type objects: PyTypeObject struct specifies behavior. Heap types (created at runtime) vs static types. Module initialization: PyMODINIT_FUNC init<name>(void). Python 3: use PyModuleDef and module factory. For all FFI: (1) Always check for NULL returns. (2) Validate input pointers. (3) Handle errors gracefully. (4) Document memory ownership. (5) Test with address sanitizer (ASAN) and LeakSanitizer.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>FFI integration: {problem}. {technique}. {hint}. Interface defined with clear ownership. Memory management correct (no leaks). Type conversions handled. Tested with ASAN and valgrind. Performance: crossing overhead minimized via batching and zero-copy.</EXEC>",
                f"<EXEC>C FFI solution: {problem}. Approach: {technique}. {hint}. Binding implemented. Memory ownership documented. GIL management correct. Callbacks working in both directions. Tested for memory leaks and crash safety. Production-ready.</EXEC>",
                f"<EXEC>Python-C interop: {problem}. Design: {technique}. {hint}. Shared library loaded. Functions callable with correct types. Numpy arrays passed zero-copy. Reference counting correct. GIL released during long C operations. All error cases handled without crash.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "systems")

EMBEDDED_TOPICS = [
    ("design a bare-metal program for an ARM Cortex-M microcontroller", "direct register access, interrupt handlers, linker script for memory layout", "set up vector table, initialize .data/.bss, configure clocks and peripherals, enter main loop"),
    ("implement a real-time task scheduler on a microcontroller", "timer-based tick, round-robin or priority-based task switching", "SysTick interrupt increments tick; scheduler runs at tick; tasks yield or are preempted"),
    ("write an interrupt-driven UART driver for an embedded system", "configure UART registers, enable RX/TX interrupts, ring buffer for data", "RX interrupt: read byte into ring buffer; TX interrupt: write next byte from ring buffer"),
    ("implement a watchdog timer with proper petting strategy", "configure watchdog to reset if not petted within timeout", "pet in main loop only if system healthy; use independent vs window watchdog"),
    ("design a low-power sleep mode with wake-on-interrupt", "enter WFI/WFE sleep mode, configure wake-up sources (GPIO, timer, comms)", "enter low-power mode, peripheral still running for wake condition, ISR resumes main"),
    ("implement a bootloader for firmware updates over UART", "bootloader at flash start, application at higher address, jump to app vector table", "on reset, check for update request; if yes, receive new firmware over UART and write to flash; else jump to app"),
    ("design a DMA-based data transfer between peripheral and memory", "configure DMA controller: source, destination, transfer size, circular mode", "peripheral requests DMA transfer; DMA moves data without CPU; interrupt on completion or half-completion"),
]

def _embedded_gen():
    while True:
        for problem, technique, hint in EMBEDDED_TOPICS:
            inp = pick(
                f"Embedded systems: {problem}. Design for bare-metal or RTOS.",
                f"Embedded programming: {problem}. Handle resource constraints.",
                f"Microcontroller firmware: {problem}. Implement with minimal overhead.",
                f"Given: {problem}. Design for real-time and low-power constraints.",
            )
            plan = pick(
                f"<PLAN>Embedded design: {problem}. {technique}: {hint}. Plan: (1) Understand hardware: memory map, peripherals, interrupts. (2) Set up toolchain and linker script. (3) Implement startup code. (4) Configure peripherals. (5) Implement main logic. (6) Test on hardware or emulator. (7) Optimize for size/power/speed.</PLAN>",
                f"<PLAN>Embedded solution for {problem}: {technique}. {hint}. Steps: (1) Hardware initialization. (2) Peripheral configuration. (3) Interrupt setup. (4) Main loop. (5) Low-power mode. (6) Debug with UART or SWO. (7) Verify with oscilloscope/logic analyzer.</PLAN>",
                f"<PLAN>Firmware design: {problem}. {technique}. {hint}. Plan: (1) Clock configuration. (2) GPIO/peripheral setup. (3) Interrupt handlers. (4) Data structures (buffers, queues). (5) Main logic. (6) Error handling and watchdog. (7) Power management.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing embedded {problem}: {technique}. {hint}. Embedded systems have limited resources: KB of RAM, MHz CPU, no MMU, no OS. Code must be deterministic and efficient. For bare-metal: startup code in assembly sets up vector table (stack pointer, reset handler, exception handlers). C runtime init: clear BSS, copy data segment. Then main(). For scheduler: SysTick generates periodic interrupt. Simple scheduler maintains task list with function pointers and states (READY, RUNNING, WAITING). Each tick, scheduler checks if current task exceeded time slice and switches. Cooperative: tasks yield explicitly. Preemptive: every tick can switch. For UART driver: ring buffer decouples interrupt from main code. RX interrupt writes byte to tail of buffer. Main code reads from head. This avoids losing bytes and keeps interrupt handler fast. For watchdog: pet at specific point in main loop; if system hangs, watchdog resets. Independent watchdog uses internal RC oscillator (always running). Window watchdog requires pet within a specific time window. For low-power: WFI (Wait For Interrupt) stops CPU until interrupt. Configure wake-up sources (EXTI on GPIO, RTC alarm, UART RX). Preserve peripheral states across sleep. For bootloader: first sector of flash contains bootloader. On reset, check GPIO or flash flag for update mode. If update: receive binary over UART (XMODEM/YMODEM or custom protocol), write to flash sectors, verify CRC, jump to application. Jump: disable interrupts, set vector table offset (SCB->VTOR), load stack pointer from app vector table, load program counter from app vector table + 4. For DMA: configure source (peripheral data register), destination (memory buffer), transfer count. Circular mode: after completion, count resets to initial value, continues transferring. Half-complete interrupt lets CPU process first half while DMA fills second half (double buffering). This is critical for high-speed ADC or audio.</THINK>",
                f"<THINK>Analyzing embedded {problem}: {technique}. {hint}. Resource constraints drive every decision. Use fixed-point instead of float. Use lookup tables instead of computation. Use interrupt-driven I/O instead of polling. Minimize ISR time -- just copy data, set flag. Main loop handles processing. For real-time: worst-case execution time (WCET) analysis. Critical sections disable interrupts briefly. Priority inversion: high-priority task waiting on low-priority task's resource. Solution: priority inheritance or priority ceiling protocol. For watchdog: safety-critical systems use dual watchdogs or windowed watchdogs. For bootloader: must handle power loss during update -- use two-slot (A/B) update or recoverable bootloader. For DMA: double buffering allows continuous data flow. DMA completion interrupt swaps active buffer. For low-power: measure active current vs sleep current. Wake-up time matters. Deep sleep (standby) has lowest current but longest wake-up. Keep RTC running for periodic wake-up. For debugging: no stdout; use UART debug output, SWO (Serial Wire Output), or GPIO toggles with logic analyzer. For all: use volatile for memory-mapped registers. Use __attribute__((interrupt)) for ISRs. Beware of compiler optimization reordering critical code. Use memory barriers when needed.</THINK>",
                f"<THINK>Deep embedded implementation of {problem}: {technique}. {hint}. The embedded system has: (1) Flash for code (0 wait states at low freq, wait states at high freq). (2) RAM for data (SRAM, maybe separate for core/peripheral). (3) Peripherals mapped to memory addresses. (4) Interrupt controller (NVIC on ARM). Linker script: defines memory regions (FLASH at 0x08000000, RAM at 0x20000000), stack and heap symbols. Startup code: (1) Define weak default handlers for all interrupts. (2) Provide strong override for specific handlers. (3) Call __libc_init_array for C++ constructors. (4) Call main(). For Cortex-M: vector table at start of flash: first word = initial SP, second word = reset handler. For scheduler: the PendSV exception is used for context switching (lowest priority, triggered by software). On SysTick: set PendSV pending bit. In PendSV handler: save current context (registers), load next context, return. For register manipulation: use bit-banding or read-modify-write with atomic RMW instructions. For timing: use SysTick for millisecond counter, TIM for microsecond resolution. For all: debug with semihosting or SWO for printf without UART. Test with hardware-in-the-loop, fault injection testing for robustness.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Embedded solution: {problem}. Design: {technique}. {hint}. Firmware implemented for ARM Cortex-M. Startup code, linker script, peripheral configuration, main logic. Tested on hardware/emulator. Real-time constraints met. Power consumption measured. Watchdog tested with fault injection.</EXEC>",
                f"<EXEC>Firmware: {problem}. {technique}. {hint}. Bare-metal or RTOS implementation. Interrupt-driven with proper priority. Memory efficient (KB RAM). Real-time deadlines verified with worst-case analysis. Debug via UART/SWO. Production-ready with watchdog and error handling.</EXEC>",
                f"<EXEC>Embedded implementation: {problem}. Approach: {technique}. {hint}. Hardware abstraction layer, peripheral drivers, main application logic. Tested: unit tests on host, integration on target. Power: active/sleep modes measured. DMA for zero-CPU data transfer. Bootloader with A/B update support.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "systems")

def chunk_7_gen():
    gens = [_memory_gen(), _process_gen(), _ipc_gen(), _fileio_gen(), _concurrency_gen(),
            _networking_gen(), _asm_gen(), _profiling_gen(), _cffi_gen(), _embedded_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════════════════════════════════════════════════════════
# Chunk 8: Machine Learning & AI Theory
# ═══════════════════════════════════════════════════════════════════════════

SUPERVISED_TOPICS = [
    ("design a linear regression model with multiple features, detect and handle multicollinearity", "use VIF (Variance Inflation Factor) to detect; use ridge regression (L2) or PCA for correlated features", "VIF > 10 suggests severe multicollinearity; ridge shrinks coefficients; PCA decorrelates"),
    ("implement a decision tree with pruning to prevent overfitting", "recursive splitting with information gain/gini impurity; post-prune with validation set", "pre-prune: max_depth, min_samples_split; post-prune: cost complexity pruning"),
    ("design a logistic regression model for imbalanced binary classification", "use class weights, SMOTE oversampling, or threshold moving to handle imbalance", "weighted loss function; generate synthetic minority samples; adjust decision threshold"),
    ("implement a support vector machine with RBF kernel from scratch", "dual formulation with kernel trick; quadratic programming or SMO algorithm", "map to higher-dimensional space implicitly; SMO (Sequential Minimal Optimization) solves QP efficiently"),
    ("design a k-nearest neighbors classifier for large datasets", "use KD-tree or ball tree for efficient approximate nearest neighbor search", "tree structures reduce O(n) search to O(log n); approximate methods for high dimensions"),
    ("implement a neural network classifier with one hidden layer using backpropagation", "forward pass, compute loss, backpropagate gradients, update weights via SGD", "backprop computes gradients via chain rule; SGD updates w = w - lr * dw"),
    ("design a feature engineering pipeline for tabular data with missing values", "impute (mean/median/KNN/mice), encode (one-hot/label/target), scale (standard/minmax/robust)", "handle missing data before encoding; use KNN imputer for complex relationships; robust scaler for outliers"),
]

def _supervised_gen():
    while True:
        for problem, technique, hint in SUPERVISED_TOPICS:
            inp = pick(
                f"Supervised learning: {problem}. Design and implement the solution.",
                f"ML modeling: {problem}. Choose the right algorithm and justify.",
                f"Given: {problem}. Handle data preprocessing, model selection, evaluation.",
                f"Machine learning: {problem}. Implement with proper validation.",
            )
            plan = pick(
                f"<PLAN>Supervised learning approach: {problem}. {technique}: {hint}. Plan: (1) Explore data: distributions, correlations, missing values. (2) Preprocess: handle missing, encode categoricals, scale features. (3) Split: train/validation/test. (4) Model: {technique}. (5) Tune hyperparameters via cross-validation. (6) Evaluate: accuracy, precision, recall, F1, AUC-ROC. (7) Validate on held-out test set.</PLAN>",
                f"<PLAN>ML solution for {problem}: {technique}. {hint}. Steps: (1) Data quality assessment. (2) Feature engineering. (3) Model selection based on problem type and size. (4) Training with regularization. (5) Hyperparameter optimization. (6) Evaluation with appropriate metrics. (7) Interpretation: feature importance, SHAP values.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Problem framing: regression or classification. (2) Baseline model. (3) Feature processing. (4) Model implementation with loss function. (5) Optimization: gradient descent or closed form. (6) Regularization to prevent overfitting. (7) Cross-validation and final evaluation.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing supervised model for {problem}: {technique}. {hint}. The key is understanding the bias-variance trade-off. {technique} addresses this through {hint}. Linear models: low variance, high bias. Tree-based: low bias, high variance (mitigated by pruning/ensembling). For multicollinearity: OLS coefficients become unstable and uninterpretable. Ridge adds L2 penalty that shrinks correlated features together. PCA creates orthogonal components. For imbalanced data: accuracy is misleading; use precision-recall or AUC. SMOTE creates synthetic examples along lines between minority class neighbors. For decision trees: impurity measures (Gini: 2p(1-p), Entropy: -p*log(p)). Split on feature with highest information gain. Pruning reduces overfitting: cost complexity pruning finds subtree minimizing R + alpha*|leaves|. For SVM: hinge loss with kernel trick. RBF kernel gamma controls RBF width. C controls margin violation penalty. For KNN: curse of dimensionality means distance metrics become meaningless in high dimensions. Feature selection or dimensionality reduction before KNN. For neural nets: universal approximation theorem: one hidden layer can approximate any continuous function. Backpropagation: compute gradients of loss w.r.t each weight. Vanishing gradient with sigmoid; ReLU helps. For all: cross-validation (k-fold) estimates generalization error. Hyperparameter tuning: grid search vs random search vs Bayesian optimization.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Model evaluation: never evaluate on training data. Use stratified k-fold for classification to maintain class proportions. For regression: MSE, MAE, R^2, adjusted R^2. For classification: confusion matrix, precision, recall, F1, ROC-AUC. Feature importance: coefficients (linear), feature_importances_ (tree), permutation importance (model-agnostic), SHAP (game-theoretic). For the specific problem: {hint} guides implementation choices. Feature engineering: domain knowledge is critical. Interaction features (product of two features), polynomial features, binning, one-hot encoding with handling of rare categories. Target encoding: replace category with mean of target (risk of leakage, use cross-validation). For all: establish baseline (mean/majority class) before building complex models. Start simple, then add complexity only if baseline is beaten.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. ML pipeline: (1) Data ingestion and validation (schema, statistics). (2) Preprocessing: sklearn ColumnTransformer for different feature types. (3) Model training with early stopping if applicable. (4) Hyperparameter tuning with Optuna or GridSearchCV. (5) Ensemble if beneficial: averaging, stacking, boosting. (6) Model interpretation: partial dependence plots, SHAP summary plot. For linear models: closed form (normal equation) for small n; SGD for large n. Regularization: L1 (lasso) for feature selection, L2 (ridge) for shrinkage, ElasticNet for both. For neural nets: initialization (He for ReLU, Xavier for tanh), optimizer (Adam, SGD with momentum), learning rate schedule (step decay, cosine annealing), batch normalization for training stability. For all: preventing data leakage is paramount. Any preprocessing that uses target information must be fit only on training data. Cross-validation must include all preprocessing steps. Test set used only once at the very end.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Supervised learning: {problem}. Model: {technique}. {hint}. Preprocessing applied, model trained and tuned. Evaluation: cross-val scores good, test performance strong. Feature importance analyzed. Bias-variance trade-off balanced with regularization. Ready for deployment with monitoring.</EXEC>",
                f"<EXEC>ML solution: {problem}. Approach: {technique}. {hint}. Data preprocessing complete. Model implemented and validated. Hyperparameters optimized via CV. Metrics: accuracy X%, F1 Y, AUC Z. Feature engineering with domain knowledge. Overfitting prevented with regularization and pruning.</EXEC>",
                f"<EXEC>Supervised model: {problem}. Method: {technique}. {hint}. Pipeline: ingest, preprocess, train, tune, evaluate. All preprocessing fitted on train only. No data leakage. Cross-validation used. Test set results final. Model interpretable via SHAP/coefficients.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

UNSUPERVISED_TOPICS = [
    ("implement k-means clustering from scratch with proper initialization", "k-means++ initialization, iterative assignment and update until convergence", "k-means++ chooses distant initial centroids; assign each point to nearest; recompute centroids"),
    ("design a hierarchical clustering algorithm with dendrogram visualization", "agglomerative clustering: each point starts as own cluster, merge closest pairs", "single/average/complete linkage define inter-cluster distance; dendrogram shows merge history"),
    ("implement DBSCAN density-based clustering for arbitrary shapes", "core points have minPts within eps radius; expand clusters from core points", "identify core points, density-reachability connects clusters, noise points unassigned"),
    ("design a PCA (Principal Component Analysis) for dimensionality reduction", "compute covariance matrix, eigenvectors/eigenvalues, project top k components", "center data, compute SVD of data matrix, select top k singular vectors"),
    ("implement t-SNE or UMAP for visualizing high-dimensional data", "t-SNE: minimize KL divergence between high-D and low-D pairwise similarities", "perplexity balances local vs global structure; UMAP faster and better preserves global structure"),
    ("design an anomaly detection system using isolation forest", "random forests isolate anomalies with fewer splits; anomaly score based on path length", "anomalies are few and different -- easier to isolate; path length shorter for anomalies"),
    ("implement a Gaussian Mixture Model for soft clustering", "expectation-maximization: E-step computes responsibilities, M-step updates parameters", "E-step: posterior probability of each cluster given data; M-step: update means, covariances, weights"),
]

def _unsupervised_gen():
    while True:
        for problem, technique, hint in UNSUPERVISED_TOPICS:
            inp = pick(
                f"Unsupervised learning: {problem}. Design and implement the approach.",
                f"Given: {problem}. What algorithm to use and how to validate?",
                f"Clustering/dimensionality reduction: {problem}. Implement with proper evaluation.",
                f"Unsupervised method: {problem}. Handle scaling and parameter selection.",
            )
            plan = pick(
                f"<PLAN>Unsupervised approach: {problem}. {technique}: {hint}. Plan: (1) Scale/normalize data. (2) Choose algorithm based on data characteristics. (3) Implement core algorithm. (4) Determine hyperparameters (k, eps, perplexity). (5) Validate: silhouette score, elbow method, visualization. (6) Interpret results.</PLAN>",
                f"<PLAN>Unsupervised solution for {problem}: {technique}. {hint}. Steps: (1) Data preprocessing: standardize, handle missing. (2) Algorithm selection. (3) Implementation. (4) Hyperparameter tuning. (5) Evaluation metrics: inertia, silhouette, Davies-Bouldin. (6) Visualization: 2D projection for inspection.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Understand data structure. (2) Choose unsupervised method. (3) Implement. (4) Determine parameters via heuristics. (5) Validate with internal metrics. (6) If available, compare with external labels. (7) Visualize and report.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing unsupervised model for {problem}: {technique}. {hint}. Unsupervised learning finds structure without labels. For clustering: k-means assumes spherical clusters of equal size; hierarchical captures arbitrary shapes with dendrogram; DBSCAN handles noise and arbitrary shapes but sensitive to eps parameter. For dimensionality reduction: PCA finds orthogonal directions of maximum variance; t-SNE preserves local neighborhoods (perplexity parameter balances local/global); UMAP is faster and better preserves global structure. For anomaly detection: isolation forest isolates anomalies in fewer splits because anomalies are few and different. For GMM: soft clustering with probabilistic assignments. EM algorithm alternates: E-step computes responsibility (probability point belongs to each cluster); M-step updates parameters. GMM can model elliptical clusters of different sizes. Validation: clustering is inherently hard to validate without labels. Silhouette score (how similar point is to its own cluster vs others) ranges [-1, 1], higher better. Elbow method: plot inertia vs k, look for elbow. Domain knowledge is the ultimate validator. For high-dimensional data: curse of dimensionality affects distance-based methods. PCA as preprocessing before clustering.</THINK>",
                f"<THINK>Analyzing {problem}: {technique} with {hint}. Data scaling is critical for distance-based methods (k-means, DBSCAN, PCA). Use StandardScaler (z-score) or MinMaxScaler. For k-means: k-means++ initialization prevents poor local optima. Run multiple restarts, pick best inertia. For hierarchical: linkage choice affects clustering structure. Single linkage creates long chains; complete creates compact clusters; average balanced. Dendrogram cutoff determines cluster count. For DBSCAN: eps determines neighborhood size; minPts determines density threshold. K-distance graph helps choose eps: find elbow in sorted distances to k-th nearest neighbor. For PCA: explained variance ratio shows how much information each component captures. Scree plot selects k. For t-SNE/UMAP: use for visualization, not for feature extraction (stochastic, not reproducible with different random seeds). For isolation forest: contamination parameter estimates proportion of anomalies. Path length normalization: anomaly score = 2^(-E(h(x))/c(n)). Score close to 1 indicates anomaly. For all: unsupervised methods require careful hyperparameter tuning. Grid search over parameters with internal validation metrics. Visual inspection of results is essential.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. For k-means: initialization (k-means++), assignment (compute distances to centroids), update (mean of assigned points), convergence (centroids stop changing). Complexity: O(n*k*d*i). Lloyd algorithm. Mini-batch k-means for large datasets. For PCA: centered data matrix X (n x d). SVD: X = U*S*V^T. Principal components = columns of V. Projection = X*V_k. Explained variance = S_k^2 / sum(S^2). For t-SNE: computes pairwise similarities in high-D (Gaussian, perplexity-controlled). In low-D: student-t distribution for similarities. Gradient descent minimizes KL(P||Q). Perplexity (typically 5-50) controls Gaussian variance. For UMAP: builds fuzzy simplicial set representation, then optimizes low-D embedding with cross-entropy loss. Much faster than t-SNE for large datasets. For GMM: EM algorithm is guaranteed to converge to local optimum. Initialization: k-means provides good starting point. Components: multivariate Gaussian with full/tied/diag/spherical covariance. BIC/AIC for model selection. For all: check for convergence, handle degenerate cases (empty clusters, singular covariance), use multiple random initializations.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Unsupervised learning: {problem}. Method: {technique}. {hint}. Data scaled and preprocessed. Algorithm implemented with proper initialization. Hyperparameters tuned via internal metrics. Cluster quality evaluated (silhouette, inertia). Visualization confirms structure. Results interpretable.</EXEC>",
                f"<EXEC>Unsupervised solution: {problem}. Approach: {technique}. {hint}. Implemented with convergence criteria. Multiple restarts for stability. Dimension reduction for visualization. Internal validation metrics reported. Parameter sensitivity analyzed. Ready for use in pipeline.</EXEC>",
                f"<EXEC>Unsupervised model: {problem}. Design: {technique}. {hint}. Algorithm converged. Cluster assignments or low-D embedding produced. Evaluation: silhouette score X, explained variance Y%. Visualization shows meaningful separation. Results validated with domain knowledge.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "machine_learning")

DL_TOPICS = [
    ("design a convolutional neural network for image classification on CIFAR-10", "conv-pool-conv-pool-FC architecture with batch norm and dropout", "conv layers learn spatial hierarchies; pooling reduces dimension; FC layers classify; data augmentation helps"),
    ("implement a ResNet with skip connections to train very deep networks", "residual block: F(x) + x, skip connection allows gradient flow", "skip connections solve vanishing gradient; bottleneck blocks for efficiency; pre-activation variant"),
    ("design a recurrent neural network (LSTM/GRU) for time series forecasting", "LSTM with forget gate, input gate, output gate; GRU with reset and update gates", "LSTM addresses vanishing gradient via cell state; GRU has fewer parameters, faster training"),
    ("implement a transformer encoder for sequence classification", "multi-head self-attention + position-wise FFN + layer norm + residual connections", "self-attention captures all pairwise interactions; positional encoding gives order info; parallelizable"),
    ("design a generative adversarial network (GAN) for image generation", "generator creates fake images, discriminator distinguishes real/fake, adversarial training", "minimax game: D tries to maximize log D(x) + log(1-D(G(z))), G tries to minimize log(1-D(G(z)))"),
    ("implement a variational autoencoder (VAE) for anomaly detection", "encoder outputs mean and log variance, reparameterization trick, decoder reconstructs", "KL divergence regularizes latent space to Gaussian; reconstruction error detects anomalies"),
    ("design a training pipeline with mixed precision and gradient accumulation", "use FP16 for compute, FP32 for master weights; accumulate gradients over micro-batches", "FP16 halves memory and speeds up on tensor cores; gradient accumulation simulates larger batch"),
]

def _dl_gen():
    while True:
        for problem, technique, hint in DL_TOPICS:
            inp = pick(
                f"Deep learning: {problem}. Design the architecture and training.",
                f"Neural network: {problem}. Implement with modern best practices.",
                f"Given: {problem}. Choose architecture, loss, optimizer, regularization.",
                f"Deep learning design: {problem}. Handle training stability and performance.",
            )
            plan = pick(
                f"<PLAN>Deep learning: {problem}. {technique}: {hint}. Plan: (1) Define architecture. (2) Choose loss function. (3) Select optimizer (Adam, SGD+momentum). (4) Regularization: dropout, weight decay, batch norm. (5) Training: learning rate schedule, early stopping. (6) Evaluation on validation set. (7) Test set final evaluation.</PLAN>",
                f"<PLAN>DL solution for {problem}: {technique}. {hint}. Steps: (1) Data preprocessing and augmentation. (2) Model definition with proper initialization. (3) Loss and optimizer. (4) Training loop with gradient clipping. (5) Validation and checkpointing. (6) Hyperparameter tuning. (7) Deployment: export to ONNX/TorchScript.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Architecture design. (2) Forward/backward pass. (3) Training loop. (4) Regularization. (5) Monitoring: loss curves, gradient norms. (6) Evaluation metrics. (7) Ablation studies.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing deep learning for {problem}: {technique}. {hint}. Deep learning relies on hierarchical feature learning, end-to-end optimization, and large data. For CNN: conv layers learn local patterns (edges, textures, parts, objects). Pooling adds translation invariance. Batch norm stabilizes training by normalizing layer inputs. Dropout prevents co-adaptation of neurons. Data augmentation (random crop, flip, color jitter) effectively increases dataset size. For ResNet: skip connections solve the degradation problem (deeper nets have higher training error). Identity mapping allows gradient to flow directly to earlier layers. Bottleneck block (1x1, 3x3, 1x1) reduces parameters. For RNN/LSTM: sequential processing, hidden state maintained across time steps. LSTM cell state with forget gate resolves vanishing gradient for long sequences. GRU simplifies with fewer gates. For transformer: self-attention computes Q, K, V matrices. Attention weights = softmax(Q*K^T/sqrt(d_k)). Multi-head: multiple attention heads capture different relationships. Layer norm normalizes across feature dimension. For GAN: training is unstable -- mode collapse, non-convergence. Techniques: Wasserstein loss with gradient penalty, label smoothing, spectral normalization. For VAE: reparameterization trick z = mu + sigma * epsilon enables backprop through sampling. Beta-VAE: weight KL term for disentangled representation. For mixed precision: FP16 reduces memory by half; tensor cores give 2-8x speedup. Loss scaling prevents underflow in gradients. Gradient accumulation: divide batch into micro-batches, accumulate gradients, step optimizer every N micro-batches. This simulates larger batch size without OOM.</THINK>",
                f"<THINK>Analyzing deep learning for {problem}: {technique} with {hint}. Training deep networks requires careful hyperparameter tuning. Learning rate: too high diverges, too low converges slowly. LR schedule: step decay, cosine annealing, warmup + decay. Optimizer: Adam (adaptive LR per parameter, with momentum). Weight decay (L2 regularization): prevents weights from growing too large. Gradient clipping: cap gradient norm to prevent exploding gradients. For CNN: architectures evolved from AlexNet -> VGG -> Inception -> ResNet -> EfficientNet. Each improved parameter efficiency. For transfer learning: fine-tune pretrained models (ImageNet) with small learning rate; freeze early layers, fine-tune later layers. For sequence models: RNNs process tokens sequentially (O(n), hard to parallelize). Transformers process all tokens simultaneously (O(n^2) attention). Long sequences: sparse attention, Linformer, Longformer. For GAN: evaluation: Inception Score (IS), Frechet Inception Distance (FID). Lower FID better (measures distribution distance). For VAE: reconstruction + KL loss. Beta > 1 encourages disentanglement at cost of reconstruction quality. For all: monitor training with TensorBoard. Loss curves, gradient histograms, learning rate, validation metrics. Early stopping: stop when validation loss stops improving. Save best checkpoint.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. Architecture specifics: For ResNet: each layer has stride 1 or 2. Downsampling: conv 1x1 with stride 2 in skip connection. For LSTM: input gate i = sigmoid(W_i*[h_prev, x] + b_i); forget gate f = sigmoid(W_f*[h_prev, x] + b_f); cell update C = f*C_prev + i*tanh(W_c*[h_prev, x] + b_c); output gate o = sigmoid(W_o*[h_prev, x] + b_o); h = o*tanh(C). For transformer: positional encoding: sine/cosine at different frequencies. Multi-head attention: split d_model into h heads of d_k = d_model/h dimensions. Self-attention: each token attends to all tokens. Masked self-attention for decoder (causal: can't attend to future). For training: label smoothing for classification (prevents overconfidence). Warmup + cosine decay schedule. Adam: betas=(0.9, 0.999), epsilon=1e-8. For mixed precision: torch.cuda.amp or apex. GradScaler scales loss: scaled_loss.backward(), scaler.step(optimizer), scaler.update(). For gradient accumulation: optimizer.zero_grad(); for each micro-batch: loss.backward(); if (i+1) % accumulation_steps == 0: optimizer.step(); optimizer.zero_grad(). For all: set seed for reproducibility. Use deterministic algorithms (torch.use_deterministic_algorithms(True)). Log everything for debugging.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Deep learning: {problem}. Architecture: {technique}. {hint}. Model built and trained. Loss converged, validation metrics strong. Regularization applied (dropout, weight decay, batch norm). Learning rate schedule used. Gradient norm monitored. Checkpoint saved. Ready for evaluation.</EXEC>",
                f"<EXEC>DL solution: {problem}. Design: {technique}. {hint}. Implementation: forward/backward pass, training loop, validation. Optimizer: Adam/SGD. Mixed precision for speed. Gradient accumulation for batch size. TensorBoard logs. Best checkpoint saved. Test performance: X% accuracy/Y loss.</EXEC>",
                f"<EXEC>Neural network: {problem}. Method: {technique}. {hint}. Architecture implemented. Training stable (loss curves smooth). No overfitting (train/val gap small). Hyperparameters tuned. Ablation studies confirm design choices. Model exported for deployment.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

NLP_TOPICS = [
    ("implement a text classification pipeline with TF-IDF and logistic regression", "tokenize, lowercase, remove stopwords, TF-IDF vectorize, train logistic regression", "TF-IDF: term frequency * inverse document frequency; reduces common word importance"),
    ("design a sequence-to-sequence model with attention for machine translation", "encoder-decoder with attention: encoder produces hidden states, decoder attends to them", "Bahdanau/Luong attention: context vector = weighted sum of encoder states, weights from alignment"),
    ("implement a BERT-style masked language model pretraining from scratch", "mask 15% of tokens, predict masked tokens with cross-entropy; next sentence prediction", "bidirectional context via masked LM; embeddings: token + segment + position; fine-tune for downstream tasks"),
    ("design a named entity recognition (NER) system using BiLSTM-CRF", "BiLSTM gives per-token context; CRF models tag transitions; Viterbi for optimal tag sequence", "BiLSTM encodes each token with context; CRF ensures valid tag sequences (BIO/BILOU encoding)"),
    ("implement a topic model (LDA) from scratch using Gibbs sampling", "Latent Dirichlet Allocation: documents as mixtures of topics, topics as distributions over words", "Gibbs sampling iteratively reassigns each word to a topic based on document-topic and topic-word counts"),
    ("design an embedding-based retrieval system for semantic search", "encode query and documents with sentence-BERT; cosine similarity for ranking; approximate nearest neighbor", "dense retrieval vs sparse (BM25); use FAISS/Annoy for ANN search; hybrid systems combine both"),
    ("implement a text summarization system using extractive or abstractive methods", "extractive: rank sentences by importance (TextRank, BERT); abstractive: encoder-decoder with attention", "TextRank: PageRank on sentence similarity graph; abstractive: finetune BART/T5 on summarization data"),
]

def _nlp_gen():
    while True:
        for problem, technique, hint in NLP_TOPICS:
            inp = pick(
                f"NLP: {problem}. Design and implement the solution.",
                f"Natural language processing: {problem}. Handle language ambiguity.",
                f"Given: {problem}. Choose representation and model architecture.",
                f"NLP system: {problem}. Implement with text preprocessing and evaluation.",
            )
            plan = pick(
                f"<PLAN>NLP approach: {problem}. {technique}: {hint}. Plan: (1) Text preprocessing. (2) Text representation. (3) Model architecture. (4) Training. (5) Evaluation (accuracy, BLEU, ROUGE, F1). (6) Error analysis. (7) Deployment optimization.</PLAN>",
                f"<PLAN>NLP solution for {problem}: {technique}. {hint}. Steps: (1) Tokenization and normalization. (2) Feature extraction. (3) Model definition. (4) Training with appropriate loss. (5) Inference pipeline. (6) Metrics computation. (7) Failure analysis.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Corpus analysis (vocabulary size, sequence length). (2) Preprocessing pipeline. (3) Model design. (4) Training procedure. (5) Decoding/inference. (6) Evaluation on standard benchmarks.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing NLP system for {problem}: {technique}. {hint}. NLP challenges: ambiguity, context-dependence, sparsity. Text representation: bag-of-words loses word order and semantics; TF-IDF reduces common word impact; word embeddings (Word2Vec, GloVe) capture semantics via vector geometry; contextual embeddings (BERT, RoBERTa) capture meaning in context. For sequence-to-sequence: encoder reads input, produces hidden states. Decoder generates output, conditioned on encoder representation. Attention mechanism: decoder computes alignment between current output position and each input position, weighted sum of encoder states forms context vector. This solves the information bottleneck of fixed-length encoder state. For BERT: pretraining on large corpus (BooksCorpus + Wikipedia). Masked LM: 80% mask token, 10% random token, 10% unchanged. Next Sentence Prediction: predict if sentence B follows sentence A. Fine-tuning: add task-specific head, train all parameters with small LR. For NER: BIO encoding (B-begin, I-inside, O-outside). BiLSTM gives both left and right context. CRF layer ensures valid tag transitions (I-PER cannot follow O). Viterbi decoding finds most probable tag sequence. For topic modeling: LDA generative process: for each document, sample topic distribution theta ~ Dir(alpha). For each word, sample topic z ~ theta, sample word w ~ phi_z where phi_z ~ Dir(beta). Gibbs sampling: iteratively update each word's topic assignment conditioned on all other assignments. For semantic search: sentence-BERT (SBERT) fine-tunes BERT with Siamese/triplet loss to produce semantically meaningful sentence embeddings. Cosine similarity between embeddings. ANN (FAISS, Annoy, HNSW) for scalable retrieval. Hybrid: combine sparse (BM25) and dense (SBERT) scores. For summarization: extractive methods select important sentences from source. Abstractive: generate novel sentences. BART (denoising autoencoder) and T5 (text-to-text) are strong abstractive models. ROUGE evaluates n-gram overlap. BERTScore evaluates semantic similarity.</THINK>",
                f"<THINK>Analyzing NLP for {problem}: {technique} with {hint}. Tokenization choices: word-level (common words), subword (BPE, WordPiece, SentencePiece), character-level. BPE: merge most frequent byte pair; WordPiece: merge based on likelihood. For sequence tasks: padding to max length, attention masks. For embeddings: OOV words handled by subword tokenization. For low-resource: multilingual models (mBERT, XLM-R), cross-lingual transfer learning. For evaluation: NLU tasks (GLUE, SuperGLUE benchmarks). Error analysis: confusion matrix, misclassification patterns, dataset bias. For production: model quantization (FP16, INT8), distillation (train smaller student model from larger teacher), ONNX export, serving with Triton/TF Serving. For all: tokenization must be consistent between training and inference. Check for train-test mismatch in preprocessing. Handle special tokens ([CLS], [SEP], [PAD], [UNK], [MASK]) correctly.</THINK>",
                f"<THINK>Deep implementation of NLP {problem}: {technique}. {hint}. Text preprocessing: (1) Normalize: lowercase, unicode normalization (NFC/NFD). (2) Tokenization: space-based for tokenizers, BPE for transformers. (3) Phrase detection: using PMI (pointwise mutual information) for multi-word expressions. For seq2seq with attention: encoder: bidirectional (concatenated forward/backward states). Decoder state s_t = f(s__{{t-1}}, y__{{t-1}}, c_t). Context c_t = sum(alpha__{{t,i}} * h_i). Attention weights alpha__{{t,i}} = exp(score(s__{{t-1}}, h_i)) / sum. Score functions: dot, general (s^T * W * h), concat (v^T * tanh(W*[s; h])). For BERT: WordPiece tokenizer with 30K vocabulary. Embedding size 768 (base) or 1024 (large). 12/24 transformer layers. 12/16 attention heads. Total params: 110M/340M. MLM accuracy ~70-80%. Fine-tuning: 2-5 epochs with LR 2e-5 to 5e-5. For CRF: transition matrix T of size (num_tags x num_tags). Score of sequence = sum(s_i,t_i) + sum(T[t_i,t__{{i+1}}]). Loss = -log P(y|x) = -(score - log Z). Z computed via forward algorithm (DP). Viterbi decoding: DP for max score path. For semantic search: SBERT uses (u, v, |u-v|) concatenation with cosine similarity loss. For all: handle long sequences ( > 512 tokens) with truncation, sliding window, or Longformer/BigBird.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>NLP system: {problem}. Method: {technique}. {hint}. Preprocessing pipeline built. Model implemented and trained. Evaluation metrics strong. Error analysis conducted. Tokenization consistent. Ready for deployment with optimized inference (quantization, distillation).</EXEC>",
                f"<EXEC>NLP solution: {problem}. Approach: {technique}. {hint}. Text processing, model architecture, training, evaluation complete. Standard benchmarks: X score. Production optimizations: ONNX export, FP16 inference. Handling of edge cases (long text, OOV, multilingual) implemented.</EXEC>",
                f"<EXEC>NLP implementation: {problem}. Design: {technique}. {hint}. Preprocessing, model, inference pipeline. Evaluated on held-out set. Error analysis reveals systematic issues. Special token handling correct. Reproducibility: seed set, preprocessing documented. Ready for downstream integration.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

CV_TOPICS = [
    ("implement an image classifier using a pre-trained ResNet with fine-tuning", "load ImageNet pre-trained ResNet, replace FC head, train with small LR on new dataset", "freeze early layers initially; gradually unfreeze; data augmentation crucial for small datasets"),
    ("design a real-time object detection system using YOLO", "YOLO divides image into grid, each cell predicts bounding boxes and class probabilities", "grid cell responsible if object center falls in it; non-max suppression removes duplicate detections"),
    ("implement image segmentation using U-Net for biomedical images", "encoder-decoder with skip connections; each decoder layer concatenates corresponding encoder feature map", "skip connections combine low-level (edge) with high-level (semantic) features; data augmentation with elastic deformation"),
    ("design a face recognition system with face detection, alignment, and embedding", "MTCNN for detection/alignment; FaceNet/SFace for embedding; cosine similarity for matching", "triplet loss: anchor-positive distance < anchor-negative distance by margin; L2 normalize embeddings"),
    ("implement a neural style transfer between content and style images", "optimize random image to match content loss (feature activations) and style loss (Gram matrices)", "content: MSE between VGG features; style: MSE between Gram matrices; total variation denoising"),
    ("design an image captioning system with CNN encoder and transformer decoder", "CNN extracts image features; transformer decoder generates caption conditioned on image features", "object detection features (Faster R-CNN) better than grid features; beam search for decoding"),
    ("implement a video action recognition system using 3D CNNs or two-stream networks", "3D CNN: 3D convolutions over spatio-temporal volumes; two-stream: RGB + optical flow streams fused", "I3D inflates 2D conv to 3D; slow-fast network processes different frame rates; attention for temporal aggregation"),
]

def _cv_gen():
    while True:
        for problem, technique, hint in CV_TOPICS:
            inp = pick(
                f"Computer vision: {problem}. Design the architecture and pipeline.",
                f"CV system: {problem}. Implement with proper data handling.",
                f"Given: {problem}. Choose architecture, loss function, evaluation metrics.",
                f"Computer vision: {problem}. Handle image preprocessing and model design.",
            )
            plan = pick(
                f"<PLAN>CV approach: {problem}. {technique}: {hint}. Plan: (1) Data collection and annotation. (2) Preprocessing: resize, normalize, augment. (3) Model architecture design. (4) Loss function and optimizer. (5) Training with validation. (6) Post-processing (NMS, thresholding). (7) Evaluation: mAP, IoU, accuracy.</PLAN>",
                f"<PLAN>CV solution for {problem}: {technique}. {hint}. Steps: (1) Data pipeline (loading, transforms, batching). (2) Base model selection. (3) Task-specific head. (4) Training configuration. (5) Inference pipeline. (6) Metric computation. (7) Qualitative analysis of predictions.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Input/output specification. (2) Feature extraction backbone. (3) Task-specific module. (4) Loss formulation. (5) Training procedure. (6) Post-processing. (7) Evaluation on standard benchmarks.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing CV system for {problem}: {technique}. {hint}. Computer vision tasks require understanding of spatial hierarchies in images. CNNs process images through layers of increasing receptive field: early layers detect edges, middle layers detect parts/patterns, late layers detect objects/semantics. For transfer learning: pre-training on ImageNet (1.2M images, 1000 classes) provides general visual features. Fine-tuning adapts to specific domain. Data augmentation: random crop, horizontal flip, color jitter, random rotation, CutOut, CutMix, MixUp. This reduces overfitting significantly. For object detection: YOLO frames detection as regression problem: divide image into SxS grid. Each cell predicts B bounding boxes (x, y, w, h, confidence) and C class probabilities. Loss: localization loss + confidence loss + classification loss. NMS: greedy algorithm that selects highest-scoring box, suppresses overlapping boxes with IoU > threshold. For segmentation: U-Net encoder (downsampling) captures context; decoder (upsampling) recovers spatial resolution. Skip connections combine encoder and decoder features at same resolution, preserving fine details. For face recognition: triplet loss minimizes distance between same identity, maximizes between different identities. Batch hard mining: select hardest positive and hardest negative within batch. FaceNet embedding is L2 normalized, enabling cosine similarity as distance metric. For style transfer: content loss (high-level features from early layers) and style loss (Gram matrix correlations across feature maps). Optimization: initialize with content image, minimize total loss with L-BFGS. For captioning: bottom-up attention uses object proposals from Faster R-CNN as image features. Transformer decoder with cross-attention to image features. Beam search: maintain top-k partial captions at each step, score by log probability + length normalization. For video: I3D inflates 2D conv kernels to 3D (e.g., 3x3 -> 3x3x3). Two-stream: RGB stream (appearance) + optical flow stream (motion). Late fusion averages predictions.</THINK>",
                f"<THINK>Analyzing CV for {problem}: {technique} with {hint}. Data quality is paramount: annotation consistency, class balance, diverse viewpoints/lighting. For small datasets ( < 1000 images): heavy augmentation, transfer learning with frozen backbone, strong regularization. For object detection evaluation: mAP (mean Average Precision) averaged over IoU thresholds (0.5:0.95:0.05). For segmentation: IoU (Intersection over Union) per class, mean IoU. For face recognition: TAR@FAR (True Accept Rate at False Accept Rate), ROC curve. For captioning: BLEU (n-gram precision), METEOR (alignment-based), CIDEr (TF-IDF weighted n-gram), SPICE (scene graph). For video: Top-1/Top-5 accuracy, per-frame vs video-level prediction. For all: training tricks: (1) Learning rate warmup. (2) Cosine annealing schedule. (3) Label smoothing. (4) EMA (exponential moving average) of model weights. (5) Gradient clipping. (6) SyncBN (synchronized batch norm across GPUs). (7) Distributed training (DDP). Hardware: GPU memory limits batch size. Gradient checkpoint trades compute for memory.</THINK>",
                f"<THINK>Deep implementation of CV {problem}: {technique}. {hint}. For classification: ResNet architecture: conv1 (7x7 stride 2), maxpool, layer1-4 (each with multiple residual blocks), global avg pool, FC. For ResNet50: [3,4,6,3] blocks, total 50 layers. Bottleneck: 1x1 (reduce dim), 3x3, 1x1 (restore dim). For YOLO: output tensor is S x S x (B*5 + C). For S=7, B=2, C=20: 7x7x30. YOLO loss imbalances coordinates vs confidence. Modern YOLO (v5-v8) use anchor boxes, CIoU loss, mosaic augmentation, and are much more accurate. For U-Net: encoder: repeated (conv 3x3 + ReLU + maxpool 2x2), double features each stage. Decoder: up-conv (transposed conv 2x2), concatenate with cropped encoder features, conv 3x3 + ReLU. Final: 1x1 conv to desired channels. For Siamese network (FaceNet): triplet loss: L = max(0, d(a,p) - d(a,n) + margin). d = ||f(a) - f(p)||^2. Mine hardest triplets: hardest positive (max d(a,p)) and hardest negative (min d(a,n)) within batch. For all: PyTorch implementation: torchvision models for backbone, torchvision.transforms for augmentation, torch.nn.DataParallel/DistributedDataParallel for multi-GPU. For inference: torch.no_grad(), torch.cuda.amp for FP16. For deployment: torch.jit.script for scripting, ONNX for cross-platform.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>CV system: {problem}. Architecture: {technique}. {hint}. Data pipeline with augmentation built. Model implemented with backbone and task head. Training converged. Evaluation metrics strong. Qualitative analysis shows reasonable predictions. Model exported for deployment.</EXEC>",
                f"<EXEC>Computer vision: {problem}. Approach: {technique}. {hint}. Preprocessing and augmentation configured. Transfer learning from ImageNet. Training with proper regularization. Evaluation: mAP/IoU/accuracy X%. Post-processing (NMS, thresholding) applied. Ready for production.</EXEC>",
                f"<EXEC>CV solution: {problem}. Method: {technique}. {hint}. Data loading, model, training, evaluation pipeline complete. Standard benchmark results competitive. Ablation studies confirm design choices. Qualitative results visually inspected. Inference optimized for speed.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

RL_TOPICS = [
    ("implement Q-learning for a grid world navigation task", "tabular Q-learning: Q(s,a) <- Q(s,a) + lr * (r + gamma * max Q(s',a') - Q(s,a))", "epsilon-greedy exploration; off-policy: learns from any policy trajectory"),
    ("design a Deep Q-Network (DQN) with experience replay for Atari games", "neural network approximates Q function; replay buffer decorrelates samples; target network stabilizes", "store (s,a,r,s') in replay buffer; sample mini-batch uniformly; target network updated periodically"),
    ("implement policy gradient (REINFORCE) for continuous control", "optimize policy pi(a|s) directly: gradient = E[ sum(gamma^t * grad(log pi(a_t|s_t)) * R_t) ]", "REINFORCE: Monte Carlo returns; high variance; use baseline (value function) to reduce variance"),
    ("design an actor-critic architecture (A2C/A3C) for parallel training", "actor updates policy, critic evaluates state value; advantage A(s,a) = Q(s,a) - V(s)", "A2C: synchronous; A3C: asynchronous; advantage reduces variance; entropy bonus encourages exploration"),
    ("implement PPO (Proximal Policy Optimization) with clipped objective", "clip ratio r(theta) = pi_new(a|s) / pi_old(a|s) to [1-eps, 1+eps] to prevent large updates", "surrogate objective: L = min(r * A, clip(r, 1-eps, 1+eps) * A); multiple epochs per data batch"),
    ("design a reward shaping strategy for sparse reward environments", "potential-based reward shaping: F(s,s') = gamma * Phi(s') - Phi(s) preserves optimal policy", "shaping guides exploration; potential-based ensures policy invariance; domain knowledge encoded in Phi"),
    ("implement model-based RL with learned dynamics model and planning", "learn environment model p(s'|s,a); use model for planning (MPC) or generating synthetic rollouts", "Dyna: interleave real and simulated experience; PETS: MPC with ensemble of probabilistic dynamics models"),
]

def _rl_gen():
    while True:
        for problem, technique, hint in RL_TOPICS:
            inp = pick(
                f"Reinforcement learning: {problem}. Design the algorithm and training.",
                f"RL problem: {problem}. Choose algorithm with appropriate exploration.",
                f"Given: {problem}. Implement with environment interaction and reward modeling.",
                f"Reinforcement learning: {problem}. Handle the exploration-exploitation trade-off.",
            )
            plan = pick(
                f"<PLAN>RL approach: {problem}. {technique}: {hint}. Plan: (1) Define MDP: states, actions, rewards, transitions. (2) Choose algorithm type: value-based, policy-based, actor-critic. (3) Implement agent. (4) Environment interaction loop. (5) Training with exploration. (6) Evaluation: cumulative reward, convergence. (7) Hyperparameter tuning.</PLAN>",
                f"<PLAN>RL solution for {problem}: {technique}. {hint}. Steps: (1) Environment setup. (2) Agent design with function approximator. (3) Experience collection. (4) Learning updates. (5) Exploration schedule. (6) Monitoring: reward, loss, entropy. (7) Checkpoint best performing policy.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) State/action representation. (2) Exploration strategy. (3) Learning algorithm. (4) Training loop. (5) Stability techniques (target network, gradient clipping). (6) Evaluation on multiple random seeds.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing RL for {problem}: {technique}. {hint}. RL agent learns by interacting with environment. Key challenges: exploration vs exploitation, credit assignment, non-stationary targets. For Q-learning: temporal difference learning uses bootstrapping. Off-policy: learns optimal policy while following epsilon-greedy. For DQN: experience replay breaks correlation between consecutive samples. Target network fixed for C steps provides stable targets. For policy gradient: REINFORCE uses complete episode returns. High variance: baseline (V(s)) reduces variance. Actor-critic combines value-based and policy-based: critic estimates V(s), actor updates policy using advantage A(s,a) = Q(s,a) - V(s). For PPO: clipped surrogate objective prevents destructively large policy updates. Multiple epochs of minibatch updates per data batch. Trust region: KL penalty or clipping keeps new policy close to old. For reward shaping: sparse rewards (only at goal) make learning hard. Shaping provides intermediate rewards. Potential-based shaping guarantees policy invariance: optimal policy of original MDP + shaping = optimal policy of original MDP. For model-based: learn dynamics model, then plan or generate additional experience. Dyna: Q-learning with simulated experience from model. PETS: MPC with probabilistic ensemble and trajectory sampling. For all: tune learning rate, discount factor gamma, exploration epsilon, network architecture. Use multiple random seeds for reliable evaluation. TensorBoard for monitoring.</THINK>",
                f"<THINK>Analyzing RL for {problem}: {technique} with {hint}. Algorithm selection: (1) Discrete action spaces: DQN, C51, Rainbow. (2) Continuous action spaces: DDPG, TD3, SAC. (3) On-policy: PPO, A2C (stable but sample-inefficient). (4) Off-policy: DQN, SAC (sample-efficient but less stable). For continuous control: SAC (Soft Actor-Critic) adds entropy regularization for better exploration. For robotics: sample efficiency critical, use model-based or sim-to-real. For games: high sample count acceptable; DQN/PPO work well. For hyperparameters: learning rate (3e-4 for Adam common), gamma (0.99), lambda (GAE, 0.95), clip epsilon (0.2 for PPO), entropy coefficient (0.01). For exploration: epsilon decay (DQN), action noise (DDPG: OU noise or Gaussian), entropy (SAC). For stability: gradient clipping (max norm 1.0), target network with polyak averaging (tau=0.005), layer normalization. For evaluation: average return over fixed number of episodes, success rate, sample efficiency (reward vs environment steps).</THINK>",
                f"<THINK>Deep implementation of RL {problem}: {technique}. {hint}. For DQN: network takes state (84x84x4 stacked frames for Atari), outputs Q values per action. Convolutional layers, then FC. Huber loss more stable than MSE. For PPO: GAE (Generalized Advantage Estimation) computes advantage: delta_t = r_t + gamma*V(s__{{t+1}}) - V(s_t); A_t = sum((gamma*lambda)^k * delta__{{t+k}}). PPO objective: L = min(ratio*A, clip(ratio, 1-eps, 1+eps)*A). Add value loss + entropy bonus. Total: L = L_policy + c1*L_value + c2*L_entropy. For SAC: policy outputs mean and std of Gaussian (for continuous). Reparameterization trick: action = tanh(mu + sigma * epsilon). Q-function: minimize soft Bellman residual with target entropy. For experience replay: circular buffer of size 1e6. Uniform or prioritized sampling. For training loop: collect episode, store transitions, sample batch, update networks, update target network. For distributed: A3C uses multiple workers with shared global network. A2C: workers collect experience, compute gradients synchronously on master. For all: normalize observations and returns. Use running mean/std for observations. Clip rewards to [-1, 1] for stability. Set seed for reproducibility.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>RL: {problem}. Algorithm: {technique}. {hint}. Agent implemented and trained. Reward curve shows convergence. Evaluation: average return X, success rate Y%. Exploration-exploitation balanced. Hyperparameters tuned. Training stable across seeds. Policy saved for deployment.</EXEC>",
                f"<EXEC>Reinforcement learning: {problem}. Method: {technique}. {hint}. Environment interaction works. Learning updates correct. Experience replay/reward shaping implemented. Training monitored (reward, loss, entropy). Best checkpoint saved. Reproducible with fixed seed.</EXEC>",
                f"<EXEC>RL solution: {problem}. Approach: {technique}. {hint}. Agent design complete. Training converges to optimal policy. Exploration schedule effective. Value function accurate. Advantage estimation correct. Sample efficiency good. Ready for transfer to real environment.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

GENAI_TOPICS = [
    ("implement a GPT-style autoregressive language model from scratch", "decoder-only transformer with causal masking, next token prediction", "causal attention: each token attends only to previous tokens; training: predict next token given previous"),
    ("design a diffusion model for image generation (DDPM)", "forward: gradually add noise; reverse: learn to denoise; sample: start from noise, iteratively denoise", "UNet with attention; sinusoidal time embeddings; predict noise; DDIM for faster sampling"),
    ("implement a flow-based generative model (Normalizing Flows)", "invertible transformations with tractable Jacobian determinant; exact likelihood estimation", "affine coupling layers (RealNVP): split, scale+shift, concatenate; invertible 1x1 conv (Glow)"),
    ("design an instruction-following fine-tuning pipeline for LLMs", "supervised fine-tuning on instruction-response pairs; RLHF for alignment", "collect demonstrations, fine-tune with LM loss; train reward model; optimize policy with PPO"),
    ("implement a retrieval-augmented generation (RAG) system", "retrieve relevant documents from knowledge base, concatenate with query, generate answer", "chunk documents, embed with sentence transformer, store in vector DB, top-k retrieval, LLM generation"),
    ("design a controllable text generation system with constraints", "guided decoding: logit manipulation, classifier-free guidance, constrained beam search", "temperature, top-k, top-p sampling; repetition penalty; grammar constraints via GBNF/guidance"),
    ("implement a multimodal model (text + image) like CLIP or LLaVA", "contrastive learning: image-text pairs, maximize cosine similarity of correct pairs", "dual encoders (image + text), contrastive loss (InfoNCE); projection heads match embedding dimensions"),
]

def _genai_gen():
    while True:
        for problem, technique, hint in GENAI_TOPICS:
            inp = pick(
                f"Generative AI: {problem}. Design the model architecture and training.",
                f"GenAI: {problem}. Implement generation with appropriate control.",
                f"Given: {problem}. Choose architecture, training objective, sampling strategy.",
                f"Generative model: {problem}. Handle training stability and output quality.",
            )
            plan = pick(
                f"<PLAN>GenAI approach: {problem}. {technique}: {hint}. Plan: (1) Data preparation. (2) Model architecture design. (3) Training objective. (4) Training procedure. (5) Sampling/generation. (6) Evaluation: perplexity, FID, human evaluation. (7) Optimization for inference.</PLAN>",
                f"<PLAN>GenAI solution for {problem}: {technique}. {hint}. Steps: (1) Tokenization/data representation. (2) Model definition. (3) Loss function. (4) Training with appropriate hardware. (5) Inference pipeline. (6) Quality evaluation. (7) Safety filters if applicable.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Architecture selection. (2) Training setup. (3) Generation strategy. (4) Controllability mechanisms. (5) Evaluation metrics. (6) Ablation studies. (7) Deployment optimization.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing generative model for {problem}: {technique}. {hint}. Generative models learn data distribution and sample from it. For autoregressive (GPT): causal attention mask ensures each token only sees previous tokens. Training maximizes log likelihood of next token. Sampling: greedy (argmax), temperature (softmax with scaled logits), top-k (sample from k most likely), top-p (nucleus: smallest set with cumulative prob > p). For diffusion: forward process q(x_t|x__{{t-1}}) = N(sqrt(1-beta_t)*x__{{t-1}}, beta_t*I). Reverse: learn p_theta(x__{{t-1}}|x_t). Training: predict noise added at step t. DDIM: deterministic sampling, 10-50 steps instead of 1000. For normalizing flows: require invertibility and tractable Jacobian. Coupling layer: split input, first half unchanged, second half = (first_half_params) * second_half + (first_half_params). Inverse: same structure, rearrange terms. For instruction fine-tuning: supervised on (instruction, response) pairs. RLHF: train reward model on human preferences (pairwise comparisons). PPO: optimize policy to maximize reward while staying close to SFT model (KL penalty). For RAG: documents are chunked (256-512 tokens), embedded with sentence-BERT, stored in FAISS/Chroma. Retrieval: embed query, nearest neighbor search. Concatenate retrieved chunks with query, feed to LLM. For controllable generation: temperature controls sharpness of distribution. top-k limits vocabulary to k most likely. top-p dynamically selects tokens with cumulative probability p. Repetition penalty: scales logits of previously generated tokens down. For multimodal: CLIP trains image encoder and text encoder with contrastive loss (InfoNCE). Goal: correct (image, text) pairs have higher similarity than incorrect pairs. LLaVA: connects CLIP vision encoder to LLM via projection layer; fine-tune on image+text data.</THINK>",
                f"<THINK>Analyzing generative AI for {problem}: {technique} with {hint}. Training large generative models requires significant compute. For GPT: model sizes range from 125M (GPT-2 small) to 175B (GPT-3) to 1T+ (sparse). Training: next token prediction on massive text corpora (Common Crawl, books, Wikipedia). For diffusion: UNet with attention blocks at multiple resolutions. Timestep embedding (sinusoidal) injected at each block. Classifier-free guidance: train with conditional and unconditional objectives; sample: eps = w*eps_c + (1-w)*eps_u. w > 1 improves quality. For RLHF: reward model trained on human comparisons (which response is better). Bradley-Terry model: P(y_i > y_j) = sigma(r_i - r_j). PPO: optimize against reference policy with KL penalty KL(pi_theta || pi_ref) to prevent reward hacking. For RAG: challenges: (1) Retrieval quality -- reranking improves. (2) Context length -- LLM must handle long input. (3) Faithfulness -- model may ignore retrieved context. (4) Latency -- retrieval + generation < user tolerance. For multimodal: contrastive learning benefits from large batch sizes (32K+). Gradients are computed only on positive pairs; all other pairs in batch serve as negatives. InfoNCE loss: -log(exp(sim(i,t)/tau) / sum(exp(sim(i,t')/tau))). For all: evaluation is challenging. Perplexity measures likelihood but not quality. Human evaluation is gold standard but expensive. Task-specific metrics (BLEU, ROUGE for text; FID, IS for images) approximate but imperfect.</THINK>",
                f"<THINK>Deep implementation of generative {problem}: {technique}. {hint}. For GPT: token embedding + positional embedding (learned or sinusoidal). Transformer block: layer norm -> multi-head causal attention -> residual -> layer norm -> MLP (GELU activation, 4x hidden dim) -> residual. Output: layer norm -> LM head (embedding weight tied). For diffusion: UNet downsamples to bottleneck, upsamples with skip connections. Attention at 16x16 resolution. Sinusoidal time embedding. Epsilon prediction vs v-prediction. For flow: RealNVP coupling layer: (1) Split x into x_a, x_b. (2) s, t = NN(x_a). (3) y_b = x_b * exp(s) + t. (4) y_a = x_a. (5) Concatenate y_a, y_b. Reverse: (1) Split y into y_a, y_b. (2) s, t = NN(y_a). (3) x_b = (y_b - t) * exp(-s). (4) x_a = y_a. For RAG: chunking strategy: overlapping chunks with 256-512 tokens. Embedding model: sentence-transformers/all-MiniLM-L6-v2 or BAAI/bge-large-en-v1.5. Vector DB: Chroma, Pinecone, Weaviate, Milvus. Hybrid search: BM25 + dense embedding combined. For CLIP: image encoder (ResNet/ViT), text encoder (Transformer). Projection heads map to shared embedding dimension. Loss: symmetric cross-entropy on similarity matrix. Temperature tau learned during training. For deployment: model quantization (AWQ, GPTQ), KV caching for generation, continuous batching, speculative decoding, tensor parallelism for large models.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Generative AI: {problem}. Architecture: {technique}. {hint}. Model built and trained. Generation quality evaluated. Sampling strategy tuned. Controllability mechanisms implemented. Inference optimized for latency. Safety filters in place. Ready for deployment.</EXEC>",
                f"<EXEC>GenAI solution: {problem}. Method: {technique}. {hint}. Training pipeline complete. Generation samples examined. Metrics reported. Ablation studies confirm design. Instruction tuning/retrieval/control mechanisms work as expected. Model exported for inference.</EXEC>",
                f"<EXEC>Generative model: {problem}. Approach: {technique}. {hint}. Model implemented with proper training objective. Sampling produces high-quality outputs. Evaluation metrics strong. Training stable. Inference optimizations applied (quantization, caching). Production-ready.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

MLMATH_TOPICS = [
    ("derive the gradient of cross-entropy loss with respect to softmax inputs", "dL/dz_i = p_i - y_i where p_i = softmax(z)_i and y_i is one-hot target", "cross-entropy: L = -sum(y_i * log(p_i)); softmax derivative: dp_i/dz_j = p_i*(delta_ij - p_j); chain rule simplifies to p_i - y_i"),
    ("prove that the expected value of the gradient in stochastic gradient descent is the true gradient", "E[grad_L_B] = 1/n * sum(E[grad_L_i]) for batch B, unbiased estimator of full gradient", "each sample contributes grad_L_i; E[grad_L_i] = grad_L (equal weight in loss); expectation linearity gives result"),
    ("explain the bias-variance decomposition of MSE and its implications for model complexity", "MSE = Bias^2 + Variance + Irreducible Error; as model complexity increases, bias decreases but variance increases", "underfitting: high bias, low variance; overfitting: low bias, high variance; optimal complexity at trade-off"),
    ("derive the closed-form solution for linear regression (normal equation)", "theta = (X^T X)^{-1} X^T y from minimizing MSE", "MSE = (y - X*theta)^T * (y - X*theta); derivative = -2 X^T (y - X*theta); set to 0 -> X^T X theta = X^T y"),
    ("explain the kernel trick and how it enables non-linear SVMs", "replace dot products with kernel function K(x_i, x_j) = phi(x_i)^T phi(x_j) without computing phi", "kernel implicitly maps to higher dimension; RBF: K(x,y) = exp(-||x-y||^2 / (2*sigma^2)); polynomial: (x^T y + c)^d"),
    ("prove convergence of gradient descent for convex functions with Lipschitz gradients", "if f is convex and gradient L-Lipschitz, GD with step < 1/L converges at O(1/k) rate", "f(y) <= f(x) + grad f(x)^T (y-x) + L/2 ||y-x||^2 (descent lemma); choose y = x - lr*grad; rearrange to show f(x_k) - f(x*) <= O(1/k)"),
    ("explain the derivation of variational inference (ELBO) for Bayesian models", "log p(x) = KL(q(z) || p(z|x)) + ELBO(q); maximizing ELBO minimizes KL", "ELBO(q) = E_q[log p(x,z)] - E_q[log q(z)] = E_q[log p(x|z)] - KL(q(z) || p(z)); reparameterization gradient for optimization"),
]

def _mlmath_gen():
    while True:
        for problem, technique, hint in MLMATH_TOPICS:
            inp = pick(
                f"ML math foundations: {problem}. Provide the derivation and intuition.",
                f"Mathematical derivation: {problem}. Show each step clearly.",
                f"Given: {problem}. Derive the result and explain its significance.",
                f"Machine learning theory: {problem}. Prove the theorem or identity.",
            )
            plan = pick(
                f"<PLAN>Mathematical derivation: {problem}. {technique}: {hint}. Plan: (1) State the problem formally. (2) Write relevant definitions and known results. (3) Apply chain rule, calculus, or linear algebra. (4) Simplify step by step. (5) Arrive at final result. (6) Provide intuition and implications.</PLAN>",
                f"<PLAN>Derive {problem}: {technique}. {hint}. Steps: (1) Formal setup with notation. (2) Key identities. (3) Step-by-step manipulation. (4) Intermediate simplifications. (5) Final expression. (6) Verify with concrete example. (7) Discuss consequences for ML practice.</PLAN>",
                f"<PLAN>Prove {problem}: {technique}. {hint}. Plan: (1) Assumptions and definitions. (2) Main derivation/proof. (3) Key lemmas or ingredients. (4) Result. (5) Intuitive explanation. (6) Practical implications.</PLAN>",
            )
            think = pick(
                f"<THINK>Deriving {problem}: {technique}. {hint}. The derivation connects fundamental mathematical concepts to practical ML. For cross-entropy + softmax: softmax outputs probability distribution over classes. Cross-entropy measures difference between predicted and true distributions. The gradient dL/dz = p - y is intuitive: when predicted probability for correct class p_y < 1, gradient pushes logits z_y up; when p_i > 0 for wrong class, gradient pushes z_i down. For SGD unbiasedness: the key insight is that each sample's gradient expectation equals the full gradient because the training objective is an average over samples. The minibatch gradient is average of sample gradients, so E[grad_B] = E[grad_i] = grad_full. This holds regardless of batch size. For bias-variance decomposition: E[(y - f_hat)^2] = (Bias[f_hat])^2 + Var[f_hat] + sigma^2. As model complexity increases, bias decreases (model fits data better) but variance increases (model fits noise). Optimal complexity minimizes total error. For normal equation: MSE is convex quadratic in theta; setting gradient to zero gives unique global minimum. (X^T X must be invertible; if not, use pseudoinverse or regularization). For kernel trick: dual formulation of SVM depends only on dot products. Replacing with kernel is valid because kernel corresponds to dot product in some feature space (Mercer theorem). RBF kernel corresponds to infinite-dimensional feature space. For GD convergence: Lipschitz gradient ensures quadratic upper bound. Choosing lr = 1/L gives optimal decrease per iteration. Convergence rate O(1/k) for convex; O(exp(-k)) for strongly convex. For variational inference: ELBO = E_q[log p(x|z)] - KL(q(z) || p(z)). First term encourages data fit; second term encourages q close to prior. Maximizing ELBO is equivalent to minimizing KL(q || p(z|x)), but ELBO is computable while KL is not. Reparameterization trick: sample z = mu + sigma * epsilon where epsilon ~ N(0,1), enabling backprop through sampling.</THINK>",
                f"<THINK>Mathematical analysis of {problem}: {technique}. {hint}. For cross-entropy gradient: chain rule: dL/dz = (dL/dp) * (dp/dz). dL/dp = -y/p (element-wise). dp/dz = diag(p) - p*p^T (Jacobian of softmax). Product simplifies to p - y. This is the delta between prediction and target, which is intuitive for gradient-based learning. For SGD: law of large numbers ensures sample average converges to expectation. For finite batch size, gradient is unbiased but has variance sigma^2 / B. Reducing batch size increases variance but may help escape sharp minima (implicit regularization). For bias-variance: the decomposition uses the fact that y = f(x) + epsilon, E[epsilon] = 0, Var[epsilon] = sigma^2. f_hat is estimated from training data (random). The expectation is over training data randomness. High bias: model cannot capture true function (underfitting). High variance: model changes a lot with different training sets (overfitting). For normal equation: deriving involves matrix calculus. d/d_theta (y - X*theta)^T (y - X*theta) = -2 X^T (y - X*theta). Set to 0: X^T X theta = X^T y. Solve: theta = (X^T X)^{{-1}} X^T y. For kernel trick: representer theorem: optimal solution lies in span of training points. So w = sum(alpha_i * y_i * x_i) for SVM. Then w^T x = sum(alpha_i * y_i * x_i^T x) = sum(alpha_i * y_i * K(x_i, x)). The kernel function need not be explicitly computed. For GD convergence: Lipschitz constant L = max eigenvalue of Hessian. For quadratic: L = max(eig(X^T X)). GD with lr < 2/L converges. For strongly convex with parameter mu, convergence is linear: O(exp(-mu/L * k)).</THINK>",
                f"<THINK>Deep mathematical derivation of {problem}: {technique}. {hint}. For softmax gradient derivation: define p_i = exp(z_i) / sum_j exp(z_j). For k = i: dp_i/dz_i = p_i * (1 - p_i). For k != i: dp_i/dz_k = -p_i * p_k. Jacobian J = diag(p) - p*p^T. Then dL/dz = (dL/dp)^T * J = (-y/p)^T * (diag(p) - p*p^T). Simplify: term1 = -y/p * diag(p) = -y. term2 = -y/p * (-p*p^T) = sum(y_i) * p^T = 1 * p^T (since y is one-hot, sum(y_i) = 1). So dL/dz = -y + p = p - y. For bias-variance: E[L] = E[(y - f_hat)^2] = E[(f + epsilon - f_hat)^2]. Expand: E[(f - f_hat)^2] + E[epsilon^2] + 2E[(f - f_hat)*epsilon]. Cross term = 0 (epsilon independent). So MSE = E[(f - f_hat)^2] + sigma^2. Now E[(f - f_hat)^2] = (E[f_hat] - f)^2 + E[(f_hat - E[f_hat])^2] = Bias^2 + Variance. For ELBO: Jensen inequality: log p(x) = log integral p(x,z) dz >= integral q(z) log (p(x,z)/q(z)) dz = ELBO(q). The gap is KL(q || p(.|x)) = integral q(z) log (q(z)/p(z|x)) dz.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Derivation: {problem}. Result: {technique}. {hint}. Step-by-step derivation complete with formal justification. Intuitive explanation provided. Practical implications discussed. Verification with concrete example confirms correctness.</EXEC>",
                f"<EXEC>Mathematical analysis: {problem}. {technique}. {hint}. Derivation rigorous and complete. Assumptions stated. Key identities used. Final result matches known form. Interpretation and significance explained. Example calculation validates.</EXEC>",
                f"<EXEC>ML theory: {problem}. Proof: {technique}. {hint}. Derivation follows standard mathematical procedure. Each step justified. Result connects to practical ML observations. Intuition aligned with mathematical formalism.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "machine_learning")

MLEVAL_TOPICS = [
    ("design a cross-validation strategy for time series data", "time series split: train on past, validate on future; no future leakage", "expanding window: train size grows; sliding window: fixed train size; purge gap between train and val"),
    ("implement a bootstrap confidence interval for a model performance metric", "sample with replacement from test set B times, compute metric each time, report percentiles", "bootstrap samples of size N from N test points; 95% CI = [2.5th, 97.5th] percentile of B metric values"),
    ("design an A/B testing framework for comparing ML models in production", "randomized assignment to control/treatment; one-sided metric; significance test; MDE calculation", "compute sample size needed: n = (Z_alpha + Z_beta)^2 * 2*sigma^2 / delta^2; sequential testing for early stopping"),
    ("implement a fairness evaluation across demographic groups", "compute demographic parity, equal opportunity, equal odds; compare across groups", "demographic parity: P(positive|group A) = P(positive|group B); equal opportunity: TPR equal; equal odds: TPR and FPR equal"),
    ("design an evaluation pipeline for ranking systems (NDCG, MAP, MRR)", "compute graded relevance; NDCG = DCG / IDCG; DCG = sum(rel_i / log2(i+1))", "NDCG handles multiple relevance levels; MAP for binary relevance; MRR measures first relevant result position"),
    ("implement calibration assessment for probabilistic classifiers", "reliability diagram: bin predictions by confidence, plot accuracy vs confidence; ECE metric", "ECE = sum(w_b * |acc_b - conf_b|); temperature scaling post-hoc calibrates; Platt scaling for binary"),
]

def _mleval_gen():
    while True:
        for problem, technique, hint in MLEVAL_TOPICS:
            inp = pick(
                f"ML evaluation: {problem}. Design the evaluation framework.",
                f"Model evaluation: {problem}. Handle statistical significance.",
                f"Given: {problem}. Implement rigorous evaluation methodology.",
                f"Evaluation design: {problem}. Address bias, variance, and validity.",
            )
            plan = pick(
                f"<PLAN>Evaluation design: {problem}. {technique}: {hint}. Plan: (1) Define success metrics. (2) Choose validation strategy. (3) Implement evaluation pipeline. (4) Compute statistical significance. (5) Check for bias. (6) Document methodology. (7) Reproduce results.</PLAN>",
                f"<PLAN>ML evaluation for {problem}: {technique}. {hint}. Steps: (1) Split data appropriately. (2) Train model. (3) Compute metrics with uncertainty. (4) Hypothesis testing. (5) Subgroup analysis. (6) Robustness checks. (7) Report findings.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Evaluation protocol. (2) Metric selection based on task. (3) Statistical framework. (4) Implementation. (5) Validation of evaluation itself. (6) Interpret results.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing evaluation for {problem}: {technique}. {hint}. Rigorous evaluation is critical for reliable ML. For time series: standard k-fold leaks future information. TimeSeriesSplit preserves temporal order: train on [0, t], validate on [t, t+1]. Expanding window uses all past data; sliding window uses fixed window size. Gap between train and val prevents autocorrelation leakage. For bootstrap CI: sample N test points with replacement B times (B=1000-10000). For each bootstrap sample, compute metric. Sort metrics, take 2.5th and 97.5th percentile as CI. BCA (bias-corrected accelerated) bootstrap adjusts for skewness. For A/B testing: control (current model) vs treatment (new model). Metric: one primary metric (pre-specified). MDE (minimum detectable effect) determines sample size. Sequential testing: continuously monitor with stopping boundaries (O'Brien-Fleming) to avoid peeking bias. For fairness: demographic parity (equal selection rates), equal opportunity (equal TPR), equal odds (equal TPR and FPR). Trade-offs: fairness metrics may conflict; equalizing one may worsen another. Intersectional analysis: consider multiple demographic dimensions simultaneously. For ranking: NDCG rewards relevant results higher in list. DCG = sum(rel_i / log2(i+1)). IDCG = DCG of ideal ranking. NDCG = DCG/IDCG. MAP: average precision per query, averaged over queries. MRR: reciprocal rank of first relevant result. For calibration: perfectly calibrated: among predictions with confidence c, accuracy = c. Reliability diagram: bin predicted probabilities (10 bins, 0-1), plot accuracy per bin. ECE = sum(|bin|/N * |acc - conf|). Temperature scaling: single parameter T > 0 scales logits: p = softmax(logits / T). Optimizes NLL on validation set. Platt: logistic regression model on classifier outputs.</THINK>",
                f"<THINK>Analyzing evaluation for {problem}: {technique} with {hint}. Evaluation pitfalls: (1) Data leakage: any information from future/test set influences training. (2) Selection bias: test set not representative. (3) Multiple comparison: testing many metrics inflates false positives. (4) p-hacking: running experiments until significant. (5) Overfitting to test set: reporting test performance used for model selection. For all: pre-register evaluation plan. Report confidence intervals, not just point estimates. Use hold-out test set only once at the very end. For time series: also consider temporal correlation: nearby points may have similar values. Gap (purging) between train and validation removes autocorrelation. For bootstrap: percentile bootstrap is simple but may be biased. BCa bootstrap corrects for bias and skewness. For A/B testing: MDE depends on baseline rate, desired power (80%), significance level (5%). For small effect sizes, sample size needed is large. For fairness: group sizes may be imbalanced. Small groups have noisier metrics. Use confidence intervals to assess significance. For ranking: graded relevance (0-4 for search) vs binary (for question answering). NDCG is rank-sensitive: top ranks matter more. For calibration: reliability diagrams need sufficient samples per bin. ECE is weighted average of calibration error. Overconfident models (accuracy < confidence) have positive ECE; underconfident have negative.</THINK>",
                f"<THINK>Deep evaluation implementation for {problem}: {technique}. {hint}. For time series CV: sklearn TimeSeriesSplit. max_train_size for sliding window. test_size for validation horizon. For bootstrap: bootstrap.BCA from scipy or manual implementation. For A/B: statsmodels for power analysis and hypothesis testing. Sequential testing: always valid p-values (mixture Sequential Probability Ratio Test). For fairness: fairlearn, AIF360 libraries. Compute metrics per group, compute disparity (difference or ratio). For ranking: sklearn.metrics.ndcg_score, average_precision_score. Implement from scratch to verify. For calibration: sklearn.calibration.calibration_curve. Temperature scaling: optimize T to minimize NLL on validation using L-BFGS. For all: reproducibility: set seed, log all parameters, version data and model. Use MLflow or Weights and Biases for experiment tracking. CI/CD for ML: unit tests for evaluation code, integration tests for pipeline, monitoring for production drift.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Evaluation framework: {problem}. Method: {technique}. {hint}. Protocol designed and implemented. Metrics computed with confidence intervals. Statistical significance assessed. Bias checked across subgroups. Reproducibility ensured. Results documented.</EXEC>",
                f"<EXEC>ML evaluation: {problem}. Approach: {technique}. {hint}. Proper validation strategy used. Metrics with uncertainty reported. A/B or fairness analysis conducted. Results robust to assumptions. Evaluation code tested and versioned.</EXEC>",
                f"<EXEC>Evaluation complete: {problem}. Design: {technique}. {hint}. Valid split strategy, appropriate metrics, statistical rigor. Confidence intervals reported. No leakage. All assumptions checked. Ready for publication or production decision.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "machine_learning")

MLDEPLOY_TOPICS = [
    ("design a model serving API with batching and caching", "async inference server with request queue, dynamic batching, response cache", "collect requests during window, batch into single inference, return results; LRU cache for identical inputs"),
    ("implement model quantization (INT8) for faster inference", "post-training quantization: calibrate scale/zero_point, quantize weights and activations", "per-channel vs per-tensor quantization; KL divergence calibration; PTQ vs QAT (Quantization-Aware Training)"),
    ("design a feature store for consistent online/offline feature computation", "store feature definitions and values; point-in-time joins for training; low-latency retrieval for serving", "Feast/Tecton: offline store (S3/parquet), online store (Redis/DynamoDB); feature serving with same transformations"),
    ("implement model monitoring for data drift and concept drift", "track input distributions (mean, std, histograms); track prediction distributions; alert on significant change", "data drift: distribution shift detected via statistical tests (KS, PSI); concept drift: accuracy degradation over time"),
    ("design a pipeline for continuous training and model deployment", "automated retraining on new data; model evaluation against current production model; canary deployment", "trigger on schedule or data freshness; A/B test new vs current; rollback if metrics degrade; version all models"),
    ("implement explainability (SHAP/LIME) in production for compliance", "SHAP: game-theoretic feature importance; approximate with KernelSHAP or TreeSHAP for speed", "SHAP values: Shapley values for features; LIME: locally approximate model with interpretable surrogate; feature attribution per prediction"),
]

def _mldeploy_gen():
    while True:
        for problem, technique, hint in MLDEPLOY_TOPICS:
            inp = pick(
                f"ML deployment: {problem}. Design the production system.",
                f"MLOps: {problem}. Implement reliable serving pipeline.",
                f"Given: {problem}. Handle scale, latency, and reliability.",
                f"Production ML: {problem}. Design for observability and maintenance.",
            )
            plan = pick(
                f"<PLAN>ML deployment: {problem}. {technique}: {hint}. Plan: (1) Requirements: latency, throughput, availability. (2) Architecture design. (3) Implementation. (4) Testing: load test, chaos test. (5) Monitoring and alerting. (6) Deployment strategy. (7) Documentation.</PLAN>",
                f"<PLAN>Production ML for {problem}: {technique}. {hint}. Steps: (1) Containerize model. (2) Design API. (3) Implement optimizations. (4) Set up CI/CD. (5) Deploy to staging. (6) Canary to production. (7) Monitor and iterate.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Performance baseline. (2) Optimization implementation. (3) Validation of preserved accuracy. (4) Integration with serving infrastructure. (5) Testing under load. (6) Gradual rollout with monitoring.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing ML deployment for {problem}: {technique}. {hint}. Production ML systems must handle real-world constraints. For model serving: dynamic batching collects requests during a window (e.g., 10ms) and processes as a batch. This increases throughput at cost of slight latency increase. Response cache: for repeated inputs (e.g., same user/query), cache inference results with TTL. Invalidation: clear cache when model updated. For quantization: INT8 reduces model size by 4x and speeds up inference 2-4x on supported hardware. Calibration: pass representative data through model, collect activation ranges. Per-channel quantization (each output channel has own scale) better than per-tensor. KL divergence calibration minimizes information loss. QAT: simulate quantization during training for better accuracy. For feature store: offline features (compute once, store in parquet) used for training. Online features (computed in real-time, stored in Redis) used for serving. Point-in-time join ensures correct feature values at prediction time. Feature definitions: SQL + transformation code, versioned. For monitoring: data drift: KS test for continuous, PSI (Population Stability Index) for categorical. Concept drift: track accuracy/precision over time. Drift detection methods: ADWIN, Page-Hinkley, DDM. Alerts: pager duty integration for significant drift. For continuous training: trigger when new data available, when drift detected, or on schedule. Validation: evaluate against champion model on hold-out set. Deploy: canary (5% traffic -> 25% -> 100%), monitor metrics, auto-rollback on degradation. Model registry: MLflow Model Registry stores models with version, stage (staging/production/archived). For explainability: SHAP: Shapley values from cooperative game theory. For each prediction, SHAP values sum to prediction minus baseline. TreeSHAP is O(TLD^2) for trees, faster than naive. LIME: fits linear model locally around prediction. Both provide feature attribution (which features drove prediction up/down). For compliance: log explanations with predictions. Audit trail: who requested which prediction, what features, what explanation, when.</THINK>",
                f"<THINK>Analyzing ML deployment for {problem}: {technique} with {hint}. Infrastructure: cloud (AWS SageMaker, GCP Vertex AI, Azure ML) or on-prem (Kubeflow, MLflow). GPU serving: NVIDIA Triton Inference Server supports dynamic batching, model ensembles, concurrent model execution. CPU serving: ONNX Runtime optimized for x86/ARM. Container: Docker with CUDA base image for GPU. Orchestration: Kubernetes for scaling. For dynamic batching: client sends requests; server accumulates; when batch_size reached or timeout elapsed, run inference. For cache: Redis or Memcached for response cache. Cache key = model_version + input_hash. For quantization: calibration dataset should be representative of production data (1000-10000 samples). INT8: symmetric (int8 range [-128, 127]) for weights, asymmetric (uint8) for activations (ReLU positive). For monitoring: statistical tests for drift: KS (Kolmogorov-Smirnov) compares distributions; PSI measures difference across bins. For categorical: chi-squared test. Monitoring metrics: request latency (p50, p95, p99), throughput, error rate, model metrics (accuracy served). Dashboards: Grafana. Alerts: thresholds + anomaly detection. For CI/CD: GitHub Actions or GitLab CI. Train stage: run training pipeline, upload model to registry. Validate stage: evaluate on test set, compare to baseline. Deploy stage: update serving endpoint with new model (canary). For explainability: KernelSHAP samples feature subsets to approximate. For tabular models: TreeSHAP is exact for trees (XGBoost, LightGBM). For deep learning: Integrated Gradients, GradCAM for images, LIME for text.</THINK>",
                f"<THINK>Deep deployment implementation for {problem}: {technique}. {hint}. For Triton serving: model configuration (max_batch_size, input/output shapes, backend). Dynamic batching: preferred_batch_size, max_queue_delay_microseconds. Ensemble: chain multiple models (preprocess -> inference -> postprocess). For quantization: PyTorch: torch.quantization. TensorRT: nvidia tensorrt for maximum GPU optimization. For feature store: Feast: define features in feature_repo, materialize to online store, serving API for real-time features. Offline: query with point-in-time correctness. For monitoring: model monitoring system collects: predictions, actuals (when available), feature values, metadata. Compute drift metrics at regular intervals. For continuous training: Airflow or Kubeflow Pipelines. DAG: data extraction -> validation -> feature computation -> training -> evaluation -> deployment. For rollback: N-1 version kept ready. Traffic split: via deployment manager (Kuberneties) or load balancer weights. For A/B testing: split traffic by user_id hash. Monitor both arms. Decision: if new model not worse on primary metric, promote. For explainability: production: SHAP computed on a sample of requests (not all, too expensive). Store explanations alongside predictions. For compliance: audit logging: timestamp, model version, input hash, prediction, explanation, user_id. All logs immutable, stored securely.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>ML deployment: {problem}. Design: {technique}. {hint}. Serving infrastructure built. Optimizations applied (batching, caching, quantization). Monitoring active (drift detection, performance metrics). CI/CD pipeline operational. Canary deployment strategy in place. Production-ready.</EXEC>",
                f"<EXEC>Production ML: {problem}. Approach: {technique}. {hint}. API endpoint serving with low latency. Batching improves throughput. Quantization reduces cost. Feature store enables consistent features. Monitoring alerts on drift. Continuous training pipeline running. Explainability integrated.</EXEC>",
                f"<EXEC>MLOps solution: {problem}. Method: {technique}. {hint}. Server deployed with optimizations. Feature pipelines operational. Monitoring dashboards active. Automated retraining and deployment configured. Explainability for compliance. All metrics within SLAs. Ready for production traffic.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "machine_learning")

def chunk_8_gen():
    gens = [_supervised_gen(), _unsupervised_gen(), _dl_gen(), _nlp_gen(), _cv_gen(),
            _rl_gen(), _genai_gen(), _mlmath_gen(), _mleval_gen(), _mldeploy_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════════════════════════════════════════════════════════
# Chunk 9: Data Science & Statistics
# ═══════════════════════════════════════════════════════════════════════════

VIZ_TOPICS = [
    ("design a visualization for high-dimensional data (10+ features)", "use PCA/t-SNE/UMAP for 2D projection, color by cluster or target, interactive tooltips", "scatter plot matrix for small dimensions; parallel coordinates; dimensionality reduction for >5 dims"),
    ("create a dashboard showing KPIs for a SaaS business", "line charts for trends, bar charts for comparisons, pie/donut for composition, heatmap for correlations", "context KPIs: MRR, churn, LTV, CAC; sparklines for mini-trends; use dashboarding tool (Grafana, Tableau, Streamlit)"),
    ("visualize geospatial data with choropleth and point maps", "choropleth: color regions by value; point maps: scatter on map; dot density for distributions", "handle projection distortion; use appropriate color scales (sequential, diverging, qualitative); avoid cluttering"),
    ("design an effective visualization for a time series with seasonal patterns", "decompose into trend, seasonal, residual; use subplots; highlight anomalies with markers", "STL decomposition: season-trend using LOESS; plot original, trend, seasonal, remainder on shared x-axis"),
    ("visualize uncertainty in predictions using confidence bands", "line plot with shaded region (+/- 1 or 2 std); fan plots for percentiles; ensemble spread", "confidence bands show uncertainty; prediction intervals for future values; ensemble shows model disagreement"),
    ("create an interactive network graph visualization for social network analysis", "node-link diagram with force-directed layout; color by community; size by centrality", "force-directed: simulate repulsion (nodes) and attraction (edges); community detection (Louvain); interactive filtering"),
]

def _viz_gen():
    while True:
        for problem, technique, hint in VIZ_TOPICS:
            inp = pick(
                f"Data visualization: {problem}. Design the chart or dashboard.",
                f"Visualization design: {problem}. Choose chart types and encoding.",
                f"Given: {problem}. Create an effective visual representation.",
                f"Data viz: {problem}. Handle perceptual and cognitive principles.",
            )
            plan = pick(
                f"<PLAN>Visualization design: {problem}. {technique}: {hint}. Plan: (1) Define data and message. (2) Choose chart type. (3) Select encoding (position, color, size, shape). (4) Design layout. (5) Add interactivity. (6) Test with stakeholders.</PLAN>",
                f"<PLAN>Visualization for {problem}: {technique}. {hint}. Steps: (1) Understand data structure. (2) Identify key patterns. (3) Choose visual encoding. (4) Implement. (5) Refine for clarity. (6) Add labels and annotations.</PLAN>",
                f"<PLAN>Design viz: {problem}. Use {technique}. {hint}. Plan: (1) Preprocess/aggregate data. (2) Select visualization type. (3) Map data to aesthetics. (4) Implement with library. (5) Polish: colors, labels, annotations. (6) Validate message delivery.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing visualization for {problem}: {technique}. {hint}. Good visualization follows perceptual principles: position is most accurate channel (vs angle, area, color). Color: sequential for ordered data, diverging for bipolar, qualitative for categories. Avoid: pie charts (angle perception poor), 3D (distortion), dual y-axis (misleading). For high-dimensional data: PCA projects linearly; t-SNE preserves local structure. Parallel coordinates: each dimension is vertical axis, each data point is line crossing axes. For dashboards: choose metrics aligned with business goals. Top-left: most important KPI. Sparklines show trends compactly. Color: use consistently (green=good, red=bad). For geospatial: choropleth: color intensity encodes value. Avoid equal-area bins for varying region sizes (normalize by population/area). Dot density: each dot represents N units. For time series: line charts with time on x-axis. Decomposition: additive (y = T + S + R) for constant variance, multiplicative (y = T*S*R) for growing variance. STL: robust to outliers, handles any seasonal period. For uncertainty: confidence interval (parameter uncertainty) vs prediction interval (future observation uncertainty). Fan plots: increasingly transparent bands for percentiles. For network: force-directed layout (Fruchterman-Reingold: attractive force along edges, repulsive force between all nodes). Louvain community detection optimizes modularity. Size nodes by degree/centrality. Interactive: hover for details, click to highlight neighbors.</THINK>",
                f"<THINK>Analyzing visualization for {problem}: {technique} with {hint}. Grammar of Graphics (Wilkinson): a visualization is composed of data, mapping, scales, coordinate system, marks (points, lines, bars), and facets. Libraries: matplotlib (foundation), seaborn (statistical), plotly (interactive), altair (declarative), bokeh (dashboard). For effective design: (1) Show data clearly. (2) Maximize data-ink ratio (Tufte). (3) Avoid chartjunk. (4) Use accessible color palettes (colorblind-friendly). (5) Label directly (not separate legend). For exploration: scatter plot matrix (pairs), parallel coordinates, small multiples. For presentation: highlight key finding, remove unnecessary axes/gridlines, use annotations for story. For dashboards: real-time data requires efficient incremental updates. Web technologies: D3.js for custom, Vega-Lite for declarative. For geospatial: GeoJSON/TopoJSON for boundaries. Mapbox, Leaflet for web maps. Nominal color scales: 5-7 categories max (ColorBrewer). For all: test with target audience. Perception is faster for certain encodings. Pre-attentive attributes (color, size, orientation) are processed in <200ms.</THINK>",
                f"<THINK>Deep implementation of {problem}: {technique}. {hint}. Python implementation: plotly.graph_objects for interactive, plotly.express for quick charts. For PCA projection: sklearn.decomposition.PCA, fit_transform, then scatter plot colored by target. For parallel coordinates: plotly.express.parallel_coordinates. For dashboard: Streamlit: easy widgets, caching, deployment as web app. Plotly Dash: more complex, callback-based interactivity. For geospatial: geopandas for spatial operations, contextily for basemaps, folium for interactive maps. For time series decomposition: statsmodels.tsa.seasonal.STL. Plot original + components with shared x. For uncertainty: seaborn.lineplot with ci='sd' shows confidence band. Or matplotlib fill_between. For network: networkx for graph algorithms, pyvis or nxviz for visualization. For force layout: d3-force (web) or fa2 (ForceAtlas2) for large graphs. For all: color choices: matplotlib colormaps (viridis, plasma for sequential), ColorBrewer (Set1, Set2 for qualitative). Test colorblindness: colorcet library. For presentation: larger fonts, minimal ink, clear title, source citation.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Visualization: {problem}. Design: {technique}. {hint}. Chart created with appropriate encoding. Clear, accurate, accessible. Labels and annotations guide interpretation. Interactive features for exploration. Dashboard/chart tested with audience. Ready for presentation.</EXEC>",
                f"<EXEC>Data viz: {problem}. Approach: {technique}. {hint}. Visualization implemented. Colors accessible. Labels clear. Interactivity functional. Key insights immediately visible. Code organized and reusable. Deployed as dashboard/static chart.</EXEC>",
                f"<EXEC>Visualization complete: {problem}. Method: {technique}. {hint}. Perceptual principles followed. Data-ink ratio high. Chart type appropriate for data and message. Implementation clean. Annotations explain key findings. Stakeholder feedback incorporated.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(2,5), "data_science")

TIMESERIES_TOPICS = [
    ("forecast monthly sales for the next 12 months using historical data", "ARIMA/SARIMA or Prophet for seasonal time series forecasting", "SARIMA(p,d,q)(P,D,Q)s: seasonal differencing; auto_arima selects parameters; Prophet handles holidays and change points"),
    ("detect anomalies in a univariate time series (e.g., server metrics)", "isolation-based methods or statistical: moving average + z-score; STL decomposition + residual analysis", "rolling window: compute moving avg and std; flag points outside mean +/- 3*std; seasonal ESD for seasonality"),
    ("decompose a time series into trend, seasonal, and residual components", "STL decomposition or classical additive/multiplicative decomposition", "STL uses LOESS smoothing; handles any seasonal period; robust to outliers; additive vs multiplicative based on seasonality magnitude"),
    ("design a change point detection algorithm for structural breaks", "PELT (Pruned Exact Linear Time) or binary segmentation; minimize cost + penalty for change points", "cost function: negative log-likelihood; penalty: BIC = 2*log(n) * num_changepoints; PELT is O(n) optimal"),
    ("implement time series cross-validation for model evaluation", "expanding window: train on increasing window, evaluate on next period; no future leakage", "TimeSeriesSplit from sklearn; use purge gap to avoid autocorrelation; fixed window for computational efficiency"),
    ("handle missing values in a time series with interpolation and imputation", "forward fill, linear interpolation, seasonal interpolation, or model-based (Kalman filter)", "simple: forward fill then linear; advanced: STL impute (iterative decomposition and fill); Kalman: state space models"),
    ("design a multivariate time series forecasting model (VAR/LSTM)", "VAR for linear relationships; LSTM/Transformer for non-linear; vector auto-regression includes lagged dependencies", "VAR: each variable regressed on lagged versions of all variables; LSTM: seq-to-seq with encoder-decoder; attention captures long-range dependencies"),
]

def _timeseries_gen():
    while True:
        for problem, technique, hint in TIMESERIES_TOPICS:
            inp = pick(
                f"Time series analysis: {problem}. Design the forecasting/detection approach.",
                f"Time series: {problem}. Handle seasonality, trend, and noise.",
                f"Given: {problem}. Implement with proper validation.",
                f"Temporal data: {problem}. Choose model and evaluation strategy.",
            )
            plan = pick(
                f"<PLAN>Time series: {problem}. {technique}: {hint}. Plan: (1) Visualize: plot, check trend/seasonality/stationarity. (2) Transform if needed (differencing, Box-Cox). (3) Decompose. (4) Select model. (5) Fit and validate. (6) Forecast and evaluate.</PLAN>",
                f"<PLAN>Time series solution for {problem}: {technique}. {hint}. Steps: (1) EDA: ACF/PACF plots, stationarity tests (ADF, KPSS). (2) Preprocessing: handle missing, outliers. (3) Model selection. (4) Parameter estimation. (5) Diagnostic checking (residuals). (6) Forecast with prediction intervals.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Resample to regular frequency. (2) Handle missing data. (3) Feature engineering (lags, rolling stats, calendar features). (4) Model training. (5) Backtesting with time series CV. (6) Final forecast with uncertainty.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing time series model for {problem}: {technique}. {hint}. Time series data has temporal dependencies: adjacent points more similar. EDA: plot to see trend (long-term direction), seasonality (periodic patterns), residuals (noise). Stationarity: statistical properties constant over time. Most models require stationarity (or differencing). ADF test: null = non-stationary, p < 0.05 means stationary. ACF: autocorrelation at different lags. PACF: partial autocorrelation (direct effect of lag k). ARIMA(p,d,q): p = AR order (from PACF), d = differencing order, q = MA order (from ACF). SARIMA adds seasonal: P,D,Q,m. auto_arima (pmdarima) searches parameters. Prophet: additive model with yearly/weekly/daily seasonality, holiday effects, change points. Robust to missing data and outliers. For anomaly detection: statistical methods: rolling mean + threshold. Decomposition: residual > threshold = anomaly. Isolation Forest: anomalies easier to isolate. For change point detection: PELT finds optimal segmentation: minimize sum of costs + penalty * num_changepoints. Binary segmentation: recursively split series at most likely change point. For missing values: forward fill then linear is simple baseline. STL impute: iterative decomposition and missing value imputation. Kalman filter: state space model, handles missing naturally. For multivariate: VAR: each equation includes lags of all variables; Granger causality tests predictive relationships. LSTM: sliding window of past values predict next value. Transformer: recent advances (Informer, Autoformer) for long sequences. For all: evaluation with time series CV (expanding window). Metrics: MAE, RMSE, MAPE for scale-dependent error. MASE for scale-independent. Prediction intervals: quantile regression, bootstrapping residuals.</THINK>",
                f"<THINK>Analyzing time series for {problem}: {technique} with {hint}. Seasonal patterns: daily/weekly/monthly/yearly. Multiple seasonalities: Prophet and MSTL handle this. Holidays: irregular events, handled by Prophet or dummy variables. Rolling window statistics: moving average smooths noise; exponentially weighted moving average gives more weight to recent. For model selection: compare AIC/BIC for ARIMA. For forecast horizon: short-term (few steps) more accurate than long-term. Uncertainty grows with horizon. For all: never use standard k-fold CV (leaks future). TimeSeriesSplit: train on past, test on future. Gap between train and test prevents autocorrelation leakage. For implementation: statsmodels for ARIMA/VAR, prophet for Prophet, scikit-learn for basic methods, pyOD for anomaly detection, ruptures for change point. For LSTM: PyTorch with sliding window dataset. Sequence length: enough to capture seasonality (e.g., 24 for hourly data with daily cycle). Many-to-one: last hidden state maps to prediction. Many-to-many for multi-step forecast. For all: always perform residual diagnostics: residuals should be white noise (no autocorrelation, normally distributed). Ljung-Box test for autocorrelation in residuals. If autocorrelation remains, model is inadequate.</THINK>",
                f"<THINK>Deep time series implementation for {problem}: {technique}. {hint}. For ARIMA: model order selection via ACF/PACF. AR: PACF cutoff after lag p. MA: ACF cutoff after lag q. Estimation: MLE via Kalman filter (state space representation of ARIMA). Forecast: recursive: use predicted values as inputs for next step. For Prophet: y(t) = g(t) + s(t) + h(t) + epsilon(t). g: piecewise linear/logistic trend with changepoints. s: Fourier series for seasonality. h: holiday indicators. Fit: stan backend (MCMC). Forecast: trend continues with uncertainty from changepoint flexibility. For anomaly detection with STL: compute seasonal component. Residual = original - trend - seasonal. Flag points where |residual| > 3 * MAD(residual). MAD (median absolute deviation) more robust than std. For change point detection with PELT: assume piecewise constant mean or variance. Cost: -2*log(L) for segment. Penalty: beta * num_changepoints. PELT uses pruning to reduce computations from O(n^2) to O(n). For VAR: selection of lag order p via AIC. Estimate via OLS per equation. Impulse response: how a shock to one variable propagates. Forecast: iterative (predicted values used as inputs for next step). For LSTM forecasting: univariate: window of past N values -> next value. Feature engineering: add hour, day, month, dayofweek as categorical features (embedding or sin/cos encoding). Multi-step: direct (model per horizon), recursive, or seq2seq. For all: backtesting: roll forward one step at a time, retrain periodically (fixed window or expanding).</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Time series: {problem}. Model: {technique}. {hint}. EDA complete, model trained, validated with time series CV. Forecasts with prediction intervals. Residual diagnostics pass. Metrics: MAE X, RMSE Y. Ready for production forecasting.</EXEC>",
                f"<EXEC>Time series analysis: {problem}. Approach: {technique}. {hint}. Data preprocessed, decomposed, model selected. Stationarity ensured. Seasonality handled. Anomalies/change points detected. Forecasts generated with uncertainty bounds. Evaluation via backtesting.</EXEC>",
                f"<EXEC>Time series solution: {problem}. Method: {technique}. {hint}. Model fitted and diagnostically checked. Residuals white noise. Forecast plots show prediction intervals. Cross-validation confirms stability. Ready for deployment or reporting.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

BAYESIAN_TOPICS = [
    ("design a Bayesian A/B test for conversion rate comparison", "Beta-Binomial conjugate model: prior Beta(1,1), posterior Beta(alpha+y, beta+n-y)", "posterior distribution of conversion rate; P(A > B) via Monte Carlo; credible interval for lift; expected loss"),
    ("implement a Bayesian linear regression with informative priors", "posterior: N( (X^TX/sigma^2 + Sigma_0^{-1})^{-1} * (X^T y/sigma^2 + Sigma_0^{-1}*mu_0), ... )", "conjugate: normal prior yields normal posterior; prior shrinks coefficients toward prior mean; uncertainty quantified via posterior covariance"),
    ("design a hierarchical Bayesian model for partial pooling across groups", "each group has own parameter, but groups share a common prior distribution", "partial pooling: groups with less data shrink toward global mean; implemented via PyMC/Stan; group-level and individual-level parameters"),
    ("implement Bayesian change point detection with MCMC", "model with switchpoint: likelihood changes at unknown time t; sample from posterior over t and segment parameters", "MCMC: Metropolis-Hastings or NUTS (No-U-Turn Sampler) for posterior; trace plot for convergence; posterior over change point location"),
    ("design a Bayesian optimization strategy for hyperparameter tuning", "Gaussian Process surrogate model; acquisition function (EI, UCB, PI) selects next point to evaluate", "GP prior over objective function; posterior after each evaluation; EI: expected improvement over best observed; balance exploration/exploitation"),
    ("implement a Bayesian structural time series model (CausalImpact)", "state space model with local linear trend + seasonality + regression components", "fit model on pre-intervention period; predict counterfactual post-intervention; causal effect = observed - predicted; posterior interval for effect"),
    ("design a Bayesian network for probabilistic reasoning under uncertainty", "DAG representing conditional dependencies; each node has CPD; inference via variable elimination or MCMC", "structure learning (PC algorithm, score-based) or expert knowledge; parameter learning (MLE, Bayesian); inference: P(query|evidence)"),
]

def _bayesian_gen():
    while True:
        for problem, technique, hint in BAYESIAN_TOPICS:
            inp = pick(
                f"Bayesian analysis: {problem}. Design the model and inference.",
                f"Bayesian statistics: {problem}. Specify priors and likelihood.",
                f"Given: {problem}. Implement posterior inference and interpretation.",
                f"Probabilistic modeling: {problem}. Handle uncertainty quantification.",
            )
            plan = pick(
                f"<PLAN>Bayesian approach: {problem}. {technique}: {hint}. Plan: (1) Define likelihood. (2) Specify prior(s). (3) Derive posterior or approximate via MCMC/Variational. (4) Check convergence. (5) Posterior inference: credible intervals, hypothesis testing. (6) Sensitivity analysis to priors.</PLAN>",
                f"<PLAN>Bayesian solution for {problem}: {technique}. {hint}. Steps: (1) Model specification. (2) Prior elicitation. (3) Posterior computation. (4) Convergence diagnostics. (5) Posterior summaries. (6) Model checking (posterior predictive checks). (7) Decision making under uncertainty.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Graphical model representation. (2) Prior distributions. (3) Likelihood function. (4) Inference algorithm. (5) Posterior analysis. (6) Model comparison (WAIC, LOO). (7) Reporting uncertainty.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing Bayesian model for {problem}: {technique}. {hint}. Bayesian approach treats parameters as random variables with probability distributions. Prior encodes knowledge before seeing data. Likelihood p(data|param). Posterior p(param|data) proportional to prior * likelihood. For A/B testing: Beta prior is conjugate for Binomial likelihood. Posterior: Beta(alpha + y, beta + n - y). P(A > B) = Monte Carlo: sample from both posteriors, compute P(sample_A > sample_B). Expected loss: integrate over posterior. For linear regression: conjugate: normal prior -> normal posterior. Prior precision matrix Sigma_0^{{-1}}. Posterior mean is weighted average of prior mean and OLS estimate, weighted by precision. For hierarchical model: groups share prior hyperparameters. Example: schools (8 schools problem). Each school has treatment effect theta_j ~ N(mu, tau^2). Observed y_j ~ N(theta_j, sigma_j^2). Partial pooling: theta_j estimates shrink toward mu when within-school variance high. For change point detection: model: y_t ~ N(mu_1, sigma) for t <= tau, N(mu_2, sigma) for t > tau. Priors: mu_1, mu_2, tau. MCMC samples from joint posterior p(mu_1, mu_2, tau | y). For Bayesian optimization: GP: y(x) ~ GP(m(x), k(x,x')). Kernel: RBF, Matern. Acquisition function EI(x) = E[max(0, f(x) - f(x_best))] under posterior. UCB: mu(x) + kappa * sigma(x). Bayesian methods handle uncertainty naturally, incorporate prior knowledge, and update beliefs with evidence. Useful when data is limited and uncertainty estimates are important.</THINK>",
                f"<THINK>Analyzing Bayesian {problem}: {technique} with {hint}. Prior selection: conjugate priors simplify computation (Beta for Binomial, Normal for Normal, Gamma for Poisson). Non-informative: uniform or Jeffreys prior (invariant). Weakly informative: centered at reasonable value with moderate variance. For complex models: MCMC samples from posterior (no closed form). PyMC: uses NUTS (No-U-Turn Sampler), adaptive HMC. Stan: full Bayesian inference with HMC. Diagnostics: trace plot (should mix well, no trends), R-hat ( < 1.01 indicates convergence), effective sample size ( > 100 per parameter). For model comparison: WAIC and LOO approximate leave-one-out cross-validation from MCMC samples. Lower is better. ELPD difference > 4*SE indicates meaningful difference. For posterior predictive checks: simulate data from posterior, compare to observed data. If simulated data systematically differs from observed, model is misspecified. For Bayesian optimization: GP hyperparameters fitted via MLE (built into sklearn). Expected Improvement automatically balances exploration (high sigma) and exploitation (high mu). For all: sensitivity analysis: try different priors, check how posterior changes. If posterior is robust to reasonable prior changes, conclusions are reliable. The Bayesian workflow: build, fit, criticize, repeat.</THINK>",
                f"<THINK>Deep Bayesian implementation for {problem}: {technique}. {hint}. For A/B test: Beta(1,1) is uniform (uninformative). Flat prior: Beta(0.5,0.5) (Jeffreys). Posterior for A: Beta(y_A+1, n_A-y_A+1). For B similarly. P(A > B): sample 10000 from each, count A > B. If P(A > B) > 0.95, declare winner. For hierarchical model: Stan code: parameters {{ vector[J] theta; real mu; real tau; }}; model {{ theta ~ N(mu, tau); y ~ N(theta, sigma); }}. For change point: discrete parameter tau (MCMC with reversible jump or enumerate over possible tau). For continuous: model as continuous with latent mixture. For Bayesian optimization: sklearn GaussianProcessRegressor with Matern kernel. EI acquisition: from scipy.stats import norm. mu, sigma = gp.predict(x, return_std=True). gamma = (best_mu - mu) / sigma. EI = sigma * (gamma * norm.cdf(gamma) + norm.pdf(gamma)). For Bayesian network: pgmpy for structure learning and inference. For all: MCMC warmup (burn-in) discards initial samples (non-stationary). Thinning reduces autocorrelation (keep every k-th sample). Convergence: multiple chains from overdispersed starting points. R-hat: between-chain variance / within-chain variance. Close to 1 = converged. Posterior intervals: equal-tailed (2.5%, 97.5%) or HPD (Highest Posterior Density, narrowest interval containing 95% probability). For reporting: communicate using probability statements: There is a 95% probability that the effect is between X and Y.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Bayesian analysis: {problem}. Model: {technique}. {hint}. Priors specified, likelihood defined, posterior computed. MCMC converged (R-hat < 1.01). Posterior summaries with credible intervals. Sensitivity analysis robust. Model checked with posterior predictive.</EXEC>",
                f"<EXEC>Bayesian solution: {problem}. Approach: {technique}. {hint}. Model built and fitted. Convergence diagnostics passed. Interpretable posterior results. Uncertainty quantified. Decision recommendation with probability statements. Ready for reporting.</EXEC>",
                f"<EXEC>Probabilistic model: {problem}. Method: {technique}. {hint}. Prior choice justified. Inference completed. Posterior distributions summarized. Model comparison favors this specification. Posterior predictive checks validate fit. Results actionable with quantified uncertainty.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

HYPTEST_TOPICS = [
    ("design an experiment to compare two website layouts with conversion rate", "two-sample z-test for proportions; sample size calculation; A/B testing framework", "H0: p_A = p_B; test statistic: z = (p_A - p_B) / sqrt(p*(1-p)*(1/n_A + 1/n_B)); reject if |z| > 1.96"),
    ("implement a permutation test for difference in means (non-parametric)", "shuffle group labels many times, compute observed test statistic, p-value = proportion of shuffled stats exceeding observed", "no normality assumption; exact test (all permutations) or approximate (random permutations); robust to outliers"),
    ("design a multiple hypothesis testing correction strategy", "Bonferroni: alpha/m; FDR (Benjamini-Hochberg): rank p-values, compare to (i/m)*Q", "FWER (Bonferroni) controls probability of any false positive; FDR controls expected proportion of false positives among rejections"),
    ("implement a chi-square test for independence between categorical variables", "observed vs expected under independence; chi-sq = sum((O-E)^2/E); df = (r-1)*(c-1)", "expected = row_total * col_total / grand_total; reject if test stat > chi^2 critical value; Cramers V for effect size"),
    ("design a power analysis to determine required sample size for an experiment", "power = P(reject H0 | H1 true); depends on alpha, effect size, sample size, variance", "n = (Z_alpha + Z_beta)^2 * 2*sigma^2 / delta^2 for two-sample t-test; use pilot study for variance estimate"),
    ("implement an ANOVA to compare means across multiple groups", "one-way ANOVA: F = MS_between / MS_within; MS = SS/df; follows F-distribution under H0", "SS_between = sum(n_i*(x_i_bar - grand_mean)^2); SS_within = sum((n_i-1)*s_i^2); post-hoc Tukey HSD for pairwise comparisons"),
    ("design a sequential analysis with early stopping rules", "group sequential design: O'Brien-Fleming boundaries; alpha spending function", "split alpha across interim analyses; OBF: very strict early, relaxed later; Pocock: constant boundary at each look"),
]

def _hyptest_gen():
    while True:
        for problem, technique, hint in HYPTEST_TOPICS:
            inp = pick(
                f"Hypothesis testing: {problem}. Design the statistical test.",
                f"Statistical testing: {problem}. Choose test and interpret results.",
                f"Given: {problem}. Implement with proper assumptions and power.",
                f"Experimental design: {problem}. Handle multiple comparisons and power.",
            )
            plan = pick(
                f"<PLAN>Hypothesis test: {problem}. {technique}: {hint}. Plan: (1) Define H0 and H1. (2) Choose test statistic. (3) Determine distribution under H0. (4) Compute p-value. (5) Interpret: reject or not. (6) Report effect size and CI.</PLAN>",
                f"<PLAN>Statistical test for {problem}: {technique}. {hint}. Steps: (1) Check assumptions. (2) Compute test statistic. (3) Compare to null distribution. (4) Calculate p-value. (5) Multiple comparison correction if needed. (6) Conclusion with caution.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Pre-register analysis plan. (2) Power analysis for sample size. (3) Data collection. (4) Assumption checking. (5) Main analysis. (6) Sensitivity analysis. (7) Report.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing hypothesis test for {problem}: {technique}. {hint}. Statistical hypothesis testing: H0 (null: no effect) vs H1 (alternative: there is effect). p-value: probability of observing data as extreme as actual, assuming H0 true. If p < alpha (0.05), reject H0. But p-value is not P(H0|data). For proportions test: z-test requires np > 5 and n(1-p) > 5 for normal approximation. Fisher exact test for small samples. For permutation test: no distributional assumptions. Shuffle group labels B times (B=10000). Compute statistic each time. Two-sided p-value: 2 * min(proportion shuffles > observed, < observed). For multiple testing: Bonferroni: alpha / m (conservative, independent tests). Bonferroni-Holm: step-down, more powerful. FDR: Benjamini-Hochberg: sort p-values, find largest p_k < (k/m)*Q, reject all with p <= p_k. FDR is less conservative, appropriate for many tests (genomics, ML features). For chi-square: expected counts > 5 per cell assumption. Fisher exact test for small cells. For power analysis: effect size must be practically meaningful (not just statistically significant). Small effects require huge n. For ANOVA: assumptions: normality of residuals, homogeneity of variance (Levene test), independence. If violated: Kruskal-Wallis (non-parametric). Post-hoc: Tukey HSD (controls family-wise error) or Dunnett (vs control). For sequential analysis: group sequential design allows stopping early if effect is large. O'Brien-Fleming: extremely conservative early boundaries (requires large effect to stop early), relaxed later. Alpha spending function: distribute alpha across looks flexibly. For all: pre-registration prevents p-hacking and HARKing (Hypothesizing After Results are Known). Report effect sizes and confidence intervals alongside p-values.</THINK>",
                f"<THINK>Analyzing hypothesis testing for {problem}: {technique} with {hint}. Common pitfalls: (1) p-hacking: running multiple tests, reporting only significant. (2) Optional stopping: collecting more data until significant. (3) Garden of forking paths: many possible analyses, choose one that gives significant. (4) Misinterpreting p-value: not the probability H0 is true. (5) Ignoring assumptions. For permutation test: advantage: exact p-value (no approximation). Disadvantage: computationally expensive. For n < 20, enumerate all permutations (exact). For larger, random sample (approximate). For multiple testing: FWER control appropriate when a single false positive is costly (confirmatory). FDR appropriate for exploratory (many tests, accept some false positives). For power analysis: retrospective power (computed after study) is meaningless. Prospective power determines sample size needed. For equivalence testing: TOST (two one-sided tests) to show effect is within [delta_low, delta_high]. Useful when goal is to show no important effect. For Bayesian alternative: use Bayes factor (BF) for evidence quantification. BF > 3: moderate evidence for H1; BF > 10: strong. BF < 1/3: moderate evidence for H0. For all: report with uncertainty: point estimate, CI, p-value, interpretation. Pre-register to separate confirmatory from exploratory analyses.</THINK>",
                f"<THINK>Deep hypothesis test implementation for {problem}: {technique}. {hint}. For proportion test: scipy.stats.proportions_ztest or chi2_contingency. For permutation test: manual implementation: observed = mean(group1) - mean(group2). pooled = np.concatenate([group1, group2]). B=10000. perm_diffs = [np.mean(random_perm[:n1]) - np.mean(random_perm[n1:]) for _ in range(B)]. p = np.mean(abs(perm_diffs) >= abs(observed)). For Bonferroni: adjusted_alpha = alpha / m. For BH: p_sorted = np.sort(p_values); rank = np.arange(1, m+1); bh_critical = (rank / m) * Q; reject = p_sorted < bh_critical; find max rank where true, reject all with p <= p_sorted[rank]. For chi-square: scipy.stats.chi2_contingency(observed). Returns chi2, p, df, expected. For ANOVA: scipy.stats.f_oneway. Tukey: statsmodels.stats.multicomp.pairwise_tukeyhsd. For power: statsmodels.stats.power.TTestIndPower.solve_power(effect_size, alpha, power, ratio). For all: set random seed for reproducibility. Document all analysis decisions. Provide code for full reproducibility. Include sensitivity analysis: show how results change with different assumptions, exclusions, preprocessing choices.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Hypothesis test: {problem}. Method: {technique}. {hint}. Test implemented. Assumptions checked. p-value computed. Effect size reported. Multiple comparisons corrected. Power adequate. Results interpreted cautiously. Pre-registered analysis plan followed.</EXEC>",
                f"<EXEC>Statistical test: {problem}. Approach: {technique}. {hint}. H0 and H1 defined. Test statistic computed. p-value = X. Conclusion: reject/fail to reject H0. Effect size: Y (CI). Sensitivity analysis robust. Results reported with full methodology.</EXEC>",
                f"<EXEC>Hypothesis testing: {problem}. Design: {technique}. {hint}. Pre-registered. Power analysis done. Test executed. Corrected for multiplicity. Results: significant/non-significant. Effect size practically meaningful. Interpretation caveats documented.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

REGRESSION_TOPICS = [
    ("design a multiple linear regression model with interaction terms", "y = b0 + b1*x1 + b2*x2 + b3*x1*x2 + epsilon; interaction captures non-additive effects", "center variables before creating interactions to reduce multicollinearity; interpret simple slopes at different levels of moderator"),
    ("implement logistic regression for binary classification with L1 regularization", "lasso logistic regression: loss = log_loss + lambda * ||beta||_1; drives some coefficients to zero", "L1 for feature selection; L2 for shrinkage; ElasticNet for both; tune lambda via cross-validation"),
    ("design a Poisson regression for count data (e.g., number of accidents)", "log link: log(mu) = X*beta; mu = rate parameter for Poisson distribution", "offset for exposure: log(rate) = X*beta + log(exposure); check for overdispersion (variance > mean); negative binomial alternative"),
    ("implement a Cox proportional hazards model for survival analysis", "h(t) = h0(t) * exp(X*beta); baseline hazard h0 arbitrary; partial likelihood estimates beta", "hazard ratio = exp(beta); proportional hazards assumption: hazard ratio constant over time; Kaplan-Meier for visualization"),
    ("design a mixed-effects model for repeated measures or hierarchical data", "y = X*beta + Z*u + epsilon; random effects u ~ N(0, G); fixed effects beta", "random intercept: each subject has own baseline; random slope: each subject has own time trend; lme4/rstan for estimation"),
    ("implement ridge regression with the bias-variance trade-off", "L2 penalty: loss = MSE + lambda * ||beta||_2^2; closed form: beta = (X^T X + lambda*I)^{{-1}} X^T y", "lambda controls shrinkage; larger lambda = lower variance, higher bias; solution via SVD: shrinks along PCs proportional to eigenvalues"),
    ("design a quantile regression for robust prediction at different percentiles", "minimize sum of absolute deviations with tilted loss: rho_tau(u) = u*(tau - I(u<0))", "no normality assumption; robust to outliers; predicts median (tau=0.5) or any quantile; confidence intervals via bootstrap or rank inversion"),
]

def _regression_gen():
    while True:
        for problem, technique, hint in REGRESSION_TOPICS:
            inp = pick(
                f"Regression analysis: {problem}. Design the model and interpret.",
                f"Regression: {problem}. Handle assumptions and regularization.",
                f"Given: {problem}. Fit, diagnose, and interpret the regression model.",
                f"Statistical modeling: {problem}. Choose appropriate regression type.",
            )
            plan = pick(
                f"<PLAN>Regression approach: {problem}. {technique}: {hint}. Plan: (1) Exploratory analysis of relationships. (2) Specify regression equation. (3) Check assumptions (linearity, independence, homoscedasticity, normality). (4) Fit model. (5) Diagnose residuals. (6) Interpret coefficients. (7) Validate predictions.</PLAN>",
                f"<PLAN>Regression solution for {problem}: {technique}. {hint}. Steps: (1) Data preprocessing. (2) Feature selection/engineering. (3) Model specification. (4) Parameter estimation. (5) Diagnostic plots (residuals vs fitted, Q-Q, scale-location). (6) Model improvement. (7) Interpretation and reporting.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Outcome and predictor selection. (2) Functional form. (3) Regularization/random effects. (4) Estimation method. (5) Model diagnostics. (6) Inference and uncertainty. (7) Predictions.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing regression model for {problem}: {technique}. {hint}. Regression models the relationship between outcome and predictors. For linear regression: OLS minimizes sum of squared residuals. Assumptions: linearity, independence, homoscedasticity (constant variance), normality of residuals (for inference). Violations: non-linearity (transform predictors or use polynomials), heteroscedasticity (robust standard errors, weighted least squares), autocorrelation (ARIMA, GLS), non-normality (bootstrapping for inference). Interaction terms: product of two predictors. Centering (subtract mean) reduces multicollinearity between main effects and interaction. Simple slope: effect of x1 at specific level of x2 = b1 + b3*x2. For logistic regression: logit(p) = log(p/(1-p)) = X*beta. L1 regularization (lasso): encourages sparsity. L2 (ridge): shrinks coefficients. ElasticNet: combination. Regularization improves prediction by reducing overfitting. For Poisson regression: for count outcomes. Log link ensures positive predictions. Overdispersion: variance > mean, use quasi-Poisson or negative binomial. For Cox model: semi-parametric: baseline hazard estimated non-parametrically. Partial likelihood: estimates beta without specifying h0(t). Proportional hazards: the effect of predictors on hazard is constant over time. Check with Schoenfeld residuals. For mixed effects: fixed effects (population-level) + random effects (subject-specific). Random intercept: y_it = mu + alpha_i + beta*x_it + epsilon_it. alpha_i ~ N(0, sigma_alpha^2). Random slope: allow beta to vary across subjects. For ridge regression: penalized likelihood. Tuning parameter lambda chosen via CV. Ridge solution shrinks but does not select features. For quantile regression: estimates conditional quantile. Robust to outliers in outcome. Asymmetric absolute error loss function. Coefficients interpreted as effect on specified quantile.</THINK>",
                f"<THINK>Analyzing regression for {problem}: {technique} with {hint}. Model diagnostics: (1) Residuals vs fitted: check for non-linearity or heteroscedasticity. (2) Q-Q plot: check normality. (3) Scale-location: sqrt(|residuals|) vs fitted, check homoscedasticity. (4) Residuals vs leverage: identify influential points (Cook's distance). For multicollinearity: VIF > 10 indicates problematic collinearity. Solutions: remove correlated predictors, PCA, ridge regression. For categorical predictors: n levels -> n-1 dummy variables. Choose reference category wisely. For interactions: plot interactions (interaction.plot, ggplot with facet). Simple slopes analysis for moderation. For logistic regression: pseudo-R^2 (McFadden, Cox-Snell, Nagelkerke). Hosmer-Lemeshow test for calibration. AUC-ROC for discrimination. For Poisson: check dispersion parameter. If > 1.25, consider negative binomial. Zero-inflated models if excess zeros. For Cox: Kaplan-Meier survival curves per group. Log-rank test compares groups. Cox-Snell residuals for overall fit. For mixed effects: likelihood ratio test for random effects significance. REML vs ML: REML for variance components, ML for fixed effects comparison. For all: report coefficients with CIs, not just p-values. Standardize for comparability. Model comparison: AIC, BIC (lower better). Cross-validated prediction error.</THINK>",
                f"<THINK>Deep regression implementation for {problem}: {technique}. {hint}. For OLS with interactions: smf.ols('y ~ x1 * x2', data). The * adds x1, x2, and x1:x2. Centering: x1_c = x1 - x1.mean(). Interpretation: b1 is effect of x1 when x2=mean. For lasso logistic: sklearn.linear_model.LogisticRegression(penalty='l1', solver='saga', C=1/lambda). For ridge: sklearn.linear_model.Ridge. CV: sklearn.linear_model.RidgeCV. For Poisson: smf.glm('y ~ x', data, family=sm.families.Poisson()). offset=log(exposure). NegativeBinomial if overdispersed. For Cox: lifelines.CoxPHFitter, fit with formula. Check proportional hazards: model.check_assumptions(). Plot survival: model.plot_partial_effects_on_outcome(). For mixed effects: statsmodels.MixedLM from formula. R formula: 'y ~ x + (1|group)' (random intercept). 'y ~ x + (x|group)' (random slope and intercept). For quantile regression: statsmodels.QuantReg(y, X).fit(q=0.5) for median. For all: use robust standard errors (HC3) for inference when homoscedasticity violated. Check influential points: cooks_distance, dffits, dfbetas. Document preprocessing steps. Report full model summary: coefficients, SE, CI, t/z, p, VIF, R^2.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Regression analysis: {problem}. Model: {technique}. {hint}. Assumptions checked, model fitted, diagnostics reviewed. Coefficients interpreted with CIs. Regularization tuned. Goodness-of-fit: R^2/AIC/BIC. Validation via CV. Predictions with uncertainty.</EXEC>",
                f"<EXEC>Regression solution: {problem}. Approach: {technique}. {hint}. Model specification, estimation, diagnostics, interpretation complete. Robust SE used if needed. All assumptions verified or addressed. Reporting includes effect sizes and uncertainty. Code reproducible.</EXEC>",
                f"<EXEC>Regression: {problem}. Method: {technique}. {hint}. Model selected based on outcome type. Fit with appropriate estimation. Diagnostics: residuals well-behaved, no influential points. Coefficients signed as expected. Predictive performance validated.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

CLUSTERING_TOPICS = [
    ("design a customer segmentation using k-means with proper validation", "scale features, k-means++, elbow plot, silhouette score, interpret clusters", "determine k via elbow (within-cluster SSE) and silhouette; profile clusters by mean feature values; visualize with PCA"),
    ("implement hierarchical clustering for taxonomy of products", "agglomerative clustering with Ward linkage; cut dendrogram at desired height for k clusters", "Ward minimizes within-cluster variance; dendrogram shows merge order; cutting gives flat clusters; interpret via cluster profiles"),
    ("design a density-based clustering for spatial data with irregular shapes", "DBSCAN: eps and minPts parameters; core points expand clusters; noise points left unassigned", "HDBSCAN: hierarchical DBSCAN, finds stable clusters across densities; better for varying density; no need to choose eps"),
    ("implement spectral clustering for non-convex clusters", "construct similarity graph, compute Laplacian eigenvectors, cluster with k-means on eigenvectors", "fully connected (RBF kernel), k-nearest neighbor, or epsilon graph; Normalized Laplacian; eigenvectors embed non-linear structure"),
    ("design a cluster evaluation framework without ground truth", "internal metrics: silhouette, Davies-Bouldin, Calinski-Harabasz; stability analysis via bootstrap", "silhouette: (-1 to 1, higher better); DB: lower better; CH: higher better. Stability via adjusted Rand index"),
    ("implement Gaussian Mixture Model for soft clustering with uncertainty", "EM algorithm: E-step compute responsibilities; M-step update parameters; BIC/AIC for selection", "soft assignment: each point has probability per cluster; BIC penalizes complexity; full vs tied vs diag covariance"),
]

def _clustering_gen():
    while True:
        for problem, technique, hint in CLUSTERING_TOPICS:
            inp = pick(
                f"Clustering: {problem}. Design the approach and validate.",
                f"Unsupervised clustering: {problem}. Handle scale and interpretation.",
                f"Given: {problem}. Choose algorithm, parameters, and validation.",
                f"Cluster analysis: {problem}. Interpret results with domain context.",
            )
            plan = pick(
                f"<PLAN>Clustering approach: {problem}. {technique}: {hint}. Plan: (1) Preprocess: scale, handle missing, reduce dimension. (2) Choose algorithm. (3) Determine parameters. (4) Fit model. (5) Validate with internal metrics. (6) Interpret clusters: profile by feature means. (7) Visualize results.</PLAN>",
                f"<PLAN>Clustering solution for {problem}: {technique}. {hint}. Steps: (1) Feature selection. (2) Distance/similarity. (3) Algorithm selection. (4) Parameter tuning. (5) Cluster assignment. (6) Evaluation. (7) Cluster characterization.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Data prep and scaling. (2) Algorithm choice. (3) Parameter selection. (4) Execution. (5) Internal validation. (6) Cluster profiling. (7) Reporting.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing clustering for {problem}: {technique}. {hint}. K-means: spherical clusters. Sensitive to scaling. K-means++ initialization. Elbow plot SEE vs k. Silhouette: a(i) = avg distance to own cluster, b(i) = min avg to other clusters. s(i) = (b-a)/max(a,b). Average > 0.5 indicates structure. Hierarchical: Ward minimizes within-cluster variance. Dendrogram cut at desired height. DBSCAN: eps and minPts. K-distance graph helps choose eps. HDBSCAN handles varying density. Spectral: captures non-convex shapes via Laplacian embedding. GMM: soft clustering, EM algorithm, BIC for model selection. Without labels, internal metrics only suggest good clustering. Domain knowledge validates. Stability across bootstrap samples confirms robustness.</THINK>",
                f"<THINK>Analyzing clustering for {problem}: {technique} with {hint}. Algorithm choice: (1) Spherical equal-sized: k-means. (2) Unknown number: hierarchical. (3) Arbitrary shapes, noise: DBSCAN. (4) Non-convex: spectral. (5) Soft assignment: GMM. Large datasets: k-means O(nkd*i), DBSCAN O(n log n) with index. High dimensions: curse of dimensionality. All distances become similar. Use DR first. Standardize features. For evaluation: silhouette best internal metric. DB: lower better. CH: higher better. External (if labels): ARI, NMI, homogeneity, completeness, V-measure.</THINK>",
                f"<THINK>Deep clustering implementation for {problem}: {technique}. {hint}. sklearn.cluster.KMeans(n_clusters=k, init='k-means++', n_init=10). scipy.cluster.hierarchy.linkage(method='ward'). dendrogram. fcluster for cut. DBSCAN(eps=0.5, min_samples=5). HDBSCAN from hdbscan library. SpectralClustering(n_clusters=k, affinity='rbf'). GaussianMixture(n_components=k, covariance_type='full'). Use BIC for selection. For all: set random_state. Compare multiple algorithms. Report cluster profiles (feature means per cluster). Visualize with PCA/t-SNE.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Clustering: {problem}. Method: {technique}. {hint}. Data scaled, parameters tuned via internal validation. Clusters profiled and interpreted. Visualization shows separation. Stability confirmed. Results validated with domain knowledge.</EXEC>",
                f"<EXEC>Cluster analysis: {problem}. Approach: {technique}. {hint}. Optimal k determined via elbow+silhouette. Cluster profiles meaningful. Algorithm assumptions met. Evaluation metrics favorable. Results actionable.</EXEC>",
                f"<EXEC>Unsupervised clustering: {problem}. Design: {technique}. {hint}. Preprocessing, clustering, validation complete. Clusters interpretable. Stability confirmed. Visualizations support findings.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

DIMRED_TOPICS = [
    ("implement PCA for dimensionality reduction with explained variance analysis", "SVD of centered data matrix; select k components by cumulative explained variance > threshold", "standardize before PCA; explained variance from singular values; scree plot for k selection; biplot for interpretation"),
    ("design a feature selection pipeline using mutual information", "compute MI between each feature and target; select top k features by MI score", "MI captures non-linear relationships; handles continuous and categorical; use kNN-based estimation"),
    ("implement t-SNE for visualization of high-dimensional clusters", "convert distances to probabilities, minimize KL divergence between high-D and low-D probabilities", "perplexity (5-50) balances local/global; PCA init for stability; multiple runs to assess stability"),
    ("design a feature extraction using autoencoders", "encoder compresses to bottleneck, decoder reconstructs; bottleneck activations are features", "undercomplete for compression; sparse for interpretability; denoising for robust features"),
    ("implement forward feature selection with cross-validation", "start with empty set, iteratively add feature that most improves CV score", "wrapper method; O(k^2) fits for k features; use for k < 50; RFE is alternative"),
    ("design a factor analysis model to identify latent variables", "observed = loadings * latent factors + noise; factors explain covariance structure", "PCA vs FA: PCA explains variance, FA explains covariance; rotation (varimax) for interpretability"),
]

def _dimred_gen():
    while True:
        for problem, technique, hint in DIMRED_TOPICS:
            inp = pick(
                f"Dimensionality reduction: {problem}. Design the approach.",
                f"Feature reduction: {problem}. Balance information and interpretability.",
                f"Given: {problem}. Reduce dimensions while preserving structure.",
                f"Dimension reduction: {problem}. Choose method and validate.",
            )
            plan = pick(
                f"<PLAN>DR approach: {problem}. {technique}: {hint}. Plan: (1) Scale data. (2) Choose method. (3) Determine target dimension. (4) Fit transformation. (5) Validate information retention. (6) Interpret features. (7) Use downstream.</PLAN>",
                f"<PLAN>Reduce dimensions for {problem}: {technique}. {hint}. Steps: (1) Preprocessing. (2) Method selection. (3) Parameter selection. (4) Fit and transform. (5) Evaluate. (6) Interpret.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Understand data. (2) Choose method. (3) Implementation. (4) Retention check. (5) Interpretability. (6) Downstream validation.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing DR for {problem}: {technique}. {hint}. PCA: linear, orthogonal. First PC captures max variance. SVD: X = U*S*V^T. PCs = V. Explained variance = S^2 / sum(S^2). Scree plot for k selection. Biplot shows feature contributions. For MI: I(X;Y) = sum(p(x,y)*log(p/(p_x*p_y))). Non-parametric. feature_selection.mutual_info_classif/regression. For t-SNE: pairwise similarities. Perplexity controls sigma. Non-convex loss, multiple runs. UMAP alternative: faster, preserves more global structure. For autoencoders: neural net with bottleneck. Undercomplete: forced compressed representation. Denoising: robust representations. For forward selection: greedy. RFE: recursive elimination based on model weights. For FA: latent variables explain covariances. Varimax rotation maximizes high loadings for interpretability. For all: standardize before PCA/FA. Validate: reconstruction error, downstream task performance. Visualize 2D/3D projections colored by target.</THINK>",
                f"<THINK>Analyzing DR for {problem}: {technique} with {hint}. PCA: fast, globally interpretable. t-SNE: non-linear, local preservation. UMAP: non-linear, more global. For non-linear structure: t-SNE/UMAP better. For interpretability: PCA loadings, FA rotated loadings, feature selection retains original features. For large data: randomized SVD, UMAP scales. Autoencoders: tune bottleneck size. For validation: reconstruction error, visualization quality, downstream task improvement. For all: no single best method. Try multiple, compare, use domain knowledge.</THINK>",
                f"<THINK>Deep DR implementation for {problem}: {technique}. {hint}. sklearn.decomposition.PCA(n_components=k). RandomizedPCA for large n. mutual_info_classif. SelectKBest(mutual_info_classif, k=10). sklearn.manifold.TSNE(perplexity=30). init='pca'. umap.UMAP(n_neighbors=15). Autoencoder: keras Model. Encoder Dense(bottleneck, 'relu'). Decoder Dense(input_dim). Loss: MSE. RFE: sklearn.feature_selection.RFE(estimator, n_features_to_select). For all: set seed. Visualize: PC1 vs PC2 colored by target.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Dimensionality reduction: {problem}. Method: {technique}. {hint}. Transformation fitted. Information retention at X%. Interpretable features/components. Downstream validation positive. Visualization reveals structure.</EXEC>",
                f"<EXEC>DR solution: {problem}. Approach: {technique}. {hint}. Reduced from D to d dimensions. Retention validated. Features interpretable or relevant. Downstream task maintained or improved.</EXEC>",
                f"<EXEC>Feature reduction: {problem}. Design: {technique}. {hint}. Preprocessing, transformation, validation complete. Reduced representation preserves essential structure. Ready for analysis.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "data_science")

CAUSAL_TOPICS = [
    ("design a causal inference study for a marketing campaign effect", "difference-in-differences: compare treated vs control before/after; parallel trends", "DiD: (post_treat - pre_treat) - (post_control - pre_control); cluster SE at unit level; test parallel trends"),
    ("implement propensity score matching for observational studies", "estimate P(treatment | covariates) via logistic regression; match treated to control on propensity", "nearest neighbor with caliper; check balance via standardized mean differences; IPW alternative"),
    ("design a regression discontinuity design for policy evaluation", "identify cutoff in assignment variable; compare just above vs below cutoff; local linear regression", "bandwidth selection (Imbens-Kalyanaraman); check continuity of covariates at cutoff; donut RD"),
    ("implement instrumental variables estimation for endogenous treatment", "IV: treatment predicted by instrument; two-stage least squares (2SLS)", "instrument relevance (F > 10) and exogeneity (overidentification test); LATE for compliers"),
    ("design a causal graph (DAG) and identify adjustment set for causal effect", "draw DAG with exposure, outcome, confounders, mediators, colliders; backdoor criterion", "confounder: adjust; collider: do not adjust; mediator: do not adjust for direct effect; use do-calculus"),
    ("implement a synthetic control method for comparative case studies", "weight control units to match pre-treatment outcome of treated; post-treatment gap = effect", "weights non-negative sum to 1; minimize pre-RMSE; inference via placebo tests"),
    ("design a randomized controlled trial with blocked randomization", "block by covariates predicting outcome; randomize within blocks; analyze with strata FE", "blocks ensure covariate balance; stratification increases precision; pre-register analysis plan"),
]

def _causal_gen():
    while True:
        for problem, technique, hint in CAUSAL_TOPICS:
            inp = pick(
                f"Causal inference: {problem}. Design the identification strategy.",
                f"Causal analysis: {problem}. Handle confounding and selection bias.",
                f"Given: {problem}. Estimate causal effect with observational data.",
                f"Causal reasoning: {problem}. Choose strategy and validate assumptions.",
            )
            plan = pick(
                f"<PLAN>Causal inference: {problem}. {technique}: {hint}. Plan: (1) Causal question. (2) Draw DAG. (3) Identification strategy. (4) Check assumptions. (5) Estimate. (6) Sensitivity analysis. (7) Interpret.</PLAN>",
                f"<PLAN>Causal analysis for {problem}: {technique}. {hint}. Steps: (1) Causal model. (2) Identification conditions. (3) Estimator. (4) Balance/diagnostics. (5) Effect and CIs. (6) Robustness. (7) Report.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Units. (2) Pre-treatment covariates. (3) Identification assumption. (4) Estimation. (5) Inference. (6) Sensitivity. (7) Conclusion.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing causal study for {problem}: {technique}. {hint}. Causal inference requires strong assumptions. DiD: parallel trends assumption. Test with pre-treatment periods. Event study. Propensity score: conditional on PS, treatment independent of potential outcomes. Balance: SMD < 0.1. RDD: cutoff creates quasi-experiment. Covariates continuous at cutoff. McCrary density test. IV: instrument relevant and exogenous. Weak instruments (F < 10) problematic. DAG: backdoor criterion for adjustment set. Must block all backdoor paths, not include descendants of treatment or colliders. Synthetic control: weights match pre-treatment trajectory. Placebo test for inference. RCT: gold standard. Randomization balances confounders. Pre-registration prevents p-hacking. For all: sensitivity analysis (E-value). Report with caution appropriate to identification strength.</THINK>",
                f"<THINK>Analyzing causal {problem}: {technique} with {hint}. Potential outcomes (Rubin): each unit has Y(1), Y(0). Only observe one. DAGs (Pearl): causal diagram. do-calculus. For DiD: two-way FE: Y = beta*Treat*Post + alpha_i + gamma_t. Staggered adoption: Sun-Abraham, Callaway-Sant Anna. For matching: 1:1 nearest neighbor with replacement. IPW: weight = Z/e + (1-Z)/(1-e). For RDD: local linear with triangular kernel. bandwidth selection. For IV: 2SLS. First stage F > 10. LATE for compliers. For all: test assumptions, relax when possible. Sensitivity: how large would unmeasured confounding need to be? E-value calculation.</THINK>",
                f"<THINK>Deep causal implementation for {problem}: {technique}. {hint}. DiD: smf.ols('Y ~ Treat*Post + C(unit) + C(time)'). cluster='unit'. Event study: leads/lags of treatment. PS matching: sklearn LogisticRegression. Caliper 0.25*SD. SMD check. RDD: rdrobust (R) or rdd (Python). MSE-optimal bandwidth. IV: linearmodels.IV2SLS. DAG: dagitty or causalgraphicalmodels. Synthetic control: augsynth (R). For all: bootstrap CI. Report ATE, CI, p-value. E-value. Pre-register. Code and data for reproducibility.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Causal analysis: {problem}. Method: {technique}. {hint}. Effect estimated. Assumptions checked. Sensitivity analysis done. Balance achieved. Causal claim supported with transparent assumptions.</EXEC>",
                f"<EXEC>Causal inference: {problem}. Approach: {technique}. {hint}. Causal effect: X (CI). Identification assumptions stated and tested. Robustness confirmed. Sensitivity to unmeasured confounding assessed.</EXEC>",
                f"<EXEC>Causal study: {problem}. Design: {technique}. {hint}. Treatment effect identified. Assumptions plausible. Estimates robust. Pre-registered analysis. Potential outcomes framework. Cautious interpretation.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "data_science")

def chunk_9_gen():
    gens = [_viz_gen(), _timeseries_gen(), _bayesian_gen(), _hyptest_gen(), _regression_gen(),
            _clustering_gen(), _dimred_gen(), _causal_gen()]
    while True:
        for g in gens:
            yield next(g)

# ═══════════════════════════════════════════════════════════════════════════
# Chunk 10: Security & Cryptography
# ═══════════════════════════════════════════════════════════════════════════

CRYPTO_TOPICS = [
    ("design a symmetric encryption system using AES-GCM", "AES-256-GCM: 256-bit key, 12-byte nonce, authenticated encryption with AAD", "encrypt-then-MAC; GCM provides both; nonce must never repeat"),
    ("implement RSA key generation, encryption, and decryption from scratch", "generate p,q; compute n=pq, phi(n); e=65537; d = e^-1 mod phi(n)", "2048+ bits; OAEP padding; textbook RSA insecure; CRT for speed"),
    ("design a Diffie-Hellman key exchange with ephemeral keys", "ECDHE: ephemeral keypair per session; ECDH shared secret; forward secrecy", "perfect forward secrecy; Curve25519 modern choice"),
    ("implement elliptic curve cryptography (ECDSA) for signatures", "generate keypair on P-256; sign: hash, compute (r,s); verify: check equation", "nonce k must be random; deterministic ECDSA RFC 6979 avoids k reuse"),
    ("design a secure hash function usage with salting for passwords", "store hash(password + salt); use argon2 for key derivation", "argon2: memory/time/parallel-hard; salt prevents rainbow tables"),
    ("implement a Merkle tree for data integrity verification", "leaf: hash(block); internal: hash(children); root commitment; O(log n) proof", "Git, blockchains, certificate transparency use Merkle trees"),
    ("design a post-quantum cryptographic primitive (lattice-based)", "LWE/ring-LWE: security from lattice problem hardness", "quantum breaks RSA/ECC; NIST: Kyber, Dilithium; lattice-based"),
]

def _crypto_gen():
    while True:
        for problem, technique, hint in CRYPTO_TOPICS:
            inp = pick(
                f"Cryptography: {problem}. Design the cryptographic system.",
                f"Crypto: {problem}. Implement with proper security parameters.",
                f"Given: {problem}. Choose algorithms and parameters.",
                f"Secure system: {problem}. Handle key management.",
            )
            plan = pick(
                f"<PLAN>Crypto design: {problem}. {technique}: {hint}. Plan: (1) Security requirements. (2) Algorithm selection. (3) Key generation. (4) Implementation. (5) Side-channel resistance. (6) Testing. (7) Security review.</PLAN>",
                f"<PLAN>Cryptographic system for {problem}: {technique}. {hint}. Steps: (1) Goals. (2) Primitives. (3) Implementation. (4) Key management. (5) Test vectors. (6) Hardening.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Primitive specs. (2) Implementation. (3) Parameters. (4) Security analysis. (5) Interoperability. (6) Testing.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing crypto for {problem}: {technique}. {hint}. AES-GCM: 256-bit key, 96-bit nonce, never reuse nonce. GCM = CTR + GHASH. RSA OAEP padding provably secure. Minimum 2048 bits. CRT decrypt with dp, dq, qinv. ECDHE: ephemeral keys ensure forward secrecy. Curve25519 safe, constant-time. ECDSA: nonce k must be secret and unique. Deterministic ECDSA derives k from key+hash. Argon2: memory-hard, time-hard. Salt 16-32 bytes. Merkle tree: verify inclusion with O(log n) proof. Post-quantum: Kyber (KEM), Dilithium (signatures). Lattice-based. For all: use well-vetted libraries, constant-time, zero secrets after use.</THINK>",
                f"<THINK>Analyzing crypto for {problem}: {technique} with {hint}. Security levels: AES-128: 128-bit. RSA-2048: 112-bit. ECC-256: 128-bit. Post-quantum: Kyber-512 ~128-bit. Common pitfalls: ECB mode, nonce reuse, weak PRNG, timing attacks, padding oracle. Use standard libraries. For password storage: argon2id recommended. For signatures: deterministic ECDSA prevents k reuse attacks. For key exchange: ECDHE with HKDF key derivation. For all: document threat model. Guide algorithm choice.</THINK>",
                f"<THINK>Deep crypto implementation for {problem}: {technique}. {hint}. AES-GCM: cryptography library. cipher = AES.new(key, MODE_GCM, nonce). encrypt_and_digest. RSA: rsa.generate_private_key(65537, 2048). OAEP padding. ECDSA: ec.generate_private_key(SECP256R1). sign with ECDSA(SHA256). Argon2: PasswordHasher(time=3, memory=65536). Merkle: hashlib.sha256. Proof: sibling hashes. For all: secrets module, hmac.compare_digest, avoid string ops in sensitive code. Key management: HSM or vault. Periodic rotation.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Cryptography: {problem}. Design: {technique}. {hint}. Correct parameters, proven primitives. Side-channel resistant. Key management secure. Test vectors pass.</EXEC>",
                f"<EXEC>Crypto solution: {problem}. Method: {technique}. {hint}. Algorithm with proper padding/mode/nonce. Secure key generation. Timing attacks mitigated. Memory safe.</EXEC>",
                f"<EXEC>Secure system: {problem}. Approach: {technique}. {hint}. Primitives correctly composed. Security levels adequate. Constant-time. Cryptographically secure randomness.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "security")

NETSEC_TOPICS = [
    ("design a firewall rule set for a corporate network with DMZ", "default deny, allow specific services, DMZ isolates public-facing servers", "ingress: allow 80/443 to DMZ, allow established connections; egress: allow needed; DMZ cannot initiate to internal"),
    ("implement a network intrusion detection system using signature matching", "Snort/Suricata: rules match packet patterns; preprocessors normalize traffic", "rules: protocol, source/dest IP, port, content pattern; alert/block actions; regular signature updates"),
    ("design a zero-trust network architecture", "never trust, always verify; micro-segmentation; per-request authentication and authorization", "all traffic encrypted; least privilege; continuous verification; no implicit trust based on network location"),
    ("implement a VPN tunnel using WireGuard", "WireGuard: simple, fast, modern VPN; UDP-based; Noise protocol framework", "each peer has private/public keypair; cryptokey routing; perfect forward secrecy; minimal configuration"),
    ("design secure DNS architecture with DNSSEC and DNS-over-HTTPS", "DNSSEC: sign DNS records; validate chain of trust; DoH: encrypt DNS queries", "DNSSEC prevents spoofing; DoH prevents surveillance; stub resolver does DoH to recursive resolver"),
    ("implement network segmentation and VLAN isolation", "VLANs separate broadcast domains; ACLs between VLANs; 802.1Q trunking", "management VLAN isolated from user VLAN; guest network separated; VoIP VLAN with QoS"),
]

def _netsec_gen():
    while True:
        for problem, technique, hint in NETSEC_TOPICS:
            inp = pick(
                f"Network security: {problem}. Design the security controls.",
                f"Network defense: {problem}. Implement with defense in depth.",
                f"Given: {problem}. Design architecture and rule sets.",
                f"Secure networking: {problem}. Handle segmentation and monitoring.",
            )
            plan = pick(
                f"<PLAN>Network security: {problem}. {technique}: {hint}. Plan: (1) Threat model. (2) Security requirements. (3) Architecture design. (4) Rule/policy definition. (5) Implementation. (6) Testing and validation. (7) Monitoring and maintenance.</PLAN>",
                f"<PLAN>Network defense for {problem}: {technique}. {hint}. Steps: (1) Asset identification. (2) Attack surface analysis. (3) Control selection. (4) Configuration. (5) Pen testing. (6) Monitoring setup.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Requirements. (2) Architecture. (3) Implementation. (4) Testing. (5) Operations.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing network security for {problem}: {technique}. {hint}. Defense in depth: multiple layers of security so one failure doesn't expose everything. Firewall: default deny, explicit allow. Stateful: tracks connection state. DMZ: public servers in DMZ, not on internal network. Internal initiates outbound; DMZ cannot initiate to internal. IDS/IPS: signature-based (known attacks), anomaly-based (behavioral deviations). Snort rules: alert tcp $EXTERNAL any -> $HTTP_SERVERS 80 (msg: SQL injection attempt; content: 'OR 1=1'; sid:1234). Zero trust: every request authenticated and authorized regardless of source. Micro-segmentation: per-application/ workload network policies. Continuous monitoring and re-evaluation. WireGuard: no configuration on connect/disconnect. Keys tied to allowed IPs. Handshake: Noise IK pattern. DoH: prevents DNS spoofing and surveillance. DNSSEC: chain of trust from root zone. RRSIG, DNSKEY, DS records. VLANs: separate traffic at layer 2. ACLs control inter-VLAN traffic. Port security prevents unauthorized devices.</THINK>",
                f"<THINK>Analyzing network security for {problem}: {technique} with {hint}. Threat modeling: STRIDE (Spoofing, Tampering, Repudiation, Info disclosure, DoS, Elevation of privilege). DREAD for risk rating. Network segmentation: reduce blast radius. DMZ architecture: three-leg firewall (external, DMZ, internal). Bastion host: hardened server in DMZ for access. IDS placement: before firewall, after firewall, on each segment. For WireGuard: no dynamic addressing built-in. Use with DHCP or network manager. Roaming: built in. For DoH: Firefox/Chrome support. Privacy-focused recursive resolvers (Cloudflare 1.1.1.1, Quad9). For DNSSEC: signed zones, validating resolvers. DS records in parent zone. For all: log and monitor. SIEM aggregates logs, correlates events. Regular security audits and penetration testing.</THINK>",
                f"<THINK>Deep netsec implementation for {problem}: {technique}. {hint}. Firewall: iptables/nftables default DROP. Allow established/related. Specific allow rules. Log blocked. IDS: Snort/Suricata config: network vars, rule files, output plugins. Barnyard2 for DB output. Zero trust: Google BeyondCorp model. Device inventory, user identity, context-aware access. WireGuard: wg0.conf: [Interface] PrivateKey, Address, ListenPort. [Peer] PublicKey, AllowedIPs, Endpoint. wg-quick up/down. DoH: unbound with forward-tls-upstream. DNSSEC validator. VLAN: switch configuration. SVI for inter-VLAN routing. VACLs for filtering. For all: test with vulnerability scanner (Nessus, OpenVAS). Pen test annually. Review logs daily.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Network security: {problem}. Design: {technique}. {hint}. Architecture planned, controls implemented. Default deny enforced. Segmentation/DMZ in place. IDS monitoring active. Firewall rules tested. Logging enabled. Security posture improved.</EXEC>",
                f"<EXEC>Network defense: {problem}. Approach: {technique}. {hint}. Zero trust/segmentation implemented. Firewall rules least privilege. IDS/IPS signatures current. VPN configured. DNSSEC validated. VLAN isolation tested.</EXEC>",
                f"<EXEC>Secure networking: {problem}. Method: {technique}. {hint}. Controls implemented and validated. Pentest results addressed. Monitoring active. Incident response plan documented. Security maturity increased.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "security")

WEBSEC_TOPICS = [
    ("design a web application firewall rule set to prevent SQL injection", "WAF: parameter validation, pattern matching for SQL keywords, prepared statements backend", "block UNION, OR 1=1, comments, stacked queries; use parameterized queries server-side as primary defense"),
    ("implement CSRF protection for a web application", "anti-CSRF token: random per-session token in forms, validated on state-changing requests", "SameSite cookie attribute (Lax/Strict); CSRF token in hidden form field; double-submit cookie pattern"),
    ("design a secure authentication flow with OAuth 2.0 and PKCE", "authorization code flow with PKCE; code verifier/challenge prevents interception", "PKCE: S256 code challenge; state parameter for CSRF; redirect_uri validation; token binding"),
    ("implement XSS prevention using Content Security Policy", "CSP headers: default-src 'self'; script-src 'nonce-...' or 'hash-...'", "inline scripts blocked without nonce; report-uri for violations; strict CSP vs allowlist CSP"),
    ("design a session management system with secure cookies", "HTTPOnly, Secure, SameSite flags; session ID generated via CSPRNG; session timeout and rotation", "session fixation prevention: regenerate on login; idle timeout; absolute timeout; encrypted session store"),
    ("implement proper HTTPS configuration with HSTS and certificate pinning", "TLS 1.3 only; strong ciphers (ECDHE + AES-GCM); HSTS header; certificate transparency", "disable TLS 1.0/1.1; disable weak ciphers (RC4, CBC, 3DES); HPKP deprecated; use CT monitoring"),
]

def _websec_gen():
    while True:
        for problem, technique, hint in WEBSEC_TOPICS:
            inp = pick(
                f"Web security: {problem}. Design the defense mechanisms.",
                f"Web app security: {problem}. Implement with OWASP best practices.",
                f"Given: {problem}. Protect against common web vulnerabilities.",
                f"Secure web development: {problem}. Handle authentication and data protection.",
            )
            plan = pick(
                f"<PLAN>Web security: {problem}. {technique}: {hint}. Plan: (1) Threat model (OWASP Top 10). (2) Identify vulnerable patterns. (3) Select controls. (4) Implement defense. (5) Test with security scanner. (6) Penetration test. (7) Monitor for bypasses.</PLAN>",
                f"<PLAN>Web defense for {problem}: {technique}. {hint}. Steps: (1) Code review. (2) Input validation. (3) Output encoding. (4) Security headers. (5) Authentication/authorization. (6) Session management. (7) Testing.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Requirements. (2) Control selection. (3) Implementation. (4) Configuration. (5) Automated testing. (6) Manual review.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing web security for {problem}: {technique}. {hint}. OWASP Top 10: injection, broken auth, sensitive data exposure, XXE, broken access control, security misconfiguration, XSS, insecure deserialization, vulnerable components, insufficient logging. For SQL injection: parameterized queries are primary defense. WAF is secondary. ORM frameworks reduce risk but raw queries still vulnerable. For CSRF: SameSite=Lax is modern defense. CSRF token in forms provides defense when SameSite not enough. Double-submit cookie: send random value as both cookie and request header, server checks match. For OAuth: Authorization Code + PKCE is standard for public clients. S256 code challenge. state parameter binds request to session. Redirect URI strict validation prevents open redirectors. For XSS: CSP is defense-in-depth. Output encoding is primary. Context-sensitive encoding: HTML entity, JavaScript string, URL encoding. DOMPurify for HTML sanitization. For session management: session ID from CSPRNG (16+ bytes). Regenerate on privilege escalation. Encrypt session data server-side. Redis with encryption. For TLS: SSL Labs A+ rating. TLS 1.3 mandatory. HSTS preload list. Certificate Transparency logs for monitoring. For all: security headers: X-Content-Type-Options: nosniff, X-Frame-Options: DENY, X-XSS-Protection: 0 (modern browsers deprecate). Feature-Policy/Permissions-Policy. Report-To and NEL for security reporting.</THINK>",
                f"<THINK>Analyzing web security for {problem}: {technique} with {hint}. Defense in depth: multiple controls, one fails another catches. For SQLi: parameterized queries (always), WAF (secondary), least privilege DB user (third). Input validation: allowlist (accept known good) vs blocklist (reject known bad). Allowlist is safer. For XSS: reflected (in URL), stored (in DB), DOM-based (client-side). Each requires different prevention. CSP with nonce: script-src 'nonce-{random}' . Inline scripts only if they have nonce attribute. Violation reports sent to report-uri. For CSP: strict CSP recommended over allowlist (allowlist easily bypassed). For OAuth: client_secret for confidential clients confidential_clients. PKCE for public clients. Token endpoint authentication. For TLS: Qualys SSL Labs test. HSTS: max-age=31536000; includeSubDomains; preload. For session management: risk-based: additional auth for sensitive actions. Concurrent session control. Remember-me tokens are separate, long-lived, revocable. For all: security testing: SAST (Static Analysis), DAST (Dynamic Analysis), SCA (Software Composition Analysis), penetration testing, bug bounty program. Use dependency scanning for known vulnerabilities in libraries.</THINK>",
                f"<THINK>Deep web security implementation for {problem}: {technique}. {hint}. WAF: ModSecurity with OWASP CRS. Custom rules for application-specific patterns. For SQLi: use parameterized queries/ORM. WAF rule: SecRule ARGS '@detectSQLi' 'block,msg:SQL Injection' . For CSRF: Django has CSRF middleware. Flask-WTF. Express: csurf (now deprecated), double-submit cookie. For OAuth: libraries: passport.js, Spring Security OAuth, Authlib (Python). For CSP: helmet (Node), django-csp, secure (Python). CSP report-uri / csp-report. For session: express-session with connect-redis. Django: SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SECURE, SESSION_COOKIE_SAMESITE. For HTTPS: certbot (Let's Encrypt), cert-manager (K8s). HSTS: response header. For testing: OWASP ZAP, Burp Suite, nikto, sqlmap. For CI/CD: integrate SAST (Semgrep, SonarQube), SCA (Snyk, Dependabot). For all: follow secure coding guidelines (OWASP ASVS). Security reqs per feature. Threat modeling in design phase.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Web security: {problem}. Design: {technique}. {hint}. Controls implemented: input validation, output encoding, CSP, CSRF protection, secure cookies, TLS. OWASP Top 10 risks addressed. Security headers set. Scanner results clean. Ready for deployment.</EXEC>",
                f"<EXEC>Web app security: {problem}. Approach: {technique}. {hint}. SQLi prevented with parameterized queries. XSS blocked with CSP + encoding. CSRF protected. Auth flow secure. Session management hardened. HTTPS configured to A+.</EXEC>",
                f"<EXEC>Secure web dev: {problem}. Method: {technique}. {hint}. Defense in depth applied. OWASP ASVS Level 2 compliant. Automated security tests in CI. Regular dependency scanning. Pen test scheduled. Security posture strong.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "security")

MALWARE_TOPICS = [
    ("design a static analysis pipeline for PE file classification", "extract features: imports, sections, entropy, strings; ML classifier for malicious/benign", "PE parsing: headers, sections, imports, exports; entropy detects packing; suspicious imports (WriteProcessMemory, CreateRemoteThread)"),
    ("implement dynamic analysis in a sandbox for malware behavior detection", "run in isolated VM; hook system calls; log file/registry/network activity; classify behavior", "Cuckoo Sandbox / CAPE: API monitoring, process tree, dropped files, network PCAP; YARA rules for detection"),
    ("design a memory forensics tool to detect rootkits", "analyze RAM dump: process list, loaded modules, kernel callbacks, hidden processes", "Volatility: pslist vs psscan (hidden processes); modules vs modscan; malfind for injected code; kernel timers, callbacks"),
    ("implement ransomware detection based on file system activity", "monitor file operations: rapid encrypt, rename, delete patterns; entropy increase in files", "honeypot files: monitor access patterns; file extension changes; mass file rename events; entropy spike detection"),
    ("design a method to extract C2 server indicators from malware samples", "static: extract strings, decode config; dynamic: monitor network connections, DNS queries", "strings for URLs, IPs, domains; XOR/decode config blobs; DNS tunneling detection; JA3 fingerprinting for TLS C2"),
    ("implement PE packer detection and unpacking", "entropy analysis, section name anomalies, import table characteristics", "packed: high entropy, single section, suspicious section names; unpack: run to OEP via debugger, dump process memory"),
]

def _malware_gen():
    while True:
        for problem, technique, hint in MALWARE_TOPICS:
            inp = pick(
                f"Malware analysis: {problem}. Design the analysis approach.",
                f"Malware: {problem}. Static/dynamic/hybrid analysis methodology.",
                f"Given: {problem}. Identify malicious indicators.",
                f"Malware detection: {problem}. Build detection logic.",
            )
            plan = pick(
                f"<PLAN>Malware analysis: {problem}. {technique}: {hint}. Plan: (1) Sample acquisition/handling. (2) Static analysis: hashes, strings, PE structure, imports. (3) Dynamic analysis: sandbox execution. (4) Memory analysis. (5) Network analysis. (6) Indicators extraction. (7) Classification.</PLAN>",
                f"<PLAN>Analysis for {problem}: {technique}. {hint}. Steps: (1) Isolate sample. (2) Compute hashes. (3) Static analysis. (4) Dynamic analysis. (5) Memory forensics. (6) Report generation.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Detection methodology. (2) Feature extraction. (3) Analysis pipeline. (4) Alerting. (5) Continuous improvement.</PLAN>",
            )
            think = pick(
                f"<THINK>Analyzing malware for {problem}: {technique}. {hint}. Malware analysis approaches: (1) Static: examine without executing. PE structure, section names (.text, .rdata, UPX0), imports (kernel32!VirtualAlloc, ntdll!NtCreateThreadEx). High entropy suggests packing. Strings: C2 URLs, registry keys, mutex names. (2) Dynamic: execute in sandbox. API monitoring: CreateFile, RegSetValue, InternetOpenUrl. Process tree: parent-child relationships. Registry: persistence mechanisms (Run keys, services). Network: HTTP POST, DNS queries, IRC. (3) Memory: RAM dump. Volatility plugins: pslist (list processes via EPROCESS), psscan (scan for hidden), malfind (detect injected code), dlllist (loaded DLLs). Detecting rootkits: DKOM (Direct Kernel Object Manipulation) hides processes; compare pslist with psscan. Kernel callbacks: PsSetCreateProcessNotifyRoutine. SSDT hooks: check syscall table integrity. For ransomware: rapid file operations, extension changes, ransom notes. Detection: monitor FileCreate, FileWrite, FileRename. Entropy measurement: AES encrypted data has high entropy (approx 8 bits/byte). Honeypot files: create decoy files, monitor any access (normal user won't access). For C2 extraction: static: XOR, Base64, custom encoding. Dynamic: run and capture network traffic. JA3: TLS handshake fingerprint (ClientHello parameters). Distinct C2 frameworks have distinct JA3 signatures. For PE packing: UPX, Themida, VMProtect. Detect via entropy, section count/names. Unpacking: generic (run to OEP via hardware breakpoint) or specific (dedicated unpacker). For all: use VM snapshots for isolation. Disable network or simulate. Use INetSim for fake network services. Report: TTPs (MITRE ATT&CK framework), IOCs (hashes, IPs, domains, registry keys).</THINK>",
                f"<THINK>Analyzing malware detection for {problem}: {technique} with {hint}. Classification features: static (entropy, imports, sections, strings, compile timestamp) and dynamic (API calls, file ops, registry, network). ML: Random Forest, XGBoost for static. RNN/Transformer for behavioral sequences. Challenges: adversarial evasion (polymorphic code, packers), concept drift (new malware families). YARA rules: pattern matching on file content. rule Ransomware: $encrypt_ext = /\.(encrypted|crypt|locked)$/; condition: any of them. For memory forensics: volatility plugins. malfind: detects VADs with PAGE_EXECUTE_READWRITE protection (likely shellcode). hollowfind: detects process hollowing (legitimate process with malicious image loaded). For all: update signatures and models continuously. Share intelligence via MISP. Automate analysis pipeline with Cuckoo/CAPE, MISP, TheHive.</THINK>",
                f"<THINK>Deep malware analysis implementation for {problem}: {technique}. {hint}. PE parsing: pefile library. Structures: IMAGE_DOS_HEADER, IMAGE_NT_HEADERS, IMAGE_SECTION_HEADER. Imports: IMAGE_IMPORT_DESCRIPTOR. Sections: .text (code), .rdata (read-only), .data (writable). Entropy: shannon or chi-square. Packed: entropy > 7.0. YARA: compiled with yara-python. Dynamic: Drakvuf or CAPE. Syscall logs. Memory: volatility3 framework. volatility -f memory.dump windows.psscan. For malware dev: for writing analysis tools, use Python, lief library for PE/ELF. For C2 extraction: unxor, base64 decode, custom decoding functions. For all: contained environment (VM with snapshot revert). No internet access (simulate with INetSim). Store analysis results in structured format (JSON, MISP).</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Malware analysis: {problem}. Method: {technique}. {hint}. Static analysis complete (hashes, strings, imports, entropy). Dynamic analysis (sandbox logs). Memory forensics (Volatility plugins). Network indicators extracted. Classification: malicious with X% confidence. Report with MITRE ATT&CK TTPs and IOCs.</EXEC>",
                f"<EXEC>Malware detection: {problem}. Approach: {technique}. {hint}. Analysis pipeline built. YARA rules written. ML model trained. Features: static+dynamic. Detection rate high. False positives low. Automated analysis in sandbox. Results in MISP.</EXEC>",
                f"<EXEC>Malware: {problem}. Design: {technique}. {hint}. Static/dynamic/memory analysis complete. IOCs extracted: hashes, C2 domains, registry keys. MITRE ATT&CK mapping. Analysis report generated. Defenses updated.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "security")

AUTH_TOPICS = [
    ("design a multi-factor authentication system", "something you know (password) + something you have (TOTP/HW token) + something you are (biometric)", "TOTP: time-based one-time password (RFC 6238), 30-second window, shared secret; backup codes for recovery"),
    ("implement a JWT-based stateless authentication for APIs", "JWT: header.payload.signature; RS256 or HS256; short expiry, refresh token rotation", "access token: 15 min; refresh token: 7 days; refresh rotation invalidates old refresh; JWT secret/key management"),
    ("design a role-based access control (RBAC) system", "users -> roles -> permissions; role hierarchy; permission inheritance", "define roles: admin, editor, viewer. Each role has permissions (read, write, delete). Users assigned roles. Principle of least privilege."),
    ("implement a passwordless authentication flow with magic links", "send email with one-time link containing token; token expires after use or time limit", "token: CSPRNG 32+ bytes, stored hashed in DB, single-use, 15-min expiry. Verify, create session, invalidate token"),
    ("design an API key management system with rotation and revocation", "generate API key with prefix (identifies key) + secret; hash store; rate limiting per key", "key format: sk_live_xxxx (32+ chars). Hash with SHA-256. Revocation list. Grace period for key rotation. Scopes per key"),
    ("implement OAuth 2.0 scopes and consent for fine-grained authorization", "scopes: read:posts, write:posts, delete:posts; user consents; resource server validates", "scopes are space-separated strings. Client requests scopes. User consents. Authorization server issues token with granted scopes. Resource server checks scopes."),
]

def _auth_gen():
    while True:
        for problem, technique, hint in AUTH_TOPICS:
            inp = pick(
                f"Authentication/authorization: {problem}. Design the system.",
                f"Auth: {problem}. Implement securely with industry standards.",
                f"Given: {problem}. Handle secrets, tokens, and access control.",
                f"Identity and access: {problem}. Design for security and usability.",
            )
            plan = pick(
                f"<PLAN>Auth design: {problem}. {technique}: {hint}. Plan: (1) Requirements: security, usability, compliance. (2) Protocol selection. (3) Credential storage. (4) Token management. (5) Authorization model. (6) Implementation. (7) Security review.</PLAN>",
                f"<PLAN>Auth system for {problem}: {technique}. {hint}. Steps: (1) Threat model. (2) Protocol. (3) Key management. (4) Implementation. (5) Testing. (6) Monitoring.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Identity model. (2) Authentication factors. (3) Authorization model. (4) Token lifecycle. (5) Recovery. (6) Audit.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing auth for {problem}: {technique}. {hint}. MFA: password + TOTP (authenticator app) + recovery codes. TOTP: time-based, shared secret between server and authenticator. Hotp: counter-based (used when no accurate clock). For backup: one-time use recovery codes (10 codes, each used once). For JWT: stateless auth. Header: {{'alg':'RS256','typ':'JWT'}}. Payload: {{'sub':'user_id','exp':timestamp,'scope':'read'}}. Signature: RSASSA-PKCS1-v1_5 with SHA-256. RS256 (asymmetric): public key in verification service, private key in issuing service. HS256 (symmetric): shared secret, simpler but both sides must trust each other. Short-lived tokens minimize damage from leak. Refresh token rotation: issuing new refresh with each use, invalidating old. Thwarts refresh token theft. For RBAC: role hierarchy: admin inherits all permissions of editor and viewer. Permission: granular action on resource (e.g., article:create). Deny overrides allow for explicit denial. For magic links: no password to remember. Token unique, unpredictable, single-use, time-limited. Store hash(token) in DB. When user clicks, look up hash, verify not expired/used, create session, delete token. Rate-limit email sending per user. For API keys: prefix identifies key (e.g., sk_live_), rest is secret. Hash with slow hash (bcrypt/argon2) or fast (SHA-256) plus pepper. Store prefix + hash. On use: look up by prefix, verify hash. Rate limit per key. Scopes limit what key can do. For OAuth scopes: granular permissions the client requests. User approves on consent screen. Resource server validates scope before allowing access. For all: rate-limit auth endpoints (login, register, password reset) to prevent brute force. Account lockout after N failures. Log all auth events (success/failure) for audit. Use secure comparison for token verification.</THINK>",
                f"<THINK>Analyzing auth for {problem}: {technique} with {hint}. Password storage: never store plaintext. Argon2id recommended. Bcrypt acceptable (cost >= 10). Scrypt also good. PBKDF2 with high iteration count is fallback. Pepper: secret key added to password before hashing (different from salt). For MFA: phishing-resistant methods: FIDO2/WebAuthn (public key cryptography). Passkeys: platform authenticator (biometric) synced via cloud. Hardware security keys (YubiKey). For JWT: common vulnerabilities: alg=none attack (if server accepts none); algorithm confusion: RS256 public key used as HS256 secret (server must validate algorithm). Use jku/x5u carefully (SSRF risk). For RBAC: ABAC (Attribute-Based Access Control) for more dynamic policies (user attributes, resource attributes, environment). ReBAC (Relationship-Based) for social graphs. For magic links: clickjacking prevention (X-Frame-Options). Rate limiting: prevent enumeration. For API keys: allow multiple keys per user (different apps/scopes). Key rotation: generate new, switch apps, revoke old. Monitor key usage for anomalies. For OAuth: RFC 6749. Authorization Server issues tokens. Resource Server validates. Client types: confidential (server-side, can keep secret), public (SPA, mobile, no secret). For all: session management: HttpOnly, Secure, SameSite=Strict. Regenerate session ID on login. Idle timeout (30 min). Absolute timeout (24h). Audit trail: who did what when.</THINK>",
                f"<THINK>Deep auth implementation for {problem}: {technique}. {hint}. MFA: pyotp for TOTP. totp = pyotp.TOTP(secret). totp.verify(code). QR code provisioning. Recovery codes: generate 10 codes, bcrypt hash each, store. On use: mark used. JWT: PyJWT or jose. jwt.encode(payload, private_key, algorithm='RS256'). jwt.decode(token, public_key, algorithms=['RS256']). Validation: exp, nbf, iss, aud. For RBAC: SQLAlchemy models: User, Role, Permission. RolePermissions association. UserRoles association. Alembic migrations. For magic links: secrets.token_urlsafe(32) for token. Store hash. Celery for async email. Rate limiter: Django REST Framework throttling or flask-limiter. For API keys: generate: prefix + secrets.token_urlsafe(48). Hash with hashlib.sha256(pepper + raw_key). Verify: lookup by prefix, SHA-256 verify. For OAuth: Authlib or Django OAuth Toolkit. AS configuration: clients, grants, tokens. RS validates via introspection endpoint or JWKS. For all: use HTTPS everywhere. HSTS. Security headers. Input validation. Output encoding. Prepared statements. CSP. CSRF tokens. Regular security audits.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Auth system: {problem}. Design: {technique}. {hint}. MFA/JWT/RBAC/passwordless implemented. Credentials stored securely (argon2). Tokens short-lived with rotation. RBAC enforces least privilege. Rate limiting active. Auth logs audited. Security review passed.</EXEC>",
                f"<EXEC>Authentication: {problem}. Approach: {technique}. {hint}. Multi-factor enabled. JWT with RS256. Session management secure. RBAC policies defined. API keys with rotation. OAuth scopes granular. All endpoints protected.</EXEC>",
                f"<EXEC>Auth/authorization: {problem}. Method: {technique}. {hint}. Secure credential storage. Token lifecycle managed. Access control enforced. Passwordless option available. Audit logging active. Compliance requirements met.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "security")

SECCODE_TOPICS = [
    ("design a secure code review checklist for OWASP Top 10", "check for injection (SQL, OS, LDAP), XSS, broken auth, sensitive data exposure, XXE, access control, misconfig, insecure deserialization, vulnerable components, insufficient logging", "automated SAST scanning + manual review focused on auth, access control, business logic flaws"),
    ("implement input validation and output encoding framework", "whitelist validation at entry; context-aware encoding at exit; sanitize vs validate", "allowlist: regex or type check. Reject invalid early. Encode for HTML/JS/CSS/URL/XML context. DOMPurify for rich text"),
    ("design a secure software development lifecycle (SSDLC)", "threat modeling in design; SAST in development; DAST in testing; SCA for dependencies; pen test before release", "shift left: security early. Threat modeling: STRIDE per feature. Security requirements in user stories. Bug bounty post-release"),
    ("implement secure deserialization protection", "avoid native deserialization of untrusted data; use safe formats (JSON); integrity checks (HMAC, signatures)", "PHP unserialize, Java readObject, Python pickle are dangerous. Validate HMAC before deserializing. Use allowlist of classes for Java"),
    ("design error handling that does not leak sensitive information", "generic error messages to user; detailed errors logged server-side; no stack traces in production", "production DEBUG=False. Custom error pages. Log with context (user, IP, action). Monitor error rates for anomalies"),
    ("implement proper logging and monitoring for security events", "log auth events, access control failures, input validation rejections, suspicious patterns; SIEM aggregation", "log format: timestamp, level, source, event, user, details. Centralize (ELK/Splunk). Alert on thresholds. Regular review"),
]

def _securecode_gen():
    while True:
        for problem, technique, hint in SECCODE_TOPICS:
            inp = pick(
                f"Secure coding: {problem}. Design the secure development practices.",
                f"Security: {problem}. Implement secure coding standards.",
                f"Given: {problem}. Prevent vulnerabilities through coding practices.",
                f"Software security: {problem}. Integrate into development lifecycle.",
            )
            plan = pick(
                f"<PLAN>Secure coding: {problem}. {technique}: {hint}. Plan: (1) Security requirements. (2) Coding standards. (3) Tooling. (4) Review process. (5) Testing. (6) Monitoring. (7) Training.</PLAN>",
                f"<PLAN>Security practices for {problem}: {technique}. {hint}. Steps: (1) Guidelines. (2) Implementation. (3) Automated checks. (4) Manual review. (5) Testing. (6) Incident response.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Standards. (2) Tooling. (3) Process. (4) Training. (5) Metrics. (6) Continuous improvement.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing secure coding for {problem}: {technique}. {hint}. Security is everyone's responsibility. SSDLC integrates security throughout. Phase 1 (Design): threat modeling (STRIDE, DREAD, PASTA). Phase 2 (Dev): SAST in IDE (Semgrep, SonarLint). Phase 3 (Build): SCA (Snyk, Dependabot), SAST (CodeQL, SonarQube). Phase 4 (Test): DAST (OWASP ZAP), manual pen test. Phase 5 (Deploy): security headers, secrets scanning, infrastructure security. Phase 6 (Operate): monitoring, incident response, bug bounty. Code review checklist: (1) Input validation? (2) Output encoding? (3) Auth checked? (4) Access control? (5) CSRF token? (6) SQL parameterized? (7) Sensitive data encrypted? (8) Error handling safe? (9) Logging appropriate? (10) Dependencies current? For input validation: allowlist (specific characters/format) vs blocklist (known bad). Allowlist preferred. Validate: type, length, format, range, allowed values. For encoding: context matters. HTML: &amp; &lt; &gt; &quot; &#39; . HTML attribute: encode for attr. JavaScript: \\xHH. URL: percent-encode. CSS: encode. For deserialization: Java: validate object class before deserializing (SerialKiller, allowlist). Python: use JSON instead of pickle. For errors: custom error pages (404, 500). Log full exception details server-side. Monitor: auth failures, input validation rejections, access control violations, suspicious IPs. For logging: structured logging (JSON). Required fields: @timestamp, severity, source_ip, user_id, action, result. SIEM: Elasticsearch, Logstash, Kibana (ELK) or Splunk. Alerts: more than N auth failures from same IP. For secure config: disable directory listing, remove server version headers, secure default configs, secrets in vault/env vars.</THINK>",
                f"<THINK>Analyzing secure coding for {problem}: {technique} with {hint}. Common weaknesses: CWE Top 25. CWE-79 (XSS), CWE-89 (SQLi), CWE-787 (buffer overflow), CWE-20 (input validation), CWE-862 (missing auth), CWE-22 (path traversal), CWE-352 (CSRF), CWE-502 (deserialization), CWE-434 (file upload). Prevention: (1) Input: validate, reject invalid. (2) Output: encode for context. (3) Auth: centralize, use standard frameworks. (4) Access control: deny by default, explicit allow. (5) Cryptography: use libraries, not custom. (6) Error handling: safe defaults. (7) Logging: enough for incident response. (8) Dependencies: keep updated, scan for vulns. For all: secure by design, secure by default, secure in deployment. Training: OWASP Top 10, secure coding workshop, annual refresher. Culture: security champions in each team. Metrics: time to fix, vulnerability recurrence, scan coverage, training completion.</THINK>",
                f"<THINK>Deep secure coding implementation for {problem}: {technique}. {hint}. Tooling: pre-commit hooks: secrets detection (truffleHog, git-secrets), SAST (Semgrep). CI: SonarQube quality gate, Snyk/Dependabot for dependencies, Container scanning (Trivy, Clair). IaC scanning (tfsec, checkov). DAST: OWASP ZAP in staging. IDE: SonarLint, ErrorProne (Java), Pyre (Python). Frameworks: Django/Flask have built-in CSRF, XSS protection. Spring Security: comprehensive. React: automatically encodes JSX. For JS: DOMPurify. For SQL: SQLAlchemy/Prisma parameterize. For serialization: JSON with schema validation (JSON Schema, Pydantic). For logging: structured logging library (structlog, python-json-logger). For incident response: playbooks for each scenario (SQLi detected, account takeover, DDoS). Post-mortem: blameless, systemic improvements. For all: automate as much as possible. Security debt tracked alongside technical debt. Regular executive reporting: risk posture, metrics, incidents.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Secure coding: {problem}. Design: {technique}. {hint}. SSDLC implemented: threat modeling, SAST/DAST/SCA in CI, manual review, pen test. Input validated, output encoded. Deserialization safe. Error handling secure. Logging active. Training completed.</EXEC>",
                f"<EXEC>Security practices: {problem}. Approach: {technique}. {hint}. Secure coding standards adopted. Automated tooling integrated. Review checklist followed. Vulnerabilities found and fixed. Metrics tracked. Security posture improved.</EXEC>",
                f"<EXEC>Software security: {problem}. Method: {technique}. {hint}. Secure lifecycle deployed. Code review checklist covers OWASP Top 10. SAST/SCA in CI. Incident response ready. Training ongoing. Security culture growing.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(3,6), "security")

PRIVACY_TOPICS = [
    ("design a data anonymization pipeline for PII", "remove direct identifiers, generalize quasi-identifiers (k-anonymity), add noise (differential privacy)", "k-anonymity: each record indistinguishable from k-1 others. l-diversity: sensitive values diverse within group. t-closeness: distribution close to global"),
    ("implement differential privacy for aggregate statistics", "add calibrated noise (Laplace/Exponential mechanism) to query results; epsilon budget tracks privacy loss", "Laplace mechanism: M(x) = f(x) + Lap(0, sensitivity/epsilon). sensitivity = max||f(x) - f(y)||_1 for neighboring datasets. Composition: sequential, parallel theorems"),
    ("design a GDPR consent management platform", "record consent per purpose; allow withdraw; right to access, rectification, erasure, portability", "consent: unambiguous, specific, informed, freely given. Withdraw as easy as give. Data subject access request response within 30 days"),
    ("implement data encryption at rest and in transit with proper key management", "at rest: AES-256-GCM for files, TDE for databases; in transit: TLS 1.3; key management: HSM/KMS", "encryption: server-side (SSE-S3, SSE-KMS) or client-side. Key rotation: annually or on compromise. KMS: AWS KMS, HashiCorp Vault"),
    ("design a privacy-preserving data sharing protocol with secure multi-party computation", "MPC: multiple parties compute function on private inputs without revealing individual inputs", "garbled circuits (Yao) for 2PC; secret sharing (Shamir) for MPC; SPDZ protocol for malicious security; use cases: joint analytics without sharing raw data"),
    ("implement data retention and deletion policies", "classify data (retention period per class); automated deletion after retention; secure deletion (overwrite/degauss)", "retention schedule: logs 90 days, user data 7 years after account deletion, analytics 24 months. Secure delete: overwrite 7 times, SSD: secure erase command, physical: shred/degauss"),
]

def _privacy_gen():
    while True:
        for problem, technique, hint in PRIVACY_TOPICS:
            inp = pick(
                f"Privacy engineering: {problem}. Design the privacy controls.",
                f"Data privacy: {problem}. Implement with regulatory compliance.",
                f"Given: {problem}. Protect personal data while enabling utility.",
                f"Privacy: {problem}. Anonymization, encryption, access controls.",
            )
            plan = pick(
                f"<PLAN>Privacy design: {problem}. {technique}: {hint}. Plan: (1) Data inventory and classification. (2) Privacy requirements. (3) Control selection. (4) Implementation. (5) Testing. (6) Audit and compliance review.</PLAN>",
                f"<PLAN>Privacy for {problem}: {technique}. {hint}. Steps: (1) Identify personal data. (2) Risk assessment. (3) Choose anonymization/encryption. (4) Implement. (5) Document. (6) Monitor.</PLAN>",
                f"<PLAN>Design {problem}: Use {technique}. {hint}. Plan: (1) Data flow mapping. (2) Privacy controls. (3) Consent management. (4) Enforcement. (5) Data subject rights. (6) Breach response.</PLAN>",
            )
            think = pick(
                f"<THINK>Designing privacy for {problem}: {technique}. {hint}. Privacy by design: proactive, not reactive. Data minimization: collect only necessary. Purpose limitation: use only for stated purpose. Storage limitation: delete when no longer needed. For anonymization: k-anonymity: group by quasi-identifiers, suppress/top-code to ensure each group has k records. l-diversity: within each group, sensitive values have l distinct values or entropy above threshold. t-closeness: distribution of sensitive values within group close to global distribution. For differential privacy: epsilon parameter: lower = more privacy, more noise. Typical epsilon: 1-10 for single release. Sequential composition: total epsilon = sum of epsilons. Parallel: max epsilon. Laplace: for numeric. Exponential: for non-numeric. Gaussian: for numeric (with relaxed DP, (epsilon, delta)-DP). For GDPR: legal basis (consent, legitimate interest, contract, legal obligation). Data Protection Impact Assessment (DPIA) for high-risk processing. Data Protection Officer (DPO) appointment. Breach notification: 72 hours to supervisory authority. For encryption: at rest: AES-256-GCM or AES-256-CBC with HMAC. Key hierarchy: master key (HSM/KMS), data encryption keys (wrapped by master), per-file keys (optional). In transit: TLS 1.3 with strong ciphers. Certificate management: Let's Encrypt, cert-manager. For MPC: garbled circuits: encrypt truth tables, evaluate one gate at a time. Secret sharing: split secret into shares, reconstruct with threshold. SPDZ: preprocessing + online phase. For data retention: classify: PII, financial, logs, analytics. Retention periods: legal requirements (tax: 7 years), business need (customer data: account duration + 90 days). Deletion: soft delete (mark deleted, purge after retention) then secure delete. Backup retention: encrypted, matching source retention. For all: privacy impact assessment. Privacy policy transparency. User rights: access, rectify, erase, port, object, restrict. Automated workflows for SAR (Subject Access Request). Regular privacy audits.</THINK>",
                f"<THINK>Analyzing privacy for {problem}: {technique} with {hint}. Privacy vs utility trade-off: more anonymization reduces data utility. Differential privacy provides formal privacy guarantee but adds noise. k-anonymity provides intuitive protection but may not protect against attribute disclosure. For DP: local DP (randomize at client) vs central DP (trusted curator adds noise). Local DP stronger privacy but more noise. For GDPR: extra-territorial scope (applies to any org processing EU residents' data). Fines up to 4% of global revenue. For encryption: key management is the hardest part. HSM provides hardware security. KMS provides software key management with access control and audit. AWS KMS, Azure Key Vault, GCP Cloud KMS. For MPC: expensive (communication rounds, computation). For two-party, garbled circuits practical. For multi-party, threshold secret sharing with SPDZ. For data retention: automate with lifecycle policies (S3 lifecycle, object storage retention). Legal holds: prevent deletion of data relevant to litigation. For all: privacy is not just compliance. It builds trust. Transparency: tell users what data you collect, why, how long, and their rights. Provide easy-to-use privacy controls. Privacy-enhancing technologies: PETs. Privacy by design: consider privacy at every stage of product development.</THINK>",
                f"<THINK>Deep privacy implementation for {problem}: {technique}. {hint}. Anonymization: ARX tool or custom Python. Generalization: age groups (18-25, 26-35, ...). Suppression: remove unique records. k-anonymity = 5 typically. l-diversity = 3. Differential privacy: Google's differential privacy library. Laplace: numpy.random.laplace(0, sensitivity/epsilon). For GDPR consent platform: store consent records (user_id, purpose, timestamp, consent_given). Enable withdraw endpoint. SAR: search all systems for user data, compile report within 30 days. Right to erasure: delete or anonymize. For encryption: cryptography.fernet for symmetric encryption (AES-128-CBC + HMAC-SHA256). For S3: AWS KMS managed keys. Database: TDE or column-level encryption. For MPC: MP-SPDZ library. Garbled circuits: Obliv-C, libOTe. For data deletion: overwrite with random data before deletion. S3: versioning + lifecycle. Database: DELETE + VACUUM (PostgreSQL). For all: DPIAs via CNIL template. Records of processing activities (ROPA). Data protection by design and default. Privacy training for all employees. Incident response: data breach notification plan, communication templates, forensics process.</THINK>",
            )
            exec_ = pick(
                f"<EXEC>Privacy: {problem}. Design: {technique}. {hint}. Anonymization applied (k-anonymity, l-diversity). DP with epsilon budget. GDPR consent platform operational. Encryption at rest and in transit. Data retention/deletion policies active. DPIA completed.</EXEC>",
                f"<EXEC>Privacy engineering: {problem}. Approach: {technique}. {hint}. Data inventory complete. Privacy controls implemented. User rights automated. Encryption configured. Secure deletion scheduled. Audit log maintained. Compliance verified.</EXEC>",
                f"<EXEC>Data privacy: {problem}. Method: {technique}. {hint}. PII protected, anonymized. DP guarantees formal. Consent management active. Encryption standards met. Retention policies enforced. Privacy impact assessed. Readily auditable.</EXEC>",
            )
            yield (inp, plan, think, exec_, random.randint(4,7), "security")

def chunk_10_gen():
    gens = [_crypto_gen(), _netsec_gen(), _websec_gen(), _malware_gen(), _auth_gen(),
            _securecode_gen(), _privacy_gen()]
    while True:
        for g in gens:
            yield next(g)

# ============================================================
# CHUNK 11: Game Development & Graphics
# ============================================================

GAME_PHYSICS_TOPICS = [
    ("Rigid body dynamics with collision detection", "SAT + impulse resolution", "Use separating axis theorem for convex polygons; apply normal impulse with friction"),
    ("Particle system with forces and constraints", "Verlet integration + distance constraints", "Each particle: position, previous position. Constrain pairs with relaxation"),
    ("Raycasting for visibility and AI sensing", "Bresenham / DDA ray marching", "Trace ray through grid cells; report first intersection"),
    ("Game networking with client-side prediction", "Input prediction + server reconciliation", "Predict state locally; reconcile when server state arrives"),
    ("Fluid simulation for water in 2D", "Smoothed Particle Hydrodynamics (SPH)", "Particles with density, pressure, viscosity forces"),
    ("Procedural terrain generation", "Perlin/Simplex noise layering", "Multiple octaves of noise: amplitude and frequency scaling"),
    ("Character animation blending", "Linear blend skinning + blend trees", "Bone matrices interpolated via quaternion slerp; vertex weights"),
    ("Spatial partitioning for broad-phase collision", "Dynamic AABB tree / sweep-and-prune", "Sort axis intervals; use BVH for dynamic objects"),
]

RENDERING_TOPICS = [
    ("Forward vs deferred rendering pipeline", "Deferred shading with G-buffer", "G-buffer: position, normal, albedo, metallic, roughness. Light accum in screen space"),
    ("Shadow mapping with PCF", "Depth map from light + percentage-closer filtering", "Sample depth map 4-16 times; average comparison results for soft shadow"),
    ("Screen-space ambient occlusion (SSAO)", "Hemisphere sampling in view-space", "Sample kernel oriented by normal; compare depth buffer samples"),
    ("Physically-based rendering (PBR)", "Cook-Torrance BRDF with energy conservation", "Diffuse: Lambert. Specular: GGX normal distribution, Smith geometry, Fresnel-Schlick"),
    ("Level of detail (LOD) system", "Discrete LOD with mesh simplification", "Quadric edge collapse decimation; distance-based LOD selection"),
    ("Image-based lighting (IBL)", "Irradiance map + pre-filtered environment map", "Lambertian diffuse from cubemap; specular from mipmap split-sum approximation"),
    ("Batched rendering for many objects", "GPU instancing with uniform buffer", "Draw instances with per-instance model matrix in vertex buffer"),
    ("Post-processing effects pipeline", "Multi-pass full-screen quads", "Bloom: extract bright, blur (gaussian separable), combine. Tone mapping: ACES filmic"),
]

GAME_AI_TOPICS = [
    ("Pathfinding with dynamic obstacles", "A* with hierarchical pathfinding", "A* on nav mesh; re-plan on obstacle change. HPA*: cluster coarse graph + local refinement"),
    ("Behavior trees for NPC decision-making", "Fallback + sequence + action/decorator nodes", "Selector (?) chooses first succeeding child; sequence (->) requires all succeed"),
    ("Finite state machines for character states", "State pattern with transitions and actions", "States: idle, walk, run, attack, die. Transitions on conditions with entry/exit actions"),
    ("Utility AI for tactical decisions", "Utility scoring with curves and dynamic factors", "Each action scored as curve(distance) * weight; pick highest or weighted random"),
    ("Steering behaviors for movement", "Seek, flee, arrive, pursue, evade, wander", "Seek: desired = target - pos; steer = desired - velocity. Pursue: predict target future"),
    ("Goal-oriented action planning (GOAP)", "Strip-like planner; goals -> actions -> plan", "Actions with preconditions and effects; A* in state space for plan"),
    ("Monte Carlo tree search for strategy games", "Select -> expand -> simulate -> backpropagate", "UCT: exploitation (win rate) + exploration (sqrt(ln(N)/n))"),
    ("Perception system with visual/audio cues", "Sensory stimulus with falloff and modifiers", "Visual: dot(viewDir, toTarget) > FOV, raycast, distance falloff. Audio: attenuation curve"),
]

AUDIO_TOPICS = [
    ("3D audio spatialization with HRTF", "Head-related transfer function convolution", "Convolve audio with HRTF for each ear based on azimuth/elevation angle"),
    ("Procedural audio generation", "Granular synthesis / additive synthesis", "Overlap grains of audio (windowed); FM synthesis: carrier = sin(carrierFreq + mod * sin(modFreq * t))"),
    ("Dynamic music system", "Layered stems with cross-fade transitions", "Separate stem tracks per instrument; cross-fade based on intensity parameter"),
    ("Audio compression for games", "Perceptual coding (Vorbis/Opus) + ADPCM", "Vorbis: psychoacoustic masking; Opus: SILK + CELT hybrid. ADPCM: 4:1 lossless compression"),
    ("Real-time audio effects (reverb/echo)", "Schroeder reverb: comb + all-pass filters", "Series of comb filters (delay 30-50ms, feedback 0.5-0.8) + all-pass for echo density"),
    ("Audio streaming and memory management", "Streaming buffer ring with seek-ahead loading", "Ring buffer: read position, write position. Preload 2-3 seconds. Async decode in thread"),
    ("DSP for audio processing", "Biquad filters for EQ / FFT for spectrum", "Biquad: 2-pole, 2-zero IIR. Direct form I. FFT: windowed (Hann) overlap-add for STFT"),
]

GAME_DESIGN_TOPICS = [
    ("Object pooling for game objects", "Fixed-size pool with active/inactive list", "Dictionary of pools. Activate: get inactive obj, reset state. Deactivate: return to pool"),
    ("Event-driven architecture for game systems", "Observer pattern with prioritized handlers", "Event bus: register handler(type, priority). Publish: iterate sorted handlers; cancelable"),
    ("Command pattern for input handling", "Bindable actions via command objects", "Each key/button maps to Command. Execute/undo stack. Rebindable at runtime"),
    ("Entity component system (ECS)", "Component arrays + system iteration", "Components: plain data structs. Systems: iterate over entities with specific component mask"),
    ("State management for game UI", "MVC / MVVM pattern for HUD and menus", "Model (state) -> View (render) -> Controller/ViewModel (input -> state mutation)"),
    ("Save/load system with serialization", "Binary format with versioning and checksum", "Magic number, version, checksum (CRC32), data (protobuf/JSON + compression). Atomic write"),
    ("Achievement and progression system", "Triggers, rules, and progression trees", "Rule engine: condition -> reward. Atomic triggers; track in player profile"),
    ("Localization system for games", "String table with ICU pluralization", "CSV -> binary lookup. ICU MessageFormat for plurals/gender. Fallback: en -> key"),
]

ANIMATION_TOPICS = [
    ("Skeletal animation with skinning", "Hierarchical bone transforms + linear blend skinning", "Bind pose inverse * bone world = skinning matrix; blend: vertex * skinning * weight"),
    ("Inverse kinematics (FABRIK)", "Forward and backward reaching IK", "Iterative: forward pass (end effector -> root, reach target distance), backward (root -> end effector)"),
    ("Blend tree for smooth transitions", "1D/2D blend space with directional blending", "Parameters (speed, direction) -> triangle/interpolation weights -> blend pose clip"),
    ("Motion matching for natural locomotion", "Feature database + KNN search", "Extract features (trajectory, foot contact). Search for best matching clip. In-place blend"),
    ("Procedural animation for ragdolls", "Physics-driven bone simulation with constraints", "Active ragdoll: target angles from animation -> PD controller -> physics torque"),
    ("Facial animation with blend shapes", "Morph targets interpolated by weights", "Delta per vertex per expression. Linear blend. Phonemes for lip sync with audio"),
    ("Animation compression techniques", "Keyframe reduction + quantization + curve fitting", "Reduce keyframes (tolerance). Quantize quaternions (48 bits). Compress float curves (speculative)"),
    ("Animation layering and masking", "Override/additive layers with bone mask", "Base -> upper body (override) -> look IK (additive). Weighted accumulate per bone"),
]

OPT_GRAPHICS_TOPICS = [
    ("GPU frustum culling with compute shader", "Compute shader: load instance bounds -> AABB test -> compact draw indirect args", "Thread group: 64 instances. Frustum test each. Atomic counter for visible count. Fill indirect draw args buffer"),
    ("Occlusion culling with depth buffer", "Hardware occlusion queries / hierarchical Z-buffer", "HZB: build depth pyramid. Test bounding box against HZB at appropriate mip. Hi-Z: mask, reject, or accept"),
    ("Texture compression and streaming", "BCn compression + mipmap streaming", "BC1: DXT1 (RGB, 4:1). BC3: DXT5 (RGBA, 4:1). BC5: RG (normal maps). BC6H/BC7: HDR/quality. Mipmap: priority-based streaming"),
    ("Compute shaders for particle systems", "Compute: update particle (pos, vel, life) -> indirect draw", "Buffers: position (RWStructuredBuffer), particle data. Thread per particle. Append active particles to draw args"),
    ("Temporal anti-aliasing (TAA)", "Sub-pixel jitter + history accumulation + rejection", "Jitter projection matrix each frame. Sample history with motion vectors. Reject (clamp/discard) on disocclusion"),
    ("Variable rate shading (VRS)", "Tier 2 hardware; shading rate per 16x16 tile", "Based on luminance variance, motion, or importance. Coarse shading: 2x2 pixel Shading Rate per 4x4 MSAA"),
    ("GPU-driven rendering pipeline", "Visibility buffer / mesh shader pipeline", "Mesh shaders replace vertex + geometry. Amplification shader: thread groups create task payload. Combined cull + LOD"),
    ("async compute for graphics + post-processing", "Async compute queue for non-graphics workloads", "Graphics queue: main render. Compute queue: post-process (bloom, DOF), particle physics. Avoid sync points"),
]

def chunk_11_gen():
    cats = [GAME_PHYSICS_TOPICS, RENDERING_TOPICS, GAME_AI_TOPICS, AUDIO_TOPICS,
            GAME_DESIGN_TOPICS, ANIMATION_TOPICS, OPT_GRAPHICS_TOPICS]
    while True:
        for topics in cats:
            for problem, tech, hint in topics:
                inp = pick(
                    f"Game dev: {problem}. Implement the system.",
                    f"Implement {problem} for a game engine.",
                    f"Design: {problem} with focus on {tech}.",
                    f"Build {problem} in a real-time game context.",
                    f"Game systems: {problem}. Code the solution.",
                    f"How would you implement {problem} for games?",
                )
                plan = pick(
                    f"<PLAN>Game: {problem}. Approach: {tech}. {hint}. Plan: (1) Setup data structures. (2) Implement core algorithm. (3) Integration. (4) Performance tuning and edge case handling.</PLAN>",
                    f"<PLAN>{problem}: Using {tech}. {hint}. Steps: (1) Requirements. (2) Data structures. (3) Algorithm implementation. (4) Testing and profiling. (5) Production-ready.</PLAN>",
                    f"<PLAN>System design: {problem}. {tech}. {hint}. Plan: (1) Design. (2) Implementation. (3) Test correctness. (4) Profile and optimize. (5) Ship.</PLAN>",
                    f"<PLAN>Game implementation: {problem}. Method: {tech}. {hint}. Phases: (1) Research. (2) Prototype. (3) Optimize. (4) Polish. (5) Documentation.</PLAN>",
                )
                think = pick(
                    f"<THINK>Game dev analysis for {problem}: {tech}. {hint}.",
                    f"<THINK>Deep dive into {problem} in game context: {tech}. {hint}.",
                    f"<THINK>Architecture for {problem}: {tech}. {hint}.",
                )
                exec_ = pick(
                    f"<EXEC>Game: {problem}. Implementation complete using {tech}. {hint}. Tested and validated.</EXEC>",
                    f"<EXEC>Game system built: {problem}. Approach: {tech}. Performance verified. Edge cases handled.</EXEC>",
                    f"<EXEC>Implementation: {problem}. {tech} applied. {hint}. Ready for integration.</EXEC>",
                )
                yield (inp, plan, think, exec_, random.randint(3,6), "game_dev")

# ============================================================
# CHUNK 12: DevOps & Cloud Infrastructure
# ============================================================

CICD_TOPICS = [
    ("CI pipeline with multi-stage builds", "Docker multi-stage + caching strategy", "Stage 1: build deps. Stage 2: app build. Stage 3: runtime (distroless). Layer caching for faster rebuilds"),
    ("GitHub Actions workflow optimization", "Matrix builds + dependency caching + concurrency", "Matrix: os, node/python version. Cache: actions/cache with hash of lock file. Concurrency: cancel-in-progress"),
    ("Artifact management and versioning", "Semantic versioning with auto-release pipeline", "git describe -> major.minor.patch. Build metadata: commit SHA. Publish to artifact registry"),
    ("Deployment strategies (blue-green, canary)", "Blue-green: DNS swap. Canary: traffic splitting with metrics", "Blue-green: duplicate env, switch load balancer. Canary: 5% -> 25% -> 100% with error rate monitoring"),
    ("Automated testing in CI pipeline", "Unit + integration + e2e + static analysis", "Fast: unit tests. Medium: integration (depends on DB). Slow: e2e (Selenium/Cypress). Lint + SAST + type checking"),
    ("Release management and changelog automation", "Conventional commits + auto-changelog", "feat -> minor, fix -> patch, BREAKING -> major. Changelog: grouped by type, auto-generated"),
    ("CI/CD for mobile apps", "Code signing + test flight + app store deploy", "iOS: xcodebuild + codesign + xcrun altool. Android: gradle assembleRelease + apksigner + bundletool"),
]

CONTAINER_TOPICS = [
    ("Container image optimization", "Minimal base + multi-stage + distroless", "Alpine (5MB) or distroless base. Combine RUN commands. Remove package manager cache. Use .dockerignore"),
    ("Kubernetes pod lifecycle management", "Init containers + probes + termination grace period", "Init: wait-for-db, setup config. Liveness: HTTP/grpc health check. Readiness: traffic ready. PreStop: graceful drain"),
    ("Helm chart best practices", "Values hierarchy + hooks + dependency management", "global -> environment -> service overrides. Hooks: pre/post install, upgrade, delete. Chart dependencies with conditions"),
    ("Service mesh (Istio/Linkerd)", "Sidecar proxy + mTLS + traffic policies", "Envoy sidecar auto-injected. mTLS: mutual authentication. VirtualService + DestinationRule for traffic routing"),
    ("Container security scanning", "Image scanning (Trivy) + admission control", "Trivy: scan for CVEs in OS packages + language deps. Admission: OPA/Gatekeeper policies; reject non-compliant images"),
    ("Horizontal pod autoscaling", "HPA with custom/external metrics + VPA", "HPA: target CPU/memory utilization or custom metric (QPS). VPA: recommend/automatic resource requests/limits"),
    ("StatefulSet for stateful applications", "Headless service + stable network identity + PVC template", "Ordinal index: pod-0, pod-1. Stable DNS: pod-0.service.namespace.svc.cluster.local. PersistentVolumeClaim per pod"),
]

MONITORING_TOPICS = [
    ("Observability: metrics, logs, traces", "Three pillars with correlation", "Metrics (Prometheus): counters, histograms, gauges. Logs (Loki/ELK): structured JSON. Traces (Jaeger/Tempo): OpenTelemetry spans with trace_id in logs"),
    ("Prometheus monitoring setup", "Pull model + service discovery + alerting rules", "Scrape targets via k8s SD. Recording rules for aggregations. Alerting rules: severity (warning/critical), annotations"),
    ("Distributed tracing with OpenTelemetry", "Instrument + propagate context + visualize", "TraceId propagation via W3C trace-context header. Span attributes for key metadata. Sampling: probabilistic (head) or rate-limited"),
    ("Log aggregation and analysis", "Structured logging + centralized ingestion + querying", "Log format: JSON with timestamp, level, service, trace_id. Buffer and ship (Fluentd/Vector). Query: Loki LogQL"),
    ("SLO-driven alerting", "Service level indicators (SLI) + objectives (SLO) + burn rate", "SLI: latency p99 < 200ms, error rate < 0.1%. SLO: 99.9%. Burn rate: 1x (alert if > 5% budget in 1h)"),
    ("Synthetic monitoring and uptime checks", "Playwright scripts run on schedule", "Critical user journeys: login, search, checkout. Run every 5 min from multiple regions. Alert on failure"),
    ("Dashboard design best practices", "USE method: Utilization, Saturation, Errors", "Utilization: CPU, memory, disk. Saturation: queue depth, run queue. Errors: rate, server errors. RED: Rate, Errors, Duration"),
]

IAC_TOPICS = [
    ("Terraform state management", "Remote state + locking + workspaces", "Backend: S3 + DynamoDB (locking). Workspaces: dev, staging, prod. State file: sensitive, never commit. Terraform Cloud for collaboration"),
    ("AWS infrastructure as code", "VPC + subnets + security groups + IAM + ECS/EKS", "VPC: CIDR, public/private subnets, NAT gateway, internet gateway. IAM: least privilege policy. ECS: Fargate task definitions"),
    ("Pulumi for infra in general-purpose languages", "Infrastructure as program (TypeScript/Python/Go)", "Describe infra with code, not DSL. State: Pulumi Cloud or self-managed. Automation API: embed in apps"),
    ("Ansible configuration management", "Playbooks + roles + idempotent modules", "Playbook: hosts, tasks, handlers. Roles: organize tasks/vars/templates. Modules: idempotent (check mode). Jinja2 templates"),
    ("Crossplane for platform engineering", "Control plane with custom resource definitions + compositions", "Platform CRDs: PostgreSQLInstance, Bucket. Compositions: XR -> managed resources. Claims: namespaced, consumed by app teams"),
    ("Nix/NixOS for reproducible dev environments", "Declarative system config + nix flake", "Flake: inputs (nixpkgs, self), outputs (packages, devShells). devShell: exact tooling versions. Reproducible build"),
    ("Secrets management (Vault/AWS Secrets Manager)", "Dynamic secrets + rotation + auditing", "Vault: KV engine, database dynamic creds, PKI for certs. AWS SM: automatic rotation with Lambda. KMS for encryption"),
]

CLOUD_DESIGN_TOPICS = [
    ("Microservices architecture patterns", "API gateway + service discovery + circuit breaker", "Gateway: Kong/AWS API GW. Discovery: k8s DNS. Circuit breaker: resilience4j, hysteresis: close -> open (failure threshold) -> half-open (retry)"),
    ("Serverless application design", "Lambda + API GW + DynamoDB + SQS", "Lambda: stateless, cold start (~100ms-1s). API GW: REST/HTTP/WebSocket. DynamoDB: single-digit ms latency. SQS: async decoupling. Step Functions for workflow"),
    ("Event-driven architecture with message queues", "Event bus + schema registry + dead-letter", "Schema: Avro/Protobuf with registry (Confluent). DLQ: poison pill handling. Retry: exponential backoff with max attempts"),
    ("Disaster recovery and business continuity", "RTO/RPO strategies: backup, pilot light, warm standby, multi-site", "Backup: RPO 24h, RTO 48h. Pilot: RPO 1h, RTO 2h. Warm: RPO 5min, RTO 30min. Active-active: RPO 0, RTO 0"),
    ("Cloud cost optimization", "Compute: reserved/spot instances. Storage: lifecycle policies", "Spot: interruptible workloads (batch, ML). Reserved: steady-state (1-3 year). S3: Standard -> Infrequent -> Glacier with lifecycle. RDS: reserved instances"),
    ("Multi-cloud strategy", "Abstraction layer + portability + failover", "Terraform/Pulumi for multi-cloud. Kubernetes for workload portability. Cloud-agnostic storage (S3-compatible). Active-active with global load balancer"),
]

SRE_TOPICS = [
    ("Incident response and on-call management", "Severity levels + escalation + postmortem", "SEV1: critical (all hands). SEV2: major. SEV3: minor. Escalation: primary -> secondary -> engineering manager. Postmortem: blameless, action items"),
    ("Chaos engineering principles", "Steady state hypothesis + blast radius + automated experiments", "Hypothesis: system remains available. Blast radius: small (1 pod, 1 AZ). Tools: Chaos Mesh, Litmus. GameDays: scheduled"),
    ("Capacity planning and scaling", "Trend analysis + load testing + autoscaling", "Gather metrics (CPU, memory, QPS) over 3-6 months. Model growth. Load test (k6, locust). Configure HPA/Cluster Autoscaler"),
    ("SLI/SLO/SLA definitions and management", "Service level indicators (latency, error rate, throughput) + budget tracking", "SLI: measured metric. SLO: target (99.9% of requests < 200ms). SLA: contractual (99.95%, with penalty). Error budget: 1 - SLO"),
    ("Runbooks and operational playbooks", "Step-by-step procedures for common incidents", "Format: symptoms -> diagnosis steps -> mitigation -> verification. Keep in wiki or code (GitOps). Test during GameDays"),
    ("Release engineering and change management", "Feature flags + gradual rollout + automatic rollback", "Feature flags: LaunchDarkly/Flagsmith. Gradual: percentage-based rollout (1%->10%->100%). Rollback: automatic on error rate increase > 5%"),
]

INFRA_SECURITY_TOPICS = [
    ("Cloud security: IAM and network policies", "Least privilege IAM + VPC security groups + NACLs", "IAM: policy conditions (source IP, MFA, time). SGs: allow specific ports, stateful. NACLs: stateless, subnet-level"),
    ("Container security: runtime + image + host", "Image scanning + runtime (Falco) + seccomp/apparmor", "Falco: abnormal syscalls (shell in container). Seccomp: profile (whitelist syscalls). AppArmor: file/network access controls"),
    ("Hardening Kubernetes clusters", "Pod security standards + network policies + RBAC", "Pod Security: restricted profile (runAsNonRoot, readOnlyRootFS). NetworkPolicy: default deny, allow specific. RBAC: least privilege"),
    ("Zero trust architecture in cloud", "Micro-segmentation + mTLS + continuous verification", "ZTA: never trust, always verify. Network: zero-trust tiers (GCP BeyondCorp). mTLS everywhere. Continuous auth (decisions, not just tokens)"),
    ("Cloud compliance: SOC2, HIPAA, PCI-DSS", "Audit logs + encryption + access control + compliance reporting", "SOC2: controls over security, availability, processing integrity. HIPAA: BAA, PHI encryption. PCI: cardholder data environment segmentation"),
    ("Security information and event management (SIEM)", "CloudTrail + GuardDuty + Security Hub", "CloudTrail: API activity logging. GuardDuty: threat detection (ML + threat intel). Security Hub: consolidated findings across AWS"),
]

def chunk_12_gen():
    cats = [CICD_TOPICS, CONTAINER_TOPICS, MONITORING_TOPICS, IAC_TOPICS,
            CLOUD_DESIGN_TOPICS, SRE_TOPICS, INFRA_SECURITY_TOPICS]
    while True:
        for topics in cats:
            for problem, tech, hint in topics:
                inp = pick(
                    f"DevOps: {problem}. Design and implement.",
                    f"Implement {problem} in cloud infrastructure.",
                    f"How to set up {problem} for production?",
                    f"Design a solution for {problem}.",
                    f"Build {problem} with industry best practices.",
                    f"Implement and deploy {problem} at scale.",
                )
                plan = pick(
                    f"<PLAN>DevOps: {problem}. Approach: {tech}. {hint}. Plan: (1) Requirements gathering. (2) Tool selection. (3) Implementation. (4) Testing. (5) Deployment and monitoring.</PLAN>",
                    f"<PLAN>{problem}: Using {tech}. {hint}. Steps: (1) Setup. (2) Configure. (3) Test. (4) Validate security. (5) Document runbook.</PLAN>",
                    f"<PLAN>Infrastructure design: {problem}. {tech}. {hint}. Plan: (1) Architecture. (2) Implementation. (3) Observability. (4) DR/HA. (5) Cost optimization.</PLAN>",
                    f"<PLAN>System: {problem}. Method: {tech}. {hint}. Phases: (1) Foundation. (2) Integration. (3) Automation. (4) Monitoring. (5) Iterate.</PLAN>",
                )
                think = pick(
                    f"<THINK>DevOps analysis for {problem}: {tech}. {hint}.",
                    f"<THINK>Infrastructure deep dive: {problem}. {tech}. {hint}.",
                    f"<THINK>Architecture for {problem}: {tech}. {hint}.",
                )
                exec_ = pick(
                    f"<EXEC>DevOps: {problem}. Implementation complete. {tech}. {hint}. Verified and deployed.</EXEC>",
                    f"<EXEC>Infrastructure: {problem}. Solution: {tech}. Testing passed. Monitoring configured.</EXEC>",
                    f"<EXEC>Implementation: {problem}. {tech} applied. {hint}. Production-ready.</EXEC>",
                )
                yield (inp, plan, think, exec_, random.randint(3,6), "devops")

# ============================================================
# CHUNK 13: Database Design & Optimization
# ============================================================

SQL_OPT_TOPICS = [
    ("Query performance analysis with EXPLAIN", "EXPLAIN ANALYZE + query plan interpretation", "Seq scan vs index scan vs bitmap scan. Cost: startup + total. Actual: loops x actual time. Look for: sequential scans on large tables, nested loops"),
    ("SQL join optimization strategies", "Hash join vs merge join vs nested loop", "Hash: one table fits in memory (hash table). Merge: both sorted, index scan. NL: small driving table with index on inner. Join order matters"),
    ("Subquery optimization with CTEs and window functions", "Materialized CTE vs inline subquery vs lateral join", "CTEs: materialized (PostgreSQL 12+: optimization fence). Window: PERCENT_RANK, NTILE to avoid self-joins. LATERAL: correlated subquery optimized"),
    ("Anti-patterns in SQL queries", "N+1 queries, implicit type conversion, excessive JOINs", "N+1: eager loading (batch). IMPLICIT: 'col = string' (no index). Excessive: denormalize or materialized view. ORDER BY on non-indexed column"),
    ("Full-text search in SQL databases", "GIN indexes with tsvector/tsquery", "to_tsvector('english', text) @@ plainto_tsquery('english', words). GIN index: fast. Ranking: ts_rank. Highlight: ts_headline"),
    ("Partition pruning and query planning", "Partition key + constraint exclusion + partition-wise join", "List/range/hash partitioning. Pruning WHERE on partition key. Partition-wise join: same partition key, equi-join. Sub-partitioning"),
    ("Recursive CTEs for hierarchical data", "WITH RECURSIVE + anchor + UNION + recursive step", "Tree traversal. Cycle detection: array[edge] to detect loops. Graph: depth-first (LATERAL) vs breadth-first (ORDER BY depth)"),
]

INDEXING_TOPICS = [
    ("B-tree index internals and optimization", "Balanced tree: page splits, fill factor, height", "Fill factor: 90 (high writes) vs 100 (read-only). Height: log_fanout(n). Fanout: ~200-400 (8KB page, 28 byte tuple). Leaf pages contain ctid"),
    ("GIN and GiST index types", "GIN: array/jsonb/full-text. GiST: geometry/range/fuzzy", "GIN: inverted index, fast for contains/overlaps. GiST: balanced tree, KNN search, nearest neighbor. BRIN: block range index for correlated ordering"),
    ("Partial and covering indexes", "Partial: WHERE condition. Covering: INCLUDE columns", "Partial: WHERE status = 'active' (size reduction). Covering: INCLUDE (payload) to avoid heap access (index-only scan). Columns from WHERE + SELECT only"),
    ("Index maintenance: bloat, fragmentation, reindex", "Autovacuum + pg_repack + CONCURRENTLY", "Bloat: dead tuples. Autovacuum threshold: scale_factor * reltuples + min_threshold. pg_repack: online rebuild. REINDEX CONCURRENTLY: new index, drop old"),
    ("Expression indexes for computed columns", "Index on function result (LOWER, date_trunc, JSON field)", "CREATE INDEX ON table (LOWER(name)). date_trunc('hour', created_at). JSONB: idx on (data->>'key'). Maintained automatically"),
    ("Multi-column index column order", "Equality first, then range, then sort", "Most selective column first (highest cardinality). Works for prefix queries. Index skip scan (PostgreSQL 15+): reverse scan for distinct prefix values"),
    ("Indexing for ORDER BY and GROUP BY", "Index on sort columns, matching sort direction", "ORDER BY col ASC: index ASC. ORDER BY col DESC: index DESC. GROUP BY: index on group columns (sorted group scan). DISTINCT: index with distinct prefix"),
]

NOSQL_TOPICS = [
    ("Document DB schema design (MongoDB)", "Embedding vs referencing + schema patterns", "Embed: one-to-one, one-to-few (arrays under 100). Reference: one-to-many, many-to-many. Patterns: attribute, bucket, computed, outbox, document versioning"),
    ("Cassandra data modeling", "Query-first design: table per query pattern + partition key", "Primary key: partition key (high cardinality) + clustering columns (ordering). Table per query: denormalized. Materialized views for alternate access (limited support)"),
    ("Redis data structures and use cases", "Strings: cache. Lists: queue. Sorted sets: leaderboard. Hashes: objects. Sets: tags. Streams: event log", "Strings: SET/GET, 512MB max. Lists: LPUSH/RPUSH, cap with LTRIM. Sorted sets: ZADD/ZRANGE, scores doubles. Streams: XADD/XREAD, consumer groups"),
    ("Time-series database (InfluxDB/TimescaleDB)", "Hypertable with time dimension + continuous aggregates", "Hypertable: partitioned by time. Chunk size: 7 days or 1GB. Continuous aggregates: materialized, auto-refresh. Retention: drop_chunks older than N days"),
    ("Graph database (Neo4j / Dgraph)", "Labeled property graph + Cypher traversal", "Nodes: labels. Relationships: directed, type. Traversal: MATCH (a)-[:KNOWS]->(b). Graph DB vs JOINs: at scale, 1000x faster for deep traversal"),
    ("Elasticsearch indexing and search", "Inverted index + analysis + mapping + relevance", "Mapping: text (with analyzer), keyword, integer, geo_point. Index: shards (1-10GB per shard), replicas. Query: bool (must, should, filter, must_not). Score: BM25"),
    ("DynamoDB single-table design", "Entity + composite sort key + GSIs + access patterns", "Table: PK = partition, SK = sort. GSIs: alternate access patterns. Sparse indexes: GSIs with attribute present only for subset. Hot keys: partition key with high write volume -> shard"),
]

TRANSACTION_TOPICS = [
    ("ACID properties and implementation", "Atomicity: WAL. Consistency: constraints/triggers. Isolation: MVCC. Durability: fsync/wal", "WAL: write-ahead log (redo + undo). MVCC: tuple visibility (xmin, xmax). ISOLATION: read committed, repeatable read, serializable. Durability: synchronous_commit"),
    ("Isolation levels and anomalies", "Dirty read, non-repeatable read, phantom read, serialization anomaly", "Read uncommitted: dirty reads. Read committed: non-repeatable. Repeatable: phantom. Serializable: all, but high conflict rate (SSI in PostgreSQL). Snapshot isolation: write skew"),
    ("Optimistic vs pessimistic concurrency control", "Optimistic: version field + retry. Pessimistic: SELECT FOR UPDATE", "Optimistic: retry on version conflict (CAS). Pessimistic: lock row/page/table. Deadlock detection: timeout or WFG. MVCC: no read locks (PostgreSQL)"),
    ("Distributed transactions: 2PC and Saga", "2PC: coordinator + prepare/commit/abort. Saga: compensating actions", "2PC: blocking, coordinator SPOF. XA protocol. Saga: choreography (events) vs orchestration (state machine). Compensation: undo action, eventually consistent"),
    ("Concurrent write handling in SQL", "UPSERT (INSERT ... ON CONFLICT) + MERGE + advisory locks", "ON CONFLICT: DO NOTHING or DO UPDATE (excluded.*). MERGE: conditional insert/update/delete. Advisory locks: pg_advisory_xact_lock, session-scoped. SKIP LOCKED for queue"),
    ("Deadlock detection and resolution", "Wait-for graph + timeout + retry", "Deadlock_timeout (200ms in PostgreSQL). Check pg_locks. Error: 40P01. Retry logic: exponential backoff + jitter. Order locks consistently"),
]

DATA_MODELING_TOPICS = [
    ("Normalization forms (1NF-5NF)", "1NF: atomic columns. 2NF: no partial dependency. 3NF: no transitive dependency. BCNF: every determinant is a key", "3NF vs BCNF: BCNF eliminates all redundancy based on functional dependencies. 4NF: multi-valued dependencies. 5NF: join dependencies. Denormalization for performance"),
    ("Entity-relationship modeling", "Entities, relationships, attributes, cardinality, keys", "ERD: Chen, Crow's Foot, UML. Cardinality: 1:1, 1:M, M:N. Weak entity: dependent on strong entity, composite PK. Subtypes: supertype/subtype with discriminator"),
    ("Schema migration strategies", "Evolutionary + backward-compatible + zero-downtime", "Expand-Migrate-Contract: add nullable column -> backfill -> make NOT NULL -> drop old. Avoid: long-running locks. Use: pt-online-schema-change, gh-ost"),
    ("Data pipeline ETL/ELT design", "Extract -> load -> transform (dbt, Airflow)", "Extract: CDC (Debezium), batch export. Load: staging tables. Transform: dbt (SQL models), incremental models. Orchestration: Airflow DAGs. Quality: dbt tests"),
    ("Slowly changing dimensions (SCD)", "Type 0-6: retain, overwrite, new row, historical + current, mini-dimension, hybrid", "Type 2: surrogate key, effective date, expiry date, current flag. Type 3: original + current columns (limited history). Type 6: Type 2 + current attributes. Type 4: mini-dimension"),
    ("Data warehouse schema (star vs snowflake)", "Star: fact + dimension. Snowflake: normalized dimensions", "Fact: measures, foreign keys. Dimension: descriptive attributes. Snowflake: dim hierarchies (separate tables). Performance: star preferred (fewer joins). Bitmap indexes"),
]

DISTRIBUTED_DB_TOPICS = [
    ("Consistency models: strong, eventual, causal", "Strong: linearizability. Eventual: converge. Causal: happens-before preserved", "Strong: Raft/Paxos (consensus), 2PC. Eventual: Dynamo-style, vector clocks. Causal: version vectors, we need causal consistency. CAP: partition tolerance + consistency vs availability"),
    ("Distributed consensus: Raft and Paxos", "Leader election + log replication + safety", "Raft: leader (heartbeat), log entry (term + index), commit. Majority (2N+1). Paxos: prepare (ballot), promise, accept (value), accepted (learning). Multi-Paxos"),
    ("Sharding strategies and rebalancing", "Hash + range + consistent hashing + virtual nodes", "Hash: modulo (rebalancing expensive). Consistent hash: ring (minimal reshuffle). Range: ordered (hotspot risk). Virtual nodes: 128-256 per physical node"),
    ("Database replication (sync/async)", "Leader-follower, multi-leader, quorum read/write", "Sync: commit waits for replica ack (durability, latency). Async: faster, possible data loss. Multi-leader: conflict resolution (CRDT, LWW). Quorum: read + write > N"),
    ("Distributed SQL engines (CockroachDB, Spanner)", "TrueTime (Spanner) + HLC (Cockroach) + atomic clocks", "Spanner: TrueTime (GPS + atomic clocks), external consistency. Cockroach: hybrid logical clocks, serializable isolation. F1: Google-scale distributed SQL"),
    ("Conflict resolution in distributed databases", "CRDTs + last-write-wins + custom merge", "CRDT: G-Counter, OR-Set, LWW-Register. LWW: compare timestamps. Custom: application-specific merge function. Operational transformation for collaborative editing"),
]

QUERY_PLANNING_TOPICS = [
    ("Query plan analysis and optimization", "Cost estimation + plan node types + statistics", "Plan nodes: Seq Scan, Index Scan, Index Only Scan, Bitmap Scan, Sort, Hash, Agg. Stats: pg_stat_user_tables (n_mod_since_analyze). Analyze: update stats"),
    ("Join algorithms and when they apply", "Hash join (one side small), Merge join (sorted), Nested loop (few rows)", "Hash: one side fits work_mem. Merge: both sides sorted on join key (index). NL: probing with index. Hash vs Merge: hash for equi, merge for sorted+range"),
    ("Parallel query execution", "Parallel seq scan, parallel hash join, parallel agg", "Parallel workers: max_parallel_workers_per_gather. Gather node: merge from workers. Parallel agg: partial -> combine -> final. Repartition: for hash join"),
    ("Cost estimation and statistics", "pg_statistic: most common values (MCV), histograms, correlation", "MCV: most frequent values. Histogram: distribution bounds. Correlation: physical sort order (correlation ~1 = index scan better). extended statistics (expressions, MCVs)"),
    ("Materialized views: usage and maintenance", "Pre-computed + auto refresh + partial refresh", "CREATE MATERIALIZED VIEW. REFRESH MATERIALIZED VIEW CONCURRENTLY (requires unique index). Used for: expensive aggregations, dashboards. Trade-off: stale data"),
    ("Query tuning: finding and fixing slow queries", "pg_stat_statements + auto_explain + pgbadger", "pg_stat_statements: top by total time, mean time, calls. auto_explain: log plan for slow queries (threshold). pgbadger: log analysis. Index suggestions: pg_hint_plan"),
]

def chunk_13_gen():
    cats = [SQL_OPT_TOPICS, INDEXING_TOPICS, NOSQL_TOPICS, TRANSACTION_TOPICS,
            DATA_MODELING_TOPICS, DISTRIBUTED_DB_TOPICS, QUERY_PLANNING_TOPICS]
    while True:
        for topics in cats:
            for problem, tech, hint in topics:
                inp = pick(
                    f"Database: {problem}. Design/implement the solution.",
                    f"How to handle {problem} in database systems?",
                    f"Implement {problem} for production database.",
                    f"Design a database solution for {problem}.",
                    f"Database optimization: {problem}. Show implementation.",
                    f"Solve {problem} in database design context.",
                )
                plan = pick(
                    f"<PLAN>Database: {problem}. Approach: {tech}. {hint}. Plan: (1) Analyze. (2) Design. (3) Implement. (4) Test. (5) Optimize and validate.</PLAN>",
                    f"<PLAN>{problem}: Using {tech}. {hint}. Steps: (1) Understand requirements. (2) Model. (3) Implement. (4) Benchmark. (5) Deploy and monitor.</PLAN>",
                    f"<PLAN>DB design: {problem}. {tech}. {hint}. Plan: (1) Schema. (2) Query design. (3) Index selection. (4) Testing with realistic data. (5) Tuning.</PLAN>",
                    f"<PLAN>Implementation: {problem}. Method: {tech}. {hint}. Phases: (1) Research. (2) Prototype. (3) Optimize. (4) Review. (5) Productionize.</PLAN>",
                )
                think = pick(
                    f"<THINK>Database analysis for {problem}: {tech}. {hint}.",
                    f"<THINK>Deep dive into {problem}: {tech}. {hint}.",
                    f"<THINK>Database architecture for {problem}: {tech}. {hint}.",
                )
                exec_ = pick(
                    f"<EXEC>Database: {problem}. Implementation complete. {tech}. {hint}. Validated and optimized.</EXEC>",
                    f"<EXEC>DB solution: {problem}. Approach: {tech}. Performance verified. Edge cases handled.</EXEC>",
                    f"<EXEC>Implementation: {problem}. {tech} applied. {hint}. Production-ready and documented.</EXEC>",
                )
                yield (inp, plan, think, exec_, random.randint(3,6), "database")

# ============================================================
# CHUNK 14: Software Engineering & Best Practices
# ============================================================

DESIGN_PATTERNS_TOPICS = [
    ("Creational patterns: factory, builder, singleton", "Factory: create objects without specifying exact class. Builder: build complex objects step by step. Singleton: ensure one instance", "Factory: interface/abstract class. Builder: separate Construction director. Singleton: __new__ or module-level instance. Use cases: dependency injection (factory), configuration (singleton)"),
    ("Structural patterns: adapter, facade, proxy", "Adapter: convert interface. Facade: simplify subsystem. Proxy: control access", "Adapter: class (inheritance) vs object (composition). Facade: orchestrates complex subsystem. Proxy: virtual (lazy), remote (RPC), protection (auth). Decorator: add behavior"),
    ("Behavioral patterns: observer, strategy, command", "Observer: publisher-subscriber. Strategy: interchangeable algorithms. Command: encapsulate request", "Observer: Subject + Observer interface. Weak refs to avoid leak. Strategy: interface + concrete implementations. Command: execute/undo/replay. Template method: algorithm skeleton"),
    ("Dependency injection and IoC containers", "Constructor injection vs setter vs interface injection", "Constructor injection: required dependencies. Setter: optional. DI container: registry, resolve, lifecycle (transient, scoped, singleton). Python: injector, dependency-injector"),
    ("Hexagonal/Ports and Adapters architecture", "Core domain (ports) + adapters (infrastructure) + dependency inversion", "Core: use cases, entities. Ports: interfaces (Repository, Notifier). Adapters: PostgreSQL, Redis, SES. Adapter implements port. Core depends on ports (not adapters). Test: mock adapters"),
    ("Domain-driven design (DDD) tactical patterns", "Aggregate, value object, domain event, repository, factory, service", "Aggregate: consistency boundary (root entity). Value object: immutable, equality by value. Domain event: side effects (outbox pattern). Repository: collection-like persistence. Domain service: stateless operations"),
    ("CQRS and event sourcing", "Command (write) model + Query (read) model + event store", "Commands: state change (Task, Result). Queries: projections (denormalized). Event store: append-only, replay for state. Snapshots to avoid full replay. Separate DB per model"),
]

TESTING_TOPICS = [
    ("Unit testing strategies and best practices", "AAA pattern + mocks + edge cases + test naming", "Arrange-Act-Assert. Mock: unittest.mock, pytest-mock. Test one behavior. Naming: test_unitOfWork_stateUnderTest_expectedBehavior. Coverage: 80%+ line, focus on logic"),
    ("Integration testing with test containers", "Docker containers in tests + DB/service lifecycle", "Testcontainers: Postgres, Redis, S3. Module fixtures (scope=session). DB migration before tests. Cleanup after. Realistic: close to production, not identical"),
    ("End-to-end testing with Playwright/Cypress", "User flows + stable selectors + network mocking", "Page Object Model. data-testid attributes over CSS selectors. API mocking for edge cases. Visual regression: percy, snapshot. CI: parallel sharding. Retries on flaky"),
    ("Property-based testing (Hypothesis)", "Generate random inputs matching description", "hypothesis.strategies: integers, text, lists. composite strategies for domain objects. falsifying examples (minimal). shrink: find minimal failing example. Good for: AI/math/validation"),
    ("Test doubles: mock, stub, fake, spy, dummy", "Mock: verify interactions. Stub: canned answers. Fake: working implementation (in-memory DB). Spy: real + record. Dummy: passed but unused", "Mock: assert_called_with. Stub: return_value, side_effect. Fake: LightRepo implements RepoInterface. Spy: wraps original. Partial mock: mock.patch object for real system"),
    ("Mutation testing for test quality", "Mutate code (change operators) -> see if tests detect", "Mutators: arithmetic (<-> +/-, relation flip, bool negation). Coverage: mutation score = killed / total. pitest (Java), mutmut (Python). Threshold: 80%+ to ensure good tests"),
    ("Performance/load testing", "k6/Gatling: virtual users, ramp-up, thresholds", "Scenarios: peak load (2x expected), soak (24h at nominal), stress (breaking point). Metrics: p50/p95/p99 latency, error rate, throughput. Thresholds: p99 < 500ms, errors < 1%"),
]

CODE_REVIEW_TOPICS = [
    ("Review checklist and best practices", "Correctness, security, performance, readability, test coverage", "Check: edge cases, null safety, error handling, sensitive data, algorithm complexity. Review in small batches (<400 lines). 60-90 min sessions. Use checklists per language"),
    ("Giving and receiving constructive feedback", "Specific, objective, kind. 'I noticed X' vs 'You did Y wrong'", "Suggestion format: What (issue) + Why (impact) + How (suggestion). Nit: (minor) prefix. RFC process for large changes. Accept feedback: separate self from code"),
    ("Automated code review tools", "Static analysis (linter) + SAST + formatting + type checking", "CI: run linter + formatter + typecheck. SAST: Semgrep, CodeQL. Reviewdog: post comments. Pre-commit hooks. Incremental: diff lint in CI. Auto-fix with formatter"),
    ("Code review with security focus", "OWASP Top 10, input validation, auth, injection, secrets", "SQL injection: parameterized queries. XSS: escaping, CSP. CSRF: tokens. Auth: consistent (RBAC/ABAC). Secrets: detect (detect-secrets, truffleHog). Sensitive data in logs"),
    ("Reviewing large refactors", "Readability + no behavior change + test before/after", "Focus on structure, not details. Verify old->new mapping. Snapshot tests before refactor. Check for: dead code, renamed edge cases, missed coverage. Batch: small PRs if possible"),
    ("Architecture review process", "ADRs (Architecture Decision Records) + RFC + reviewers", "ADR: context, decision, consequences, status. RFC: template (problem, options, recommendation, timeline). Reviewers: architects, senior engineers. Alignment with tech strategy. Cost/effort estimate"),
]

VERSION_CONTROL_TOPICS = [
    ("Git branching strategies", "GitHub Flow vs GitFlow vs trunk-based", "GitHub Flow: feature branch -> PR -> main (deploy). GitFlow: develop, feature, release, hotfix branches. Trunk: short-lived branches, feature flags, continuous deploy. Monorepo: single branch with scoped packages"),
    ("Merge vs rebase: when and why", "Merge: preserve history (merge commit). Rebase: linear history (clean)", "Merge: public/shared branches. Rebase: private feature branches. Squash merge: feature -> one commit on main. Interactive rebase: squash, reword, reorder. DANGER: rebase published branch"),
    ("Git hooks and automation", "pre-commit: lint/format. commit-msg: conventional commits. pre-push: test", "pre-commit: .pre-commit-config.yaml. commit-msg: check format (type(scope): description). pre-push: run full test suite. post-checkout: setup env. post-merge: install new deps"),
    ("Monorepo tooling (Nx, Turborepo)", "Affected commands + dependency graph + caching", "Nx: affected:test (only changed). Dep graph: nx graph. Cache: local + remote (nx cloud). Task orchestration: parallel dependency order. Distribute tasks across machines"),
    ("Git bisect for finding bugs", "Binary search through git history", "git bisect start <bad> <good>. git bisect run <script> (returns 0 = good, 1 = bad, 125 = skip). Automate: specify a test script that checks for the bug. Scope: narrow to a few commits"),
    ("Semantic versioning and changelogs", "MAJOR.MINOR.PATCH + breaking/feature/fix", "MAJOR: incompatible API change. MINOR: new functionality (backward-compatible). PATCH: bug fixes. Pre-release: alpha, beta, rc. Changelog: Keep a Changelog format. Auto-generated from conventional commits"),
]

API_DESIGN_TOPICS = [
    ("RESTful API design principles", "Resource-oriented + HTTP verbs + status codes + HATEOAS", "Nouns not verbs. Verbs: GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE. Status: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401/403, 404, 409 Conflict, 500"),
    ("GraphQL schema design", "Type system + resolvers + N+1 problem + batching (DataLoader)", "Types: Query, Mutation, Subscription. Resolver: field-level function. DataLoader: batch + cache (per request). N+1: solve with DataLoader (loadMany). Federation: subgraph composition (Apollo)"),
    ("gRPC and protobuf design", "Service definition + message types + streaming + interceptor", "Service: rpc, client/server streaming. Message: proto3, field numbers (1-15: 1 byte). Interceptors: auth, logging, rate limit. Health: grpc-health-probe. Deadlines/timeout propagation"),
    ("API versioning strategies", "URI versioning (/v1) vs header (Accept: application/vnd.v1+json) vs query param", "URI: explicit, easy to route. Header: clean URLs. Query: simple. Best practice: v1 stable, v2 in development. Sunset: deprecation notice in header, 410 Gone. Support: N versions (v1, v2)"),
    ("API security: auth, rate limiting, validation", "JWT/OAuth2 + rate limit (token bucket) + input validation", "JWT: stateless auth, verify signature. OAuth2: authorization server (client -> auth code -> access token). Rate limit: per user (sliding window). Input: Pydantic/cerberus validation"),
    ("API documentation (OpenAPI/Swagger)", "OpenAPI 3.0 spec + auto-generated docs + client SDK", "Spec: paths, components (schemas, securitySchemes), tags. Tools: Swagger UI, ReDoc, Stoplight. Code generation: openapi-generator (client/server stubs). Validate: spectral linting"),
    ("WebSocket/SSE for real-time APIs", "WebSocket: bidirectional, persistent. SSE: server -> client, auto-reconnect", "WebSocket: ws:// protocol, frames (text/binary). Handshake: HTTP upgrade. Keepalive: ping/pong. SSE: EventSource API, text/event-stream format. Reconnect: Last-Event-ID. Fallback: long polling"),
]

DOCUMENTATION_TOPICS = [
    ("README and project documentation", "What, why, how, quick start, architecture, contributing", "Top: name, badge, description. Quick start: install, configure, run. Architecture: high-level diagram. Contributing: setup, coding guide, PR process. FAQ. License. Changelog. Code of conduct"),
    ("API docs with examples", "Exhaustive examples + request/response + error codes", "Example-first: cURL, Python, JavaScript. Show realistic payloads. Error responses: every error code with explanation. Rate limits: headers, limits, reset. Pagination: cursor vs offset"),
    ("Documentation as code", "Markdown + docs generator (MkDocs, Docusaurus) + CI verification", "Markdown with frontmatter. MkDocs: mkdocs.yml, mkdocs-material theme. Docusaurus: React-based. CI: spell check (aspell), link check (broken-link-checker), style guide (vale). Auto-deploy"),
    ("ADR documents for architecture decisions", "Template: context, decision, consequences, status", "ADR-001: Title. Status: proposed, accepted, deprecated, superseded. Context: why this decision. Decision: what we chose. Consequences: tradeoffs, follow-up. ADRs in repo (docs/adr/)"),
    ("Runbooks and operational documentation", "Symptom -> diagnosis -> fix -> verify", "Template: Title, Symptoms, Severity, Affected components, Diagnosis steps (with commands), Fix steps, Verification, Escalation. Keep as code (runbooks in repository). Review quarterly"),
    ("Technical writing principles", "Audience, clarity, consistency, structure, examples, visuals", "Audience: beginner, expert. Clarity: short sentences, active voice. Consistency: terminology, style guide (Google, Microsoft). Structure: headings, lists, tables. Examples > abstract. Visuals: diagrams, screenshots"),
]

PM_TOPICS = [
    ("Agile/Scrum methodology", "Sprints, ceremonies, roles, artifacts", "Ceremonies: sprint planning (2h/2wk), daily standup (15min), review (1h/wk), retro (1h/wk). Roles: PO (backlog), SM (process dev), dev team. Artifacts: user stories, backlog, sprint goal, burndown"),
    ("Estimating engineering effort", "Story points (Fibonacci), t-shirt sizes, planning poker", "Points: 1,2,3,5,8,13,21. Relative not absolute. Velocity: points per sprint. Planning poker: reveal together. T-shirt: XS, S, M, L, XL. Time: Ideal hours (discount overhead 0.5-0.7). Ranges: best/worst/most likely"),
    ("Issue tracking and project boards (Jira/GitHub Projects)", "Epics -> stories -> tasks + kanban board + prioritization", "Epic: large feature. Story: user value (As a/I want/So that). Tasks: technical breakdown. Board: columns (Backlog, To Do, In Progress, Review, Done). Priority: MoSCoW (Must, Should, Could, Won't)"),
    ("OKR and goal setting for engineering teams", "Objectives (qualitative) + Key Results (quantitative, measurable)", "Objective: aspirational. KR: measurable outcome (not output). Example: Objective: Improve deployment reliability. KRs: 99.9% uptime, deploy time < 10min, rollback < 2min. Quarterly review"),
    ("Risk management in software projects", "Identify, assess (likelihood x impact), mitigate, monitor", "Risk matrix: 5x5 grid (likelihood vs impact). Mitigation: reduce likelihood or impact, contingency plan, accept, avoid, transfer (insurance). Monitor: risk register, review monthly. Blocker: unblock ASAP"),
    ("Stakeholder communication", "Status reports, demos, async updates, escalation", "Format: weekly email (accomplished, planned, blockers, metrics). Demo: working software every sprint. Async: Slack updates, dashboards. Escalation: early and often (blameless). Technical debt: communicate trade-offs"),
]

def chunk_14_gen():
    cats = [DESIGN_PATTERNS_TOPICS, TESTING_TOPICS, CODE_REVIEW_TOPICS, VERSION_CONTROL_TOPICS,
            API_DESIGN_TOPICS, DOCUMENTATION_TOPICS, PM_TOPICS]
    while True:
        for topics in cats:
            for problem, tech, hint in topics:
                inp = pick(
                    f"Software engineering: {problem}. Explain and implement.",
                    f"Implement {problem} in a professional setting.",
                    f"How to apply {problem} in software projects?",
                    f"Design and implement {problem} with best practices.",
                    f"Engineering best practice: {problem}. Show details.",
                    f"Apply {problem} to real-world software development.",
                )
                plan = pick(
                    f"<PLAN>Software engineering: {problem}. Approach: {tech}. {hint}. Plan: (1) Understand context. (2) Design. (3) Implement. (4) Review. (5) Deploy and iterate.</PLAN>",
                    f"<PLAN>{problem}: Using {tech}. {hint}. Steps: (1) Research. (2) Prototype. (3) Refine. (4) Test. (5) Document and maintain.</PLAN>",
                    f"<PLAN>Engineering design: {problem}. {tech}. {hint}. Plan: (1) Requirements. (2) Architecture. (3) Implementation. (4) Quality assurance. (5) Operations.</PLAN>",
                    f"<PLAN>Implementation: {problem}. Method: {tech}. {hint}. Phases: (1) Analysis. (2) Design. (3) Implementation. (4) Testing. (5) Release.</PLAN>",
                )
                think = pick(
                    f"<THINK>Engineering analysis for {problem}: {tech}. {hint}.",
                    f"<THINK>Deep dive into {problem}: {tech}. {hint}.",
                    f"<THINK>Software architecture for {problem}: {tech}. {hint}.",
                )
                exec_ = pick(
                    f"<EXEC>Engineering: {problem}. Implementation complete. {tech}. {hint}. Reviewed and deployed.</EXEC>",
                    f"<EXEC>Solution: {problem}. Approach: {tech}. Tests pass. Documentation updated.</EXEC>",
                    f"<EXEC>Implementation: {problem}. {tech} applied. {hint}. Production-ready and maintainable.</EXEC>",
                )
                yield (inp, plan, think, exec_, random.randint(3,6), "software_engineering")

# ============================================================
# CHUNK 15: Advanced Mathematics & Physics
# ============================================================

LINEAR_ALGEBRA_TOPICS = [
    ("Matrix decomposition: LU, QR, SVD", "LU: Gaussian elimination (A = PLU). QR: Gram-Schmidt (A = QR). SVD: A = U Sigma V^T", "LU: forward/backward substitution O(n^3). QR: stable for least squares. SVD: eigenvalues of AA^T, PCA, pseudo-inverse. Use: scipy.linalg"),
    ("Eigenvalue computation (power iteration, QR algorithm)", "Power iteration: dominant eigenvector. QR algorithm: all eigenvalues", "Power: x_{k+1} = A x_k / ||A x_k||, converges to dominant eigenpair (Rayleigh quotient). QR: iterative, shift strategy (Wilkinson shift). ARPACK: sparse (scipy.sparse.linalg.eigs)"),
    ("Conjugate gradient for linear systems", "Iterative method for symmetric positive definite matrices", "x_{k+1} = x_k + alpha_k p_k. alpha: minimize residual (p_k^T r_k) / (p_k^T A p_k). beta: Fletcher-Reeves (r_{k+1}^T r_{k+1}) / (r_k^T r_k). Preconditioner: incomplete Cholesky. O(sqrt(kappa)) iterations"),
    ("Krylov subspace methods (GMRES, BiCGSTAB)", "Arnoldi iteration: orthogonal basis. GMRES: minimize residual in Krylov subspace", "GMRES: restart parameter m (memory O(m*n)). BiCGSTAB: stable for non-symmetric. FGMRES: flexible (different precond each step). PETSc: scalable parallel solvers"),
    ("Tensor operations and multilinear algebra", "Tensor contraction, CP/Tucker decomposition", "Tensor: n-dimensional array. Contraction: sum over indices. CP: rank-1 factors. Tucker: core + factor matrices. ALS (alternating least squares). Applications: ML (attention, embeddings)"),
    ("Matrix calculus and gradients", "Derivative w.r.t. matrix: vectorization, trace trick", "d(X^T A X)/dX = (A + A^T) X. d(log det X)/dX = X^{-T}. d(X^{-1})/dX = -X^{-1} dot dX dot X^{-1}. Chain rule. Jacobian: (m x n) matrix of partials. Hessian: (n x n) of second partials"),
]

CALCULUS_TOPICS = [
    ("Numerical integration (quadrature)", "Gaussian quadrature: nodes (roots of Legendre poly) + weights. Adaptive Simpson", "Gauss-Legendre: n points, degree 2n-1. Weights: w_i = 2 / ((1-x_i^2) [P'_n(x_i)]^2). Adaptive: refine where error large (Simpson rule). Romberg: Richardson extrapolation"),
    ("Multivariable calculus: gradient, divergence, curl", "Gradient: scalar -> vector. Div: vector -> scalar (outflow). Curl: vector -> vector (rotation)", "Grad: [df/dx, df/dy, df/dz]. Div: dP/dx + dQ/dy + dR/dz. Curl: (dR/dy - dQ/dz, dP/dz - dR/dx, dQ/dx - dP/dy). Laplacian: div(grad) = d^2f/dx^2 + ..."),
    ("Fourier analysis and FFT", "Fourier series: periodic -> frequencies. FFT: O(n log n) radix-2 Cooley-Tukey", "DFT: X_k = sum x_n * exp(-2pi i k n / N). FFT: divide into even/odd indices, butterfly. Convolution: FFT -> multiply -> IFFT. Applications: signal processing, spectral methods"),
    ("Complex analysis: integrals and residues", "Residue theorem: contour integral = 2pi i sum of residues inside", "Residue: coefficient of (z - z0)^{-1} in Laurent series. Cauchy integral formula: f^(n)(a) = n!/(2pi i) contour f(z)/(z-a)^{n+1}. Applications: improper real integrals, fluid dynamics"),
    ("Calculus of variations", "Functional derivative: Euler-Lagrange equation", "F[y] = integral L(x, y, y'). Euler-Lagrange: dL/dy - d/dx(dL/dy') = 0. Extremal: solution of E-L. Brachistochrone: minimize time. Isoperimetric constraints: Lagrange multiplier"),
    ("Stochastic calculus and Ito calculus", "Ito process: dX = mu dt + sigma dW. Ito's lemma", "Ito's lemma: df = (df/dt + mu df/dX + 1/2 sigma^2 d^2f/dX^2) dt + sigma df/dX dW. Brownian motion: dW ~ N(0, dt). Geometric Brownian motion: dS = mu S dt + sigma S dW. Black-Scholes"),
]

DE_TOPICS = [
    ("ODEs: RK4, adaptive step, stiff solvers", "RK4: k1,k2,k3,k4 slope evaluations. Adaptive: embedded (RK45, Dormand-Prince). Stiff: implicit (BDF, Radau, backward Euler)", "RK4: y_{n+1} = y_n + (h/6)(k1 + 2k2 + 2k3 + k4). Adaptive: tol-based step size. Stiff: A-stability. BDF: implicit multistep (order 1-6). scipy.integrate.solve_ivp"),
    ("PDEs: finite difference, finite element, FVM", "FD: grid-based derivatives. FEM: variational, basis functions. FVM: conservation, flux", "FD: forward/central/backward. CFL: stability condition (dt/dx < 1). FEM: weak form, Galerkin, element assembly. FVM: cell averages, Godunov flux. Parabolic: heat eq. Hyperbolic: wave eq"),
    ("Spectral methods for PDEs", "Global basis functions (Chebyshev, Fourier). Fast transform", "Chebyshev: collocation points (cos(pi k / N)). Spectral: exponential convergence for smooth solutions. Pseudospectral: nonlinear terms. Gibbs phenomenon at discontinuities. Filtering: spectral viscosity"),
    ("Monte Carlo methods for integrals", "MC integration: sample mean (O(1/sqrt(N))). Importance sampling: variance reduction", "MC: integral f = E[f(X)]. Var = (E[f^2] - E[f]^2)/N. Importance: sample from g proportional to f. Stratified: partition domain. MCMC: Metropolis-Hastings, Gibbs sampling. QMC: low-discrepancy (Sobol)"),
    ("Laplace and Fourier transform methods", "Laplace: solve ODEs with initial conditions. Fourier: PDEs, convolution", "Laplace: F(s) = integral_0^inf f(t) e^{-st} dt. Inverse via partial fractions. Fourier: F(w) = integral f(t) e^{-iwt} dt. Applications: heat eq (Fourier), control theory (Laplace). Z-transform: discrete"),
    ("Numerical stability and conditioning", "Condition number: ||A|| * ||A^{-1}||. Wilkinson: backward/forward error", "Ill-conditioned: small changes -> large output. Normal equations: kappa^2 (squared). QR: kappa. SVD: best conditioning. Machine epsilon: 2^{-53} (double). Catastrophic cancellation: avoid subtracting near-equal numbers"),
]

PROBABILITY_TOPICS = [
    ("Probability distributions and their properties", "Discrete: Binomial, Poisson, Geometric. Continuous: Normal, Beta, Gamma, Exponential, Cauchy", "Normal: mu, sigma^2, CLT (sum -> Normal). Beta: prior for Bernoulli (alpha, beta). Exponential: memoryless, lambda. MGF: E[e^{tX}] = moment generating function. Characteristic: phi(t) = E[e^{itX}]"),
    ("Bayesian inference and MCMC", "Posterior = likelihood * prior / evidence. MCMC: Metropolis-Hastings, NUTS", "MH: proposal q(x'|x), acceptance alpha = min(1, posterior(x')q(x|x')/(posterior(x)q(x'|x))). NUTS: no-U-turn, Hamiltonian MC, leapfrog steps. Convergence: Gelman-Rubin R_hat < 1.01. Effective sample size"),
    ("Information theory basics", "Entropy: H(X) = -sum p log p. KL divergence. Mutual information", "Entropy: uncertainty (bits for log2). Cross-entropy: H(p,q) = -sum p log q. KL: D_KL(p||q) = sum p log(p/q). Mutual: I(X;Y) = H(X) - H(X|Y) = D_KL(p(x,y) || p(x)p(y)). Max entropy: given constraints"),
    ("Statistical hypothesis testing", "Null + alternative. p-value: P(obs | H0 true). Type I/II error", "Test: t-test (mean), chi-square (independence), ANOVA (multiple groups), F-test (variance). p < 0.05 (significant). Multiple comparison: Bonferroni, FDR (Benjamini-Hochberg). Power: 1-beta (sample size)"),
    ("Graphical models: Bayesian networks, Markov random fields", "DAG (BN): directed, conditional independence. MRF: undirected, potential functions", "BN: P(X1..Xn) = prod P(Xi | parents). d-separation: block paths. Inference: variable elimination, belief propagation. MRF: P(X) = (1/Z) exp(sum potential(x)). Loopy BP. Applications: structured prediction"),
    ("Random processes: Markov chains, Poisson process", "MC: transition matrix P(X_{n+1} | X_n). Stationary distribution: pi = pi P. Poisson: arrivals, rate lambda", "MC: ergodic (irreducible + aperiodic). Detailed balance: pi_i P_ij = pi_j P_ji. Poisson process: inter-arrival ~ Exponential. Compound Poisson: random jumps. Renewal: general inter-arrival. Brownian: limit of RW"),
]

CLASSICAL_MECHANICS_TOPICS = [
    ("Lagrangian and Hamiltonian mechanics", "L = T - V. Euler-Lagrange: d/dt(dL/dq') - dL/dq = 0. H = sum p q' - L", "Hamilton's equations: dq/dt = dH/dp, dp/dt = -dH/dq. Poisson bracket: {f,g} = sum(df/dq dg/dp - df/dp dg/dq). Symmetry: Noether's theorem (conservation). Phase space: (q,p). Liouville: volume preserving"),
    ("Central forces and orbital mechanics", "Center of mass frame, reduced mass. Kepler's laws. Two-body problem", "Lagrangian: L = 1/2 mu (r'^2 + r^2 theta'^2) - V(r). Effective potential: V_eff(r) = V(r) + L^2/(2 mu r^2). Kepler: elliptical, hyperbolic, parabolic. Specific orbital energy. Vis-viva equation. Precession"),
    ("Rigid body dynamics", "Moment of inertia tensor I. Euler equations: I omega' + omega x I omega = tau", "Euler angles: 3 rotations (precession, nutation, spin). Quaternions: q = (cos(theta/2), n sin(theta/2)). Angular momentum: L = I omega. Gyroscope: precession omega_p = mgh / (I omega_s). Tensor: principal axes"),
    ("Wave mechanics and oscillations", "Harmonic oscillator: mx'' + kx = 0. Damped: mx'' + cx' + kx = 0. Driven: + F cos(wt)", "Natural freq: w_0 = sqrt(k/m). Damping ratio: zeta = c / (2 sqrt(mk)). Underdamped (zeta < 1): e^{-zeta w_0 t}(A cos(w_d t) + B sin(w_d t)). Resonance: amplitude max at w ~ w_0. Coupled oscillators: normal modes"),
    ("Continuum mechanics: stress, strain, elasticity", "Stress tensor sigma_ij (force/area). Strain epsilon_ij = 1/2 (du_i/dx_j + du_j/dx_i). Hooke's law: sigma = C epsilon", "Young's modulus E = sigma / epsilon (uniaxial). Poisson's ratio nu = -epsilon_transverse / epsilon_axial. Bulk modulus K. Shear modulus G. Navier-Cauchy eq: (lambda + mu) grad(div u) + mu Laplace u + F = rho u''"),
    ("Hamilton-Jacobi theory", "H(q, dS/dq, t) + dS/dt = 0. S: action, generating function", "Canonical transformation: (q,p) -> (Q,P) via generating function F. HJ: characteristic curves. Action-angle variables: J = 1/2pi contour p dq. Integrable systems: n constants in involution. KAM theorem: small perturbation preserves invariant tori"),
]

QUANTUM_MECHANICS_TOPICS = [
    ("Schrodinger equation: time-dependent and stationary", "Time-dep: i hbar d|psi>/dt = H|psi>. Stationary: H|psi> = E|psi>", "Separation: psi(r,t) = phi(r) e^{-iEt/hbar}. 1D infinite well: solutions sin(n pi x / L), E_n proportional n^2. Harmonic: Hermite polynomials. Finite well: transcendental equations. Hydrogen: spherical harmonics + radial solutions"),
    ("Quantum operators and commutation relations", "[x, p] = i hbar. [L_i, L_j] = i hbar epsilon_ijk L_k. Pauli matrices", "Position: X, momentum: P = -i hbar d/dx. Angular momentum: L = r x p. Spin-1/2: S = hbar/2 sigma. Ladder operators: a|n> = sqrt{n}|n-1>, a^+|n> = sqrt{n+1}|n+1>. Hamiltonian: H = hbar w (a^+ a + 1/2)"),
    ("Quantum measurement and decoherence", "Born rule: P(result) = |<result|psi>|^2. Collapse postulate. Density matrix", "Projective: projectors sum to I. POVM: positive operators sum to I. Density matrix: rho = sum p_i |psi_i><psi_i|. Lindblad: master equation. Decoherence: off-diagonal -> 0 in position/environment basis. Zeno: frequent meas. freezes evolution"),
    ("Perturbation theory (time-independent and dependent)", "Time-indep: H = H_0 + lambda V. First: E_n^{(1)} = <n^{(0)}|V|n^{(0)}>. Second: E_n^{(2)} = sum |<k|V|n>|^2 / (E_n - E_k)", "Degenerate: diagonalize V in degenerate subspace. Time-dependent: transition probability P_i->f. Fermi's golden rule: Rate = 2pi/hbar |<f|V|i>|^2 density of states. Sudden approx: state unchanged if H changes fast"),
    ("Scattering theory", "Born approximation: f(theta, phi) = -(m/(2pi hbar^2)) integral e^{-i q . r} V(r) dr^3", "Partial wave: expansion in Legendre polynomials. Phase shift delta_l. Cross section: sigma = 4pi/k^2 sum (2l+1) sin^2 delta_l. S-matrix: unitarity. Resonance: Breit-Wigner. Optical theorem: sigma_tot = (4pi/k) Im f(0)"),
    ("Path integral formulation", "Amplitude = integral D[x(t)] e^{iS[x]/hbar}. Propagator: K(x_f, t_f; x_i, t_i)", "Free particle: Gaussian integral. Classical: stationary action (delta S = 0). Feynman rules: vertex, propagator, loops. Instanton: tunneling via saddle point. QED: photon propagator. Renormalization: absorb divergences in bare params"),
]

ELECTROMAGNETISM_TOPICS = [
    ("Maxwell's equations in vacuum and matter", "Gauss: div D = rho_f, div B = 0. Faraday: curl E = -dB/dt. Ampere: curl H = J_f + dD/dt", "Vacuum: D = epsilon_0 E, B = mu_0 H. Matter: D = epsilon_0 E + P, H = B/mu_0 - M. Wave eq: Laplace E - (1/c^2) d^2E/dt^2 = 0. c = 1/sqrt(epsilon_0 mu_0). Boundary: D_perp, E_parallel, B_perp, H_parallel. Poynting: S = E x H"),
    ("Electromagnetic waves and radiation", "Plane wave: E = E_0 e^{i(kz - wt)}. Polarization: linear, circular, elliptical", "E perpendicular to k. Impedance: Z = E/H = sqrt(mu/epsilon). Energy density: u = 1/2 epsilon E^2 + 1/(2mu) B^2. Dipole radiation: power P = (mu_0 p_0^2 w^4)/(12 pi c). Antenna: radiation pattern. Bremsstrahlung"),
    ("Electrostatics and magnetostatics", "Poisson: div(grad phi) = -rho/epsilon. Laplace: div(grad phi) = 0 (no charge)", "Green function: phi(r) = (1/(4pi epsilon)) integral rho(r') / |r - r'| dr'^3. Method of images. Multipole: monopole, dipole, quadrupole. Biot-Savart: B(r) = (mu_0/4pi) integral I dl' x (r - r')/|r|^3. Ampere: curl B = mu_0 J"),
    ("Relativistic electrodynamics", "4-vector potential: A^mu = (phi/c, A). Field tensor: F^{munu} = d^mu A^nu - d^nu A^mu", "Covariant Maxwell: d_mu F^{munu} = mu_0 J^nu. Lorentz: dp/dtau = q F . u. Transform: E_parallel' = E_parallel, E_perp' = gamma (E_perp + v x B). Lienard-Wiechert: potentials for moving point charge"),
    ("Waveguides and cavities", "TEM: E_perp, B_perp, B = (k/w) k_hat x E. TE: axial H only. TM: axial E only", "Boundary: E_parallel = 0 at walls. TE modes: Hz = H_0 cos(m pi x / a) cos(n pi y / b) e^{i(kz - wt)}. Cutoff: w_c = c sqrt((m pi/a)^2 + (n pi/b)^2). Rectangular waveguide: TE_10 lowest. Quality factor Q. Cavity resonator"),
    ("Plasma physics: Debye shielding, MHD", "Debye length: lambda_D = sqrt(epsilon kT / (n e^2)). Plasma oscillation: w_p = sqrt(n e^2 / (epsilon m))", "MHD: rho dv/dt = J x B - grad p + mu grad^2 v. Induction: dB/dt = curl(v x B) + eta/(mu_0) grad^2 B. Alfven wave: v_A = B/sqrt(mu_0 rho). Frozen-in flux (perfect MHD). Landau damping: collisionless, resonant particles"),
]

def chunk_15_gen():
    cats = [LINEAR_ALGEBRA_TOPICS, CALCULUS_TOPICS, DE_TOPICS, PROBABILITY_TOPICS,
            CLASSICAL_MECHANICS_TOPICS, QUANTUM_MECHANICS_TOPICS, ELECTROMAGNETISM_TOPICS]
    while True:
        for topics in cats:
            for problem, tech, hint in topics:
                inp = pick(
                    f"Math/Physics: {problem}. Solve with {tech}.",
                    f"Compute/analyze {problem} using {tech}.",
                    f"Solve {problem} with focus on {tech}.",
                    f"Derive and implement {problem} mathematically.",
                    f"Advanced: {problem}. Show rigorous approach.",
                    f"Deep dive: {problem} in context of {tech}.",
                )
                plan = pick(
                    f"<PLAN>Math/Physics: {problem}. Method: {tech}. {hint}. Plan: (1) Setup equations. (2) Derivation. (3) Implementation. (4) Verify numeric/analytic. (5) Interpret results.</PLAN>",
                    f"<PLAN>{problem}: Using {tech}. {hint}. Steps: (1) Model. (2) Solve. (3) Validate. (4) Visualize. (5) Document.</PLAN>",
                    f"<PLAN>Scientific computation: {problem}. {tech}. {hint}. Plan: (1) Mathematical formulation. (2) Algorithm. (3) Implementation. (4) Precision analysis. (5) Applications.</PLAN>",
                    f"<PLAN>Analysis: {problem}. Approach: {tech}. {hint}. Phases: (1) Literature. (2) Derivation. (3) Numerics. (4) Testing. (5) Discussion.</PLAN>",
                )
                think = pick(
                    f"<THINK>Scientific analysis for {problem}: {tech}. {hint}.",
                    f"<THINK>Deep dive into {problem}: {tech}. {hint}.",
                    f"<THINK>Mathematical framework for {problem}: {tech}. {hint}.",
                )
                exec_ = pick(
                    f"<EXEC>Math/Physics: {problem}. Solution: {tech}. {hint}. Verified and interpreted.</EXEC>",
                    f"<EXEC>Scientific: {problem}. Computation: {tech}. Accuracy validated. Results documented.</EXEC>",
                    f"<EXEC>Implementation: {problem}. {tech} applied. {hint}. Rigorously verified.</EXEC>",
                )
                yield (inp, plan, think, exec_, random.randint(4,7), "math_physics")

# ============================================================
# CONSTANTS: Generator registry for chunks 6-15
# ============================================================

CHUNK_GENS_EXT = {
    6: chunk_6_gen,
    7: chunk_7_gen,
    8: chunk_8_gen,
    9: chunk_9_gen,
    10: chunk_10_gen,
    11: chunk_11_gen,
    12: chunk_12_gen,
    13: chunk_13_gen,
    14: chunk_14_gen,
    15: chunk_15_gen,
}

CHUNK_NAMES_EXT = {
    6: "Advanced Algorithms & Data Structures",
    7: "Systems & Low-Level Programming",
    8: "Machine Learning & AI Theory",
    9: "Data Science & Statistics",
    10: "Security & Cryptography",
    11: "Game Development & Graphics",
    12: "DevOps & Cloud Infrastructure",
    13: "Database Design & Optimization",
    14: "Software Engineering & Best Practices",
    15: "Advanced Mathematics & Physics",
}

CHUNK_DOMAINS_EXT = {
    6: "algorithms",
    7: "systems",
    8: "machine_learning",
    9: "data_science",
    10: "security",
    11: "game_dev",
    12: "devops",
    13: "database",
    14: "software_engineering",
    15: "math_physics",
}
