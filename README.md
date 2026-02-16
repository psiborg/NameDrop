# NameDrop - Smart File Renaming Tool

## 🎯 New Features

### Core Enhancements
- ✅ **Drag & Drop Support** - Drop files or folders directly onto the interface
- ✅ **EXIF Date Renaming** - Rename photos by their EXIF datetime metadata
- ✅ **Strip Punctuation** - Remove all non-alphanumeric characters
- ✅ **Customizable DateTime Format** - Full control over date/time formatting
- ✅ **Smart Duplicate Handling** - Automatic increment counters for duplicate names

### Complete Feature List
- **4 Renaming Modes:**
  1. Title Case (with minor words)
  2. All Lower Case
  3. All Upper Case  
  4. Date/Time from EXIF metadata
  
- **Character Replacement:**
  - Replace spaces with underscores
  - Strip punctuation and non-alphanumeric
  - Replace special/reserved characters
  
- **Advanced Options:**
  - Customizable minor words list
  - Customizable special characters list
  - Customizable datetime format with live preview
  - Preview changes before applying
  - Real-time progress tracking
  - Color-coded debug output

---

## 📋 Requirements

### Required (included with Python)
- Python 3.6 or higher
- tkinter (usually included)

### Optional (for enhanced features)
- **Pillow** (PIL) - For EXIF date extraction from photos
  ```bash
  pip install pillow
  ```
  
- **tkinterdnd2** - For drag-and-drop support
  ```bash
  pip install tkinterdnd2
  ```

**Note:** The application works without these optional packages, but with reduced functionality.

---

## 🚀 Installation

### Windows

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install optional dependencies** (recommended)
   ```cmd
   pip install pillow tkinterdnd2
   ```

3. **Run the application**
   - Double-click `NameDrop.bat`
   - Or run: `python namedrop.py`

### macOS

1. **Python** comes pre-installed, or install via Homebrew:
   ```bash
   brew install python3
   ```

2. **Install optional dependencies** (recommended)
   ```bash
   pip3 install pillow tkinterdnd2
   ```

3. **Run the application**
   ```bash
   chmod +x NameDrop.sh
   ./NameDrop.sh
   ```

### Linux

1. **Install Python and tkinter**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3 python3-tk python3-pip
   
   # Fedora
   sudo dnf install python3 python3-tkinter python3-pip
   
   # Arch
   sudo pacman -S python tk python-pip
   ```

2. **Install optional dependencies** (recommended)
   ```bash
   pip3 install pillow tkinterdnd2
   ```

3. **Run the application**
   ```bash
   chmod +x NameDrop.sh
   ./NameDrop.sh
   ```

---

## 📖 User Guide

### File Selection

**Method 1: Drag & Drop** (if tkinterdnd2 installed)
- Drag files or folders directly onto the drop zone
- Multiple files and folders supported

**Method 2: Buttons** (always available)
- **Add Files** - Select individual files
- **Add Folder** - Add all files from a folder
- **Clear All** - Remove all files from list

### Renaming Modes

#### 1. Title Case
Capitalizes first letter of each word, with smart minor word handling.

**Options:**
- ✅ **Use minor words** - Keeps words like "a", "the", "of" lowercase
- **Edit Minor Words** - Customize which words stay lowercase

**Examples:**
```
the_art_of_war.pdf → The Art of War.pdf
guide-to-python-and-javascript.txt → Guide to Python and Javascript.txt
```

#### 2. All Lower Case
Converts everything to lowercase.

**Mode-Specific Options:**
- ✅ **Replace spaces with underscores** - Converts spaces to `_`
- ✅ **Strip punctuation and non-alphanumeric** - Removes all special characters

**Examples:**
```
MY_DOCUMENT.PDF → my_document.pdf
HelloWorld.txt → helloworld.txt
My Document.pdf → my_document.pdf  (with "Replace spaces")
file: name?.txt → filename.txt  (with "Strip punctuation")
```

#### 3. All Upper Case
Converts everything to uppercase.

**Mode-Specific Options:**
- ✅ **Replace spaces with underscores** - Converts spaces to `_`
- ✅ **Strip punctuation and non-alphanumeric** - Removes all special characters

**Examples:**
```
my_document.pdf → MY_DOCUMENT.PDF
hello_world.txt → HELLO_WORLD.TXT
My Document.pdf → MY_DOCUMENT.PDF  (with "Replace spaces")
file: name?.txt → FILENAME.TXT  (with "Strip punctuation")
```

#### 4. Date/Time from EXIF ⭐ NEW
Renames files based on their date/time metadata.

**How it works:**
1. For photos (JPEG, TIFF): Extracts EXIF datetime
2. For other files: Uses file modification time
3. Auto-adds counters for duplicates (e.g., 20240115-143025-0001)

**Options:**
- **Edit DateTime Format** - Customize the date/time format

**Default format:** `%Y%m%d-%H%M%S` → `20240115-143025`

**Common formats:**
```
%Y%m%d-%H%M%S         → 20240115-143025
%Y-%m-%d_%H-%M-%S     → 2024-01-15_14-30-25
IMG_%Y%m%d_%H%M%S     → IMG_20240115_143025
%Y%m%d                → 20240115
%Y-%m-%d              → 2024-01-15
```

**Examples:**
```
DSC_1234.jpg → 20240115-143025.jpg
photo.jpg → 20240115-143026.jpg
photo2.jpg → 20240115-143026-0001.jpg  (if duplicate)
```

### Character Replacement

This section is available for all renaming modes.

#### Replace special/reserved characters
Replaces characters that are invalid in filenames: `< > : " / \ | ? *`
```
file:name?.txt → file_name_.txt
report<final>.docx → report_final_.docx
```

**Edit Special Characters** - Customize which characters to replace

---

### Mode-Specific Options

Different renaming modes show different additional options:

**Title Case:**
- Use minor words (checkbox)
- Edit Minor Words (button)

**All Lower Case / All Upper Case:**
- Replace spaces with underscores (checkbox)
- Strip punctuation and non-alphanumeric (checkbox)

**Date/Time from EXIF:**
- Edit DateTime Format (button)

### Processing Options

**Preview Changes** (Recommended)
- Shows exactly what will change
- Color-coded output:
  - 🟢 Green: Files to be renamed
  - 🟠 Orange: Files with no changes
  - 🔴 Red: Errors or conflicts
- No actual changes made

**Convert Files**
- Actually renames the files
- Shows confirmation dialog
- ⚠️ **Cannot be undone!**
- Progress bar shows real-time status

---

## 💡 Usage Examples

### Example 1: Organize vacation photos by date

**Settings:**
- Mode: Date/Time from EXIF
- Format: `%Y-%m-%d_%H%M%S`

**Before:**
```
DSC_0001.jpg
DSC_0002.jpg
IMG_1234.jpg
```

**After:**
```
2024-01-15_143025.jpg
2024-01-15_143026.jpg
2024-01-15_150340.jpg
```

### Example 2: Clean up document names for web

**Settings:**
- Mode: All Lower Case
  - Strip punctuation: ✅
  - Replace spaces: ✅

**Before:**
```
My Report (Final Draft).docx
Meeting Notes - Jan 15th.txt
Q&A Document.pdf
```

**After:**
```
my_report_final_draft.docx
meeting_notes_jan_15th.txt
qa_document.pdf
```

### Example 3: Professional document formatting

**Settings:**
- Mode: Title Case
- Use minor words: ✅
- Replace special chars: ✅

**Before:**
```
the-complete-guide-to-python.pdf
notes:from:meeting.txt
quarterly-report-Q1-2024.xlsx
```

**After:**
```
The Complete Guide to Python.pdf
notes_from_meeting.txt
Quarterly Report Q1 2024.xlsx
```

### Example 4: Batch rename code files

**Settings:**
- Mode: All Lower Case
  - Strip punctuation: ✅
  - Replace spaces: ✅

**Before:**
```
Helper Functions.js
My New Script.py
Test Cases & Examples.rb
```

**After:**
```
helper_functions.js
my_new_script.py
test_cases_examples.rb
```

---

## 🎨 DateTime Format Reference

### Basic Formats

| Code | Meaning | Example |
|------|---------|---------|
| %Y | Year (4 digits) | 2024 |
| %y | Year (2 digits) | 24 |
| %m | Month (01-12) | 01 |
| %d | Day (01-31) | 15 |
| %H | Hour 24h (00-23) | 14 |
| %I | Hour 12h (01-12) | 02 |
| %M | Minute (00-59) | 30 |
| %S | Second (00-59) | 45 |
| %p | AM/PM | PM |

### Month & Day Names

| Code | Meaning | Example |
|------|---------|---------|
| %B | Full month | January |
| %b | Short month | Jan |
| %A | Full day | Monday |
| %a | Short day | Mon |

### Complete Examples

```
%Y%m%d-%H%M%S              → 20240115-143025
%Y-%m-%d_%H-%M-%S          → 2024-01-15_14-30-25
%Y%m%d_%H%M                → 20240115_1430
%Y-%m-%d                   → 2024-01-15
%b_%d_%Y                   → Jan_15_2024
%Y-%m-%d_%I-%M%p           → 2024-01-15_02-30PM
IMG_%Y%m%d_%H%M%S          → IMG_20240115_143025
Photo_%Y-%m-%d_%H%M        → Photo_2024-01-15_1430
%A_%B_%d_%Y                → Monday_January_15_2024
```

---

## ⚠️ Important Notes

### Duplicate Handling
**Date/Time mode ONLY:** When renaming files with the same timestamp, auto-incremented counters are added:
```
20240115-143025.jpg
20240115-143025-0001.jpg
20240115-143025-0002.jpg
```

**Other modes:** Duplicate names will cause errors. The preview will show conflicts before renaming, and conversion will skip files with duplicate target names. You'll need to manually resolve duplicates or use different settings.

### EXIF Support
- **Supported formats:** JPEG (.jpg, .jpeg), TIFF (.tif, .tiff)
- **Requires:** Pillow (PIL) library
- **Fallback:** Uses file modification time if EXIF unavailable

### File Extensions
- Always preserved
- Case-sensitive on Linux/Mac
- Example: `.JPG` stays `.JPG`, not changed to `.jpg`

### Safe Operation
1. **Always preview first!**
2. Test on copies of important files
3. No undo - renamed files stay renamed
4. Conflicts are detected before renaming

---

## 🐛 Troubleshooting

### "tkinterdnd2 not installed" warning
- Drag-and-drop unavailable
- Use "Add Files" and "Add Folder" buttons instead
- To enable: `pip install tkinterdnd2`

### "PIL/Pillow not installed" warning
- EXIF extraction unavailable
- Falls back to file modification time
- To enable: `pip install pillow`

### Permission denied errors
- Check write permissions on files
- Close files if they're open
- Run as administrator (Windows) or with sudo (Linux/Mac) if needed

### Files not renaming
- Check if target names already exist
- Verify file isn't in use by another program
- Look at debug output for specific errors

### GUI looks wrong on Linux
Install tkinter:
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

---

## 🔧 Advanced Tips

### Custom Minor Words
- Add industry-specific terms
- Include acronyms (e.g., "api", "ui", "ux")
- Remove words you always want capitalized

### DateTime for Non-Photos
- Works on any file type
- Uses file modification time
- Useful for organizing downloads, documents, etc.

### Batch Processing
- No limit on number of files
- Processes files in order added
- Shows real-time progress

### Special Characters
- Default list covers Windows, Mac, and Linux
- Add more for extra safety
- Remove some if needed for your use case

---

## 📝 Version History

**v2.0 - Enhanced Version**
- ✅ Drag & drop support
- ✅ EXIF date/time renaming mode
- ✅ Strip punctuation option
- ✅ Customizable datetime format
- ✅ Smart duplicate handling
- ✅ Live preview in datetime editor

**v1.0 - Initial Release**
- Title Case, Lower Case, Upper Case
- Minor words customization
- Special character replacement
- Preview and batch conversion

---

## 📄 License

Free and open source. Use at your own risk.

No warranty provided. Always backup important files before batch renaming.
