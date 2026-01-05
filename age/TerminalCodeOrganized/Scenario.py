from Engine import SimpleEngine
def spawn_asymmetric_armies(engine: "SimpleEngine", left_offset=10, right_offset=10):
    mid_x = engine.w / 2
    mid_y = engine.h / 2

    type_stats = {
        "Pikeman": {"hp": 55, "attack": 4, "reload_time": 3.0, "range": 1.0, "speed": 1.0, "tags": ["infantry"], "bonuses": {"Cavalry": 22.0}},
        "Crossbowman":{"hp": 35, "attack": 5,"reload_time": 2.0, "range": 5.0, "speed": 0.96, "tags": ["archer"]},
        "knight": {"hp": 100, "attack": 10, "reload_time": 1.8, "armor": 2, "range": 1.0, "speed": 1.35, "tags": ["Cavalry"]},
        "Monk": {"hp": 30, "attack": 0.0, "reload_time": 1.0, "range": 9.0, "speed": 0.7, "regen": 2.5, "tags": ["Monk"]},
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
    for i in range(5):
        x = anchor_x - i * 2 * side_dir
        y = mid_y + 2
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
