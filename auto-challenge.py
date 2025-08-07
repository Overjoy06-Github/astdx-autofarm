from functions import *
import subprocess
import os
import time
import json
three_x_speed = False

# UNITS
farm_unit = ('6', 4)
hill_unit = ('1', 4)
ground_unit = ('5', 4)


# COORDINATES
three_x_speed_coords = (1556, 556)
two_x_speed_coords = (1493, 556)
start_button = (795, 156)

# PRIORITY
priority_order = [
    "Juggernaut Enemies",
    "Unsellable",
    "Single Placement",
    "Flying Enemies"
]


def ocr(x1, y1, x2, y2):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    ahk_script = f"""
    #Requires AutoHotkey v2.0
    #Include {script_dir}\\OCR.ahk
    
    result := OCR.FromRect({x1}, {y1}, {x2-x1}, {y2-y1})
    
    if result.Text {{
        FileAppend(result.Text, "*")
        ExitApp(1)
    }}
    ExitApp(0)
    """
    
    temp_script = os.path.join(script_dir, "temp_ocr.ahk")
    with open(temp_script, "w") as f:
        f.write(ahk_script)
    
    try:
        result = subprocess.run(
            [r"C:\Program Files\AutoHotkey\UX\AutoHotkeyUX.exe", temp_script],
            capture_output=True,
            text=True,
            timeout=5
        )
                
        if result.returncode == 1 and result.stdout.strip():
            text = result.stdout.strip()
            return text
                
    finally:
        try:
            if os.path.exists(temp_script):
                os.remove(temp_script)
        except:
            pass
            
    return None


def move_to_challenges():
    while not find_button("images/setting.png"):
        time.sleep(0.5)
    fix_click(56, 480)
    time.sleep(1)
    fix_click(927, 556)
    fix_click(1087, 257)
    pydirectinput.keyDown("d")
    pydirectinput.keyDown("w")
    time.sleep(5)
    pydirectinput.keyUp("d")
    pydirectinput.keyUp("w")
    pydirectinput.press("e")


def clean_text(text):
    if text:
        clean_text = ''.join(char for char in text if char.isalpha() or char.isspace())
        if clean_text.strip():
            return clean_text
        else:
            return None
    else:
        return None
    

def get_challenges():
    regions = [
        (290, 450, 524, 472),
        (290, 560, 524, 582),
        (290, 670, 524, 692)
    ]

    challenge_names = {
        #"HighCost": "High Cost",
        #"HihCost": "High Cost",
        "Flying Encmiean": "Flying Enemies",
        "Fjng Enemies": "Flying Enemies",
        "Single PlaccmönV": "Single Placement",
        "Juggerngut Enenies": "Juggernaut Enemies",
        "Juggerngut Enenies": "Juggernaut Enemies"
    }

    for challenge in priority_order:
        for x1, y1, x2, y2 in regions:
            text = clean_text(ocr(x1, y1, x2, y2))
            text = challenge_names.get(text, text)
            if challenge in text:
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                return (center_x, center_y, challenge)
    
    return None


def run_game_sequence():
    while not find_button("images/setting.png"):
        time.sleep(0.5)
    
    adjust_camera()
    current_map = get_map()
    position = detect_spawn_position(current_map)
    print(position)

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

    return position_data

def place_all_units(coordinates):
    try:
        if "farm" in coordinates and farm_unit[1] > 0:
            for i in range(min(farm_unit[1] + 1, len(coordinates["farm"]))):
                try:
                    verify_placement(farm_unit[0], coordinates["farm"][i][0], coordinates["farm"][i][1])
                except (IndexError, TypeError) as e:
                        print(f"Error placing farm unit {i+1}: {e}")
                        continue
                except Exception as e:
                    print(f"Unexpected error placing farm unit: {e}")
                    continue
            
        if "hill" in coordinates and hill_unit[1] > 0:
            for i in range(min(hill_unit[1] + 1, len(coordinates["hill"]))):
                try:
                    verify_placement(hill_unit[0], coordinates["hill"][i][0], coordinates["hill"][i][1])
                except (IndexError, TypeError) as e:
                        print(f"Error placing hill unit {i+1}: {e}")
                        continue
                except Exception as e:
                    print(f"Unexpected error placing hill unit: {e}")
                    continue
        
        if "ground" in coordinates and ground_unit[1] > 0:
            for i in range(min(ground_unit[1], len(coordinates["ground"]))):
                try:
                    verify_placement(ground_unit[0], coordinates["ground"][i][0], coordinates["ground"][i][1])
                except (IndexError, TypeError) as e:
                        print(f"Error placing ground unit {i+1}: {e}")
                        continue
                except Exception as e:
                    print(f"Unexpected error placing ground unit: {e}")
                    continue

    except Exception as e:
        print(f"Unexpected error in place_all_units: {e}")

def auto_upgrade():
    pydirectinput.press("t")
    pydirectinput.press("k")
    pydirectinput.press("t")

def macro_normal():
    coordinates = run_game_sequence()
    print(coordinates)
    verify_placement(farm_unit[0], coordinates["farm"][0][0], coordinates["farm"][0][1])
    fix_click(start_button[0], start_button[1])
    verify_placement(hill_unit[0], coordinates["hill"][0][0], coordinates["hill"][0][1])
    place_all_units(coordinates)
    auto_upgrade()
    print("Waiting for the game to end...")
    while True:
        complete = find_button('images/completion.png')
        if complete:
            print("Found completion screen, clicking until retry button appears...")
            screen_width, screen_height = pyautogui.size()
            while True:
                retry_btn = find_button('images/retry.png')
                if retry_btn:
                    print("Found retry button, clicking it...")
                    fix_click(retry_btn[0], retry_btn[1])
                    time.sleep(1)
                    macro_normal()
                    break
                else:
                    return_btn = find_button('images/return.png')
                    if return_btn:
                        fix_click(return_btn[0], return_btn[1])
                        time.sleep(1)
                        main()
                fix_click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)


def macro_high_cost():
    run_game_sequence()


def macro_single_placement():
    coordinates = run_game_sequence()
    verify_placement(farm_unit[0], coordinates["farm"][0][0], coordinates["farm"][0][1])
    fix_click(start_button[0], start_button[1])
    verify_placement(hill_unit[0], coordinates["hill"][0][0], coordinates["hill"][0][1])
    verify_placement(ground_unit[0], coordinates["ground"][0][0], coordinates["ground"][0][1])
    auto_upgrade()
    print("Waiting for the game to end...")
    while True:
        complete = find_button('images/completion.png')
        if complete:
            print("Found completion screen, clicking until retry button appears...")
            screen_width, screen_height = pyautogui.size()
            while True:
                return_btn = find_button('images/return.png')
                if return_btn:
                    print("Found return button, clicking it...")
                    fix_click(return_btn[0], return_btn[1])
                    time.sleep(1)
                    main()
                    break
                fix_click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)
            break

def macro_flying_enemies():
    run_game_sequence()

# CHALLENGES
challenge_macros = {
    "juggernaut_enemies": macro_normal,
    "unsellable": macro_normal,
    "single_placement": macro_single_placement,
    "flying_enemies": macro_flying_enemies
}

def main():
    move_to_challenges()
    time.sleep(1)
    challenge_info = get_challenges()
    fix_click(challenge_info[0], challenge_info[1])
    time.sleep(1)
    fix_click(994, 456)
    time.sleep(1)
    fix_click(1016, 700)
    time.sleep(1)
    fix_click(1247, 596)
    challenge_macros[challenge_info[2].lower().replace(" ", "_")]()


if __name__ == "__main__":
    main()
