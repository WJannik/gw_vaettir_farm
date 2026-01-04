import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
from pynput.mouse import Button, Listener as MouseListener
from pynput import mouse


# Create a keyboard controller
keyboard = Controller()
# Create a mouse controller
mouse_controller = mouse.Controller()

def generate_bbox(x, y, width, height):
    """
    Generate a bounding box tuple from position and dimensions.
    
    Args:
        x: x-coordinate of the top-left corner
        y: y-coordinate of the top-left corner
        width: width of the bounding box
        height: height of the bounding box
    
    Returns:
        tuple: (left, top, right, bottom) bounding box coordinates
    """
    return (x, y, x + width, y + height)

def generate_center_bbox(center_x, center_y, radius):
    """
    Generate a bounding box centered around a point with given radius.
    
    Args:
        center_x: x-coordinate of the center
        center_y: y-coordinate of the center
        radius: radius from center to edge
    
    Returns:
        tuple: (left, top, right, bottom) bounding box coordinates
    """
    return (center_x - radius, center_y - radius, center_x + radius, center_y + radius)

def capture_and_process_region(bbox, debug_filename=None, save_debug=True):
    """
    Capture a screenshot of a specific region and convert to numpy array.
    
    Args:
        bbox: tuple of (left, top, right, bottom) coordinates
        debug_filename: filename to save debug image (without extension)
        save_debug: whether to save debug images
    
    Returns:
        tuple: (PIL Image, numpy array) of the captured region
    """
    screenshot = ImageGrab.grab(bbox=bbox)
    
    # Save debug image if requested
    if save_debug and debug_filename:
        try:
            screenshot.save(f"gw_vaettir_bot/debug_images/{debug_filename}.png")
        except Exception as e:
            print(f"Error saving debug image {debug_filename}.png:", e)
    
    # Convert to numpy array
    img_array = np.array(screenshot)
    return screenshot, img_array

def compare_with_reference_image(img_array, reference_name, asset_path="gw_vaettir_bot/assets/items", 
                                threshold_binary=128, threshold_difference=2000, 
                                print_diff=False, save_debug=True):
    """
    Compare an image array with a reference image from assets.
    
    Args:
        img_array: numpy array of the image to compare
        reference_name: name of the reference image (without extension)
        asset_path: path to the assets folder
        threshold_binary: threshold for binary mask creation
        threshold_difference: threshold for considering images similar
        print_diff: whether to print the difference value
        save_debug: whether to save debug images
    
    Returns:
        bool: True if images are similar (below threshold_difference)
    """
    try:
        reference_image = Image.open(f"{asset_path}/item_{reference_name}.png")
        reference_array = np.array(reference_image)
        
        # Create binary masks
        mask_reference = np.sum(reference_array, axis=-1) > threshold_binary
        mask_test = np.sum(img_array, axis=-1) > threshold_binary
        
        # Save debug masks if requested
        if save_debug:
            try:
                import os
                debug_dir = "gw_vaettir_bot/debug_images"
                if not os.path.exists(debug_dir):
                    os.makedirs(debug_dir)
                    
                mask_reference_img = Image.fromarray((mask_reference * 255).astype(np.uint8))
                mask_test_img = Image.fromarray((mask_test * 255).astype(np.uint8))
                mask_reference_img.save(f"{debug_dir}/mask_reference.png")
                mask_test_img.save(f"{debug_dir}/mask_test.png")
                
                # Save difference image
                diff_image = np.abs(reference_array.astype(int) - img_array.astype(int)).astype(np.uint8)
                diff_image_pil = Image.fromarray(diff_image)
                diff_image_pil.save(f"{debug_dir}/diff_image.png")
            except Exception as e:
                print("Error saving debug images:", e)
        
        # Compute the difference
        diff = np.linalg.norm(reference_array.astype(int) - img_array.astype(int))
        
        if print_diff:
            print(f"Difference for {reference_name}:", diff)
        
        return diff < threshold_difference
    
    except Exception as e:
        print(f"Error comparing with reference image {reference_name}:", e)
        return False

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
    #print(f"{color_name.capitalize()} pixels found: {pixel_count}")
    return pixel_count > pixel_threshold

def is_red(img_array, pixel_threshold=25):
    # Red is typically high red, low green and blue
    return is_color(img_array, "red", r_min=128, r_max=255, g_min=0, g_max=100, b_min=0, b_max=100, pixel_threshold=pixel_threshold)

def is_yellow(img_array, pixel_threshold=10):
    # Yellow is typically high red and green, low blue
    return is_color(img_array, "yellow", r_min=200, r_max=255, g_min=200, g_max=255, b_min=0, b_max=100, pixel_threshold=pixel_threshold)

def is_purple(img_array):
    # Purple is typically high red and blue, low green
    return is_color(img_array, "purple", r_min=150, r_max=255, g_min=0, g_max=100, b_min=150, b_max=255, pixel_threshold=20)

def is_blue(img_array):
    # Blue is typically low red and green, high blue
    return is_color(img_array, "blue", r_min=0, r_max=100, g_min=0, g_max=100, b_min=150, b_max=255, pixel_threshold=20)

def is_object(img_array, object_name, threshhold_binary=128, threshhold_difference=2000, print_diff=False, asset_path="gw_vaettir_bot/assets/items"):
    """ Compare the cropped area with the image of the object as png. Can be used for npc, items, areas, enemies"""
    return compare_with_reference_image(
        img_array, object_name, asset_path=asset_path,
        threshold_binary=threshhold_binary, 
        threshold_difference=threshhold_difference, 
        print_diff=print_diff
    )

def pick_up_selected_object(waiting_item_seconds=1.0):
    """Pick up the currently selected item."""
    #print("Picking up item")
    keyboard.press(Key.space)
    time.sleep(0.01)
    keyboard.release(Key.space)
    time.sleep(waiting_item_seconds)  # Wait after picking up the item

def click_at_position(x, y, button=Button.left, clicks=1, delay=0.1):
    """
    Click at a specific position on the screen
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate  
        button: Mouse button to click (Button.left, Button.right, Button.middle)
        clicks (int): Number of clicks (1 for single click, 2 for double click)
        delay (float): Delay between clicks for multi-click
    """    
    # Move mouse to position
    mouse_controller.position = (x, y)
    time.sleep(0.05)  # Small delay to ensure movement
    
    # Perform clicks
    for _ in range(clicks):
        mouse_controller.click(button)
        if clicks > 1 and _ < clicks - 1:  # Add delay between multiple clicks
            time.sleep(delay)

def right_click_at_position(x, y):
    """Right click at specific position"""
    click_at_position(x, y, button=Button.right)

def double_click_at_position(x, y):
    """Double click at specific position"""
    click_at_position(x, y, clicks=2, delay=0.1)

def drag_to_position(start_x, start_y, end_x, end_y, duration=1.0):
    """
    Drag from start position to end position
    
    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates  
        duration: Time in seconds to complete the drag
    """    
    # Move to start position
    mouse_controller.position = (start_x, start_y)
    time.sleep(0.1)
    
    # Press and hold mouse button
    mouse_controller.press(Button.left)
    
    # Calculate steps for smooth movement
    steps = int(duration * 60)  # 60 steps per second
    for i in range(steps + 1):
        progress = i / steps
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        mouse_controller.position = (current_x, current_y)
        time.sleep(duration / steps)
    
    # Release mouse button
    mouse_controller.release(Button.left)

if __name__== "__main__":
    # Example usage
    bbox = generate_bbox(860, 55, 180, 15)
    screenshot, img_array = capture_and_process_region(bbox, "test_region")
    # Compare the imge with the assest image at assets/npc/jarnskeggi.png
    if is_object(img_array, "jarnskeggi", print_diff=True, asset_path="gw_vaettir_bot/assets/npcs"):
        print("Jarnskeggi detected!")
    else:
        print("Jarnskeggi not detected.")
        # Compare the imge with the assest image at assets/npc/kobach_the_ferocious.png
    if is_object(img_array, "kobach_the_ferocious", print_diff=True, asset_path="gw_vaettir_bot/assets/npcs"):
        print("Kobach the Ferocious detected!")
    else:
        print("Kobach the Ferocious not detected.")