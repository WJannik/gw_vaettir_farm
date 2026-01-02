import time
from pynput.keyboard import Controller
from utils_general import generate_bbox, generate_center_bbox, capture_and_process_region, is_red, is_yellow, is_object
import numpy as np
import matplotlib.pyplot as plt
# Create a keyboard controller
keyboard = Controller()

def are_enemies_stacked():
    """Check if there are stacked enemies."""
    # Generate bounding box and capture the main region
    bbox_compass = generate_center_bbox(1798, 153, 20)
    screenshot, img_array = capture_and_process_region(bbox_compass, "enemy_stack_check")
    # Remove the middel of the bounding box by setting is to black
    height, width, _ = np.shape(img_array)
    middel_height = height // 2
    middle_width = width // 2
    size_of_box = 6
    img_array[middel_height-size_of_box:middel_height+size_of_box, middle_width-size_of_box:middle_width+size_of_box, :] = 0
    try:
        # Save the debug image img_array
        plt.imsave("debug_images/enemies_stacked.png", img_array)
    except Exception as e:
        print(f"Error saving debug image {"enemies_stacked"}.png:", e)
    # Check for red or yellow colors indicating are not stacked
    if is_red(img_array, 3) or is_yellow(img_array, 3):
        print("Stacked enemies detected outside the middle!.")
        return False
    else:
        print("Enemies are stacked in the middle.")
        return True


def check_next_enemy(use_only_compass=False):
    """Check if there is an enemy in the next position."""
    screenshot, img_array = None, None
    
    if not use_only_compass:
        # Simulate pressing key 'c' to check the next enemy
        keyboard.press('c')
        time.sleep(0.01)
        keyboard.release('c')
        time.sleep(0.01)  # Wait a moment for the UI to update
        
        # Generate bounding box and capture the main region
        bbox = generate_bbox(860, 55, 180, 15)
        screenshot, img_array = capture_and_process_region(bbox, "enemy_check")
    
    # Generate compass bounding box and capture compass region
    bbox_compass = generate_center_bbox(1798, 153, 20)
    screenshot_compass, img_array_compass = capture_and_process_region(bbox_compass, "enemy_check_compass")
    
    if is_red(img_array_compass, 1) or is_yellow(img_array_compass, 1):
        print("Enemy detected on compass!.")
        if use_only_compass:
            return True
        if (is_object(img_array, "vaettir_no_hp", 180, 6000, False) or 
            is_object(img_array, "vaettir_full_hp", 180, 6000, False) or 
            is_red(img_array)):
            print("Enemy detected!.")
            return True
        else:
            print("No enemy detected.")
            return False
    else:
        print("No enemy detected.")
        return False

if __name__ == "__main__":
    time.sleep(2)  # Give some time before checking
    for _ in range(1):  # Check 1 cycle
        check_next_enemy()
        time.sleep(0.5)  # Wait a bit before checking again
        are_enemies_stacked()