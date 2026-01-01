import time
from pynput.keyboard import Controller
from utils_general import generate_bbox, generate_center_bbox, capture_and_process_region, is_red, is_yellow, is_object

# Create a keyboard controller
keyboard = Controller()

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