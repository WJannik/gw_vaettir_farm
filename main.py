from pynput.keyboard import Key, Listener, Controller
import time

import utils_item
import utils_areas
import utils_energy_management
from utils_skill_management import cast_shadowform, cast_way_of_perfection_and_master, cast_shroud_of_distress, cast_mantra_of_earth,cast_spike
from utils_movement import handle_movement_sequence

# Create a keyboard controller
keyboard = Controller()

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
    phase_spike = False
    nearest_enemy = True
    phase_collecting = False
    minimal_enchantment_maintained = False
    turn_around_done = False
    # Counter for collecting items
    counter_irrelevant_items = 0 

    # Movement configuration and state tracking
    dict_movement_forwards = {
        "move_forward_1": 10.0,
        "turn_right_1": 0.65,
        "move_forward_2": 11.0,
    }
    dict_movement_reverse = {
        "move_forward_1": 8.0,
    }
    start_movement = True
    reached_final_position = False
    current_movement_key_forward = None
    current_movement_remaining_forward = 0.0
    current_movement_key_reverse = None
    current_movement_remaining_reverse = 0.0
    last_movement_time = 0
    movement_keys_forwards = list(dict_movement_forwards.keys())
    movement_keys_reverse = list(dict_movement_reverse.keys())
    current_movement_index_forward = 0
    current_movement_index_reverse = 0
    movement_chunk_size = 1.0  # Split long movements into 0.5-second chunks


    # Get current time
    start_time = time.time()

    while True and time.time() - start_time < 500:
        time_passed_in_seconds = time.time() - start_time
        ######### ENCHANTMENT UP KEEP LOGIC #########

        # Cast Shadowform every 20 seconds after it was last casted
        if ((time_passed_in_seconds - last_shadowform_cast_time)%20 >= 0.0 and 
            (time_passed_in_seconds -  last_shadowform_cast_time)%20 < 2.0 
            and not shadowform_casted):
            cast_shadowform()
            shadowform_casted = True
            last_shadowform_cast_time = time.time() - start_time # This is the time when shadowform was last casted
            # Go to next iteration to avoid double casting
            continue
        # Reset flags after 18 seconds such that it maintains the enchantment for sure
        if shadowform_casted and time_passed_in_seconds - last_shadowform_cast_time >= 18.0:
            shadowform_casted = False

        # Cast Mantra of earth 2 seconds after shadowform was casted 
        if (not mantra_casted and time_passed_in_seconds> 20 and
            time_passed_in_seconds - last_shadowform_cast_time > 0.0 and
            time_passed_in_seconds - last_shadowform_cast_time < 2.0
            and not minimal_enchantment_maintained):
            cast_mantra_of_earth()
            mantra_casted = True
            # Go to next iteration to avoid double casting
            continue
        # Reset mantra_casted flag after 0.5 seconds
        if mantra_casted and time_passed_in_seconds - last_shadowform_cast_time >= 3.5:
            mantra_casted = False

        # Cast Shroud of Distress every 45 seconds  after it was last casted
        if ((time_passed_in_seconds - last_shroud_of_distress_cast_time)%45 > 0.0 and 
            (time_passed_in_seconds - last_shroud_of_distress_cast_time)%45 < 45.0
            and not shroud_casted and not minimal_enchantment_maintained):
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
            cast_way_of_perfection_and_master()
            ways_casted = True
            last_ways_cast_time = time.time() - start_time
            # Go to next iteration to avoid double casting
            continue
        # Reset flags after 30 seconds
        if ways_casted and time_passed_in_seconds - last_ways_cast_time >= 30.0:
            ways_casted = False
        
        ######### COLLECTING LOGIC #########
        if phase_collecting and counter_irrelevant_items < 10:
            phase_spike = False
            minimal_enchantment_maintained = True
            if utils_item.check_next_item():
                counter_irrelevant_items = 0  # Reset counter if an item of interest is found
                time.sleep(0.3)  # Wait a bit before checking the next item
            else:
                counter_irrelevant_items += 1
                print("Irrelevant item encountered. Counter: ", counter_irrelevant_items)
        if phase_collecting and counter_irrelevant_items >= 10:
            # Programm finished collecting 10 items, stop the collecting process
            print("Collecting finished")
            phase_collecting = False
            if not turn_around_done:
                # Press x once for a u turn in game and change flag 
                print("Performing U-turn after collecting")
                keyboard.press('x')
                time.sleep(0.01)
                keyboard.release('x')
                turn_around_done = True


        ################ SPIKE LOGIC ################

        if reached_final_position and not phase_spike and not phase_collecting and not turn_around_done:
            if time.time() - last_movement_time > 20:
                # Enable spike flag after 20 seconds of no movement
                phase_spike = True
                print("No movement for 20 seconds, enabling spike mode")

        if phase_collecting and utils_item.check_next_enemy(use_only_compass=True):
            print("Enemy detected during collecting, pausing collecting and go back to spike mode")
            phase_spike = True
            phase_collecting = False
            minimal_enchantment_maintained = False
            time.sleep(0.01)  # Wait a bit before checking again

        if phase_spike:
            if ((time_passed_in_seconds - last_shadowform_cast_time > 3.0 or last_shadowform_cast_time == 0) 
                and (time_passed_in_seconds - last_wastrels_demise_cast_time >= 3.0)):
                if not utils_item.check_next_enemy():
                    # Wait 0.1  seconds before next check
                    time.sleep(0.1)
                    if not utils_item.check_next_enemy():
                        print("Collecting since no enemies detected")
                        phase_collecting = True
                        counter_irrelevant_items = 0
                        e_pressed = False  # Reset the flag so it doesn't trigger repeatedly
                        continue
                # Check if mana is above 60% before casting
                energy_img_array = utils_energy_management.get_energy_level()
                if energy_img_array < 60.0:
                    print(f"Mana below 60%, skipping Wastrel's Demise cast with mana at {energy_img_array}%")
                    continue
                if utils_item.check_next_enemy():
                    cast_spike(True)
                nearest_enemy = not nearest_enemy  # Alternate between nearest and next enemy
                last_wastrels_demise_cast_time = time_passed_in_seconds
                continue
        
    
        ######### MOVEMENT LOGIC #########

        # Handle movement when not casting spells and not collecting
        if (start_movement and not phase_collecting and not phase_spike and 
            current_movement_index_forward < len(movement_keys_forwards) and
            shadowform_casted and shroud_casted and ways_casted):
            
            current_movement_key_forward, current_movement_remaining_forward, current_movement_index_forward, sequence_complete = handle_movement_sequence(
                dict_movement_forwards, current_movement_key_forward, current_movement_remaining_forward, 
                current_movement_index_forward, movement_chunk_size, "forward"
            )
            
            # Check if all movements are complete
            if sequence_complete:
                start_movement = False
                reached_final_position = True
                last_movement_time = time.time()


        # Use second movement dictionary to go back
        if (reached_final_position and not phase_spike and not phase_collecting and
            current_movement_index_reverse < len(movement_keys_reverse) and turn_around_done):
            
            current_movement_key_reverse, current_movement_remaining_reverse, current_movement_index_reverse, sequence_complete = handle_movement_sequence(
                dict_movement_reverse, current_movement_key_reverse, current_movement_remaining_reverse, 
                current_movement_index_reverse, movement_chunk_size, "reverse"
            )
            
            # Check if all movements are complete
            if sequence_complete:
                reached_final_position = False
                current_movement_index_forward = 0
                current_movement_key = None
                break
            
        # Fail safe to start collecting after 300 seconds. Something seem to be wrong if it reaches here

        # Start collecting after 300 seconds of runtime
        if time_passed_in_seconds > 300 and not phase_collecting:
            print(f"Starting collecting after 300 seconds at {time_passed_in_seconds} seconds")
            phase_collecting = True
            if phase_spike:
                phase_spike = False  # Disable spike mode when starting collecting

        time.sleep(0.01)  # Sleep to prevent high CPU usage


    # Go back to jarnskeggi and than to jaga moraine area
    utils_areas.jaga_moraine2jarnskeggi(12.0)  # Example call to go to jarnskeggi area
    utils_areas.bjora_marches2jaga_moraine() # Works also the other way around