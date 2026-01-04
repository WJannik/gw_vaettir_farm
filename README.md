# Guild Wars Vaettir Farm

A Python automation script for farming Vaettir in Guild Wars.

## Quick Start

To start the farm, simply run:

```bash
python run_farm.py
```

## Project Structure

- `run_farm.py` - Main entry point to start the farming process
- `farm/` - Contains all the farming logic and utilities
  - `main.py` - Core farming algorithm and main loop  
  - `constants.py` - Configuration constants
  - `utils_*.py` - Various utility modules for different aspects of the farm
  - `assets/` - Image assets for computer vision
  - `logs/` - Farm run logs and statistics
  - `debug_images/` - Debug screenshots and images

## Requirements

- Python 3.x
- See the original README in `farm/README.md` for detailed requirements and setup instructions

## Usage

The farm will automatically:
1. Navigate to the farming area
2. Execute the farming sequence  
3. Collect items
4. Return to start position
5. Generate performance statistics and charts

Press `Ctrl+C` to stop the farm at any time.