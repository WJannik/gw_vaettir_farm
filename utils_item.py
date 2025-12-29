import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
# Create a keyboard controller
keyboard = Controller()

def is_color(img_array, color_name, r_min=0, r_max=255, g_min=0, g_max=255, b_min=0, b_max=255, pixel_threshold=20):
    """
    Generic function to check for a specific color by analyzing pixel colors.
    
    Args:
        img_array: numpy array of the image
        color_name: string name of the color for display purposes
        r_min, r_max: min and max values for red channel
        g_min, g_max: min and max values for green channel  
        b_min, b_max: min and max values for blue channel
        pixel_threshold: minimum number of pixels needed to consider color present
    
    Returns:
        bool: True if color is detected above threshold
    """
    # Create color mask based on RGB ranges
    color_mask = (
        (img_array[:, :, 0] >= r_min) & (img_array[:, :, 0] <= r_max) &  # Red channel
        (img_array[:, :, 1] >= g_min) & (img_array[:, :, 1] <= g_max) &  # Green channel
        (img_array[:, :, 2] >= b_min) & (img_array[:, :, 2] <= b_max)    # Blue channel
    )
    # Count pixels matching the color
    pixel_count = np.sum(color_mask)
    print(f"{color_name.capitalize()} pixels found: {pixel_count}")
    return pixel_count > pixel_threshold

def is_red(img_array, pixel_threshold=25):
    # Red is typically high red, low green and blue
    return is_color(img_array, "red", r_min=200, r_max=255, g_min=0, g_max=100, b_min=0, b_max=100, pixel_threshold=pixel_threshold)

def is_yellow(img_array, pixel_threshold=20):
    # Yellow is typically high red and green, low blue
    return is_color(img_array, "yellow", r_min=200, r_max=255, g_min=200, g_max=255, b_min=0, b_max=100, pixel_threshold=pixel_threshold)

def is_purple(img_array):
    # Purple is typically high red and blue, low green
    return is_color(img_array, "purple", r_min=150, r_max=255, g_min=0, g_max=100, b_min=150, b_max=255, pixel_threshold=20)

def is_blue(img_array):
    # Blue is typically low red and green, high blue
    return is_color(img_array, "blue", r_min=0, r_max=100, g_min=0, g_max=100, b_min=150, b_max=255, pixel_threshold=20)

def is_object(img_array, object_name, threshhold_binary = 128, threshhold_difference=2000, print_diff=False):
    """ Compare the cropped area with the image of the object as png. Can be used for npc, items, areas, enemies"""
    object_reference = Image.open(f"assets/items/item_{object_name}.png")
    object_array = np.array(object_reference)
    # Compare arrays by looking at their norm only at values which are not black i.e. are bighter than threshhold_binary on average
    mask_reference = np.sum(object_array, axis=-1) > threshhold_binary
    mask_test = np.sum(img_array, axis=-1) > threshhold_binary
    
    # Save masks as images
    mask_reference_img = Image.fromarray((mask_reference * 255).astype(np.uint8))
    mask_test_img = Image.fromarray((mask_test * 255).astype(np.uint8))
    try:
        mask_reference_img.save("mask_reference.png")
        mask_test_img.save("mask_test.png")
    except Exception as e:
        print("Error saving mask images:", e)
    #print("Masks saved as mask_reference.png and mask_test.png")

    # Compute the difference
    diff = np.linalg.norm(object_array.astype(int) - img_array.astype(int))

    # Save this image glacial_stone_array.astype(int) - img_array.astype(int)
    diff_image = np.abs(object_array.astype(int) - img_array.astype(int)).astype(np.uint8)
    diff_image_pil = Image.fromarray(diff_image)
    diff_image_pil.save("diff_image.png")
    if print_diff:
        print("Difference :", diff)
    
    return diff < threshhold_difference # Below threshold_difference is considered a match

def check_next_item():
    """Check if the next item is of interest and pick it up if so."""
    # Simulate pressing key 'ä' to check the next item
    keyboard.press('ä')
    time.sleep(0.01)
    keyboard.release('ä')
    time.sleep(0.01)  # Wait a moment for the UI to update
    
    # Take a screenshot of a specific region (left, top, right, bottom)
    # Coordinates: x=860, y=55, width=180, height=15 to grab the correct area
    bbox = (860, 55, 1040, 70)  # (left, top, right, bottom)
    screenshot = ImageGrab.grab(bbox=bbox)
    
    # Save the screenshot (optional - for debugging)
    try:
        screenshot.save("item_check.png")
    except Exception as e:
        print("Error saving item check screenshot:", e)
    
    # Convert to numpy array for color analysis
    img_array = np.array(screenshot)

    if is_yellow(img_array):
        print("Yellow item detected!")
        pick_up_selected_item()
    elif is_object(img_array, "glacial_stone"):
        print("Glacial Stone detected!")
        pick_up_selected_item()
    elif is_object(img_array, "mesmer_tome"):
        print("Mesmer Tome detected!")
        pick_up_selected_item()
    elif is_object(img_array, "eggnog"):
        print("Eggnog detected!")
        pick_up_selected_item()
    elif is_object(img_array, "fruitcake"):
        print("Fruitcake detected!")
        pick_up_selected_item()
    elif is_object(img_array, "snowman_summoner"):
        print("Snowman Summoner detected!")
        pick_up_selected_item()
    elif is_object(img_array, "lockpick"):
        print("Lockpick detected!")
        pick_up_selected_item()
    elif is_object(img_array, "candy_cane_shard"):
        print("Candy Cane Shard detected!")
        pick_up_selected_item()
    else: 
        return False  # Not an item of interest
    return True  # Item of interest picked up

def check_next_enemy():
    """Check if there is an enemy in the next position."""
    # Simulate pressing key 'c' to check the next enemy
    keyboard.press('c')
    time.sleep(0.01)
    keyboard.release('c')
    time.sleep(0.01)  # Wait a moment for the UI to update
    
    # Take a screenshot of a specific region (left, top, right, bottom)
    bbox = (860, 55, 1040, 70) # (left, top, right, bottom)
    screenshot = ImageGrab.grab(bbox=bbox)
    
    center_x = 1800
    center_y = 150
    radius = 25
    bbox_compass = (center_x - radius, center_y - radius, center_x + radius, center_y + radius) # (left, top, right, bottom)
    screenshot_compass = ImageGrab.grab(bbox=bbox_compass)

    # Save the screenshot (optional - for debugging)
    screenshot.save("enemy_check.png")
    screenshot_compass.save("enemy_check_compass.png")
    # Convert to numpy array for color analysis
    img_array = np.array(screenshot)
    img_array_compass = np.array(screenshot_compass)
    
    if is_red(img_array_compass,1) or is_yellow(img_array_compass,1):
        print("Enemy detected on compass! Skipping pickup.")
        if (is_object(img_array, "vaettir_no_hp", 180, 4000,True) or 
            is_object(img_array, "vaettir_full_hp", 180, 4000,True) or 
            is_red(img_array)):
            print("Enemy detected! Skipping pickup.")
            return True
        else:
            print("False alarm, no enemy detected in main area.")
            return False
    else:
        print("No enemy detected.")
        return False


def pick_up_selected_item(waiting_item_seconds=1.0):
    print("Picking up item")
    keyboard.press(Key.space)
    time.sleep(0.01)
    keyboard.release(Key.space)
    time.sleep(waiting_item_seconds)  # Wait after picking up the item

if __name__ == "__main__":
    time.sleep(2)  # Give some time before checking
    for _ in range(1):  # Check 1 cycle
        check_next_item()
        time.sleep(0.5)  # Wait a bit before checking the next item
        check_next_enemy()