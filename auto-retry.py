from functions import *
three_x_speed = False

# UNITS
farm_unit = '6'
hill_unit = '1'
ground_unit = '5'

# COORDINATES
three_x_speed_coords = (1556, 556)
two_x_speed_coords = (1493, 556)

def place_all_units(map_placements):
    verify_placement(farm_unit, map_placements["farm"][0], map_placements["farm"][1])
    
    start_btn = find_button("images/start.png")
    if start_btn:
        fix_click(start_btn[0], start_btn[1])
    time.sleep(1)
    
    verify_placement(hill_unit, map_placements["hill"][0], map_placements["hill"][1])
    
    placed_positions = {
        "farm": [(map_placements["farm"][0], map_placements["farm"][1])],
        "hill": [(map_placements["hill"][0], map_placements["hill"][1])],
        "ground": []
    }
    
    for unit_type in [farm_unit, hill_unit, ground_unit]:
        unit_key = "farm" if unit_type == farm_unit else "hill" if unit_type == hill_unit else "ground"
        coords = map_placements.get(unit_key)
        
        if isinstance(coords[0], list):
            for coord in coords:
                if (coord[0], coord[1]) not in placed_positions[unit_key]:
                    verify_placement(unit_type, coord[0], coord[1])
                    placed_positions[unit_key].append((coord[0], coord[1]))
        else:
            if (coords[0], coords[1]) not in placed_positions[unit_key]:
                verify_placement(unit_type, coords[0], coords[1])
                placed_positions[unit_key].append((coords[0], coords[1]))
    
    pydirectinput.press("t")
    pydirectinput.press("k")
    pydirectinput.press("t")

def run_game_sequence():
    while not find_button('images/start.png'):
        time.sleep(0.5)
    
    adjust_camera()
    current_map = get_map()
    position = detect_spawn_position(current_map)

    with open('placements.json') as f:
        placements = json.load(f)
    
    map_data = placements.get(current_map, {})
    position_data = map_data.get(position, {})
    
    if not position_data:
        print(f"No placements found for {current_map} {position}")
        return False
    
    if three_x_speed:
        fix_click(three_x_speed_coords[0], three_x_speed_coords[1])
    else:
        fix_click(two_x_speed_coords[0], two_x_speed_coords[1])
    
    place_all_units(position_data)
    return True

def main():
    while True:
        try:
            if run_game_sequence():
                print("Waiting for game to end...")
                while True:
                    complete = find_button('images/completion.png')
                    if complete:
                        print("Found retry button, starting new game...")
                        screen_width, screen_height = pyautogui.size()
                        for i in range(3):
                            fix_click(int(screen_width / 2), int(screen_height / 2))
                        retry_btn = find_button('images/retry.png')
                        fix_click(retry_btn[0], retry_btn[1])
                        time.sleep(1)
                        break
                    time.sleep(1)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(1)
            continue

if __name__ == "__main__":
    main()