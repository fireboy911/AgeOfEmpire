from Client import parse_args
import pygame
from Generals import DaftGeneral, BrainDeadGeneral
from Engine import SimpleEngine
from Map import MAP_W, MAP_H
from random import random
from PyGameRenderer import PygameRenderer
from Scenario import spawn_asymmetric_armies
from Client import run_headless
import random

def main():
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    engine = SimpleEngine(w=MAP_W, h=MAP_H)

    # Spawn asymmetric armies (different formations for P1 and P2)
    spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)

    # Generals
    generals = {
        1: DaftGeneral(1),
        2: BrainDeadGeneral(2)
    }

    # Run simulation
    if args.headless:
        run_headless(engine, generals, max_ticks=180.0)
        return

    if pygame is None:
        print("Pygame not available. Install with `pip install pygame` or run with --headless.")
        return

    # Main loop supporting view switching
    current_view = 'pygame'
    
    while True:
        if current_view == 'pygame':
            renderer = PygameRenderer(engine, generals)
            result = renderer.run()
            
            if result == 'switch_terminal':
                current_view = 'terminal'
                print("Switching to terminal view...")
                # Import here to avoid issues if curses not available
                try:
                    from TerminalRenderer import TerminalRenderer
                except ImportError:
                    print("Terminal view not available on this system.")
                    break
            else:
                break
        
        elif current_view == 'terminal':
            try:
                from TerminalRenderer import TerminalRenderer
                renderer = TerminalRenderer(engine, generals)
                result = renderer.run()
                
                if result == 'switch_pygame' or result == ('switch_pygame',):
                    current_view = 'pygame'
                    print("Switching to PyGame view...")
                elif result == 'reset' or result == ('reset',):
                    # Reset the game
                    engine = SimpleEngine(w=MAP_W, h=MAP_H)
                    spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)
                    generals = {1: DaftGeneral(1), 2: BrainDeadGeneral(2)}
                    current_view = 'terminal'
                else:
                    break
            except Exception as e:
                print(f"Terminal view error: {e}")
                break


if __name__ == "__main__":
    main()
