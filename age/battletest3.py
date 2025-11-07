#!/usr/bin/env python3
"""
Minimal skeleton for MedievAIl / MedievAIl-like project.

Features:
- Separation of logic (SimpleEngine) from view (PygameRenderer)
- CLI: headless or gui
- Large tilemap with camera and borders (default 120x120)
- Basic Unit class and two simple Generals: BrainDead and Daft
- Simple scenario generator (mirrored armies)
- Controls in GUI: pan, pause, speed, minimap

Extend:
- Replace damage model with AoE formulas
- Add unit types with proper stats
- Implement formations, pathfinding, Lanchester scenarios, tournament runner, save/load
"""

from functions import *
from classes import *
from renderer import *


import argparse
import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

try:
    import pygame
except Exception:
    pygame = None

# ---------- CONFIG ----------
TILE_SIZE = 24         # pixels per tile in GUI
SCREEN_W, SCREEN_H = 960, 640
MAP_W, MAP_H = 120, 120
FPS = 60
camera_speed = 8.0     # tiles per second
# ---------------------------

Vec2 = Tuple[int, int]

def clamp(v, a, b): return max(a, min(b, v))

# -------------------------
# CLI & main
# -------------------------
def parse_args():
    p = argparse.ArgumentParser(description="MedievAIl minimal prototype")
    p.add_argument("--headless", action="store_true", help="run headless (logic only)")
    p.add_argument("--seed", type=int, default=None, help="random seed")
    p.add_argument("--units", type=int, default=12, help="units per side for default scenario")
    return p.parse_args()

def run_headless(engine: SimpleEngine, generals: Dict[int, General], max_ticks=300.0):
    t=0.0; dt=0.2; step=0; start=time.time()
    while t<max_ticks:
        engine.step(dt, generals)
        t+=dt; step+=1
        p1 = engine.get_units_for_player(1)
        p2 = engine.get_units_for_player(2)
        if not p1 or not p2:
            winner = 2 if p2 else (1 if p1 else 0)
            print(f"Battle ended at t={t:.1f}s steps={step}. Winner: P{winner}")
            break
    else:
        print("Battle timed out (draw).")
    print(f"Simulation took {time.time()-start:.2f}s wall time. Engine ticks: {engine.tick:.2f}")
    print("Events:")
    for e in engine.events[-20:]:
        print("  ", e)

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
