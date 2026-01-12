def lanchester_scenario(engine, unit_type, N):
    """
    Scénario pur pour validation scientifique (Lois de Lanchester).
    Oppose N unités (P1) à 2N unités (P2) de type identique.
    """
    # Statistiques symétriques pour ne pas fausser le test
    stats_lanchester = {
        "Knight": {
            "hp": 100, "attack": 10, "range": 0.5, "speed": 1.5, 
            "reload_time": 1.0, "tags": ["Cavalry"]
        },
        "Crossbowman": {
            "hp": 100, "attack": 10, "range": 10.0, "speed": 1.0, 
            "reload_time": 1.0, "tags": ["archer"]
        }
    }
    
    u_stats = stats_lanchester.get(unit_type, stats_lanchester["Knight"])

    # Positionnement Joueur 1 (N unités)
    for i in range(N):
        engine.spawn_unit(
            player=1, 
            x=20 + (i % 5) * 0.5,
            y=30 + (i // 5) * 0.5, 
            unit_type=unit_type, 
            **u_stats
        )
    
    # Positionnement Joueur 2 (2N unités)
    for i in range(2 * N):
        engine.spawn_unit(
            player=2, 
            x=28 + (i % 5) * 0.5, #ppour avoire une bataille qui se fasse vite au debut 
            y=30 + (i // 5) * 0.5, 
            unit_type=unit_type, 
            **u_stats
        )