import copy
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ui.tooltip import CreateToolTip
import os
from qol_script import DigimonROM, Randomizer
from configs import ExpYieldConfig, RandomizeOverworldItems, RandomizeStartersConfig, RandomizeWildEncounters, RandomizeDigivolutions, RandomizeDigivolutionConditions, ConfigManager, RookieResetConfig
from src.model import LvlUpMode
from pathlib import Path
import webbrowser
import sys
import random
import numpy as np
import logging
from io import StringIO
from ui.LabelledSlider import LabelledSlider



class AppState:
    def __init__(self):
        self.config_manager: ConfigManager = ConfigManager()
        self.current_rom: DigimonROM = None  
        self.target_rom: DigimonROM = None  
        self.randomizer: Randomizer = None
        self.log_stream: StringIO = StringIO()
        self.logger: logging.Logger = self.setLogger()
        self.seed: int = -1

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


# this function is called when writing the patched/randomized rom; serves as the equivalent to main() for qol_script
def execute_rom_changes(save_path):

    patcher_config_options = {
        "CHANGE_TEXT_SPEED": change_text_speed_var,
        "CHANGE_MOVEMENT_SPEED": change_movement_speed_var,
        "CHANGE_ENCOUNTER_RATE": change_wild_encounter_rate_var,
        #"CHANGE_STAT_CAPS": increase_stat_caps_var,
        "EXTEND_PLAYERNAME_SIZE": expand_player_name_var,

        "APPLY_EXP_PATCH_FLAT": ExpYieldConfig(exp_yield_option_var.get()),
        "BUFF_SCAN_RATE": increase_flat_scan_rate_var,
        "CHANGE_FARM_EXP": change_farm_exp_var,
        "ENABLE_VERSION_EXCLUSIVE_AREAS": unlock_version_exclusive_areas_var,
    
        "RANDOMIZE_STARTERS": RandomizeStartersConfig(starters_option_var.get()),  # RandomizeStartersConfig(starters_option_var) might have to be initialized like this
        "ROOKIE_RESET_EVENT": RookieResetConfig(rookie_reset_option_var.get()),
        "NERF_FIRST_BOSS": nerf_first_boss_var,
        
        "RANDOMIZE_AREA_ENCOUNTERS": RandomizeWildEncounters(wild_digimon_option_var.get()),
        "WILD_DIGIMON_EXCLUDE_CALUMON": wild_digimon_exclude_calumon_var,
        "AREA_ENCOUNTERS_STATS": stat_gen_option_var,

        "RANDOMIZE_DIGIVOLUTIONS": RandomizeDigivolutions(digivolutions_option_var.get()),
        "DIGIVOLUTIONS_SIMILAR_SPECIES": digivolution_similar_species_var,

        "RANDOMIZE_DIGIVOLUTION_CONDITIONS": RandomizeDigivolutionConditions(digivolution_conditions_option_var.get()),
        "DIGIVOLUTION_CONDITIONS_AVOID_DIFF_SPECIES_EXP": digivolution_conditions_species_exp_var,

        "RANDOMIZE_OVERWORLD_ITEMS": RandomizeOverworldItems(overworld_items_option_var.get())
    }


    if(app_state.seed == -1):
        app_state.seed = random.randrange(2**32-1)
        
    app_state.apply_seed()
    app_state.config_manager.update_from_ui(patcher_config_options)
    app_state.target_rom.executeQolChanges()
    app_state.randomizer.executeRandomizerFunctions()
    app_state.target_rom.writeRom(save_path)
    app_state.writeLog(save_path)
    app_state.seed = -1
    app_state.target_rom = copy.deepcopy(app_state.current_rom)     # next randomization will be applied to base rom instead of previously randomized rom again




def enable_buttons():
    
    # Enable Save Changes button
    save_changes_button.configure(state="normal")

    # Enable qol checkboxes
    textSpeedCheckbox.configure(state="normal")
    increaseMovementSpeedCheckbox.configure(state="normal")
    decreaseWildEncounterCheckbox.configure(state="normal")
    #increaseStatCapsCheckbox.configure(state="normal")
    #increaseExpYieldCheckbox.configure(state="normal")
    increaseFlatScanRateCheckbox.configure(state="normal")
    expandPlayerNameCheckbox.configure(state="normal")
    increaseFarmExpCheckbox.configure(state="normal")
    unlockVersionExclusiveAreasCheckbox.configure(state="normal")
    exp_yield_unchanged_rb.configure(state="normal")
    exp_yield_halved_rb.configure(state="normal")
    exp_yield_full_rb.configure(state="normal")


    # Enable tabs
    notebook.tab(0, state="normal")  # QoL Changes tab
    notebook.tab(1, state="normal")  # Randomization Settings tab

    # Enable randomization options
    # Randomize starters
    starters_unchanged_rb.configure(state="normal")
    starters_same_stage_rb.configure(state="normal")
    starters_completely_random_rb.configure(state="normal")
    rookie_reset_unchanged_rb.configure(state="normal")
    rookie_reset_same_stage_rb.configure(state="normal")
    rookie_reset_cancel_rb.configure(state="normal")
    nerfFirstBossCheckbox.configure(state="normal")

    # Randomize wild digimon
    wild_digimon_unchanged_rb.configure(state="normal")
    wild_digimon_randomize_rb.configure(state="normal")
    wild_digimon_randomize_completely_rb.configure(state="normal")
    wildDigimonExcludeCalumonCheckbox.configure(state="normal")

    # Randomize digivolutions and conditions

    digivolutions_unchanged_rb.configure(state="normal")
    digivolutions_randomize_rb.configure(state="normal")
    digivolution_conditions_unchanged_rb.configure(state="normal")
    digivolution_conditions_randomize_rb.configure(state="normal")
    digivolutionConditionsSpeciesExpCheckbox.configure(state="normal")

    # Randomize overworld items

    overworld_items_unchanged_rb.configure(state="normal")
    overworld_items_same_category_rb.configure(state="normal")
    overworld_items_completely_random_rb.configure(state="normal")



def open_rom():
    file_path = filedialog.askopenfilename(
        title="Open ROM",
        filetypes=[("ROM Files", "*.nds"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            app_state.current_rom = DigimonROM(file_path, app_state.config_manager, app_state.logger)
            app_state.randomizer = Randomizer(app_state.current_rom.version, app_state.current_rom.rom_data, app_state.config_manager, app_state.logger)
            app_state.target_rom = copy.deepcopy(app_state.current_rom)
        except ValueError:
            messagebox.showerror("Error","Game not recognized. Please check your rom (file \"" +  os.path.basename(file_path) + "\").")
            return
        rom_name_label.config(text=f"ROM Name: {file_path.split('/')[-1]}")
        #rom_size_label.config(text=f"ROM Size: {os.path.getsize(file_path) / 1024:.2f} KB")
        rom_version_label.config(text=f"ROM Version: {app_state.current_rom.version}")
        rom_path_label.config(text=f"ROM Path: {file_path}")
        
        rom_status_label.config(text="Status: Loaded")

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
        text="Version 0.1.0",
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


def toggle_digivolution_randomization_options():
    if digivolutions_option_var.get() != RandomizeDigivolutions.UNCHANGED.value:
        digivolutionSimilarSpeciesCheckbox.configure(state="normal")
    else:
        digivolutionSimilarSpeciesCheckbox.configure(state="disabled")



# Initialize main window
root = tk.Tk()
root.title("Digimon World Dawn/Dusk Randomizer")
root.geometry("")
root.minsize(800, 600) 
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

premade_seed_button = ttk.Button(button_frame, text="Set Random Seed", command=set_random_seed)
premade_seed_button.pack(fill="x", pady=5)

about_button = ttk.Button(button_frame, text="About", command=show_about_popup)
about_button.pack(fill="x", pady=5)

# Right section: ROM Information
rom_info_frame = ttk.LabelFrame(rom_frame, text="ROM Information", padding=10)
rom_info_frame.pack(side="right", fill="both", expand=True, padx=10)

# Add some labels to display ROM info (placeholders for now)
rom_name_label = ttk.Label(rom_info_frame, text="ROM Name: Not Loaded")
rom_name_label.pack(anchor="w", pady=2)

#rom_size_label = ttk.Label(rom_info_frame, text="ROM Size: N/A")
#rom_size_label.pack(anchor="w", pady=2)

rom_version_label = ttk.Label(rom_info_frame, text="ROM Version: N/A")
rom_version_label.pack(anchor="w", pady=2)

rom_path_label = ttk.Label(rom_info_frame, text="ROM Path: N/A")
rom_path_label.pack(anchor="w", pady=2)

rom_status_label = ttk.Label(rom_info_frame, text="Status: Not Loaded")
rom_status_label.pack(anchor="w", pady=2)



# Create a Notebook widget to hold the tabs
notebook = ttk.Notebook(root, padding=10)
notebook.pack(fill="both", expand=True)

# QoL Changes Tab
qol_frame = ttk.Frame(notebook, padding=10)
qol_frame.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(qol_frame, text="QoL Patches")

# QoL Checkbuttons
change_text_speed_var = tk.BooleanVar(value=True)
textSpeedCheckbox = tk.Checkbutton(qol_frame, text="Increase Text Speed", variable=change_text_speed_var, state="disabled")
textSpeedCheckbox.pack(anchor='w')
textSpeedTooltip = CreateToolTip(textSpeedCheckbox, "Increases the speed at which the text is displayed, removing the need to hold A to speed up the dialogues.")

change_movement_speed_var = tk.BooleanVar(value=True)
increaseMovementSpeedCheckbox = tk.Checkbutton(qol_frame, text="Increase Movement Speed", variable=change_movement_speed_var, state="disabled")
increaseMovementSpeedCheckbox.pack(anchor='w')
increaseMovementSpeedTooltip = CreateToolTip(increaseMovementSpeedCheckbox, "Increases the player's movement speed to 1.5x of the default speed.")

change_wild_encounter_rate_var = tk.BooleanVar(value=True)
decreaseWildEncounterCheckbox = tk.Checkbutton(qol_frame, text="Reduce Wild Encounter Rate", variable=change_wild_encounter_rate_var, state="disabled")
decreaseWildEncounterCheckbox.pack(anchor='w')
decreaseWildEncounterTooltip = CreateToolTip(decreaseWildEncounterCheckbox, "Reduces the wild encounter rate in all areas by 0.5x.")

encounter_slider_widget = LabelledSlider(qol_frame)
encounter_slider_widget.pack(anchor="w", padx=10)

#increase_exp_yield_var = tk.BooleanVar(value=True)
#increaseExpYieldCheckbox = tk.Checkbutton(qol_frame, text="Increase Exp Yield for Wild Digimon", variable=increase_exp_yield_var, state="disabled")
#increaseExpYieldCheckbox.pack(anchor='w')
#increaseExpYieldTootip = CreateToolTip(increaseExpYieldCheckbox, "Changes the exp given by all wild digimon to match game progression.\nThe exp yield values are roughly calculated through pokémon's standard formula for experience yield: base_exp * encounter_lvl / 7, where base_exp is a fixed value depending on the digimon's digivolution stage, and encounter_lvl is the level of the encounter.")

increase_flat_scan_rate_var = tk.BooleanVar(value=True)
increaseFlatScanRateCheckbox = tk.Checkbutton(qol_frame, text="Increase Scan Rate", variable=increase_flat_scan_rate_var, state="disabled")
increaseFlatScanRateCheckbox.pack(anchor='w')
increaseFlatScanRateTooltip = CreateToolTip(increaseFlatScanRateCheckbox, "Increases the base scan rate by 10%.")

expand_player_name_var = tk.BooleanVar(value=True)
expandPlayerNameCheckbox = tk.Checkbutton(qol_frame, text="Expand Player Name Length", variable=expand_player_name_var, state="disabled")
expandPlayerNameCheckbox.pack(anchor="w")
expandPlayerNameTooltip = CreateToolTip(expandPlayerNameCheckbox, "Expands the maximum length of the player's name from 5 to 7 characters.")

#increase_stat_caps_var = tk.BooleanVar(value=False)
#increaseStatCapsCheckbox = tk.Checkbutton(qol_frame, text="Increase Stat Caps", variable=increase_stat_caps_var, state="disabled")
#increaseStatCapsCheckbox.pack(anchor='w')
#increaseStatCapsTooltip = CreateToolTip(increaseStatCapsCheckbox, "Increases the stat cap to 65535 for all stats.\nOriginally the HP and MP are limited to 9999, and the other stats are limited to 999.")


# Farm EXP; might do a custom frame for all exp-related stuff


change_farm_exp_var = tk.BooleanVar(value=True)
increaseFarmExpCheckbox = tk.Checkbutton(qol_frame, text="Increase Farm EXP", variable=change_farm_exp_var, state="disabled")
increaseFarmExpCheckbox.pack(anchor='w')
increaseFarmExpTooltip = CreateToolTip(increaseFarmExpCheckbox, "Increases the base farm exp by 10x.")


# unlock version-exclusive areas

unlock_version_exclusive_areas_var = tk.BooleanVar(value=True)
unlockVersionExclusiveAreasCheckbox = tk.Checkbutton(qol_frame, text="Unlock Version-Exclusive Areas", variable=unlock_version_exclusive_areas_var, state="disabled")
unlockVersionExclusiveAreasCheckbox.pack(anchor='w')
unlockVersionExclusiveAreasTooltip = CreateToolTip(unlockVersionExclusiveAreasCheckbox, "Unlocks areas that were previously exclusive to a single version of the game.\nFor DAWN, this option unlocks Magnet Mine at the same time that Task Canyon is unlocked, and unlocks Process Factory at the same time that Pallette Amazon is unlocked.\nFor DUSK, this option unlocks Task Canyon at the same time that Magnet Mine is unlocked.")




# Exp Yield frame
exp_yield_frame = ttk.LabelFrame(qol_frame, text="Exp. Yield", padding=10)
exp_yield_frame.pack(side="top", anchor="w", padx=10, pady=10)


exp_yield_option_var = tk.IntVar(value=ExpYieldConfig.INCREASE_HALVED.value)

exp_yield_unchanged_rb = tk.Radiobutton(exp_yield_frame, text="Unchanged", variable=exp_yield_option_var, value=ExpYieldConfig.UNCHANGED.value, state="disabled")
exp_yield_unchanged_rb.pack(anchor="w")

exp_yield_halved_rb = tk.Radiobutton(exp_yield_frame, text="Increase (halved)", variable=exp_yield_option_var, value=ExpYieldConfig.INCREASE_HALVED.value, state="disabled")
exp_yield_halved_tooltip = CreateToolTip(exp_yield_halved_rb, "Adjusts wild Digimon exp to match progression with half increase.\nExp is calculated using Pokémon's exp.share formula: base_exp * level / 14, where base_exp depends on evolution stage and level is the encounter level.\nFor reference, a lvl 33 wild Greymon's exp yield increases from 71 to 283 points.")
exp_yield_halved_rb.pack(anchor="w")

exp_yield_full_rb = tk.Radiobutton(exp_yield_frame, text="Increase (full)", variable=exp_yield_option_var, value=ExpYieldConfig.INCREASE_FULL.value, state="disabled")
exp_yield_full_tooltip = CreateToolTip(exp_yield_full_rb, "Adjusts wild Digimon exp to match progression with full increase.\nExp is calculated using Pokémon's formula: base_exp * level / 7, where base_exp depends on evolution stage and level is the encounter level.\nFor reference, a lvl 33 wild Greymon's exp yield increases from 71 to 566 points.")
exp_yield_full_rb.pack(anchor="w")


'''
# QoL Slider for Movement Speed Multiplier
tk.Label(qol_frame, text="Movement Speed Multiplier:").pack(anchor='w')
movement_speed_multiplier = tk.DoubleVar(value=1.5)
tk.Scale(qol_frame, from_=0.5, to=3.0, orient="horizontal", resolution=0.5,
         variable=movement_speed_multiplier).pack(fill="x")
'''
         


# Randomization Settings Tab
randomizer_tab = ttk.Frame(notebook, padding=10)
randomizer_tab.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(randomizer_tab, text="Randomization Settings")


# Starters frame
starters_frame = ttk.LabelFrame(randomizer_tab, text="Starter Packs", padding=10)
starters_frame.pack(side="top", fill="x", padx=10, pady=5)


starters_radio_frame = ttk.Frame(starters_frame)
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


starters_misc_frame = ttk.Frame(starters_frame)
starters_misc_frame.pack(side="left", fill="both", expand=True, padx=10)

nerf_first_boss_var = tk.BooleanVar(value=False)
nerfFirstBossCheckbox = tk.Checkbutton(starters_misc_frame, text="Nerf First Boss", variable=nerf_first_boss_var, state="disabled")
nerfFirstBossCheckbox.pack(anchor='w')
nerfFirstBossTootip = CreateToolTip(nerfFirstBossCheckbox, "Enabling this option reduces the total HP of the first boss (virus that attacks the city) by half.\nThis fight usually relies on the lvl 20 Coronamon / Lunamon to be cleared. \nThis option is recommended if randomizing the starter packs, as any other digimon will be set to rookies at lvl 1 (even the digimon that are already rookies).")


# Right side: Rookie Reset Event

rookie_reset_frame = ttk.LabelFrame(starters_frame, text="Rookie Reset Event", padding=10)
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


# Wild digimon frame

wild_digimon_frame = ttk.LabelFrame(randomizer_tab, text="Wild Digimon", padding=10)
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

wild_digimon_sub_frame = ttk.Frame(wild_digimon_inner_container)
wild_digimon_sub_frame.pack(side="left", fill="both", expand=True, padx=10)


wild_digimon_exclude_calumon_var = tk.BooleanVar(value=True)
wildDigimonExcludeCalumonCheckbox = tk.Checkbutton(wild_digimon_sub_frame, text="Exclude Calumon", variable=wild_digimon_exclude_calumon_var, state="disabled")
wildDigimonExcludeCalumonCheckbox.pack(anchor='w')
wildDigimonExcludeCalumonTooltip = CreateToolTip(wildDigimonExcludeCalumonCheckbox, "Excludes Calumon from the wild digimon pool.\nWhile Calumon is an In-Training digimon, its stats are equivalent to the stats of a Mega.\nExcluding Calumon from the wild digimon pool avoids situations where a player would struggle to defeat (or run from) Calumon encounters.")




# Right side: Stat Generation frame
stat_gen_frame = ttk.LabelFrame(wild_digimon_inner_container, text="Stat Generation", padding=10)
stat_gen_frame.pack(side="right", fill="y", padx=10, pady=5)

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



# Digivolutions frame

general_digivolution_settings_frame = ttk.Frame(randomizer_tab)
general_digivolution_settings_frame.pack(side="top", fill="x")

digivolutions_frame = ttk.LabelFrame(general_digivolution_settings_frame, text="Digivolutions", padding=10)
digivolutions_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

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
digivolutionSimilarSpeciesCheckbox.pack(anchor='w')
digivolutionSimilarSpeciesTootip = CreateToolTip(digivolutionSimilarSpeciesCheckbox, "Digivolutions will be more likely to follow the digimon's original species.\nExample: a holy digimon will be more likely to evolve into other holy digimon.")


# Digivolution conditions randomization

digivolution_conditions_frame = ttk.LabelFrame(general_digivolution_settings_frame, text="Digivolution Conditions", padding=10)
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



# Overworld Items Frame
overworld_items_frame = ttk.LabelFrame(randomizer_tab, text="Overworld Items", padding=10)
overworld_items_frame.pack(side="top", fill="x", padx=10, pady=5)


overworld_items_radio_frame = ttk.Frame(overworld_items_frame)
overworld_items_radio_frame.pack(side="left", fill="both", expand=True, padx=10)

overworld_items_option_var = tk.IntVar(value=RandomizeOverworldItems.UNCHANGED.value)

overworld_items_unchanged_rb = tk.Radiobutton(overworld_items_radio_frame, text="Unchanged", variable=overworld_items_option_var, value=RandomizeOverworldItems.UNCHANGED.value, state="disabled")
overworld_items_unchanged_rb.pack(anchor="w")

overworld_items_same_category_rb = tk.Radiobutton(overworld_items_radio_frame, text="Random (same category)", variable=overworld_items_option_var, value=RandomizeOverworldItems.RANDOMIZE_KEEP_CATEGORY.value, state="disabled")
overworld_items_same_category_rb_tooltip = CreateToolTip(overworld_items_same_category_rb, "Randomizes each overworld item chest while keeping the original category of the item (for example, a consumable like a GateDisk will be replaced by another consumable, farm items will be replaced by other farm items, etc).\nNOTE: Key items are not included in the randomization pool, and chests that contain key items are not randomized.")
overworld_items_same_category_rb.pack(anchor="w")

overworld_items_completely_random_rb = tk.Radiobutton(overworld_items_radio_frame, text="Random (completely)", variable=overworld_items_option_var, value=RandomizeOverworldItems.RANDOMIZE_COMPLETELY.value, state="disabled")
overworld_items_completely_random_tooltip = CreateToolTip(overworld_items_completely_random_rb, "Randomizes each overworld item chest completely (a chest can have any item, regardless of its original item).\nNOTE: Key items are not included in the randomization pool, and chests that contain key items are not randomized.")
overworld_items_completely_random_rb.pack(anchor="w")






# Apply buttons at the bottom
button_frame = tk.Frame(root, pady=10)
button_frame.pack()


# Run the Tkinter event loop
root.mainloop()