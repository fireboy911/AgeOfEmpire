from Map import MAP_W, MAP_H
from typing import List, Dict
from Engine import SimpleEngine
from Scenario import square_scenario, chevron_scenario
import random
import curses
from Client import parse_args, run_headless
from Generals import DaftGeneral, BrainDeadGeneral

def main():
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    engine = SimpleEngine(w=MAP_W, h=MAP_H)
    square_scenario(engine)

    generals = {
        1: DaftGeneral(1),
        2: BrainDeadGeneral(2)
    }

    if args.headless or curses is None:
        if curses is None and not args.headless:
            print("curses not available, running headless simulation. Use --headless to silence this message.")
        run_headless(engine, generals, max_ticks=180.0)
        return

    # Terminal UI loop with option to reset scenario or switch view
    current_view = 'terminal'
    
    while True:
        if current_view == 'terminal':
            from TerminalRenderer import TerminalRenderer
            renderer = TerminalRenderer(engine, generals)
            action = renderer.run()
            
            if action == 'reset' or action == ('reset',):
                engine = SimpleEngine(w=MAP_W, h=MAP_H)
                square_scenario(engine)
                generals = {1: DaftGeneral(1), 2: BrainDeadGeneral(2)}
                continue
            elif action == 'switch_pygame' or action == ('switch_pygame',):
                current_view = 'pygame'
                print("Switching to PyGame view...")
                try:
                    import pygame
                except ImportError:
                    print("PyGame not available. Install with `pip install pygame`.")
                    break
            else:
                break
        
        elif current_view == 'pygame':
            try:
                from PyGameRenderer import PygameRenderer
                import pygame
                renderer = PygameRenderer(engine, generals)
                result = renderer.run()
                
                if result == 'switch_terminal':
                    current_view = 'terminal'
                    print("Switching to terminal view...")
                else:
                    break
            except Exception as e:
                print(f"PyGame view error: {e}")
                break

if __name__ == '__main__':
    main()


