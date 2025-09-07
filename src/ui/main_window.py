import tkinter as tk
from tkinter import ttk
import ttkthemes
from .analyze_frame import AnalyzeFrame
from .view_frame import ViewFrame

class XMLAnalyzerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XML Duplicate Analyzer")
        self.setup_theme()
        self.setup_variables()
        self.create_widgets()

    def setup_theme(self):
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")
        self.configure_styles()

    def setup_variables(self):
        self.mode = tk.StringVar(value="analyze")

    def configure_styles(self):
        self.style.configure(
            'Action.TButton',
            background='#2196F3',
            foreground='#000000',
            font=('Helvetica', 11, 'bold'),
            padding=10
        )
        self.style.configure(
            "Horizontal.TProgressbar",
            troughcolor='#f0f0f0',
            background='#2196F3',
            thickness=25
        )
        self.style.configure(
            'Original.TFrame',
            background='#E3F2FD',
            relief="solid",
            borderwidth=2
        )

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)

        self.create_mode_selection(main_frame)
        self.analyze_frame = AnalyzeFrame(main_frame)
        self.view_frame = ViewFrame(main_frame)
        self.switch_mode()

    def create_mode_selection(self, parent):
        mode_frame = ttk.LabelFrame(parent, text="Mode Selection", padding=15)
        mode_frame.pack(fill="x", pady=(0, 10))

        ttk.Radiobutton(
            mode_frame, 
            text="Analyze XML", 
            variable=self.mode, 
            value="analyze",
            command=self.switch_mode
        ).pack(side="left", padx=10)

        ttk.Radiobutton(
            mode_frame, 
            text="View Duplicates", 
            variable=self.mode, 
            value="view",
            command=self.switch_mode
        ).pack(side="left", padx=10)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
