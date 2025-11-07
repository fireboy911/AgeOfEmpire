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
camera_speed = 3.0     # tiles per second
# ---------------------------

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
    color: Optional[Tuple[int,int,int]] = None  # will be set in __post_init__

    def __post_init__(self):
        """Automatically assign colors based on unit type if not set."""
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

        # passive regen
        if self.regen > 0:
            self.hp = min(self.hp + self.regen * dt, 55)

        # ---------------------------------------------------
        # Monk logic
        # ---------------------------------------------------
        if self.unit_type == "Monk":
            heal_range = self.range
            heal_power = self.attack * dt * 2  # heal is stronger than attack
            # only wounded allies
            allies = [a for a in engine.units if a.player == self.player and a.alive and a.hp < 55]
            if not allies:
                return  # nothing to heal

            # choose closest wounded ally
            target = min(allies, key=lambda a: self.distance_to(a))
            dist = self.distance_to(target)

            if dist <= heal_range:
                target.hp = min(target.hp + heal_power, 55)  # heal
            else:
                # move toward wounded ally
                dx = target.x - self.x
                dy = target.y - self.y
                dist = math.hypot(dx, dy)
                if dist > 1e-6:
                    nx = dx / dist
                    ny = dy / dist
                    self.x += nx * self.speed * dt
                    self.y += ny * self.speed * dt
                    



        # ---------------------------------------------------
        # normal combat logic
        # ---------------------------------------------------
        target = None  # make sure it's defined!

        if self.target_id is not None:
            target = engine.units_by_id.get(self.target_id)

        # 🔹 here target will *always* exist (even if None)
        if target is None or not target.alive:
            self.target_id = None
            return

        # attack or move toward target
        d = self.distance_to(target)
        if d <= self.range + 0.1:
            # attack
            damage = self.attack * dt
            target.hp -= damage
            if target.hp <= 0:
                target.alive = False
                target.hp = 0
                engine.mark_dead(target)
        else:
            # move toward target
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

# -------------------------
# Scenario generator
# -------------------------
# -------------------------
# New placement helpers (asymmetric formations)
# -------------------------

def spawn_asymmetric_armies(engine: "SimpleEngine", left_offset=10, right_offset=10):
    mid_x = engine.w / 2
    mid_y = engine.h / 2

    # --- Define stats per unit type ---
    type_stats = {
        "Pikeman": {"hp": 55, "attack": 6, "range": 1.0, "speed": 1.0},
        "Crossbowman":{"hp": 40, "attack": 12, "range": 5.0, "speed": 1.0},
        "knight": {"hp": 70, "attack": 8, "range": 1.2, "speed": 1.5},
        "Monk": {"hp": 55, "attack": 1.5, "range": 5.0, "speed": 1.0, "regen": 2.0},
    }

    # --- Define per-player colors ---
    type_colors = {
        1: {  # Player 1
            "Pikeman": (255, 100, 50),   # orange/red
            "Crossbowman": (255, 50, 50),    # red
            "knight": (200, 0, 0),      # dark red
            "Monk": (255, 150, 100),  # light orange
        },
        2: {  # Player 2
            "Pikeman": (50, 150, 255),   # blue-ish
            "Crossbowman": (100, 200, 255),  # light blue
            "knight": (0, 100, 255),    # dark blue
            "Monk": (150, 200, 255),  # light blue
        }
    }

    # --------------------------
    # Player 1: left side
    side_dir = 1
    anchor_x = mid_x - left_offset

    # Front: knights
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + i
        unit_type = "knight"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # Middle: Pikeman
    for row in range(3):
       for i in range(-row, row+1, 2):  # number of units increases each row
        x = anchor_x - row * 4 * side_dir
        y = mid_y + i
        engine.spawn_unit(player=1, x=x, y=y, unit_type="Pikeman*", 
                          color=type_colors[1]["Pikeman"], **type_stats["Pikeman"])
        unit_type = "Pikeman"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # Back: Crossbowman
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "Crossbowman"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])
    # Monk
    for i in range(2):
        x = anchor_x - i * 6 * side_dir
        y = mid_y - 3 + i * 6
        unit_type = "Monk"
        engine.spawn_unit(player=1, x=x, y=y, unit_type=unit_type,
                          color=type_colors[1][unit_type], **type_stats[unit_type])

    # --------------------------
    # Player 2: right side
    side_dir = -1
    anchor_x = mid_x + right_offset

    # Front: Crossbowman
    for i in range(4):
        x = anchor_x - i * 2 * side_dir
        y = mid_y - 2
        unit_type = "Crossbowman"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

    # Middle: knights
    for i in range(3):
        x = anchor_x - i * 2 * side_dir
        y = mid_y
        unit_type = "knight"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

    # Back: Pikeman
    for i in range(5):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
        unit_type = "Pikeman"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])
    
    # Monk
    for i in range(2):
        x = anchor_x - i * 6 * side_dir
        y = mid_y - 3 + i * 6
        unit_type = "Monk"
        engine.spawn_unit(player=2, x=x, y=y, unit_type=unit_type,
                          color=type_colors[2][unit_type], **type_stats[unit_type])

# -------------------------
# Pygame renderer (optional)
# -------------------------
class PygameRenderer:
    def __init__(self, engine: SimpleEngine, generals: Dict[int, General]):
        if pygame is None:
            raise RuntimeError("Pygame not installed.")
        pygame.init()
        self.engine = engine
        self.generals = generals
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("MedievAIl prototype")
        self.clock = pygame.time.Clock()
        self.cam_x = max(0, engine.w//2 - (SCREEN_W // TILE_SIZE)//2)
        self.cam_y = max(0, engine.h//2 - (SCREEN_H // TILE_SIZE)//2)
        self.speed_multiplier = 1.0
        self.paused = False
        self.show_minimap = True

    def world_to_screen(self, wx, wy) -> Tuple[int,int]:
        sx = int((wx - self.cam_x) * TILE_SIZE)
        sy = int((wy - self.cam_y) * TILE_SIZE)
        return sx, sy

    def draw(self):
        cols = SCREEN_W // TILE_SIZE + 2
        rows = SCREEN_H // TILE_SIZE + 2
        for i in range(cols):
            for j in range(rows):
                tx = self.cam_x + i
                ty = self.cam_y + j
                if tx < 0 or ty < 0 or tx >= self.engine.w or ty >= self.engine.h:
                    color = (50,50,50)
                else:
                    color = (34,139,34) if (int(tx)+int(ty))%2==0 else (40,120,40)
                pygame.draw.rect(self.screen, color, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE+1, TILE_SIZE+1))
        for u in self.engine.units:
            sx, sy = self.world_to_screen(u.x, u.y)
            col = u.color
            r = int(TILE_SIZE*0.4)
            pygame.draw.circle(self.screen, col, (sx+TILE_SIZE//2, sy+TILE_SIZE//2), r)
            hp_frac = clamp(u.hp / 55.0, 0.0, 1.0)
            bar_w = int(TILE_SIZE * hp_frac)
            pygame.draw.rect(self.screen, (0,0,0), (sx, sy-6, TILE_SIZE, 4))
            pygame.draw.rect(self.screen, (0,255,0), (sx, sy-6, bar_w, 4))
        font = pygame.font.SysFont(None, 20)
        txt = f"Tick: {self.engine.tick:.2f}  Units: {len(self.engine.units)}  Speed x{self.speed_multiplier:.1f}"
        surf = font.render(txt, True, (255,255,255))
        self.screen.blit(surf, (8,8))
        if self.show_minimap:
            mm_w, mm_h = 200,200
            mm_surf = pygame.Surface((mm_w, mm_h))
            mm_surf.fill((20,20,20))
            scale_x = mm_w / self.engine.w
            scale_y = mm_h / self.engine.h
            for u in self.engine.units:
                ux = int(u.x*scale_x)
                uy = int(u.y*scale_y)
                c = (255,50,50) if u.player==1 else (50,50,255)
                mm_surf.fill(c, (ux, uy, 2,2))
            self.screen.blit(mm_surf, (SCREEN_W - mm_w - 8, 8))
        pygame.display.flip()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dt = self.clock.get_time()/1000.0
        move_speed = camera_speed * dt * (1 + self.speed_multiplier)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.cam_x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cam_x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.cam_y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.cam_y += move_speed
        self.cam_x = clamp(self.cam_x, 0, max(0, self.engine.w - SCREEN_W//TILE_SIZE))
        self.cam_y = clamp(self.cam_y, 0, max(0, self.engine.h - SCREEN_H//TILE_SIZE))

    def run(self):
        running = True
        while running:
            dt_real = self.clock.tick(FPS)/1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: running = False
                    elif event.key == pygame.K_p: self.paused = not self.paused
                    elif event.key == pygame.K_m: self.show_minimap = not self.show_minimap
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS): self.speed_multiplier *= 2.0
                    elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE): self.speed_multiplier = max(0.125, self.speed_multiplier/2.0)
            self.handle_input()
            if not self.paused:
                sim_dt = dt_real * self.speed_multiplier
                sim_dt = min(sim_dt, 0.5)
                self.engine.step(sim_dt, self.generals)
            self.screen.fill((0,0,0))
            self.draw()
        pygame.quit()

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
