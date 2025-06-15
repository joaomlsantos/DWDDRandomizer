from enum import Enum
from src import model


# strife was here
class RookieResetConfig(Enum):
    UNCHANGED = 0                       # same as base game; resets digimon to rookies after the chaos event 
    #RESET_ALL_INCLUDING_LUNAMON = 1     # same as base game but also resets Lunamon to lvl 1
    RESET_KEEPING_EVO = 1               # reset digimon's levels, stats, etc, but keep them at their original form (ex: SkullGreymon stays as SkullGreymon but lvl 1) 
    DO_NOT_RESET = 2                    # rookie reset event does not happen; keeps digimon as they were before the chaos event


class RandomizeStartersConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RAND_SAME_STAGE = 1                 # randomize while keeping the same stage of the digimon
    RAND_FULL = 2                       # fully randomize


class RandomizeSpeciesConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOM = 1                          # randomize digimon species


class RandomizeWildEncounters(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE_1_TO_1_SAME_STAGE = 1     # randomize 1-to-1, same stage digimon
    RANDOMIZE_1_TO_1_COMPLETELY = 2     # randomize 1-to-1, completely random digimon


class RandomizeDigivolutions(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE = 1                       # randomize (specific randomization options are outside of this enum)

class RandomizeDigivolutionConditions(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE = 1                       # randomize (specific randomization options are outside of this enum)

class RandomizeDnaDigivolutions(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE_SAME_STAGE = 1            # randomize keeping original DNA digimon stages
    RANDOMIZE_COMPLETELY = 2            # generate completely random DNA digivolutions regardless of digimon stages

class RandomizeDnaDigivolutionConditions(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE = 1                       # randomize (specific randomization options are outside of this enum)
    REMOVED = 2                         # remove DNA digivolution conditions: DNA digivolutions will only require joining both digimon

class RandomizeOverworldItems(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE_KEEP_CATEGORY = 1         # randomize while keeping the original item's category (consumables replaced by other consumables, farm items replaced by other farm items, etc)
    RANDOMIZE_COMPLETELY = 2            # randomize completely


class ExpYieldConfig(Enum):
    UNCHANGED = 0                       # do not change exp yield
    INCREASE_HALVED = 1                 # base formula as if exp.share was enabled
    INCREASE_FULL = 2                   # base formula flat


class ConfigManager:
    def __init__(self):
        self.configs = {}
        self.update_from_ui(inner_configmanager_settings)

    def set(self, key, value):
        self.configs[key] = value

    def get(self, key, default=None):
        return self.configs.get(key, default)

    def update_from_ui(self, ui_variables):
        for key, tk_var in ui_variables.items():
            if hasattr(tk_var, "get"):
                self.set(key, tk_var.get())
            else:
                self.set(key, tk_var)
            

# QoL settings

# these are loaded specifically when running qol_script directly
default_configmanager_settings = {

    "CHANGE_TEXT_SPEED": True,
    "CHANGE_MOVEMENT_SPEED": True,
    "CHANGE_ENCOUNTER_RATE": True,
    "CHANGE_STAT_CAPS": True,
    "EXTEND_PLAYERNAME_SIZE": True,
    
    "APPLY_EXP_PATCH_FLAT": ExpYieldConfig.INCREASE_FULL,
    "BUFF_SCAN_RATE": True,
    "CHANGE_FARM_EXP": True,
    
    
    # Randomization settings
    
    "ROOKIE_RESET_EVENT": RookieResetConfig.UNCHANGED,
    "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_SAME_STAGE,
    "NERF_FIRST_BOSS": True,                                  # city attack boss's max hp will be reduced by half (to compensate for no Lunamon at lvl 20)
    
    "RANDOMIZE_AREA_ENCOUNTERS": RandomizeWildEncounters.UNCHANGED,
    "AREA_ENCOUNTERS_STATS": model.LvlUpMode.FIXED_AVG,      # this defines how the randomized enemy digimon's stats are generated when changing the levels
    
    "RANDOMIZE_FIXED_BATTLES": False,
    "FIXED_BATTLES_DIGIMON_SAME_STAGE": True,                 # digimon will be swapped with another digimon of the same stage
    "FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES": False,             # do not change boss-exclusive digimon like ???, SkullBaluchimon, Grimmon, etc
    "FIXED_BATTLES_BALANCE_BY_BST": False,                    # if true, generated encounter will have roughly the same stat total as the original encounter (which can lead to a different digimon lvl); if false, the generated encounter will be set at the same level regardless of how stronger/weaker the new digimon is
    "FIXED_BATTLES_KEEP_HP": True,                            # do not change base HP of the encounter: most fixed battles have enemies with slightly more hp than usual, this will keep the digimon's HP stat the same as before
    
    
    "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.UNCHANGED,
    "DIGIVOLUTIONS_SIMILAR_SPECIES": True,        # example: holy digimon will be more likely to evolve into other holy digimon
    
    "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions.UNCHANGED,
    "DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP": True,       # example: a digivolution from the holy species will be less likely to have aquan/dark/etc exp as a requirement than other conditions

    "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions.RANDOMIZE_SAME_STAGE,
    #"FORCE_RARE_DNADIGIVOLUTIONS": dna_digivolution_force_rare_var,
    "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions.REMOVED,
    "DNADIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP":True,

    "RANDOMIZE_OVERWORLD_ITEMS": RandomizeOverworldItems.RANDOMIZE_COMPLETELY
    
}

# these settings are initialized upon creating ConfigManager, thus shared w/ all instances
# at the moment these are not obtainable through the tkinter ui but are needed nonetheless
inner_configmanager_settings = {
    "MOVEMENT_SPEED_MULTIPLIER": 1.5,
    "ENCOUNTER_RATE_MULTIPLIER": 0.5,
    "NEW_BASE_SCAN_RATE": 25,        # this is the base value for scanning an in-training digimon as normal rank tamer; -5 for each subsequent digivolution
    "DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS": 0.9,    # the total odds for the same species digimon will be the bias value (in this case it's 0.9), total odds for digimon from other species will be the remaining value (1 - bias)
    "DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS": 0.2,          # how less likely each exp condition is to be picked (in this case, the probability for each of those exp conditions is multiplied by the bias value; multiplying by 0.2 makes the condition 5 times less likely)
    "FARM_EXP_MODIFIER": 10             # multiplier for farm exp

}

PATH_SOURCE = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (USA).nds"
PATH_TARGET = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (USA)_overworlditem_test.nds"

#PATH_SOURCE = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA).nds"
#PATH_TARGET = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA)_qolpatch_contra.nds"
