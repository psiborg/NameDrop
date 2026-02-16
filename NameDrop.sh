#!/bin/bash
# Launch NameDrop - Smart File Renaming Tool

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting NameDrop..."
echo ""

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed or not in PATH"
    echo ""
    echo "Please install Python 3:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    echo "  Fedora: sudo dnf install python3"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "Using: $PYTHON_CMD"
echo ""

# Check for optional dependencies
echo "Checking optional dependencies..."

if ! $PYTHON_CMD -c "import PIL" 2>/dev/null; then
    echo "[WARNING] Pillow not installed - EXIF date extraction unavailable"
    echo "Install with: pip3 install pillow"
    echo ""
fi

if ! $PYTHON_CMD -c "import tkinterdnd2" 2>/dev/null; then
    echo "[WARNING] tkinterdnd2 not installed - Drag-and-drop unavailable"
    echo "Install with: pip3 install tkinterdnd2"
    echo ""
fi

# Check for tkinter
if ! $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
    echo "ERROR: tkinter is not installed"
    echo ""
    echo "Please install tkinter:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  macOS: Usually included with Python"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "Starting application..."
echo ""

# Run the application
$PYTHON_CMD "$SCRIPT_DIR/namedrop.py"

if [ $? -ne 0 ]; then
    echo ""
    echo "Application closed with an error."
    echo ""
    read -p "Press Enter to close..."
fi
