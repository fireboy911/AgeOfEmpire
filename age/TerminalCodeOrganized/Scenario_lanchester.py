def lanchester_scenario(engine, unit_type="Knight", N=20):
    
    stats = {
        "Knight": {"hp": 100, "attack": 10, "range": 1.2, "speed": 1.5, "reload_time": 1.0, "radius": 0.8},
        "Crossbowman": {"hp": 100, "attack": 10, "range": 12.0, "speed": 1.0, "reload_time": 1.0, "radius": 0.3}
    }
    u_stats = stats.get(unit_type, stats["Knight"])
    # Engagement immédiat
    x_p1, x_p2 = 20.0, 21.2 

    for i in range(N):
        engine.spawn_unit(player=1, x=x_p1 - (i%5)*0.6, y=30 + (i//5)*0.6, unit_type=unit_type, **u_stats)
    for i in range(2 * N):
        engine.spawn_unit(player=2, x=x_p2 + (i%5)*0.6, y=30 + (i//5)*0.6, unit_type=unit_type, **u_stats)