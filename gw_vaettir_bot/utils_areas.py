import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
from pynput.mouse import Button, Listener as MouseListener
from pynput import mouse

# Try relative imports first, then absolute imports for testing
try:
    from .utils_general import pick_up_selected_object, click_at_position, generate_bbox, capture_and_process_region, is_object
except ImportError:
    # If relative imports fail, try absolute imports for testing
    try:
        from utils_general import pick_up_selected_object, click_at_position, generate_bbox, capture_and_process_region, is_object
    except ImportError:
        # If that fails too, try adding the parent directory to path
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gw_vaettir_bot.utils_general import pick_up_selected_object, click_at_position, generate_bbox, capture_and_process_region, is_object
# Create a keyboard controller
keyboard = Controller()
# Create a mouse controller
mouse_controller = mouse.Controller()

def bjora_marches2jaga_moraine(time_to_wait= 10.0):
    keyboard.press('ö')
    time.sleep(0.01)
    keyboard.release('ö')
    time.sleep(0.1)  
    # Check if the selected area is Jaga Moraine. 
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "area_check")
    if is_object(img_array, "jaga_moraine", print_diff=True, asset_path="gw_vaettir_bot/assets/areas"):
        pick_up_selected_object(time_to_wait)  # Wait longer for area change
    elif is_object(img_array, "bjora_marches", print_diff=True, asset_path="gw_vaettir_bot/assets/areas"):
        print("Already in Bjora Marches. Reset area.")
        jaga_moraine2bjora_marches(time_to_wait+5)
        bjora_marches2jaga_moraine(time_to_wait+5)
    else:
        print("Area not recognized. Cannot change area.")

def jaga_moraine2bjora_marches(time_to_wait=7.5):
    keyboard.press('ö')
    time.sleep(0.01)
    keyboard.release('ö')
    time.sleep(0.01) 
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "area_check")
    # Check if the selected area is Bjora Marches.
    if is_object(img_array, "bjora_marches", print_diff=False, asset_path="gw_vaettir_bot/assets/areas"):
        pick_up_selected_object(time_to_wait) 
    elif is_object(img_array, "jaga_moraine", print_diff=False, asset_path="gw_vaettir_bot/assets/areas"):
        print("Already in Jaga Moraine. I should reset to respawn enemies.")
        bjora_marches2jaga_moraine(time_to_wait+5)
        jaga_moraine2bjora_marches(time_to_wait+5)
    else:
        print("Area not recognized. Cannot change area.")

def jaga_moraine2jarnskeggi(time_to_wait=7.5):
    # Simulate pressing keys to set the area
    keyboard.press('v')
    time.sleep(0.02)
    keyboard.release('v')
    time.sleep(0.02 )  # Wait for the area to load
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "npc_check")
    # Check if the selected npc is Jarnskeggi.
    if is_object(img_array, "jarnskeggi", print_diff=False, asset_path="gw_vaettir_bot/assets/npcs"):
        print("Jarnskeggi found! Go to him.")
        pick_up_selected_object(time_to_wait)  # Wait longer for area change
    elif (is_object(img_array, "kobach_the_ferocious", print_diff=False, asset_path="gw_vaettir_bot/assets/npcs") or 
        is_object(img_array, "polar_bear", print_diff=False, asset_path="gw_vaettir_bot/assets/npcs")):
        print("I am in the wrong area i.e. in bjora marches. Going back to jaga moraine.")
        jaga_moraine2bjora_marches(time_to_wait)
    else:
        print("NPC not recognized. Cannot change area.")

def pick_up_norn_blessing():
    # Left mouse click at x = 900 and y = 575 to get norn blessing
    click_at_position(900, 575)

if __name__ == "__main__":
    # Add current directory to path for testing
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    time.sleep(2)  # Additional wait to ensure item is picked up
    print("Starting area change tests...")
    print("Bjora to Jaga")
    bjora_marches2jaga_moraine() 
    print("Jaga to Jarnskeggi")
    jaga_moraine2jarnskeggi()  
    print("Picking up Norn Blessing")
    pick_up_norn_blessing() 

