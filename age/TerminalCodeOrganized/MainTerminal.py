from Map import MAP_W, MAP_H
from typing import List, Dict
from Engine import SimpleEngine
from Scenario import spawn_asymmetric_armies
from TerminalRenderer import TerminalRenderer
import random
import curses
from Client import parse_args, run_headless
from Generals import DaftGeneral, BrainDeadGeneral
def main():
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    engine = SimpleEngine(w=MAP_W, h=MAP_H)
    spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)

    generals = {
        1: DaftGeneral(1),
        2: BrainDeadGeneral(2)
    }

    if args.headless or curses is None:
        if curses is None and not args.headless:
            print("curses not available, running headless simulation. Use --headless to silence this message.")
        run_headless(engine, generals, max_ticks=180.0)
        return

    # Terminal UI loop with option to reset scenario
    while True:
        renderer = TerminalRenderer(engine, generals)
        action = renderer.run()
        # action is tuple returned by wrapper; wrapper returns the return value of run_curses
        if action == 'reset' or action == ('reset',):
            engine = SimpleEngine(w=MAP_W, h=MAP_H)
            spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)
            generals = {1: DaftGeneral(1), 2: BrainDeadGeneral(2)}
            continue
        else:
            break

if __name__ == '__main__':
    main()