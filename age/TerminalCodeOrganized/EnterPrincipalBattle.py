import argparse
import sys
import random
# Imports de vos modules existants
from Engine import SimpleEngine
from Generals import DaftGeneral, BrainDeadGeneral
from Scenario import spawn_asymmetric_armies 
from Map import MAP_W, MAP_H

def main():
    parser = argparse.ArgumentParser(description="MedievAIl Battle Simulator")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # --- Commande RUN ---
    run_parser = subparsers.add_parser('run', help='Lancer une bataille unique')
    run_parser.add_argument('--t', action='store_true', help='Mode Terminal (Curses)')
    run_parser.add_argument('--headless', action='store_true', help='Mode sans graphique (rapide)')
    run_parser.add_argument('--seed', type=int, help='Graine aléatoire', default=None)

    # --- Commande TOURNEY (A faire plus tard) ---
    tourney_parser = subparsers.add_parser('tourney', help='Lancer un tournoi')

    args = parser.parse_args()

    if args.command == 'run':
        start_battle(args)
    elif args.command == 'tourney':
        print("Mode tournoi pas encore implémenté.")
    else:
        parser.print_help()

def start_battle(args):
    if args.seed:
        random.seed(args.seed)

    # Initialisation Moteur
    engine = SimpleEngine(MAP_W, MAP_H)
    
    # Setup Scénario (Pour l'instant en dur, à rendre dynamique plus tard)
    spawn_asymmetric_armies(engine)

    # Setup Généraux
    generals = {
        1: DaftGeneral(1), 
        2: BrainDeadGeneral(2) # A remplacer par votre SmartGeneral plus tard
    }

    # Choix du Renderer
    if args.headless:
        from Client import run_headless
        run_headless(engine, generals)
    elif args.t:
        try:
            from TerminalRenderer import TerminalRenderer
            renderer = TerminalRenderer(engine, generals)
            renderer.run()
        except ImportError:
            print("Erreur: Impossible de lancer le mode terminal (curses manquant ?)")
    else:
        from PyGameRenderer import PygameRenderer
        renderer = PygameRenderer(engine, generals)
        renderer.run()

if __name__ == "__main__":
    main()