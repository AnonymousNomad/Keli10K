"""Sovereign terminal mode selector — DNA helix + underwater + Parrot-style tree."""
import sys

class ModeSelector:
    MODES = {'1': 'plan', '2': 'build', '3': 'tutor', '4': 'train',
             'plan': 'plan', 'build': 'build', 'tutor': 'tutor', 'train': 'train'}

    # Parrot OS-style tree with Keli's DNA helix + underwater twist
    WELCOME = (
        '\033[36m┌─────────────────────────────────────────────────────────────┐\033[0m\n'
        '\033[36m│  \033[95m◇\033[0m  \033[1;96mFSI — KELI SOVEREIGN v2.0\033[0m                   \033[36m│\033[0m\n'
        '\033[36m│  \033[94m╱╲\033[0m  \033[90m10,000 nanobots · DNA-swarm core\033[0m            \033[36m│\033[0m\n'
        '\033[36m│  \033[92m├─\033[0m  \033[1;93m[1] PLAN\033[0m   \033[93m≈\033[0m  Coding Q&A with nanobot confidence     \033[36m│\033[0m\n'
        '\033[36m│  \033[92m├─\033[0m  \033[1;94m[2] BUILD\033[0m  \033[96m≈\033[0m  Multi-file project generation            \033[36m│\033[0m\n'
        '\033[36m│  \033[92m├─\033[0m  \033[1;95m[3] TUTOR\033[0m  \033[95m≈\033[0m  Interactive coding lessons + certificates \033[36m│\033[0m\n'
        '\033[36m│  \033[92m├─\033[0m  \033[1;97m[4] TRAIN\033[0m  \033[97m≈\033[0m  Keli as teacher — train your own model    \033[36m│\033[0m\n'
        '\033[36m│  \033[92m│\033[0m                                         \033[36m│\033[0m\n'
        '\033[36m│  \033[90m├── 0101  ·.·.·.  ~≈≈~~  ◇  \033[0m              \033[36m│\033[0m\n'
        '\033[36m│  \033[90m└── donate — support the swarm \033[95m☕\033[0m          \033[36m│\033[0m\n'
        '\033[36m└─────────────────────────────────────────────────────────────┘\033[0m'
    )

    @staticmethod
    def get_mode():
        while True:
            sys.stdout.write('\033[92m└──╼ \033[0m\033[1;96mSelect mode\033[0m \033[90m[1-4]\033[0m\033[92m:\033[0m ')
            sys.stdout.flush()
            choice = sys.stdin.readline().strip().lower()
            if choice in ModeSelector.MODES:
                return ModeSelector.MODES[choice]
            if choice in ('exit', 'quit', 'q'):
                print('\n\033[93m╲╱  Shutting down swarm... ◇\033[0m')
                sys.exit(0)
            if choice in ('donate', 'sponsor'):
                print('\n  \033[96m◇\033[0m \033[95mFSI / Keli\033[0m — Free. Open. Sovereign.')
                print('  \033[96m☕\033[0m https://ko-fi.com/ferrellsi')
                print('  \033[95m💖\033[0m https://github.com/sponsors/AnonymousNomad\n')
                continue
            print('\033[93m  Enter 1 (plan), 2 (build), 3 (tutor), 4 (train), or donate.\033[0m')
