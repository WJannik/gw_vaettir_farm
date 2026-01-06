"""Spike phase handling for Vaettir farming bot."""

import time

# Try relative imports first, then absolute imports for testing
try:
    from .utils import utils_enemy
    from .utils import utils_energy_management
    from .utils.utils_skill_management import cast_spike
    from .utils.constants import SPIKE_COOLDOWN
except ImportError:
    try:
        from utils import utils_enemy
        from utils import utils_energy_management
        from utils.utils_skill_management import cast_spike
        from utils.constants import SPIKE_COOLDOWN
    except ImportError:
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gw_vaettir_bot.utils import utils_enemy
        from gw_vaettir_bot.utils import utils_energy_management
        from gw_vaettir_bot.utils.utils_skill_management import cast_spike
        from gw_vaettir_bot.utils.constants import SPIKE_COOLDOWN


class SpikePhase:
    """Handles the pre-spike and spike phases of the Vaettir farming bot."""
    
    def __init__(self):
        self.pre_phase_spike = False
        self.phase_spike = False
        self.last_spike_cast_time = 0
        self.nearest_enemy = True
        self.time_for_real_spike_start = 0
    
    def reset_spike_state(self):
        """Reset spike state for new run."""
        self.pre_phase_spike = False
        self.phase_spike = False
        self.last_spike_cast_time = 0
        self.nearest_enemy = True
        self.time_for_real_spike_start = 0
    
    def enable_pre_spike_mode(self, delay=5.0):
        """Enable pre-spike mode with a delay before actual spiking."""
        self.pre_phase_spike = True
        self.time_for_real_spike_start = time.time() + delay
        print("No movement for 60 seconds or enemies are stacked, enabling spike mode")
    
    def update_pre_spike_to_spike(self):
        """Update from pre-spike to actual spike phase."""
        if self.pre_phase_spike and time.time() > self.time_for_real_spike_start:
            self.phase_spike = True
            self.pre_phase_spike = False
            return True
        return False
    
    def handle_spike_logic(self, time_passed_in_seconds, last_shadowform_cast_time, 
                          last_used_logging_time):
        """Handle the main spike logic including enemy detection and spell casting."""
        if not self.phase_spike:
            return None, last_used_logging_time
        
        # Check timing conditions for casting
        if not ((time_passed_in_seconds - last_shadowform_cast_time > 3.0 or last_shadowform_cast_time == 0)
                and time_passed_in_seconds - last_shadowform_cast_time < 18.0 
                and (time_passed_in_seconds - self.last_spike_cast_time >= SPIKE_COOLDOWN)):
            return None, last_used_logging_time
        
        # Check for enemies
        if not utils_enemy.check_next_enemy():
            time.sleep(0.1)
            if not utils_enemy.check_next_enemy():
                print("Collecting since no enemies detected")
                run_time_spike = time.time() - last_used_logging_time
                return "start_collecting", run_time_spike
        
        # Check if mana is above 60% before casting
        energy_img_array = utils_energy_management.get_energy_level()
        if energy_img_array < 60.0:
            print(f"Mana below 60%, skipping Wastrel's Demise cast with mana at {energy_img_array}%")
            return None, last_used_logging_time
        
        # Cast spike if enemy is present
        if utils_enemy.check_next_enemy():
            cast_spike(self.nearest_enemy)
        
        # Alternate enemy targeting in first 30 seconds, then always nearest
        if time.time() - last_used_logging_time < 30.0:
            self.nearest_enemy = not self.nearest_enemy  # Alternate between nearest and next enemy
        else:
            self.nearest_enemy = True  # Always nearest enemy
        
        self.last_spike_cast_time = time_passed_in_seconds
        return "spike_cast", last_used_logging_time
    
    def handle_enemy_detection_during_collecting(self):
        """Handle enemy detection during collecting phase."""
        if utils_enemy.check_next_enemy(use_only_compass=True):
            print("Enemy detected during collecting, pausing collecting and go back to spike mode")
            self.phase_spike = True
            return True
        return False
    
    def disable_spike_mode(self):
        """Disable spike mode."""
        self.phase_spike = False
    
    def is_in_spike_phase(self):
        """Check if currently in spike phase."""
        return self.phase_spike
    
    def is_in_pre_spike_phase(self):
        """Check if currently in pre-spike phase."""
        return self.pre_phase_spike