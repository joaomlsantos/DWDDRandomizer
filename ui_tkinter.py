from collections import OrderedDict
import copy
from datetime import datetime
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List

import toml
from src import utils
from ui.tooltip import CreateToolTip
import os
from qol_script import DigimonROM, Randomizer
from configs import APP_VERSION, ExpYieldConfig, RandomizeDnaDigivolutionConditions, RandomizeDnaDigivolutions, RandomizeMovesets, RandomizeItems, RandomizeSpeciesConfig, RandomizeStartersConfig, RandomizeWildEncounters, RandomizeDigivolutions, RandomizeDigivolutionConditions, ConfigManager, RookieResetConfig, RandomizeElementalResistances, RandomizeBaseStats, RandomizeDigimonStatType, RandomizeTraits, RandomizeEnemyDigimonEncounters, inner_configmanager_settings
from src.model import LvlUpMode
from pathlib import Path
import webbrowser
import sys
import random
import numpy as np
import logging
from io import StringIO
from ui.LabelledSlider import LabelledSlider
from ui import autoUpdater

class AppState:
    def __init__(self):
        self.config_manager: ConfigManager = ConfigManager()
        self.current_rom: DigimonROM = None
        self.target_rom: DigimonROM = None
        self.randomizer: Randomizer = None
        self.log_stream: StringIO = StringIO()
        self.logger: logging.Logger = self.setLogger()
        self.seed: int = -1
        self.last_rom_dir: str = None
        self.custom_starters_packs = []
        self.load_preferences()

    def _get_app_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def _get_preferences_path(self):
        return os.path.join(self._get_app_dir(), "preferences.toml")


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
        normalized = [AppState._normalize_list_for_toml(x) if isinstance(x, list) else x for x in lst]
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
            v = AppState._normalize_list_for_toml(v)
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

    def _load_preferences_file(self):
        """Load preferences from TOML."""
        toml_path = self._get_preferences_path()
        try:
            with open(toml_path, 'r') as f:
                text = f.read()
            return toml.loads(self._fix_toml_mixed_arrays(text))
        except FileNotFoundError:
            pass
        return {}

    def load_preferences(self):
        preferences = self._load_preferences_file()
        self.last_rom_dir = preferences.get("last_rom_dir")
        advanced = preferences.get("advanced_settings")
        if advanced:
            self.config_manager.update_from_ui(advanced)

    def save_preferences(self):
        # load existing preferences to preserve fields we don't manage (e.g. skipped_update_version)
        existing = self._load_preferences_file()
        existing["last_rom_dir"] = self.last_rom_dir
        try:
            with open(self._get_preferences_path(), 'w') as f:
                f.write(self._dump_preferences_toml(existing))
        except Exception:
            pass

    def initialize_advanced_settings(self):
        """Ensure advanced_settings section exists in preferences.toml with all default keys.
        Called on first ROM load. Adds any missing keys without overwriting existing user edits."""
        existing = self._load_preferences_file()

        advanced = existing.get("advanced_settings", {})
        updated = False
        for key, default_value in inner_configmanager_settings.items():
            if key not in advanced:
                advanced[key] = default_value
                updated = True

        if updated:
            existing["advanced_settings"] = advanced
            try:
                with open(self._get_preferences_path(), 'w') as f:
                    f.write(self._dump_preferences_toml(existing))
            except Exception:
                pass

        # load the advanced settings into config_manager
        self.config_manager.update_from_ui(advanced)

    def setLogger(self):
        logger = logging.getLogger(__name__)
        logging.basicConfig(stream=self.log_stream, level=logging.INFO, format='%(message)s')
        return logger
    
    def writeLog(self, fpath: str):
        with open(fpath + ".log", "w", encoding="utf8") as log_f:
            log_f.write(self.log_stream.getvalue())

    def apply_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)


app_state = AppState()

# Path to the icon file
if getattr(sys, 'frozen', False):  # Running as a bundled app
    bundle_dir = sys._MEIPASS
else:  # Running as a script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

#icon_path = os.path.join(bundle_dir, "public", "dusk_transparent.ico")
icon_png_path = os.path.join(bundle_dir, "public", "dusk_transparent.png")      # fixing issue w linux icons, making icon universal



def get_patcher_config_options():
    
    patcher_config_options = {
        "INCREASE_TEXT_SPEED": change_text_speed_var,
        "INCREASE_MOVEMENT_SPEED": change_movement_speed_var,
        "EXPAND_PLAYER_NAME_LENGTH": expand_player_name_var,
        "IMPROVE_BATTLE_PERFORMANCE": improve_battle_performance_var,
        #"CHANGE_STAT_CAPS": increase_stat_caps_var,

        "REDUCE_WILD_ENCOUNTER_RATE": change_wild_encounter_rate_var,
        "INCREASE_SCAN_RATE": increase_flat_scan_rate_var,
        "INCREASE_DIGIMON_EXP": ExpYieldConfig.INCREASE_HALVED if exp_wild_digimon_var.get() else ExpYieldConfig.UNCHANGED,
        "INCREASE_WILD_ENCOUNTER_MONEY": buff_wild_encounter_money_var,
        "INCREASE_FARM_EXP": change_farm_exp_var,
        "BALANCE_CALUMON_STATS": balance_calumon_var,
    
        "ENABLE_LEGENDARY_TAMER_QUEST": quests_enable_legendary_tamer_var,
        "UNLOCK_MAIN_QUESTS_IN_SEQUENCE": quests_unlock_main_in_sequence_var,
        "UNLOCK_VERSION_EXCLUSIVE_AREAS": unlock_version_exclusive_areas_var,

        "RANDOMIZE_STARTERS": RandomizeStartersConfig(starters_option_var.get()),  # RandomizeStartersConfig(starters_option_var) might have to be initialized like this
        "CUSTOM_STARTER_PACKS": get_custom_starters_data(),
        "NERF_FIRST_BOSS": nerf_first_boss_var,
        "FORCE_STARTER_W_ROOKIE_STAGE": force_starter_w_rookie_var,
        "ROOKIE_RESET_EVENT": RookieResetConfig(rookie_reset_option_var.get()),
        
        "RANDOMIZE_OVERWORLD_ITEMS": RandomizeItems(overworld_items_option_var.get()),
        "RANDOMIZE_QUEST_ITEM_REWARDS": RandomizeItems(quest_rewards_option_var.get()),

        "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": RandomizeWildEncounters(wild_digimon_option_var.get()),
        "RANDOMIZE_WILD_ENCOUNTER_ITEMS": RandomizeItems(wild_encounter_items_option_var.get()),
        "WILD_ENCOUNTERS_STATS": stat_gen_option_var,
        "RANDOMIZE_FIXED_BATTLES": RandomizeEnemyDigimonEncounters(enemy_digimon_option_var.get()),

        "RANDOMIZE_DIGIMON_SPECIES": RandomizeSpeciesConfig(species_option_var.get()),
        "SPECIES_ALLOW_UNKNOWN": species_allow_unknown_var,
        "RANDOMIZE_ELEMENTAL_RESISTANCES": RandomizeElementalResistances(elemental_res_option_var.get()),
        "KEEP_SPECIES_RESISTANCE_COHERENCE": elemental_res_keep_coherence_var,
        "RANDOMIZE_BASE_STATS": RandomizeBaseStats(base_stats_option_var.get()),
        "BASESTATS_STATTYPE_BIAS": base_stats_bias_type_var,
        "RANDOMIZE_DIGIMON_STATTYPE": RandomizeDigimonStatType(digimon_type_option_var.get()),

        "RANDOMIZE_MOVESETS": RandomizeMovesets(movesets_option_var.get()),
        "MOVESETS_LEVEL_BIAS": movesets_level_bias_var,
        "REGULAR_MOVE_POWER_BIAS": movesets_power_bias_var,
        "SIGNATURE_MOVE_POWER_BIAS": movesets_signature_power_bias_var,
        "MOVESETS_SIGNATURE_MOVES_POOL": movesets_signature_moves_var,
        "MOVESETS_GUARANTEE_BASIC_MOVE": movesets_guarantee_basic_move_var,

        "RANDOMIZE_TRAITS": RandomizeTraits(traits_option_var.get()),
        "TRAITS_FORCE_FOUR": traits_force_four_var,
        "TRAITS_ENABLE_UNUSED": traits_enable_unused_var,

        "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions(digivolutions_option_var.get()),
        "DIGIVOLUTIONS_SIMILAR_SPECIES": digivolution_similar_species_var,
        "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions(digivolution_conditions_option_var.get()),
        "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": digivolution_conditions_species_exp_var,

        "RANDOMIZE_DNADIGIVOLUTIONS": RandomizeDnaDigivolutions(dna_digivolutions_option_var.get()),
        #"FORCE_RARE_DNADIGIVOLUTIONS": dna_digivolution_force_rare_var,
        "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": RandomizeDnaDigivolutionConditions(dna_digivolution_conditions_option_var.get()),
        "DNADIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": dna_digivolution_conditions_species_exp_var,
    }
    
    return patcher_config_options




# this function is called when writing the patched/randomized rom; serves as the equivalent to main() for qol_script
def execute_rom_changes(save_path):

    patcher_config_options = get_patcher_config_options()


    if(app_state.seed == -1):
        app_state.seed = random.randrange(2**32-1)
        
    app_state.apply_seed()
    app_state.config_manager.update_from_ui(patcher_config_options)
    
    app_state.target_rom.executeQolChanges()
    app_state.randomizer.executeRandomizerFunctions(app_state.target_rom.rom_data)
    app_state.target_rom.writeRom(save_path)
    app_state.writeLog(save_path)
    app_state.seed = -1
    app_state.target_rom = copy.deepcopy(app_state.current_rom)     # next randomization will be applied to base rom instead of previously randomized rom again
    app_state.randomizer = Randomizer(app_state.target_rom.version, app_state.target_rom.rom_data, app_state.config_manager, app_state.logger)  # reset randomizer state
    app_state.target_rom.config_manager = app_state.config_manager
    app_state.log_stream.truncate(0)    # reset logger
    app_state.log_stream.seek(0)        # reset logger




def enable_buttons():
    
    # Enable Save/Import/Export
    save_changes_button.configure(state="normal")
    import_settings_button.configure(state="normal")
    export_settings_button.configure(state="normal")

    # Enable qol checkboxes
    textSpeedCheckbox.configure(state="normal")
    increaseMovementSpeedCheckbox.configure(state="normal")
    decreaseWildEncounterCheckbox.configure(state="normal")
    #increaseStatCapsCheckbox.configure(state="normal")
    #increaseExpYieldCheckbox.configure(state="normal")
    increaseFlatScanRateCheckbox.configure(state="normal")
    expandPlayerNameCheckbox.configure(state="normal")
    improveBattlePerformanceCheckbox.configure(state="normal")
    increaseFarmExpCheckbox.configure(state="normal")
    unlockVersionExclusiveAreasCheckbox.configure(state="normal")
    increaseExpWildDigimonCheckbox.configure(state="normal")
    #exp_yield_unchanged_rb.configure(state="normal")
    #exp_yield_halved_rb.configure(state="normal")
    #exp_yield_full_rb.configure(state="normal")


    # Enable tabs
    notebook.tab(0, state="normal")  # QoL Changes tab
    notebook.tab(1, state="normal")  # Randomization Settings tab

    # Enable randomization options
    # Randomize starters
    starters_unchanged_rb.configure(state="normal")
    starters_same_stage_rb.configure(state="normal")
    starters_completely_random_rb.configure(state="normal")
    starters_custom_rb.configure(state="normal")
    rookie_reset_unchanged_rb.configure(state="normal")
    rookie_reset_same_stage_rb.configure(state="normal")
    rookie_reset_cancel_rb.configure(state="normal")
    nerfFirstBossCheckbox.configure(state="normal")
    forceStarterWRookieCheckbox.configure(state="normal")

    # Randomize wild digimon
    wild_digimon_unchanged_rb.configure(state="normal")
    wild_digimon_randomize_rb.configure(state="normal")
    wild_digimon_randomize_completely_rb.configure(state="normal")
    balanceCalumonCheckbox.configure(state="normal")

    # Randomize wild encounter item drops
    wild_encounter_items_unchanged_rb.configure(state="normal")
    wild_encounter_items_same_category_rb.configure(state="normal")
    wild_encounter_items_completely_random_rb.configure(state="normal")
    buffWildEncounterMoneyCheckbox.configure(state="normal")

    # Randomize fixed enemies
    enemy_digimon_unchanged_rb.configure(state="normal")
    enemy_digimon_randomize_rb.configure(state="normal")
    enemy_digimon_randomize_completely_rb.configure(state="normal")


    # Randomize overworld items
    overworld_items_unchanged_rb.configure(state="normal")
    overworld_items_same_category_rb.configure(state="normal")
    overworld_items_completely_random_rb.configure(state="normal")

    # Quest data
    quest_rewards_unchanged_rb.configure(state="normal")
    quest_rewards_same_category_rb.configure(state="normal")
    quest_rewards_completely_random_rb.configure(state="normal")
    questsUnlockMainQuestsInSequenceCheckbox.configure(state="normal")
    questsEnableLegendaryTamerCheckbox.configure(state="normal")

    # Randomize digimon species
    species_unchanged_rb.configure(state="normal")
    species_random_rb.configure(state="normal")
    speciesAllowUnknownCheckbox.configure(state="normal")

    # Randomize elemental resistances
    elemental_res_unchanged_rb.configure(state="normal")
    elemental_res_shuffle_rb.configure(state="normal")
    elemental_res_randomize_rb.configure(state="normal")
    elementalResKeepCoherenceCheckbox.configure(state="normal")

    # Randomize base stats
    base_stats_unchanged_rb.configure(state="normal")
    base_stats_shuffle_rb.configure(state="normal")
    base_stats_random_sane_rb.configure(state="normal")
    base_stats_random_full_rb.configure(state="normal")
    base_stats_bias_type_cb.configure(state="normal")
    
    # Randomize stat type
    digimon_type_unchanged_rb.configure(state="normal")
    digimon_type_randomize_rb.configure(state="normal")
    

    # Randomize movesets
    movesets_unchanged_rb.configure(state="normal")
    movesets_randomize_same_species_rb.configure(state="normal")
    movesets_randomize_rb.configure(state="normal")
    movesetsLevelBiasCheckbox.configure(state="normal")
    movesetsPowerBiasCheckbox.configure(state="normal")
    movesetsSignaturePowerBiasCheckbox.configure(state="normal")
    movesetsSignatureMovesCheckbox.configure(state="normal")
    movesetsGuaranteeBasicMoveCheckbox.configure(state="normal")


    # Randomize traits
    traits_unchanged_rb.configure(state="normal")
    traits_randomize_same_stage_rb.configure(state="normal")
    traits_randomize_completely_rb.configure(state="normal")
    traitsForceFourCheckbox.configure(state="normal")
    traitsEnableUnusedCheckbox.configure(state="normal")


    # Randomize digivolutions and conditions
    digivolutions_unchanged_rb.configure(state="normal")
    digivolutions_randomize_rb.configure(state="normal")
    digivolution_conditions_unchanged_rb.configure(state="normal")
    digivolution_conditions_randomize_rb.configure(state="normal")
    digivolutionConditionsSpeciesExpCheckbox.configure(state="normal")

    # Randomize DNA digivolutions and conditions
    dna_digivolutions_unchanged_rb.configure(state="normal")
    dna_digivolutions_randomize_same_stage_rb.configure(state="normal")
    dna_digivolutions_randomize_completely_rb.configure(state="normal")
    dna_digivolution_conditions_unchanged_rb.configure(state="normal")
    dna_digivolution_conditions_randomize_rb.configure(state="normal")
    dna_digivolution_conditions_remove_rb.configure(state="normal")
    dnaDigivolutionConditionsSpeciesExpCheckbox.configure(state="normal")



def load_starters():
    """Load current starter pack values from ROM."""
    starters_array = app_state.randomizer.getStartersArray()

    for pack_ix in range(len(starters_array)):
        for starter_ix in range(len(starters_array[pack_ix])):
            app_state.custom_starters_packs[pack_ix][starter_ix].set(starters_array[pack_ix][starter_ix])
            

def open_rom():
    file_path = filedialog.askopenfilename(
        title="Open ROM",
        filetypes=[("ROM Files", "*.nds"), ("All Files", "*.*")],
        initialdir=app_state.last_rom_dir
    )
    if file_path:
        try:
            app_state.current_rom = DigimonROM(file_path, app_state.config_manager, app_state.logger)
            app_state.target_rom = copy.deepcopy(app_state.current_rom)
            app_state.target_rom.config_manager = app_state.config_manager
            app_state.randomizer = Randomizer(app_state.target_rom.version, app_state.target_rom.rom_data, app_state.config_manager, app_state.logger)
        except ValueError as e:
            messagebox.showerror("Error", e.args[0])
            #messagebox.showerror("Error","Game not recognized. Please check your rom (file \"" +  os.path.basename(file_path) + "\").")
            return

        # Remember the ROM directory for next time
        app_state.last_rom_dir = os.path.dirname(file_path)
        app_state.save_preferences()

        # Initialize advanced settings in preferences.toml (adds missing keys with defaults)
        app_state.initialize_advanced_settings()


        filename = os.path.basename(file_path)
        max_chars = 56
        if len(filename) > max_chars:
            filename = filename[:max_chars-3] + "..."
        rom_name_label.config(text=f"ROM Name: {filename}")
        #rom_name_label.config(text=f"ROM Name: {file_path.split('/')[-1]}")
        #rom_size_label.config(text=f"ROM Size: {os.path.getsize(file_path) / 1024:.2f} KB")
        rom_version_label.config(text=f"ROM Version: {app_state.current_rom.version}")
        #rom_path_label.config(text=f"ROM Path: {file_path}")

        rom_status_label.config(text="Status: Loaded")

        load_starters()

        # Enable interface
        enable_buttons()


def save_changes():
    
    rom_dir = os.path.dirname(app_state.target_rom.fpath)
    save_path = filedialog.asksaveasfilename(
        title="Save ROM",
        defaultextension=".nds",
        filetypes=[("ROM Files", "*.nds"), ("All Files", "*.*")],
        initialdir=rom_dir,
        #initialfile=Path(app_state.current_rom.fpath).stem + "_patched.nds"
    )
    if save_path:
        try:
            execute_rom_changes(save_path)
            messagebox.showinfo("ROM patched successfully!", f"Changes saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")


EXPORT_SETTINGS_DESCRIPTIONS = {
    # QoL
    "INCREASE_TEXT_SPEED": "Increase dialogue text speed",
    "INCREASE_MOVEMENT_SPEED": "Increase overworld movement speed",
    "EXPAND_PLAYER_NAME_LENGTH": "Allow longer player names",
    "IMPROVE_BATTLE_PERFORMANCE": "Improve battle performance by removing visual effects",
    "REDUCE_WILD_ENCOUNTER_RATE": "Reduce the wild encounter rate",
    "INCREASE_SCAN_RATE": "Increase the base digimon scan rate",
    "INCREASE_DIGIMON_EXP": "Increase exp yield from battles (0 = unchanged, 1 = halved, 2 = full)",
    "INCREASE_WILD_ENCOUNTER_MONEY": "Increase money earned from wild encounters",
    "INCREASE_FARM_EXP": "Increase farm exp gain",
    "BALANCE_CALUMON_STATS": "Balance Calumon's base stats",
    "ENABLE_LEGENDARY_TAMER_QUEST": "Enable Legendary Tamer quest",
    "UNLOCK_MAIN_QUESTS_IN_SEQUENCE": "Unlock main quests in sequence",
    "UNLOCK_VERSION_EXCLUSIVE_AREAS": "Unlock version-exclusive areas",
    # Starters
    "RANDOMIZE_STARTERS": "Randomize starter packs (0 = unchanged, 1 = same stage, 2 = fully random, 3 = custom)",
    "NERF_FIRST_BOSS": "Nerf first boss to compensate for randomized starters",
    "FORCE_STARTER_W_ROOKIE_STAGE": "Force at least one starter to be a Rookie",
    "ROOKIE_RESET_EVENT": "Rookie reset event behavior (0 = unchanged, 1 = reset keeping evo, 2 = do not reset)",
    # Items
    "RANDOMIZE_OVERWORLD_ITEMS": "Randomize overworld items (0 = unchanged, 1 = keep category, 2 = completely)",
    "RANDOMIZE_QUEST_ITEM_REWARDS": "Randomize quest item rewards (0 = unchanged, 1 = keep category, 2 = completely)",
    # Wild encounters
    "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": "Randomize wild digimon encounters (0 = unchanged, 1 = same stage, 2 = completely)",
    "RANDOMIZE_WILD_ENCOUNTER_ITEMS": "Randomize wild encounter item drops (0 = unchanged, 1 = keep category, 2 = completely)",
    "WILD_ENCOUNTERS_STATS": "Stat generation mode for randomized wild encounters",
    "RANDOMIZE_FIXED_BATTLES": "Randomize fixed battle encounters (0 = unchanged, 1 = same stage, 2 = completely)",
    # Species
    "RANDOMIZE_DIGIMON_SPECIES": "Randomize digimon species (0 = unchanged, 1 = random)",
    "SPECIES_ALLOW_UNKNOWN": "Allow Unknown species in randomization",
    "RANDOMIZE_ELEMENTAL_RESISTANCES": "Randomize elemental resistances (0 = unchanged, 1 = shuffle, 2 = random)",
    "KEEP_SPECIES_RESISTANCE_COHERENCE": "Keep elemental resistances coherent with species",
    "RANDOMIZE_BASE_STATS": "Randomize base stats (0 = unchanged, 1 = shuffle, 2 = random sanity, 3 = random completely)",
    "BASESTATS_STATTYPE_BIAS": "Bias base stat randomization towards digimon type",
    "RANDOMIZE_DIGIMON_STATTYPE": "Randomize digimon stat type (0 = unchanged, 1 = randomize)",
    # Movesets
    "RANDOMIZE_MOVESETS": "Randomize movesets (0 = unchanged, 1 = species bias, 2 = completely)",
    "MOVESETS_LEVEL_BIAS": "Filter randomized moves by level proximity",
    "REGULAR_MOVE_POWER_BIAS": "Filter randomized regular moves by power proximity",
    "SIGNATURE_MOVE_POWER_BIAS": "Filter randomized signature moves by power proximity",
    "MOVESETS_SIGNATURE_MOVES_POOL": "Include signature moves in the randomization pool",
    "MOVESETS_GUARANTEE_BASIC_MOVE": "Guarantee at least one basic (no MP cost) move",
    # Traits
    "RANDOMIZE_TRAITS": "Randomize traits (0 = unchanged, 1 = stage bias, 2 = completely)",
    "TRAITS_FORCE_FOUR": "Force all digimon to have four traits",
    "TRAITS_ENABLE_UNUSED": "Include unused traits in the randomization pool",
    # Digivolutions
    "RANDOMIZE_DIGIVOLUTIONS": "Randomize digivolution trees (0 = unchanged, 1 = randomize)",
    "DIGIVOLUTIONS_SIMILAR_SPECIES": "Bias digivolutions towards similar species",
    "RANDOMIZE_DIGIVOLUTION_CONDITIONS": "Randomize digivolution conditions (0 = unchanged, 1 = randomize)",
    "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": "Bias conditions towards matching species exp",
    # DNA
    "RANDOMIZE_DNADIGIVOLUTIONS": "Randomize DNA digivolutions (0 = unchanged, 1 = same stage, 2 = completely)",
    "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": "Randomize DNA digivolution conditions (0 = unchanged, 1 = randomize, 2 = removed)",
    "DNADIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": "Bias DNA conditions towards matching species exp",
}


def export_settings():
    patcher_config_options = get_patcher_config_options()
    toml_data = OrderedDict()

    toml_data["app_data"] = OrderedDict()
    toml_data["app_data"]["APP_VERSION"] = APP_VERSION
    toml_data["app_data"]["ROM_VERSION"] = app_state.current_rom.version
    toml_data["app_data"]["SEED"] = app_state.seed

    toml_data["randomizer_options"] = OrderedDict()

    # enum case, tkinter var case, bool/int case
    for key, value in patcher_config_options.items():
        if hasattr(value, 'value'):
            toml_data["randomizer_options"][key] = value.value
        elif hasattr(value, 'get'):
            toml_data["randomizer_options"][key] = value.get()
        else:
            toml_data["randomizer_options"][key] = value

    # include current advanced settings
    toml_data["advanced_settings"] = dict(inner_configmanager_settings)

    configs_dir = os.path.join(app_state._get_app_dir(), "configs")
    os.makedirs(configs_dir, exist_ok=True)

    toml_path = filedialog.asksaveasfilename(
        title="Export Settings",
        defaultextension=".toml",
        filetypes=[("TOML Files", "*.toml"), ("All Files", "*.*")],
        initialdir=configs_dir
    )

    if toml_path:
        try:
            with open(toml_path, 'w') as f:
                f.write(_format_export_toml(toml_data))
            messagebox.showinfo("Success", f"Settings exported to:\n{toml_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings:\n{str(e)}")


def _format_export_toml(data: dict) -> str:
    """Format exported settings TOML with descriptive comments."""
    lines = [
        "# DWDDRandomizer Settings Export",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # [app_data]
    lines.append("[app_data]")
    for k, v in data.get("app_data", {}).items():
        lines.append(f'{AppState._toml_key(k)} = {AppState._toml_value(v)}')
    lines.append("")

    # [randomizer_options] with comments
    lines.append("[randomizer_options]")
    for k, v in data.get("randomizer_options", {}).items():
        desc = EXPORT_SETTINGS_DESCRIPTIONS.get(k)
        if desc:
            lines.append(f'# {desc}')
        lines.append(f'{AppState._toml_key(k)} = {AppState._toml_value(v)}')
        lines.append('')

    # [advanced_settings] - reuse AppState's formatter logic
    advanced = data.get("advanced_settings", {})
    if advanced:
        lines.append("[advanced_settings]")
        simple_keys = [k for k in advanced if not isinstance(advanced[k], dict)]
        dict_keys = [k for k in advanced if isinstance(advanced[k], dict)]

        for k in simple_keys:
            v = advanced[k]
            desc = AppState.ADVANCED_SETTINGS_DESCRIPTIONS.get(k)
            if desc:
                lines.append(f'# {desc}')
            lines.append(f'{AppState._toml_key(k)} = {AppState._toml_value(v)}')
            lines.append('')

        for k in dict_keys:
            v = advanced[k]
            desc = AppState.ADVANCED_SETTINGS_DESCRIPTIONS.get(k)
            if desc:
                lines.append(f'# {desc}')
            lines.append(f'[advanced_settings.{AppState._toml_key(k)}]')
            for sk, sv in v.items():
                lines.append(f'{AppState._toml_key(sk)} = {AppState._toml_value(sv)}')
            lines.append('')

    return '\n'.join(lines) + '\n'


def import_settings():
    # Mapping from config keys to tkinter variables
    # BooleanVar mappings
    bool_var_mapping = {
        "INCREASE_TEXT_SPEED": change_text_speed_var,
        "INCREASE_MOVEMENT_SPEED": change_movement_speed_var,
        "EXPAND_PLAYER_NAME_LENGTH": expand_player_name_var,
        "IMPROVE_BATTLE_PERFORMANCE": improve_battle_performance_var,
        "REDUCE_WILD_ENCOUNTER_RATE": change_wild_encounter_rate_var,
        "INCREASE_SCAN_RATE": increase_flat_scan_rate_var,
        "INCREASE_WILD_ENCOUNTER_MONEY": buff_wild_encounter_money_var,
        "INCREASE_FARM_EXP": change_farm_exp_var,
        "BALANCE_CALUMON_STATS": balance_calumon_var,
        "ENABLE_LEGENDARY_TAMER_QUEST": quests_enable_legendary_tamer_var,
        "UNLOCK_MAIN_QUESTS_IN_SEQUENCE": quests_unlock_main_in_sequence_var,
        "UNLOCK_VERSION_EXCLUSIVE_AREAS": unlock_version_exclusive_areas_var,
        "NERF_FIRST_BOSS": nerf_first_boss_var,
        "FORCE_STARTER_W_ROOKIE_STAGE": force_starter_w_rookie_var,
        "SPECIES_ALLOW_UNKNOWN": species_allow_unknown_var,
        "KEEP_SPECIES_RESISTANCE_COHERENCE": elemental_res_keep_coherence_var,
        "BASESTATS_STATTYPE_BIAS": base_stats_bias_type_var,
        "MOVESETS_LEVEL_BIAS": movesets_level_bias_var,
        "REGULAR_MOVE_POWER_BIAS": movesets_power_bias_var,
        "SIGNATURE_MOVE_POWER_BIAS": movesets_signature_power_bias_var,
        "MOVESETS_SIGNATURE_MOVES_POOL": movesets_signature_moves_var,
        "MOVESETS_GUARANTEE_BASIC_MOVE": movesets_guarantee_basic_move_var,
        "TRAITS_FORCE_FOUR": traits_force_four_var,
        "TRAITS_ENABLE_UNUSED": traits_enable_unused_var,
        "DIGIVOLUTIONS_SIMILAR_SPECIES": digivolution_similar_species_var,
        "DIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": digivolution_conditions_species_exp_var,
        "DNADIGIVOLUTION_CONDITIONS_FOLLOW_SPECIES_EXP": dna_digivolution_conditions_species_exp_var,
    }

    # IntVar mappings (for radio button options)
    int_var_mapping = {
        "RANDOMIZE_STARTERS": starters_option_var,
        "ROOKIE_RESET_EVENT": rookie_reset_option_var,
        "RANDOMIZE_OVERWORLD_ITEMS": overworld_items_option_var,
        "RANDOMIZE_QUEST_ITEM_REWARDS": quest_rewards_option_var,
        "RANDOMIZE_WILD_DIGIMON_ENCOUNTERS": wild_digimon_option_var,
        "RANDOMIZE_WILD_ENCOUNTER_ITEMS": wild_encounter_items_option_var,
        "WILD_ENCOUNTERS_STATS": stat_gen_option_var,
        "RANDOMIZE_FIXED_BATTLES": enemy_digimon_option_var,
        "RANDOMIZE_DIGIMON_SPECIES": species_option_var,
        "RANDOMIZE_ELEMENTAL_RESISTANCES": elemental_res_option_var,
        "RANDOMIZE_BASE_STATS": base_stats_option_var,
        "RANDOMIZE_DIGIMON_STATTYPE": digimon_type_option_var,
        "RANDOMIZE_MOVESETS": movesets_option_var,
        "RANDOMIZE_TRAITS": traits_option_var,
        "RANDOMIZE_DIGIVOLUTIONS": digivolutions_option_var,
        "RANDOMIZE_DIGIVOLUTION_CONDITIONS": digivolution_conditions_option_var,
        "RANDOMIZE_DNADIGIVOLUTIONS": dna_digivolutions_option_var,
        "RANDOMIZE_DNADIGIVOLUTION_CONDITIONS": dna_digivolution_conditions_option_var,
    }

    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    configs_dir = os.path.join(app_dir, "configs")

    toml_path = filedialog.askopenfilename(
        title="Import Settings",
        defaultextension=".toml",
        filetypes=[("TOML Files", "*.toml"), ("All Files", "*.*")],
        initialdir=configs_dir
    )

    if toml_path:
        try:
            warning_str = ""

            with open(toml_path, 'r') as f:
                toml_data = toml.load(f)

            app_data = toml_data.get("app_data", None)
            if app_data:
                app_version = app_data.get("APP_VERSION", None)
                rom_version = app_data.get("ROM_VERSION", None)
                seed = app_data.get("SEED", None)
                if(app_version and app_version != APP_VERSION):
                    warning_str += f"\nWarning: current app version {APP_VERSION} does not match config file's expected app version {app_version}."
                if(rom_version and rom_version != app_state.current_rom.version):
                    warning_str += f"\nWarning: loaded rom ({app_state.current_rom.version}) does not match config file's expected rom ({rom_version}). Settings such as custom starters may have inadvertently been altered."
                if(seed):
                    app_state.seed = seed

            randomizer_options = toml_data.get("randomizer_options", None)

            if randomizer_options:
                for key, value in randomizer_options.items():
                    if key in bool_var_mapping:
                        bool_var_mapping[key].set(value)
                    elif key in int_var_mapping:
                        int_var_mapping[key].set(value)
                    elif key == "INCREASE_DIGIMON_EXP":
                        exp_wild_digimon_var.set(value > 0)
            else:
                warning_str += f"\nWarning: [randomizer_options] not found in config file. Randomizer settings may not have been loaded properly."

            # load starters
            custom_starters_data = randomizer_options.get("CUSTOM_STARTER_PACKS", None)
            if custom_starters_data:
                for pack_idx, pack in enumerate(custom_starters_data):
                    if pack_idx >= len(app_state.custom_starters_packs):
                        continue        
                    for starter_idx, digimon_name in enumerate(pack):
                        if starter_idx >= len(app_state.custom_starters_packs[pack_idx]):
                            continue
                        combo = app_state.custom_starters_packs[pack_idx][starter_idx]
                        combo.set(digimon_name)

            messagebox.showinfo("Success", f"Settings imported from:\n{toml_path}\n{warning_str}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings:\n{str(e)}")


def set_random_seed():

    set_random_seed_window = tk.Toplevel(root)
    set_random_seed_window.title("Set Random Seed")
    #set_random_seed_window.geometry("600x360")
    set_random_seed_window.resizable(False, False)


    # Get the main window's position
    main_x = root.winfo_rootx()
    main_y = root.winfo_rooty()

    # Offset the pop-up slightly (e.g., center it over the main window)
    offset_x = 250
    offset_y = 150
    set_random_seed_window.geometry(f"+{main_x + offset_x}+{main_y + offset_y}")

    frame = tk.Frame(set_random_seed_window)
    frame.pack(padx=20, pady=20)

    random_seed_label = tk.Label(frame, text="Random Seed:")
    random_seed_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

    cur_seed_val = str(app_state.seed) if app_state.seed != -1 else "N/A"

    description_label = tk.Label(
        set_random_seed_window,
        text="Current seed value: " + cur_seed_val,
        wraplength=320
    )
    description_label.pack()


    def validate_seed_input(P):
        if P == "" or P.isdigit():  
            return True
        else:
            return False

    validate_seed = set_random_seed_window.register(validate_seed_input)
    random_seed_entry = tk.Entry(frame, validate="key", validatecommand=(validate_seed, "%P"))
    random_seed_entry.grid(row=0, column=1, padx=10, pady=5)

    def submit_seed():
        try:
            random_seed_val = random_seed_entry.get().strip()
            if random_seed_val and random_seed_val.isdigit():
                random_seed_val_int = int(random_seed_val)
                if(random_seed_val_int > 2**32 - 1):
                    messagebox.showinfo("Random Seed Set", f"Random seed not set (seed value must not exceed 4294967295).")
                    set_random_seed_window.destroy()
                else:
                    app_state.seed = random_seed_val_int
                    messagebox.showinfo("Random Seed Set", f"Seed set to: {random_seed_val}")
                set_random_seed_window.destroy()
            elif(len(random_seed_val) == 0):
                messagebox.showinfo("Random Seed Set", f"Random seed not set (empty input field).")
                app_state.seed = -1
                set_random_seed_window.destroy()
            else:
                messagebox.showerror("Error", f"Invalid seed input. Please enter a valid number or leave the field empty (no set seed).")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid seed input. Please enter a valid number.")

            
    submit_button = tk.Button(set_random_seed_window, text="Submit", command=submit_seed)
    submit_button.pack(pady=20)





def show_about_popup():
    # Create the pop-up window
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("")
    about_window.resizable(False, False)
    about_window.minsize(360, 300)
    #about_window.iconbitmap(icon_path)
    about_window.iconphoto(False, tk.PhotoImage(file=icon_png_path))

    # Get the main window's position
    main_x = root.winfo_rootx()
    main_y = root.winfo_rooty()

    # Offset the pop-up slightly (e.g., center it over the main window)
    offset_x = 150
    offset_y = 120
    about_window.geometry(f"+{main_x + offset_x}+{main_y + offset_y}")

    title_label = tk.Label(
        about_window,
        text="Digimon World Dawn/Dusk Randomizer",
        font=("Segoe UI", 12, "bold"),
        justify="center",
        anchor="center"
    )
    title_label.pack(pady=(10, 0))

    version_label = tk.Label(
        about_window,
        text=f"Version {APP_VERSION}",
        justify="center",
        anchor="center"
    )
    version_label.pack()

    tk.Label(about_window, text="").pack(pady=1)  # empty label for spacing

    description_label = tk.Label(
        about_window,
        text="ROM patcher for Digimon World Dawn/Dusk that provides quality-of-life patches and randomization settings.",
        wraplength=320, 
        justify="center",
        anchor="center"
    )
    description_label.pack()

    tk.Label(about_window, text="").pack(pady=1)  # empty label for spacing

    copyright_label = tk.Label(
        about_window,
        text="Copyright © 2024-2025 João Santos\nLicensed under the GPL-3.0 license",
        justify="center",
        anchor="center"
    )
    copyright_label.pack()

    tk.Label(about_window, text="").pack(pady=1) 

    attribution_label = tk.Label(
        about_window,
        text="All rights to the original Digimon World Dawn/Dusk belong to Bandai Namco Entertainment.",
        wraplength=320, 
        justify="center",
        anchor="center"
    )
    attribution_label.pack(pady=(0, 10))

    links_frame = tk.Frame(about_window)
    links_frame.pack(pady=10)

    github_label = tk.Label(
        links_frame,
        text="GitHub",
        fg="blue",
        cursor="hand2",
        #font=("Helvetica", 10, "underline")
    )
    github_label.grid(row=0, column=0, padx=5)
    github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/joaomlsantos/DWDDRandomizer"))

    wiki_label = tk.Label(
        links_frame,
        text="Wiki",
        fg="blue",
        cursor="hand2",
        #font=("Helvetica", 10, "underline")
    )
    wiki_label.grid(row=0, column=1, padx=5)
    wiki_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/joaomlsantos/DWDDRandomizer/wiki"))
    
    donate_label = tk.Label(
        links_frame,
        text="Ko-Fi",
        fg="blue",
        cursor="hand2",
        #font=("Helvetica", 10, "underline")
    )
    donate_label.grid(row=0, column=2, padx=5)
    donate_label.bind("<Button-1>", lambda e: webbrowser.open("https://ko-fi.com/joaomlsantos"))



def toggle_stat_generation():
    if wild_digimon_option_var.get() != RandomizeWildEncounters.UNCHANGED.value:
        for rb in stat_gen_radio_buttons:
            rb.configure(state="normal")
    else:
        for rb in stat_gen_radio_buttons:
            rb.configure(state="disabled")



#def toggle_enemy_stat_generation():
#    if enemy_digimon_option_var.get() != RandomizeEnemyDigimonEncounters.UNCHANGED.value:
#        for rb in enemy_stat_gen_radio_buttons:
#            rb.configure(state="normal")
#    else:
#        for rb in enemy_stat_gen_radio_buttons:
#            rb.configure(state="disabled")



def toggle_digivolution_randomization_options():
    if digivolutions_option_var.get() != RandomizeDigivolutions.UNCHANGED.value:
        digivolutionSimilarSpeciesCheckbox.configure(state="normal")
    else:
        digivolutionSimilarSpeciesCheckbox.configure(state="disabled")

'''
def toggle_dna_digivolution_rand_options():
    if dna_digivolutions_option_var.get() != RandomizeDnaDigivolutions.UNCHANGED.value:
        dnaDigivolutionForceRareCheckbox.configure(state="normal")
    else:
        dnaDigivolutionForceRareCheckbox.configure(state="disabled")
'''


# Initialize main window
root = tk.Tk()
root.title("Digimon World Dawn/Dusk Randomizer")
root.geometry("")
#root.minsize(800, 600) 
root.minsize(800, 705) 
#root.iconbitmap(icon_path)
root.iconphoto(False, tk.PhotoImage(file=icon_png_path))


# Create a frame for the ROM Loading section
rom_frame = ttk.Frame(root, padding=10)
rom_frame.pack(side="top", fill="x", pady=10)

# Left section: Buttons
button_frame = ttk.Frame(rom_frame)
button_frame.pack(side="left", fill="y", padx=10)

open_rom_button = ttk.Button(button_frame, text="Open ROM", command=open_rom)
open_rom_button.pack(fill="x", pady=5, ipadx=30)

save_changes_button = ttk.Button(button_frame, text="Save Patched ROM", command=save_changes, state="disabled")
save_changes_button.pack(fill="x", pady=5)

about_button = ttk.Button(button_frame, text="About", command=show_about_popup)
about_button.pack(fill="x", pady=5)

# Right section: ROM Information
rom_info_frame = ttk.LabelFrame(rom_frame, text="ROM Information", padding=10)
rom_info_frame.pack(side="left", fill="both", expand=True, padx=10)

# Add some labels to display ROM info (placeholders for now)
rom_name_label = ttk.Label(rom_info_frame, text="ROM Name: Not Loaded", width=64, anchor="w")
rom_name_label.pack(anchor="w", pady=2)

#rom_size_label = ttk.Label(rom_info_frame, text="ROM Size: N/A")
#rom_size_label.pack(anchor="w", pady=2)

rom_version_label = ttk.Label(rom_info_frame, text="ROM Version: N/A")
rom_version_label.pack(anchor="w", pady=2)

#rom_path_label = ttk.Label(rom_info_frame, text="ROM Path: N/A")
#rom_path_label.pack(anchor="w", pady=2)

rom_status_label = ttk.Label(rom_info_frame, text="Status: Not Loaded")
rom_status_label.pack(anchor="w", pady=2)


# Last section: Import/Export Settings
settings_buttons_frame = ttk.Frame(rom_frame)
settings_buttons_frame.pack(side="right", fill="both", padx=10)

import_settings_button = ttk.Button(settings_buttons_frame, text="Import Settings", command=import_settings, state="disabled")
import_settings_button.pack(fill="x", pady=5, ipadx=30)

export_settings_button = ttk.Button(settings_buttons_frame, text="Export Settings", command=export_settings, state="disabled")
export_settings_button.pack(fill="x", pady=5)

premade_seed_button = ttk.Button(settings_buttons_frame, text="Set Random Seed", command=set_random_seed)
premade_seed_button.pack(fill="x", pady=5)


# Create a Notebook widget to hold the tabs
notebook = ttk.Notebook(root, padding=10)
notebook.pack(fill="both", expand=True)

# QoL Changes Tab
#qol_frame = ttk.Frame(notebook, padding=10)
qol_frame = ttk.Frame(notebook, padding=10)
qol_frame.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(qol_frame, text="QoL Patches")



# Performance Improvements frame
performance_frame = ttk.LabelFrame(qol_frame, text="Performance Improvements", padding=10)
performance_frame.pack(side="top", fill="x", padx=10, pady=5)


performance_checkbox_frame = ttk.Frame(performance_frame)
performance_checkbox_frame.pack(side="left", fill="both", expand=True, padx=10)

# QoL Checkbuttons
change_text_speed_var = tk.BooleanVar(value=True)
textSpeedCheckbox = tk.Checkbutton(performance_checkbox_frame, text="Increase Text Speed", variable=change_text_speed_var, state="disabled")
textSpeedCheckbox.pack(anchor='w')
textSpeedTooltip = CreateToolTip(textSpeedCheckbox, "Increases the speed at which the text is displayed, removing the need to hold A to speed up the dialogues.")

change_movement_speed_var = tk.BooleanVar(value=True)
increaseMovementSpeedCheckbox = tk.Checkbutton(performance_checkbox_frame, text="Increase Movement Speed", variable=change_movement_speed_var, state="disabled")
increaseMovementSpeedCheckbox.pack(anchor='w')
increaseMovementSpeedTooltip = CreateToolTip(increaseMovementSpeedCheckbox, "Increases the player's movement speed to 1.5x of the default speed.")

expand_player_name_var = tk.BooleanVar(value=True)
expandPlayerNameCheckbox = tk.Checkbutton(performance_checkbox_frame, text="Expand Player Name Length", variable=expand_player_name_var, state="disabled")
expandPlayerNameCheckbox.pack(anchor="w")
expandPlayerNameTooltip = CreateToolTip(expandPlayerNameCheckbox, "Expands the maximum length of the player's name from 5 to 7 characters.")

improve_battle_performance_var = tk.BooleanVar(value=True)
improveBattlePerformanceCheckbox = tk.Checkbutton(performance_checkbox_frame, text="Improve Battle Performance", variable=improve_battle_performance_var, state="disabled")
improveBattlePerformanceCheckbox.pack(anchor="w")
improveBattlePerformanceTooltip = CreateToolTip(improveBattlePerformanceCheckbox, "Reduces imposed frame delay in several battle animations, making battles significantly faster.")




# Wild Encounters, Money & EXP frame
wild_exp_money_frame = ttk.LabelFrame(qol_frame, text="Wild Encounters, Money & EXP", padding=10)
wild_exp_money_frame.pack(side="top", fill="x", padx=10, pady=5)

wild_exp_money_checkbox_frame = ttk.Frame(wild_exp_money_frame)
wild_exp_money_checkbox_frame.pack(side="left", fill="both", expand=True, padx=10)


change_wild_encounter_rate_var = tk.BooleanVar(value=False)
decreaseWildEncounterCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Reduce Wild Encounter Rate", variable=change_wild_encounter_rate_var, state="disabled")
decreaseWildEncounterCheckbox.pack(anchor='w')
decreaseWildEncounterTooltip = CreateToolTip(decreaseWildEncounterCheckbox, "Reduces the wild encounter rate in all areas by 0.5x.")

#encounter_slider_widget = LabelledSlider(qol_frame)
#encounter_slider_widget.pack(anchor="w", padx=10)

#increase_exp_yield_var = tk.BooleanVar(value=True)
#increaseExpYieldCheckbox = tk.Checkbutton(qol_frame, text="Increase Exp Yield for Wild Digimon", variable=increase_exp_yield_var, state="disabled")
#increaseExpYieldCheckbox.pack(anchor='w')
#increaseExpYieldTootip = CreateToolTip(increaseExpYieldCheckbox, "Changes the exp given by all wild digimon to match game progression.\nThe exp yield values are roughly calculated through pokémon's standard formula for experience yield: base_exp * encounter_lvl / 7, where base_exp is a fixed value depending on the digimon's digivolution stage, and encounter_lvl is the level of the encounter.")

increase_flat_scan_rate_var = tk.BooleanVar(value=False)
increaseFlatScanRateCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Increase Scan Rate", variable=increase_flat_scan_rate_var, state="disabled")
increaseFlatScanRateCheckbox.pack(anchor='w')
increaseFlatScanRateTooltip = CreateToolTip(increaseFlatScanRateCheckbox, "Increases the base scan rate by 10%.")

#increase_stat_caps_var = tk.BooleanVar(value=False)
#increaseStatCapsCheckbox = tk.Checkbutton(qol_frame, text="Increase Stat Caps", variable=increase_stat_caps_var, state="disabled")
#increaseStatCapsCheckbox.pack(anchor='w')
#increaseStatCapsTooltip = CreateToolTip(increaseStatCapsCheckbox, "Increases the stat cap to 65535 for all stats.\nOriginally the HP and MP are limited to 9999, and the other stats are limited to 999.")

exp_wild_digimon_var = tk.BooleanVar(value=False)
increaseExpWildDigimonCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Increase Wild Digimon EXP", variable=exp_wild_digimon_var, state="disabled")
increaseExpWildDigimonCheckbox.pack(anchor='w')
increaseExpWildDigimonTooltip = CreateToolTip(increaseExpWildDigimonCheckbox, "Increases earned experience from defeating wild digimon.\nExp is calculated using Pokémon's exp.share formula: base_exp * level / 14, where base_exp depends on evolution stage and level is the encounter level.\nFor reference, a lvl 33 wild Greymon's exp yield increases from 71 to 283 points.")


buff_wild_encounter_money_var = tk.BooleanVar(value=False)
buffWildEncounterMoneyCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Increase Wild Encounter Money", variable=buff_wild_encounter_money_var, state="disabled")
buffWildEncounterMoneyCheckbox.pack(anchor='w')
buffWildEncounterMoneyTooltip = CreateToolTip(buffWildEncounterMoneyCheckbox, "Increase earned money from defeating wild digimon (by 4x).")



# Farm EXP; might do a custom frame for all exp-related stuff

change_farm_exp_var = tk.BooleanVar(value=False)
increaseFarmExpCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Increase Farm EXP", variable=change_farm_exp_var, state="disabled")
increaseFarmExpCheckbox.pack(anchor='w')
increaseFarmExpTooltip = CreateToolTip(increaseFarmExpCheckbox, "Increases the base farm exp by 10x for all terrains.")


# Balance Calumon

balance_calumon_var = tk.BooleanVar(value=True)
balanceCalumonCheckbox = tk.Checkbutton(wild_exp_money_checkbox_frame, text="Balance Calumon Stats", variable=balance_calumon_var, state="disabled")
balanceCalumonCheckbox.pack(anchor='w')
balanceCalumonTooltip = CreateToolTip(balanceCalumonCheckbox, "Reduces Calumon's stats to those of a regular in-training digimon.\nOriginally, while Calumon is an In-Training digimon, its stats are equivalent to the stats of a Mega.\nReducing Calumon's stats avoids situations where a player would struggle to defeat (or run from) Calumon encounters, or situations where a player would suddenly have an overpowered digimon at an early stage of the game.\nThis setting also removes Calumon's additional traits besides D-Entelechy, and sets its signature move to Frothy Spit.")




# Quests & Version Exclusives frame
quests_versions_frame = ttk.LabelFrame(qol_frame, text="Quests & Version Exclusives", padding=10)
quests_versions_frame.pack(side="top", fill="x", padx=10, pady=5)

quests_versions_checkbox_frame = ttk.Frame(quests_versions_frame)
quests_versions_checkbox_frame.pack(side="left", fill="both", expand=True, padx=10)

quests_enable_legendary_tamer_var = tk.BooleanVar(value=True)
questsEnableLegendaryTamerCheckbox = tk.Checkbutton(quests_versions_checkbox_frame, text="Enable Legendary Tamer Quest", variable=quests_enable_legendary_tamer_var, state="disabled")
questsEnableLegendaryTamerCheckbox.pack(anchor='w')
questsEnableLegendaryTamerTooltip = CreateToolTip(questsEnableLegendaryTamerCheckbox, "Enables the quest \"The Legendary Tamer\" after obtaining Platinum rank and completing the quest \"Gaia Origin Challenge\", disabling the requirement of playing online once.")



quests_unlock_main_in_sequence_var = tk.BooleanVar(value=False)
questsUnlockMainQuestsInSequenceCheckbox = tk.Checkbutton(quests_versions_checkbox_frame, text="Unlock Main Quests in Sequence", variable=quests_unlock_main_in_sequence_var, state="disabled")
questsUnlockMainQuestsInSequenceCheckbox.pack(anchor='w')
questsUnlockMainQuestsInSequenceTooltip = CreateToolTip(questsUnlockMainQuestsInSequenceCheckbox, "Unlocks each main quest immediately after completing the previous main quest, eliminating the requirement of clearing side quests to unlock the next main quest.")



# unlock version-exclusive areas

unlock_version_exclusive_areas_var = tk.BooleanVar(value=False)
unlockVersionExclusiveAreasCheckbox = tk.Checkbutton(quests_versions_checkbox_frame, text="Unlock Version-Exclusive Areas", variable=unlock_version_exclusive_areas_var, state="disabled")
unlockVersionExclusiveAreasCheckbox.pack(anchor='w')
unlockVersionExclusiveAreasTooltip = CreateToolTip(unlockVersionExclusiveAreasCheckbox, "Unlocks areas that were previously exclusive to a single version of the game.\nFor DAWN, this option unlocks Magnet Mine at the same time that Task Canyon is unlocked, and unlocks Process Factory at the same time that Pallette Amazon is unlocked.\nFor DUSK, this option unlocks Task Canyon at the same time that Magnet Mine is unlocked.")




# Exp Yield frame
#exp_yield_frame = ttk.LabelFrame(qol_frame, text="Wild Digimon Exp.", padding=10)
#exp_yield_frame.pack(side="top", anchor="w", padx=10, pady=10)





#exp_yield_option_var = tk.IntVar(value=ExpYieldConfig.INCREASE_HALVED.value)
#
#exp_yield_unchanged_rb = tk.Radiobutton(exp_yield_frame, text="Unchanged", variable=exp_yield_option_var, value=ExpYieldConfig.UNCHANGED.value, state="disabled")
#exp_yield_unchanged_rb.pack(anchor="w")
#
#exp_yield_halved_rb = tk.Radiobutton(exp_yield_frame, text="Increase (halved)", variable=exp_yield_option_var, value=ExpYieldConfig.INCREASE_HALVED.value, state="disabled")
#exp_yield_halved_tooltip = CreateToolTip(exp_yield_halved_rb, "Adjusts wild Digimon exp to match progression with half increase.\nExp is calculated using Pokémon's exp.share formula: base_exp * level / 14, where base_exp depends on evolution stage and level is the encounter level.\nFor reference, a lvl 33 wild Greymon's exp yield increases from 71 to 283 points.")
#exp_yield_halved_rb.pack(anchor="w")
#
#exp_yield_full_rb = tk.Radiobutton(exp_yield_frame, text="Increase (full)", variable=exp_yield_option_var, value=ExpYieldConfig.INCREASE_FULL.value, state="disabled")
#exp_yield_full_tooltip = CreateToolTip(exp_yield_full_rb, "Adjusts wild Digimon exp to match progression with full increase.\nExp is calculated using Pokémon's formula: base_exp * level / 7, where base_exp depends on evolution stage and level is the encounter level.\nFor reference, a lvl 33 wild Greymon's exp yield increases from 71 to 566 points.")
#exp_yield_full_rb.pack(anchor="w")


'''
# QoL Slider for Movement Speed Multiplier
tk.Label(qol_frame, text="Movement Speed Multiplier:").pack(anchor='w')
movement_speed_multiplier = tk.DoubleVar(value=1.5)
tk.Scale(qol_frame, from_=0.5, to=3.0, orient="horizontal", resolution=0.5,
         variable=movement_speed_multiplier).pack(fill="x")
'''
         


# Starters, Items & Quests Tab
starters_items_quests_tab = ttk.Frame(notebook, padding=10)
starters_items_quests_tab.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(starters_items_quests_tab, text="Starters, Items & Quests")


# Starters frame
starters_frame = ttk.LabelFrame(starters_items_quests_tab, text="Starter Packs", padding=10)
starters_frame.pack(side="top", fill="x", padx=10, pady=5)

# Top row container for the three side-by-side frames
starters_top_row = ttk.Frame(starters_frame)
starters_top_row.pack(side="top", fill="x")

starters_radio_frame = ttk.Frame(starters_top_row)
starters_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

starters_option_var = tk.IntVar(value=RandomizeStartersConfig.UNCHANGED.value)

starters_unchanged_rb = tk.Radiobutton(starters_radio_frame, text="Unchanged", variable=starters_option_var, value=RandomizeStartersConfig.UNCHANGED.value, state="disabled")
starters_unchanged_rb.pack(anchor="w")

starters_same_stage_rb = tk.Radiobutton(starters_radio_frame, text="Random (same digivolution stages)", variable=starters_option_var, value=RandomizeStartersConfig.RAND_SAME_STAGE.value, state="disabled")
starters_same_stage_rb_tooltip = CreateToolTip(starters_same_stage_rb, "Randomizes each starter digimon pack, keeping the original digivolution stages for each digimon.")
starters_same_stage_rb.pack(anchor="w")

starters_completely_random_rb = tk.Radiobutton(starters_radio_frame, text="Random (completely)", variable=starters_option_var, value=RandomizeStartersConfig.RAND_FULL.value, state="disabled")
starters_completely_random_tooltip = CreateToolTip(starters_completely_random_rb, "Randomizes each starter digimon pack completely.")
starters_completely_random_rb.pack(anchor="w")

starters_custom_rb = tk.Radiobutton(starters_radio_frame, text="Custom", variable=starters_option_var, value=RandomizeStartersConfig.CUSTOM.value, state="disabled")
starters_custom_tooltip = CreateToolTip(starters_custom_rb, "Enables customization of each digimon starter pack.")
starters_custom_rb.pack(anchor="w")


starters_misc_frame = ttk.Frame(starters_top_row)
starters_misc_frame.pack(side="left", fill="both", expand=True, padx=10)

nerf_first_boss_var = tk.BooleanVar(value=False)
nerfFirstBossCheckbox = tk.Checkbutton(starters_misc_frame, text="Nerf First Boss", variable=nerf_first_boss_var, state="disabled")
nerfFirstBossCheckbox.pack(anchor='w')
nerfFirstBossTootip = CreateToolTip(nerfFirstBossCheckbox, "Enabling this option reduces the total HP of the first boss (virus that attacks the city) by half.\nThis fight usually relies on the lvl 20 Coronamon / Lunamon to be cleared. \nThis option is recommended if randomizing the starter packs, as any other digimon will be set to rookies at lvl 1 (even the digimon that are already rookies).")

force_starter_w_rookie_var = tk.BooleanVar(value=False)
forceStarterWRookieCheckbox = tk.Checkbutton(starters_misc_frame, text="Force Starter w/ Rookie Stage", variable=force_starter_w_rookie_var, state="disabled")
forceStarterWRookieCheckbox.pack(anchor='w')
forceStarterWRookieTootip = CreateToolTip(forceStarterWRookieCheckbox, "Guarantees that the randomized starters can degenerate to rookie stage: after the rookie reset, this option ensures that your party will be composed of three rookie (or lower, if the starter was originally an in-training) digimon.")



# Right side: Rookie Reset Event

rookie_reset_frame = ttk.LabelFrame(starters_top_row, text="Rookie Reset Event", padding=10)
rookie_reset_frame.pack(side="right", fill="y", padx=10, pady=5)

rookie_reset_option_var = tk.IntVar(value=RookieResetConfig.UNCHANGED.value)    # Default to UNCHANGED

rookie_reset_unchanged_rb = tk.Radiobutton(rookie_reset_frame, text="Unchanged", variable=rookie_reset_option_var, value=RookieResetConfig.UNCHANGED.value, state="disabled")
rookie_reset_unchanged_rb_tooltip = CreateToolTip(rookie_reset_unchanged_rb, "Resets each starter digimon to level 1, and reverts its digivolution stage to a rookie.\nExample: a starter lvl 35 SkullGreymon will be a lvl 1 BlackAgumon after the rookie reset event (if digivolution lines are not randomized).")
rookie_reset_unchanged_rb.pack(anchor="w")

rookie_reset_same_stage_rb = tk.Radiobutton(rookie_reset_frame, text="Keep Digivolution Stages", variable=rookie_reset_option_var, value=RookieResetConfig.RESET_KEEPING_EVO.value, state="disabled")
rookie_reset_same_stage_rb_tooltip = CreateToolTip(rookie_reset_same_stage_rb, "Resets each starter digimon to level 1, but keeps its current digivolution stage instead of reverting the digimon to a rookie.\nExample: a starter lvl 35 SkullGreymon will be a lvl 1 SkullGreymon after the rookie reset event.")
rookie_reset_same_stage_rb.pack(anchor="w")


rookie_reset_cancel_rb = tk.Radiobutton(rookie_reset_frame, text="Disable Rookie Reset Event", variable=rookie_reset_option_var, value=RookieResetConfig.DO_NOT_RESET.value, state="disabled")
rookie_reset_cancel_rb_tooltip = CreateToolTip(rookie_reset_cancel_rb, "Disables the rookie reset event entirely: starter digimon keep their current level and digivolution stage.\nExample: a starter lvl 35 SkullGreymon will be a lvl 35 SkullGreymon after the rookie reset event.")
rookie_reset_cancel_rb.pack(anchor="w")

'''

starters_same_stage_rb = tk.Radiobutton(starters_radio_frame, text="Random (same digivolution stages)", variable=starters_option_var, value=RandomizeStartersConfig.RAND_SAME_STAGE.value, state="disabled")
starters_same_stage_rb_tooltip = CreateToolTip(starters_same_stage_rb, "Randomizes each starter digimon pack, keeping the original digivolution stages for each digimon.")
starters_same_stage_rb.pack(anchor="w")

starters_completely_random_rb = tk.Radiobutton(starters_radio_frame, text="Random (completely)", variable=starters_option_var, value=RandomizeStartersConfig.RAND_FULL.value, state="disabled")
starters_completely_random_tooltip = CreateToolTip(starters_completely_random_rb, "Randomizes each starter digimon pack completely.")
starters_completely_random_rb.pack(anchor="w")

'''



# Custom Starters

custom_starters_frame = ttk.LabelFrame(starters_frame, text="Customize Starter Packs", padding=10)
custom_starters_frame.pack(side="top", fill="x", padx=10, pady=5)

for pack_idx in range(4):
    pack_frame = ttk.Frame(custom_starters_frame)
    pack_frame.grid(row=pack_idx, column=0, columnspan=12, pady=5, padx=5, sticky="ew")
    
    pack_number_label = ttk.Label(pack_frame, text=f"{str(pack_idx + 1)}.")
    pack_number_label.grid(row=0, column=0, padx=(0, 8), sticky="w")
    
    pack_digimon_combos = []
    for starter_idx in range(3):
        col_offset = starter_idx * 4

        digimon_var = tk.StringVar()
        digimon_combo = ttk.Combobox(
            pack_frame,
            textvariable=digimon_var,
            values=utils.get_digimon_names(),
            state="disabled",
            width=25
        )
        digimon_combo.grid(row=0, column=col_offset, padx=(25, 2), pady=2, sticky="w")
        pack_digimon_combos.append(digimon_combo)

    app_state.custom_starters_packs.append(pack_digimon_combos)

def update_custom_starters_state(*_):
    is_custom = starters_option_var.get() == RandomizeStartersConfig.CUSTOM.value
    new_state = "readonly" if is_custom else "disabled"

    for pack in app_state.custom_starters_packs:
        for combo in pack:
            combo.config(state=new_state)

def get_custom_starters_data() -> List[List[str]]:
    packs = []
    for pack in app_state.custom_starters_packs:
        packs.append([combo.get() for combo in pack])
    return packs

starters_option_var.trace_add("write", update_custom_starters_state)
update_custom_starters_state()

    


items_quests_container = ttk.Frame(starters_items_quests_tab)
items_quests_container.pack(side="top", fill="x", padx=10, pady=5)


# Overworld Items Frame
overworld_items_frame = ttk.LabelFrame(items_quests_container, text="Overworld Items", padding=10)
#overworld_items_frame.pack(side="top", fill="x", padx=10, pady=5)
overworld_items_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))


overworld_items_radio_frame = ttk.Frame(overworld_items_frame)
overworld_items_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

overworld_items_option_var = tk.IntVar(value=RandomizeItems.UNCHANGED.value)

overworld_items_unchanged_rb = tk.Radiobutton(overworld_items_radio_frame, text="Unchanged", variable=overworld_items_option_var, value=RandomizeItems.UNCHANGED.value, state="disabled")
overworld_items_unchanged_rb.pack(anchor="w")

overworld_items_same_category_rb = tk.Radiobutton(overworld_items_radio_frame, text="Random (same category)", variable=overworld_items_option_var, value=RandomizeItems.RANDOMIZE_KEEP_CATEGORY.value, state="disabled")
overworld_items_same_category_rb_tooltip = CreateToolTip(overworld_items_same_category_rb, "Randomizes each overworld item chest while keeping the original category of the item.\nFor example, a consumable like a GateDisk will be replaced by another consumable, farm items will be replaced by other farm items, etc.\nNOTE: Key items are not included in the randomization pool, and chests that contain key items are not randomized.")
overworld_items_same_category_rb.pack(anchor="w")

overworld_items_completely_random_rb = tk.Radiobutton(overworld_items_radio_frame, text="Random (completely)", variable=overworld_items_option_var, value=RandomizeItems.RANDOMIZE_COMPLETELY.value, state="disabled")
overworld_items_completely_random_tooltip = CreateToolTip(overworld_items_completely_random_rb, "Randomizes each overworld item chest completely (a chest can have any item, regardless of its original item).\nNOTE: Key items are not included in the randomization pool, and chests that contain key items are not randomized.")
overworld_items_completely_random_rb.pack(anchor="w")



# Quests Frame
quests_frame = ttk.LabelFrame(items_quests_container, text="Quest Item Rewards", padding=10)
#quests_frame.pack(side="top", fill="x", padx=10, pady=5)
quests_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

quest_rewards_option_var = tk.IntVar(value=RandomizeItems.UNCHANGED.value)

quest_rewards_unchanged_rb = tk.Radiobutton(quests_frame, text="Unchanged", variable=quest_rewards_option_var, value=RandomizeItems.UNCHANGED.value, state="disabled")
quest_rewards_unchanged_rb.pack(anchor="w")

quest_rewards_same_category_rb = tk.Radiobutton(quests_frame, text="Random (same category)", variable=quest_rewards_option_var, value=RandomizeItems.RANDOMIZE_KEEP_CATEGORY.value, state="disabled")
quest_rewards_same_category_rb_tooltip = CreateToolTip(quest_rewards_same_category_rb, "Randomizes each quest reward while keeping the original category of the item.\nFor example, an equipment item like Water Ring will be replaced by another equipment item, farm items will be replaced by other farm items, etc.\nNOTE: Key items are not included in the randomization pool, and rewards corresponding to key items will not be randomized (e.g. the rewarded Love DigiEgg from the quest \"Explore Limit Valley\").")
quest_rewards_same_category_rb.pack(anchor="w")

quest_rewards_completely_random_rb = tk.Radiobutton(quests_frame, text="Random (completely)", variable=quest_rewards_option_var, value=RandomizeItems.RANDOMIZE_COMPLETELY.value, state="disabled")
quest_rewards_completely_random_tooltip = CreateToolTip(quest_rewards_completely_random_rb, "Randomizes each quest reward completely (each reward can be any item type, regardless of its original item type).\nNOTE: Key items are not included in the randomization pool, and rewards corresponding to key items will not be randomized.")
quest_rewards_completely_random_rb.pack(anchor="w")



#quests_randomize_item_rewards_var = tk.IntVar(value=RandomizeItems.UNCHANGED.value)
#questsRandomizeItemRewardsCheckbox = tk.Checkbutton(quests_sub_frame, text="Randomize Quest Item Rewards", variable=quests_randomize_item_rewards_var, state="disabled")
#questsRandomizeItemRewardsCheckbox.pack(anchor='w')
#questsRandomizeItemRewardsTooltip = CreateToolTip(questsRandomizeItemRewardsCheckbox, "Randomizes the rewarded item for each completed quest.\nThis setting does not randomize the rewarded Love DigiEgg from the quest \"Explore Limit Valley\".")


# Encounters & Tamers Tab
encounters_tamers_tab = ttk.Frame(notebook, padding=10)
encounters_tamers_tab.pack(fill="both", expand=True)
notebook.add(encounters_tamers_tab, text="Wild Encounters & Enemies")



# Wild digimon frame

wild_digimon_frame = ttk.LabelFrame(encounters_tamers_tab, text="Wild Digimon", padding=10)
wild_digimon_frame.pack(side="top", fill="x", padx=10, pady=5)



# Create a container frame inside Wild Digimon for horizontal layout
wild_digimon_inner_container = ttk.Frame(wild_digimon_frame)
wild_digimon_inner_container.pack(side="top", fill="x")

wild_digimon_option_var = tk.IntVar(value=RandomizeWildEncounters.UNCHANGED.value)

# Left side: Wild Digimon randomization radio buttons
wild_digimon_radio_frame = ttk.Frame(wild_digimon_inner_container)
wild_digimon_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

wild_digimon_unchanged_rb = tk.Radiobutton(wild_digimon_radio_frame, text="Unchanged", variable=wild_digimon_option_var, value=RandomizeWildEncounters.UNCHANGED.value, state="disabled", command=toggle_stat_generation)
wild_digimon_unchanged_rb.pack(anchor="w")

wild_digimon_randomize_rb = tk.Radiobutton(wild_digimon_radio_frame, text="Random (same digivolution stages)", variable=wild_digimon_option_var, value=RandomizeWildEncounters.RANDOMIZE_1_TO_1_SAME_STAGE.value, state="disabled", command=toggle_stat_generation)
wild_digimon_randomize_tooltip = CreateToolTip(wild_digimon_randomize_rb, "Replaces each wild digimon by another digimon of the same stage.")
wild_digimon_randomize_rb.pack(anchor="w")

wild_digimon_randomize_completely_rb = tk.Radiobutton(wild_digimon_radio_frame, text="Random (completely)", variable=wild_digimon_option_var, value=RandomizeWildEncounters.RANDOMIZE_1_TO_1_COMPLETELY.value, state="disabled", command=toggle_stat_generation)
wild_digimon_randomize_tooltip = CreateToolTip(wild_digimon_randomize_completely_rb, "Replaces each wild digimon by a random digimon of any stage.")
wild_digimon_randomize_completely_rb.pack(anchor="w")



# Specific options for wild digimon randomization

#wild_digimon_sub_frame = ttk.Frame(wild_digimon_inner_container)
#wild_digimon_sub_frame.pack(side="left", fill="both", expand=True, padx=10)




wild_encounter_rewards_radio_frame = ttk.LabelFrame(wild_digimon_inner_container, text="Encounter Item Drops")
wild_encounter_rewards_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

wild_reward_items_radio_frame = ttk.Frame(wild_encounter_rewards_radio_frame)
wild_reward_items_radio_frame.pack(side="left", fill="both", expand=True, padx=10)
wild_reward_money_radio_frame = ttk.Frame(wild_encounter_rewards_radio_frame)
wild_reward_money_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

wild_encounter_items_option_var = tk.IntVar(value=RandomizeItems.UNCHANGED.value)

wild_encounter_items_unchanged_rb = tk.Radiobutton(wild_reward_items_radio_frame, text="Unchanged", variable=wild_encounter_items_option_var, value=RandomizeItems.UNCHANGED.value, state="disabled")
wild_encounter_items_unchanged_rb.pack(anchor="w")

wild_encounter_items_same_category_rb = tk.Radiobutton(wild_reward_items_radio_frame, text="Random (same category)", variable=wild_encounter_items_option_var, value=RandomizeItems.RANDOMIZE_KEEP_CATEGORY.value, state="disabled")
wild_encounter_items_same_category_rb_tooltip = CreateToolTip(wild_encounter_items_same_category_rb, "Randomizes each wild encounter item drop while keeping the original category of the item.\nFor example, an equipment item like Water Ring will be replaced by another equipment item, farm items will be replaced by other farm items, etc.\nNOTE: Key items are not included in the randomization pool.")
wild_encounter_items_same_category_rb.pack(anchor="w")

wild_encounter_items_completely_random_rb = tk.Radiobutton(wild_reward_items_radio_frame, text="Random (completely)", variable=wild_encounter_items_option_var, value=RandomizeItems.RANDOMIZE_COMPLETELY.value, state="disabled")
wild_encounter_items_completely_random_tooltip = CreateToolTip(wild_encounter_items_completely_random_rb, "Randomizes each wild encounter item drop completely (each drop can be any item type, regardless of its original item type).\nNOTE: Key items are not included in the randomization pool.")
wild_encounter_items_completely_random_rb.pack(anchor="w")







# Right side: Stat Generation frame
stat_gen_frame = ttk.LabelFrame(wild_digimon_inner_container, text="Stat Generation", padding=10)
stat_gen_frame.pack(side="top", fill="y", padx=10, pady=5)

stat_gen_option_var = tk.IntVar(value=LvlUpMode.RANDOM.value)  # Default to "Random"

stat_gen_radio_buttons = []
stat_gen_options = [("Random", LvlUpMode.RANDOM.value), ("Lowest (easier)", LvlUpMode.FIXED_MIN.value), ("Median", LvlUpMode.FIXED_AVG.value), ("Highest (harder)", LvlUpMode.FIXED_MAX.value)]
stat_gen_tooltips = ["A random value from the possible level-up values is picked for each stat upon each level-up operation while generating the wild digimon's stats.\nThis is likely to result in an average stat distribution for the digimon, but is less deterministic than Median.", "The lowest value from the possible level-up values is always picked for each stat upon each level-up operation while generating the wild digimon's stats.\nThis gives the wild digimon a weaker stat constitution, thus granting an easier game experience.", "The median value from the possible level-up values is always picked for each stat upon each level-up operation while generating the wild digimon's stats.\nThis gives the wild digimon a median stat constitution.", "The highest value from the possible level-up values is always picked for each stat upon each level-up operation while generating the wild digimon's stats.\nThis gives the wild digimon a stronger stat constitution, thus granting a harder game experience."]

for text, value in stat_gen_options:
    rb = tk.Radiobutton(
        stat_gen_frame,
        text=text,
        variable=stat_gen_option_var,
        value=value,
        state="disabled"  # Initially disabled
    )
    rb.pack(anchor="w")
    CreateToolTip(rb, stat_gen_tooltips[value])
    stat_gen_radio_buttons.append(rb)

# Initialize the toggle state
toggle_stat_generation()


# Enemy tamers & bosses


enemy_digimon_frame = ttk.LabelFrame(encounters_tamers_tab, text="Enemy Tamers, Quest Digimon & Bosses", padding=10)
enemy_digimon_frame.pack(side="top", fill="x", padx=10, pady=5)

# Create a container frame inside Enemy Tamers & Bosses for horizontal layout
enemy_digimon_inner_container = ttk.Frame(enemy_digimon_frame)
enemy_digimon_inner_container.pack(side="top", fill="x")

enemy_digimon_option_var = tk.IntVar(value=RandomizeEnemyDigimonEncounters.UNCHANGED.value)

# Left side: Enemy Digimon randomization radio buttons
enemy_digimon_radio_frame = ttk.Frame(enemy_digimon_inner_container)
enemy_digimon_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

#enemy_digimon_unchanged_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Unchanged", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.UNCHANGED.value, state="disabled", command=toggle_enemy_stat_generation)
enemy_digimon_unchanged_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Unchanged", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.UNCHANGED.value, state="disabled")
enemy_digimon_unchanged_rb.pack(anchor="w")

#enemy_digimon_randomize_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Random (same digivolution stages)", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_SAME_STAGE.value, state="disabled", command=toggle_enemy_stat_generation)
enemy_digimon_randomize_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Random (same digivolution stages)", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_SAME_STAGE.value, state="disabled")
enemy_digimon_randomize_tooltip = CreateToolTip(enemy_digimon_randomize_rb, "Replaces each fixed enemy digimon by another digimon of the same stage.\nThis setting does not yet randomize non-scannable digimon (e.g. Grimmon, SkullBaluchimon).")
enemy_digimon_randomize_rb.pack(anchor="w")

#enemy_digimon_randomize_completely_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Random (completely)", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_COMPLETELY.value, state="disabled", command=toggle_enemy_stat_generation)
enemy_digimon_randomize_completely_rb = tk.Radiobutton(enemy_digimon_radio_frame, text="Random (completely)", variable=enemy_digimon_option_var, value=RandomizeEnemyDigimonEncounters.RANDOMIZE_1_TO_1_COMPLETELY.value, state="disabled")
enemy_digimon_randomize_tooltip = CreateToolTip(enemy_digimon_randomize_completely_rb, "Replaces each fixed enemy digimon by a random digimon of any stage.\nThis setting does not yet randomize non-scannable digimon (e.g. Grimmon, SkullBaluchimon).")
enemy_digimon_randomize_completely_rb.pack(anchor="w")



## Right side: Stat Generation frame
#enemy_stat_gen_frame = ttk.LabelFrame(enemy_digimon_inner_container, text="Stat Generation", padding=10)
#enemy_stat_gen_frame.pack(side="top", fill="y", padx=10, pady=5)
#
#enemy_stat_gen_option_var = tk.IntVar(value=LvlUpMode.RANDOM.value)  # Default to "Random"
#
#enemy_stat_gen_radio_buttons = []
#enemy_stat_gen_options = [("Random", LvlUpMode.RANDOM.value), ("Lowest (easier)", LvlUpMode.FIXED_MIN.value), ("Median", LvlUpMode.FIXED_AVG.value), ("Highest (harder)", LvlUpMode.FIXED_MAX.value)]
#enemy_stat_gen_tooltips = ["A random value from the possible level-up values is picked for each stat upon each level-up operation while generating the enemy digimon's stats.\nThis is likely to result in an average stat distribution for the digimon, but is less deterministic than Median.", "The lowest value from the possible level-up values is always picked for each stat upon each level-up operation while generating the enemy digimon's stats.\nThis gives the enemy digimon a weaker stat constitution, thus granting an easier game experience.", "The median value from the possible level-up values is always picked for each stat upon each level-up operation while generating the enemy digimon's stats.\nThis gives the enemy digimon a median stat constitution.", "The highest value from the possible level-up values is always picked for each stat upon each level-up operation while generating the enemy digimon's stats.\nThis gives the enemy digimon a stronger stat constitution, thus granting a harder game experience."]
#
#for text, value in enemy_stat_gen_options:
#    rb = tk.Radiobutton(
#        enemy_stat_gen_frame,
#        text=text,
#        variable=enemy_stat_gen_option_var,
#        value=value,
#        state="disabled"  # Initially disabled
#    )
#    rb.pack(anchor="w")
#    CreateToolTip(rb, enemy_stat_gen_tooltips[value])
#    enemy_stat_gen_radio_buttons.append(rb)
#
## Initialize the toggle state
#toggle_enemy_stat_generation()







# Base Information Tab
base_information_tab = ttk.Frame(notebook, padding=10)
base_information_tab.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(base_information_tab, text="Species & Base Stats")


# Species frame
species_frame = ttk.LabelFrame(base_information_tab, text="Digimon Species", padding=10)
species_frame.pack(side="top", fill="x", padx=10, pady=5)
#species_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))



species_radio_frame = ttk.Frame(species_frame)
species_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

species_option_var = tk.IntVar(value=RandomizeSpeciesConfig.UNCHANGED.value)

species_unchanged_rb = tk.Radiobutton(species_radio_frame, text="Unchanged", variable=species_option_var, value=RandomizeSpeciesConfig.UNCHANGED.value, state="disabled")
species_unchanged_rb.pack(anchor="w")


species_random_rb = tk.Radiobutton(species_radio_frame, text="Random", variable=species_option_var, value=RandomizeSpeciesConfig.RANDOM.value, state="disabled")
species_random_tooltip = CreateToolTip(species_random_rb, "Randomizes each digimon's species (HOLY, DARK, DRAGON, etc), changing the corresponding Species EXP awarded.\nIf paired with related options such as Elemental Resistance randomization, or Digivolution randomization w/ Similar Species, this option will significantly influence the results of the randomization.")
species_random_rb.pack(anchor="w")


species_sub_frame = ttk.Frame(species_frame)
species_sub_frame.pack(side="left", fill="both", expand=True, padx=10)


species_allow_unknown_var = tk.BooleanVar(value=False)
speciesAllowUnknownCheckbox = tk.Checkbutton(species_sub_frame, text="Allow [???] Species", variable=species_allow_unknown_var, state="disabled")
speciesAllowUnknownCheckbox.pack(anchor="w")
speciesAllowUnknownTooltip = CreateToolTip(speciesAllowUnknownCheckbox, "Allows digimon species to be randomized into [???] species.\nThis is the set species for bosses such as Grimmon.")





elemental_res_frame = ttk.LabelFrame(base_information_tab, text="Elemental Resistances", padding=10)
elemental_res_frame.pack(side="top", fill="x", padx=10, pady=5)
#elemental_res_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))


elemental_res_main_frame = ttk.Frame(elemental_res_frame)
elemental_res_main_frame.pack(side="left", fill="both", expand=True, padx=10)

elemental_res_option_var = tk.IntVar(value=RandomizeElementalResistances.UNCHANGED.value)

elemental_res_unchanged_rb = tk.Radiobutton(elemental_res_main_frame, text="Unchanged", variable=elemental_res_option_var, value=RandomizeElementalResistances.UNCHANGED.value, state="disabled")
elemental_res_unchanged_rb.pack(anchor="w")

elemental_res_shuffle_rb = tk.Radiobutton(elemental_res_main_frame, text="Shuffle", variable=elemental_res_option_var, value=RandomizeElementalResistances.SHUFFLE.value, state="disabled")
elemental_res_shuffle_tooltip = CreateToolTip(elemental_res_shuffle_rb, "Shuffles the resistance values of a given digimon.\nFor example, if Greymon has a WATER resistance of 700, if shuffled, another elemental resistance (e.g. WIND) will be set with the value 700, and Greymon's WATER resistance will be set to the original value of one of its other elements.")
elemental_res_shuffle_rb.pack(anchor="w")

elemental_res_randomize_rb = tk.Radiobutton(elemental_res_main_frame, text="Random", variable=elemental_res_option_var, value=RandomizeElementalResistances.RANDOM.value, state="disabled")
elemental_res_randomize_tooltip = CreateToolTip(elemental_res_randomize_rb, "Randomizes the resistance values of a given digimon.\nThe total sum of the generated resistance values will always equal the total sum of the original resistance values (e.g: if Greymon originally had the resistance values [700, 500, 1000, 100, 200, 500, 700, 500] with a total of 4200, the sum of the newly-generated values would also be 4200).")
elemental_res_randomize_rb.pack(anchor="w")


elemental_res_sub_frame = ttk.Frame(elemental_res_frame)
elemental_res_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

elemental_res_keep_coherence_var = tk.BooleanVar(value=False)
elementalResKeepCoherenceCheckbox = tk.Checkbutton(elemental_res_sub_frame, text="Keep Species-Resistance Coherence", variable=elemental_res_keep_coherence_var, state="disabled")
#digivolutionSimilarSpeciesCheckbox.pack(anchor="w")
elementalResKeepCoherenceCheckbox.pack(anchor="w")
elementalResKeepCoherenceTooltip = CreateToolTip(elementalResKeepCoherenceCheckbox, "Ensures that the main resistance and main weakness of each digimon is coherent with their species.\nFor example, a digimon of the HOLY species will guaranteedly have its highest resistance be LIGHT, and its lowest resistance be DARK.")




stats_stattype_container = ttk.Frame(base_information_tab)
stats_stattype_container.pack(side="top", fill="x", padx=10, pady=5)

# Base Stats frame
base_stats_frame = ttk.LabelFrame(stats_stattype_container, text="Base Stats", padding=10)
base_stats_frame.pack(side="left", fill="both", expand=True)


base_stats_main_frame = ttk.Frame(base_stats_frame)
base_stats_main_frame.pack(side="left", fill="both", expand=True, padx=10)

base_stats_option_var = tk.IntVar(value=RandomizeBaseStats.UNCHANGED.value)
base_stats_unchanged_rb = tk.Radiobutton(base_stats_main_frame, text="Unchanged", variable=base_stats_option_var, value=RandomizeBaseStats.UNCHANGED.value, state="disabled")
base_stats_unchanged_rb.pack(anchor="w")

base_stats_shuffle_rb = tk.Radiobutton(base_stats_main_frame, text="Shuffle", variable=base_stats_option_var, value=RandomizeBaseStats.SHUFFLE.value, state="disabled")
base_stats_shuffle_tooltip = CreateToolTip(base_stats_shuffle_rb, "Shuffles the ATK, DEF, SPIRIT and SPEED values of a given digimon.\nThe values for HP, MP and APTITUDE will be unchanged.")
base_stats_shuffle_rb.pack(anchor="w")

base_stats_random_sane_rb = tk.Radiobutton(base_stats_main_frame, text="Random (Sanity)", variable=base_stats_option_var, value=RandomizeBaseStats.RANDOM_SANITY.value, state="disabled")
base_stats_random_sane_tooltip = CreateToolTip(base_stats_random_sane_rb, "Randomizes base stats given the digimon's base stat total, but ensures that HP and MP are always higher than the digimon's highest stat (between ATK, DEF, SPIRIT or SPEED).\nThis does not randomize APTITUDE.")
base_stats_random_sane_rb.pack(anchor="w")

base_stats_random_full_rb = tk.Radiobutton(base_stats_main_frame, text="Random (Completely)", variable=base_stats_option_var, value=RandomizeBaseStats.RANDOM_COMPLETELY.value, state="disabled")
base_stats_random_full_tooltip = CreateToolTip(base_stats_random_full_rb, "Completely randomizes base stats according to the digimon's base stat total.\nAssumes a minimum of 40 on HP and MP, and 20 on ATK, DEF, SPIRIT and SPEED. This does not randomize APTITUDE.")
base_stats_random_full_rb.pack(anchor="w")


base_stats_sub_frame = ttk.Frame(base_stats_frame)
base_stats_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

base_stats_bias_type_var = tk.BooleanVar(value=False)
base_stats_bias_type_cb = tk.Checkbutton(base_stats_sub_frame, text="Digimon StatType Bias", variable=base_stats_bias_type_var, state="disabled")
base_stats_bias_type_tooltip = CreateToolTip(base_stats_bias_type_cb, "Forces the Digimon's highest stat to match its StatType.\nE.g. Attacker -> higher ATK stat; Tank -> higher DEF stat.\nThis does not apply to HP and MP if Shuffle, and if doing Random (Sanity), HP and MP are considered distinct from ATK, DEF, SPIRIT, SPEED (if the target digimon is an Attacker, then the highest stat between ATK, DEF, SPIRIT and SPEED is swapped).")
base_stats_bias_type_cb.pack(anchor="w")


# Digimon Type frame
digimon_type_frame = ttk.LabelFrame(stats_stattype_container, text="Digimon StatType", padding=10)
digimon_type_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))


digimon_type_main_frame = ttk.Frame(digimon_type_frame)
digimon_type_main_frame.pack(side="left", fill="both", expand=True, padx=10)

digimon_type_option_var = tk.IntVar(value=RandomizeDigimonStatType.UNCHANGED.value)
digimon_type_unchanged_rb = tk.Radiobutton(digimon_type_main_frame, text="Unchanged", variable=digimon_type_option_var, value=RandomizeDigimonStatType.UNCHANGED.value, state="disabled")
digimon_type_unchanged_rb.pack(anchor="w")

digimon_type_randomize_rb = tk.Radiobutton(digimon_type_main_frame, text="Random", variable=digimon_type_option_var, value=RandomizeDigimonStatType.RANDOMIZE.value, state="disabled")
digimon_type_randomize_tooltip = CreateToolTip(digimon_type_randomize_rb, "Randomizes Digimon's StatType (Balance, Attacker, Tank, etc).\nThis affects stat growths (e.g. Attacker digimon typically have higher ATK stat gains upon levelling up).")
digimon_type_randomize_rb.pack(anchor="w")



# Base Information Tab
movesets_traits_tab = ttk.Frame(notebook, padding=10)
movesets_traits_tab.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(movesets_traits_tab, text="Movesets & Traits")



# Movesets frame

movesets_frame = ttk.LabelFrame(movesets_traits_tab, text="Movesets", padding=10)
movesets_frame.pack(side="top", fill="x", padx=10, pady=5)

movesets_option_var = tk.IntVar(value=RandomizeMovesets.UNCHANGED.value)


movesets_radio_frame = ttk.Frame(movesets_frame)
movesets_radio_frame.pack(side="left", fill="both", expand=True, padx=10)


movesets_unchanged_rb = tk.Radiobutton(movesets_radio_frame, text="Unchanged", variable=movesets_option_var, value=RandomizeMovesets.UNCHANGED.value, state="disabled")
movesets_unchanged_rb.pack(anchor="w")

movesets_randomize_same_species_rb = tk.Radiobutton(movesets_radio_frame, text="Random (preferring same species)", variable=movesets_option_var, value=RandomizeMovesets.RANDOM_SPECIES_BIAS.value, state="disabled")
movesets_randomize_rb_tooltip = CreateToolTip(movesets_randomize_same_species_rb, "Randomizes each digimon's movesets, with bias for moves with the main element of the given digimon's species (e.g. HOLY digimon will be more likely to have LIGHT moves).")
movesets_randomize_same_species_rb.pack(anchor="w")

movesets_randomize_rb = tk.Radiobutton(movesets_radio_frame, text="Random (completely)", variable=movesets_option_var, value=RandomizeMovesets.RANDOM_COMPLETELY.value, state="disabled")
movesets_randomize_rb_tooltip = CreateToolTip(movesets_randomize_rb, "Randomizes each digimon's movesets completely.")
movesets_randomize_rb.pack(anchor="w")


movesets_sub_frame = ttk.Frame(movesets_frame)
movesets_sub_frame.pack(side="left", fill="both", expand=True, padx=10)


movesets_level_bias_var = tk.BooleanVar(value=False)
movesetsLevelBiasCheckbox = tk.Checkbutton(movesets_sub_frame, text="Move Level Bias", variable=movesets_level_bias_var, state="disabled")
movesetsLevelBiasCheckbox.pack(anchor="w")
movesetsLevelBiasTooltip = CreateToolTip(movesetsLevelBiasCheckbox, "When randomizing Digimon movesets, each new move will be learned at a level close to the original move's level (within +- 5 levels, by default).\nE.g. a digimon that originally learned Little Blizzard (lvl 10) will have it replaced by a move learned between levels 5-15.\nThis setting is not recommended to use with \"Add Signature Moves To Random Pool\", as signature moves are learned at lvl 1 (thus only regular moves learned near lvl 1 would be changed).")

movesets_power_bias_var = tk.BooleanVar(value=False)
movesetsPowerBiasCheckbox = tk.Checkbutton(movesets_sub_frame, text="Regular Move Power Bias", variable=movesets_power_bias_var, state="disabled")
movesetsPowerBiasCheckbox.pack(anchor="w")
movesetsPowerBiasTooltip = CreateToolTip(movesetsPowerBiasCheckbox, "When randomizing Digimon movesets, each regular move will be replaced by a move with a similar power value to the original (within +- 8 power, by default).\nE.g. a digimon that originally learned Little Blizzard (28 power) will have it replaced by a move that has between 20-36 power whenever possible (this includes signature moves if \"Add Signature Moves To Regular Move Pool\" is enabled).")

movesets_signature_power_bias_var = tk.BooleanVar(value=False)
movesetsSignaturePowerBiasCheckbox = tk.Checkbutton(movesets_sub_frame, text="Signature Move Power Bias", variable=movesets_signature_power_bias_var, state="disabled")
movesetsSignaturePowerBiasCheckbox.pack(anchor="w")
movesetsSignaturePowerBiasTooltip = CreateToolTip(movesetsSignaturePowerBiasCheckbox, "When randomizing Digimon movesets, each signature move will be replaced by another signature move with a similar power value to the original (within +- 8 power, by default).\nE.g. a digimon that originally had Bantyo Blade (145 power) as its signature move will have it replaced by a move that has between 137-153 power whenever possible.")

movesets_signature_moves_var = tk.BooleanVar(value=False)
movesetsSignatureMovesCheckbox = tk.Checkbutton(movesets_sub_frame, text="Add Signature Moves To Regular Move Pool", variable=movesets_signature_moves_var, state="disabled")
movesetsSignatureMovesCheckbox.pack(anchor="w")
movesetsSignatureMovesTooltip = CreateToolTip(movesetsSignatureMovesCheckbox, "Adds the exclusive signature move of each digimon to the regular moveset randomization pool.\nBy default, learned moves and signature moves are randomized separately, as signature moves are always learned at lvl 1.\nE.g. with this option enabled, a digimon could have up to four signature moves at lvl 1 (depending on the randomization result).\nThis setting is not recommended to use with \"Move Level Bias\", as signature moves are learned at lvl 1 (thus only regular moves learned near lvl 1 would be changed).")


movesets_guarantee_basic_move_var = tk.BooleanVar(value=False)
movesetsGuaranteeBasicMoveCheckbox = tk.Checkbutton(movesets_sub_frame, text="Guarantee Basic Move", variable=movesets_guarantee_basic_move_var, state="disabled")
movesetsGuaranteeBasicMoveCheckbox.pack(anchor="w")
movesetsGuaranteeBasicMoveTooltip = CreateToolTip(movesetsGuaranteeBasicMoveCheckbox, "Forces the first move of each digimon to be the move Charge, which is changed to have 8 base power and cost 0 MP.\nThis ensures that all digimon have access to at least one basic move that they can use.\nIf this option is checked without randomizing the movesets, then the first move of all digimon will be replaced by Charge.")



traits_frame = ttk.LabelFrame(movesets_traits_tab, text="Traits", padding=10)
traits_frame.pack(side="top", fill="x", padx=10, pady=5)

traits_option_var = tk.IntVar(value=RandomizeTraits.UNCHANGED.value)

traits_radio_frame = ttk.Frame(traits_frame)
traits_radio_frame.pack(side="left", fill="both", expand=True, padx=10)


traits_unchanged_rb = tk.Radiobutton(traits_radio_frame, text="Unchanged", variable=traits_option_var, value=RandomizeTraits.UNCHANGED.value, state="disabled")
traits_unchanged_rb.pack(anchor="w")

traits_randomize_same_stage_rb = tk.Radiobutton(traits_radio_frame, text="Random (same stages)", variable=traits_option_var, value=RandomizeTraits.RANDOM_STAGE_BIAS.value, state="disabled")
traits_randomize_same_stage_rb_tooltip = CreateToolTip(traits_randomize_same_stage_rb, "Randomizes each digimon's traits within its own stage group.\nE.g. the trait \"Speed 1\" will only be learnable by in-training digimon, \"Speed 2\" will only be learnable by rookie digimon, etc.")
traits_randomize_same_stage_rb.pack(anchor="w")

traits_randomize_completely_rb = tk.Radiobutton(traits_radio_frame, text="Random (completely)", variable=traits_option_var, value=RandomizeTraits.RANDOM_COMPLETELY.value, state="disabled")
traits_randomize_completely_rb_tooltip = CreateToolTip(traits_randomize_completely_rb, "Randomizes each digimon's traits completely.")
traits_randomize_completely_rb.pack(anchor="w")


traits_sub_frame = ttk.Frame(traits_frame)
traits_sub_frame.pack(side="left", fill="both", expand=True, padx=10)


# force 4 traits on every digimon

traits_force_four_var = tk.BooleanVar(value=False)
traitsForceFourCheckbox = tk.Checkbutton(traits_sub_frame, text="Force Four Traits", variable=traits_force_four_var, state="disabled")
traitsForceFourCheckbox.pack(anchor="w")
traitsForceFourTooltip = CreateToolTip(traitsForceFourCheckbox, "Forces every digimon to have 4 traits (+ support trait).\nTypically, In-Training digimon have 1 trait, Rookie and Champion digimon have 2 traits, Ultimate digimon have 3 traits, and Mega digimon have 4 traits.")

# enable unused traits
traits_enable_unused_var = tk.BooleanVar(value=False)
traitsEnableUnusedCheckbox = tk.Checkbutton(traits_sub_frame, text="Enable Unused Traits", variable=traits_enable_unused_var, state="disabled")
traitsEnableUnusedCheckbox.pack(anchor="w")
traitsEnableUnusedTooltip = CreateToolTip(traitsEnableUnusedCheckbox, "Adds traits that were not used by the game's code to the possible trait pool.\nIf Random (same stages) is set, then these traits will only appear for digimon of the stages Ultimate and Mega.\nThis option is highly experimental and not recommended for proper gameplay.\nThere are a total of 18 unused traits, with descriptions such as:\nFriend Power: Damage done using DigivolveDisk increases by 10%\nDigivolveSoul: Slightly increases Digimon's abrupt evolution\nChildlikeHeart: Slightly increases success rate of farm goods")



# Digivolutions Tab
digivolutions_tab = ttk.Frame(notebook, padding=10)
digivolutions_tab.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(digivolutions_tab, text="Digivolutions")


# Digivolutions frame

general_digivolution_settings_frame = ttk.Frame(digivolutions_tab)
general_digivolution_settings_frame.pack(side="top", fill="x")

digivolutions_frame = ttk.LabelFrame(general_digivolution_settings_frame, text="Digivolutions", padding=10)
digivolutions_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

digivolutions_inner_container = ttk.Frame(digivolutions_frame)
digivolutions_inner_container.pack(side="top", fill="x")

digivolutions_option_var = tk.IntVar(value=RandomizeDigivolutions.UNCHANGED.value)


# Digivolution radio buttons frame
digivolutions_radio_frame = ttk.Frame(digivolutions_inner_container)
digivolutions_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

digivolutions_unchanged_rb = tk.Radiobutton(digivolutions_radio_frame, text="Unchanged", variable=digivolutions_option_var, value=RandomizeDigivolutions.UNCHANGED.value, state="disabled", command=toggle_digivolution_randomization_options)
digivolutions_unchanged_rb.pack(anchor="w")

digivolutions_randomize_rb = tk.Radiobutton(digivolutions_radio_frame, text="Random", variable=digivolutions_option_var, value=RandomizeDigivolutions.RANDOMIZE.value, state="disabled", command=toggle_digivolution_randomization_options)
digivolutions_randomize_rb_tooltip = CreateToolTip(digivolutions_randomize_rb, "Randomizes each digimon's digivolutions, creating up to three different digivolutions for each digimon.\nIf a digimon did not have any digivolution conditions, a set of conditions will be generated for it.")
digivolutions_randomize_rb.pack(anchor="w")


# Specific options for digivolution randomization

digivolutions_sub_frame = ttk.Frame(digivolutions_inner_container)
digivolutions_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

digivolution_similar_species_var = tk.BooleanVar(value=False)
digivolutionSimilarSpeciesCheckbox = tk.Checkbutton(digivolutions_sub_frame, text="Similar Species", variable=digivolution_similar_species_var, state="disabled")
#digivolutionSimilarSpeciesCheckbox.pack(anchor="w")
digivolutionSimilarSpeciesCheckbox.grid(row=0, column=0, sticky="w")
digivolutionSimilarSpeciesTootip = CreateToolTip(digivolutionSimilarSpeciesCheckbox, "Digivolutions will be more likely to follow the digimon's original species.\nExample: a holy digimon will be more likely to evolve into other holy digimon.")


# Digivolution conditions randomization

digivolution_conditions_frame = ttk.LabelFrame(digivolutions_inner_container, text="Digivolution Conditions", padding=10)
digivolution_conditions_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

digivolution_conditions_inner_container = ttk.Frame(digivolution_conditions_frame)
digivolution_conditions_inner_container.pack(side="top", fill="x")

# Digivolution conditions radio buttons frame
digivolution_conditions_radio_frame = ttk.Frame(digivolution_conditions_inner_container)
digivolution_conditions_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

digivolution_conditions_option_var = tk.IntVar(value=RandomizeDigivolutionConditions.UNCHANGED.value)

digivolution_conditions_unchanged_rb = tk.Radiobutton(digivolution_conditions_radio_frame, text="Unchanged", variable=digivolution_conditions_option_var, value=RandomizeDigivolutionConditions.UNCHANGED.value, state="disabled")
digivolution_conditions_unchanged_rb.pack(anchor="w")

digivolution_conditions_randomize_rb = tk.Radiobutton(digivolution_conditions_radio_frame, text="Random", variable=digivolution_conditions_option_var, value=RandomizeDigivolutionConditions.RANDOMIZE.value, state="disabled")
digivolution_conditions_randomize_rb_tooltip = CreateToolTip(digivolution_conditions_randomize_rb, "Randomizes each digimon's digivolution conditions, creating up to three different conditions for each digimon.\nLvl will always be the first condition.")
digivolution_conditions_randomize_rb.pack(anchor="w")


# Specific options for digivolution conditions randomization

digivolution_conditions_sub_frame = ttk.Frame(digivolution_conditions_inner_container)
digivolution_conditions_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

digivolution_conditions_species_exp_var = tk.BooleanVar(value=False)
digivolutionConditionsSpeciesExpCheckbox = tk.Checkbutton(digivolution_conditions_sub_frame, text="Follow Species EXP", variable=digivolution_conditions_species_exp_var, state="disabled")
digivolutionConditionsSpeciesExpCheckbox.pack(anchor='w')
digivolutionConditionsSpeciesExpTootip = CreateToolTip(digivolutionConditionsSpeciesExpCheckbox, "Digivolutions will be less likely to need EXP from different species than their own.\nExample: a digivolution from the HOLY species will be less likely to have AQUAN/DARK/etc EXP as a requirement.\nThis can be applied to newly generated digivolutions even if the base conditions are not randomized (if a digimon did not have any digivolution conditions, it will follow this rule).")






# DNA Digivolutions frame


dna_digivolutions_frame = ttk.LabelFrame(general_digivolution_settings_frame, text="DNA Digivolutions", padding=10)
dna_digivolutions_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

dna_digivolutions_inner_container = ttk.Frame(dna_digivolutions_frame)
dna_digivolutions_inner_container.pack(side="top", fill="x")

dna_digivolutions_option_var = tk.IntVar(value=RandomizeDnaDigivolutions.UNCHANGED.value)





# DNA Digivolution radio buttons frame
dna_digivolutions_radio_frame = ttk.Frame(dna_digivolutions_inner_container)
dna_digivolutions_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

dna_digivolutions_unchanged_rb = tk.Radiobutton(dna_digivolutions_radio_frame, text="Unchanged", variable=dna_digivolutions_option_var, value=RandomizeDnaDigivolutions.UNCHANGED.value, state="disabled")
dna_digivolutions_unchanged_rb.pack(anchor="w")

#dna_digivolutions_randomize_same_stage_rb = tk.Radiobutton(dna_digivolutions_radio_frame, text="Random (same stages)", variable=dna_digivolutions_option_var, value=RandomizeDnaDigivolutions.RANDOMIZE_SAME_STAGE.value, state="disabled", command=toggle_dna_digivolution_rand_options)
dna_digivolutions_randomize_same_stage_rb = tk.Radiobutton(dna_digivolutions_radio_frame, text="Random (same stages)", variable=dna_digivolutions_option_var, value=RandomizeDnaDigivolutions.RANDOMIZE_SAME_STAGE.value, state="disabled")
dna_digivolutions_randomize_same_stage_rb_tooltip = CreateToolTip(dna_digivolutions_randomize_same_stage_rb, "Randomizes each DNA digivolution, keeping the original stages for each DNA digivolution.\nE.g. for Patamon + SnowAgumon = Airdramon, Patamon and SnowAgumon will be replaced by two other rookie digimon and Airdramon will be replaced by another champion digimon.")
dna_digivolutions_randomize_same_stage_rb.pack(anchor="w")

#dna_digivolutions_randomize_completely_rb = tk.Radiobutton(dna_digivolutions_radio_frame, text="Random (completely)", variable=dna_digivolutions_option_var, value=RandomizeDnaDigivolutions.RANDOMIZE_COMPLETELY.value, state="disabled", command=toggle_dna_digivolution_rand_options)
dna_digivolutions_randomize_completely_rb = tk.Radiobutton(dna_digivolutions_radio_frame, text="Random (completely)", variable=dna_digivolutions_option_var, value=RandomizeDnaDigivolutions.RANDOMIZE_COMPLETELY.value, state="disabled")
dna_digivolutions_randomize_completely_rb_tooltip = CreateToolTip(dna_digivolutions_randomize_completely_rb, "Randomizes each DNA digivolution, creating new combinations regardless of stage.\nThis may result in scenarios where, for example, joining two In-Training digimon generates an Ultimate digimon, or joining two Mega digimon results in a Rookie digimon.")
dna_digivolutions_randomize_completely_rb.pack(anchor="w")


# Specific options for digivolution randomization
# disabling for now
dna_digivolutions_sub_frame = ttk.Frame(dna_digivolutions_inner_container)
dna_digivolutions_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

'''
dna_digivolution_force_rare_var = tk.BooleanVar(value=False)
dnaDigivolutionForceRareCheckbox = tk.Checkbutton(dna_digivolutions_sub_frame, text="Prioritize Rare Digimon", variable=dna_digivolution_force_rare_var, state="disabled")
#dnaDigivolutionForceRareCheckbox.pack(anchor='w')
dnaDigivolutionForceRareCheckbox.grid(row=0, column=0, sticky="w")
dnaDigivolutionForceRareTooltip = CreateToolTip(dnaDigivolutionForceRareCheckbox, "If randomized, DNA Digivolutions will prioritize digimon that are not obtainable in the wild or through any standard evolution line of the current seed.\nE.g. if Gallantmon is not obtainable in the wild or through any digivolution line of an obtainable digimon, then it will have priority over other Mega digimon that are obtainable.")
'''

# DNA Digivolution conditions randomization

dna_digivolution_conditions_frame = ttk.LabelFrame(dna_digivolutions_inner_container, text="DNA Digivolution Conditions", padding=10)
dna_digivolution_conditions_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

dna_digivolution_conditions_inner_container = ttk.Frame(dna_digivolution_conditions_frame)
dna_digivolution_conditions_inner_container.pack(side="top", fill="x")

# DNA Digivolution conditions radio buttons frame
dna_digivolution_conditions_radio_frame = ttk.Frame(dna_digivolution_conditions_inner_container)
dna_digivolution_conditions_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

dna_digivolution_conditions_option_var = tk.IntVar(value=RandomizeDnaDigivolutionConditions.UNCHANGED.value)

dna_digivolution_conditions_unchanged_rb = tk.Radiobutton(dna_digivolution_conditions_radio_frame, text="Unchanged", variable=dna_digivolution_conditions_option_var, value=RandomizeDnaDigivolutionConditions.UNCHANGED.value, state="disabled")
dna_digivolution_conditions_unchanged_rb_tooltip = CreateToolTip(dna_digivolution_conditions_unchanged_rb, "Keeps the original DNA digivolution's conditions unchanged.\n If a given digimon did not have a DNA digivolution before, then a set of DNA digivolution conditions will be generated for that digimon.")
dna_digivolution_conditions_unchanged_rb.pack(anchor="w")

dna_digivolution_conditions_randomize_rb = tk.Radiobutton(dna_digivolution_conditions_radio_frame, text="Random", variable=dna_digivolution_conditions_option_var, value=RandomizeDnaDigivolutionConditions.RANDOMIZE.value, state="disabled")
dna_digivolution_conditions_randomize_rb_tooltip = CreateToolTip(dna_digivolution_conditions_randomize_rb, "Randomizes each DNA digivolution's conditions, creating up to three different conditions for each DNA digivolution.\nLvl will always be the first condition.")
dna_digivolution_conditions_randomize_rb.pack(anchor="w")

dna_digivolution_conditions_remove_rb = tk.Radiobutton(dna_digivolution_conditions_radio_frame, text="Removed", variable=dna_digivolution_conditions_option_var, value=RandomizeDnaDigivolutionConditions.REMOVED.value, state="disabled")
dna_digivolution_conditions_remove_rb_tooltip = CreateToolTip(dna_digivolution_conditions_remove_rb, "Removes all conditions to DNA digivolve two digimon.\nE.g. to digivolve WarGreymon and MetalGarurumon into Omnimon, the requirements of lvl 65, speed 415, friendship 100% will no longer be required.")
dna_digivolution_conditions_remove_rb.pack(anchor="w")

# Specific options for digivolution conditions randomization

dna_digivolution_conditions_sub_frame = ttk.Frame(dna_digivolution_conditions_inner_container)
dna_digivolution_conditions_sub_frame.pack(side="left", fill="both", expand=True, padx=10)

dna_digivolution_conditions_species_exp_var = tk.BooleanVar(value=False)
dnaDigivolutionConditionsSpeciesExpCheckbox = tk.Checkbutton(dna_digivolution_conditions_sub_frame, text="Follow Species EXP", variable=dna_digivolution_conditions_species_exp_var, state="disabled")
dnaDigivolutionConditionsSpeciesExpCheckbox.pack(anchor='w')
dnaDigivolutionConditionsSpeciesExpTootip = CreateToolTip(dnaDigivolutionConditionsSpeciesExpCheckbox, "DNA Digivolutions will be less likely to need EXP from species that are not part of the three digimon involved in each DNA digivolution.\nE.g. for the hypothetical DNA digivolution composed of Agumon + Gaomon = Devimon, it will be less likely to have any EXP that is not DRAGON, BEAST or DARK as a requirement.")









# Apply buttons at the bottom
button_frame = tk.Frame(root, pady=10)
button_frame.pack()

# autoupdater version check
autoUpdater.mainThreadCheck(root, APP_VERSION, app_state._get_preferences_path())

# Run the Tkinter event loop
root.mainloop()