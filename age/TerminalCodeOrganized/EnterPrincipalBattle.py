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

    # Boucle principale pour permettre le "Reset" (Touche R)
    while True:
        # 1. Initialisation Moteur (Nouvelle instance à chaque reset)
        engine = SimpleEngine(MAP_W, MAP_H)
        
        # 2. Setup Scénario
        # Utilise votre fonction corrigée dans Scenario.py
        spawn_asymmetric_armies(engine) 

        # 3. Setup Généraux
        generals = {
            1: DaftGeneral(1), 
            2: BrainDeadGeneral(2) 
        }

        # 4. Lancement du Renderer choisi
        result = None
        
        if args.headless:
            from Client import run_headless
            run_headless(engine, generals)
            break # Pas de reset en headless
            
        elif args.t:
            # Mode Terminal
            try:
                from TerminalRenderer import TerminalRenderer
                renderer = TerminalRenderer(engine, generals)
                result = renderer.run() # C'est ici qu'on appelle votre méthode run() !
            except ImportError:
                print("Erreur: curses manquant.")
                break
                
        else:
            # Mode PyGame
            from PyGameRenderer import PygameRenderer
            renderer = PygameRenderer(engine, generals)
            renderer.run()
            # Pygame gère sa propre boucle, on sort après fermeture
            break

        # Si le renderer renvoie autre chose que 'reset', on quitte vraiment
        if result != 'reset' and result != ('reset',):
            break
        
        print("Relancement de la bataille...")

if __name__ == "__main__":
    main()