import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from xml_analyzer import XMLFlattener
import threading
import logging
import ttkthemes
from PIL import Image, ImageTk
import sqlite3
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLAnalyzerUI:
    def __init__(self, root):
        self.root = root
        # Apply material theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        # Variables
        self.xml_path = tk.StringVar()
        self.db_path = tk.StringVar(value="xml_data.db")
        self.progress_var = tk.DoubleVar()
        self.mode = tk.StringVar(value="analyze")
        self.processing = False
        
        # Initialize image display variables
        self.image_labels = []
        self.thumbnails = []
        self.current_group_index = 0
        self.groups = []
        
        # Pagination variables
        self.groups_per_page = 5
        self.current_page = 0
        self.total_pages = 0
        
        # Add scrolling attributes
        self.main_canvas = None
        self.scrollable_frame = None
        
        # Configure styles
        self.style.configure(
            'Action.TButton',
            background='#2196F3',
            foreground='#000000',
            font=('Helvetica', 11, 'bold'),
            padding=10
        )
        
        # Configure progress bar style
        self.style.configure(
            "Horizontal.TProgressbar",
            troughcolor='#f0f0f0',
            background='#2196F3',
            thickness=25
        )
        
        # Configure styles for image frames
        self.style.configure(
            'Original.TFrame',
            background='#E3F2FD',
            relief="solid",
            borderwidth=2
        )
        
        # Create right-click menu
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)
        
        # Store current filepath for context menu
        self.current_filepath = None

        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Mode Selection", padding=15)
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
        
        # Create analyze frame
        self.analyze_frame = ttk.Frame(main_frame)
        
        # File Selection Frame in analyze_frame
        file_frame = ttk.LabelFrame(self.analyze_frame, text="File Selection", padding=15)
        file_frame.pack(fill="x", pady=(0, 10))
        
        file_content = ttk.Frame(file_frame)
        file_content.pack(fill="x", expand=True)
        
        ttk.Label(file_content, text="XML File:", font=("Helvetica", 10)).pack(anchor="w")
        file_entry = ttk.Entry(file_content, textvariable=self.xml_path, width=80)
        file_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        browse_btn = ttk.Button(
            file_content, 
            text="Browse XML",
            command=self.browse_xml,
            style='Action.TButton',
            width=15
        )
        browse_btn.pack(side="right", padx=5)
        
        # Database Configuration Frame in analyze_frame
        db_frame = ttk.LabelFrame(self.analyze_frame, text="Database Configuration", padding=15)
        db_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(db_frame, text="Database Name:", font=("Helvetica", 10)).pack(anchor="w")
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path, width=80)
        db_entry.pack(fill="x")
        
        # Process Button Frame in analyze_frame
        button_frame = ttk.Frame(self.analyze_frame, padding=15)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.process_button = ttk.Button(
            button_frame, 
            text="Process XML",
            command=self.process_xml,
            style='Action.TButton',
            width=20
        )
        self.process_button.pack(pady=10)
        
        # Progress Frame in analyze_frame
        progress_frame = ttk.LabelFrame(self.analyze_frame, text="Progress", padding=15)
        progress_frame.pack(fill="both", expand=True)
        
        self.progress_label = ttk.Label(
            progress_frame, 
            text="0%",
            font=("Helvetica", 12, "bold"),
            foreground='#2196F3'
        )
        self.progress_label.pack(side="right")
        
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=("Helvetica", 10),
            foreground='#666666'
        )
        self.status_label.pack(side="left")
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style="Horizontal.TProgressbar"
        )
        self.progress_bar.pack(fill="x", pady=10)
        
        # Log Text Area in analyze_frame
        self.log_text = tk.Text(
            progress_frame, 
            height=15,
            wrap=tk.WORD,
            bg='#ffffff',
            fg='#333333',
            font=("Consolas", 10),
            pady=10,
            border=1,
            relief="solid"
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Create view frame and its widgets
        self.view_frame = ttk.Frame(main_frame)
        self.create_view_widgets()
        
        # Show initial mode
        self.switch_mode()
    
    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def create_view_widgets(self):
        # Database selection
        db_select_frame = ttk.LabelFrame(self.view_frame, text="Database Selection", padding=15)
        db_select_frame.pack(fill="x", pady=(0, 10))
        
        self.db_path_view = tk.StringVar()
        ttk.Entry(db_select_frame, textvariable=self.db_path_view, width=80).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
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
        
        # Navigation controls
        nav_container = ttk.LabelFrame(self.view_frame, text="Navigation", padding=15)
        nav_container.pack(fill="x", pady=(0, 10))
        
        nav_frame = ttk.Frame(nav_container)
        nav_frame.pack(fill="x")
        
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
        
        # Group navigation entry
        ttk.Label(nav_center, text="Go to Group:").pack(side="left", padx=5)
        self.goto_group = ttk.Entry(nav_center, width=10)
        self.goto_group.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_group,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
        # Page navigation entry
        ttk.Label(nav_center, text="Go to Page:").pack(side="left", padx=5)
        self.goto_page = ttk.Entry(nav_center, width=10)
        self.goto_page.pack(side="left", padx=5)
        
        ttk.Button(
            nav_center,
            text="Go",
            command=self.goto_specific_page,
            style='Action.TButton'
        ).pack(side="left", padx=5)
        
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
        
        # Groups container
        self.groups_container = ttk.Frame(self.view_frame)
        self.groups_container.pack(fill="both", expand=True)

    def switch_mode(self):
        if self.mode.get() == "analyze":
            self.view_frame.pack_forget()
            self.analyze_frame.pack(fill="both", expand=True)
        else:
            self.analyze_frame.pack_forget()
            self.view_frame.pack(fill="both", expand=True)
    
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
    
    def load_current_page(self):
        # Clear existing groups
        for widget in self.groups_container.winfo_children():
            widget.destroy()
        
        start_idx = self.current_page * self.groups_per_page
        end_idx = min(start_idx + self.groups_per_page, len(self.groups))
        
        # Create a canvas for each group in the current page
        for i, group in enumerate(self.groups[start_idx:end_idx]):
            group_frame = ttk.LabelFrame(
                self.groups_container, 
                text=f"Group {group[0]}", 
                padding=10
            )
            group_frame.pack(fill="x", pady=5)
            self.load_group_images(group[0], parent=group_frame)
        
        self.update_navigation()

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

    def copy_path(self):
        """Copy filepath to clipboard"""
        if self.current_filepath:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_filepath)

    def show_tooltip(self, widget, text):
        """Show tooltip with filepath"""
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip, text=text, justify='left',
                          background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        """Hide tooltip window"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()

    def show_context_menu(self, event, filepath):
        """Show right-click context menu"""
        self.current_filepath = filepath
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def open_image(self, filepath):
        """Open image in default system viewer"""
        try:
            import platform
            import subprocess
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(filepath)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            logger.error(f"Failed to open image {filepath}: {str(e)}")
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")

    def load_group_images(self, group_id, parent=None):
        try:
            if parent is None:
                return
                
            conn = sqlite3.connect(self.db_path_view.get())
            cursor = conn.cursor()
            
            # Get all files in the group
            files = cursor.execute("""
                SELECT filepath, duplicate_flag, file_id 
                FROM all_groups 
                WHERE group_id = ?
                ORDER BY file_id
            """, (group_id,)).fetchall()
            
            conn.close()
            
            # Create scrollable frame for images
            canvas = tk.Canvas(parent, bg='#f0f0f0', height=250)
            scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
            image_container = ttk.Frame(canvas)
            
            canvas.configure(xscrollcommand=scrollbar.set)
            
            # Create frame to hold all images in a horizontal layout
            for i, (filepath, is_duplicate, file_id) in enumerate(files):
                try:
                    # Create frame for each image
                    frame = ttk.Frame(image_container)
                    frame.pack(side="left", padx=5, pady=5)
                    
                    try:
                        # Create thumbnail
                        image = Image.open(filepath)
                        image.thumbnail((150, 150))
                        photo = ImageTk.PhotoImage(image)
                        
                        # Keep reference to prevent garbage collection
                        frame.photo = photo
                        
                        # Image label with events
                        label = ttk.Label(frame, image=photo, cursor="hand2")
                        label.pack(pady=2)
                        
                        # Bind events
                        label.bind('<Enter>', lambda e, path=filepath: self.show_tooltip(label, path))
                        label.bind('<Leave>', lambda e: self.hide_tooltip())
                        label.bind('<Button-3>', lambda e, path=filepath: self.show_context_menu(e, path))
                        label.bind('<Button-1>', lambda e, path=filepath: self.open_image(path))
                        
                        # Add colored border for original
                        if not is_duplicate:
                            frame.configure(style='Original.TFrame')
                        
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
                        
                    except (IOError, OSError) as e:
                        # Handle missing or invalid image
                        error_frame = ttk.Frame(frame, padding=10)
                        error_frame.pack(fill="both", expand=True)
                        ttk.Label(
                            error_frame,
                            text="⚠️\nImage not found",
                            foreground='red',
                            font=("Helvetica", 9)
                        ).pack()
                        ttk.Label(
                            error_frame,
                            text=os.path.basename(filepath),
                            wraplength=140,
                            font=("Helvetica", 8)
                        ).pack()
                        
                except Exception as e:
                    logger.error(f"Failed to process thumbnail for {filepath}: {str(e)}")
        
            # Configure canvas with scrolling
            canvas.create_window((0, 0), window=image_container, anchor="nw")
            image_container.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            # Pack canvas and scrollbar
            canvas.pack(side="top", fill="both", expand=True)
            scrollbar.pack(side="bottom", fill="x")
            
        except Exception as e:
            logger.error(f"Failed to load group images: {str(e)}")
            messagebox.showerror("Error", f"Failed to load group images: {str(e)}")
    
    def prev_group(self):
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self.load_group_images(self.groups[self.current_group_index][0])
            self.update_navigation()
    
    def next_group(self):
        if self.current_group_index < len(self.groups) - 1:
            self.current_group_index += 1
            self.load_group_images(self.groups[self.current_group_index][0])
            self.update_navigation()
    
    def update_navigation(self):
        self.page_label.config(text=f"Page: {self.current_page + 1}/{self.total_pages}")
        self.prev_btn.config(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current_page < self.total_pages - 1 else "disabled")
    
    def update_progress(self, current, total):
        """Update progress bar with current progress"""
        if total > 0:
            percentage = (current / total) * 100
            self.root.after(0, lambda: self._update_progress_ui(percentage))

    def _update_progress_ui(self, value):
        """Update UI elements with progress value"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        self.status_label.config(
            text="Processing..." if value < 100 else "Completed",
            foreground='#2196F3' if value < 100 else '#4CAF50'
        )
        
    def browse_xml(self):
        filename = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.xml_path.set(filename)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def process_xml(self):
        if not self.xml_path.get():
            messagebox.showerror("Error", "Please select an XML file")
            return
            
        if not self.db_path.get():
            messagebox.showerror("Error", "Please enter a database name")
            return
            
        if self.processing:
            return
            
        self.processing = True
        self.process_button.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, f"{msg}\n")
                self.text_widget.see(tk.END)
    
        logger = logging.getLogger()
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(text_handler)
    
        def process():
            try:
                flattener = XMLFlattener(self.db_path.get())
                flattener.process_large_xml(self.xml_path.get(), self.update_progress)
                
                def success_callback():
                    messagebox.showinfo(
                        "Success", 
                        f"Data successfully processed and stored in {self.db_path.get()}"
                    )
                    self.processing = False
                    self.process_button.config(state="normal")
                    
                self.root.after(0, success_callback)
                
            except Exception as e:
                def error_callback():
                    messagebox.showerror(
                        "Error",
                        f"Failed to process XML: {str(e)}"
                    )
                    self.processing = False
                    self.process_button.config(state="normal")
                    
                self.root.after(0, error_callback)
            finally:
                logger.removeHandler(text_handler)
    
        threading.Thread(target=process, daemon=True).start()

def main():
    root = tk.Tk()
    app = XMLAnalyzerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()