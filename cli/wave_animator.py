"""Background wave animation thread for Keli terminal."""
import threading, time, sys, shutil

class WaveAnimator:
    """Animates a flowing wave across the terminal header."""

    WAVES = [
        '~≈≈~~≈≈≈~~≈≈~~≈≈≈~~',
        '≈~≈≈~≈≈≈~≈≈~≈≈≈~≈~',
        '≈≈~≈≈~≈≈≈≈~≈≈~≈≈≈~',
        '≈≈≈~≈≈≈~~≈≈≈~≈≈≈~~',
        '~~≈≈≈~≈≈≈~~≈≈≈~≈≈≈',
        '≈~~≈≈≈≈~≈≈≈~~≈≈≈≈~',
    ]

    COLORS = ['\033[96m', '\033[94m', '\033[36m', '\033[92m']

    def __init__(self):
        self.running = False
        self._thread = None
        self._idx = 0
        self._frame = 0

    def _animate(self):
        while self.running:
            wave = self.WAVES[self._frame % len(self.WAVES)]
            color = self.COLORS[(self._frame // 2) % len(self.COLORS)]
            width = shutil.get_terminal_size((80, 20)).columns
            line = f'{color}{wave:{width}}{' ' * (width - len(wave))}\033[0m'
            sys.stdout.write(f'\033[1;1H{line}')
            sys.stdout.flush()
            self._frame += 1
            time.sleep(0.3)

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1)

    def clear_line(self):
        sys.stdout.write('\033[K')
        sys.stdout.flush()
