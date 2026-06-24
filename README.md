# ◢◣ Keli10K — Sovereign Nanobot Swarm Intelligence

**25.1M parameters · 10,000 nanobots · 5 territories · CPU-native**

Keli is a language model built on a **nanobot swarm architecture**. Instead of monolithic feed-forward layers, 10,000 individually differentiable nanobots coordinate through territorial coordinators to solve coding tasks. Runs entirely on CPU. No GPU required.

## Quick Start

```bash
pip install torch

# Start the API + IDE server
python api_server.py

# Or launch the terminal CLI
python cli/keli.py

# Or do both
python launch.py --mode all
```

Open **http://localhost:8085** for the web IDE.

## Terminal Modes

| Mode | Command | What it does |
|------|---------|-------------|
| **Plan** | `[1]` | Coding Q&A with confidence-scored responses |
| **Build** | `[2]` | Multi-file project generation with territory visualization |
| **Tutor** | `[3]` | Interactive step-by-step coding lessons with certificates |
| **Train** | `[4]` | Keli as teacher — generate training data, score outputs, supervise other models |

## Architecture

```
                    ┌──────────────────────┐
                    │  10 Coordinator Bots  │
                    │  (task classification)│
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │     TaskRouter        │
                    │  (routes 10K swarm)   │
                    └──────────┬───────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │ HTML    │          │  CSS    │          │  JS     │
    │ Territory│         │Territory│         │Territory│
    └─────────┘          └─────────┘          └─────────┘
    ┌────▼────┐          ┌────▼────┐
    │ Python  │          │  DB     │
    │Territory│         │Territory│
    └─────────┘          └─────────┘
```

## Training

Keli10K trains on **1.5M gold-standard cognitive examples** across 15 domains. The training loop streams from disk with manual batching, checkpointing every 100 steps. Current checkpoint: ~261MB.

## Train Your Own Models

Keli's **Train mode** lets you use the 10K nanobot swarm as a teacher:
1. Load your student model (PyTorch)
2. Keli generates high-quality training examples
3. Keli scores outputs and provides feedback
4. Run distillation epochs with progress tracking

## Web IDE

The underwater-themed IDE features:
- Code editor with syntax highlighting (CodeMirror)
- File tree with persistent storage (IndexedDB)
- AI chat panel
- Blueprint swarm visualization
- Ambient audio engine
- Build/preview/export system

## Comparison

- **vs Claude Fable 5**: Keli is 1000× smaller, runs on CPU, fully open source, has confidence-gated responses, and includes a native training mode
- **vs OpenAI Codex**: Keli provides transparent confidence scoring, swarm visualization, and offline capability
- **vs Gemini Antigravity**: Keli's nanobot architecture provides transparent multi-agent coordination with territorial specialization

## Support Keli

Keli is and always will be **free and open source** (MIT). If you want to support development:

| Method | Link |
|--------|------|
| ☕ Buy me a coffee | [ko-fi.com/ferrellsi](https://ko-fi.com/ferrellsi) |
| 💖 GitHub Sponsors | [github.com/sponsors/AnonymousNomad](https://github.com/sponsors/AnonymousNomad) |
| ₿ Bitcoin | `bc1q...` (coming soon) |

Every coffee keeps the nanobots swimming. No pressure — the code is free regardless.

## License

MIT — Free for all use. No restrictions. No telemetry. No nonsense.

---

*Built with PyTorch · 10,000 nanobots can't be wrong · [Support the swarm](https://ko-fi.com/ferrellsi)*
