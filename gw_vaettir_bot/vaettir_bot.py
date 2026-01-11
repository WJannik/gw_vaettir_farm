from pynput.keyboard import Key, Listener, Controller
import time
import threading
from PIL import ImageGrab
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Try relative imports first, then absolute imports for testing
try:
    from .utils import utils_areas
    from .utils import utils_enemy
    from .utils.constants import MAX_RUN_TIME
    from .utils.utils_plotting import plot_run_times
    from .phase_movement import MovementPhase
    from .phase_spike import SpikePhase
    from .phase_collecting import CollectingPhase
    from .enchantment_management import EnchantmentManager
except ImportError:
    # If relative imports fail, try absolute imports for testing
    try:
        from utils import utils_areas
        from utils import utils_enemy
        from utils.constants import MAX_RUN_TIME
        from utils.utils_plotting import plot_run_times
        from phase_movement import MovementPhase
        from phase_spike import SpikePhase
        from phase_collecting import CollectingPhase
        from enchantment_management import EnchantmentManager
    except ImportError:
        # If that fails too, try adding the parent directory to path
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gw_vaettir_bot.utils import utils_areas
        from gw_vaettir_bot.utils import utils_enemy
        from gw_vaettir_bot.utils.constants import MAX_RUN_TIME
        from gw_vaettir_bot.utils.utils_plotting import plot_run_times
        from gw_vaettir_bot.phase_movement import MovementPhase
        from gw_vaettir_bot.phase_spike import SpikePhase
        from gw_vaettir_bot.phase_collecting import CollectingPhase
        from gw_vaettir_bot.enchantment_management import EnchantmentManager

def start_farm(number_of_runs):
    """Main function to start the Vaettir farming process."""
    # Create a keyboard controller
    keyboard = Controller()

    # Compact run times tracking
    run_data = {
        'total': [],
        'forward': [],
        'backward': [],
        'spike': [],
        'collecting': [],
        'enemies_stacked': []
    }
    
    for run_number in tqdm(range(number_of_runs), desc="Runs"):
        start_time_run = time.time()
        # Compact run time tracking
        times = {'forward': 0, 'backward': 0, 'spike': 0, 'collecting': 0, 'enemies_stacked': 0}
        last_used_logging_time = time.time()
        #print(f"Starting the {run_number+1}-th run in ...")
        for countdown in range(3, 0, -1):
            time.sleep(1)
        # Start run in bjora marches to jaga moraine area
        utils_areas.bjora_marches2jaga_moraine()  
        utils_areas.jaga_moraine2jarnskeggi() 
        utils_areas.pick_up_norn_blessing() 

        # Initialize phase handlers
        movement_phase = MovementPhase()
        spike_phase = SpikePhase()
        collecting_phase = CollectingPhase()
        enchantment_manager = EnchantmentManager()

        # Phase flags
        phase_movement = True
        minimal_enchantment_maintained = False

        # Get current time
        start_time = time.time()

        while True and time.time() - start_time < MAX_RUN_TIME:
            time_passed_in_seconds = time.time() - start_time

            # Handle enchantments management
            if enchantment_manager.update_enchantments(time_passed_in_seconds, minimal_enchantment_maintained):
                continue  # Skip other logic this iteration if an enchantment was cast
            
            # Get current enchantment states
            enchantment_states = enchantment_manager.get_enchantment_states()
            shadowform_casted = enchantment_states['shadowform']
            shroud_casted = enchantment_states['shroud']
            ways_casted = enchantment_states['ways']
            
            # Collecting phase 
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
                    times['collecting'] += updated_time
                    last_used_logging_time = time.time()
                    movement_phase.perform_turn_around()

            # Spike phase 
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
                times['enemies_stacked'] += time.time() - last_used_logging_time
                last_used_logging_time = time.time()
                
            # Handle spike logic
            result, updated_time = spike_phase.handle_spike_logic(
                time_passed_in_seconds, enchantment_manager.get_last_shadowform_cast_time(), last_used_logging_time
            )
            
            if result == "start_collecting":
                collecting_phase.start_collecting()
                times['spike'] += updated_time
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
                    times['forward'] += time.time() - last_used_logging_time
                    last_used_logging_time = time.time()

            # Handle backward movement
            if (movement_phase.final_position_reached_forward and not spike_phase.is_in_spike_phase() 
                and not collecting_phase.is_collecting() and movement_phase.turn_around_done):
                
                result = movement_phase.handle_backward_movement()
                
                if result == "found_npc":
                    break
                elif result == "sequence_complete":
                    break
                
            # Fail safe to start collecting after 400 seconds
            if time_passed_in_seconds > 400 and not collecting_phase.is_collecting():
                #print(f"Starting collecting after 400 seconds at {time_passed_in_seconds} seconds")
                collecting_phase.start_collecting()
                spike_phase.disable_spike_mode()

            time.sleep(0.01)  # Sleep to prevent high CPU usage

        # Go back to jarnskeggi and than to jaga moraine area to start a new run
        utils_areas.jaga_moraine2jarnskeggi(12.0)
        utils_areas.jaga_moraine2bjora_marches(10.0)

        times['backward'] += time.time() - last_used_logging_time
        
        # Log all run data compactly
        total_time = time.time() - start_time_run
        run_data['total'].append(total_time)
        for phase in ['forward', 'backward', 'spike', 'collecting', 'enemies_stacked']:
            run_data[phase].append(times[phase])

        print(f"Run {run_number+1} completed in {total_time:.2f} seconds.")

    # Plot the run times using compact data
    plot_run_times(run_data)

if __name__ == "__main__":
    # Add current directory to path for testing
    import os
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    number_of_runs = 20
    start_farm(number_of_runs)