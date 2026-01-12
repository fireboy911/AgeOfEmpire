import math

def lanchester_scenario(engine, unit_type, N):
    """
    Scénario pour validation scientifique (Lois de Lanchester).
    Version optimisée pour forcer la séparation entre Loi Linéaire et Quadratique.
    """
    # Statistiques ajustées pour mettre en évidence l'encombrement (collisions)
    stats_lanchester = {
        "Knight": {
            "hp": 100, "attack": 10, "range": 0.5, "speed": 0.8, 
            "reload_time": 1.0, "radius": 0.6, "tags": ["Cavalry"]
        },
        "Crossbowman": {
            "hp": 100, "attack": 10, "range": 12.0, "speed": 1.0, 
            "reload_time": 1.0, "radius": 0.4, "tags": ["archer"]
        }
    }
    
    u_stats = stats_lanchester.get(unit_type, stats_lanchester["Knight"])

    # Positionnement Joueur 1 (N unités) - Légèrement espacés
    for i in range(N):
        engine.spawn_unit(
            player=1, 
            x=15 + (i % 5) * 1.2,
            y=25 + (i // 5) * 1.2, 
            unit_type=unit_type, 
            **u_stats
        )
    
    # Positionnement Joueur 2 (2N unités) - Placé plus loin (x=45)
    # On augmente l'espacement pour que les collisions soient gérées par l'Engine
    for i in range(2 * N):
        engine.spawn_unit(
            player=2, 
            x=45 + (i % 5) * 1.2, 
            y=25 + (i // 5) * 1.2, 
            unit_type=unit_type, 
            **u_stats
        )