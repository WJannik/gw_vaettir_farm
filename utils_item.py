import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
# Create a keyboard controller
keyboard = Controller()

# Check if item is yellow
def check_next_item(enemy_check=False):
    # Check if the item is of interesst. This includes yellow items, glacial stone, mesmer tomes, etc.
    print("Checking for yellow item")

    if enemy_check:
        # Simulate pressing key 'c' to check the next itemitem
        keyboard.press('c')
        time.sleep(0.01)
        keyboard.release('c')
        time.sleep(0.01)  # Wait a moment for the UI to update
    else:
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
    screenshot.save("item_check.png")
    
    # Convert to numpy array for color analysis
    img_array = np.array(screenshot)
    

    def is_red(img_array):
        # Check for red color (you can adjust these RGB ranges)
        # Red is typically high red, low green and blue
        red_mask = (
            (img_array[:, :, 0] > 200) &  # Red channel > 200
            (img_array[:, :, 1] < 100) &  # Green channel < 100
            (img_array[:, :, 2] < 100)    # Blue channel < 100
        )
        # Count red pixels
        red_pixel_count = np.sum(red_mask)
        print(f"Red pixels found: {red_pixel_count}")
        return red_pixel_count > 50  # Adjust threshold as needed

    if enemy_check:
        if is_red(img_array):
            print("Enemy item detected! Skipping pickup.")
            return True
        else:
            print("No enemy item detected.")
            return False

    # Check if it is yellow by analyzing pixel colors
    def is_yellow(img_array):
        # Check for yellow color (you can adjust these RGB ranges)
        # Yellow is typically high red and green, low blue
        yellow_mask = (
            (img_array[:, :, 0] > 200) &  # Red channel > 200
            (img_array[:, :, 1] > 200) &  # Green channel > 200
            (img_array[:, :, 2] < 100)    # Blue channel < 100
        )
        # Count yellow pixels
        yellow_pixel_count = np.sum(yellow_mask)
        print(f"Yellow pixels found: {yellow_pixel_count}")
        return yellow_pixel_count > 20  # Adjust threshold as needed
    
    def is_purple(img_array):
        # Check for purple color (you can adjust these RGB ranges)
        # Purple is typically high red and blue, low green
        purple_mask = (
            (img_array[:, :, 0] > 150) &  # Red channel > 150
            (img_array[:, :, 1] < 100) &  # Green channel < 100
            (img_array[:, :, 2] > 150)    # Blue channel > 150
        )
        # Count purple pixels
        purple_pixel_count = np.sum(purple_mask)
        print(f"Purple pixels found: {purple_pixel_count}")
        return purple_pixel_count > 20  # Adjust threshold as needed
    
    def is_blue(img_array):
        # Check for blue color (you can adjust these RGB ranges)
        # Blue is typically low red and green, high blue
        blue_mask = (
            (img_array[:, :, 0] < 100) &  # Red channel < 100
            (img_array[:, :, 1] < 100) &  # Green channel < 100
            (img_array[:, :, 2] > 150)    # Blue channel > 150
        )
        # Count blue pixels
        blue_pixel_count = np.sum(blue_mask)
        print(f"Blue pixels found: {blue_pixel_count}")
        return blue_pixel_count > 20  # Adjust threshold as needed
    
    def is_item(img_array, item_name):
        """ Compare the cropped area with the image with name item_city.png """
        glacial_stone_reference = Image.open(f"assets/items/item_{item_name}.png")
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
    

    if is_yellow(img_array):
        print("Yellow item detected!")
        pick_up_selected_item()
    elif is_item(img_array, "glacial_stone"):
        print("Glacial Stone detected!")
        pick_up_selected_item()
    elif is_item(img_array, "mesmer_tome"):
        print("Mesmer Tome detected!")
        pick_up_selected_item()
    elif is_item(img_array, "eggnog"):
        print("Eggnog detected!")
        pick_up_selected_item()
    elif is_item(img_array, "fruitcake"):
        print("Fruitcake detected!")
        pick_up_selected_item()
    elif is_item(img_array, "snowman_summoner"):
        print("Snowman Summoner detected!")
        pick_up_selected_item()
    elif is_item(img_array, "lockpick"):
        print("Lockpick detected!")
        pick_up_selected_item()
    elif is_item(img_array, "candy_cane_shard"):
        print("Candy Cane Shard detected!")
        pick_up_selected_item()


def pick_up_selected_item(waiting_item_seconds=1.0):
    print("Picking up item")
    keyboard.press(Key.space)
    time.sleep(0.01)
    keyboard.release(Key.space)
    time.sleep(waiting_item_seconds)  # Wait after picking up the item

if __name__ == "__main__":
    time.sleep(2)  # Give some time before checking
    for _ in range(1):  # Check 5 items
        check_next_item()
        time.sleep(0.5)  # Wait a bit before checking the next item