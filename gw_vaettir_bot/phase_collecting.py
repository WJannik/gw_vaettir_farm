import time

# Try relative imports first, then absolute imports for testing
try:
    from .utils import utils_item
except ImportError:
    from utils import utils_item


class CollectingPhase:
    """Handles the collecting phase of the Vaettir farming bot."""
    
    def __init__(self)->None:
        self.phase_collecting = False
        self.counter_irrelevant_items = 0
        self.max_irrelevant_items = 10
    
    def reset_collecting_state(self) -> None:
        """Reset collecting state for new run."""
        self.phase_collecting = False
        self.counter_irrelevant_items = 0
    
    def start_collecting(self) -> None:
        """Start the collecting phase."""
        self.phase_collecting = True
        self.counter_irrelevant_items = 0
    
    def stop_collecting(self) -> None:
        """Stop the collecting phase."""
        self.phase_collecting = False
    
    def handle_collecting_logic(self, last_used_logging_time: float) -> tuple[None | str, float]:
        """Handle the main collecting logic including item pickup and counter management."""
        if not self.phase_collecting:
            return None, last_used_logging_time
        
        # Check if we've reached the maximum irrelevant items threshold
        if self.counter_irrelevant_items >= self.max_irrelevant_items:
            self.phase_collecting = False
            run_time_collecting = time.time() - last_used_logging_time
            return "collecting_finished", run_time_collecting
        
        # Try to pick up the next item
        if utils_item.check_next_item():
            self.counter_irrelevant_items = 0
            time.sleep(0.3)
            return "item_picked", last_used_logging_time
        else:
            self.counter_irrelevant_items += 1
            return "irrelevant_item", last_used_logging_time
    
    def is_collecting(self) -> bool:
        """Check if currently in collecting phase."""
        return self.phase_collecting
    
    def get_irrelevant_items_count(self) -> int:
        """Get the current count of irrelevant items found in a row."""
        return self.counter_irrelevant_items
    
    def is_collecting_finished(self) -> bool:
        """Check if collecting phase is finished based on irrelevant items counter."""
        return self.counter_irrelevant_items >= self.max_irrelevant_items
    
    def set_max_irrelevant_items(self, max_count: int) -> None:
        """Set the maximum number of irrelevant items before finishing collecting."""
        self.max_irrelevant_items = max_count