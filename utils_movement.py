import time
from pynput.keyboard import Key, Controller
# Create a keyboard controller
keyboard = Controller()


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
    return current_movement_remaining - chunk_duration