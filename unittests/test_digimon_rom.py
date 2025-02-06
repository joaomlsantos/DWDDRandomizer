from io import StringIO
import logging

import pytest
from src import model
from qol_script import DigimonROM, Randomizer
from configs import ConfigManager, RandomizeDigivolutionConditions, RandomizeDigivolutions, RandomizeStartersConfig, RandomizeWildEncounters, ExpYieldConfig
from unittests.test_configs import PATH_TARGET_DAWN, PATH_TARGET_DUSK, test_unchanged_settings, PATH_SOURCE_DAWN, PATH_SOURCE_DUSK
import copy


# there HAS to be a better way to do these than my current approach
# pqp

starting_settings = copy.deepcopy(test_unchanged_settings)      # start with all unchanged

def load_rom(path_source):
    config_manager = ConfigManager()
    config_manager.update_from_ui(starting_settings)
    log_stream = StringIO()
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=log_stream, level=logging.INFO,  format='%(message)s')
    return DigimonROM(path_source, config_manager, logger)


def test_default_configmanager():
    config_manager = ConfigManager()
    config_manager.update_from_ui(starting_settings)
    #return config_manager


def test_logger_creation():
    log_stream = StringIO()
    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=log_stream, level=logging.INFO,  format='%(message)s')
    #return logger


def test_load_dawn():
    rom = load_rom(PATH_SOURCE_DAWN)
    
def test_load_dusk():
    rom = load_rom(PATH_SOURCE_DUSK)


@pytest.fixture
def rom_dawn():
    return load_rom(PATH_SOURCE_DAWN)

@pytest.fixture
def rom_dusk():
    return load_rom(PATH_SOURCE_DUSK)

@pytest.fixture
def randomizer_dawn():
    rom = load_rom(PATH_SOURCE_DAWN)
    return Randomizer(rom.version, rom.rom_data, rom.config_manager, rom.logger)

@pytest.fixture
def randomizer_dusk():
    rom = load_rom(PATH_SOURCE_DUSK)
    return Randomizer(rom.version, rom.rom_data, rom.config_manager, rom.logger)


# QoL Features tests

def test_changeTextSpeed(rom_dawn, rom_dusk):
    rom_dawn.changeTextSpeed()
    rom_dusk.changeTextSpeed()

def test_changeMovementSpeed(rom_dawn, rom_dusk):
    rom_dawn.changeMovementSpeed()
    rom_dusk.changeMovementSpeed()

def test_changeEncounterRate(rom_dawn, rom_dusk):
    rom_dawn.changeEncounterRate()
    rom_dusk.changeEncounterRate()

def test_extendPlayerNameSize(rom_dawn, rom_dusk):
    rom_dawn.extendPlayerNameSize()
    rom_dusk.extendPlayerNameSize()

def test_buffScanRate(rom_dawn, rom_dusk):
    rom_dawn.buffScanRate()
    rom_dusk.buffScanRate()


# Starters Randomization Tests

def test_startersRandomizeUnchanged(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.UNCHANGED
    randomizer_dusk.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.UNCHANGED
    randomizer_dawn.randomizeStarters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeStarters(randomizer_dusk.rom_data)

def test_startersRandomizeSameStage(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.RAND_SAME_STAGE
    randomizer_dusk.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.RAND_SAME_STAGE
    randomizer_dawn.randomizeStarters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeStarters(randomizer_dusk.rom_data)

def test_startersRandomizeFull(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.RAND_FULL
    randomizer_dusk.config_manager.configs["RANDOMIZE_STARTERS"] = RandomizeStartersConfig.RAND_FULL
    randomizer_dawn.randomizeStarters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeStarters(randomizer_dusk.rom_data)

def test_nerfFirstBossFalse(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["NERF_FIRST_BOSS"] = False
    randomizer_dusk.config_manager.configs["NERF_FIRST_BOSS"] = False
    randomizer_dawn.nerfFirstBoss(randomizer_dawn.rom_data)
    randomizer_dusk.nerfFirstBoss(randomizer_dusk.rom_data)
    
def test_nerfFirstBossTrue(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["NERF_FIRST_BOSS"] = True
    randomizer_dusk.config_manager.configs["NERF_FIRST_BOSS"] = True
    randomizer_dawn.nerfFirstBoss(randomizer_dawn.rom_data)
    randomizer_dusk.nerfFirstBoss(randomizer_dusk.rom_data)
    

# Digivolution Randomization Tests

def test_digivolutionsUnchanged(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dawn.randomizeDigivolutions(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeDigivolutions(randomizer_dusk.rom_data)
    
def test_digivolutionsRandom(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.RANDOMIZE
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.RANDOMIZE
    randomizer_dawn.config_manager.configs["DIGIVOLUTIONS_SIMILAR_SPECIES"] = False
    randomizer_dusk.config_manager.configs["DIGIVOLUTIONS_SIMILAR_SPECIES"] = False
    randomizer_dawn.randomizeDigivolutions(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeDigivolutions(randomizer_dusk.rom_data)

def test_digivolutionsRandomSimilarSpecies(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.RANDOMIZE
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.RANDOMIZE
    randomizer_dawn.config_manager.configs["DIGIVOLUTIONS_SIMILAR_SPECIES"] = True
    randomizer_dusk.config_manager.configs["DIGIVOLUTIONS_SIMILAR_SPECIES"] = True
    randomizer_dawn.randomizeDigivolutions(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeDigivolutions(randomizer_dusk.rom_data)

def test_digivolutionConditionsOnly(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTION_CONDITIONS"] = RandomizeDigivolutionConditions.RANDOMIZE
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTION_CONDITIONS"] = RandomizeDigivolutionConditions.RANDOMIZE
    randomizer_dawn.config_manager.configs["DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP"] = False
    randomizer_dusk.config_manager.configs["DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP"] = False
    randomizer_dawn.randomizeDigivolutionConditionsOnly(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeDigivolutionConditionsOnly(randomizer_dusk.rom_data)
    
def test_digivolutionConditionsOnlyAvoidDiffSpecies(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTIONS"] = RandomizeDigivolutions.UNCHANGED
    randomizer_dawn.config_manager.configs["RANDOMIZE_DIGIVOLUTION_CONDITIONS"] = RandomizeDigivolutionConditions.RANDOMIZE
    randomizer_dusk.config_manager.configs["RANDOMIZE_DIGIVOLUTION_CONDITIONS"] = RandomizeDigivolutionConditions.RANDOMIZE
    randomizer_dawn.config_manager.configs["DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP"] = True
    randomizer_dusk.config_manager.configs["DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP"] = True
    randomizer_dawn.randomizeDigivolutionConditionsOnly(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeDigivolutionConditionsOnly(randomizer_dusk.rom_data)
    

# Wild Encounter Randomization Tests

def test_areaEncountersUnchanged(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.UNCHANGED
    randomizer_dusk.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.UNCHANGED
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)
        
def test_areaEncountersRandomSameStage(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
    randomizer_dusk.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)

def test_areaEncountersRandomCompletely(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY
    randomizer_dusk.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)

def test_areaEncountersStats(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE
    randomizer_dusk.config_manager.configs["RANDOMIZE_AREA_ENCOUNTERS"] = RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE

    randomizer_dawn.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.RANDOM
    randomizer_dusk.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.RANDOM
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)

    randomizer_dawn.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_MIN
    randomizer_dusk.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_MIN
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)

    randomizer_dawn.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_AVG
    randomizer_dusk.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_AVG
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)

    randomizer_dawn.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_MAX
    randomizer_dusk.config_manager.configs["AREA_ENCOUNTERS_STATS"] = model.LvlUpMode.FIXED_MAX
    randomizer_dawn.randomizeAreaEncounters(randomizer_dawn.rom_data)
    randomizer_dusk.randomizeAreaEncounters(randomizer_dusk.rom_data)


# Exp Patch Tests

def test_expPatchUnchanged(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.UNCHANGED
    randomizer_dusk.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.UNCHANGED
    randomizer_dawn.expPatchFlat(randomizer_dawn.rom_data, randomizer_dawn.enemyDigimonInfo)
    randomizer_dusk.expPatchFlat(randomizer_dusk.rom_data, randomizer_dusk.enemyDigimonInfo)

def test_expPatchHalved(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.INCREASE_HALVED
    randomizer_dusk.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.INCREASE_HALVED
    randomizer_dawn.expPatchFlat(randomizer_dawn.rom_data, randomizer_dawn.enemyDigimonInfo)
    randomizer_dusk.expPatchFlat(randomizer_dusk.rom_data, randomizer_dusk.enemyDigimonInfo)

def test_expPatchFull(randomizer_dawn, randomizer_dusk):
    randomizer_dawn.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.INCREASE_FULL
    randomizer_dusk.config_manager.configs["APPLY_EXP_PATCH_FLAT"] = ExpYieldConfig.INCREASE_FULL
    randomizer_dawn.expPatchFlat(randomizer_dawn.rom_data, randomizer_dawn.enemyDigimonInfo)
    randomizer_dusk.expPatchFlat(randomizer_dusk.rom_data, randomizer_dusk.enemyDigimonInfo)
