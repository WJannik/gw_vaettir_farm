import time
from pynput.keyboard import Key, Controller
from utils_general import generate_bbox, capture_and_process_region, is_yellow, is_object
from utils_general import pick_up_selected_object
# Create a keyboard controller
keyboard = Controller()

items_of_interest = [
    "glacial_stone",
    "mesmer_tome",
    "eggnog",
    "fruitcake",
    "snowman_summoner",
    "lockpick",
    "candy_cane_shard"
]

def check_next_item():
    """Check if the next item is of interest and pick it up if so."""
    # Simulate pressing key 'ä' to check the next item
    keyboard.press('ä')
    time.sleep(0.01)
    keyboard.release('ä')
    time.sleep(0.01)  # Wait a moment for the UI to update
    
    # Generate bounding box and capture the region
    bbox = generate_bbox(860, 55, 180, 15)  # x=860, y=55, width=180, height=15
    screenshot, img_array = capture_and_process_region(bbox, "item_check")

    if is_yellow(img_array):
        print("Yellow item detected!")
        pick_up_selected_object()
        return True
    for item in items_of_interest:
        if is_object(img_array, item):
            print(f"{item.replace('_', ' ').title()} detected!")
            pick_up_selected_object()
            return True
    return False

if __name__ == "__main__":
    time.sleep(2)  # Give some time before checking
    for _ in range(1):  # Check 1 cycle
        check_next_item()
        time.sleep(0.5)  # Wait a bit before checking the next item