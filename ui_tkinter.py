import tkinter as tk
from tkinter import ttk


def open_file_function():
    # Code to open a file
    pass

def save_file_function():
    # Code to save a file
    pass

def show_about_info():
    # Code to show "About" information
    pass
        


# Initialize main window
root = tk.Tk()
root.title("DWDD QoL Patcher")
root.geometry("400x600")
root.iconbitmap("puttimon_transparent.ico")

# Create the menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# Add items to File menu
file_menu.add_command(label="Open File...", command=open_file_function)
file_menu.add_command(label="Save", command=save_file_function)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Add Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Add items to Help menu
help_menu.add_command(label="About", command=show_about_info)

# Create a Notebook widget to hold the tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# QoL Changes Tab
qol_frame = ttk.Frame(notebook, padding=10)
qol_frame.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(qol_frame, text="QoL Changes")

# QoL Checkbuttons
change_text_speed_var = tk.BooleanVar(value=True)
tk.Checkbutton(qol_frame, text="Change Text Speed", variable=change_text_speed_var).pack(anchor='w')

change_movement_speed_var = tk.BooleanVar(value=True)
tk.Checkbutton(qol_frame, text="Change Movement Speed", variable=change_movement_speed_var).pack(anchor='w')

# Extra QoL Checkbuttons
change_wild_encounter_rate_var = tk.BooleanVar(value=True)
tk.Checkbutton(qol_frame, text="Change Wild Encounter Rate", variable=change_wild_encounter_rate_var).pack(anchor='w')

increase_stat_caps_var = tk.BooleanVar(value=True)
tk.Checkbutton(qol_frame, text="Increase Stat Caps", variable=increase_stat_caps_var).pack(anchor='w')

# QoL Slider for Movement Speed Multiplier
tk.Label(qol_frame, text="Movement Speed Multiplier:").pack(anchor='w')
movement_speed_multiplier = tk.DoubleVar(value=1.5)
tk.Scale(qol_frame, from_=0.5, to=3.0, orient="horizontal", resolution=0.5,
         variable=movement_speed_multiplier).pack(fill="x")

# Randomization Settings Tab
random_frame = ttk.Frame(notebook, padding=10)
random_frame.pack(fill="both", expand=True)  # Ensure frame fills space
notebook.add(random_frame, text="Randomization Settings")

# Dropdown for Rookie Reset Config
tk.Label(random_frame, text="Rookie Reset Config:").pack(anchor='w')
rookie_reset_options = ["UNCHANGED", "RESET_ALL_INCLUDING_LUNAMON", "RESET_KEEPING_EVO", "DO_NOT_RESET"]
rookie_reset_var = tk.StringVar(value=rookie_reset_options[0])
ttk.OptionMenu(random_frame, rookie_reset_var, *rookie_reset_options).pack(fill="x")

# Dropdown for Randomize Starters Config
tk.Label(random_frame, text="Randomize Starters Config:").pack(anchor='w')
starter_randomize_options = ["UNCHANGED", "RAND_SAME_STAGE", "RAND_FULL"]
starter_randomize_var = tk.StringVar(value=starter_randomize_options[0])
ttk.OptionMenu(random_frame, starter_randomize_var, *starter_randomize_options).pack(fill="x")

# Function to apply QoL changes
def apply_qol_changes():
    # Replace this with calls to executeQolChanges or related methods
    print("QoL changes applied:")
    print(" - Change Text Speed:", change_text_speed_var.get())
    print(" - Change Movement Speed:", change_movement_speed_var.get())
    print(" - Movement Speed Multiplier:", movement_speed_multiplier.get())
    print(" - Change Wild Encounter Rate:", change_wild_encounter_rate_var.get())
    print(" - Increase Stat Caps:", increase_stat_caps_var.get())

# Function to apply randomization settings
def apply_randomization():
    # Replace with calls to Randomizer class methods
    print("Randomization applied:")
    print(" - Rookie Reset Config:", rookie_reset_var.get())
    print(" - Starter Randomize Config:", starter_randomize_var.get())

# Apply buttons at the bottom
button_frame = tk.Frame(root, pady=10)
button_frame.pack()

tk.Button(button_frame, text="Apply QoL Changes", command=apply_qol_changes).pack(side="left", padx=10)
tk.Button(button_frame, text="Apply Randomization", command=apply_randomization).pack(side="left", padx=10)

# Exit button
tk.Button(button_frame, text="Exit", command=root.quit).pack(side="left", padx=10)

# Run the Tkinter event loop
root.mainloop()