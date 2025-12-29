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
    print(f"Clicking at position ({x}, {y})")
    
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
    print(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
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


def bjora_marches2jaga_moraine():
    print("Setting area to Bjora Marches to Jaga Moraine")
    # Simulate pressing keys to set the area
    keyboard.press('ö')
    time.sleep(0.01)
    keyboard.release('ö')
    time.sleep(0.1)  # Wait for the area to load
    pick_up_selected_item(10.0)  # Wait longer for area change

def jaga_moraine2jarnskeggi():
    print("Go from Jaga Moraine to Jarnskeggi")
    # Simulate pressing keys to set the area
    keyboard.press('v')
    time.sleep(0.01)
    keyboard.release('v')
    time.sleep(0.1)  # Wait for the area to load
    pick_up_selected_item(7.5)  # Wait longer for area change

def pick_up_norn_blessing():
    print("Picking up Norn Blessing")
    # Left mouse click at x = 1000 and y = 1000 to get norn blessing
    click_at_position(900, 575)

def pick_up_selected_item(waiting_item_seconds=1.0):
    print("Picking up item")
    keyboard.press(Key.space)
    time.sleep(0.01)
    keyboard.release(Key.space)
    time.sleep(waiting_item_seconds)  # Wait after picking up the item


def go2sacred_altar2jarnskeggi2bjora_marches():
    # Get current time 
    time_last_iteration = time.time()
    while time.time() - time_last_iteration < 5:
        go_to_area_as_object("sacred_altar")
    print("I SHOULD BE IN BJORA MARCHES NOW. TIME TO RESTART EVERYTHING.")


def go_to_area_as_object(area = "sacred_altar"):

    # Check if the item is of interesst. This includes yellow items, glacial stone, mesmer tomes, etc.
    print("Checking for yellow item")
    # Simulate pressing key 'ä' to check the next itemitem
    keyboard.press('ä')
    time.sleep(0.01)
    keyboard.release('ä')
    time.sleep(0.01)  # Wait a moment for the UI to update
    
    # Take a screenshot of a specific region (left, top, right, bottom)
    # Coordinates: x=860, y=55, width=180, height=15 to grab the correct area
    bbox = (860, 55, 1040, 70)  # (left, top, right, bottom)
    screenshot = ImageGrab.grab(bbox=bbox)
    
    # Save the screenshot (optional - for debugging)
    screenshot.save("area_check.png")
    
    # Convert to numpy array for color analysis
    img_array = np.array(screenshot)
 
    def is_item(img_array, area_name):
        """ Compare the cropped area with the image with name item_city.png """
        glacial_stone_reference = Image.open(f"assets/areas/item_{area_name}.png")
        glacial_stone_array = np.array(glacial_stone_reference)
        print(np.shape(img_array), np.shape(glacial_stone_array))
        # Compare arrays by looking at their norm only at values which are not black i.e. are bighter than 50 on average
        mask_reference = np.sum(glacial_stone_array, axis=-1) > 128
        mask_test = np.sum(img_array, axis=-1) > 128
        
        # Save masks as images
        mask_reference_img = Image.fromarray((mask_reference * 255).astype(np.uint8))
        mask_test_img = Image.fromarray((mask_test * 255).astype(np.uint8))
        
        mask_reference_img.save("mask_reference.png")
        mask_test_img.save("mask_test.png")
        print("Masks saved as mask_reference.png and mask_test.png")

        # Compute the difference
        diff = np.linalg.norm(glacial_stone_array.astype(int) - img_array.astype(int))

        # Save this image glacial_stone_array.astype(int) - img_array.astype(int)
        diff_image = np.abs(glacial_stone_array.astype(int) - img_array.astype(int)).astype(np.uint8)
        diff_image_pil = Image.fromarray(diff_image)
        diff_image_pil.save("diff_image.png")
        print("Difference :", diff)
        
        return diff < 2000 # Below 2000 is considered a match
    

    if is_item(img_array, area):
        print("Area detected!")
        pick_up_selected_item(10.0)  # Wait longer for area change
        # Go to next ally
        keyboard.press('v')
        time.sleep(0.01)
        keyboard.release('v')
        time.sleep(0.01)  # Wait a moment for the UI to update
        pick_up_selected_item(15)  # Wait longer for area change
        keyboard.press('ö')
        time.sleep(0.01)
        keyboard.release('ö')
        time.sleep(0.01)  # Wait a moment for the UI to update
        pick_up_selected_item(15)  # Wait longer for area change


if __name__ == "__main__":
    time.sleep(2)  # Additional wait to ensure item is picked up
    if False:  # Change to True to test area changing functions
        bjora_marches2jaga_moraine()  # Example call to set area
        jaga_moraine2jarnskeggi()  # Example call to set area
        pick_up_norn_blessing()  # Example call to pick up norn blessing
    go2sacred_altar2jarnskeggi2bjora_marches()  # Example call to go to sacred altar area
