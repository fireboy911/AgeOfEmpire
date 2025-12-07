from Client import parse_args
import pygame
from Generals import DaftGeneral, BrainDeadGeneral
from Engine import SimpleEngine
from Map import MAP_W, MAP_H
from random import random
from PyGameRenderer import PygameRenderer
from Scenario import spawn_asymmetric_armies
from Client import run_headless

def main():
    args = parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    engine = SimpleEngine(w=MAP_W, h=MAP_H)

    # ----------------------
    # Spawn asymmetric armies (different formations for P1 and P2)
    # ----------------------
    spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)

    # ----------------------
    # Generals
    # ----------------------
    generals = {
        1: DaftGeneral(1),
        2: BrainDeadGeneral(2)
    }

    # ----------------------
    # Run simulation
    # ----------------------
    if args.headless:
        run_headless(engine, generals, max_ticks=180.0)
        return

    if pygame is None:
        print("Pygame not available. Install with `pip install pygame` or run with --headless.")
        return

    renderer = PygameRenderer(engine, generals)
    renderer.run()


if __name__ == "__main__":
    main()

