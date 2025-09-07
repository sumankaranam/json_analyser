import tkinter as tk
import logging

class TextLogger(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, f"{msg}\n")
        self.text_widget.see(tk.END)
