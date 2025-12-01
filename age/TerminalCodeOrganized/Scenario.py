from Engine import SimpleEngine
def spawn_asymmetric_armies(engine: "SimpleEngine", left_offset=10, right_offset=10):
    mid_x = engine.w / 2
    mid_y = engine.h / 2

    type_stats = {
        "Pikeman": {"hp": 55, "attack": 6, "range": 1.0, "speed": 1.0},
        "Crossbowman":{"hp": 40, "attack": 12, "range": 10.0, "speed": 1.0},
        "knight": {"hp": 70, "attack": 8, "range": 1.2, "speed": 1.5},
        "Monk": {"hp": 55, "attack": 1.5, "range": 5.0, "speed": 1.0, "regen": 2.0},
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
    for row in range(3):
       for i in range(-row, row+1, 2):
        x = anchor_x - row * 4 * side_dir
        y = mid_y + i
        engine.spawn_unit(player=1, x=x, y=y, unit_type="Pikeman*", 
                          color=type_colors[1]["Pikeman"], **type_stats["Pikeman"])
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
