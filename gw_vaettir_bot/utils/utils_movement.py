import time
from pynput.keyboard import Key, Controller
# Create a keyboard controller
keyboard = Controller()


def move_forward(duration):
    """Move forward for specified duration"""
    #print(f"Moving forward for {duration} seconds")
    keyboard.press('w')
    time.sleep(duration)
    keyboard.release('w')

def move_backward(duration):
    """Move backward for specified duration"""
    #print(f"Moving backward for {duration} seconds")
    keyboard.press('s')
    time.sleep(duration)
    keyboard.release('s')

def move_stop(duration):
    """Stop movement for specified duration"""
    #print(f"Stopping movement for {duration} seconds")
    keyboard.release('w')
    keyboard.release('s')
    time.sleep(duration)

def move_sideways_left(duration):
    """Move sideways left for specified duration"""
    #print(f"Moving sideways left for {duration} seconds")
    keyboard.press('q')
    time.sleep(duration)
    keyboard.release('q')

def move_sideways_right(duration):
    """Move sideways right for specified duration"""
    #print(f"Moving sideways right for {duration} seconds")
    keyboard.press('e')
    time.sleep(duration)
    keyboard.release('e')

def turn_left(duration):
    """Turn left for specified duration"""
    #print(f"Turning left for {duration} seconds")
    keyboard.press('a')
    time.sleep(duration)
    keyboard.release('a')

def turn_right(duration):
    """Turn right for specified duration"""
    #print(f"Turning right for {duration} seconds")
    keyboard.press('d')
    time.sleep(duration)
    keyboard.release('d')

def execute_chunk_of_movement(current_movement_key, current_movement_remaining,movement_chunk_size):
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
    elif "move_sideways_left" in current_movement_key:
        move_sideways_left(chunk_duration)
    elif "move_sideways_right" in current_movement_key:
        move_sideways_right(chunk_duration)
    elif "stop" in current_movement_key:
        move_stop(chunk_duration)
    return current_movement_remaining - chunk_duration

def handle_movement_sequence(movement_dict, current_movement_key, current_movement_remaining, 
                           current_movement_index, movement_chunk_size, movement_type="forward"):
    """
    Handle a sequence of movements from a movement dictionary.
    
    Args:
        movement_dict: Dictionary containing movement keys and durations
        current_movement_key: Current movement being executed (None if starting new)
        current_movement_remaining: Remaining time for current movement
        current_movement_index: Index of current movement in sequence
        movement_chunk_size: Size of movement chunks in seconds
        movement_type: Type of movement for logging ("forward" or "reverse")
    
    Returns:
        tuple: (new_movement_key, new_remaining_time, new_index, sequence_complete)
    """
    movement_keys = list(movement_dict.keys())
    
    # Check if we've completed all movements
    if current_movement_index >= len(movement_keys):
        return None, 0.0, current_movement_index, True
    
    # Initialize new movement if needed
    if current_movement_key is None:
        current_movement_key = movement_keys[current_movement_index]
        current_movement_remaining = movement_dict[current_movement_key]
        #print(f"Starting {movement_type} movement: {current_movement_key} for {current_movement_remaining} seconds")
    
    # Execute movement in chunks
    if current_movement_remaining > 0:
        current_movement_remaining = execute_chunk_of_movement(current_movement_key, current_movement_remaining, movement_chunk_size)
        
        # If movement is complete, move to next movement
        if current_movement_remaining <= 0:
            #print(f"Completed {movement_type} movement: {current_movement_key}")
            current_movement_index += 1
            current_movement_key = None
            
            # Check if all movements are complete
            if current_movement_index >= len(movement_keys):
                #print(f"All {movement_type} movements completed")
                return None, 0.0, current_movement_index, True
    
    return current_movement_key, current_movement_remaining, current_movement_index, False

def stuck():
    duration = 0.01
    # Write /stuck in chat to get unstuck
    keyboard.press(Key.enter)
    time.sleep(duration)
    keyboard.release(Key.enter)
    time.sleep(duration)
    letter = ['/','s','t','u','c','k']
    for char in letter:
        keyboard.press(char)
        keyboard.release(char)
        time.sleep(0.01)
    keyboard.press(Key.enter)
    time.sleep(duration)
    keyboard.release(Key.enter)
    time.sleep(duration)

