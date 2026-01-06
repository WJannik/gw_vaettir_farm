from pynput.keyboard import Key, Listener, Controller
import time
import threading
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt

# Try relative imports first, then absolute imports for testing
try:
    from . import utils_areas
    from . import utils_enemy
    from .utils_skill_management import *
    from .constants import SHADOWFORM_DURATION, SHROUD_DURATION, WAYS_DURATION, MAX_RUN_TIME
    from .utils_plotting import plot_run_times
    from .phase_movement import MovementPhase
    from .phase_spike import SpikePhase
    from .phase_collecting import CollectingPhase
except ImportError:
    # If relative imports fail, try absolute imports for testing
    try:
        import utils_areas
        import utils_enemy
        from utils_skill_management import *
        from constants import SHADOWFORM_DURATION, SHROUD_DURATION, WAYS_DURATION, MAX_RUN_TIME
        from utils_plotting import plot_run_times
        from phase_movement import MovementPhase
        from phase_spike import SpikePhase
        from phase_collecting import CollectingPhase
    except ImportError:
        # If that fails too, try adding the parent directory to path
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gw_vaettir_bot import utils_areas
        from gw_vaettir_bot import utils_enemy
        from gw_vaettir_bot.utils_skill_management import *
        from gw_vaettir_bot.constants import SHADOWFORM_DURATION, SHROUD_DURATION, WAYS_DURATION, MAX_RUN_TIME
        from gw_vaettir_bot.utils_plotting import plot_run_times
        from gw_vaettir_bot.phase_movement import MovementPhase
        from gw_vaettir_bot.phase_spike import SpikePhase
        from gw_vaettir_bot.phase_collecting import CollectingPhase

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

        # Initialize phase handlers
        movement_phase = MovementPhase()
        spike_phase = SpikePhase()
        collecting_phase = CollectingPhase()

        # Initialise last casttime of skills
        last_shadowform_cast_time = 0
        last_shroud_of_distress_cast_time = 0
        last_ways_cast_time = 0
        # Flags to track enchanments 
        shadowform_casted = False
        shroud_casted = False
        ways_casted = False
        mantra_casted = False

        # Phase flags
        phase_movement = True
        minimal_enchantment_maintained = False

        # Get current time
        start_time = time.time()

        while True and time.time() - start_time < MAX_RUN_TIME:
            time_passed_in_seconds = time.time() - start_time

            # Shadowform and other enchantments management in order tank the enmeies ---------------

            # Cast Shadowform every 20 seconds after it was last casted
            if ((time_passed_in_seconds - last_shadowform_cast_time)%SHADOWFORM_DURATION >= 0.0 and 
                (time_passed_in_seconds -  last_shadowform_cast_time)%SHADOWFORM_DURATION < 2.0 
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
                time_passed_in_seconds - last_shadowform_cast_time > 1.5 and
                time_passed_in_seconds - last_shadowform_cast_time < 5.0
                and not minimal_enchantment_maintained):
                cast_mantra_of_earth()
                mantra_casted = True
                continue

            # Reset mantra_casted flag
            if mantra_casted and time_passed_in_seconds - last_shadowform_cast_time >= 5.0:
                mantra_casted = False

            # Cast Shroud of Distress every 45 seconds  after it was last casted
            if ((time_passed_in_seconds - last_shroud_of_distress_cast_time)%SHROUD_DURATION > 0.0 
                and time_passed_in_seconds - last_shadowform_cast_time < 18.0
                and not shroud_casted):
                cast_shroud_of_distress()
                shroud_casted = True
                last_shroud_of_distress_cast_time = time.time() - start_time
                continue

            # Reset flags after 45 seconds
            if shroud_casted and time_passed_in_seconds - last_shroud_of_distress_cast_time >= SHROUD_DURATION:
                shroud_casted = False

            # Cast Way of Perfection and Master every 30 seconds after it was last casted
            if ((time_passed_in_seconds - last_ways_cast_time)%WAYS_DURATION > 0.0 
                and time_passed_in_seconds - last_shadowform_cast_time < 18.0 
                and not ways_casted and not minimal_enchantment_maintained):
                cast_way_of_perfection_and_master()
                ways_casted = True
                last_ways_cast_time = time.time() - start_time
                continue

            # Reset flags after 30 seconds
            if ways_casted and time_passed_in_seconds - last_ways_cast_time >= WAYS_DURATION:
                ways_casted = False
            
            # Collecting phase -------------------------------------------------
            if collecting_phase.is_collecting():
                spike_phase.disable_spike_mode()
                minimal_enchantment_maintained = True
                
                # Handle enemy detection during collecting
                if spike_phase.handle_enemy_detection_during_collecting():
                    collecting_phase.stop_collecting()
                    minimal_enchantment_maintained = False
                    time.sleep(0.01)
                    continue
                
                # Handle collecting logic
                result, updated_time = collecting_phase.handle_collecting_logic(last_used_logging_time)
                
                if result == "collecting_finished":
                    run_time_collecting += updated_time
                    last_used_logging_time = time.time()
                    movement_phase.perform_turn_around()
                elif result == "item_picked":
                    # Item was picked up successfully
                    pass
                elif result == "irrelevant_item":
                    # Irrelevant item found, counter incremented
                    pass

            # Spike phase ------------------------------------------------------
            # Enable spike phase if final position is reached and no movement for specified time
            if (movement_phase.final_position_reached_forward and not spike_phase.is_in_pre_spike_phase() 
                and not spike_phase.is_in_spike_phase() and not collecting_phase.is_collecting() 
                and not movement_phase.turn_around_done):
                
                # Handle stuck detection
                movement_phase.handle_stuck_detection()
                
                # Check if spike mode should be enabled
                if movement_phase.should_enable_spike_mode(utils_enemy.are_enemies_stacked):
                    spike_phase.enable_pre_spike_mode()
                    
            # Update from pre-spike to spike phase
            if spike_phase.update_pre_spike_to_spike():
                run_time_enemies_stacked += time.time() - last_used_logging_time
                last_used_logging_time = time.time()
                
            # Handle spike logic
            result, updated_time = spike_phase.handle_spike_logic(
                time_passed_in_seconds, last_shadowform_cast_time, last_used_logging_time
            )
            
            if result == "start_collecting":
                collecting_phase.start_collecting()
                run_time_spike += updated_time
                last_used_logging_time = time.time()
                continue
            elif result == "spike_cast":
                continue

            # Handle movement when not casting spells and not collecting
            if (phase_movement and not collecting_phase.is_collecting() and not spike_phase.is_in_spike_phase() and
                shadowform_casted and shroud_casted and ways_casted):
                
                movement_complete = movement_phase.handle_forward_movement(shadowform_casted, shroud_casted, ways_casted)
                
                if movement_complete:
                    phase_movement = False
                    run_time_forward += time.time() - last_used_logging_time
                    last_used_logging_time = time.time()

            # Handle backward movement
            if (movement_phase.final_position_reached_forward and not spike_phase.is_in_spike_phase() 
                and not collecting_phase.is_collecting() and movement_phase.turn_around_done):
                
                result = movement_phase.handle_backward_movement()
                
                if result == "found_npc":
                    break
                elif result == "sequence_complete":
                    break
                
            # Fail safe to start collecting after 300 seconds
            if time_passed_in_seconds > 300 and not collecting_phase.is_collecting():
                print(f"Starting collecting after 300 seconds at {time_passed_in_seconds} seconds")
                collecting_phase.start_collecting()
                spike_phase.disable_spike_mode()

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

    # Plot the run times
    plot_run_times(run_times, run_times_running_forward, run_times_waiting_for_stacked_enemies,
                   run_times_spike_phase, run_times_collecting_phase, run_times_running_backward, number_of_runs)


if __name__ == "__main__":
    # Add current directory to path for testing
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    number_of_runs = 1
    start_farm(number_of_runs)