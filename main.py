import tkinter as tk
from src.ui.main_window import XMLAnalyzerUI

def main():
    root = tk.Tk()
    root.state('zoomed')  # Start maximized
    app = XMLAnalyzerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
