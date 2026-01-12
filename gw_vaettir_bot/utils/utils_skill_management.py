import time
from pynput.keyboard import Key, Controller

# Try relative imports first, then absolute imports for testing
try:
    from .constants import AFTERCAST_DELAY
except ImportError:
    # If relative imports fail, try absolute imports for testing
    from constants import AFTERCAST_DELAY

# Create a keyboard controller
keyboard = Controller()

def cast_skill(key, cast_time, aftercast_delay_required = True, skill_name= None):
    """
    Generic skill cast function with aftercast delay.
    
    Args:
        key (str): The keyboard key to press for the skill
        cast_time (float): The casting time in seconds
        aftercast_delay_required (bool): Normally True, set to False for instant skills or stances
        skill_name (str): Optional name of the skill for logging
    """ 
    # Press and release the skill key
    keyboard.press(key)
    time.sleep(0.01)  # Brief key press duration
    keyboard.release(key)
    
    # Wait for cast time
    time.sleep(cast_time)
    
    if aftercast_delay_required:
        # Apply aftercast delay if needed
        time.sleep(AFTERCAST_DELAY)

    """if skill_name:
        print(f"Finished casting {skill_name}")
    else:
        print(f"Finished casting skill bound to {key}")"""


def cast_shadowform():
    cast_skill('1', cast_time=0.0, aftercast_delay_required = False, skill_name="Deadly Paradox")
    cast_skill('2', cast_time=1.0, aftercast_delay_required=True, skill_name="Shadowform")

def cast_shroud_of_distress():
    cast_skill('3', cast_time=1.0, aftercast_delay_required = True, skill_name="Shroud of Distress")

def cast_way_of_perfection_and_master():
    cast_skill('4', cast_time=0.25, aftercast_delay_required = True, skill_name="Way of Perfection")
    cast_skill('5', cast_time=0.25, aftercast_delay_required = True, skill_name="Way of Mastery")

def cast_mantra_of_earth():
    cast_skill('8', cast_time=0.0, aftercast_delay_required = False, skill_name="Mantra of Earth")#

def cast_spike(nearest_enemy=True):
    if nearest_enemy:
        # Get nearest enemy
        keyboard.press('c')
        time.sleep(0.01)
        keyboard.release('c')
        time.sleep(0.01)
    else:
        for _ in range(1):
            # Get next enemy by pressing tab key
            keyboard.press(Key.tab)
            time.sleep(0.01)
            keyboard.release(Key.tab)
            time.sleep(0.01)
    cast_skill('7', cast_time=0.25, aftercast_delay_required=True, skill_name="Wastrel's Demise")
    # Remove aftercast delay, since this is sometimes on cooldown
    cast_skill('6', cast_time=0.25, aftercast_delay_required=False, skill_name="Cry of Pain") 