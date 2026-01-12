import time
from pynput.keyboard import Controller
import numpy as np
import matplotlib.pyplot as plt

# Try relative imports first, then absolute imports for testing
try:
    from .utils_general import generate_bbox, generate_center_bbox, capture_and_process_region, is_red, is_yellow, is_object
except ImportError:
    # If relative imports fail, try absolute imports for testing
    from utils_general import generate_bbox, generate_center_bbox, capture_and_process_region, is_red, is_yellow, is_object

        
# Create a keyboard controller
keyboard = Controller()

def are_enemies_stacked() -> bool:
    """Check if there are stacked enemies."""
    # Generate bounding box and capture the main region
    bbox_compass = generate_center_bbox(1798, 123, 22)
    _, img_array = capture_and_process_region(bbox_compass, "enemy_stack_check")
    # Remove the middle of the bounding box by setting it to black
    height, width, _ = np.shape(img_array)
    middle_height = height // 2
    middle_width = width // 2
    size_of_box = 7
    img_array[middle_height-size_of_box:middle_height+size_of_box, middle_width-size_of_box:middle_width+size_of_box, :] = 0
    try:
        # Save the debug image img_array
        plt.imsave("gw_vaettir_bot/debug_images/enemies_stacked.png", img_array)
    except Exception as e:
        print(f"Error saving debug image {"enemies_stacked"}.png:", e)
    # Check for red or yellow colors indicating that the enemies are not yet stacked
    return not (is_red(img_array, 1) or is_yellow(img_array, 1))


def check_next_enemy(use_only_compass: bool = False) -> bool:
    """Check if there is an enemy in the next position."""
    _, img_array = None, None
    
    if not use_only_compass:
        # Simulate pressing key 'c' to check the next enemy
        keyboard.press('c')
        time.sleep(0.01)
        keyboard.release('c')
        time.sleep(0.01)  # Wait a moment to update
        
        # Generate bounding box and capture the main region
        bbox = generate_bbox(860, 25, 180, 15)
        _, img_array = capture_and_process_region(bbox, "enemy_check")
    
    # Generate compass bounding box and capture compass region
    bbox_compass = generate_center_bbox(1798, 123, 20)
    _, img_array_compass = capture_and_process_region(bbox_compass, "enemy_check_compass")
    # img_array_compass is a 40x40x3 numpy array. I only want to look at the circle with radius 20
    center_y, center_x = 20, 20
    height, width, _ = np.shape(img_array_compass)
    for y in range(height):
        for x in range(width):
            # Set every pixel outside the compass range to black
            if (y - center_y) ** 2 + (x - center_x) ** 2 > 25 ** 2:
                img_array_compass[y, x, :] = 0 

    try:
        # Save the debug image img_array_compass
        plt.imsave("gw_vaettir_bot/debug_images/enemies_without_edge.png", img_array_compass)
    except Exception as e:
        print(f"Error saving debug image {"enemies_without_edge"}.png:", e)
    if is_red(img_array_compass, 1) or is_yellow(img_array_compass, 1):
        if use_only_compass:
            return True
        if (is_object(img_array, "vaettir_no_hp", 180, 6000, False) or 
            is_object(img_array, "vaettir_full_hp", 180, 6000, False) or 
            is_red(img_array)):
            return True
        else:
            return False
    else:
        return False

if __name__ == "__main__":
    # Add current directory to path for testing
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    time.sleep(2)  # Give some time before checking
    for _ in range(1):  # Check 1 cycle
        check_next_enemy()
        time.sleep(0.5)  # Wait a bit before checking again
        are_enemies_stacked()