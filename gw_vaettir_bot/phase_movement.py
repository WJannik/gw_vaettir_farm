"""Movement phase handling for Vaettir farming bot."""

import time
from pynput.keyboard import Controller

# Try relative imports first, then absolute imports for testing
try:
    from .utils.utils_movement import handle_movement_sequence, stuck
    from .utils.constants import MOVEMENT_CHUNK_SIZE
    from .utils.utils_general import generate_bbox, capture_and_process_region, is_object
except ImportError:
    try:
        from utils.utils_movement import handle_movement_sequence, stuck
        from utils.constants import MOVEMENT_CHUNK_SIZE
        from utils.utils_general import generate_bbox, capture_and_process_region, is_object
    except ImportError:
        import os
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gw_vaettir_bot.utils.utils_movement import handle_movement_sequence, stuck
        from gw_vaettir_bot.utils.constants import MOVEMENT_CHUNK_SIZE
        from gw_vaettir_bot.utils.utils_general import generate_bbox, capture_and_process_region, is_object


class MovementPhase:
    """Handles the movement phase of the Vaettir farming bot."""
    
    def __init__(self):
        self.keyboard = Controller()
        
        # Movement configuration
        self.dict_movement_forwards = {
            "stop_1": 4.0,
            "move_forward_1": 10.0,
            "turn_right_1": 0.67,
            "move_forward_2": 16.0,
        }
        self.dict_movement_backward = {
            "move_forward_1": 15.0,
        }
        
        # Movement state tracking
        self.final_position_reached_forward = False
        self.current_movement_key_forward = None
        self.current_movement_key_backward = None
        self.current_movement_remaining_forward = 0.0
        self.current_movement_remaining_backward = 0.0
        self.last_movement_time = 0
        self.movement_keys_forward = list(self.dict_movement_forwards.keys())
        self.movement_keys_backward = list(self.dict_movement_backward.keys())
        self.current_movement_index_forward = 0
        self.current_movement_index_backward = 0
        self.stuck_used = False
        self.turn_around_done = False
    
    def reset_movement_state(self):
        """Reset movement state for new run."""
        self.final_position_reached_forward = False
        self.current_movement_key_forward = None
        self.current_movement_key_backward = None
        self.current_movement_remaining_forward = 0.0
        self.current_movement_remaining_backward = 0.0
        self.last_movement_time = 0
        self.current_movement_index_forward = 0
        self.current_movement_index_backward = 0
        self.stuck_used = False
        self.turn_around_done = False
    
    def handle_forward_movement(self, shadowform_casted, shroud_casted, ways_casted):
        """Handle forward movement sequence."""
        if (self.current_movement_index_forward < len(self.movement_keys_forward) and
            shadowform_casted and shroud_casted and ways_casted):
            
            self.current_movement_key_forward, self.current_movement_remaining_forward, self.current_movement_index_forward, sequence_complete = handle_movement_sequence(
                self.dict_movement_forwards, self.current_movement_key_forward, self.current_movement_remaining_forward, 
                self.current_movement_index_forward, MOVEMENT_CHUNK_SIZE, "forward"
            )
            
            # Check if all movements are complete
            if sequence_complete:
                self.final_position_reached_forward = True
                self.last_movement_time = time.time()
                return True  # Movement phase complete
        
        return False  # Movement phase ongoing
    
    def handle_stuck_detection(self):
        """Handle stuck detection and recovery."""
        if self.final_position_reached_forward and not self.stuck_used:
            if time.time() - self.last_movement_time > 30:
                self.stuck_used = True
                stuck()
                return True
        return False
    
    def should_enable_spike_mode(self, are_enemies_stacked_func):
        """Check if spike mode should be enabled."""
        if self.final_position_reached_forward:
            return (time.time() - self.last_movement_time > 40 or 
                    are_enemies_stacked_func())
        return False
    
    def handle_backward_movement(self):
        """Handle backward movement sequence."""
        if (self.final_position_reached_forward and 
            self.current_movement_index_backward < len(self.movement_keys_backward) and
            self.turn_around_done):
            
            # Check if jarnskeggi is found
            self.keyboard.press('v')
            time.sleep(0.01)
            self.keyboard.release('v')
            time.sleep(0.01)
            bbox = generate_bbox(860, 25, 180, 15)
            screenshot, img_array = capture_and_process_region(bbox, "npc_check")
            if is_object(img_array, "jarnskeggi", print_diff=False, asset_path="gw_vaettir_bot/assets/npcs"):
                return "found_npc"  # Signal to break main loop
            
            self.current_movement_key_backward, self.current_movement_remaining_backward, self.current_movement_index_backward, sequence_complete = handle_movement_sequence(
                self.dict_movement_backward, self.current_movement_key_backward, self.current_movement_remaining_backward, 
                self.current_movement_index_backward, MOVEMENT_CHUNK_SIZE, "backward"
            )
            
            # Check if all movements are complete
            if sequence_complete:
                self.final_position_reached_forward = False
                self.current_movement_index_forward = 0
                self.current_movement_key_forward = None
                return "sequence_complete"  # Signal to break main loop
        
        return "ongoing"  # Movement ongoing
    
    def perform_turn_around(self):
        """Perform U-turn after collecting."""
        if not self.turn_around_done:
            #print("Collecting finished, performing U-turn after collecting")
            self.keyboard.press('x')
            time.sleep(0.01)
            self.keyboard.release('x')
            self.turn_around_done = True