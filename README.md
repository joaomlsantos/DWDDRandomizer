# Digimon World Dawn / Dusk Randomizer

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](LICENSE)

This repository contains a set of tools and scripts to modify the Digimon World Dawn/Dusk ROMs.

The information presented in these pages refers to the USA roms (serial codes NTR-A6RE-USA and NTR-A3VE-USA for Dusk and Dawn respectively).

Current functionalities include certain quality-of-life changes and randomization options.

Providing these tools/scripts in the form of an app is a priority, and will be done in the near future.

The following **quality-of-life changes** have been implemented so far:
- [Increased text speed](https://github.com/joaomlsantos/DWDDRandomizer/wiki/Change-Text-Speed)
- [Player movement speed modifier](https://github.com/joaomlsantos/DWDDRandomizer/wiki/Change-Player-Movement-Speed)
- Encounter rate modifier
- Increase stat caps

The following **randomization options** have been implemented so far:
- Randomize starters
- Randomize wild digimon area encounters



## QoL Changes

### [Increased text speed](https://github.com/joaomlsantos/DWDDRandomizer/wiki/Change-Text-Speed)
In the base games the text is displayed character-by-character, and the player needs to hold A to speed up the dialogue boxes. 

This patch removes the need of holding A for the text to speed up.

### [Player movement speed modifier](https://github.com/joaomlsantos/DWDDRandomizer/wiki/Change-Player-Movement-Speed)
Modifies the player's movement speed in the overworld. 

The default multiplier in the script is set to increase the movement speed by 1.5x of the speed in the base game.

### Encounter rate modifier
Changes the encounter rate of wild digimon in all given areas. This reflects itself in-game by increasing/reducing the amount of steps the player has to take in a given area until a wild digimon encounter is initiated.

Setting this multiplier to a number above 1 makes encounters **more frequent**, while reducing it makes encounters **less frequent**.

The default multiplier in the script is set to reduce the step frequency in all areas by 0.5x (thus, encounters will take double the usual amount of steps to be initiated).


### Increase stat caps

In the base game, the maximum possible value of the HP/MP stats of a given digimon is 9999, while the maximum possible value of the ATK/DEF/SPIRIT/SPEED stats is 999.

This patch changes that cap to 65535 for all stats (which corresponds to the maximum value held by two bytes).


## Randomizer Options

### Randomize Starters

Randomize the available starter packs in the beginning of the game. 

There are currently two randomization settings available:
- **RAND_SAME_STAGE:** Keeps the original stage (Rookie/Champion/Ultimate) of the digimon in the starter pack. Champion/Ultimate digimon will be swapped with another Champion/Ultimate, and Coronamon/Lunamon will be swapped with another Rookie digimon.
- **RAND_FULL:** Fully randomizes the digimon in each starter pack without any constraints.

**NOTE:** If the randomized digimon's APTITUDE stat is lower than the original digimon's LVL, the randomized digimon's LVL is set to the same value as its APTITUDE stat.


### Randomize Area Encounters

Randomize the wild digimon encountered in each area of the game.

Due to the nature of the wild encounters in the game, the current area randomization implementation swaps each digimon with another digimon of the same digivolution stage, and then generates the stats of the new digimon given the original digimon's level.

The stats for the new digimon are generated using the same formula for the level-ups in the game, which depends on the digimon's base stats (stats at lvl 1) and the digimon's Type (Balance/Attacker/Tank/Technical/Speed/HPtype/MPtype). 

Upon levelling up, there is a range of possible values by which each stat can increase, and as such, for the wild digimon encounters, it is possible for each digimon to be stronger or weaker depending on their level-ups.

Thus, there are four possible level-up mode settings:
- **RANDOM:** A random value from the possible level-up values is picked for each stat upon each level-up operation. This is likely to result in an average stat distribution for the digimon, but is less deterministic than **FIXED_AVG**.
- **FIXED_MIN:** The **lowest value** from the possible level-up values is always picked for each stat upon each level-up operation. This results in **weaker** digimon encounters.
- **FIXED_AVG:** The **median value** from the possible level-up values is always picked for each stat upon each level-up operation. This results in **average** digimon encounters.
- **FIXED_MAX:** The **highest value** from the possible level-up values is always picked for each stat upon each level-up operation. This results in **stronger** digimon encounters.



## Contact

For questions or suggestions, please reach out via Issues or [joao.l.santos@tecnico.ulisboa.pt](mailto:joao.l.santos@tecnico.ulisboa.pt).


## Copyright Notice


Digimon World: Dawn/Dusk are owned by Bandai Namco Entertainment. I do not own, nor do I claim any rights to, the original game assets, code, or intellectual property associated with Digimon World Dawn and Digimon World Dusk. 

This repository and the tools within are provided for educational and personal use only. They are not intended for commercial use, nor for redistribution of copyrighted game assets.