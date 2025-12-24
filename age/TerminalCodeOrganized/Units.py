from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import math
@dataclass
class Unit:
    id: int
    player: int
    x: float
    y: float
    hp: float = 0.0
    max_hp: Optional[float] = None
    attack: float = 50.0
    armor: float = 0.0
    range: float = 1.0
    speed: float = 1.0
    alive: bool = True
    target_id: Optional[int] = None
    regen: float = 0.
    reload_time: float = 1.0
    reload_timer: float = 0.0
    unit_type: str = "Pikeman"
    color: Optional[Tuple[int,int,int]] = None  # unused by curses but kept
    tags: List[str] = field(default_factory=list)
    bonuses: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        type_colors = {
            "Pikeman": (200, 50, 50),
            "Crossbowman": (255, 200, 50),
            "knight": (180, 180, 180),
            "mage": (120, 50, 200),
            "Monk": (50, 200, 120)
        }
        if self.color is None:
            self.color = type_colors.get(self.unit_type, (255, 255, 255))

        if self.max_hp is None:
            self.max_hp = self.hp

    def distance_to(self, other: "Unit") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def step(self, dt: float, engine: "SimpleEngine"):
        if not self.alive:
            return

        # Gestion du timer de rechargement
        if self.reload_timer > 0:
            self.reload_timer -= dt

        if self.regen > 0:
            self.hp = min(self.hp + self.regen * dt, self.max_hp)

        # Monk healing behavior
        if self.unit_type == "Monk":
            heal_range = self.range
            allies = [a for a in engine.units if a.player == self.player and a.alive and a.hp < a.max_hp]
            if not allies:
                return
            target = min(allies, key=lambda a: self.distance_to(a))
            dist = self.distance_to(target)
            if dist <= heal_range:
                if self.reload_timer <= 0:
                    target.hp = min(target.hp + self.regen, target.max_hp)
                    self.reload_timer = self.reload_time
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
            if self.reload_timer <= 0:
                current_attack = self.attack
                # On regarde chaque tag de la cible (ex: "Mounted")
                for tag in target.tags:
                    # Si j'ai un bonus contre ce tag, je l'ajoute
                    if tag in self.bonuses:
                        current_attack += self.bonuses[tag]
                base_damage = max(0, current_attack - target.armor)
                damage = base_damage
                target.hp -= damage
                self.reload_timer = self.reload_time
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