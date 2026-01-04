import time
from PIL import ImageGrab, Image
import numpy as np
from pynput.keyboard import Key, Listener, Controller
# Create a keyboard controller
keyboard = Controller()




def get_energy_bar_snapshot():
    """ Capture a screenshot of the energy bar area at the bottom middle of the screen """
    bbox = (970, 960, 1175, 966)
    screenshot = ImageGrab.grab(bbox=bbox)
    img_array = np.array(screenshot)
    return img_array

def get_energy_level():
    """ Analyze the energy bar image to determine the current energy level """
    img_array = get_energy_bar_snapshot()
    # The energy bar is typically blue, so we can analyze the blue channel
    blue_channel = img_array[:, :, 2]
    # Sum each column to find the filled portion
    blue_column_sums = np.sum(blue_channel > 80, axis=0)
    # How many columns have a significant amount of blue pixels
    filled_columns = np.sum(blue_column_sums >= (img_array.shape[0]*1.0))
    total_columns = img_array.shape[1]
    energy_percentage = (filled_columns / total_columns) * 100
    print(f"Energy level: {energy_percentage:.2f}%")
    return energy_percentage

if __name__ == "__main__":
    for i in range(50):
        img_array = get_energy_bar_snapshot()
        img = Image.fromarray(img_array)
        energy_level = get_energy_level()
        # Save image
        img.save("energy_bar_snapshot.png")
        #img.show()
        # Wait one second before next capture
        time.sleep(1)