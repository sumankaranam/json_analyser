import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .components.group_viewer import GroupViewer
import sqlite3

class ViewFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_variables()
        self.create_widgets()

    def setup_variables(self):
        self.db_path_view = tk.StringVar()
        self.current_page = 0
        self.groups_per_page = 3  # Changed from 5 to 3
        self.total_pages = 0
        self.groups = []

    def create_widgets(self):
        # Database selection frame
        self.create_db_selection()
        
        # Navigation frame
        self.create_navigation()
        
        # Create main scrollable container for groups
        self.create_groups_container()

    def create_groups_container(self):
        # Create main container frame
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill="both", expand=True)
        
        # Create canvas with fixed height and scrollbar
        self.canvas = tk.Canvas(
            self.main_container,
            bg='#f0f0f0',
            height=600,  # Fixed height to ensure scroll works
            highlightthickness=0  # Remove border
        )
        self.scrollbar = ttk.Scrollbar(
            self.main_container,
            orient="vertical",
            command=self.canvas.yview
        )
        
        # Create frame to hold groups
        self.groups_container = ttk.Frame(self.canvas)
        
        # Pack scrollbar and canvas
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.groups_container,
            anchor="nw",
            width=self.canvas.winfo_reqwidth()
        )
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind events
        self.groups_container.bind(
            "<Configure>",
            self._on_frame_configure
        )
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )
        
        # Bind mouse wheel scrolling
        self.bind_mouse_wheel()

    def bind_mouse_wheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta/120)), "units")
        
        # Bind to canvas and groups container
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _on_frame_configure(self, event):
        """Reset the scroll region when the frame changes size"""
        # Update the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Update the groups container width when canvas changes size"""
        # Update the width of the window to fit the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def create_db_selection(self):
        db_select_frame = ttk.LabelFrame(self, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Entry(
            db_select_frame, 
            textvariable=self.db_path_view, 
            width=80
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ttk.Button(
            db_select_frame,
            text="Browse DB",
            command=self.browse_db,
            style='Action.TButton'
        ).pack(side="left")
        
        ttk.Button(
            db_select_frame,
            text="Load Duplicates",
            command=self.load_duplicates,
            style='Action.TButton'
        ).pack(side="left", padx=10)

    def create_navigation(self):
        nav_container = ttk.LabelFrame(self, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
        # Navigation controls
        self.create_navigation_controls(nav_frame)

    def create_navigation_controls(self, nav_frame):
        # Left side navigation
        nav_left = ttk.Frame(nav_frame)
        nav_left.pack(side="left")
        
        self.prev_btn = ttk.Button(
            nav_left, 
            text="← Previous",
            command=self.prev_page,
            state="disabled",
            style='Action.TButton'
        )
        self.prev_btn.pack(side="left", padx=5)
        
        # Center navigation
        nav_center = ttk.Frame(nav_frame)
        nav_center.pack(side="left", expand=True, padx=20)
        
        self.page_label = ttk.Label(
            nav_center,
            text="Page: 0/0",
            font=("Helvetica", 12, "bold")
        )
        self.page_label.pack(side="left", padx=10)
        
        # Group navigation
        self.create_goto_controls(nav_center)
        
        # Right side navigation
        nav_right = ttk.Frame(nav_frame)
        nav_right.pack(side="right")
        
        self.next_btn = ttk.Button(
            nav_right,
            text="Next →",
            command=self.next_page,
            state="disabled",
            style='Action.TButton'
        )
        self.next_btn.pack(side="right", padx=5)

    def create_goto_controls(self, parent):
        # Group navigation
        ttk.Label(parent, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(parent, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            parent,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation
        ttk.Label(parent, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(parent, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            parent,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)

    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Add groups to the container
        for group in self.groups[start_idx:end_idx]:
            group_viewer = GroupViewer(self.groups_container, group[0], self.db_path_view.get())
            group_viewer.pack(fill="x", pady=5, padx=5)
        
        # Important: Update scroll region after adding groups
        self.groups_container.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.update_navigation()

    def update_navigation(self):
        self.page_label.config(text=f"Page: {self.current_page + 1}/{self.total_pages}")
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")

    def browse_db(self):
        filename = filedialog.askopenfilename(
            title="Select Database File",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        if filename:
            self.db_path_view.set(filename)

    def load_duplicates(self):
        if not self.db_path_view.get():
            messagebox.showerror("Error", "Please select a database file")
            return
        
        try:
            conn = sqlite3.connect(self.db_path_view.get())
            cursor = conn.cursor()
            
            self.groups = cursor.execute("""
                SELECT DISTINCT group_id 
                FROM all_groups 
                WHERE duplicate_flag = 0
                ORDER BY group_id
            """).fetchall()
            
            conn.close()
            
            if not self.groups:
                messagebox.showinfo("Info", "No duplicate groups found")
                return
            
            self.current_page = 0
            self.total_pages = (len(self.groups) + self.groups_per_page - 1) // self.groups_per_page
            self.load_current_page()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")

    def goto_specific_group(self):
        try:
            group_id = int(self.goto_group.get())
            if group_id in [g[0] for g in self.groups]:
                group_index = [g[0] for g in self.groups].index(group_id)
                self.current_page = group_index // self.groups_per_page
                self.load_current_page()
            else:
                messagebox.showerror("Error", "Group ID not found")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid group number")

    def goto_specific_page(self):
        try:
            page = int(self.goto_page.get()) - 1
            if 0 <= page < self.total_pages:
                self.current_page = page
                self.load_current_page()
            else:
                messagebox.showerror("Error", "Page number out of range")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number")

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_current_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_current_page()
