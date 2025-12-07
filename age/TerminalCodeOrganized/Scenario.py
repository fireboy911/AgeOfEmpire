from Engine import SimpleEngine
from GameData import UNIT_STATS

def create_lanchester_scenario(engine: SimpleEngine, unit_type: str, n: int, spacing: int = 20):
    """
    Scénario pour tester les lois de Lanchester (Requis PDF).
    Player 1 : N unités
    Player 2 : 2*N unités (Force supérieure)
    """
    if unit_type not in UNIT_STATS:
        print(f"Attention: Type d'unité inconnu '{unit_type}', défaut sur Pikeman")
        unit_type = "Pikeman"

    mid_x, mid_y = engine.w / 2, engine.h / 2
    
    # Armée P1 (Gauche)
    for i in range(n):
        # Formation en ligne verticale
        engine.spawn_unit(player=1, x=mid_x - spacing, y=mid_y - n//2 + i, unit_type=unit_type)

    # Armée P2 (Droite) - Deux fois plus nombreuse
    for i in range(n * 2):
        # Formation en ligne (plus serrée ou double ligne pour que ça rentre)
        x_pos = mid_x + spacing + (i % 2) # Légère profondeur
        y_pos = mid_y - n + i
        engine.spawn_unit(player=2, x=x_pos, y=y_pos, unit_type=unit_type)


def spawn_asymmetric_armies(engine: SimpleEngine, left_offset=15, right_offset=15):
    """
    Scénario de démonstration avec différentes unités.
    """
    mid_x, mid_y = engine.w / 2, engine.h / 2

    # Configuration des couleurs spécifiques pour la démo (Optionnel, sinon géré par Unit)
    # On laisse Unit gérer les couleurs par défaut via GameData maintenant.

    # --- JOUEUR 1 (Gauche) : Cavalerie lourde et Moines ---
    # Formation de Chevaliers (Knight)
    anchor_x = mid_x - left_offset
    for i in range(3):
        engine.spawn_unit(1, x=anchor_x, y=mid_y - 2 + (i*2), unit_type="Knight")
    
    # Soutien Piquiers (Pikeman)
    for i in range(4):
        engine.spawn_unit(1, x=anchor_x - 2, y=mid_y - 3 + (i*2), unit_type="Pikeman")

    # Moines (Monk) en arrière
    engine.spawn_unit(1, x=anchor_x - 5, y=mid_y, unit_type="Monk")


    # --- JOUEUR 2 (Droite) : Armée à distance (Archers) et Piquiers ---
    anchor_x = mid_x + right_offset
    
    # Ligne de front Piquiers (Pikeman) pour protéger les archers
    for i in range(5):
        engine.spawn_unit(2, x=anchor_x, y=mid_y - 4 + (i*2), unit_type="Pikeman")

    # Ligne arrière Arbalétriers (Crossbowman)
    for i in range(4):
        engine.spawn_unit(2, x=anchor_x + 3, y=mid_y - 3 + (i*2), unit_type="Crossbowman")