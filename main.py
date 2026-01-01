from pynput.keyboard import Key, Listener, Controller
import time
import threading
from PIL import ImageGrab
import numpy as np


import utils_item
import utils_areas
import utils_energy_management
from utils_skill_management import cast_shadowform, cast_way_of_perfection_and_master, cast_shroud_of_distress, cast_mantra_of_earth,cast_spike

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

def move_forward(duration):
    """Move forward for specified duration"""
    print(f"Moving forward for {duration} seconds")
    keyboard.press('w')
    time.sleep(duration)
    keyboard.release('w')

def move_backward(duration):
    """Move backward for specified duration"""
    print(f"Moving backward for {duration} seconds")
    keyboard.press('s')
    time.sleep(duration)
    keyboard.release('s')

def turn_left(duration):
    """Turn left for specified duration"""
    print(f"Turning left for {duration} seconds")
    keyboard.press('a')
    time.sleep(duration)
    keyboard.release('a')

def turn_right(duration):
    """Turn right for specified duration"""
    print(f"Turning right for {duration} seconds")
    keyboard.press('d')
    time.sleep(duration)
    keyboard.release('d')

# Global flag to track if 'q' was pressed
q_pressed = False
e_pressed = False

# Create a keyboard controller
keyboard = Controller()

# Start the keyboard listener in a separate thread
listener = Listener(on_press=on_press, on_release=on_release)
listener.start()
for i in range(25):
    print("Starting the automation script in...")
    for i in range(3, 0, -1):
        print(i)
        time.sleep(1)
    # Start run in bjora marches to jaga moraine area
    utils_areas.bjora_marches2jaga_moraine()  # Example call to set area
    utils_areas.jaga_moraine2jarnskeggi()  # Example call to set area
    utils_areas.pick_up_norn_blessing()  # Example call to pick up norn blessing

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
    
    # Movement configuration and state tracking
    dict_movement = {
        "move_forward_1": 10.0,
        "turn_right_1": 0.750,
        "move_forward_2": 11.0,
    }
    start_movement = True
    final_state = False
    current_movement_key = None
    current_movement_remaining = 0.0
    last_movement_time = 0
    movement_keys = list(dict_movement.keys())
    current_movement_index = 0
    movement_chunk_size = 1.0  # Split long movements into 0.5-second chunks


    # Get current time
    start_time = time.time()

    while True and time.time() - start_time < 500:
        time_passed_in_seconds = time.time() - start_time
        #print("time passed: ", time_passed_in_seconds)
        # Cast Shadowform every 20 seconds after it was last casted
        if ((time_passed_in_seconds - last_shadowform_cast_time)%20 > 0.0 and 
            (time_passed_in_seconds -  last_shadowform_cast_time)%20 < 2.0 
            and not shadowform_casted):
            cast_shadowform()
            print("Casting shadowform at ", time_passed_in_seconds, time.time() - start_time)
            shadowform_casted = True
            last_shadowform_cast_time = time.time() - start_time # This is the time when shadowform was last casted
            # Go to next iteration to avoid double casting
            if start_collecting and utils_item.check_next_enemy():
                print("Enemy detected during collecting, pausing collecting and go back to spike mode")
                start_spike = True
                start_collecting = False
                time.sleep(0.01)  # Wait a bit before checking again
                # Skip picking up items if enemy is detected
            continue
        # Reset flags after 18 seconds such that it maintains the enchantment for sure
        if shadowform_casted and time_passed_in_seconds - last_shadowform_cast_time >= 18.0:
            shadowform_casted = False

        # Cast Mantra of earth 2 seconds after shadowform was casted 
        if (not mantra_casted and time_passed_in_seconds> 20 and
            time_passed_in_seconds - last_shadowform_cast_time > 0.0 and
            time_passed_in_seconds - last_shadowform_cast_time < 2.0):
            print("Casting Mantra of Earth at ", time_passed_in_seconds)
            cast_mantra_of_earth()
            mantra_casted = True
            # Go to next iteration to avoid double casting
            continue
        # Reset mantra_casted flag after 0.5 seconds
        if mantra_casted and time_passed_in_seconds - last_shadowform_cast_time >= 3.5:
            mantra_casted = False

        # Cast Shroud of Distress every 50 seconds  after it was last casted
        if ((time_passed_in_seconds - last_shroud_of_distress_cast_time)%45 > 0.0 and 
            (time_passed_in_seconds - last_shroud_of_distress_cast_time)%45 < 45.0
            and not shroud_casted):
            print("Casting Shroud of Distress at ", time_passed_in_seconds)
            cast_shroud_of_distress()
            shroud_casted = True
            last_shroud_of_distress_cast_time = time.time() - start_time
            # Go to next iteration to avoid double casting
            continue
        # Reset flags after 45 seconds
        if shroud_casted and time_passed_in_seconds - last_shroud_of_distress_cast_time >= 45.0:
            shroud_casted = False

        # Cast Way of Perfection and Master every 30 seconds after it was last casted
        if ((time_passed_in_seconds - last_ways_cast_time)%30 > 0.0 and 
            (time_passed_in_seconds - last_ways_cast_time)%30 < 30.0
            and not ways_casted):
            print("Casting Way of Perfection and Master at ", time_passed_in_seconds)
            cast_way_of_perfection_and_master()
            ways_casted = True
            last_ways_cast_time = time.time() - start_time
            # Go to next iteration to avoid double casting
            continue
        # Reset flags after 30 seconds
        if ways_casted and time_passed_in_seconds - last_ways_cast_time >= 30.0:
            ways_casted = False
        
        # If spike is started, cast Wastrel's Demise every 3 seconds but not 3 seconds after and before shadowform
        if start_spike:
            if ((time_passed_in_seconds - last_shadowform_cast_time > 3.0 or last_shadowform_cast_time == 0) 
                and (time_passed_in_seconds - last_wastrels_demise_cast_time >= 3.0)):
                if not utils_item.check_next_enemy():
                    # Wait 0.2ö  seconds before next check
                    time.sleep(0.2)
                    if not utils_item.check_next_enemy():
                        print("Collecting since no enemies detected")
                        start_collecting = True
                        counter_irrelevant_items = 0
                        e_pressed = False  # Reset the flag so it doesn't trigger repeatedly
                        continue
                # Check if mana is above 50% before casting
                energy_img_array = utils_energy_management.get_energy_level()
                if energy_img_array < 50.0:
                    print("Mana below 50%, skipping Wastrel's Demise cast")
                    print("Current mana: ", energy_img_array)
                    continue
                print("Casting Wastrel's Demise at ", time_passed_in_seconds)
                if utils_item.check_next_enemy():
                    cast_spike(True)
                nearest_enemy = not nearest_enemy  # Alternate between nearest and next enemy
                last_wastrels_demise_cast_time = time_passed_in_seconds
        
        if start_collecting and counter_irrelevant_items < 10:
            start_spike = False
            if utils_item.check_next_item():
                counter_irrelevant_items = 0  # Reset counter if an item of interest is found
                print("Item of interest picked up!")
                time.sleep(0.3)  # Wait a bit before checking the next item
            else:
                counter_irrelevant_items += 1
                print("Irrelevant item encountered. Counter: ", counter_irrelevant_items)
        if counter_irrelevant_items >= 10:
            # Programm finished collecting 10 items, stop the collecting process
            print("Collecting finished")
            start_collecting = False
            break
        

        if final_state and not start_spike and not start_collecting:
            if time.time() - last_movement_time > 20:
                # Enable spike flag after 20 seconds of no movement
                start_spike = True
                print("No movement for 20 seconds, enabling spike mode")

        # Handle movement when not casting spells and not collecting
        if (start_movement and not start_collecting and not start_spike and 
            current_movement_index < len(movement_keys) and
            shadowform_casted and shroud_casted and ways_casted):
            
            # Initialize new movement if needed
            if current_movement_key is None:
                current_movement_key = movement_keys[current_movement_index]
                current_movement_remaining = dict_movement[current_movement_key]
                print(f"Starting movement: {current_movement_key} for {current_movement_remaining} seconds")
            
            # Execute movement in chunks
            if current_movement_remaining > 0:
                # Determine chunk duration (smaller of remaining time or chunk size)
                chunk_duration = min(current_movement_remaining, movement_chunk_size)
                
                # Execute the appropriate movement
                if "move_forward" in current_movement_key:
                    move_forward(chunk_duration)
                elif "move_backward" in current_movement_key:
                    move_backward(chunk_duration)
                elif "turn_left" in current_movement_key:
                    turn_left(chunk_duration)
                elif "turn_right" in current_movement_key:
                    turn_right(chunk_duration)
                
                # Update remaining time
                current_movement_remaining -= chunk_duration
                
                # If movement is complete, move to next movement
                if current_movement_remaining <= 0:
                    print(f"Completed movement: {current_movement_key}")
                    current_movement_index += 1
                    current_movement_key = None
                    
                    # Check if all movements are complete
                    if current_movement_index >= len(movement_keys):
                        print("All movements completed")
                        start_movement = False
                        final_state = True
                        last_movement_time = time.time()

        # Start collecting after 240 seconds of runtime
        if time_passed_in_seconds > 300 and not start_collecting:
            print("Starting collecting after 300 seconds")
            start_collecting = True
            if start_spike:
                start_spike = False  # Disable spike mode when starting collecting

        time.sleep(0.025)  # Sleep to prevent high CPU usage


    # Press x once for a u turn in game  
    keyboard.press('x')
    time.sleep(0.01)
    keyboard.release('x')

    # Move forward 5 seconds to get back
    move_forward(8.0)
    utils_areas.jaga_moraine2jarnskeggi(12.0)  # Example call to go to jarnskeggi area
    utils_areas.bjora_marches2jaga_moraine() # Works also the other way around
    #utils_areas.go2sacred_altar2jarnskeggi2bjora_marches()  # Example call to go to sacred altar area
