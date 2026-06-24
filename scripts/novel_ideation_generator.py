#!/usr/bin/env python3
"""Novel ideation generator — 10K creative problem-solving examples."""
import sys, os, json, random, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from snca_tokenizer import SNCATokenizer

random.seed(42)
tok = SNCATokenizer()
os.makedirs('data/creative', exist_ok=True)

# ─── Category 1: Problem Reframing ───────────────────────────────────────

REFRAWING = [
    ("I need a todo app",
     "You need a commitment device, not a list. Lists don't make people do things — consequences do. What if the app charged you $1 for every missed deadline, donated to a charity you hate? That's a todo app that works."),
    ("My website loads slow",
     "Your perception of speed is broken. The actual load time doesn't matter — what matters is when the user FEELS they can interact. Show a skeleton screen in 100ms, stream in content, and the user never notices the 2-second load."),
    ("Users forget passwords",
     "Passwords are the wrong abstraction. Authentication should be continuous and passive. What if users authenticated by how they type (keystroke biometrics), or when they use the app (behavioral patterns)?"),
    ("I need a dashboard",
     "No you don't. You need a decision-maker. A dashboard is just eye candy unless it answers exactly one question per screen. What decision do you make from this data? If you can't name it, delete that chart."),
    ("Should I use React or Vue?",
     "Both work. The real question: who maintains this in 2 years when you're gone? Pick the one your team already half-knows. The best framework is the one that doesn't need a rewrite when the original dev quits."),
    ("I want to build an Uber clone",
     "Why? Uber already exists. What's your actual problem? Logistics, trust, or payment? If logistics — build a route optimizer. If trust — build a reputation system. If payment — integrate Stripe. Don't clone, solve."),
    ("My code is messy, I need to refactor",
     "Don't refactor. Rewrite the part that changes most often. 80% of your codebase is never touched. Only 20% is hot code. Find the hot code, clean it, leave the rest alone. Perfect is the enemy of working."),
    ("How do I scale my database?",
     "You probably don't need to. 99% of apps never exceed 1000 concurrent users. Before scaling, optimize: add indexes, use query cache, add Redis. Scaling is a rich person's problem. Optimization is a smart person's solution."),
    ("My team has too many meetings",
     "Meetings are a tax on lack of trust. If you trust your team to read the async update and act on it, you don't need the meeting. Replace status meetings with written async updates. Replace decision meetings with RFC documents."),
    ("I need to learn 10 new technologies for this job",
     "No. You need to learn 3 core concepts. Frameworks change. Concepts don't. Master state management, caching, and async programming. Everything else is syntax sugar on those three."),
    ("My tests are too slow",
     "Your tests are too integrated. Unit tests should run in milliseconds. If they take seconds, you're testing the framework, not your code. Mock the database. Stub the API. Test logic, not infrastructure."),
    ("Users don't read the documentation",
     "Good documentation isn't read. It's felt. If you need docs to explain your UI, your UI is wrong. The best UX is invisible — users just know what to do. Fix the interface, not the README."),
    ("My startup needs to move fast",
     "Moving fast means making decisions fast, not coding fast. You can code 100 lines per hour but if those lines solve the wrong problem, you're moving backward. Speed == clarity of direction, not velocity of keystrokes."),
    ("We need microservices",
     "You need bounded contexts, not microservices. Start with a monolith. Extract services only when you can prove the monolith is slowing you down. Premature microservicing is the root of all evil in distributed systems."),
    ("The design looks ugly",
     "Ugly that works > beautiful that confuses. Before redesigning, check: does the user find what they need in 3 seconds? If yes, ugly is fine. If no, the layout hierarchy is wrong. Make it functional first, then pretty."),
    ("I have too many tabs open",
     "Your working memory is full. Each open tab is a deferred decision. Close everything except what you need right now. If you'll need it later, bookmark it. If you won't, forget it. Context switching costs 23 minutes per interruption."),
]

REFRAWING_INPUTS = [r[0] for r in REFRAWING]
REFRAWING_TARGETS = [r[1] for r in REFRAWING]

# ─── Category 2: Cross-Domain Mashups ────────────────────────────────────

MASHUPS = [
    ("What if Tinder's swipe mechanic met Excel's data grid?",
     "Data validation becomes a swipe. Swipe right to include a row in a report, swipe left to exclude. Swipe up to promote to a summary. The grid becomes a pipeline — data flows through decisions, not just sits in cells."),
    ("What if Minecraft's block-building met project management?",
     "Tasks are blocks you place in a 3D space. Dependencies connect blocks like redstone. Completed tasks emit particles. Late tasks turn to gravel. The Gantt chart becomes a physical world you walk through."),
    ("What if Spotify's recommendation engine met code review?",
     "The reviewer sees 'You fixed a React useEffect memory leak — here are 3 similar patterns in your codebase.' Code review becomes a learning tool. The model learns what each developer struggles with and suggests relevant education."),
    ("What if a Tamagotchi met CI/CD?",
     "Your deployment pipeline is a digital pet. It evolves based on what you feed it (test coverage, code quality). It gets happy when tests pass, sad when they fail, and DIES if you deploy without tests. Developers take care of their builds."),
    ("What if Google Maps navigation met code architecture?",
     "You enter a destination (feature request). The system maps the shortest path through existing code, warns about roadblocks (tech debt), suggests detours (refactoring), and estimates arrival time (delivery date). Codebase = city map."),
    ("What if a restaurant menu met an API design?",
     "Each endpoint is a dish. Appetizers are health checks. Mains are core CRUD. Desserts are analytics. The menu (API docs) shows ingredients (params), preparation time (latency), and dietary restrictions (auth)."),
    ("What if a fitness tracker met a code linter?",
     "Each day the linter gives you a 'code fitness score' based on complexity, duplication, test coverage. Streak bonuses for clean commits. Warnings when you write 'smelly' code. Leaderboard for team code hygiene."),
    ("What if Instagram filters met error messages?",
     "Error messages stop looking like technical vomit and start looking helpful. A 500 error shows a heat map of where things broke. A 404 suggests similar valid routes. Errors become diagnostic visualizations, not stack traces."),
    ("What if a chess engine met deployment strategy?",
     "Each deploy is a chess move. You think 3 moves ahead (rollback plan). The system evaluates board positions (system health). Castling = blue-green deploy. En passant = canary release. Checkmate = prod outage."),
    ("What if a recipe app met database schema design?",
     "Tables are ingredients. Indexes are prep work. Migrations are cooking steps. You can taste (query) at each step. Too many ingredients (columns) = complex dish. Missing ingredients (nullable fields) = substitution risk."),
    ("What if Uber's rating system met a code review tool?",
     "Each PR gets a passenger rating (code quality) AND driver rating (reviewer thoroughness). Low-rated code gets matched with high-rated reviewers. Bad reviewers get fewer PRs assigned. Market dynamics improve both sides."),
    ("What if a language translator met error handling?",
     "Errors are translated from 'system-speak' to 'user-speak'. Instead of 'IndexError: list index out of range', it says 'You tried to access item 5 in a list that only has 3 items. Items available: 0, 1, 2'."),
    ("What if a thermostat met autoscaling?",
     "Set a desired temperature (response time). The system heats up (adds servers) or cools down (removes servers) to maintain it. Predictive algorithms anticipate traffic spikes like thermostats anticipate temperature changes."),
    ("What if a photo album met a component library?",
     "Components are photos in an album. You flip through (browse), zoom in (inspect code), tag faces (document props), add to favorites (star components). Albums versioned like photo collections over time."),
    ("What if a voting system met code deployment?",
     "Stakeholders vote on features. Weighted by expertise. Feature passes with 60% approval. Code deploys only if vote passes. Retrospectives after each release to adjust voting weights."),
]

# ─── Category 3: Constraint-Based Innovation ──────────────────────────────

CONSTRAINED = [
    ("Build a chat app with no database",
     "Use the filesystem. Each message is a file named by timestamp. Read directory for history. No DB install needed. Slow after 10K messages, but for a team of 5 it works. Bonus: messages are real files you can grep."),
    ("Build a search engine with no server",
     "Use the browser. Service worker pre-fetches and indexes pages on first visit. localStorage stores the index. Search is instant, offline, and zero-infrastructure. Perfect for documentation sites. Tradeoff: only indexes visited pages."),
    ("Build a game with only CSS",
     "Checkbox hack + transitions. Radio buttons control state, :checked toggles scenes, CSS animations provide motion. No JS at all. Games like memory match, tic-tac-toe, even simple platformers are possible."),
    ("Build a social network that works entirely offline",
     "Local-first architecture. CRDTs for conflict resolution. Each user has a local database that syncs when connectivity is available. Posts work offline, comments sync later. Like Git for social media. Tradeoff: eventual consistency."),
    ("Build an image editor in a terminal",
     "Use pixel art in terminal cells. Each character is a pixel. Colors via ANSI escape codes. Operations: draw with arrow keys, fill with flood fill, save as .txt. ImageMagick converts to/from real formats."),
    ("Build a payment system with no server",
     "Use Web Crypto API for signing. Client creates payment intent, signs it with private key. Merchant verifies with public key. No server in the middle. Tradeoff: no refund capability, no dispute resolution."),
    ("Build a CI/CD pipeline with no dedicated server",
     "GitHub Actions. Or GitLab CI. Or any runner. The pipeline is a YAML file in the repo. Self-hosted runner runs on any available machine (your laptop, a Raspberry Pi, an old server). Infinite horizontal scaling for free."),
    ("Build a database with only flat files",
     "Each table is a CSV. SQL queries become Python one-liners: `grep, cut, sort, uniq`. For <1M rows, this is fine. PostgreSQL is overkill for your blog's 100 posts. The simplest tool that works is the right tool."),
    ("Build a rate limiter with no Redis",
     "Use the filesystem. Each IP address creates a file. File name = IP, content = count. `touch` updates mtime. Read directory for count. Cron job clears stale files. Works for <1000 concurrent users. No dependencies."),
    ("Build a notification system with no push service",
     "Polling. Client asks 'anything new?' every 30 seconds. Server says yes/no and sends updates. Add exponential backoff. For internal tools, polling at 30s is indistinguishable from push. No WebSocket, no SSE, no third-party."),
    ("Build a CMS with no database",
     "Markdown files in a Git repo. Git history = versioning. Git branches = staging/prod. Push to deploy. Static site generator builds HTML. No DB, no CMS admin panel. Just a folder of .md files."),
    ("Build a recommendation engine with no ML",
     "Collaborative filtering via SQL. 'People who bought this also bought' is just a self-join on purchase history. No training. No inference server. Just a nightly SQL query that pre-computes recommendations."),
]

# ─── Category 4: Master Collaborator ──────────────────────────────────────

COLLABORATOR = [
    ("I want to build an Uber clone",
     "Why? Uber is a logistics company that looks like a tech company. The hard part isn't the app—it's the network of drivers, the insurance, the regulations. What's your moat? If it's 'better UI,' don't bother. Uber already has designers."),
    ("I need a dashboard",
     "What decision does a human make while looking at it? If you can't answer in one sentence, you don't need a dashboard. You need a report. A dashboard is for decisions in the moment. A report is for patterns over time."),
    ("Should I use React or Vue?",
     "Wrong question. Both are fine. The real question: who maintains this in 2 years? If it's just you, pick what you know. If it's a team, pick whichever is easier to hire for in your market. Tech choices are people problems."),
    ("I have an idea for an app",
     "Ideas are cheap. Show me the user who cried because they don't have this. If you can't find one, you're building a solution in search of a problem. Find the pain, not the idea. The pain is the product."),
    ("How do I get started with machine learning?",
     "Don't. Start with statistics. ML is 90% data cleaning, 9% feature engineering, 1% model selection. If you can't explain the distribution of your data, no model will save you. Start by asking: what question am I answering with data?"),
    ("My code is a mess. I need to start over.",
     "That's the seduction of the rewrite. You think 'next time I'll get it right.' You won't. You'll make different mistakes. Refactoring is like cleaning a garage: you only keep what you use. Rewriting is moving houses—you just take the mess with you."),
    ("I'm stuck between these two design patterns",
     "Stop choosing. Write both. See which one hurts less to maintain after a week. Design patterns are crutches for weak abstractions. If the code is simple enough, you don't need a pattern. Complexity should be a last resort."),
    ("How do I convince my boss to let me refactor?",
     "Don't use the word 'refactor.' Managers hear 'I want to rewrite everything for fun.' Instead say: 'This module takes 3 days to add a feature. If I clean it up, it takes 1 day. That saves us 2 days next sprint.' Speak in time, not code quality."),
    ("I think I need a database",
     "Do you need persistence or just state? If the data fits in memory and doesn't need to survive a crash, use a dict. If it needs to persist but fits on one machine, use SQLite. If it needs multiple machines, then you need a real database."),
    ("I don't understand this legacy code",
     "Good. That means it's bad code. Bad code is code that requires context the author didn't write down. Your job isn't to understand it—it's to make it understandable. Rename variables. Extract functions. Add tests. Then you'll understand it."),
    ("How do I hire good developers?",
     "Give them a broken test suite and ask them to fix it. Good developers debug. Great developers write tests that prevent bugs. Don't ask trivia like 'what is a closure.' Ask them to fix a broken one and explain what they learned."),
    ("My startup is running out of money",
     "Stop building features. Go sell. You don't have a product problem, you have a revenue problem. Features don't make money. Customers make money. Talk to 10 potential customers today. Don't write code until you've had those conversations."),
    ("I want to contribute to open source",
     "Don't start by writing code. Start by reading. Find a project you use daily. Read their issue tracker. Read their PRs. Understand their conventions. Then fix a typo in docs. Then fix a small bug. Earn the right to contribute."),
    ("Which cloud provider should I use?",
     "The one you already know. All three major clouds are identical in capability. The difference is your team's familiarity. A team that knows AWS will build faster on AWS than a team learning GCP. Speed to market beats cloud optimization."),
    ("I feel like I'm not a real developer",
     "Imposter syndrome means you're growing. The day you feel like an expert is the day you stopped learning. Every real developer I know feels like a fraud. The fakes are the ones who are confident. Stay uncomfortable. It means you're becoming."),
]

# ─── Category 5: Architecture Invention ──────────────────────────────────

ARCHITECTURE = [
    ("Design a social network where users own their data",
     "Use ActivityPub protocol + local-first storage. Each user runs a personal data server (like Solid Pods). Posts are CRDTs that sync between servers. The 'feed' is a federation of your friends' servers. No central database. No ads. No surveillance."),
    ("Design a code editor that prevents bugs before you write them",
     "Real-time static analysis as you type. TypeScript for type safety, ESLint for patterns, and a custom analyzer for common bug patterns. The editor shows 'this code will throw if usersInput is empty' before you save. Predictive bug detection."),
    ("Design a payment system with no central authority",
     "Use signed messages + a public ledger. Alice signs a message 'I give Bob $5' and broadcasts it. Everyone keeps a copy of the ledger. Double-spend is detected by checking the sequence number. No blockchain needed — just signatures and gossip."),
    ("Design a search engine that learns your intent",
     "Query embedding + behavioral reranking. First stage: BM25 for keyword match. Second stage: user behavior model reranks based on what similar users clicked. Third stage: personalized embedding of your past searches. Learns intent patterns over time."),
    ("Design a CI/CD system for an offline-first world",
     "Git as the source of truth. CI runs on developer machines when they pull (pre-commit hooks). Tests run in Docker containers. Results are gossiped via a peer-to-peer network. No central CI server. Works in a bunker with no internet."),
    ("Design a database that automatically tunes itself",
     "Monitor query patterns. For the top 10 slow queries, suggest or auto-create indexes. Track which indexes are never used and drop them. Analyze query plans and suggest rewrites. The database becomes a DBA that works 24/7 and never sleeps."),
    ("Design an authentication system that works without passwords",
     "Cryptographic key pairs. User generates a key pair in the browser. Public key is stored on the server. Login = sign a challenge with the private key. No password to leak. No password to forget. Works like SSH but for web apps."),
    ("Design a testing system that generates its own test data",
     "Schema introspection → generate valid but random data. Constraint satisfaction: foreign keys reference existing records. Edge case injection: test with empty strings, nulls, very long strings, Unicode, SQL injection attempts."),
    ("Design a deployment system that detects regressions automatically",
     "Deploy to canary (5% of users). Collect real-user metrics: error rate, latency, conversion. Compare to baseline. If any metric degrades beyond threshold, auto-rollback. The canary runs for 15 minutes before full rollout."),
    ("Design a bug tracker that automatically fixes bugs",
     "When a crash is reported, the system captures the stack trace, git blame identifies the responsible commit, reverts it, runs the test suite, and creates a PR. The developer just reviews. Turnaround time: 2 minutes instead of 2 days."),
    ("Design a content delivery network with no servers",
     "Use the users themselves. Each user who visits a page becomes a temporary cache node. Peer-to-peer CDN using WebRTC. Popular content replicates quickly. Rare content falls back to origin. Works best for viral content."),
    ("Design a monitoring system that predicts failures before they happen",
     "Collect metrics over time. Train a simple anomaly detector on normal patterns. When metrics deviate (latency spike, error rate increase), predict 'this will fail in 30 minutes' and alert. Proactive, not reactive. Fix before users notice."),
    ("Design a code review system that reviews itself",
     "Each PR is analyzed for: test coverage change, complexity delta, security vulnerabilities. Automated reviewer adds comments for common issues. Human reviewer only sees what the bot couldn't handle. Reduces review time by 70%."),
    ("Design a architecture decision record system that prevents bad decisions",
     "Every ADR is scored against known failure patterns. 'We chose MongoDB because it's web scale' → warning: 'MongoDB is great for document storage, but this use case requires joins.' Historical data shows which decisions led to rewrites."),
    ("Design a documentation system that stays fresh",
     "Auto-generate docs from code + tests. When code changes, docs are flagged as stale. The system runs the examples in the docs as tests. If they fail, the docs are wrong. Documentation becomes a first-class test artifact."),
]

# ─── Category 6: Red Foreman ────────────────────────────────────────────

RED_FOREMAN = [
    ("I'm going to use MongoDB for our financial system",
     "That's the worst idea I've heard this week. You're trusting money transactions to a database that doesn't support ACID transactions by default. Financial systems need atomicity more than they need flexible schemas. Use PostgreSQL. It has JSON fields if you need flexibility."),
    ("I'll just add more servers when it gets slow",
     "Throwing hardware at a software problem is expensive. Before buying more servers, find the bottleneck. It's probably N+1 queries, not CPU. Optimize first. Scale only after you've squeezed every drop of performance from existing hardware."),
    ("We can fix it in production",
     "That attitude is why production is on fire. The 5 minutes you save by not testing costs 5 hours of debugging at 3 AM. If it's not tested, it's broken. You just haven't discovered which way yet."),
    ("This time I'll write it properly from scratch",
     "I've seen 47 rewrites. Only 3 succeeded. The rest produced the same mess with different variable names. You don't have a code problem. You have a specification problem. Write down what it should do before you delete what it does."),
    ("I don't need tests, I know what I'm doing",
     "Famous last words. I've never met a developer who writes bug-free code without tests. Not one. Tests aren't for you. They're for your future self at 2 AM wondering why the payment system is broken. Write tests."),
    ("We need Kubernetes for our blog",
     "You don't need Kubernetes. You need a $5 VPS. Kubernetes is a distributed systems platform, not a web host. Running K8s for a blog is like using a cargo ship to cross a pond. Use a static site generator and a CDN."),
    ("I'm going to build everything as microservices",
     "No. You're going to build a distributed monolith with network overhead. Microservices are not a free lunch. They're a trade: operational complexity for team autonomy. If you have fewer than 20 engineers, you don't have a microservices problem."),
    ("This one-line change is safe, I don't need to test it",
     "That's what the last person said before they took down production for 4 hours. Every one-line change looks safe. That's what makes it dangerous. It's not the line that's risky—it's the assumption that it has no side effects."),
    ("We'll just use AI to generate all our code",
     "AI generates the average of all code on the internet. Average code is mediocre code. If you can't tell good code from bad code, AI will give you confidently wrong code that looks correct. You still need to understand what you're building."),
    ("It works on my machine",
     "Then your machine is wrong. Code that works on one machine but not others is environment-dependent. Docker exists for exactly this reason. Containerize your app. If it fails in production but not locally, your dependencies aren't locked."),
    ("We'll add type checking later",
     "No you won't. You never do. Type checking is like a seatbelt—you don't add it after the crash. Python without types is a prototype language. TypeScript exists because JavaScript needs structure. Add types from the start or accept the tech debt."),
    ("I'm going to use a blockchain for this",
     "Unless you're building a trustless decentralized system with no central authority, you don't need a blockchain. 99% of 'blockchain projects' should be a PostgreSQL database. Blockchain is a solution looking for a problem in most cases."),
    ("We'll document it after launch",
     "You just created 6 months of undocumented code that nobody will understand. Documentation written after the fact is always incomplete because you forget the decisions you made. Document why, not what. The code shows what. Comments show why."),
    ("This is just temporary code",
     "There is nothing more permanent than a temporary solution. That 'quick fix' from 2 years ago is now a core dependency. Nothing is more permanent than a temporary solution because everyone forgets it's temporary."),
    ("Let's just use the bleeding-edge version",
     "Bleeding edge means you're the beta tester. You will find bugs. You will have no migration path. You will be stuck on an unsupported version when the next breaking change drops. Use the version that's been stable for 6 months minimum."),
]


# ─── Generator ───────────────────────────────────────────────────────────

CATEGORIES = [
    ("problem_reframing", REFRAWING, 'reframing'),
    ("cross_domain_mashups", MASHUPS, 'mashup'),
    ("constrained_innovation", CONSTRAINED, 'constraint'),
    ("master_collaborator", COLLABORATOR, 'collaborator'),
    ("architecture_invention", ARCHITECTURE, 'architecture'),
    ("red_foreman", RED_FOREMAN, 'foreman'),
]

TARGET = 10000
examples_per_cat = TARGET // len(CATEGORIES)

fmt_map = {
    'reframing': ('<REFLECTION>', '</REFLECTION><EXEC>'),
    'mashup': ('<PLAN>', '</PLAN><EXEC>'),
    'constraint': ('<PLAN>', '</PLAN><EXEC>'),
    'collaborator': ('<REFLECTION>', '</REFLECTION><EXEC>'),
    'architecture': ('<PLAN>', '</PLAN><EXEC>'),
    'foreman': ('<REFLECTION>', '</REFLECTION><EXEC>'),
}

count = 0
with open('data/creative/train.jsonl', 'w') as out:
    for cat_name, templates, fmt_key in CATEGORIES:
        cat_count = 0
        template_cycle = itertools.cycle(templates)
        while cat_count < examples_per_cat:
            q, a = next(template_cycle)
            prefix = random.choice([
                '', 'Here is a creative challenge: ', 'Think outside the box: ',
                'Consider this: ', 'Innovation prompt: ',
            ])
            open_tag, close_tag = fmt_map[fmt_key]
            input_text = f'{prefix}{q}'
            target_text = f'{open_tag}{a}{close_tag}</EXEC>'
            if not target_text.endswith('</EXEC>'):
                target_text += '</EXEC>'

            input_ids = tok.encode(input_text)
            target_ids = tok.encode(target_text)
            if len(input_ids) + len(target_ids) <= 1024:
                out.write(json.dumps({
                    'input_ids': input_ids,
                    'target_ids': target_ids,
                    'mode': 'plan',
                    'domain': 'creative',
                    'adversarial': False,
                }) + '\n')
                cat_count += 1
                count += 1
            else:
                shorter = a[:200]
                target_text = f'{open_tag}{shorter}{close_tag}</EXEC>'
                target_ids = tok.encode(target_text)
                if len(input_ids) + len(target_ids) <= 1024:
                    out.write(json.dumps({
                        'input_ids': input_ids,
                        'target_ids': target_ids,
                        'mode': 'plan',
                        'domain': 'creative',
                        'adversarial': False,
                    }) + '\n')
                    cat_count += 1
                    count += 1

            if count % 2000 == 0:
                print(f'  Progress: {count} examples generated')

        print(f'  {cat_name}: {cat_count} examples')

print(f'Done. Generated {count} examples to data/creative/train.jsonl')
