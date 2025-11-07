# -------------------------
# Core logic classes
# -------------------------

from battletest3 import *
from functions import *
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

@dataclass
class Unit:
    id: int
    player: int
    x: float
    y: float
    hp: float = 50.0
    attack: float = 6.0
    range: float = 1.0
    speed: float = 1.0
    alive: bool = True
    target_id: Optional[int] = None
    regen: float = 0.0
    unit_type: str = "infantry"
    color: Optional[Tuple[int,int,int]] = None  # will be set in __post_init__

    def __post_init__(self):
        """Automatically assign colors based on unit type if not set."""
        type_colors = {
            "infantry": (200, 50, 50),
            "archer": (255, 200, 50),
            "knight": (180, 180, 180),
            "mage": (120, 50, 200),
            "healer": (50, 200, 120)
        }
        if self.color is None:
            self.color = type_colors.get(self.unit_type, (255, 255, 255))

    def distance_to(self, other: "Unit") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def step(self, dt: float, engine: "SimpleEngine"):
        if not self.alive:
            return
        # optional HP regen
        if self.regen > 0:
            self.hp = min(self.hp + self.regen * dt, 55)

        if self.target_id is not None:
            target = engine.units_by_id.get(self.target_id)
            if target is None or not target.alive:
                self.target_id = None
            else:
                d = self.distance_to(target)
                if d <= self.range + 0.1:
                    damage = self.attack * dt
                    target.hp -= damage
                    if target.hp <= 0:
                        target.alive = False
                        target.hp = 0
                        engine.mark_dead(target)
                else:
                    dx = target.x - self.x
                    dy = target.y - self.y
                    dist = math.hypot(dx, dy)
                    if dist > 1e-6:
                        nx = dx / dist
                        ny = dy / dist
                        self.x += nx * self.speed * dt
                        self.y += ny * self.speed * dt


@dataclass
class SimpleEngine:
    w: int = MAP_W
    h: int = MAP_H
    units: List[Unit] = field(default_factory=list)
    units_by_id: Dict[int, Unit] = field(default_factory=dict)
    next_unit_id: int = 1
    tick: float = 0.0
    events: List[str] = field(default_factory=list)

    def spawn_unit(self, player: int, x: float, y: float, **kwargs) -> Unit:
        u = Unit(id=self.next_unit_id, player=player, x=x, y=y, **kwargs)
        self.next_unit_id += 1
        self.units.append(u)
        self.units_by_id[u.id] = u
        return u

    def step(self, dt: float, generals: Dict[int, "General"]):
        self.tick += dt
        for pid, gen in generals.items():
            gen.give_orders(self)
        for u in list(self.units):
            if u.alive:
                u.step(dt, self)
        self.units = [u for u in self.units if u.alive]
        self.units_by_id = {u.id: u for u in self.units}

    def mark_dead(self, unit: Unit):
        self.events.append(f"Unit {unit.id} (P{unit.player}) died at tick {self.tick:.2f}")

    def get_units_for_player(self, player: int) -> List[Unit]:
        return [u for u in self.units if u.player == player and u.alive]

# -------------------------
# Generals (AI)
# -------------------------
class General:
    def __init__(self, player: int):
        self.player = player
    def give_orders(self, engine: SimpleEngine):
        raise NotImplementedError

class BrainDeadGeneral(General):
    def give_orders(self, engine: SimpleEngine):
        my_units = engine.get_units_for_player(self.player)
        for u in my_units:
            # If this unit is already attacking someone, keep going
            if u.target_id is not None and u.target_id in engine.units_by_id:
                continue
            # If this unit was attacked, target its attacker (closest enemy)
            enemies = [e for e in engine.units if e.player != self.player and e.alive]
            if not enemies:
                return
            # Only react if someone is within aggro range (say 5 tiles)
            nearby = [e for e in enemies if u.distance_to(e) < 5.0]
            if nearby:
                target = min(nearby, key=lambda e: u.distance_to(e))
                u.target_id = target.id

class DaftGeneral(General):
    def give_orders(self, engine: SimpleEngine):
        my_units = engine.get_units_for_player(self.player)
        enemy_units = [u for u in engine.units if u.player != self.player and u.alive]
        if not enemy_units:
            return
        for u in my_units:
            if u.target_id is not None and u.target_id in engine.units_by_id:
                continue
            nearest = min(enemy_units, key=lambda e: u.distance_to(e))
            u.target_id = nearest.id
