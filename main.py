from pynput.keyboard import Key, Listener, Controller
import time
import threading
from PIL import ImageGrab
import numpy as np


import utils_item
import utils_areas
# Global flag to track if 'q' was pressed
q_pressed = False
e_pressed = False
# Keyboard listener function
def on_press(key):
    global q_pressed, e_pressed
    try:
        if key.char == 'q':
            print("Q key detected!")
            q_pressed = True
        if key.char == 'e':
            print("E key detected!")
            e_pressed = True
    except AttributeError:
        # Special keys (like ctrl, alt, etc.) don't have a char attribute
        pass

def on_release(key):
    # Stop listener on ESC key
    if key == Key.esc:
        print("ESC pressed - stopping listener")
        return False

print("Starting the automation script in...")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

# Create a keyboard controller
keyboard = Controller()

# Start the keyboard listener in a separate thread
listener = Listener(on_press=on_press, on_release=on_release)
listener.start()

utils_areas.bjora_marches2jaga_moraine()  # Example call to set area
utils_areas.jaga_moraine2jarnskeggi()  # Example call to set area
utils_areas.pick_up_norn_blessing()  # Example call to pick up norn blessing

def cast_shadowform():
    print("Casting Shadowform")
    # Simulate pressing keys '1' and '2' with a small delay and hold it for 0.1 seconds
    keyboard.press('1')
    time.sleep(0.01)
    keyboard.release('1')
    time.sleep(0.10)
    keyboard.press('2')
    time.sleep(0.01)
    keyboard.release('2')
    time.sleep(1.25) # Wait for 1 second to simulate casting time

def cast_way_of_perfection_and_master():
    print("Casting Way of Perfection and Master")
    # Simulate pressing keys '4' and '5' with a small delay and hold it for 0.1 seconds
    keyboard.press('4')
    time.sleep(0.01)
    keyboard.release('4')
    time.sleep(0.5)
    keyboard.press('5')
    time.sleep(0.01)
    keyboard.release('5')
    time.sleep(0.5)

def cast_shroud_of_distress():
    print("Casting Shroud of Distress")
    # Simulate pressing key '3' with a small delay and hold it for 0.1 seconds
    keyboard.press('3')
    time.sleep(0.01)
    keyboard.release('3')
    time.sleep(1.25) # Wait for 1 second to simulate casting time


def cast_mantra_of_earth():
    print("Casting Mantra of Earth")
    # Simulate pressing key '6' with a small delay and hold it for 0.1 seconds
    keyboard.press('8')
    time.sleep(0.01)
    keyboard.release('8')


def cast_wastrels_demise(nearest_enemy=True):
    if nearest_enemy:
        # Get nearest enemy - placeholder for actual implementation by pressing c key
        keyboard.press('c')
        time.sleep(0.01)
        keyboard.release('c')
        time.sleep(0.05) # Wait for 0.05 second to ensure target
        print("Casting Wastrel's Demise on nearest enemy")
    else:
        print("Casting Wastrel's Demise on next target")
        # Get next enemy by pressing tab key
        keyboard.press(Key.tab)
        time.sleep(0.01)
        keyboard.release(Key.tab)
        time.sleep(0.05)  # Small delay before casting

    # Simulate pressing key '7' with a small delay and hold it for 0.1 seconds
    keyboard.press('7')
    time.sleep(0.01)
    keyboard.release('7')
    time.sleep(0.5) # Wait for 0.5 second to simulate casting time

# Get current time
start_time = time.time()
# Last cast times of spells
last_shadowform_cast_time = 0
last_shroud_of_distress_cast_time = 0
last_ways_cast_time = 0
last_wastrels_demise_cast_time = 0
# Flags to track enchantment states and other flags
shadowform_casted = False
shroud_casted = False
ways_casted = False
mantra_casted = False
start_spike = False
nearest_enemy = True
start_collecting = False
# Counter for collecting items
counter_irrelevant_items = 0 

while True and time.time() - start_time < 240:
    time_passed_in_seconds = time.time() - start_time
    print("time passed: ", time_passed_in_seconds)
    # Cast Shadowform every 20 seconds after it was last casted
    if ((time_passed_in_seconds - last_shadowform_cast_time)%20 > 0.0 and 
        (time_passed_in_seconds -  last_shadowform_cast_time)%20 < 2.0 
        and not shadowform_casted):
        cast_shadowform()
        print("Casting shadowform at ", time_passed_in_seconds, time.time() - start_time)
        shadowform_casted = True
        last_shadowform_cast_time = time.time() - start_time # This is the time when shadowform was last casted
        # Go to next iteration to avoid double casting
        continue
    # Reset flags after 15 seconds
    if shadowform_casted and time_passed_in_seconds - last_shadowform_cast_time >= 19.5:
        shadowform_casted = False

    # Cast Mantra of earth 3 seconds after shadowform was casted 
    if (not mantra_casted and time_passed_in_seconds> 20 and
        time_passed_in_seconds - last_shadowform_cast_time > 2.0 and
        time_passed_in_seconds - last_shadowform_cast_time < 4.0):
        print("Casting Mantra of Earth at ", time_passed_in_seconds)
        cast_mantra_of_earth()
        mantra_casted = True
        # Go to next iteration to avoid double casting
        continue
    # Reset mantra_casted flag after 15 seconds
    if mantra_casted and time_passed_in_seconds - last_shadowform_cast_time >= 15:
        mantra_casted = False

    # Cast Shroud of Distress every 50 seconds  after it was last casted
    if ((time_passed_in_seconds - last_shroud_of_distress_cast_time)%46 > 1.0 and 
        (time_passed_in_seconds - last_shroud_of_distress_cast_time)%46 < 5.0
        and not shroud_casted):
        print("Casting Shroud of Distress at ", time_passed_in_seconds)
        cast_shroud_of_distress()
        shroud_casted = True
        last_shroud_of_distress_cast_time = time.time() - start_time
        # Go to next iteration to avoid double casting
        continue
    # Reset flags after 15 seconds
    if shroud_casted and time_passed_in_seconds - last_shroud_of_distress_cast_time >= 15:
        shroud_casted = False

    # Cast Way of Perfection and Master every 30 seconds after it was last casted
    if ((time_passed_in_seconds - last_ways_cast_time)%30 > 1.0 and 
        (time_passed_in_seconds - last_ways_cast_time)%30 < 5.0
        and not ways_casted):
        print("Casting Way of Perfection and Master at ", time_passed_in_seconds)
        cast_way_of_perfection_and_master()
        ways_casted = True
        last_ways_cast_time = time.time() - start_time
        # Go to next iteration to avoid double casting
        continue
    # Reset flags after 15 seconds
    if ways_casted and time_passed_in_seconds - last_ways_cast_time >= 15:
        ways_casted = False

    # If I press 'q' while the script runs, set the start_spike flag to True
    if q_pressed:
        print("Spike started by user")
        start_spike = True
        q_pressed = False  # Reset the flag so it doesn't trigger repeatedly
    
    # If spike is started, cast Wastrel's Demise every 3 seconds but not 3 seconds after and before shadowform
    if start_spike:
        if ((time_passed_in_seconds - last_shadowform_cast_time > 3.0 or last_shadowform_cast_time == 0) 
            and (time_passed_in_seconds - last_wastrels_demise_cast_time >= 3.0)):
            if not utils_item.check_next_enemy():
                # Wait 0.2 seconds before next check
                time.sleep(0.2)
                if not utils_item.check_next_enemy():
                    print("Collecting started by user")
                    start_collecting = True
                    counter = 0 
                    e_pressed = False  # Reset the flag so it doesn't trigger repeatedly
            print("Casting Wastrel's Demise at ", time_passed_in_seconds)
            cast_wastrels_demise(nearest_enemy)
            nearest_enemy = not nearest_enemy  # Alternate between nearest and next enemy
            last_wastrels_demise_cast_time = time_passed_in_seconds
    
    if start_collecting and counter_irrelevant_items < 20:
        start_spike = False
        if utils_item.check_next_item():
            counter_irrelevant_items = 0  # Reset counter if an item of interest is found
            print("Item of interest picked up!")
            time.sleep(0.3)  # Wait a bit before checking the next item
        else:
            counter_irrelevant_items += 1
            print("Irrelevant item encountered. Counter: ", counter_irrelevant_items)
    if counter_irrelevant_items >= 20:
        # Programm finished collecting 20 items, stop the collecting process
        print("Collecting finished")
        start_collecting = False
        break
        
        

    time.sleep(0.1)  # Sleep to prevent high CPU usage

utils_areas.go2sacred_altar2jarnskeggi2bjora_marches()  # Example call to go to sacred altar area
