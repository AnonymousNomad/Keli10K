"""Living nanobot swarm animation — helix, swarm, underwater bioluminescence."""
import threading, time, sys, shutil, random

C = lambda i: f'\033[{i}m'

class WaveAnimator:
    def __init__(self):
        self.running = False
        self._thread = None
        self._frame = 0
        self._nanobots = []
        self._init_swarm()

    def _init_swarm(self):
        for _ in range(20):
            self._nanobots.append({
                'x': random.uniform(0, 1), 'y': random.uniform(0, 1),
                'vx': random.uniform(-0.02, 0.02), 'vy': random.uniform(-0.02, 0.02),
                'char': random.choice(['◆', '◇', '•', '○', '◈', '✦', '⬡', '·']),
                'color': random.choice([36, 94, 96, 92, 95]),
                'pulse': random.uniform(0, 6.28),
                'active': random.choice([True, False]),
            })

    def _render_swarm_line(self, width, line_num, total_lines=3):
        h = 1.0 / total_lines
        y_pos = line_num * h + h/2
        chars = []
        for i in range(width):
            bots_here = [b for b in self._nanobots if abs(b['y'] - y_pos) < h/2 and abs(b['x'] - i/width) < 0.04]
            if bots_here:
                b = bots_here[0]
                intensity = 0.5 + 0.5 * math.sin(b['pulse'] + self._frame * 0.1)
                if b['active'] and random.random() < intensity:
                    chars.append(f'{C(b["color"])}{b["char"]}{C(0)}')
                else:
                    chars.append(f'{C(90)}·{C(0)}')
            else:
                dist = min((abs(b['x'] - i/width) + abs(b['y'] - y_pos)) for b in self._nanobots) if self._nanobots else 1
                if dist < 0.1:
                    chars.append(f'{C(90)}{random.choice([".","·"," "])}{C(0)}')
                else:
                    chars.append(' ')
        return ''.join(chars)

    def _render_dna_helix(self, width):
        chars = ['╱', '╲', '│', '╱', '╲', '│']
        c = chars[self._frame % len(chars)]
        colors = ['\033[36m', '\033[94m', '\033[96m', '\033[92m']
        color = colors[(self._frame // 2) % len(colors)]
        # Build a double helix strand
        helix_str = ''
        for i in range(0, min(width, 40), 2):
            pair = '╱╲' if (i // 2 + self._frame) % 4 < 2 else '╲╱'
            bot_here = random.choice(['◆', '◇', '•'])
            bot_color = random.choice(['\033[92m', '\033[96m', '\033[93m', '\033[95m'])
            helix_str += f'{color}{pair[0]}{bot_color}{bot_here}{color}{pair[1]}{C(0)}'
        return helix_str

    def _render_nanobot_bus(self, width):
        """Show nanobots communicating — moving dots with connection lines."""
        comms = []
        bot_pairs = [
            ('\033[96m◆\033[0m', '\033[92m◇\033[0m'),
            ('\033[95m⬡\033[0m', '\033[94m✦\033[0m'),
            ('\033[93m●\033[0m', '\033[96m○\033[0m'),
        ]
        pair = bot_pairs[self._frame % len(bot_pairs)]
        line = ''
        for i in range(min(width, 60)):
            r = random.random()
            if r < 0.01:
                line += f'\033[92m╱\033[0m'
            elif r < 0.02:
                line += f'\033[96m╲\033[0m'
            elif r < 0.03:
                line += random.choice(pair)
            elif r < 0.06:
                line += f'\033[90m~\033[0m'
            else:
                line += ' '
        return line

    def _animate(self):
        import math as m
        while self.running:
            width = shutil.get_terminal_size((80, 20)).columns
            t = self._frame * 0.1

            # Update nanobot positions
            for b in self._nanobots:
                b['x'] += b['vx'] + m.sin(t + b['pulse']) * 0.003
                b['y'] += b['vy'] + m.cos(t * 0.7 + b['pulse'] * 1.3) * 0.002
                b['x'] = b['x'] % 1.0
                b['y'] = max(0.0, min(1.0, b['y']))
                b['pulse'] += 0.05
                if random.random() < 0.01:
                    b['active'] = not b['active']
                if random.random() < 0.005:
                    b['char'] = random.choice(['◆', '◇', '•', '○', '◈', '✦', '⬡', '·'])

            # Line 1: Nanobot swarm row + DNA helix
            swarm1 = self._render_swarm_line(width, 0, 3)
            swarm1_pad = f'{swarm1:{width}}'

            # Line 2: DNA helix center + bot comms
            helix = self._render_dna_helix(width)
            comms = self._render_nanobot_bus(width)
            line2 = f'{helix} {comms}'
            line2_pad = f'{line2:{width}}'

            # Line 3: Bottom swarm + binary
            swarm3 = self._render_swarm_line(width, 2, 3)
            bits = ''.join(random.choice('01') for _ in range(8))
            wave = ''.join(random.choice(['~', '≈', '≈', '~', '·', '○', '°']) for _ in range(6))
            line3 = f'{swarm3}  {C(90)}{bits}{C(0)}  {C(96)}{wave}{C(0)}'
            line3_pad = f'{line3:{width}}'

            lines = [swarm1_pad, line2_pad, line3_pad]
            for i, line in enumerate(lines):
                sys.stdout.write(f'\033[{i+1};1H{line}')
            sys.stdout.flush()
            self._frame += 1
            time.sleep(0.15)

    def start(self):
        import math
        self.running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=1)

def clear_line():
    sys.stdout.write('\033[K')
    sys.stdout.flush()
