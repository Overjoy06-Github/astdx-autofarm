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
    def get_coord_list(coords):
        if isinstance(coords[0], list):
            return coords
        return [coords]
    
    farm_coords = get_coord_list(map_placements["farm"])
    print(f"Attempting to place farm unit at {farm_coords[0]}")
    
    max_attempts = 5
    for attempt in range(max_attempts):
        verify_placement(farm_unit, farm_coords[0][0], farm_coords[0][1])
        time.sleep(0.5)
        if find_button('images/upgrade.png'):
            print("Farm unit placed successfully!")
            break
        print(f"Attempt {attempt + 1}: Farm unit not verified, retrying...")
        if attempt == max_attempts - 1:
            print("Failed to place farm unit after maximum attempts!")
            return
    
    print("Looking for start button...")
    time.sleep(1)
    start_btn = find_button("images/start.png")
    if start_btn:
        print(f"Found start button at {start_btn}, clicking it...")
        fix_click(start_btn[0], start_btn[1])
        time.sleep(0.5)
    else:
        print("Start button not found!")
    time.sleep(1)
    
    hill_coords = get_coord_list(map_placements["hill"])
    verify_placement(hill_unit, hill_coords[0][0], hill_coords[0][1])

    placed_positions = {
        "farm": [(farm_coords[0][0], farm_coords[0][1])],
        "hill": [(hill_coords[0][0], hill_coords[0][1])],
        "ground": []
    }
    
    for unit_type in [farm_unit, hill_unit, ground_unit]:
        unit_key = "farm" if unit_type == farm_unit else "hill" if unit_type == hill_unit else "ground"
        coords_list = get_coord_list(map_placements[unit_key])
        
        start_index = 1 if unit_key in ["farm", "hill"] else 0
        
        for coord in coords_list[start_index:]:
            if (coord[0], coord[1]) not in placed_positions[unit_key]:
                verify_placement(unit_type, coord[0], coord[1])
                placed_positions[unit_key].append((coord[0], coord[1]))
    
    pydirectinput.press("t")
    pydirectinput.press("k")
    pydirectinput.press("t")

def run_game_sequence():
    while not find_button('images/setting.png'):
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
                        for _ in range(10):
                            fix_click(screen_width // 2, screen_height // 2)
                            time.sleep(1)
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
