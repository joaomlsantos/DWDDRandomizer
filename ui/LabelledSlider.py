import tkinter as tk
from tkinter import ttk

class LabelledSlider(ttk.Frame):
    def __init__(
        self,
        master=None,
        label_text="Slider",
        from_=0.0,
        to=1.0,
        step=0.1,
        default=0.5,
        length=200,
        format_str="{:.1f}",
        show_ticks=True,
        tick_char='│',
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.from_ = from_
        self.to = to
        self.step = step
        self.length = length
        self.format_str = format_str
        self.show_ticks = show_ticks
        self.tick_char = tick_char
        self.variable = tk.DoubleVar(value=default)

        # Title label
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(anchor="w")

        # Current value display
        self.value_label = ttk.Label(self, text=self.format_str.format(default))
        self.value_label.pack(anchor="w", padx=2)

        # Scale
        self.scale = ttk.Scale(
            self,
            from_=from_,
            to=to,
            orient="horizontal",
            variable=self.variable,
            command=self.update_value_label,
            length=self.length
        )
        self.scale.pack(anchor="w", padx=2)

        # Min/Max labels
        minmax_frame = ttk.Frame(self)
        minmax_frame.pack(fill="x", padx=2)
        ttk.Label(minmax_frame, text=self.format_str.format(from_)).pack(side="left")
        ttk.Label(minmax_frame, text=self.format_str.format(to)).pack(side="right")


    def update_value_label(self, val):
        self.value_label.config(text=self.format_str.format(float(val)))

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)
        self.update_value_label(value)

    def disable(self):
        self.scale.state(["disabled"])

    def enable(self):
        self.scale.state(["!disabled"])

    def get_variable(self):
        return self.variable