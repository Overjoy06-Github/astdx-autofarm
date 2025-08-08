import pygetwindow as gw
from functions import *
import subprocess
import threading
import requests
import psutil
import json
import time
import os
import io
three_x_speed = False
PRIVATE_SERVER_LINK = "INSERT YOUR PRIVATE SERVER LINK HERE"
WEBHOOK_URL = "INSERT YOUR WEBHOOK URL HERE"

webhook = True

# UNITS | MAX OF 4 PLACEMENTS EACH
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

def send_webhook(description, color):
    try:
        screenshot = pyautogui.screenshot()
        image_bytes = io.BytesIO()
        screenshot.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        payload = {
            "username": "Macro Bot",
            "embeds": [
                {
                    "description": description,
                    "color": color,
                    "image": {
                        "url": "attachment://screenshot.png"
                    }
                }
            ]
        }

        files = {
            "file": ("screenshot.png", image_bytes, "image/png")
        }
        response = requests.post(
            WEBHOOK_URL,
            data={"payload_json": json.dumps(payload)},
            files=files
        )

        if response.status_code == 204:
            print("Screenshot embed sent to Discord.")
        else:
            print(f"Webhook failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error sending webhook: {e}")

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
        time.sleep(1)

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
    try:
        regions = [
            (290, 450, 524, 472),
            (290, 560, 524, 582),
            (290, 670, 524, 692),
            (591, 286, 925, 322)
        ]

        challenge_names = {
            "Flying Encmiean": "Flying Enemies",
            "Fjng Enemies": "Flying Enemies",
            "Single PlaccmönV": "Single Placement",
            "Juggerngut Enenies": "Juggernaut Enemies",
            "Juggernut Ehemies": "Juggernaut Enemies",
            "Unsellahle": "Unsellable"
        }

        screen_width, screen_height = pyautogui.size()

        for challenge in priority_order:
            for idx, (x1, y1, x2, y2) in enumerate(regions):
                text = clean_text(ocr(x1, y1, x2, y2))
                text = challenge_names.get(text, text)
                print(text)
                if challenge in text:
                    if idx == len(regions) - 1:
                        return (screen_width // 2, screen_height // 2, challenge)
                    else:
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        return (center_x, center_y, challenge)
        
        return None
    except Exception as e:
        print("Error: ", e)


def detect_error_message():
    error_messages = [
        "images/errors/error1.png",
        "images/errors/error2.png"
    ]
    
    for error_img in error_messages:
        if find_button(error_img):
            return True
    return False


def is_roblox_running():
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and 'RobloxPlayerBeta.exe' in proc.info['name']:
            return True
    return False


def focus_roblox():
    try:
        roblox_windows = [w for w in gw.getAllTitles() if 'Roblox' in w]
        if roblox_windows:
            window = gw.getWindowsWithTitle(roblox_windows[0])[0]
            window.activate()
    except Exception as e:
        print(f"Could not focus Roblox: {e}")


def join_private_server(server_link):
    import webbrowser
    webbrowser.open(server_link)
    time.sleep(10)
    if is_roblox_running():
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
        focus_roblox()
    
    return True


def error_checker():
    while True:
        if detect_error_message():
            print("Error detected - attempting to reconnect...")
            join_private_server(PRIVATE_SERVER_LINK)
            time.sleep(10)
        time.sleep(5)


def run_game_sequence():
    try:
        while not find_button("images/start.png"):
            time.sleep(0.5)
    
        adjust_camera()

        while not find_button("images/map_info.png"):
            time.sleep(0.5)

        current_map = get_map()
        position = detect_spawn_position(current_map)
        print(position)
            
        if position == "unknown_position":
            send_webhook("Failed to get position number...", 0xFF3131)
            join_private_server(PRIVATE_SERVER_LINK)
            main()

        with open('placements.json') as f:
            placements = json.load(f)
        
        map_data = placements.get(current_map, {})
        position_data = map_data.get(position, {})

        if not position_data:
            send_webhook("Failed to get information from placements.json...", 0xFF3131)
            print(f"No placements found for {current_map} {position}")
            return False
        
        if three_x_speed:
            fix_click(three_x_speed_coords[0], three_x_speed_coords[1])
        else:
            fix_click(two_x_speed_coords[0], two_x_speed_coords[1])
        return position_data
    
    except Exception as e:
        print(f"Error in run_game_sequence: {e}")
        

def place_all_units(coordinates):
    try:
        if "farm" in coordinates and farm_unit[1] > 0:
            for i in range(min(farm_unit[1], len(coordinates["farm"]))):
                try:
                    verify_placement(farm_unit[0], coordinates["farm"][i][0], coordinates["farm"][i][1], 15)
                except (IndexError, TypeError) as e:
                        print(f"Error placing farm unit {i+1}: {e}")
                        continue
                except Exception as e:
                    print(f"Unexpected error placing farm unit: {e}")
                    continue
            
        if "hill" in coordinates and hill_unit[1] > 0:
            for i in range(min(hill_unit[1], len(coordinates["hill"]))):
                try:
                    verify_placement(hill_unit[0], coordinates["hill"][i][0], coordinates["hill"][i][1], 15)
                except (IndexError, TypeError) as e:
                        print(f"Error placing hill unit {i+1}: {e}")
                        continue
                except Exception as e:
                    print(f"Unexpected error placing hill unit: {e}")
                    continue
        
        if "ground" in coordinates and ground_unit[1] > 0:
            for i in range(min(ground_unit[1], len(coordinates["ground"]))):
                try:
                    verify_placement(ground_unit[0], coordinates["ground"][i][0], coordinates["ground"][i][1], 15)
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
    verify_placement(farm_unit[0], coordinates["farm"][0][0], coordinates["farm"][0][1], 30)
    fix_click(start_button[0], start_button[1])
    time.sleep(1)
    verify_placement(hill_unit[0], coordinates["hill"][0][0], coordinates["hill"][0][1], 30)
    place_all_units(coordinates)
    auto_upgrade()
    print("Waiting for the game to end...")
    while True:
        complete = find_button('images/completion.png')
        if complete:
            screen_width, screen_height = pyautogui.size()
            while True:
                retry_btn = find_button('images/retry.png')
                if retry_btn:
                    if webhook:
                        send_webhook("🎉Completed Challenge!", 0x39FF14)
                    fix_click(retry_btn[0], retry_btn[1])
                    time.sleep(1)
                    macro_normal()
                    return
                else:
                    return_btn = find_button('images/return.png')
                    if return_btn:
                        if webhook:
                            send_webhook("🎉Completed Challenge!", 0x39FF14)
                        join_private_server(PRIVATE_SERVER_LINK)
                        time.sleep(1)
                        main()
                        return
                fix_click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)


def macro_single_placement():
    coordinates = run_game_sequence()
    verify_placement(farm_unit[0], coordinates["farm"][0][0], coordinates["farm"][0][1], 30)
    fix_click(start_button[0], start_button[1])
    verify_placement(hill_unit[0], coordinates["hill"][0][0], coordinates["hill"][0][1], 30)
    verify_placement(ground_unit[0], coordinates["ground"][0][0], coordinates["ground"][0][1], 30)
    auto_upgrade()
    print("Waiting for the game to end...")
    while True:
        complete = find_button('images/completion.png')
        if complete:
            screen_width, screen_height = pyautogui.size()
            while True:
                retry_btn = find_button('images/retry.png')
                if retry_btn:
                    if webhook:
                        send_webhook("🎉Completed Challenge!", 0x39FF14)
                    fix_click(retry_btn[0], retry_btn[1])
                    time.sleep(1)
                    macro_single_placement()
                    return
                else:
                    return_btn = find_button('images/return.png')
                    if return_btn:
                        if webhook:
                            send_webhook("🎉Completed Challenge!", 0x39FF14)
                        join_private_server(PRIVATE_SERVER_LINK)
                        time.sleep(1)
                        main()
                        return
                fix_click(screen_width // 2, screen_height // 2)
                time.sleep(0.5)

challenge_macros = {
    "juggernaut_enemies": macro_normal,
    "unsellable": macro_normal,
    "single_placement": macro_single_placement,
    "flying_enemies": macro_normal
}

def main():
    print("Main Program has started...")
    move_to_challenges()
    time.sleep(1)
    challenge_info = get_challenges()

    if not challenge_info:
        send_webhook("Failed to get challenge information...", 0xFF3131)
        join_private_server(PRIVATE_SERVER_LINK)
        time.sleep(5)
        main()
        return
            
    fix_click(challenge_info[0], challenge_info[1])
    time.sleep(1)
    fix_click(994, 456)
    time.sleep(1)
    fix_click(1016, 700)
    time.sleep(1)
    fix_click(1247, 596)
    challenge_macros[challenge_info[2].lower().replace(" ", "_")]()


if __name__ == "__main__":
    threading.Thread(target=error_checker, daemon=True).start()
    main()
