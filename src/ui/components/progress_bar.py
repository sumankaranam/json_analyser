import tkinter as tk
from tkinter import ttk

class ProgressBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        # Progress status frame
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", pady=(0, 5))

        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=("Helvetica", 10),
            foreground='#666666'
        )
        self.status_label.pack(side="left")

        self.progress_label = ttk.Label(
            status_frame,
            text="0%",
            font=("Helvetica", 12, "bold"),
            foreground='#2196F3'
        )
        self.progress_label.pack(side="right")

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=5)

    def update_progress(self, value):
        """Update progress bar and labels"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        self.status_label.config(
            text="Processing..." if value < 100 else "Completed",
            foreground='#2196F3' if value < 100 else '#4CAF50'
        )

    def reset(self):
        """Reset progress bar to initial state"""
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.status_label.config(text="Ready", foreground='#666666')