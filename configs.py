from enum import Enum
from src import model


# strife was here
class RookieResetConfig(Enum):
    UNCHANGED = 0                       # same as base game; resets digimon to rookies after the chaos event 
    RESET_ALL_INCLUDING_LUNAMON = 1     # same as base game but also resets Lunamon to lvl 1
    RESET_KEEPING_EVO = 2               # reset digimon's levels, stats, etc, but keep them at their original form (ex: SkullGreymon stays as SkullGreymon but lvl 1) 
    DO_NOT_RESET = 3                    # rookie reset event does not happen; keeps digimon as they were before the chaos event


class RandomizeStartersConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RAND_SAME_STAGE = 1                 # randomize while keeping the same stage of the digimon
    RAND_FULL = 2                       # fully randomize


# QoL settings

CHANGE_TEXT_SPEED = True
CHANGE_MOVEMENT_SPEED = True
MOVEMENT_SPEED_MULTIPLIER = 1.5
CHANGE_ENCOUNTER_RATE = True
ENCOUNTER_RATE_MULTIPLIER = 0.5
CHANGE_STAT_CAPS = True
EXTEND_PLAYERNAME_SIZE = True

APPLY_EXP_PATCH_FLAT = True



# Randomization settings

ROOKIE_RESET_EVENT = RookieResetConfig.UNCHANGED
RANDOMIZE_STARTERS = RandomizeStartersConfig.UNCHANGED
NERF_FIRST_BOSS = True                                  # city attack boss's max hp will be reduced by half (to compensate for no Lunamon at lvl 20)

RANDOMIZE_AREA_ENCOUNTERS = False
AREA_ENCOUNTERS_STATS = model.LvlUpMode.FIXED_AVG      # this defines how the randomized enemy digimon's stats are generated when changing the levels

RANDOMIZE_FIXED_BATTLES = False
FIXED_BATTLES_DIGIMON_SAME_STAGE = True                 # digimon will be swapped with another digimon of the same stage
FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES = False             # do not change boss-exclusive digimon like ???, SkullBaluchimon, Grimmon, etc
FIXED_BATTLES_BALANCE_BY_BST = False                    # if true, generated encounter will have roughly the same stat total as the original encounter (which can lead to a different digimon lvl); if false, the generated encounter will be set at the same level regardless of how stronger/weaker the new digimon is
FIXED_BATTLES_KEEP_HP = True                            # do not change base HP of the encounter: most fixed battles have enemies with slightly more hp than usual, this will keep the digimon's HP stat the same as before


RANDOMIZE_DIGIVOLUTIONS = False
DIGIVOLUTIONS_SIMILAR_SPECIES = True        # example: holy digimon will be more likely to evolve into other holy digimon
DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS = 0.8    # the total odds for the same species digimon will be the bias value (in this case it's 0.8), total odds for digimon from other species will be the remaining value (1 - bias)
DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP = True       # example: a digivolution from the holy species will be less likely to have aquan/dark/etc exp as a requirement than other conditions
DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS = 0.2          # how less likely each exp condition is to be picked (in this case, the probability for each of those exp conditions is multiplied by the bias value; multiplying by 0.2 makes the condition 5 times less likely)


#PATH_SOURCE = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (U)(XenoPhobia).nds"
#PATH_TARGET = "C:/Workspace/digimon_stuffs/1421 - Digimon World - Dawn (U)_deltapatched.nds"

PATH_SOURCE = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA).nds"
PATH_TARGET = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA)_deltapatched_randomized_1.nds"
