# GameData.py

# Statistiques de base (Source: AoE2 Wiki)
UNIT_STATS = {
    "Pikeman": {
        "hp": 55, "attack": 4, "range": 0.5, "speed": 1.0, 
        "reload": 3.0, "cost": "60W, 25G" # Cost indicatif pour l'instant
    },
    "Crossbowman": {
        "hp": 35, "attack": 5, "range": 7.0, "speed": 0.96, 
        "reload": 2.0
    },
    "Knight": {
        "hp": 100, "attack": 10, "range": 0.5, "speed": 1.35, 
        "reload": 1.8
    },
    "Monk": {
        "hp": 30, "attack": 0, "range": 9.0, "speed": 0.7, 
        "reload": 1.0, "heal_rate": 2.5
    }
}

# Matrice des bonus de dégâts (Attaquant -> {Cible: Bonus})
# C'est LE cœur de la stratégie (Pierre-Papier-Ciseaux)
BONUS_DAMAGE = {
    "Pikeman": {
        "Knight": 22,  # Piquier tue Chevalier
        "Camel": 16
    },
    "Skirmisher": {
        "Archer": 3,
        "Crossbowman": 3
    },
    "Camel": {
        "Knight": 18
    },
    # Ajoutez d'autres relations ici
}