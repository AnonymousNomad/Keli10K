"""Interactive mode selector for Keli terminal."""
import sys

class ModeSelector:
    MODES = {'1': 'plan', '2': 'build', '3': 'tutor', '4': 'train',
             'plan': 'plan', 'build': 'build', 'tutor': 'tutor', 'train': 'train'}

    WELCOME = (
        '\033[96m┌─────────────────────────────────────────────┐\033[0m\n'
        '\033[96m│  \033[93m◢◣\033[0m  \033[1;96mKELI SOVEREIGN TERMINAL v2.0\033[0m       \033[96m│\033[0m\n'
        '\033[96m│  \033[94m◆\033[0m   10,000 Nanobots Online                 \033[96m│\033[0m\n'
        '\033[96m│  \033[92m≈\033[0m   \033[1;93m[1]PLAN\033[0m \033[1;94m[2]BUILD\033[0m \033[1;92m[3]TUTOR\033[0m \033[1;95m[4]TRAIN\033[0m        \033[96m│\033[0m\n'
        '\033[96m│  \033[95m~\033[0m   Type \033[1mhelp\033[0m or select a mode              \033[96m│\033[0m\n'
        '\033[96m│  \033[90m☕\033[0m   \033[90mdonate — support the swarm\033[0m            \033[96m│\033[0m\n'
        '\033[96m└─────────────────────────────────────────────┘\033[0m'
    )

    @staticmethod
    def get_mode():
        while True:
            sys.stdout.write('\033[36mkeli@sovereign:\033[0m\033[1;96m~\033[0m$ Select mode [1-4]: ')
            sys.stdout.flush()
            choice = sys.stdin.readline().strip().lower()
            if choice in ModeSelector.MODES:
                return ModeSelector.MODES[choice]
            if choice in ('exit', 'quit', 'q'):
                print('\033[33mShutting down swarm...\033[0m')
                sys.exit(0)
            if choice in ('donate', 'sponsor'):
                print('\n  \033[96m☕\033[0m https://ko-fi.com/ferrellsi')
                print('  \033[95m💖\033[0m https://github.com/sponsors/AnonymousNomad')
                print('  \033[90mNo pressure. Keli is free either way.\033[0m\n')
                continue
            print('\033[33mEnter 1 (plan), 2 (build), 3 (tutor), 4 (train), or donate.\033[0m')
