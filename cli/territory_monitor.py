"""Real-time territory progress bars for build mode."""
import sys, time, shutil, threading

class TerritoryMonitor:
    TERRITORIES = ['HTML', 'CSS', 'JS', 'Python', 'DB']

    def __init__(self):
        self._progress = {t: 0.0 for t in self.TERRITORIES}
        self._running = False
        self._lock = threading.Lock()

    def set_progress(self, territory, pct):
        with self._lock:
            self._progress[territory] = min(100.0, max(0.0, pct))

    def render(self):
        term_w = shutil.get_terminal_size((80, 20)).columns
        bar_w = term_w - 24
        sys.stdout.write('\033[1;96m[BUILD] Territories activating:\033[0m\n')
        for t in self.TERRITORIES:
            pct = self._progress[t]
            filled = int(bar_w * pct / 100)
            empty = bar_w - filled
            bar = f'\033[92m{"▓" * filled}\033[90m{"░" * empty}\033[0m'
            sys.stdout.write(f'  \033[93m{t:<8}\033[0m {bar} \033[94m{pct:5.1f}%\033[0m\n')
        sys.stdout.flush()

    def simulate_build(self, duration=3.0):
        self._running = True
        import random
        stages = [
            (0.0, 0.2, 0.1, 0.0, 0.0),
            (0.5, 0.4, 0.3, 0.0, 0.0),
            (0.8, 0.6, 0.5, 0.1, 0.0),
            (0.95, 0.85, 0.7, 0.2, 0.1),
            (1.0, 1.0, 0.95, 0.3, 0.2),
            (1.0, 1.0, 1.0, 0.5, 0.4),
            (1.0, 1.0, 1.0, 0.8, 0.7),
            (1.0, 1.0, 1.0, 1.0, 1.0),
        ]
        for stage in stages:
            if not self._running:
                break
            for i, t in enumerate(self.TERRITORIES):
                self.set_progress(t, stage[i] * 100)
            self.render()
            time.sleep(duration / len(stages))
        self._running = False

    def stop(self):
        self._running = False
