import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
from pynput.mouse import Button, Listener as MouseListener
from pynput import mouse

from utils_general import pick_up_selected_object, click_at_position, generate_bbox, capture_and_process_region, is_object
# Create a keyboard controller
keyboard = Controller()
# Create a mouse controller
mouse_controller = mouse.Controller()

def bjora_marches2jaga_moraine(time_to_wait= 10.0):
    print("Setting area from Bjora Marches to Jaga Moraine")
    keyboard.press('ö')
    time.sleep(0.01)
    keyboard.release('ö')
    time.sleep(0.1)  
    # Check if the selected area is Jaga Moraine. 
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "area_check")
    if is_object(img_array, "jaga_moraine", print_diff=False, asset_path="assets/areas"):
        pick_up_selected_object(time_to_wait)  # Wait longer for area change
    elif is_object(img_array, "bjora_marches", print_diff=False, asset_path="assets/areas"):
        print("Already in Bjora Marches. Reset area.")
        jaga_moraine2bjora_marches(time_to_wait+5)
        bjora_marches2jaga_moraine(time_to_wait+5)
    else:
        print("Area not recognized. Cannot change area.")

def jaga_moraine2bjora_marches(time_to_wait=7.5):
    print("Setting area from Jaga Moraine to Bjora Marches")
    keyboard.press('ö')
    time.sleep(0.01)
    keyboard.release('ö')
    time.sleep(0.01) 
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "area_check")
    # Check if the selected area is Bjora Marches.
    if is_object(img_array, "bjora_marches", print_diff=False, asset_path="assets/areas"):
        pick_up_selected_object(time_to_wait) 
    elif is_object(img_array, "jaga_moraine", print_diff=False, asset_path="assets/areas"):
        print("Already in Jaga Moraine. I should reset to respawn enemies.")
        bjora_marches2jaga_moraine(time_to_wait+5)
        jaga_moraine2bjora_marches(time_to_wait+5)
    else:
        print("Area not recognized. Cannot change area.")

def jaga_moraine2jarnskeggi(time_to_wait=7.5):
    print("Go from Jaga Moraine to Jarnskeggi")
    # Simulate pressing keys to set the area
    keyboard.press('v')
    time.sleep(0.02)
    keyboard.release('v')
    time.sleep(0.02 )  # Wait for the area to load
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "npc_check")
    # Check if the selected npc is Jarnskeggi.
    if is_object(img_array, "jarnskeggi", print_diff=False, asset_path="assets/npcs"):
        print("Jarnskeggi found! Go to him.")
        pick_up_selected_object(time_to_wait)  # Wait longer for area change
    elif (is_object(img_array, "kobach_the_ferocious", print_diff=False, asset_path="assets/npcs") or 
        is_object(img_array, "polar_bear", print_diff=False, asset_path="assets/npcs")):
        print("I am in the wrong area i.e. in bjora marches. Going back to jaga moraine.")
        jaga_moraine2bjora_marches(time_to_wait)
    else:
        print("NPC not recognized. Cannot change area.")

def pick_up_norn_blessing():
    print("Picking up Norn Blessing")
    # Left mouse click at x = 1000 and y = 1000 to get norn blessing
    click_at_position(900, 575)

if __name__ == "__main__":
    time.sleep(2)  # Additional wait to ensure item is picked up
    print("Starting area change tests...")
    print("Bjora to Jaga")
    bjora_marches2jaga_moraine() 
    print("Jaga to Jarnskeggi")
    jaga_moraine2jarnskeggi()  
    print("Picking up Norn Blessing")
    pick_up_norn_blessing() 

