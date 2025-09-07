import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .components.progress_bar import ProgressBar
from .utils.logger import TextLogger
from ..core.xml_processor import XMLFlattener
import threading

class AnalyzeFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_variables()
        self.create_widgets()

    def setup_variables(self):
        self.xml_path = tk.StringVar()
        self.db_path = tk.StringVar(value="xml_data.db")
        self.progress_var = tk.DoubleVar()
        self.processing = False

    def create_widgets(self):
        self.create_file_selection()
        self.create_db_config()
        self.create_process_button()
        self.create_progress_section()

    def create_file_selection(self):
        file_frame = ttk.LabelFrame(self, text="File Selection", padding=15)
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

    def create_db_config(self):
        db_frame = ttk.LabelFrame(self, text="Database Configuration", padding=15)
        db_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(db_frame, text="Database Name:", font=("Helvetica", 10)).pack(anchor="w")
        db_entry = ttk.Entry(db_frame, textvariable=self.db_path, width=80)
        db_entry.pack(fill="x")

    def create_process_button(self):
        button_frame = ttk.Frame(self, padding=15)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.process_button = ttk.Button(
            button_frame, 
            text="Process XML",
            command=self.process_xml,
            style='Action.TButton',
            width=20
        )
        self.process_button.pack(pady=10)

    def create_progress_section(self):
        progress_frame = ttk.LabelFrame(self, text="Progress", padding=15)
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

    def browse_xml(self):
        filename = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.xml_path.set(filename)

    def update_progress(self, current, total):
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"{int(percentage)}%")
            self.status_label.config(
                text="Processing..." if percentage < 100 else "Completed",
                foreground='#2196F3' if percentage < 100 else '#4CAF50'
            )

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
        
        def process():
            try:
                flattener = XMLFlattener(self.db_path.get())
                flattener.process_large_xml(self.xml_path.get(), self.update_progress)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Data successfully processed and stored in {self.db_path.get()}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Failed to process XML: {str(e)}"
                ))
            finally:
                self.processing = False
                self.root.after(0, lambda: self.process_button.config(state="normal"))
        
        threading.Thread(target=process, daemon=True).start()
