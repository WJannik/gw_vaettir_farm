# Try relative imports first, then absolute imports for testing
try:
    from .utils.utils_skill_management import *
    from .utils.constants import SHADOWFORM_DURATION, SHROUD_DURATION, WAYS_DURATION
except ImportError:
    from utils.utils_skill_management import *
    from utils.constants import SHADOWFORM_DURATION, SHROUD_DURATION, WAYS_DURATION



class EnchantmentManager:
    """Manages all enchantments for the Vaettir farming bot."""
    
    def __init__(self) -> None:
        # Last cast times for each enchantment
        self.last_shadowform_cast_time = 0
        self.last_shroud_of_distress_cast_time = 0
        self.last_ways_cast_time = 0
        
        # Flags to track enchantment states
        self.shadowform_casted = False
        self.shroud_casted = False
        self.ways_casted = False
        self.mantra_casted = False
    
    def reset_enchantment_state(self)->None:
        """Reset enchantment state for new run."""
        self.last_shadowform_cast_time = 0
        self.last_shroud_of_distress_cast_time = 0
        self.last_ways_cast_time = 0
        self.shadowform_casted = False
        self.shroud_casted = False
        self.ways_casted = False
        self.mantra_casted = False
    
    def handle_shadowform(self, time_passed_in_seconds: float) -> bool:
        """Handle Shadowform casting and timing."""
        # Cast Shadowform every 20 seconds after it was last casted
        if ((time_passed_in_seconds - self.last_shadowform_cast_time) % SHADOWFORM_DURATION > 0.0 and 
            (time_passed_in_seconds - self.last_shadowform_cast_time) % SHADOWFORM_DURATION < 2.0 
            and not self.shadowform_casted):
            cast_shadowform()  # This includes casting time + aftercast delay
            self.shadowform_casted = True
            # Set last_cast_time after the skill finishes (1.0s casting + 0.75s aftercast = ~1.75s)
            self.last_shadowform_cast_time = time_passed_in_seconds + 1.75
            return True 
        
        # Reset flags after 19.5 seconds to maintain the enchantment for sure
        if self.shadowform_casted and time_passed_in_seconds - self.last_shadowform_cast_time >= 19.5:
            self.shadowform_casted = False
        
        return False 
    
    def handle_mantra_of_earth(self, time_passed_in_seconds: float, minimal_enchantment_maintained: bool) -> bool:
        """Handle Mantra of Earth casting and timing."""
        # Cast Mantra of earth at least 2 seconds after shadowform was casted
        if (not self.mantra_casted and time_passed_in_seconds > 20 and
            time_passed_in_seconds - self.last_shadowform_cast_time > 1.5 and
            time_passed_in_seconds - self.last_shadowform_cast_time < 5.0
            and not minimal_enchantment_maintained):
            cast_mantra_of_earth()  # Instant cast, no aftercast delay
            self.mantra_casted = True
            return True  
        
        # Reset mantra_casted flag
        if self.mantra_casted and time_passed_in_seconds - self.last_shadowform_cast_time >= 5.0:
            self.mantra_casted = False
        
        return False  # No enchantment cast
    
    def handle_shroud_of_distress(self, time_passed_in_seconds: float) -> bool:
        """Handle Shroud of Distress casting and timing."""
        # Cast Shroud of Distress every 45 seconds after it was last casted
        if ((time_passed_in_seconds - self.last_shroud_of_distress_cast_time) % SHROUD_DURATION > 0.0 
            and time_passed_in_seconds - self.last_shadowform_cast_time < 18.0
            and not self.shroud_casted):
            cast_shroud_of_distress()  # 1.0s casting + 0.75s aftercast = 1.75s total
            self.shroud_casted = True
            # Set last_cast_time after the skill finishes
            self.last_shroud_of_distress_cast_time = time_passed_in_seconds + 1.75
            return True  
        
        # Reset flags after 45 seconds
        if self.shroud_casted and time_passed_in_seconds - self.last_shroud_of_distress_cast_time >= SHROUD_DURATION:
            self.shroud_casted = False
        
        return False # No enchantment cast
    
    def handle_way_of_perfection_and_master(self, time_passed_in_seconds: float, minimal_enchantment_maintained: bool) -> bool:
        """Handle Way of Perfection and Master casting and timing."""
        # Cast Way of Perfection and Master every 30 seconds after it was last casted
        if ((time_passed_in_seconds - self.last_ways_cast_time) % WAYS_DURATION > 0.0 
            and time_passed_in_seconds - self.last_shadowform_cast_time < 18.0 
            and not self.ways_casted and not minimal_enchantment_maintained):
            cast_way_of_perfection_and_master()  # 0.25s + 0.25s casting + 2*0.75s aftercast = 2.0s total
            self.ways_casted = True
            # Set last_cast_time after both skills finish
            self.last_ways_cast_time = time_passed_in_seconds + 2.0
            return True  
        
        # Reset flags after 30 seconds
        if self.ways_casted and time_passed_in_seconds - self.last_ways_cast_time >= WAYS_DURATION:
            self.ways_casted = False
        
        return False  # No enchantment cast
    
    def update_enchantments(self, time_passed_in_seconds: float, minimal_enchantment_maintained=False) -> bool:
        """Update all enchantments and return if any were cast."""
        enchantment_cast = False
        
        # Handle Shadowform (highest priority)
        if self.handle_shadowform(time_passed_in_seconds):
            enchantment_cast = True
        
        # Handle other enchantments only if shadowform wasn't just cast
        if not enchantment_cast:
            if self.handle_mantra_of_earth(time_passed_in_seconds, minimal_enchantment_maintained):
                enchantment_cast = True
            elif self.handle_shroud_of_distress(time_passed_in_seconds):
                enchantment_cast = True
            elif self.handle_way_of_perfection_and_master(time_passed_in_seconds, minimal_enchantment_maintained):
                enchantment_cast = True
        
        return enchantment_cast
    
    def are_core_enchantments_active(self) -> bool:
        """Check if core enchantments (shadowform, shroud, ways) are active."""
        return self.shadowform_casted and self.shroud_casted and self.ways_casted
    
    def get_enchantment_states(self) -> dict[str, bool]:
        """Get current enchantment states for external use."""
        return {
            'shadowform': self.shadowform_casted,
            'shroud': self.shroud_casted,
            'ways': self.ways_casted,
            'mantra': self.mantra_casted
        }
    
    def get_last_shadowform_cast_time(self) -> float:
        """Get the last shadowform cast time for external calculations."""
        return self.last_shadowform_cast_time