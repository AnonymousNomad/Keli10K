#!/usr/bin/env python3
"""Abstract reasoning generator — 15K examples, 7 categories."""
import sys, os, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_tokenizer import SNCATokenizer

random.seed(42)
tok = SNCATokenizer()
os.makedirs('data/abstract', exist_ok=True)

# ─── Template Pools ───────────────────────────────────────────────────────

CAUSAL = [
    ("If component A depends on component B, and B depends on C, what happens if C fails?",
     "C fails → B has unresolved dependencies → A cannot initialize. This cascading failure means the entire chain collapses. Solution: add health checks and graceful degradation at each level."),
    ("In an event-driven system, if message queue M drops 5% of messages, how does that affect 3 downstream services?",
     "Each service independently loses 5% of data. After 2 hops, ~9.75% data loss. After 3 hops, ~14.3% loss. The system must implement exactly-once delivery or idempotent consumers."),
    ("A user session cookie expires in 1 hour. The user takes 65 minutes to fill a form. What happens?",
     "Session expires at 60 min. At 65 min, form submission triggers a session lookup → server rejects with 401. The form data is lost unless the client saves drafts locally. Fix: refresh token on each interaction."),
    ("A database write succeeds but the connection drops before the client receives confirmation. What state is the system in?",
     "The write is committed but the client thinks it failed. Retry creates a duplicate. The system needs idempotency keys: the client sends a unique key, and the server deduplicates on key collision."),
    ("If switching from HTTP/1.1 to HTTP/2 reduces latency by 30%, and adding a CDN reduces latency by 50%, what's the combined effect?",
     "Latency multiplier = 0.7 × 0.5 = 0.35. Combined reduction = 65%. But these improvements may overlap (CDN already uses HTTP/2), making actual gain closer to 50%. Always measure, don't assume compounding."),
    ("A cache hit ratio drops from 95% to 80%. What happens to database load?",
     "Previously 5% of requests hit DB. Now 20% hit DB — a 4× increase in DB load. If DB was at 60% capacity, it now hits 240% → cascading slowdown, connection pool exhaustion, timeout errors."),
    ("A login system has 3 attempts before rate limiting. An attacker tries 100 passwords for 10 accounts. How many attempts before blocking?",
     "Per-account: 3 attempts → lock. But if the attacker rotates accounts, they get 3 per account = 30 total attempts before ANY lock. Better approach: IP-based rate limiting + per-account limiting combined."),
    ("A frontend sends requests every 5 seconds. Backend takes 8 seconds to respond. What happens to the request queue?",
     "Requests accumulate: new request arrives before previous response. After 40 seconds, 8 requests are in flight. If server handles 2 concurrent requests, queue grows unboundedly → OOM crash. Fix: debounce or queue."),
    ("A state update in React triggers re-render, which triggers another state update. What pattern is this?",
     "This is an infinite loop. setState in useEffect or render causes re-render → runs effect again → setState again. React detects this after ~50 iterations and warns. Fix: add dependency array or useRef."),
    ("CSS specificity cascade: element selector vs class vs ID vs inline. If all target the same element, which wins?",
     "Inline (1000) > ID (100) > Class (10) > Element (1). But !important overrides all. If two !important declarations conflict, the one with higher specificity wins. Best practice: avoid !important entirely."),
]

ANALOGIES = [
    ("A database index is like a book's index because:",
     "both provide a lookup table that maps search terms to locations. Without an index, you scan every page (full table scan). With an index, you jump directly to the relevant page (B-tree traversal). Tradeoff: index takes space and slows writes."),
    ("A CDN is like a network of food trucks because:",
     "instead of everyone traveling to the central kitchen (origin server), food trucks park near customers (edge nodes). Each truck serves fresh food (cached content) from a limited menu (cache TTL). The kitchen restocks trucks overnight (cache refresh)."),
    ("A garbage collector is like a janitor in a museum because:",
     "the janitor periodically walks through galleries (heap), identifies trash (unreachable objects), and disposes of them. Visitors (active references) protect exhibits from disposal. The janitor must work at night (GC pause) to avoid disrupting visitors."),
    ("unit test is to integration test as scalpel is to chainsaw because:",
     "a scalpel makes precise, controlled cuts in specific locations (unit test verifies one function in isolation). A chainsaw cuts through multiple layers at once (integration test verifies component interaction). You need both, just not for the same job."),
    ("A microservice boundary is like a national border because:",
     "crossing a border requires documents (serialization), customs checks (validation), and sometimes gets delayed (network latency). Inside the country, movement is free (in-process calls). Good border design minimizes crossing overhead."),
    ("Technical debt is like kitchen grease buildup because:",
     "a little grease is fine today, but never cleaning it leads to a fire hazard. Each quick fix (skip refactoring) adds a layer. Eventually, the entire system must shut down for deep cleaning (rewrite). Regular maintenance is cheaper."),
    ("A queue is like a ticket counter at a deli because:",
     "customers take a number (publish message) and wait. The server processes one at a time (consumer). If the server is slow, the line grows (queue backlog). If the server crashes, customers leave (message TTL dead-letter)."),
    ("A key-value store is like a coat check because:",
     "you hand over your coat (value) and receive a ticket (key). To retrieve, you present the ticket. You can't ask 'what coats are blue?' without checking every ticket. This is why key-value stores lack query flexibility."),
    ("A load balancer is like a receptionist in a busy office because:",
     "the receptionist (load balancer) directs visitors (requests) to available employees (servers). If one employee is busy, the next visitor goes to a different employee. The receptionist knows who is available (health checks)."),
    ("TypeScript is like a seatbelt because:",
     "it's optional but prevents catastrophic failure. You can drive without it (write plain JS) but when a crash happens (runtime type error), you wish you had it. It slows you down slightly to put on (type annotations), but saves lives (production bugs)."),
]

CONSTRAINT = [
    ("You have 3 files: auth.js, database.js, and app.js. auth.js must load before database.js. app.js depends on both. What's the dependency graph?",
     "auth → database → app. A linear chain. Total load time = auth_time + database_time + app_time. If they can't load in parallel, optimize auth first (it blocks everything)."),
    ("Design a rate limiter that prevents 1 million requests/minute but allows legitimate bursts. How do you track state?",
     "Use sliding window counter: track timestamps in a sorted set. Memory: ~8 bytes per request × 1M = 8MB (too much). Better: use token bucket with 1M tokens, refill rate = 1M/60s. Memory: 2 integers."),
    ("A function sorts a list using bubble sort O(n²). For n=10 it's instant. For n=1000 it's 10 seconds. The CEO needs results for n=100,000 in under 5 seconds. What do you do?",
     "Bubble sort on 100K = 10B operations ≈ 10^10 / 10^8 ops/sec = 100 seconds. Need 20× faster. Replace with mergesort O(n log n): 100K × log₂(100K) ≈ 1.7M ops ≈ 0.017 seconds. Algorithm change, not optimization."),
    ("You need to store 1 billion user records. Each record is 1KB. What's the storage requirement and which DB do you choose?",
     "Raw: 1B × 1KB = 1TB. With indexes (2×): ~2TB. Cassandra or ScyllaDB for horizontal scaling. PostgreSQL could work with partitioning (100 partitions × 10GB each) but query complexity increases."),
    ("A web page needs 15 API calls to render. Each takes 200ms. Sequential = 3 seconds. How do you make it faster?",
     "Parallelize: all 15 at once → 200ms total (the slowest). But browsers limit concurrent connections (typically 6). Use connection pooling or HTTP/2 multiplexing. Bundle critical data into fewer endpoints."),
    ("A React app re-renders 5000 list items on every keystroke. How do you fix it?",
     "Virtualization: render only visible items (e.g., react-window). For 50 visible items out of 5000, that's 99% fewer DOM nodes. Also: memoize list items, debounce the input handler, use key prop properly."),
    ("A Docker image is 2GB. The deployment takes 5 minutes per server across 100 servers. How do you speed up deploys?",
     "Total = 500 min. Use multi-stage builds (separate build deps from runtime). Switch to Alpine base (5MB vs 200MB). Use layer caching. Only deploy changed layers. Target: <1GB image, 30s deploy via rolling update."),
    ("A database has 10M rows. SELECT COUNT(*) takes 30 seconds. Why and how to fix?",
     "InnoDB does full scan for COUNT(*) because MVCC makes row count variable per transaction. Fix: use SHOW TABLE STATUS (approximate), maintain counter in Redis, or use a summary table updated by triggers."),
    ("A CI pipeline takes 45 minutes. Developers push 20 times/day. What's the productivity loss?",
     "45 min × 20 pushes = 15 hours/day wait time across the team. With 10 devs at $100/hr, that's $1,500/day in wasted cost. Fix: parallelize test suites, use test impact analysis, cache dependencies."),
    ("An API returns 60KB of JSON for a list of 100 items. The mobile app needs 50 fields per item, but only shows 4. How to optimize?",
     "GraphQL or field selection: let client specify needed fields. 4 fields × 100 items × ~20 bytes ≈ 8KB (87% reduction). Also: pagination (return 20 items per page), compression (gzip reduces another 70-80%)."),
]

ALGORITHMIC = [
    ("Find a duplicate in an array of n+1 integers where values are 1 to n. Compare hash map vs sorting approaches.",
     "Hash map: O(n) time, O(n) space. Store seen values, return first duplicate. Sort: O(n log n) time, O(1) space. Sort then check adjacent elements. Floyd's cycle detection: O(n) time, O(1) space but only works for this specific constraint."),
    ("Design a function to check if two strings are anagrams. Analyze time and space.",
     "Approach 1: Sort both strings → O(n log n), O(1). Approach 2: Count character frequencies → O(n), O(k) where k is alphabet size (26 for lowercase). For Unicode, use hash map → O(n), O(m) where m is unique chars."),
    ("Implement a cache with LRU eviction. Why linked list + hash map?",
     "Hash map gives O(1) lookup. Doubly linked list gives O(1) insertion/deletion at both ends. Combined: get → move to front (O(1)), put → if exists move to front else add to front and evict tail if over capacity."),
    ("Compare BFS vs DFS for finding the shortest path in an unweighted graph.",
     "BFS guarantees shortest path because it explores level by level. DFS finds a path but not necessarily the shortest. Use BFS when all edges have equal weight. Use DFS when memory is limited (BFS queue can be large)."),
    ("Design a function that generates all permutations of a string. What's the time complexity?",
     "Backtracking: swap each character with every subsequent character. O(n!) time, O(n) recursion depth. For n=10: 3.6M permutations. For n=12: 479M. Becomes infeasible after n>12 without pruning."),
    ("Implement debounce vs throttle. When would you use each?",
     "Debounce: wait until activity stops, then fire once. Use for search-as-you-type (wait until user stops typing). Throttle: fire at most once per interval. Use for scroll/resize handlers (ensure updates at regular intervals)."),
    ("Design a function that finds the longest palindrome substring. Compare approaches.",
     "Brute force O(n³): check all substrings. Center expansion O(n²): expand around each of 2n-1 centers. Manacher's O(n): uses symmetry to reuse previous computations. For practical use, center expansion is sufficient."),
    ("How does binary search work and what are its prerequisites?",
     "Prerequisite: sorted array. Steps: compare target with middle element, discard half based on comparison. O(log n) time, O(1) space. For n=1B, need only 30 comparisons. Must be sorted; if sorting cost dominates, linear search may be faster."),
    ("Compare array vs linked list for a fifo queue implementation.",
     "Array: O(1) enqueue (amortized), O(1) dequeue if using front index, but resizing can be expensive. Linked list: O(1) enqueue at tail, O(1) dequeue at head, no resizing, but more memory overhead per element (pointer)."),
    ("Design a Trie for auto-complete. Time and space analysis.",
     "Each node stores 26 children (for lowercase) + is_end flag. Insert: O(m) where m is word length. Search: O(m). Prefix search: O(p + results). Space: O(total_letters). Can be optimized with compression (Radix tree)."),
]

SYSTEM_DESIGN = [
    ("Design a URL shortener like bit.ly. What are the tradeoffs?",
     "Components: API gateway, hash generator, database (key: short_code, value: long_url). Hash: base62 encode auto-increment ID or use hash + collision resolution. Read:write ratio ~100:1. Use cache (Redis) for popular URLs. DB: Cassandra for write scalability or PostgreSQL with read replicas."),
    ("Design a real-time chat system. Compare WebSocket vs SSE vs polling.",
     "WebSocket: bidirectional, persistent connection. Best for chat. SSE: server-to-client only. Good for notifications. Polling: client requests every N seconds. Worst but simplest. For 1M concurrent users: WebSocket servers (gorilla/ws) behind load balancer, Redis pub/sub for message distribution."),
    ("Design a video streaming platform's CDN strategy.",
     "Edge caching: store popular videos at 1000+ edge locations. Use adaptive bitrate streaming (HLS/DASH): encode at 240p-4K, client switches based on bandwidth. Origin store: S3/Blob. Cache hit ratio target: 95%+. Cache key: video_id + resolution."),
    ("Design a payment system that handles idempotency and race conditions.",
     "Idempotency key: client generates UUID, server deduplicates. Two-phase commit: reserve → capture → confirm. If capture fails after 15 min, auto-release reservation. Use optimistic locking on balance records. Audit log every mutation."),
    ("Design a notification system that sends emails, SMS, and push notifications.",
     "Event → notification service → priority queue → template engine → provider router (SendGrid/Twilio/FCM). Retry with exponential backoff. Dead letter queue for failed notifications. Rate limit per user (max 10/min)."),
    ("Design a news feed like Twitter. How do you handle the fan-out problem?",
     "Push for celebrities: pre-compute feed for each follower (fan-out on write). Pull for regular users: compute feed on request (fan-out on read). Hybrid: push to active users, pull for inactive. Cache feed in Redis sorted set by timestamp."),
    ("Design a logging system handling 1TB of logs per day.",
     "Collect: Fluentd/Logstash agents on each server. Buffer: Kafka (retain 7 days). Store: Elasticsearch (hot: 7 days SSD, warm: 30 days HDD, cold: S3). Query: Kibana. Cost: ~$2K/month for 30TB ES hot storage. Cheaper: Loki (index only metadata)."),
    ("Design a job scheduler that runs 1M tasks per day with dependencies.",
     "DAG of tasks. Scheduler picks tasks with all deps satisfied. Workers pull from Redis queue. State in PostgreSQL (scheduled → running → completed/failed). Handle failure: retry 3× with backoff, then alert. Cron trigger or event trigger."),
    ("Design a rate-limited API for a public REST service.",
     "Token bucket per API key: 1000 tokens, refill 10/sec. Store in Redis (INCR + EXPIRE). Return 429 with Retry-After header. For distributed rate limiting: use Redis Cluster or Lua scripts for atomicity."),
    ("Design a search autocomplete system for an e-commerce site with 10M products.",
     "Trie of search queries, each node stores top 10 completions. Build from search logs (mapreduce: count query frequency). Update daily. Frontend: debounce 300ms, send fetch to autocomplete API. Cache popular prefixes in CDN."),
]

DEBUGGING = [
    ("A bug only appears on Tuesdays. What questions do you ask?",
     "1. What runs on a weekly schedule? Cron jobs, data pipelines, maintenance tasks. 2. What changes weekly? Deploy cycles, data exports, report generation. 3. Is it timezone-related? Tuesday in UTC is Monday in PST. 4. Is it a certificate renewal? Let's Encrypt renews every 60 days."),
    ("A React component renders correctly on first load but breaks after navigation. Why?",
     "Missing useEffect cleanup: component unmounts but event listeners, intervals, or subscriptions remain. Next mount creates duplicates. Or: stale closure over old props/state. Fix: add cleanup return to useEffect, use ref for callbacks."),
    ("A query runs fast in development but slow in production. What's different?",
     "1. Data size: production has 1000× more rows. Full scan vs index lookup. 2. Indexes: dev may have all indexes, production missing one. 3. Hardware: production is shared, dev is dedicated. 4. Connection pooling: prod may have exhausted connection pool."),
    ("A user reports 'it works on my machine' but not on the server. Where do you look?",
     "1. Environment variables: different API keys, DB URLs. 2. File system: case sensitivity (Mac vs Linux). 3. OS: path separators, line endings. 4. Python version: 3.8 vs 3.12, library versions. 5. Locale: date formats, number formatting."),
    ("A memory leak in Node.js that grows 1MB/hour. How do you find it?",
     "Take heap snapshots 1 hour apart, compare for retained objects. Common causes: unclosed event listeners, global variables accumulating data, closures holding references, setInterval without clearInterval."),
    ("A SQL query that was fast yesterday is slow today. No code changes. Why?",
     "1. Query plan changed: statistics updated, optimizer chose different plan. 2. Data distribution changed: new values cause index scan vs seek. 3. Other queries: blocking, lock contention. 4. Index fragmentation. Fix: update stats, analyze slow query plan, add hints."),
    ("An API returns 500 errors sporadically, once every ~1000 requests. No pattern in logs. How to debug?",
     "1. Race condition: two threads modify shared state. 2. Resource exhaustion: file descriptors, DB connections. 3. Third-party API timeout with no retry. 4. Character encoding: certain Unicode characters break parsing. Add structured logging with request IDs."),
    ("A CSS animation stutters on mobile but is smooth on desktop. Why?",
     "Mobile GPU is weaker or shares memory. Triggers: animating layout properties (width, height, top) causes reflow. Use transform and opacity only (GPU-composited). Reduce paint area. Use will-change: transform to hint GPU."),
    ("A build that succeeds locally fails in CI. What's different?",
     "1. Clean vs dirty build: CI does clean install, local has cached artifacts. 2. Node version: CI uses latest, local uses nvm-managed version. 3. Lockfile: package-lock.json not committed. 4. Environment variables: CI injects different values."),
    ("A user's session expires randomly while actively using the app. No fixed interval. Why?",
     "1. Session stored in memory on one server, requests routed to different server (sticky sessions missing). 2. Token refresh race: two concurrent requests both refresh token, first succeeds, second invalidates first. 3. Idle timeout counting activity incorrectly."),
]

LATERAL = [
    ("Why would a React app work in Chrome but not Safari? List 5 possibilities.",
     "1. Safari doesn't support optional chaining (?.) in older versions. 2. WebSocket connection fails in Safari with self-signed certs. 3. IndexedDB API differences. 4. CSS grid gaps not supported in Safari 14. 5. Fetch API: Safari has stricter CORS on 3rd-party cookies."),
    ("A deployment causes errors, but rolling back to the same commit that worked yesterday doesn't fix it. Why?",
     "1. External dependency changed: API version, database schema, CDN cache. 2. Configuration is not in the commit: environment variables, feature flags. 3. Data migration ran in production but not rolled back. 4. Certificate expired between tests."),
    ("A test passes locally 100% but fails 30% of the time in CI. What's the cause?",
     "1. Timing-dependent: async operations without proper waits. 2. Port conflict: CI runs tests in parallel on same machine. 3. Random data: test generates random input that occasionally triggers edge case. 4. Shared state between tests: order-dependent."),
    ("A database backup started causing production slowdowns. No changes to backup script. Why?",
     "1. Data growth: backup now reads 10GB instead of 1GB. 2. Locking: backup holds read locks on InnoDB tables. 3. I/O contention: backup saturates disk bandwidth. 4. Transaction log growth: backup prevents log truncation."),
    ("A feature flag rollout to 10% of users causes no issues. Rollout to 50% causes errors. Why?",
     "1. Concurrent users: at 10%, few users hit the same resource. At 50%, contention on shared state (database rows, file locks, cache keys). 2. Thundering herd: cache miss at scale. 3. Connection pool: at 10%, 5 connections used. At 50%, 50 connections → pool exhaustion."),
    ("A code review approved by 3 senior engineers introduces a production bug. How?",
     "1. Cognitive bias: all 3 assumed someone else checked the edge case. 2. Review fatigue: 500-line PR, everyone skimmed. 3. Diff blindness: small change that looks safe but interacts with other changes. 4. Testing gaps: no tests for the edge case."),
    ("A server has 80% CPU usage but zero user traffic. Where is the CPU going?",
     "1. Background jobs: cron, scheduled tasks, data processing. 2. Health check loops: monitoring agents polling excessively. 3. Memory pressure: GC thrashing. 4. Logging: verbose logs writing to disk. 5. Compromised: crypto miner running in background."),
    ("A form validation fails on submit but works on each individual field. What's happening?",
     "1. Race condition: validation runs before field states update. 2. Cross-field validation: field A depends on field B, but B is validated after A. 3. Submit button disabled incorrectly: final validation re-checks all fields and finds transient inconsistency."),
    ("A query returns different results on read replica vs primary. Why?",
     "1. Replication lag: replica is behind primary by seconds. 2. Statement-based replication: non-deterministic functions (NOW(), RAND()) produce different results. 3. Different indexes: replica may have different indexes for reporting. 4. Different isolation levels."),
    ("A single user reporting a bug is often ignored. A hundred users report it within an hour. Both describe different symptoms. What's happening?",
     "1. Shared dependency failure: CDN, DNS, auth provider, database. Each user experiences the failure differently based on what they were doing. 2. Feature flag rollout: introduced a regression that manifests differently per page."),
]


# ─── Generator ────────────────────────────────────────────────────────────

CATEGORIES = [
    ("causal_chains", CAUSAL),
    ("analogies", ANALOGIES),
    ("constraint_solving", CONSTRAINT),
    ("algorithmic_thinking", ALGORITHMIC),
    ("system_design", SYSTEM_DESIGN),
    ("debugging_logic", DEBUGGING),
    ("lateral_thinking", LATERAL),
]

TARGET = 15000
examples_per_category = TARGET // len(CATEGORIES)  # ~2143

print(f'Generating {TARGET} abstract reasoning examples...')

count = 0
with open('data/abstract/train.jsonl', 'w') as out:
    for cat_name, templates in CATEGORIES:
        cat_count = 0
        template_cycle = itertools.cycle(templates)
        while cat_count < examples_per_category:
            q, a = next(template_cycle)
            # Vary the question slightly each time for diversity
            prefix = random.choice([
                f'Here is a question: ',
                f'Think about this: ',
                f'Reason through: ',
                f'Consider: ',
                f'Analyze: ',
            ])
            input_text = f'{prefix}{q}'
            target_text = f'<PLAN>1. Understand the problem: {q[:60]}...</PLAN><EXEC>{a}</EXEC>'

            # Tokenize and check length
            input_ids = tok.encode(input_text)
            target_ids = tok.encode(target_text)
            if len(input_ids) + len(target_ids) <= 1024:
                out.write(json.dumps({
                    'input_ids': input_ids,
                    'target_ids': target_ids,
                    'mode': 'plan',
                    'domain': 'abstract',
                    'adversarial': False,
                }) + '\n')
                cat_count += 1
                count += 1
            else:
                # Try shorter version
                target_text = f'<EXEC>{a[:300]}</EXEC>'
                target_ids = tok.encode(target_text)
                if len(input_ids) + len(target_ids) <= 1024:
                    out.write(json.dumps({
                        'input_ids': input_ids,
                        'target_ids': target_ids,
                        'mode': 'plan',
                        'domain': 'abstract',
                        'adversarial': False,
                    }) + '\n')
                    cat_count += 1
                    count += 1

            if count % 1000 == 0:
                print(f'  Progress: {count} examples generated')

        print(f'  {cat_name}: {cat_count} examples')

print(f'Done. Generated {count} examples to data/abstract/train.jsonl')
