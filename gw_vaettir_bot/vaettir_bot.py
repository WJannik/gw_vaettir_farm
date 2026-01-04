from pynput.keyboard import Key, Listener, Controller
import time
import threading
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt

from . import utils_item
from . import utils_enemy
from . import utils_areas
from . import utils_energy_management
from .utils_skill_management import *
from .utils_movement import handle_movement_sequence, stuck
from .constants import MOVEMENT_CHUNK_SIZE
from .utils_general import generate_bbox, capture_and_process_region, is_object


def start_farm(number_of_runs):
    """Main function to start the Vaettir farming process."""
    # Create a keyboard controller
    keyboard = Controller()

    # Log the time of each run
    run_times = []
    run_times_running_forward = []
    run_times_running_backward = []
    run_times_spike_phase = []
    run_times_collecting_phase = []
    run_times_waiting_for_stacked_enemies = []
    
    for run_number in range(number_of_runs):
        start_time_run = time.time()
        run_time_forward = 0
        run_time_backward = 0
        run_time_spike = 0
        run_time_collecting = 0
        run_time_enemies_stacked = 0
        last_used_logging_time = time.time()
        print(f"Starting the {run_number+1}-th run in ...")
        for countdown in range(3, 0, -1):
            print(countdown)
            time.sleep(1)
        # Start run in bjora marches to jaga moraine area
        utils_areas.bjora_marches2jaga_moraine()  
        utils_areas.jaga_moraine2jarnskeggi() 
        utils_areas.pick_up_norn_blessing() 

        # Initialise last casttime of skills
        last_shadowform_cast_time = 0
        last_shroud_of_distress_cast_time = 0
        last_ways_cast_time = 0
        last_spike_cast_time = 0
        # Flags to track enchanments 
        shadowform_casted = False
        shroud_casted = False
        ways_casted = False
        mantra_casted = False

        # Phase flags
        phase_movement = True
        pre_phase_spike = False
        phase_spike = False
        phase_collecting = False

        # Other flags
        nearest_enemy = True
        minimal_enchantment_maintained = False
        turn_around_done = False
        stuck_used = False

        # Counter for collecting items
        counter_irrelevant_items = 0 

        # Movement configuration and state tracking
        dict_movement_forwards = {
            "stop_1": 4.0,
            "move_forward_1": 10.0,
            "turn_right_1": 0.6,
            "move_forward_2": 17.0,
        }
        dict_movement_backward = {
            "move_forward_1": 15.0,
        }
        final_position_reached_forward = False
        current_movement_key_forward = None
        current_movement_key_backward = None
        current_movement_remaining_forward = 0.0
        current_movement_remaining_backward = 0.0
        last_movement_time = 0
        movement_keys_forward = list(dict_movement_forwards.keys())
        movement_keys_backward = list(dict_movement_backward.keys())
        current_movement_index_forward = 0
        current_movement_index_backward = 0

        # Get current time
        start_time = time.time()

        while True and time.time() - start_time < 500:
            time_passed_in_seconds = time.time() - start_time

            # Shadowform and other enchantments management in order tank the enmeies ---------------

            # Cast Shadowform every 20 seconds after it was last casted
            if ((time_passed_in_seconds - last_shadowform_cast_time)%20 >= 0.0 and 
                (time_passed_in_seconds -  last_shadowform_cast_time)%20 < 2.0 
                and not shadowform_casted):
                cast_shadowform()
                shadowform_casted = True
                last_shadowform_cast_time = time.time() - start_time
                continue
            # Reset flags after 18 seconds such that it maintains the enchantment for sure
            if shadowform_casted and time_passed_in_seconds - last_shadowform_cast_time >= 19.5:
                shadowform_casted = False

            # Cast Mantra of earth at least 2 seconds after shadowform was casted 
            if (not mantra_casted and time_passed_in_seconds> 20 and
                time_passed_in_seconds - last_shadowform_cast_time > 1.0 and
                time_passed_in_seconds - last_shadowform_cast_time < 3.0
                and not minimal_enchantment_maintained):
                cast_mantra_of_earth()
                mantra_casted = True
                continue

            # Reset mantra_casted flag
            if mantra_casted and time_passed_in_seconds - last_shadowform_cast_time >= 3.5:
                mantra_casted = False

            # Cast Shroud of Distress every 45 seconds  after it was last casted
            if ((time_passed_in_seconds - last_shroud_of_distress_cast_time)%45 > 0.0 
                and time_passed_in_seconds - last_shadowform_cast_time < 18.0
                and not shroud_casted):
                cast_shroud_of_distress()
                shroud_casted = True
                last_shroud_of_distress_cast_time = time.time() - start_time
                continue

            # Reset flags after 45 seconds
            if shroud_casted and time_passed_in_seconds - last_shroud_of_distress_cast_time >= 45.0:
                shroud_casted = False

            # Cast Way of Perfection and Master every 30 seconds after it was last casted
            if ((time_passed_in_seconds - last_ways_cast_time)%30 > 0.0 
                and time_passed_in_seconds - last_shadowform_cast_time < 18.0 
                and not ways_casted and not minimal_enchantment_maintained):
                cast_way_of_perfection_and_master()
                ways_casted = True
                last_ways_cast_time = time.time() - start_time
                continue

            # Reset flags after 30 seconds
            if ways_casted and time_passed_in_seconds - last_ways_cast_time >= 30.0:
                ways_casted = False
            
            # Collecting phase -------------------------------------------------
            # Pick up relevant items until 10 irrelevant items are found in a row. 
            # Start way back by enabling turn around.
            # Re-enable spike mode if an enemy is detected during collecting.

            if phase_collecting and counter_irrelevant_items < 10:
                phase_spike = False
                minimal_enchantment_maintained = True
                if utils_item.check_next_item():
                    counter_irrelevant_items = 0 
                    time.sleep(0.3) 
                else:
                    counter_irrelevant_items += 1
                    print("Irrelevant item counter: ", counter_irrelevant_items)
            if phase_collecting and counter_irrelevant_items >= 10:
                phase_collecting = False
                if not turn_around_done:
                    print("Collecting finished, performing U-turn after collecting")
                    run_time_collecting += time.time() - last_used_logging_time
                    last_used_logging_time = time.time()
                    keyboard.press('x')
                    time.sleep(0.01)
                    keyboard.release('x')
                    turn_around_done = True
            
            if phase_collecting and utils_enemy.check_next_enemy(use_only_compass=True):
                print("Enemy detected during collecting, pausing collecting and go back to spike mode")
                # Re-enable spike mode if an enemy is detected during collecting
                phase_spike = True
                phase_collecting = False
                minimal_enchantment_maintained = False
                time.sleep(0.01)  

            # Spike phase ------------------------------------------------------
            # Enable spike phase if final position is reached and no movement for 20 seconds.
            # Re-enable spike mode if an enemy is detected during collecting.
            if (final_position_reached_forward and not pre_phase_spike and not phase_spike
                and not phase_collecting and not turn_around_done):
                if time.time() - last_movement_time > 30 and not stuck_used:
                    stuck_used = True
                    stuck()
                if time.time() - last_movement_time > 40 or utils_enemy.are_enemies_stacked():
                    # Enable spike mode, after 60 seconds of no movement or if enemies are stacked.
                    pre_phase_spike = True
                    time_for_real_spike_start = time.time() + 5.0
                    print("No movement for 60 seconds or enemies stacked, enabling spike mode")
            if pre_phase_spike and time.time() > time_for_real_spike_start:
                phase_spike = True
                pre_phase_spike = False
                run_time_enemies_stacked += time.time() - last_used_logging_time
                last_used_logging_time = time.time()
            # Kill the enemies nearby with spike
            if phase_spike:
                if ((time_passed_in_seconds - last_shadowform_cast_time > 3.0 or last_shadowform_cast_time == 0)
                    and time_passed_in_seconds - last_shadowform_cast_time < 18.0 
                    and (time_passed_in_seconds - last_spike_cast_time >= 3.0)):
                    if not utils_enemy.check_next_enemy():
                        time.sleep(0.1)
                        if not utils_enemy.check_next_enemy():
                            print("Collecting since no enemies detected")
                            phase_collecting = True
                            counter_irrelevant_items = 0
                            run_time_spike += time.time() - last_used_logging_time
                            last_used_logging_time = time.time()
                            continue
                    # Check if mana is above 60% before casting
                    energy_img_array = utils_energy_management.get_energy_level()
                    if energy_img_array < 60.0:
                        print(f"Mana below 60%, skipping Wastrel's Demise cast with mana at {energy_img_array}%")
                        continue
                    if utils_enemy.check_next_enemy():
                        cast_spike(nearest_enemy)
                    # In the first 35 second alternate between nearest and next enemy, afterwards only nearest
                    if time.time() - last_used_logging_time < 40:
                        nearest_enemy = not nearest_enemy  # Alternate between nearest and next enemy
                    else:
                        nearest_enemy = True  # Always nearest enemy
                    last_spike_cast_time = time_passed_in_seconds
                    continue

            # Handle movement when not casting spells and not collecting
            if (phase_movement and not phase_collecting and not phase_spike and 
                current_movement_index_forward < len(movement_keys_forward) and
                shadowform_casted and shroud_casted and ways_casted):
                
                current_movement_key_forward, current_movement_remaining_forward, current_movement_index_forward, sequence_complete = handle_movement_sequence(
                    dict_movement_forwards, current_movement_key_forward, current_movement_remaining_forward, 
                    current_movement_index_forward, MOVEMENT_CHUNK_SIZE, "forward"
                )
                
                # Check if all movements are complete
                if sequence_complete:
                    phase_movement = False
                    final_position_reached_forward = True
                    last_movement_time = time.time()
                    run_time_forward += time.time() - last_used_logging_time
                    last_used_logging_time = time.time()

            # Use second movement dictionary to go back
            if (final_position_reached_forward and not phase_spike and not phase_collecting and
                current_movement_index_backward < len(movement_keys_backward) 
                and turn_around_done):
                # Check if jarnskeggi is found
                keyboard.press('v')
                time.sleep(0.01)
                keyboard.release('v')
                time.sleep(0.01)
                bbox = generate_bbox(860, 55, 180, 15)
                screenshot, img_array = capture_and_process_region(bbox, "npc_check")
                if is_object(img_array, "jarnskeggi", print_diff=False, asset_path="gw_vaettir_bot/assets/npcs"):
                    break
                current_movement_key_backward, current_movement_remaining_backward, current_movement_index_backward, sequence_complete = handle_movement_sequence(
                    dict_movement_backward, current_movement_key_backward, current_movement_remaining_backward, 
                    current_movement_index_backward, MOVEMENT_CHUNK_SIZE, "backward"
                )
                # Check if all movements are complete
                if sequence_complete:
                    final_position_reached_forward = False
                    current_movement_index_forward = 0
                    current_movement_key = None
                    break
                
            # Fail safe to start collecting after 300 seconds. Something seem to be wrong if it reaches here
            if time_passed_in_seconds > 300 and not phase_collecting:
                print(f"Starting collecting after 300 seconds at {time_passed_in_seconds} seconds")
                phase_collecting = True
                if phase_spike:
                    phase_spike = False  # Disable spike mode when starting collecting

            time.sleep(0.01)  # Sleep to prevent high CPU usage

        # Go back to jarnskeggi and than to jaga moraine area to start a new run
        utils_areas.jaga_moraine2jarnskeggi(12.0)
        utils_areas.jaga_moraine2bjora_marches(10.0)

        run_time_backward  += time.time() - last_used_logging_time
        # Log the time of the run
        run_times.append(time.time() - start_time_run)
        # Each phase time logging
        run_times_running_forward.append(run_time_forward)
        run_times_waiting_for_stacked_enemies.append(run_time_enemies_stacked)
        run_times_spike_phase.append(run_time_spike)
        run_times_collecting_phase.append(run_time_collecting)
        run_times_running_backward.append(run_time_backward)

        print(f"Run {run_number+1} completed in {time.time() - start_time_run} seconds.")

    # Plot the run times as stacked bar chart
    current_time = time.strftime("%Y%m%d-%H%M%S")

    # Debug: Print the data to see what we have
    print("Debug - Data lengths:")
    print(f"Forward times: {len(run_times_running_forward)} values: {run_times_running_forward}")
    print(f"Waiting times: {len(run_times_waiting_for_stacked_enemies)} values: {run_times_waiting_for_stacked_enemies}")
    print(f"Spike times: {len(run_times_spike_phase)} values: {run_times_spike_phase}")
    print(f"Collecting times: {len(run_times_collecting_phase)} values: {run_times_collecting_phase}")
    print(f"Backward times: {len(run_times_running_backward)} values: {run_times_running_backward}")
    print(f"Total run times: {run_times}")

    # Create stacked bar chart
    run_numbers = list(range(1, number_of_runs+1))

    # Convert lists to numpy arrays for easier stacking calculations
    forward_times = np.array(run_times_running_forward)
    waiting_times = np.array(run_times_waiting_for_stacked_enemies)
    spike_times = np.array(run_times_spike_phase)
    collecting_times = np.array(run_times_collecting_phase)
    backward_times = np.array(run_times_running_backward)

    # Create the stacked bars
    fig, ax = plt.subplots(figsize=(12, 8))
    width = 0.8

    # Stack the bars properly - each phase on top of the previous
    ax.bar(run_numbers, forward_times, width, label='Running Forward', color='#1f77b4')
    ax.bar(run_numbers, waiting_times, width, bottom=forward_times, label='Waiting for Stacked Enemies', color='#ff7f0e')
    ax.bar(run_numbers, spike_times, width, bottom=forward_times + waiting_times, label='Spike Phase', color='#2ca02c')
    ax.bar(run_numbers, collecting_times, width, bottom=forward_times + waiting_times + spike_times, label='Collecting Phase', color='#d62728')
    ax.bar(run_numbers, backward_times, width, bottom=forward_times + waiting_times + spike_times + collecting_times, label='Running Backward', color='#9467bd')

    ax.set_xlabel('Run Number')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Time Breakdown for Each Run. Average Total Time: {:.2f} seconds'.format(np.mean(run_times)))
    ax.legend(loc="upper right")
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'gw_vaettir_bot/logs/run_times_stacked_{current_time}.png')
    plt.show()


if __name__ == "__main__":
    number_of_runs = 1
    start_farm(number_of_runs)