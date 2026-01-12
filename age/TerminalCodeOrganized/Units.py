from dataclasses import dataclass, field
from typing import Tuple, Optional,List,Dict
import math
from GameData import UNIT_STATS, BONUS_DAMAGE

@dataclass
class Unit:
    id: int
    player: int
    x: float
    y: float
    unit_type: str
    hp: float = 0.0
    attack: float = 0.0
    range: float = 0.0
    speed: float = 0.0
    alive: bool = True
    target_id: Optional[int] = None
    color: Optional[Tuple[int,int,int]] = None
    reload_time: float = 2.0  # Temps entre deux attaques
    cooldown: float = 0.0     # Temps restant avant prochaine attaque
    
    tags: List[str] = field(default_factory=list)
    bonuses: Dict[str, float] = field(default_factory=dict)
    
    radius: float = 0.4
    
    def __post_init__(self):
        # 1. Charger les stats depuis GameData si non fournies
        stats = UNIT_STATS.get(self.unit_type, UNIT_STATS["Pikeman"]) # Fallback Pikeman
        
        if self.hp == 0: self.hp = stats["hp"]
        if self.attack == 0: self.attack = stats["attack"]
        if self.range == 0: self.range = stats["range"]
        if self.speed == 0: self.speed = stats["speed"]
        self.reload_time = stats.get("reload", 2.0)

        # 2. Définir la couleur
        type_colors = {
            "Pikeman": (255, 100, 50),
            "Crossbowman": (50, 200, 50),
            "Knight": (50, 100, 255),
            "Monk": (255, 255, 255)
        }
        if self.color is None:
            # Assombrir la couleur pour le joueur 2
            base_col = type_colors.get(self.unit_type, (150, 150, 150))
            if self.player == 2:
                self.color = (max(0, base_col[0]-50), max(0, base_col[1]-50), max(0, base_col[2]-50))
            else:
                self.color = base_col

    def distance_to(self, other: "Unit") -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def step(self, dt: float, engine):
        if not self.alive: return

        # Gestion du cooldown d'attaque
        if self.cooldown > 0:
            self.cooldown -= dt

        # Logique Moine (Soin)
        if self.unit_type == "Monk":
            self._handle_monk_behavior(dt, engine)
            return

        # Logique Combat Standard
        target = engine.units_by_id.get(self.target_id)
        if target is None or not target.alive:
            self.target_id = None
            return

        d = self.distance_to(target)
        
        # SI à portée : Attaquer
        if d <= self.range + 0.1: # Petite tolérance
            if self.cooldown <= 0:
                self._attack(target, engine)
                self.cooldown = self.reload_time
        
        # SINON : Avancer
        else:
            self._move_towards(target, dt)

    def _move_towards(self, target, dt):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1e-6:
            # Normalisation et déplacement
            nx, ny = dx/dist, dy/dist
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt

    def _attack(self, target, engine):
        # Calcul des dégâts avec BONUS (Pierre-Papier-Ciseaux)
        base_dmg = self.attack
        bonus = BONUS_DAMAGE.get(self.unit_type, {}).get(target.unit_type, 0)
        
        total_damage = max(1, base_dmg + bonus)
        
        target.hp -= total_damage
        if target.hp <= 0:
            target.alive = False
            engine.mark_dead(target)

    def _handle_monk_behavior(self, dt, engine):
        # Code du moine simplifié pour l'instant
        pass