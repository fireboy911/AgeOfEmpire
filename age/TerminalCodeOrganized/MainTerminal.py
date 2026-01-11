import argparse
from Map import MAP_W, MAP_H
from typing import List, Dict
from Engine import SimpleEngine
from Scenario import square_scenario, chevron_scenario
import random
import curses
import time
from Generals import DaftGeneral, BrainDeadGeneral


def get_ai_class(ai_name: str):
    """Get AI class by name"""
    ai_map = {
        'DaftGeneral': DaftGeneral,
        'BrainDeadGeneral': BrainDeadGeneral
    }
    return ai_map.get(ai_name, DaftGeneral)


def get_scenario(scenario_name: str):
    """Get scenario function by name"""
    scenario_map = {
        'square_scenario': square_scenario,
        'chevron_scenario': chevron_scenario
    }
    return scenario_map.get(scenario_name, square_scenario)


def run_battle(engine: SimpleEngine, generals: Dict, terminal_view: bool = False, datafile: str = None):
    """Run a single battle and optionally save results to file"""
    t = 0.0
    dt = 0.2
    step = 0
    start = time.time()
    max_ticks = 180.0
    
    # Run the simulation
    while t < max_ticks:
        engine.step(dt, generals)
        t += dt
        step += 1
        p1 = engine.get_units_for_player(1)
        p2 = engine.get_units_for_player(2)
        if not p1 or not p2:
            winner = 2 if p2 else (1 if p1 else 0)
            break
    else:
        winner = 0  # Draw
    
    simulation_time = time.time() - start
    
    # Print results
    print(f"Battle ended at t={t:.1f}s steps={step}. Winner: P{winner}")
    print(f"Simulation took {simulation_time:.2f}s wall time. Engine ticks: {engine.tick:.2f}")
    print("Events:")
    for e in engine.events[-20:]:
        print("  ", e)
    
    # Save to file if specified
    if datafile is not None:
        with open(datafile, 'w') as f:
            f.write(f'Battle ended at t={t:.1f}s steps={step}. Winner: P{winner}\n')
            f.write(f'Simulation took {simulation_time:.2f}s wall time. Engine ticks: {engine.tick:.2f}\n')
            f.write('Events:\n')
            for event in engine.events:
                f.write(f'   {event}\n')
        print(f'\nBattle data successfully written to {datafile}')
    
    return winner, t, step, simulation_time


def main():
    parser = argparse.ArgumentParser(description='Battle simulation CLI')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # run command
    run_parser = subparsers.add_parser('run', help='Run a battle scenario')
    run_parser.add_argument('scenario', help='Scenario to run (square_scenario, chevron_scenario)')
    run_parser.add_argument('AI1', nargs='?', default='DaftGeneral', help='First AI (default: DaftGeneral)')
    run_parser.add_argument('AI2', nargs='?', default='BrainDeadGeneral', help='Second AI (default: BrainDeadGeneral)')
    run_parser.add_argument('-t', action='store_true', help='Terminal/headless view (default: 2.5D PyGame)')
    run_parser.add_argument('-d', type=str, help='Data file to save results')
    run_parser.add_argument('--seed', type=int, help='Random seed')

    # load command
    load_parser = subparsers.add_parser('load', help='Load a saved battle')
    load_parser.add_argument('savefile', help='Save file to load')

    # tourney command
    tourney_parser = subparsers.add_parser('tourney', help='Run a tournament')
    tourney_parser.add_argument('-G', nargs='+', default=['DaftGeneral', 'BrainDeadGeneral'], help='List of AIs')
    tourney_parser.add_argument('-S', nargs='+', default=['square_scenario'], help='List of scenarios')
    tourney_parser.add_argument('-N', type=int, default=10, help='Number of rounds per matchup')
    tourney_parser.add_argument('-na', action='store_true', help='Do not alternate positions')
    tourney_parser.add_argument('-d', type=str, help='Data file to save results')

    # plot command
    plot_parser = subparsers.add_parser('plot', help='Plot outcomes of a scenario with parameters')
    plot_parser.add_argument('AI', help='AI name (e.g., DAFT, BrainDead)')
    plot_parser.add_argument('plotter', help='Plotter type (e.g., PlotLanchester)')
    plot_parser.add_argument('scenario', help='Scenario name (e.g., Lanchester)')
    plot_parser.add_argument('units', nargs='+', help='Units to test in format: [Unit1,Unit2,...] or Unit1 Unit2 ...')
    plot_parser.add_argument('range_values', nargs='*', help='Range specification (e.g., range (1,100))')
    plot_parser.add_argument('-N', type=int, default=10, help='Number of rounds for each test')

    # view command (interactive PyGame)
    view_parser = subparsers.add_parser('view', help='View battle with interactive 2.5D/PyGame renderer')
    view_parser.add_argument('scenario', nargs='?', default='square_scenario', help='Scenario to view (square_scenario, chevron_scenario)')
    view_parser.add_argument('AI1', nargs='?', default='DaftGeneral', help='First AI')
    view_parser.add_argument('AI2', nargs='?', default='BrainDeadGeneral', help='Second AI')
    view_parser.add_argument('--seed', type=int, help='Random seed')

    args = parser.parse_args()

    # Handle run command
    if args.command == 'run':
        if args.seed is not None:
            random.seed(args.seed)
        
        print('Starting battle simulation...')
        engine = SimpleEngine(w=MAP_W, h=MAP_H)
        scenario_func = get_scenario(args.scenario)
        scenario_func(engine)
        
        AI1_class = get_ai_class(args.AI1)
        AI2_class = get_ai_class(args.AI2)
        generals = {
            1: AI1_class(1),
            2: AI2_class(2)
        }
        
        # If -t flag: run headless/terminal view
        if args.t:
            print('Running in terminal/headless mode...')
            run_battle(engine, generals, terminal_view=False, datafile=args.d)
        else:
            # Default: show 2.5D PyGame visualization
            print('Opening 2.5D map viewer...')
            try:
                import pygame
                from PyGameRenderer import PygameRenderer
                renderer = PygameRenderer(engine, generals)
                renderer.run()
                
                # Save data file if specified
                if args.d is not None:
                    winner, t, step, sim_time = 1, engine.tick, 0, 0  # Could enhance this
                    with open(args.d, 'w') as f:
                        f.write(f'Battle data saved from 2.5D view\n')
                        f.write(f'Engine ticks: {engine.tick:.2f}\n')
                        f.write('Events:\n')
                        for event in engine.events:
                            f.write(f'   {event}\n')
                    print(f'Battle data saved to {args.d}')
            except ImportError:
                print("PyGame not available. Install with: pip install pygame")
                print("Falling back to terminal view...")
                run_battle(engine, generals, terminal_view=False, datafile=args.d)
            except Exception as e:
                print(f"Error running PyGame viewer: {e}")
                print("Falling back to terminal view...")
                run_battle(engine, generals, terminal_view=False, datafile=args.d)

    # Handle load command
    elif args.command == 'load':
        print(f"Loading battle from {args.savefile}...")
        # TODO: Implement save/load functionality
        print("Load functionality not yet implemented")

    # Handle tourney command
    elif args.command == 'tourney':
        print(f"Running tournament with {len(args.G)} AIs, {len(args.S)} scenarios, {args.N} rounds each")
        print(f"AIs: {', '.join(args.G)}")
        print(f"Scenarios: {', '.join(args.S)}")
        print(f"Alternate positions: {not args.na}")
        
        results = {}
        total_matches = 0
        
        for scenario_name in args.S:
            for i, ai1 in enumerate(args.G):
                for ai2 in args.G[i+1:]:
                    matchup = f"{ai1} vs {ai2} ({scenario_name})"
                    results[matchup] = {'ai1_wins': 0, 'ai2_wins': 0, 'draws': 0}
                    
                    for round_num in range(args.N):
                        engine = SimpleEngine(w=MAP_W, h=MAP_H)
                        scenario_func = get_scenario(scenario_name)
                        scenario_func(engine)
                        
                        # Create generals
                        if args.na or round_num % 2 == 0:
                            generals = {
                                1: get_ai_class(ai1)(1),
                                2: get_ai_class(ai2)(2)
                            }
                            p1_ai, p2_ai = ai1, ai2
                        else:
                            generals = {
                                1: get_ai_class(ai2)(1),
                                2: get_ai_class(ai1)(2)
                            }
                            p1_ai, p2_ai = ai2, ai1
                        
                        winner, t, step, sim_time = run_battle(engine, generals, datafile=None)
                        
                        if winner == 0:
                            results[matchup]['draws'] += 1
                        elif winner == 1:
                            if p1_ai == ai1:
                                results[matchup]['ai1_wins'] += 1
                            else:
                                results[matchup]['ai2_wins'] += 1
                        else:
                            if p2_ai == ai1:
                                results[matchup]['ai1_wins'] += 1
                            else:
                                results[matchup]['ai2_wins'] += 1
                        
                        total_matches += 1
        
        print(f"\nTournament Results ({total_matches} matches):")
        for matchup, stats in results.items():
            print(f"{matchup}: {stats['ai1_wins']}-{stats['ai2_wins']}-{stats['draws']}")
        
        # Save to file if specified
        if args.d is not None:
            with open(args.d, 'w') as f:
                f.write(f"Tournament Results ({total_matches} matches):\n")
                for matchup, stats in results.items():
                    f.write(f"{matchup}: {stats['ai1_wins']}-{stats['ai2_wins']}-{stats['draws']}\n")
            print(f"\nTournament results saved to {args.d}")

    # Handle plot command
    elif args.command == 'plot':
        # Parse the range specification (e.g., "range (1,100)")
        range_str = ' '.join(args.range_values) if args.range_values else ''
        print(f"Plotting {args.AI} with {args.plotter} on scenario {args.scenario}")
        print(f"Units: {', '.join(args.units)}")
        if range_str:
            print(f"Range: {range_str}")
        print(f"Rounds per test: {args.N}")
        print("Plot functionality not yet implemented")

    # Handle view command
    elif args.command == 'view':
        if args.seed is not None:
            random.seed(args.seed)
        
        print('Starting interactive battle simulation with PyGame viewer...')
        engine = SimpleEngine(w=MAP_W, h=MAP_H)
        scenario_func = get_scenario(args.scenario)
        scenario_func(engine)
        
        AI1_class = get_ai_class(args.AI1)
        AI2_class = get_ai_class(args.AI2)
        generals = {
            1: AI1_class(1),
            2: AI2_class(2)
        }
        
        try:
            import pygame
            from PyGameRenderer import PygameRenderer
            renderer = PygameRenderer(engine, generals)
            renderer.run()
        except ImportError:
            print("PyGame not available. Install with: pip install pygame")
        except Exception as e:
            print(f"Error running PyGame viewer: {e}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
