# Keli10K: Sovereign Nanobot Swarm Intelligence

## Executive Summary
Keli10K is a 25.1 million parameter language model built on a novel **nanobot swarm architecture** — 10,000 individually differentiable "nanobots" that coordinate through 5 territorial coordinators to solve tasks. Unlike traditional transformer models that process information through monolithic feed-forward layers, Keli distributes computation across a dynamic swarm that can specialize, collaborate, and adapt to different problem domains in real-time.

## Architecture

### Core Transformer Backbone (d_model=384, 7 layers, 6 heads)
- **Sparse Sliding-Window Attention**: Each token attends to a local window of 128 positions plus 4 global memory tokens
- **FFN Hidden**: 768 dimensions (2× d_model)
- **Vocabulary**: 8,192 tokens (ASCII + common keywords + special tokens)
- **Max Context**: 4,096 tokens
- **Total Base Parameters**: ~25.1M

### Nanobot Swarm (10,000 bots)
- **Nanobot Embedding Layer**: 10,000 × 200-dim embedding vectors
- **Dynamic Routing**: TaskRouter selects top-32 bots per input via learned affinity
- **Communication Gates**: 2 layers of inter-bot communication (Conv1D over bot dimension)
- **Territory Biases**: 5 soft territories (HTML, CSS, JS, Python, DB) with learned biases

### Coordinator System (5 Bosses)
- **CoordinatorBots**: 10 coordinator vectors that classify task type (engineering/creative/debug/chat)
- **Territory Allocator**: Per-task-type MLP that distributes swarm weights across 5 territories
- **Confidence Gate**: Sigmoid-gated confidence score based on coordinator agreement
- **TaskRouter**: Routes swarm based on task type + territory allocation

### Tokenizer
- **8192 token vocabulary**: 15 special tokens + 95 ASCII chars + 100 numbers + common keywords
- **No UNK for English**: Unknown words fall back to character-level encoding
- **Whitespace-preserving**: Spaces encoded as token IDs

## Training

### Dataset: 1.5M Gold-Standard Cognitive Examples
15 domains × 100K examples each:

| Domain | Topics |
|--------|--------|
| Advanced Algorithms | Sorting, Graphs, DP, Strings, Trees, Greedy, Recursion, Search, Math, Geometry |
| Systems & Low-Level | Memory, Processes, IPC, File I/O, Concurrency, Networking, Assembly, Profiling, C FFI, Embedded |
| ML & AI Theory | Neural Networks, CNNs, RNNs, Transformers, Attention, GANs, RL, Optimization, Bayesian Methods |
| Data Science & Statistics | Probability, Distributions, Testing, Regression, Clustering, PCA, Time Series, Bayesian Inference |
| Security & Cryptography | Symmetric/Asymmetric Crypto, Hashing, PKI, Web Security, Network Security, Malware Analysis |
| Game Dev & Graphics | 2D/3D Rendering, Shaders, Physics, Animation, Audio, Input, AI, Networking, Optimization |
| DevOps & Cloud | CI/CD, Docker, Kubernetes, Terraform, Monitoring, Logging, AWS/GCP/Azure, Git |
| Database Design | SQL, NoSQL, Indexing, Query Optimization, Transactions, Replication, Sharding, CAP Theorem |
| Software Engineering | OOP, SOLID, Design Patterns, Testing, Refactoring, Microservices, APIs, Debugging |
| Advanced Math & Physics | Linear Algebra, Calculus, Diff Eqs, Stats, Mechanics, E&M, QM, Thermodynamics |

### Training Protocol
- **Hardware**: CPU-only (8 cores, 7.2GB RAM)
- **Batch Size**: 4
- **Sequence Length**: 384 tokens
- **Optimizer**: AdamW (lr=1e-4, weight_decay=0.01)
- **Loss**: Cross-entropy (masked, target tokens only)
- **Gradient Clipping**: 1.0
- **Checkpoint**: Every 100 steps (~261MB per checkpoint)

## Features

### Terminal CLI (Parrot-Style)
- **Plan Mode**: Coding Q&A with confidence-gated responses
- **Build Mode**: Multi-file project generation with territory progress bars
- **Tutor Mode**: Step-by-step interactive lessons with certificates
- **Train Mode**: Keli as teacher — generate examples, score outputs, distill knowledge to student models
- Wave animation, territory monitors, typewriter rendering

### Web IDE (Underwater Theme)
- CodeMirror editor with syntax highlighting
- File tree with persistent IndexedDB storage
- Chat panel with Keli AI
- Blueprint visualization (swarm node graph)
- Audio engine (ambient underwater sounds)
- Build/preview/export system
- Certificate of completion

### API Server
- RESTful API on port 8085
- Endpoints: /chat, /build, /tutor, /train, /preview, /export, /health, /status
- CORS-enabled for cross-origin access
- Static file serving for IDE

## Usage

### Start the API Server
```bash
python api_server.py
# → http://0.0.0.0:8085
```

### Launch the CLI
```bash
python launch.py --mode cli
# or standalone:
python cli/keli.py
```

### Launch Everything
```bash
python launch.py --mode all
```

### Web IDE
Open http://localhost:8085 in a browser.

### Train a Model with Keli
```bash
python cli/keli.py
# Select [4] TRAIN mode
# > generate 50
# > train
```

## Benchmarks

*(To be completed after training convergence)*

| Benchmark | Keli10K | GPT-2 125M | Comparison |
|-----------|---------|------------|------------|
| MMLU (adapted) | TBD | 32.4% | - |
| GSM8K | TBD | 8.5% | - |
| HumanEval | TBD | 4.8% | - |
| MBPP | TBD | 12.6% | - |

*Note: Keli10K has 25.1M params vs GPT-2's 125M — ~5× smaller. Benchmarks adapted for scale.*

## Comparison to Frontier Models

| Capability | Keli10K | Claude Code | Codex (OpenAI) | Gemini Antigravity |
|-----------|---------|-------------|----------------|-------------------|
| Architecture | 10K nanobot swarm | Transformer (Fable 5) | Transformer (o-series) | Transformer (3.5 Flash) |
| Parameters | 25.1M | Unknown (100B+) | Unknown (100B+) | Unknown |
| Local CPU Inference | ✓ | ✗ | ✗ | ✗ |
| Open Source | ✓ | ✗ | ✗ | ✗ |
| Multi-Agent | 10K bots native | Sub-agent delegation | Worktree agents | Managed agents |
| Self-Confidence Scoring | ✓ | ✗ (blackbox) | ✗ (blackbox) | ✗ (blackbox) |
| Training Mode | ✓ (teach other models) | ✗ | ✗ | ✗ |
| Swarm Visualization | ✓ | ✗ | ✗ | ✗ |
| Offline Capable | ✓ | ✗ | ✗ | ✗ |

## License
MIT — Free for all use. No restrictions. No telemetry. No nonsense.

## Support
Keli is and always will be free. If you'd like to support development:
- ☕ **Buy me a coffee**: https://ko-fi.com/ferrellsi
- 💖 **GitHub Sponsors**: https://github.com/sponsors/AnonymousNomad

Every contribution helps keep the nanobots swimming. No pressure either way.

## Acknowledgements
Built with PyTorch, HuggingFace, and 10,000 very opinionated nanobots.
