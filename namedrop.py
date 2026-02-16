#!/usr/bin/env python3
"""
NameDrop - Smart File Renaming Tool
Cross-platform GUI with drag-and-drop, EXIF support, and advanced options.
"""

import os
import sys
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime
from collections import defaultdict

# Try to import tkinterdnd2 for drag-and-drop, fall back to basic functionality
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False
    # Create a dummy TkinterDnD that just returns tk.Tk
    class TkinterDnD:
        @staticmethod
        def Tk():
            return tk.Tk()

# Try to import PIL for EXIF support
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

# Default minor words
DEFAULT_MINOR_WORDS = {
    'a', 'an', 'the',
    'and', 'but', 'or', 'nor', 'for', 'yet', 'so',
    'as', 'at', 'by', 'for', 'from', 'in', 'into', 'of', 'off', 'on',
    'onto', 'out', 'over', 'to', 'up', 'via', 'with',
    'vs'
}

# Default special/reserved characters to replace
DEFAULT_SPECIAL_CHARS = {
    '<', '>', ':', '"', '/', '\\', '|', '?', '*',
    '\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07',
    '\x08', '\x09', '\x0a', '\x0b', '\x0c', '\x0d', '\x0e', '\x0f',
    '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17',
    '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f'
}

# Default datetime format
DEFAULT_DATETIME_FORMAT = "%Y%m%d-%H%M%S"


class FileRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NameDrop")
        self.root.geometry("850x750")
        self.root.minsize(750, 650)
        
        # Data
        self.files = []
        self.minor_words = DEFAULT_MINOR_WORDS.copy()
        self.special_chars = DEFAULT_SPECIAL_CHARS.copy()
        self.datetime_format = DEFAULT_DATETIME_FORMAT
        
        # Variables
        self.case_mode = tk.StringVar(value="title")
        self.use_minor_words = tk.BooleanVar(value=True)
        self.replace_spaces = tk.BooleanVar(value=False)
        self.replace_special = tk.BooleanVar(value=False)
        self.strip_punctuation = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the user interface."""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # File selection area with drag-and-drop
        dnd_text = "Files to Rename (Drag & Drop Supported)" if TKDND_AVAILABLE else "Files to Rename"
        file_frame = ttk.LabelFrame(main_frame, text=dnd_text, padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # Create a frame for drag-and-drop (only if available)
        if TKDND_AVAILABLE:
            self.drop_frame = ttk.Frame(file_frame, relief=tk.SUNKEN, borderwidth=2)
            self.drop_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
            self.drop_frame.columnconfigure(0, weight=1)
            
            # Register drag-and-drop
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            
            drop_label = ttk.Label(self.drop_frame, text="📁 Drag files or folders here", 
                                  font=("TkDefaultFont", 10), foreground="gray")
            drop_label.grid(row=0, column=0, pady=20)
            
            btn_row = 1
        else:
            btn_row = 0
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=btn_row, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT)
        
        self.file_label = ttk.Label(file_frame, text="No files selected")
        self.file_label.grid(row=btn_row+1, column=0, sticky=tk.W)
        
        # Options area
        options_frame = ttk.LabelFrame(main_frame, text="Renaming Options", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)
        
        # Case conversion options
        ttk.Label(options_frame, text="Case Conversion:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        case_frame = ttk.Frame(options_frame)
        case_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(case_frame, text="Title Case", variable=self.case_mode, 
                       value="title", command=self.toggle_mode_options).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(case_frame, text="All Lower Case", variable=self.case_mode, 
                       value="lower", command=self.toggle_mode_options).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(case_frame, text="All Upper Case", variable=self.case_mode, 
                       value="upper", command=self.toggle_mode_options).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(case_frame, text="Date/Time from EXIF", variable=self.case_mode, 
                       value="datetime", command=self.toggle_mode_options).pack(side=tk.LEFT)
        
        # Minor words option (only for title case)
        ttk.Label(options_frame, text="").grid(row=1, column=0)
        
        self.minor_frame = ttk.Frame(options_frame)
        self.minor_frame.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        self.minor_words_check = ttk.Checkbutton(self.minor_frame, text="Use minor words", 
                                                 variable=self.use_minor_words)
        self.minor_words_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.edit_minor_btn = ttk.Button(self.minor_frame, text="Edit Minor Words", 
                                         command=self.edit_minor_words)
        self.edit_minor_btn.pack(side=tk.LEFT)
        
        # Space/Punctuation options (only for lower/upper case)
        self.case_options_frame = ttk.Frame(options_frame)
        self.case_options_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(self.case_options_frame, text="Replace spaces with underscores", 
                       variable=self.replace_spaces).pack(anchor=tk.W)
        
        ttk.Checkbutton(self.case_options_frame, text="Strip punctuation and non-alphanumeric", 
                       variable=self.strip_punctuation).pack(anchor=tk.W, pady=(5, 0))
        
        # DateTime format option (only for datetime mode)
        self.datetime_frame = ttk.Frame(options_frame)
        self.datetime_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.datetime_frame, text=f"Format: {self.datetime_format}").pack(side=tk.LEFT, padx=(0, 10))
        
        self.edit_datetime_btn = ttk.Button(self.datetime_frame, text="Edit DateTime Format", 
                                           command=self.edit_datetime_format)
        self.edit_datetime_btn.pack(side=tk.LEFT)
        
        if not EXIF_AVAILABLE:
            ttk.Label(self.datetime_frame, text="(PIL not installed - EXIF unavailable)", 
                     foreground="orange", font=("TkDefaultFont", 8)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Initially hide mode-specific options
        self.case_options_frame.grid_remove()
        self.datetime_frame.grid_remove()
        
        # Separator
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2, 
                                                                sticky=(tk.W, tk.E), pady=10)
        
        # Character replacement options (special characters only now)
        ttk.Label(options_frame, text="Character Replacement:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        replace_frame = ttk.Frame(options_frame)
        replace_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        special_frame = ttk.Frame(replace_frame)
        special_frame.pack(anchor=tk.W)
        
        ttk.Checkbutton(special_frame, text="Replace special/reserved characters", 
                       variable=self.replace_special).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(special_frame, text="Edit Special Characters", 
                  command=self.edit_special_chars).pack(side=tk.LEFT)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=2, column=0, pady=(0, 10))
        
        ttk.Button(action_frame, text="Preview Changes", command=self.preview_changes, 
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Convert Files", command=self.convert_files, 
                  width=20).pack(side=tk.LEFT)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        # Debug/Output pane
        output_frame = ttk.LabelFrame(main_frame, text="Output / Debug Messages", padding="5")
        output_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=12, wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("info", foreground="blue")
        self.output_text.tag_config("warning", foreground="orange")
        
        self.log_message("Ready to rename files. Add files to get started.", "info")
        if not EXIF_AVAILABLE:
            self.log_message("Note: PIL/Pillow not installed. EXIF date extraction unavailable.", "warning")
        if not TKDND_AVAILABLE:
            self.log_message("Note: tkinterdnd2 not installed. Drag-and-drop unavailable. Use Add Files/Folder buttons.", "warning")
        
    def on_drop(self, event):
        """Handle drag and drop of files."""
        # Parse dropped files (tkinterdnd2 returns a string)
        files = self.root.tk.splitlist(event.data)
        
        added_count = 0
        for item in files:
            item_path = Path(item)
            
            if item_path.is_file():
                if str(item_path) not in self.files:
                    self.files.append(str(item_path))
                    added_count += 1
            elif item_path.is_dir():
                # Add all files from directory
                for file_path in item_path.iterdir():
                    if file_path.is_file():
                        filepath = str(file_path)
                        if filepath not in self.files:
                            self.files.append(filepath)
                            added_count += 1
        
        if added_count > 0:
            self.update_file_label()
            self.log_message(f"Dropped and added {added_count} file(s)", "success")
        
    def toggle_mode_options(self):
        """Enable/disable options based on case mode."""
        mode = self.case_mode.get()
        
        # Hide all mode-specific frames first
        self.minor_frame.grid_remove()
        self.case_options_frame.grid_remove()
        self.datetime_frame.grid_remove()
        
        # Show relevant frame based on mode
        if mode == "title":
            self.minor_frame.grid()
        elif mode in ["lower", "upper"]:
            self.case_options_frame.grid()
        elif mode == "datetime":
            self.datetime_frame.grid()
        
    def log_message(self, message, tag="info"):
        """Add a message to the output pane."""
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        self.output_text.update()
        
    def add_files(self):
        """Open file dialog to select files."""
        filenames = filedialog.askopenfilenames(
            title="Select files to rename",
            filetypes=[("All files", "*.*")]
        )
        if filenames:
            for filename in filenames:
                if filename not in self.files:
                    self.files.append(filename)
            self.update_file_label()
            self.log_message(f"Added {len(filenames)} file(s)", "success")
            
    def add_folder(self):
        """Open folder dialog and add all files from the folder."""
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            count = 0
            for item in Path(folder).iterdir():
                if item.is_file():
                    filepath = str(item)
                    if filepath not in self.files:
                        self.files.append(filepath)
                        count += 1
            self.update_file_label()
            self.log_message(f"Added {count} file(s) from folder", "success")
            
    def clear_files(self):
        """Clear all selected files."""
        self.files.clear()
        self.update_file_label()
        self.log_message("Cleared all files", "info")
        
    def update_file_label(self):
        """Update the file count label."""
        count = len(self.files)
        if count == 0:
            self.file_label.config(text="No files selected")
        elif count == 1:
            self.file_label.config(text="1 file selected")
        else:
            self.file_label.config(text=f"{count} files selected")
            
    def edit_minor_words(self):
        """Open dialog to edit minor words list."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Minor Words")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Minor words (one per line, lowercase):").pack(anchor=tk.W, pady=(0, 5))
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text = scrolledtext.ScrolledText(text_frame, height=15)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(1.0, "\n".join(sorted(self.minor_words)))
        
        def save_words():
            content = text.get(1.0, tk.END)
            words = {word.strip().lower() for word in content.split("\n") if word.strip()}
            self.minor_words = words
            self.log_message(f"Updated minor words list ({len(words)} words)", "success")
            dialog.destroy()
            
        def reset_words():
            text.delete(1.0, tk.END)
            text.insert(1.0, "\n".join(sorted(DEFAULT_MINOR_WORDS)))
            
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Save", command=save_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=reset_words).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def edit_datetime_format(self):
        """Open dialog to edit datetime format."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit DateTime Format")
        dialog.geometry("550x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="DateTime Format String:", font=("TkDefaultFont", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        format_var = tk.StringVar(value=self.datetime_format)
        format_entry = ttk.Entry(frame, textvariable=format_var, width=40, font=("Courier", 10))
        format_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Preview
        preview_frame = ttk.LabelFrame(frame, text="Preview", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        preview_label = ttk.Label(preview_frame, text="", font=("Courier", 10))
        preview_label.pack(anchor=tk.W)
        
        def update_preview(*args):
            try:
                now = datetime.now()
                preview = now.strftime(format_var.get())
                preview_label.config(text=f"Example: {preview}", foreground="green")
            except Exception as e:
                preview_label.config(text=f"Error: {str(e)}", foreground="red")
        
        format_var.trace_add("write", update_preview)
        update_preview()
        
        # Help text
        help_frame = ttk.LabelFrame(frame, text="Format Codes", padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        help_text = scrolledtext.ScrolledText(help_frame, height=10, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """Common format codes:

%Y - Year with century (2024)
%y - Year without century (24)
%m - Month as zero-padded number (01-12)
%d - Day as zero-padded number (01-31)
%H - Hour (24-hour, 00-23)
%I - Hour (12-hour, 01-12)
%M - Minute (00-59)
%S - Second (00-59)
%p - AM/PM
%B - Full month name (January)
%b - Abbreviated month name (Jan)
%A - Full weekday name (Monday)
%a - Abbreviated weekday name (Mon)

Examples:
%Y%m%d-%H%M%S → 20240115-143025
%Y-%m-%d_%H-%M-%S → 2024-01-15_14-30-25
%Y%m%d_%H%M → 20240115_1430
%Y-%m-%d → 2024-01-15
IMG_%Y%m%d_%H%M%S → IMG_20240115_143025"""
        
        help_text.insert(1.0, help_content)
        help_text.config(state=tk.DISABLED)
        
        def save_format():
            try:
                # Test the format
                datetime.now().strftime(format_var.get())
                self.datetime_format = format_var.get()
                self.log_message(f"Updated datetime format: {self.datetime_format}", "success")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Invalid Format", f"Invalid format string:\n{str(e)}")
        
        def reset_format():
            format_var.set(DEFAULT_DATETIME_FORMAT)
            
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Save", command=save_format).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=reset_format).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def edit_special_chars(self):
        """Open dialog to edit special characters list."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Special Characters")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Special characters to replace (one per line):").pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(frame, text="Note: Control characters (\\x00-\\x1f) are included by default", 
                 font=("TkDefaultFont", 8, "italic")).pack(anchor=tk.W, pady=(0, 5))
        
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text = scrolledtext.ScrolledText(text_frame, height=15)
        text.pack(fill=tk.BOTH, expand=True)
        
        # Show printable characters
        printable = [c for c in sorted(self.special_chars) if ord(c) >= 32]
        text.insert(1.0, "\n".join(printable))
        
        def save_chars():
            content = text.get(1.0, tk.END)
            chars = {c for line in content.split("\n") for c in line if c}
            # Always include control characters
            chars.update({chr(i) for i in range(32)})
            self.special_chars = chars
            self.log_message(f"Updated special characters list ({len(chars)} characters)", "success")
            dialog.destroy()
            
        def reset_chars():
            text.delete(1.0, tk.END)
            printable = [c for c in sorted(DEFAULT_SPECIAL_CHARS) if ord(c) >= 32]
            text.insert(1.0, "\n".join(printable))
            
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Save", command=save_chars).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset to Default", command=reset_chars).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def get_exif_datetime(self, filepath):
        """Extract datetime from EXIF data if available."""
        if not EXIF_AVAILABLE:
            return None
            
        try:
            image = Image.open(filepath)
            exif_data = image._getexif()
            
            if exif_data:
                # Look for datetime tags
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Common datetime tags
                    if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                        # EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
                        try:
                            dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                            return dt
                        except:
                            pass
            
            return None
        except:
            return None
    
    def get_file_datetime(self, filepath):
        """Get datetime for file - from EXIF or file modification time."""
        # Try EXIF first for supported formats
        ext = Path(filepath).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.tiff', '.tif']:
            exif_dt = self.get_exif_datetime(filepath)
            if exif_dt:
                return exif_dt, "EXIF"
        
        # Fall back to file modification time
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime), "Modified"
    
    def transform_filename(self, filepath):
        """Apply transformations to a filename based on current settings."""
        path = Path(filepath)
        name = path.stem
        ext = path.suffix
        
        # Apply case conversion
        case_mode = self.case_mode.get()
        
        if case_mode == "datetime":
            # Generate datetime-based filename
            dt, source = self.get_file_datetime(filepath)
            name = dt.strftime(self.datetime_format)
            
        elif case_mode == "lower":
            name = name.lower()
        elif case_mode == "upper":
            name = name.upper()
        elif case_mode == "title":
            # Split into words
            words = name.replace('_', ' ').replace('-', ' ').split()
            
            if words:
                titled_words = []
                for i, word in enumerate(words):
                    # First and last words are always capitalized
                    if i == 0 or i == len(words) - 1:
                        titled_words.append(word.capitalize())
                    # Check if it's a minor word and option is enabled
                    elif self.use_minor_words.get() and word.lower() in self.minor_words:
                        titled_words.append(word.lower())
                    else:
                        titled_words.append(word.capitalize())
                
                name = ' '.join(titled_words)
        
        # Apply character replacements (only for lower/upper case modes)
        if case_mode in ["lower", "upper"]:
            # 1. Strip punctuation if requested
            if self.strip_punctuation.get():
                # Keep only alphanumeric, spaces, hyphens, and underscores
                name = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
            
            # 2. Replace spaces (do this after stripping punctuation)
            if self.replace_spaces.get():
                name = name.replace(' ', '_')
        
        # 3. Replace special characters (applies to all modes)
        if self.replace_special.get():
            for char in self.special_chars:
                name = name.replace(char, '_')
        
        # Clean up multiple consecutive underscores
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        return name + ext
    
    def generate_unique_filename(self, directory, base_name, ext, existing_names):
        """Generate a unique filename by adding incrementing counter if needed.
        Only adds counters when in datetime mode."""
        new_name = base_name + ext
        new_path = directory / new_name
        
        # Check if name is unique
        if str(new_path) not in existing_names and not new_path.exists():
            return new_name
        
        # Only add counter if in datetime mode
        if self.case_mode.get() != "datetime":
            # For non-datetime modes, return as-is (will cause error if duplicate exists)
            return new_name
        
        # Add counter for datetime mode
        counter = 1
        while True:
            new_name = f"{base_name}-{counter:04d}{ext}"
            new_path = directory / new_name
            
            if str(new_path) not in existing_names and not new_path.exists():
                return new_name
            
            counter += 1
    
    def preview_changes(self):
        """Show preview of what files will be renamed to."""
        if not self.files:
            messagebox.showwarning("No Files", "Please add files first.")
            return
            
        self.output_text.delete(1.0, tk.END)
        self.log_message("=== PREVIEW MODE ===\n", "info")
        
        changes = []
        no_changes = []
        errors = []
        
        # Track names by directory to handle duplicates
        dir_names = defaultdict(set)
        is_datetime_mode = self.case_mode.get() == "datetime"
        
        for filepath in self.files:
            try:
                path = Path(filepath)
                old_name = path.name
                
                # Get base transformation
                temp_name = self.transform_filename(filepath)
                base_name = Path(temp_name).stem
                ext = Path(temp_name).suffix
                
                # Generate unique name if needed (only for datetime mode)
                new_name = self.generate_unique_filename(
                    path.parent, base_name, ext, dir_names[path.parent]
                )
                
                # For non-datetime modes, check for actual conflicts
                if not is_datetime_mode:
                    new_path = path.parent / new_name
                    
                    # Check if target exists and is NOT the same file (case-only change)
                    if old_name != new_name:
                        # Case-only rename check: same file path when compared case-insensitively
                        if old_name.lower() == new_name.lower():
                            # This is just a case change of the same file - allow it
                            pass
                        elif str(new_path) in dir_names[path.parent] or new_path.exists():
                            # Different file with same name - conflict
                            errors.append((old_name, f"Target '{new_name}' already exists"))
                            continue
                
                dir_names[path.parent].add(str(path.parent / new_name))
                
                if old_name == new_name:
                    no_changes.append(old_name)
                else:
                    changes.append((old_name, new_name))
                    
            except Exception as e:
                errors.append((filepath, str(e)))
        
        # Display changes
        if changes:
            self.log_message(f"Files to be renamed ({len(changes)}):\n", "success")
            for old_name, new_name in changes[:20]:  # Show first 20
                self.log_message(f"  {old_name}", "info")
                self.log_message(f"  → {new_name}\n", "success")
            if len(changes) > 20:
                self.log_message(f"  ... and {len(changes) - 20} more\n", "info")
        
        if no_changes:
            self.log_message(f"\nNo changes needed ({len(no_changes)}):", "warning")
            for name in no_changes[:5]:  # Show first 5
                self.log_message(f"  {name}", "warning")
            if len(no_changes) > 5:
                self.log_message(f"  ... and {len(no_changes) - 5} more", "warning")
        
        if errors:
            self.log_message(f"\nErrors/Conflicts ({len(errors)}):", "error")
            for item, error in errors:
                self.log_message(f"  {item}: {error}", "error")
        
        self.log_message(f"\n=== Summary: {len(changes)} to rename, {len(no_changes)} unchanged, {len(errors)} errors ===", "info")
        
    def convert_files(self):
        """Actually rename the files."""
        if not self.files:
            messagebox.showwarning("No Files", "Please add files first.")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Rename",
            f"Are you sure you want to rename {len(self.files)} file(s)?\n\nThis action cannot be undone."
        )
        
        if not result:
            return
        
        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._do_conversion, daemon=True)
        thread.start()
        
    def _do_conversion(self):
        """Perform the actual file conversion (runs in separate thread)."""
        self.root.after(0, lambda: self.output_text.delete(1.0, tk.END))
        self.root.after(0, lambda: self.log_message("=== CONVERTING FILES ===\n", "info"))
        
        total = len(self.files)
        success_count = 0
        skip_count = 0
        error_count = 0
        
        # Track names by directory to handle duplicates
        dir_names = defaultdict(set)
        is_datetime_mode = self.case_mode.get() == "datetime"
        
        for i, filepath in enumerate(self.files):
            try:
                path = Path(filepath)
                old_name = path.name
                
                # Get base transformation
                temp_name = self.transform_filename(filepath)
                base_name = Path(temp_name).stem
                ext = Path(temp_name).suffix
                
                # Generate unique name if needed (only for datetime mode)
                new_name = self.generate_unique_filename(
                    path.parent, base_name, ext, dir_names[path.parent]
                )
                
                # Update progress
                progress = int((i + 1) / total * 100)
                self.root.after(0, lambda p=progress: self.progress.config(value=p))
                self.root.after(0, lambda i=i, t=total: self.progress_label.config(
                    text=f"Processing {i+1}/{t}..."
                ))
                
                if old_name == new_name:
                    self.root.after(0, lambda n=old_name: self.log_message(f"⊘ SKIP: {n} (no change needed)", "warning"))
                    skip_count += 1
                else:
                    new_path = path.parent / new_name
                    
                    # Check if target already exists (important for non-datetime modes)
                    if not is_datetime_mode:
                        # Case-only rename check
                        if old_name.lower() == new_name.lower():
                            # This is just a case change of the same file - allow it
                            # Need to use a temporary name on case-insensitive filesystems
                            import platform
                            if platform.system() in ['Windows', 'Darwin']:  # Case-insensitive filesystems
                                temp_path = path.parent / (new_name + '.tmp_rename')
                                path.rename(temp_path)
                                temp_path.rename(new_path)
                            else:
                                path.rename(new_path)
                            
                            dir_names[path.parent].add(str(new_path))
                            self.root.after(0, lambda o=old_name, n=new_name: self.log_message(
                                f"✓ SUCCESS: {o} → {n}", "success"
                            ))
                            success_count += 1
                            continue
                        elif str(new_path) in dir_names[path.parent] or new_path.exists():
                            self.root.after(0, lambda o=old_name, n=new_name: self.log_message(
                                f"✗ ERROR: {o} → {n} (target already exists)", "error"
                            ))
                            error_count += 1
                            continue
                    
                    # Rename the file
                    path.rename(new_path)
                    dir_names[path.parent].add(str(new_path))
                    
                    self.root.after(0, lambda o=old_name, n=new_name: self.log_message(
                        f"✓ SUCCESS: {o} → {n}", "success"
                    ))
                    success_count += 1
                        
            except Exception as e:
                self.root.after(0, lambda f=filepath, e=str(e): self.log_message(
                    f"✗ ERROR: {Path(f).name} - {e}", "error"
                ))
                error_count += 1
        
        # Final summary
        self.root.after(0, lambda: self.progress_label.config(text="Complete!"))
        self.root.after(0, lambda: self.log_message(
            f"\n=== COMPLETE: {success_count} renamed, {skip_count} skipped, {error_count} errors ===",
            "info"
        ))
        
        # Clear files list on success
        if success_count > 0:
            self.root.after(0, self.clear_files)


def main():
    """Main entry point for the GUI application."""
    root = TkinterDnD.Tk()
    app = FileRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
