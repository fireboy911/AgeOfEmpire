# -------------------------
# Scenario generator
# -------------------------
# -------------------------
# New placement helpers (asymmetric formations)
# -------------------------

from battletest3 import *
from classes import *
from renderer import *

import argparse
import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict


# ---------- CONFIG ----------
TILE_SIZE = 24         # pixels per tile in GUI
SCREEN_W, SCREEN_H = 960, 640
MAP_W, MAP_H = 120, 120
FPS = 60
camera_speed = 8.0     # tiles per second
# ---------------------------

def _unit_defaults():
    return {"hp": 55, "attack": 6, "range": 1.0, "speed": 1.5}

def _clamp_pos(x, y, engine):
    x = clamp(x, 0, engine.w - 1)
    y = clamp(y, 0, engine.h - 1)
    return x, y

def spawn_grid(engine: SimpleEngine, player: int, rows=3, cols=6, spacing=1.5, anchor_offset=8.0, unit_kwargs=None):
    mid_x = engine.w / 2
    mid_y = engine.h / 2
    unit_kwargs = {**_unit_defaults(), **(unit_kwargs or {})}
    # side_dir = direction toward the center (player1 faces right => +1, player2 faces left => -1)
    side_dir = 1 if player == 1 else -1
    anchor_x = mid_x - anchor_offset if player == 1 else mid_x + anchor_offset
    for r in range(rows):
        for c in range(cols):
            x = anchor_x - c * spacing * side_dir
            y = mid_y + (r - (rows - 1) / 2.0) * spacing
            x, y = _clamp_pos(x, y, engine)
            engine.spawn_unit(player=player, x=x, y=y, **unit_kwargs)

def spawn_wedge(engine: SimpleEngine, player: int, rows=3, spacing=1.5, anchor_offset=8.0, unit_kwargs=None):
    """
    Triangle/wedge pointing toward the enemy.
    Row 0 = apex (closest to enemy), row i has (1 + 2*i) units centered vertically.
    """
    mid_x = engine.w / 2
    mid_y = engine.h / 2
    unit_kwargs = {**_unit_defaults(), **(unit_kwargs or {})}
    side_dir = 1 if player == 1 else -1
    anchor_x = mid_x - anchor_offset if player == 1 else mid_x + anchor_offset
    for r in range(rows):
        x = anchor_x - r * spacing * side_dir   # rows go backward away from the enemy
        for c in range(-r, r + 1):
            y = mid_y + c * spacing
            xx, yy = _clamp_pos(x, y, engine)
            engine.spawn_unit(player=player, x=xx, y=yy, **unit_kwargs)

def spawn_scatter(engine: SimpleEngine, player: int, count=12, area_w=6.0, area_h=6.0, anchor_offset=8.0, unit_kwargs=None):
    """Random scatter rectangle near the side."""
    mid_x = engine.w / 2
    mid_y = engine.h / 2
    unit_kwargs = {**_unit_defaults(), **(unit_kwargs or {})}
    anchor_x = mid_x - anchor_offset if player == 1 else mid_x + anchor_offset
    half_w = area_w / 2.0
    half_h = area_h / 2.0
    for _ in range(count):
        x = anchor_x + random.uniform(-half_w, half_w)
        y = mid_y + random.uniform(-half_h, half_h)
        x, y = _clamp_pos(x, y, engine)
        engine.spawn_unit(player=player, x=x, y=y, **unit_kwargs)

def spawn_circle(engine: SimpleEngine, player: int, count=12, radius=4.0, anchor_offset=8.0, unit_kwargs=None):
    """Units arranged in a circle around anchor point (useful for defensive group)."""
    mid_x = engine.w / 2
    mid_y = engine.h / 2
    unit_kwargs = {**_unit_defaults(), **(unit_kwargs or {})}
    anchor_x = mid_x - anchor_offset if player == 1 else mid_x + anchor_offset
    anchor_y = mid_y
    for i in range(count):
        ang = (2 * math.pi * i) / count
        x = anchor_x + math.cos(ang) * radius
        y = anchor_y + math.sin(ang) * radius
        x, y = _clamp_pos(x, y, engine)
        engine.spawn_unit(player=player, x=x, y=y, **unit_kwargs)

# Generic dispatcher
def spawn_formation(engine: SimpleEngine, player: int, formation: str, **kwargs):
    formation = formation.lower()
    if formation == "grid":
        spawn_grid(engine, player, **kwargs)
    elif formation == "wedge":
        spawn_wedge(engine, player, **kwargs)
    elif formation in ("scatter", "random"):
        spawn_scatter(engine, player, **kwargs)
    elif formation == "circle":
        spawn_circle(engine, player, **kwargs)
    else:
        raise ValueError(f"Unknown formation: {formation}")

# Top-level convenience function: put player1 on left formation A and player2 on B
def mirrored_asymmetric(engine: SimpleEngine,
                        left_formation=("grid", {}),   # for player 1
                        right_formation=("wedge", {}), # for player 2
                        ):
    fmt1, params1 = left_formation
    fmt2, params2 = right_formation
    spawn_formation(engine, player=1, formation=fmt1, **(params1 or {}))
    spawn_formation(engine, player=2, formation=fmt2, **(params2 or {}))

def spawn_asymmetric_armies(engine: "SimpleEngine", left_offset=10, right_offset=10):
    mid_x = engine.w / 2
    mid_y = engine.h / 2

    # --- Define stats per unit type ---
    type_stats = {
        "infantry": {"hp": 55, "attack": 6, "range": 1.0, "speed": 1.0},
        "archer":   {"hp": 40, "attack": 12, "range": 4.0, "speed": 1.0},
        "knight":   {"hp": 70, "attack": 8, "range": 1.0, "speed": 1.5},
    }

    # --- Define per-player colors ---
    type_colors = {
        1: {  # Player 1
            "infantry": (255, 100, 50),   # orange/red
            "archer":   (255, 50, 50),    # red
            "knight":   (200, 0, 0),      # dark red
        },
        2: {  # Player 2
            "infantry": (50, 150, 255),   # blue-ish
            "archer":   (100, 200, 255),  # light blue
            "knight":   (0, 100, 255),    # dark blue
        }
    }

    # --------------------------
    # Player 1: left side
    side_dir = 1
    anchor_x = mid_x - left_offset

    # Front: knights
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y 
        unit_type = "knight"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # Middle: infantry
    for row in range(3):
       for i in range(-row, row+1, 2):  # number of units increases each row
        x = anchor_x - row * 4 * side_dir
        y = mid_y + i
        engine.spawn_unit(player=1, x=x, y=y, unit_type="infantry", 
                          color=type_colors[1]["infantry"], **type_stats["infantry"])

        unit_type = "infantry"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # Back: archers
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "archer"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # --------------------------
    # Player 2: right side
    side_dir = -1
    anchor_x = mid_x + right_offset

    # Front: archers
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y - 2
        unit_type = "archer"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

    # Middle: knights
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y
        unit_type = "knight"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

    # Back: infantry
    for i in range(5):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "infantry"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])