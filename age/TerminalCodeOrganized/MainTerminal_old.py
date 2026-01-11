import argparse
from Map import MAP_W, MAP_H
from typing import List, Dict
from Engine import SimpleEngine
from Scenario import square_scenario, chevron_scenario
import random
import curses
from Client import run_headless
from Generals import DaftGeneral, BrainDeadGeneral

def main():
    parser = argparse.ArgumentParser(description='Battle simulation commands.')
    subparsers = parser.add_subparsers(dest='command')

    # Subparser for running a battle
    run_parser = subparsers.add_parser('run', help='Run a battle scenario.')
    run_parser.add_argument('scenario', type=str, help='The scenario to run.')
    run_parser.add_argument('AI1', type=str, help='First AI to use.')
    run_parser.add_argument('AI2', type=str, help='Second AI to use.')
    run_parser.add_argument('-t', action='store_true', help='Launch terminal view instead of 2.5D.')
    run_parser.add_argument('-d', type=str, help='Data file to write battle data.')

    # Subparser for loading a save
    load_parser = subparsers.add_parser('load', help='Load a saved battle.')
    load_parser.add_argument('savefile', type=str, help='The save file to load.')

    # Subparser for tournaments
    tourney_parser = subparsers.add_parser('tourney', help='Run an automatic tournament.')
    tourney_parser.add_argument('-G', nargs='*', help='List of AIs to use.')
    tourney_parser.add_argument('-S', nargs='*', help='List of scenarios to use.')
    tourney_parser.add_argument('-N', type=int, default=10, help='Number of rounds for each matchup.')
    tourney_parser.add_argument('-na', type=bool, default=False, help='Do not alternate player position across N matches.')

    # Subparser for plotting outcomes
    plot_parser = subparsers.add_parser('plot', help='Plot outcomes of a scenario.')
    plot_parser.add_argument('AI', type=str, help='AI to plot.')
    plot_parser.add_argument('plotter', type=str, help='Plotter to use.')
    plot_parser.add_argument('scenario', nargs='+', help='Scenarios to plot.')
    plot_parser.add_argument('range', type=str, help='Range for parameters.')
    plot_parser.add_argument('-N', type=int, default=10, help='Number of rounds for each matchup.')

    args = parser.parse_args()

    if args.command == 'run':
        # Check if seed argument is provided
        if hasattr(args, 'seed') and args.seed is not None:
            random.seed(args.seed)

        engine = SimpleEngine(w=MAP_W, h=MAP_H)
        square_scenario(engine)

        generals = {
            1: DaftGeneral(1),
            2: BrainDeadGeneral(2)
        }

        if args.t or curses is None:
            if curses is None and not args.t:
                print("curses not available, running headless simulation. Use --headless to silence this message.")
            print('Starting battle simulation...')
            
            # Run headless simulation and capture results
            import time
            t = 0.0
            dt = 0.2
            step = 0
            start = time.time()
            max_ticks = 180.0
            
            while t < max_ticks:
                engine.step(dt, generals)
                t += dt
                step += 1
                p1 = engine.get_units_for_player(1)
                p2 = engine.get_units_for_player(2)
                if not p1 or not p2:
                    winner = 2 if p2 else (1 if p1 else 0)
                    print(f"Battle ended at t={t:.1f}s steps={step}. Winner: P{winner}")
                    break
            else:
                winner = 0  # Draw
                print("Battle timed out (draw).")
            
            simulation_time = time.time() - start
            print(f"Simulation took {simulation_time:.2f}s wall time. Engine ticks: {engine.tick:.2f}")
            print("Events:")
            for e in engine.events[-20:]:
                print("  ", e)
            
            # Write battle data to the specified file if -d is provided
            if args.d is not None:
                print(f'\nWriting battle data to {args.d}')
                with open(args.d, 'w') as datafile:
                    datafile.write(f'Battle ended at t={t:.1f}s steps={step}. Winner: P{winner}\n')
                    datafile.write(f'Simulation took {simulation_time:.2f}s wall time. Engine ticks: {engine.tick:.2f}\n')
                    datafile.write('Events:\n')
                    for event in engine.events:
                        datafile.write(f'   {event}\n')
                print(f'Battle data successfully written to {args.d}')
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


