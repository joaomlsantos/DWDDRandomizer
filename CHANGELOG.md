# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



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

[0.1.1]: https://github.com/joaomlsantos/DWDDRandomizer//compare/0.1.0...0.1.1
[0.1.0]: https://github.com/joaomlsantos/DWDDRandomizer/releases/tag/0.1.0