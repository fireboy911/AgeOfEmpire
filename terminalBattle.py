#!/usr/bin/env python3
"""
Terminal-playable version of the provided Age of Empires II-like simulator.

This keeps the same classes and variables (Unit, SimpleEngine, Generals,
spawn_asymmetric_armies, etc.) but adds a curses-based terminal renderer
so you can *play* in the terminal.

Controls (in the terminal UI):
  - Arrow keys / WASD : pan camera
  - Tab              : select next unit (your units, player 1)
  - t                : set selected unit's target to nearest enemy
  - p or SPACE       : pause / unpause
  - + / =            : speed x2
  - - / _            : speed /2 (min 0.125)
  - q                : quit
  - r                : reset scenario

Run: python3 aoe2_terminal_sim.py
If curses is not available, the script falls back to a simple headless run.
"""

import argparse
import random
import math
import time
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

try:
    import curses
    from curses import wrapper
except Exception:
    curses = None

# ---------- CONFIG (kept from original) ----------
TILE_SIZE = 24         # unused by terminal renderer but kept for parity
SCREEN_W, SCREEN_H = 960, 640
MAP_W, MAP_H = 60, 60
FPS = 20
camera_speed = 10.0    # tiles per second for terminal panning
# -------------------------------------------------

Vec2 = Tuple[int, int]

def clamp(v, a, b): return max(a, min(b, v))

# -------------------------
# Core logic classes
# -------------------------
@dataclass
class Unit:
    id: int
    player: int
    x: float
    y: float
    hp: float = 0.0
    attack: float = 50.0
    range: float = 1.0
    speed: float = 1.0
    alive: bool = True
    target_id: Optional[int] = None
    regen: float = 0.0
    unit_type: str = "Pikeman*"
    color: Optional[Tuple[int,int,int]] = None  # unused by curses but kept

    def __post_init__(self):
        type_colors = {
            "Pikeman*": (200, 50, 50),
            "Crossbowman": (255, 200, 50),
            "knight": (180, 180, 180),
            "mage": (120, 50, 200),
            "Monk": (50, 200, 120)
        }
        if self.color is None:
            self.color = type_colors.get(self.unit_type, (255, 255, 255))

    def distance_to(self, other: "Unit") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def step(self, dt: float, engine: "SimpleEngine"):
        if not self.alive:
            return

        if self.regen > 0:
            self.hp = min(self.hp + self.regen * dt, 55)

        # Monk healing behavior
        if self.unit_type == "Monk":
            heal_range = self.range
            heal_power = self.attack * dt * 2
            allies = [a for a in engine.units if a.player == self.player and a.alive and a.hp < 55]
            if not allies:
                return
            target = min(allies, key=lambda a: self.distance_to(a))
            dist = self.distance_to(target)
            if dist <= heal_range:
                target.hp = min(target.hp + heal_power, 55)
            else:
                dx = target.x - self.x
                dy = target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 1e-6:
                    nx = dx / dist
                    ny = dy / dist
                    self.x += nx * self.speed * dt
                    self.y += ny * self.speed * dt
            return

        # normal combat logic
        target = None
        if self.target_id is not None:
            target = engine.units_by_id.get(self.target_id)

        if target is None or not target.alive:
            self.target_id = None
            return

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
        # Ensure hp default if not passed
        if u.hp == 0.0:
            u.hp = kwargs.get('hp', 55)
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
# Generals (same as original)
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
            if u.target_id is not None and u.target_id in engine.units_by_id:
                continue
            enemies = [e for e in engine.units if e.player != self.player and e.alive]
            if not enemies:
                return
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

# -------------------------
# Scenario generator (same but ensures hp supplied)
# -------------------------

def spawn_asymmetric_armies(engine: "SimpleEngine", left_offset=10, right_offset=10):
    mid_x = engine.w / 2
    mid_y = engine.h / 2

    type_stats = {
        "Pikeman": {"hp": 55, "attack": 6, "range": 1.0, "speed": 1.0},
        "Crossbowman":{"hp": 40, "attack": 12, "range": 5.0, "speed": 1.0},
        "knight": {"hp": 70, "attack": 8, "range": 1.2, "speed": 1.5},
        "Monk": {"hp": 55, "attack": 1.5, "range": 5.0, "speed": 1.0, "regen": 2.0},
    }

    type_colors = {
        1: {  # Player 1
            "Pikeman": (255, 100, 50),
            "Crossbowman": (255, 50, 50),
            "knight": (200, 0, 0),
            "Monk": (255, 150, 100),
        },
        2: {  # Player 2
            "Pikeman": (50, 150, 255),
            "Crossbowman": (100, 200, 255),
            "knight": (0, 100, 255),
            "Monk": (150, 200, 255),
        }
    }

    # Player 1 left
    side_dir = 1
    anchor_x = mid_x - left_offset
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + i
        unit_type = "knight"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])
    for row in range(3):
       for i in range(-row, row+1, 2):
        x = anchor_x - row * 4 * side_dir
        y = mid_y + i
        engine.spawn_unit(player=1, x=x, y=y, unit_type="Pikeman*", 
                          color=type_colors[1]["Pikeman"], **type_stats["Pikeman"])
        unit_type = "Pikeman"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "Crossbowman"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])
    for i in range(2):
        x = anchor_x - i * 6 * side_dir
        y = mid_y - 3 + i * 6
        unit_type = "Monk"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # Player 2 right
    side_dir = -1
    anchor_x = mid_x + right_offset
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y - 2
        unit_type = "Crossbowman"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y
        unit_type = "knight"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])
    for i in range(5):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "Pikeman"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])
    for i in range(2):
        x = anchor_x - i * 6 * side_dir
        y = mid_y - 3 + i * 6
        unit_type = "Monk"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

# -------------------------
# Terminal renderer using curses
# -------------------------
class TerminalRenderer:
    def __init__(self, engine: SimpleEngine, generals: Dict[int, General]):
        if curses is None:
            raise RuntimeError("curses not available on this system")
        self.engine = engine
        self.generals = generals
        self.cam_x = max(0, engine.w//2 - 20)
        self.cam_y = max(0, engine.h//2 - 10)
        self.speed_multiplier = 1.0
        self.paused = False
        self.selected_idx = 0
        self.last_time = time.time()

    def unit_char(self, u: Unit) -> str:
        if u.unit_type.lower().startswith('pik'):
            return 'P'
        if u.unit_type.lower().startswith('cross'):
            return 'C'
        if u.unit_type.lower().startswith('knight'):
            return 'K'
        if u.unit_type.lower().startswith('monk'):
            return 'M'
        return '?'

    def draw(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        view_w = max(10, w-2)
        view_h = max(6, h-6)

        # draw grid background (simple dots)
        for yy in range(view_h):
            row = []
            for xx in range(view_w):
                row.append('.')
            stdscr.addstr(1+yy, 1, ''.join(row))

        # draw units
        for u in self.engine.units:
            ux = int(u.x) - int(self.cam_x)
            uy = int(u.y) - int(self.cam_y)
            if 0 <= ux < view_w and 0 <= uy < view_h:
                ch = self.unit_char(u)
                if u.player == 1:
                    attr = curses.A_BOLD
                else:
                    attr = curses.A_DIM
                # highlight selected
                selected = False
                if self.engine.get_units_for_player(1):
                    my_units = self.engine.get_units_for_player(1)
                    if 0 <= self.selected_idx < len(my_units) and my_units[self.selected_idx].id == u.id:
                        attr |= curses.A_REVERSE
                        selected = True
                try:
                    stdscr.addch(1+uy, 1+ux, ch, attr)
                except curses.error:
                    pass
                # draw tiny hp above if selected
                if selected:
                    hp_text = f"{int(u.hp)}/{int(55)}"
                    try:
                        stdscr.addstr(0, 1, hp_text)
                    except curses.error:
                        pass

        # HUD
        txt = f"Tick: {self.engine.tick:.2f} Units: {len(self.engine.units)} Speed x{self.speed_multiplier:.2f} {'PAUSED' if self.paused else ''}"
        try:
            stdscr.addstr(view_h+2, 1, txt)
            stdscr.addstr(view_h+3, 1, "Controls: arrows/WASD pan - Tab select - t target - p pause - +/- speed - q quit - r reset")
        except curses.error:
            pass
        stdscr.refresh()

    def handle_input(self, stdscr, dt):
        ch = stdscr.getch()
        if ch == -1:
            return True
        # map keys
        if ch in (ord('q'), ord('Q')):
            return False
        if ch in (ord('p'), ord(' ')):
            self.paused = not self.paused
        if ch in (ord('+'), ord('=')):
            self.speed_multiplier *= 2.0
        if ch in (ord('-'), ord('_')):
            self.speed_multiplier = max(0.125, self.speed_multiplier/2.0)
        if ch in (9,):  # Tab
            my_units = self.engine.get_units_for_player(1)
            if my_units:
                self.selected_idx = (self.selected_idx + 1) % len(my_units)
        if ch in (ord('t'), ord('T')):
            # set selected unit's target to nearest enemy
            my_units = self.engine.get_units_for_player(1)
            if my_units and self.selected_idx < len(my_units):
                su = my_units[self.selected_idx]
                enemies = [e for e in self.engine.units if e.player != 1 and e.alive]
                if enemies:
                    nearest = min(enemies, key=lambda e: su.distance_to(e))
                    su.target_id = nearest.id
        if ch in (ord('r'), ord('R')):
            return 'reset'
        # panning
        if ch in (curses.KEY_LEFT, ord('a'), ord('A')):
            self.cam_x = clamp(self.cam_x - camera_speed*dt, 0, max(0, self.engine.w - 1))
        if ch in (curses.KEY_RIGHT, ord('d'), ord('D')):
            self.cam_x = clamp(self.cam_x + camera_speed*dt, 0, max(0, self.engine.w - 1))
        if ch in (curses.KEY_UP, ord('w'), ord('W')):
            self.cam_y = clamp(self.cam_y - camera_speed*dt, 0, max(0, self.engine.h - 1))
        if ch in (curses.KEY_DOWN, ord('s'), ord('S')):
            self.cam_y = clamp(self.cam_y + camera_speed*dt, 0, max(0, self.engine.h - 1))
        return True

    def run_curses(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        running = True
        last = time.time()
        while running:
            now = time.time()
            dt = now - last
            last = now
            inp = self.handle_input(stdscr, dt)
            if inp == 'reset':
                return 'reset'
            if inp is False:
                break
            if not self.paused:
                sim_dt = dt * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5)
                self.engine.step(sim_dt, self.generals)
            self.draw(stdscr)
        return 'quit'

    def run(self):
        return wrapper(self.run_curses)

# -------------------------
# CLI & main
# -------------------------

def parse_args():
    p = argparse.ArgumentParser(description="Terminal-playable MedievAIl-like simulator")
    p.add_argument('--seed', type=int, default=None)
    p.add_argument('--headless', action='store_true')
    return p.parse_args()


def run_headless(engine: SimpleEngine, generals: Dict[int, General], max_ticks=60.0):
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
    spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)

    generals = {
        1: DaftGeneral(1),
        2: BrainDeadGeneral(2)
    }

    if args.headless or curses is None:
        if curses is None and not args.headless:
            print("curses not available, running headless simulation. Use --headless to silence this message.")
        run_headless(engine, generals, max_ticks=180.0)
        return

    # Terminal UI loop with option to reset scenario
    while True:
        renderer = TerminalRenderer(engine, generals)
        action = renderer.run()
        # action is tuple returned by wrapper; wrapper returns the return value of run_curses
        if action == 'reset' or action == ('reset',):
            engine = SimpleEngine(w=MAP_W, h=MAP_H)
            spawn_asymmetric_armies(engine, left_offset=10, right_offset=10)
            generals = {1: DaftGeneral(1), 2: BrainDeadGeneral(2)}
            continue
        else:
            break

if __name__ == '__main__':
    main()
