from __future__ import annotations
from dataclasses import dataclass 
from GameData import BONUS_DAMAGE
@dataclass
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
# Ajoutez cet import en haut
 #deja fait en haut 

# ... (Gardez vos classes General, BrainDeadGeneral, DaftGeneral) ...

class SmartGeneral(General):
    def give_orders(self, engine: SimpleEngine):
        my_units = engine.get_units_for_player(self.player)
        enemies = [u for u in engine.units if u.player != self.player and u.alive]
        
        if not enemies: return

        for u in my_units:
            if u.target_id is None: # Si l'unité n'a rien à faire
                # Trouver la cible optimale
                best_target = self.find_best_target(u, enemies)
                if best_target:
                    u.target_id = best_target.id

    def find_best_target(self, attacker, enemies):
        # Score : Bonus de dégâts (très important) - Distance (moins important)
        best_score = -float('inf')
        best_e = None
        
        for e in enemies:
            dist = attacker.distance_to(e)
            
            # Vérifier si on a un bonus contre ce type d'unité
            bonus = BONUS_DAMAGE.get(attacker.unit_type, {}).get(e.unit_type, 0)
            
            # Formule de score heuristique
            # On valorise ENORMEMENT le bonus (x10) pour forcer le contre
            score = (bonus * 10) - dist 
            
            if score > best_score:
                best_score = score
                best_e = e
                
        return best_e