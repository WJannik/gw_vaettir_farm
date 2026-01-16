# Guild Wars Vaettir Farm

A Python automation script for farming Vaettir in Guild Wars build from scratch.

## Disclaimer

This project is intended solely for educational and research purposes, showcasing automation techniques such as image recognition, input simulation, and state‑based scripting.

Using automation in online games may violate the game’s Terms of Service.
You are solely responsible for how you use this code.

## Overview
Guild Wars is a classic online RPG first released in 2005.
In 2025 it celebrated its 20th anniversary with the release of Guild Wars Reforged.

As someone who spent countless hours in the game as a kid, I revisited it and wondered whether I could build a fully automated Vaettir farming routine from scratch. This project is the result: a Python‑based automation script that demonstrates how to navigate, detect enemies, manage combat, and collect loot in a repeatable loop.

A general guide to Vaettir farming can be found on the official wiki:
[Guide to Vaettir Farming](https://wiki.guildwars.com/wiki/Guide_to_vaettir_farming).


## Features
The script includes the following features:
- Automated movement from the starting point in bjoras marches to the Vaettir area and back after the farm is complete.
- Local enemy detection to steer the combat behavior.
- Combat automation to efficiently deal with Vaettir
- Item management to pick up only items/loot of interest (e.g. rare items, festive items, glacial stones, etc.).
- Energy management to ensure the character has enough energy to cast spells.

## Demonstration
The automation routine performs the following steps:

    1. Starts in Bjora Marches
    2. Enters the portal to Jaga Moraine
    3. Picks up Blessing of the Norn
    4. Precasts and maintains defensive spells
    5. Navigates through the area, gathering up to ~36 Vaettir
    6. Waits until all enemies are grouped
    7. Executes the combat rotation until all Vaettir are defeated
    8. Loots filtered items
    9. Returns to Bjora Marches and restarts the loop

A [video demonstration](https://www.youtube.com/watch?v=MHa8c_5hUI8) is available on YouTube.

## Performance & Reliability

- Each run takes roughly 3–4 minutes on average.
- The automation has an approximate 5% failure rate, mainly due to the dynamic layout of the area, which changes every time you enter it.
- The script is built to handle most variations, but certain edge cases may still lead to suboptimal behavior.
- When a failure is detected, the script automatically resets the run and starts a fresh attempt.

## Quick Start
Install the required packages from requirements.txt.
```bash
conda create -n gw_vaettir_farm python=3.10
conda activate gw_vaettir_farm
pip install -r requirements.txt
```
To start the farm in the environment, simply run
```
python run_farm.py
# or to specify the number of runs
python run_farm.py 15
```

## Build, Armor, and Weapons
The automation is designed for a specific setup as Mesmer/Assasin or Assasin/Mesmer: <br>
Build: OQdTI4x8ZiHRn5AiAaR0G8myAAA <br>
Weapon: Staff with +20% enchantment duration (to maintain Shadow Form) <br>
Armor: Max armor with +10 armor while enchanted; other runes and insignias are flexible <br> 

## Issues & Limitations
The script is designed for 1920×1080 resolution

Other resolutions require adjusting:
- Movement coordinates
- Item pickup coordinates
- Image‑recognition assets

This is a personal project, not a universal bot, but feel free to fork and adapt it

If you encounter issues or have suggestions, please open an issue on GitHub.