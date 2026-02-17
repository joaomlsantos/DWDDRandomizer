from enum import Enum
import json
import re
from typing import Any, Dict

import toml
from src import model
from src import constants

APP_VERSION = "0.2.0"


class RookieResetConfig(Enum):
    UNCHANGED = 0                       # same as base game; resets digimon to rookies after the chaos event 
    #RESET_ALL_INCLUDING_LUNAMON = 1     # same as base game but also resets Lunamon to lvl 1
    RESET_KEEPING_EVO = 1               # reset digimon's levels, stats, etc, but keep them at their original form (ex: SkullGreymon stays as SkullGreymon but lvl 1) 
    DO_NOT_RESET = 2                    # rookie reset event does not happen; keeps digimon as they were before the chaos event


class RandomizeStartersConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RAND_SAME_STAGE = 1                 # randomize while keeping the same stage of the digimon
    RAND_FULL = 2                       # fully randomize
    CUSTOM = 3                          # custom starter packs


class RandomizeSpeciesConfig(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOM = 1                          # randomize digimon species


class RandomizeElementalResistances(Enum):
    UNCHANGED = 0                       # do not randomize
    SHUFFLE = 1                         # shuffles the existing values of a digimon's elemental resistances
    RANDOM = 2                          # randomizes the values for each elemental resistance (keeping the sum of the total for the given digimon)


class RandomizeBaseStats(Enum):
    UNCHANGED = 0                       # do not randomize
    SHUFFLE = 1                         # shuffles main base stats (atk, def, spirit, speed)
    RANDOM_SANITY = 2                   # randomizes within sanity ranges
    RANDOM_COMPLETELY = 3               # randomizes completely


class RandomizeDigimonStatType(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE = 1                       # randomize digimon type


class RandomizeMovesets(Enum):
    UNCHANGED = 0
    RANDOM_SPECIES_BIAS = 1             # randomize preferring moves of the given species' main element
    RANDOM_COMPLETELY = 2               # randomize completely


class RandomizeTraits(Enum):
    UNCHANGED = 0
    RANDOM_STAGE_BIAS = 1               # randomize while keeping traits coherent with each stage
    RANDOM_COMPLETELY = 2               # randomize completely


class RandomizeWildEncounters(Enum):
    UNCHANGED = 0                       # do not randomize
    RANDOMIZE_1_TO_1_SAME_STAGE = 1     # randomize 1-to-1, same stage digimon
    RANDOMIZE_1_TO_1_COMPLETELY = 2     # randomize 1-to-1, completely random digimon


class RandomizeEnemyDigimonEncounters(Enum):
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

class RandomizeItems(Enum):
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

    ENUM_KEYS = {
        "INCREASE_DIGIMON_EXP": ExpYieldConfig,
        "ROOKIE_RESET_EVENT": RookieResetConfig,
        "RANDOMIZE_STARTERS": RandomizeStartersConfig,
        "RANDOMIZE_OVERWORLD_ITEMS": RandomizeItems,
        "RANDOMIZE_QUEST_ITEM_REWARDS": RandomizeItems,
        "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters,
        "RANDOMIZE_WILD_ENCOUNTER_ITEMS": RandomizeItems,
        "WILD_ENCOUNTERS_STATS": model.LvlUpMode,
        "RANDOMIZE_FIXED_BATTLES": RandomizeEnemyDigimonEncounters,
        "RANDOMIZE_DIGIMON_SPECIES": RandomizeSpeciesConfig,
        "RANDOMIZE_ELEMENTAL_RESISTANCES": RandomizeElementalResistances,
        "RANDOMIZE_BASE_STATS": RandomizeBaseStats,
        "RANDOMIZE_DIGIMON_STATTYPE": RandomizeDigimonStatType,
        "RANDOMIZE_MOVESETS": RandomizeMovesets,
        "RANDOMIZE_TRAITS": RandomizeTraits,
        "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions,
        "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions,
        "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions,
        "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions,
    }

    @staticmethod
    def _resolve_condition_names(key, value):
        """Convert human-readable condition names to internal int IDs."""
        str_to_id = constants.DIGIVOLUTION_CONDITIONS_STR_TO_ID
        if key == "DIGIVOLUTION_CONDITIONS_VALUES" and isinstance(value, dict):
            return {(str_to_id[k] if k in str_to_id else int(k)): v for k, v in value.items()}
        if key == "DIGIVOLUTION_CONDITIONS_POOL" and isinstance(value, list) and value and isinstance(value[0], str):
            return [str_to_id[name] for name in value]
        return value

    def update_from_ui(self, ui_variables):
        for key, tk_var in ui_variables.items():
            if hasattr(tk_var, "get") and not isinstance(tk_var, (dict, list)):
                self.set(key, tk_var.get())
            else:
                self.set(key, self._resolve_condition_names(key, tk_var))

    def update_from_toml(self, toml_data: Dict[str, Any]):
        randomizer_options = toml_data.get("randomizer_options", {})

        for key, value in randomizer_options.items():
            if key in self.ENUM_KEYS and isinstance(value, int):
                value = self.ENUM_KEYS[key](value)
            self.set(key, value)

        advanced_settings = toml_data.get("advanced_settings", {})
        for key, value in advanced_settings.items():
            self.set(key, self._resolve_condition_names(key, value))


class PreferencesManager:
    
    ADVANCED_SETTINGS_DESCRIPTIONS = {
        "ENCOUNTER_RATE_MULTIPLIER": "Multiplier for wild encounter rate",
        "NEW_BASE_SCAN_RATE": "Base scan rate for in-training digimon as normal rank tamer; -5 per stage",
        "FARM_EXP_MODIFIER": "Multiplier for farm exp",
        "ENCOUNTER_MONEY_MULTIPLIER": "Multiplier for money earned in wild encounters",
        "EXP_DENOMINATOR": "Denominator in exp formula: (base_exp * lvl) / denominator",
        "EXP_FLAT_BY_STAGE": "Base exp value per stage used in exp yield formula: (base * lvl) / denominator",
        "MOVESET_SPECIES_BIAS": "Weight for same-element moves when randomizing movesets with species bias",
        "DIGIVOLUTION_CONDITIONS_POOL": "Pool of allowed digivolution condition types",
        "CONFIG_MOVE_LEVEL_RANGE": "Range for filtering moves by level when randomizing movesets",
        "CONFIG_MOVE_POWER_RANGE": "Range for filtering moves by power when randomizing movesets",
        "DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS": "Weight for same-species digivolutions; remaining (1 - bias) split among other species",
        "DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS": "Multiplier reducing probability of off-species exp conditions (0.2 = 5x less likely)",
        "DIGIVOLUTION_CONDITIONS_VALUES": "Condition -> [min, max] value ranges per stage (IN-TRAINING, ROOKIE, CHAMPION, ULTIMATE, MEGA)",
        "DIGIVOLUTION_AMOUNT_DISTRIBUTION": "Probability distribution for evolutions per stage: [0 evos, 1 evo, 2 evos, 3 evos]",
        "FIXED_BATTLE_STAT_TOLERANCE": "In fixed battles, stats are rescaled if they deviate more than this fraction from original",
        "MOVEMENT_SPEED_MULTIPLIER": "Multiplier for overworld movement speed",
    }

    @staticmethod
    def _toml_key(k):
        """Quote a TOML key if it contains characters beyond A-Za-z0-9_-."""
        if all(c.isalnum() or c in '-_' for c in str(k)):
            return str(k)
        return f'"{k}"'

    @staticmethod
    def _normalize_list_for_toml(lst):
        """Ensure arrays are homogeneous for TOML: if mixed int/float, convert all to float."""
        if not lst:
            return lst
        normalized = [PreferencesManager._normalize_list_for_toml(x) if isinstance(x, list) else x for x in lst]
        has_int = any(isinstance(x, int) and not isinstance(x, bool) for x in normalized)
        has_float = any(isinstance(x, float) for x in normalized)
        if has_int and has_float:
            return [float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else x for x in normalized]
        return normalized

    @staticmethod
    def _toml_value(v):
        """Serialize a Python value as a TOML inline value."""
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        if isinstance(v, str):
            return f'"{v}"'
        if isinstance(v, list):
            v = PreferencesManager._normalize_list_for_toml(v)
            return json.dumps(v, separators=(', ', ': '))
        return str(v)

    def _dump_preferences_toml(self, data: dict) -> str:
        """Format preferences as TOML with descriptive comments for advanced settings."""
        lines = []

        # top-level simple keys
        for k, v in data.items():
            if k == "advanced_settings":
                continue
            lines.append(f'{self._toml_key(k)} = {self._toml_value(v)}')

        advanced = data.get("advanced_settings", {})
        if not advanced:
            return '\n'.join(lines) + '\n'

        lines.append('')
        lines.append('[advanced_settings]')

        # separate simple values from dict values (dict values become sub-tables)
        simple_keys = [k for k in advanced if not isinstance(advanced[k], dict)]
        dict_keys = [k for k in advanced if isinstance(advanced[k], dict)]

        for k in simple_keys:
            v = advanced[k]
            desc = self.ADVANCED_SETTINGS_DESCRIPTIONS.get(k)
            if desc:
                lines.append(f'# {desc}')
            lines.append(f'{self._toml_key(k)} = {self._toml_value(v)}')
            lines.append('')

        # dict values as sub-tables
        for k in dict_keys:
            v = advanced[k]
            desc = self.ADVANCED_SETTINGS_DESCRIPTIONS.get(k)
            if desc:
                lines.append(f'# {desc}')
            lines.append(f'[advanced_settings.{self._toml_key(k)}]')
            for sk, sv in v.items():
                lines.append(f'{self._toml_key(sk)} = {self._toml_value(sv)}')
            lines.append('')

        return '\n'.join(lines) + '\n'

    @staticmethod
    def _fix_toml_mixed_arrays(text: str) -> str:
        """Pre-process TOML text to normalize mixed int/float arrays to all-float.
        TOML requires homogeneous arrays, so [0.85, 0.15, 0, 0] is invalid.
        This converts it to [0.85, 0.15, 0.0, 0.0] before parsing."""
        def fix_flat_array(match):
            content = match.group(1)
            if '[' in content:
                return match.group(0)  # skip nested arrays
            tokens = content.split(',')
            has_float = any('.' in t for t in tokens if t.strip() and t.strip().lstrip('-')[0:1].isdigit())
            if not has_float:
                return match.group(0)
            fixed = []
            for t in tokens:
                stripped = t.strip()
                if re.match(r'^-?\d+$', stripped):
                    fixed.append(t.replace(stripped, stripped + '.0'))
                else:
                    fixed.append(t)
            return '[' + ','.join(fixed) + ']'
        return re.sub(r'\[([^\[\]]*)\]', fix_flat_array, text)

    def _load_preferences_file(self, toml_path):
        """Load preferences from TOML."""
        try:
            with open(toml_path, 'r') as f:
                text = f.read()
            return toml.loads(self._fix_toml_mixed_arrays(text))
        except FileNotFoundError:
            pass
        return {}


# QoL settings

# these are loaded specifically when running qol_script directly
default_configmanager_settings = {

    "INCREASE_TEXT_SPEED": True,
    "INCREASE_MOVEMENT_SPEED": True,
    "REDUCE_WILD_ENCOUNTER_RATE": True,
    "CHANGE_STAT_CAPS": True,
    "EXPAND_PLAYER_NAME_LENGTH": True,
    
    "INCREASE_DIGIMON_EXP": ExpYieldConfig.INCREASE_FULL,
    "INCREASE_SCAN_RATE": True,
    "INCREASE_FARM_EXP": True,
    
    
    # Randomization settings
    
    "ROOKIE_RESET_EVENT": RookieResetConfig.UNCHANGED,
    "RANDOMIZE_STARTERS": RandomizeStartersConfig.RAND_SAME_STAGE,
    "NERF_FIRST_BOSS": True,                                  # city attack boss's max hp will be reduced by half (to compensate for no Lunamon at lvl 20)
    
    "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters.UNCHANGED,
    "WILD_ENCOUNTERS_STATS": model.LvlUpMode.FIXED_AVG,      # this defines how the randomized enemy digimon's stats are generated when changing the levels
    
    "RANDOMIZE_FIXED_BATTLES": False,
    "FIXED_BATTLES_DIGIMON_SAME_STAGE": True,                 # digimon will be swapped with another digimon of the same stage
    "FIXED_BATTLES_KEEP_EXCLUSIVE_BOSSES": False,             # do not change boss-exclusive digimon like ???, SkullBaluchimon, Grimmon, etc
    "FIXED_BATTLES_BALANCE_BY_BST": False,                    # if true, generated encounter will have roughly the same stat total as the original encounter (which can lead to a different digimon lvl); if false, the generated encounter will be set at the same level regardless of how stronger/weaker the new digimon is
    "FIXED_BATTLES_KEEP_HP": True,                            # do not change base HP of the encounter: most fixed battles have enemies with slightly more hp than usual, this will keep the digimon's HP stat the same as before
    
    
    "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions.UNCHANGED,
    "DIGIVOLUTIONS_SIMILAR_SPECIES": True,        # example: holy digimon will be more likely to evolve into other holy digimon
    
    "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions.UNCHANGED,
    "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": True,       # example: a digivolution from the holy species will be less likely to have aquan/dark/etc exp as a requirement than other conditions

    "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions.RANDOMIZE_SAME_STAGE,
    #"FORCE_RARE_DNADIGIVOLUTIONS": dna_digivolution_force_rare_var,
    "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions.REMOVED,
    "DNADIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP":True,

    "RANDOMIZE_OVERWORLD_ITEMS": RandomizeItems.RANDOMIZE_COMPLETELY
    
}

# these settings are initialized upon creating ConfigManager, thus shared w/ all instances
# at the moment these are not obtainable through the tkinter ui but are needed nonetheless
# advanced users can edit these values in the "advanced_settings" section of preferences.toml
inner_configmanager_settings = {

    # most important
    "ENCOUNTER_RATE_MULTIPLIER": 0.5,
    "NEW_BASE_SCAN_RATE": 25,        # this is the base value for scanning an in-training digimon as normal rank tamer; -5 for each subsequent digivolution
    "FARM_EXP_MODIFIER": 10,             # multiplier for farm exp
    "ENCOUNTER_MONEY_MULTIPLIER": 4,              # multiplier for money earned in wild encounters
    "EXP_DENOMINATOR": 14,                # denominator in exp formula: (base_exp * lvl) / denominator
    "EXP_FLAT_BY_STAGE": {               # base exp value per stage used in exp yield formula: (base * lvl) / denominator
        "IN-TRAINING": 40,
        "ROOKIE": 80,
        "CHAMPION": 120,
        "ULTIMATE": 160,
        "MEGA": 300
    },

    "WILD_DIGIMON_HP_BUFF_BY_STAGE": {
        "IN-TRAINING": 1,
        "ROOKIE": 1,
        "CHAMPION": 3,
        "ULTIMATE": 4,
        "MEGA": 5
    },

    # relatively important
    "MOVESET_SPECIES_BIAS": 0.9,         # when randomizing movesets with species bias, this is the weight for same-element moves
    "DIGIVOLUTION_CONDITIONS_POOL": ["DRAGON EXP", "BEAST EXP", "AQUAN EXP", "BIRD EXP", "INSECTPLANT EXP", "MACHINE EXP", "DARK EXP", "HOLY EXP", "SPECIES EXP", "ATK STAT", "DEF STAT", "SPEED STAT", "SPIRIT STAT", "FRIENDSHIP % STAT"],
    "CONFIG_MOVE_LEVEL_RANGE": 5,        # range for filtering moves by level when randomizing movesets
    "CONFIG_MOVE_POWER_RANGE": 8,        # range for filtering moves by power when randomizing movesets
    "DIGIVOLUTIONS_SIMILAR_SPECIES_BIAS": 0.9,    # the total odds for the same species digimon will be the bias value (in this case it's 0.9), total odds for digimon from other species will be the remaining value (1 - bias)
    "DIGIVOLUTION_CONDITIONS_DIFF_SPECIES_EXP_BIAS": 0.2,          # how less likely each exp condition is to be picked (in this case, the probability for each of those exp conditions is multiplied by the bias value; multiplying by 0.2 makes the condition 5 times less likely)

    # condition name -> [min, max] value ranges per stage (IN-TRAINING, ROOKIE, CHAMPION, ULTIMATE, MEGA)
    "DIGIVOLUTION_CONDITIONS_VALUES": {
        "NONE": [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
        "LEVEL": [[1, 5], [7, 16], [17, 30], [32, 45], [46, 65]],
        "DRAGON EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "BEAST EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "AQUAN EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "BIRD EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "INSECTPLANT EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "MACHINE EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "DARK EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "HOLY EXP": [[0, 0], [100, 500], [300, 1000], [1500, 8000], [5000, 30000]],
        "SPECIES EXP": [[0, 0], [300, 1500], [1000, 3000], [4500, 20000], [15000, 90000]],
        "ATK STAT": [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
        "DEF STAT": [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
        "SPEED STAT": [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
        "SPIRIT STAT": [[0, 0], [50, 90], [90, 150], [130, 225], [200, 400]],
        "APTITUDE STAT": [[0, 0], [15, 25], [25, 40], [40, 50], [50, 65]],
        "FRIENDSHIP % STAT": [[0, 0], [50, 70], [60, 70], [70, 80], [90, 100]],
        "DIGIMON ID IN PARTY": [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]],
        "BEFRIENDED DIGIMON ID": [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
    },

    # probability distribution for number of evolutions per stage: [0 evos, 1 evo, 2 evos, 3 evos]
    "DIGIVOLUTION_AMOUNT_DISTRIBUTION": {
        "IN-TRAINING": [0, 0.2, 0.4, 0.4],
        "ROOKIE": [0, 0.25, 0.55, 0.2],
        "CHAMPION": [0.25, 0.4, 0.3, 0.05],
        "ULTIMATE": [0.3, 0.5, 0.18, 0.02],
        "MEGA": [1, 0, 0, 0]
    },

    # low priority
    "FIXED_BATTLE_STAT_TOLERANCE": 0.20,  # in fixed battles, generated stats are rescaled if they deviate more than this fraction from the original
    "MOVEMENT_SPEED_MULTIPLIER": 1.5,
}

PATH_SOURCE = "C:/Workspace/digimon_stuffs/rom_files/1421 - Digimon World - Dawn (USA).nds"
PATH_TARGET = "C:/Workspace/digimon_stuffs/rom_files/1421 - Digimon World - Dawn (USA)_overworlditem_test.nds"

#PATH_SOURCE = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA).nds"
#PATH_TARGET = "C:/Workspace/digimon_stuffs/Digimon World - Dusk (USA)_qolpatch_contra.nds"
