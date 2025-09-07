import tkinter as tk
from tkinter import ttk
from ..utils.image_handler import ImageHandler
import sqlite3
import os

class GroupViewer(ttk.LabelFrame):
    def __init__(self, parent, group_id, db_path):
        super().__init__(parent, text=f"Group {group_id}", padding=10)
        self.group_id = group_id
        self.db_path = db_path
        self.image_handler = ImageHandler()
        self.thumbnails = []  # Keep reference to prevent garbage collection
        self.create_widgets()
        self.load_images()

    def create_widgets(self):
        self.create_image_container()

    def create_image_container(self):
        # Create scrollable container for images
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        
        # Create horizontal scrolling canvas
        self.canvas = tk.Canvas(container, height=250)
        scrollbar = ttk.Scrollbar(container, orient="horizontal", 
                                command=self.canvas.xview)
        
        self.image_frame = ttk.Frame(self.canvas)
        self.image_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.image_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="top", fill="both", expand=True)
        scrollbar.pack(side="bottom", fill="x")

    def load_images(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            files = cursor.execute("""
                SELECT filepath, duplicate_flag, file_id 
                FROM all_groups 
                WHERE group_id = ?
                ORDER BY file_id
            """, (self.group_id,)).fetchall()
            
            conn.close()

            for filepath, is_duplicate, file_id in files:
                self.add_image_frame(filepath, is_duplicate)
                
        except Exception as e:
            print(f"Error loading images for group {self.group_id}: {e}")

    def add_image_frame(self, filepath, is_duplicate):
        try:
            frame = ttk.Frame(self.image_frame)
            frame.pack(side="left", padx=5, pady=5)
            
            # Create thumbnail
            photo = self.image_handler.create_thumbnail(filepath)
            self.thumbnails.append(photo)  # Keep reference
            
            # Image label
            label = ttk.Label(frame, image=photo, cursor="hand2")
            label.pack(pady=2)
            
            # Bind events
            label.bind('<Button-1>', lambda e: self.image_handler.open_image(filepath))
            label.bind('<Enter>', lambda e: self.show_tooltip(label, filepath))
            label.bind('<Leave>', lambda e: self.hide_tooltip())
            label.bind('<Button-3>', lambda e: self.show_context_menu(e, filepath))
            
            # Status label
            status = 'Original' if not is_duplicate else 'Duplicate'
            status_color = '#4CAF50' if not is_duplicate else '#666666'
            
            ttk.Label(
                frame,
                text=status,
                foreground=status_color,
                font=("Helvetica", 9, "bold")
            ).pack()
            
            # Filename label
            ttk.Label(
                frame,
                text=os.path.basename(filepath),
                wraplength=140,
                font=("Helvetica", 8)
            ).pack()
            
            if not is_duplicate:
                frame.configure(style='Original.TFrame')
                
        except Exception as e:
            print(f"Error adding image frame for {filepath}: {e}")

    def show_tooltip(self, widget, text):
        x = y = 0
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20

        # Creates a toplevel window
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def show_context_menu(self, event, filepath):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copy Path", 
                        command=lambda: self.copy_to_clipboard(filepath))
        menu.tk_popup(event.x_root, event.y_root)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
