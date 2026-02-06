from configs import ExpYieldConfig, RandomizeDigivolutionConditions, RandomizeDigivolutions, RandomizeStartersConfig, RandomizeWildEncounters, RookieResetConfig

from src import model


test_unchanged_settings = {

    "INCREASE_TEXT_SPEED": False,
    "INCREASE_MOVEMENT_SPEED": False,
    "REDUCE_WILD_ENCOUNTER_RATE": False,
    "CHANGE_STAT_CAPS": False,
    "EXPAND_PLAYER_NAME_LENGTH": False,
    "INCREASE_DIGIMON_EXP": ExpYieldConfig.UNCHANGED,
    "INCREASE_SCAN_RATE": False,

    "ROOKIE_RESET_EVENT": RookieResetConfig.UNCHANGED,
    "RANDOMIZE_STARTERS": RandomizeStartersConfig.UNCHANGED,
    "NERF_FIRST_BOSS": False,
    
    "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters.UNCHANGED,
    "WILD_ENCOUNTERS_STATS": model.LvlUpMode.RANDOM, 
    
    "RANDOMIZE_FIXED_BATTLES": False,
    "FIXED_BATTLES_DIGIMON_SAME_STAGE": False,  
    "FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES": False, 
    "FIXED_BATTLES_BALANCE_BY_BST": False,
    "FIXED_BATTLES_KEEP_HP": False,
    
    
    "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.UNCHANGED,
    "DIGIVOLUTIONS_SIMILAR_SPECIES": False,
    
    "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions.UNCHANGED,
    "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": False,    
}

PATH_SOURCE_DAWN = "C:/Workspace/digimon_stuffs/rom_files/1421 - Digimon World - Dawn (USA).nds"
PATH_SOURCE_DUSK = "C:/Workspace/digimon_stuffs/rom_files/1420 - Digimon World - Dusk (US).nds"
PATH_TARGET_DAWN = "C:/Workspace/digimon_stuffs/rom_files/1421 - Digimon World - Dawn (USA)_pytest.nds"
PATH_TARGET_DUSK = "C:/Workspace/digimon_stuffs/rom_files/1420 - Digimon World - Dusk (US)_pytest.nds"