# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-05-24

### Added

#### Digivolutions
- Remove Scan Requirements: Removes all digivolution conditions that involve having scanned a specific digimon in order to digivolve.


### Fixed
- Fixed bug w/ standard digivolution loading
- Fixed issue w/ starter randomization when forcing starters of the same stage

**Full Changelog**: https://github.com/joaomlsantos/DWDDRandomizer/compare/0.2.0...0.2.1


## [0.2.0] - 2026-02-20

### Added

#### App Settings
- Import/Export configuration settings
- Added template settings files for QoL only, balanced randomization, chaos randomization
- Auto-update checker
- Changed UI option organization for better clarity/compactness
- Exposed advanced parameters through `preferences.toml` (e.g. edit encounter rate multiplier directly)

#### QoL Patches
- Improve Battle Performance
- Increase Wild Encounter Money
- Increase Farm EXP
- Balance Calumon Stats
- Enable Legendary Tamer Quest
- Unlock Main Quests in Sequence
- Unlock Version-Exclusive Areas

#### Starters, Items & Quests
- Force Starter w/ Rookie Stage
- Change Rookie Reset Event
- Customize Starter Packs
- Randomize Overworld Items
- Randomize Quest Item Rewards

#### Wild Encounters & Enemies
- Randomize Encounter Item Drops
- Randomize Enemy Tamers, Quest Digimon & Bosses

#### Species & Base Stats
- Randomize Digimon Species
- Randomize Elemental Resistances
- Randomize Base Stats
- Randomize Digimon's StatType

#### Movesets & Traits
- Randomize Movesets
- Add Signature Moves to Regular Move Pool
- Guarantee Basic Move
- Randomize Traits
- Enable Unused Traits

#### Digivolutions
- Randomize DNA Digivolutions
- Randomize or Remove DNA Digivolution Conditions


### Fixed
- Fixed issue where the loaded base ROM would previously be overwritten by the randomized ROM (thus, perfoming multiple randomizations/qol-patches of the same ROM would result in odd behavior such as extremely reduced encounters)
- Disabled MinAPT digivolution condition (issue #10)
- Increased wild encounter difficulty for Champion, Ultimate and Mega digimon (configurable as a direct HP multiplier in `preferences.toml`)
- Improved output logs (wild digimon locations, digivolutions, added logs for new features)

**Full Changelog**: https://github.com/joaomlsantos/DWDDRandomizer/compare/0.1.1...0.2.0



## [0.1.1] - 2025-02-06

### Added

- **Added Linux release to the available releases**


### Fixed

- **Fixed aptitude deadlock issue when randomizing digivolution conditions**: if a digimon has no pre-digivolutions, then the level requirement of at least one of its digivolutions will always be less or equal to the digimon's base aptitude. 
    - Shoutout to [u/TheSanityIsDEAD](https://www.reddit.com/user/TheSanityIsDEAD/) for pointing this out :]

- **Improved randomization output log**: pre-digivolution and digivolution randomization and conditions are now clearer

- **General bugfixing**: in particular, fixed a bug where randomizing digivolution conditions without randomizing digivolutions would result in an Error Code 479



## [0.1.0] - 2025-01-27

### Initial Release

Initial release for Digimon World Dawn / Dusk Randomizer.

Qol Patches:
- Increased Exp Yield for Wild Digimon
- Increased Scan Rate
- Reduced Wild Encounter Rate
- Increased Text Speed
- Increased Player Movement Speed
- Expanded Player Name Length (from 5 to 7 characters)

Randomization Settings:
- Starter Packs
- Wild Digimon
- Digivolutions
- Digivolution Conditions


[0.2.1]: https://github.com/joaomlsantos/DWDDRandomizer//compare/0.2.0...0.2.1
[0.2.0]: https://github.com/joaomlsantos/DWDDRandomizer//compare/0.1.1...0.2.0
[0.1.1]: https://github.com/joaomlsantos/DWDDRandomizer//compare/0.1.0...0.1.1
[0.1.0]: https://github.com/joaomlsantos/DWDDRandomizer/releases/tag/0.1.0