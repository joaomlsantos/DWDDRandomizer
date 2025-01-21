# Digimon World Dawn / Dusk Randomizer

Randomizer and quality-of-life feature patcher for the games **Digimon World: Dawn** and **Digimon World: Dusk**.

The information presented in these pages refers to the USA roms (serial codes NTR-A6RE-USA and NTR-A3VE-USA for Dusk and Dawn respectively).

![Digimon World Dawn/Dusk Randomizer](public/randomizer_preview.png)

## Contents
- [How To Use](#how-to-use)
    - [Windows](#windows)
- [Features](#features)
    - [Quality-of-Life Changes](#quality-of-life-changes)
    - [Randomization Settings](#randomization-settings)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)
- [Copyright Notice](#copyright-notice)

## How To Use

### Windows

1. Download the [latest release](https://github.com/joaomlsantos/DWDDRandomizer/releases/tag/1.0.0) of the randomizer tool.
2. Unpack the downloaded files and launch `DWDDRandomizer.exe`.
3. Click `Open ROM` and open a valid .nds ROM of your game.
4. Pick your quality-of-life and/or randomization features and click `Save Changes`. Give a name to your new patched ROM and choose the directory where to save the ROM, and click `Save`. A new .nds ROM will be generated with the chosen changes.


## Features

### Quality-of-Life Changes

The following [**quality-of-life changes**](https://github.com/joaomlsantos/DWDDRandomizer/wiki/QoL-Changes) have been implemented so far:
- Increased Text Speed
- Increased Player Movement Speed
- Reduced Wild Encounter Rate
- Increased Exp Yield for Wild Digimon
- Increased Scan Rate
- Expanded Player Name Length
- Increased Stat Caps

### Randomization Settings

The following [**randomization options**](https://github.com/joaomlsantos/DWDDRandomizer/wiki/Randomizer-Options) have been implemented so far:
- Starter Packs
- Wild Digimon
- Digivolutions
- Digivolution Conditions


## Run From Source
This application was built with Python 3.9.0, but most other versions of Python3 should be compatible.

### Steps:

1. Ensure you have Python 3 installed on your system. If it is not installed, download it from [python.org](https://www.python.org/).
2. Clone or download this repository to your computer.
3. Install the required packages by running `pip install -r requirements.txt` .
4. Launch the application by executing `python ui_tkinter.py` .


## Contact

For questions or suggestions, please reach out via Issues or [joao.l.santos@tecnico.ulisboa.pt](mailto:joao.l.santos@tecnico.ulisboa.pt).


## Acknowledgements

Most of the research work for this game was accomplished using [HxD](https://mh-nexus.de/en/hxd/), [DeSmuME](https://desmume.org/) and [Ghidra](https://ghidra-sre.org/).

The implemented user interface was heavily inspired by [Universal Pokémon Randomizer's](https://github.com/Ajarmar/universal-pokemon-randomizer-zx) design.

Special thanks to [@Dreaker](https://github.com/Dreaker75), who composed a set of thorough [code notes](https://retroachievements.org/codenotes.php?g=16152) for these games and has been supporting this project's efforts through brainstorming and listening to me yap about ROM editing for hours [:


[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](LICENSE)

## Copyright Notice


Digimon World: Dawn/Dusk are owned by Bandai Namco Entertainment. I do not own, nor do I claim any rights to, the original game assets, code, or intellectual property associated with Digimon World Dawn and Digimon World Dusk. 

This repository and the tools within are provided for educational and personal use only. They are not intended for commercial use, nor for redistribution of copyrighted game assets.