from PIL import ImageGrab
import pydirectinput
import numpy as np
import pyautogui
import json
import time
import cv2
import os

def adjust_camera():
    pyautogui.scroll(-7500)
    time.sleep(0.05)
    screen_width, screen_height = pyautogui.size()
    start_x = screen_width // 2
    pydirectinput.moveTo(start_x, 100, duration=0.2)
    
    pydirectinput.mouseDown(button='right')
    time.sleep(0.05)
    
    pydirectinput.moveRel(0, 500, duration=0.3)
    
    pydirectinput.mouseUp(button='right')
    time.sleep(0.05)

def fix_click(x, y):
    pydirectinput.moveTo(x, y, duration=0.2)
    pydirectinput.moveRel(1, 0, duration=0.05)
    pydirectinput.click(button='left')
    time.sleep(0.05)

def find_button(button_name):
    try:
        location = pyautogui.locateOnScreen(button_name, confidence=0.9)
        if location:
            center = pyautogui.center(location)
            x, y = int(center.x), int(center.y)

            return x, y
        else:
            print("Image not found on screen")
        time.sleep(1)
    except Exception as e:
        pass

def get_map():
    pydirectinput.press('z')
    screenshot = ImageGrab.grab(bbox=(1170, 218, 1500, 258))
    pydirectinput.press('z')
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    denoised = cv2.fastNlMeansDenoising(gray)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    map_dir = 'images/map_names'
    best_match = None
    best_score = 0.8
    
    for filename in os.listdir(map_dir):
        if not filename.lower().endswith('.png'):
            continue
            
        template_path = os.path.join(map_dir, filename)
        template = cv2.imread(template_path)
        if template is None:
            print(f"Warning: Could not load template image: {template_path}")
            continue
        
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.resize(template_gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        template_denoised = cv2.fastNlMeansDenoising(template_gray)
        template_enhanced = clahe.apply(template_denoised)
        
        if enhanced.shape[:2] != template_enhanced.shape[:2]:
            template_enhanced = cv2.resize(template_enhanced, (enhanced.shape[1], enhanced.shape[0]))
        
        result = cv2.matchTemplate(enhanced, template_enhanced, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > best_score:
            best_score = max_val
            best_match = os.path.splitext(filename)[0]

    if not best_match:
        return "Unknown Map"
    
    return best_match


def lobby():
    not_loaded = True
    while not_loaded:
        if find_button('images/return.png'):
            not_loaded = False
            return True
    time.sleep(1)


def get_mouse_position():
    try:
        while True:
            x, y = pyautogui.position()
            print(f"Mouse position: X = {x}, Y = {y}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nProgram stopped.") 


def take_screenshot():
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def detect_spawn_position(map_name):
    if not map_name or map_name == "Unknown Map":
        return "unknown_position"
    
    map_folder = os.path.join('images', 'spawn_locations', map_name)

    screenshot = take_screenshot()
    ref_images = []
    for file in os.listdir(map_folder):
        if file.endswith('.png'):
            img_path = os.path.join(map_folder, file)
            ref_img = cv2.imread(img_path, 0)
            if ref_img is not None:
                ref_images.append(ref_img)
    
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    best_match = None
    max_val = -1

    for i, ref_img in enumerate(ref_images):
        res = cv2.matchTemplate(gray, ref_img, cv2.TM_CCOEFF_NORMED)
        _, current_max, _, _ = cv2.minMaxLoc(res)
        
        if current_max > max_val:
            max_val = current_max
            best_match = i + 1

    threshold = 0.8
    if max_val > threshold:
        return f"position{best_match}"
    else:
        return "unknown_position"


def place_unit(slot, x, y):
    pydirectinput.press(slot)
    time.sleep(0.05)
    fix_click(x, y)

def verify_placement(slot, x, y):
    max_time = 30
    start_time = time.time()
    unit_placed = False

    while time.time() - start_time < max_time:
        place_unit(slot, x, y)
        time.sleep(1) 

        if find_button("images/upgrade.png"):
            unit_placed = True
            break
        
        fix_click(x, y)
        time.sleep(0.5)

    if not unit_placed:
        print(f"Failed to place unit after {max_time} seconds.")
    else:
        print("Unit placed successfully!")
