# C-BOM: Download & Installation Guide

Complete instructions for getting C-BOM on your computer.

---

## Download Options

### Option 1: Windows Desktop App (Recommended for Non-Technical Users)

**No Python installation required. Just download and run!**

1. **Visit GitHub Releases:**
   - Go to: `https://github.com/ibrahim9924/C-BOM/releases`

2. **Download the EXE:**
   - Click the latest release
   - Download `C-BOM.exe`

3. **Run It:**
   - Double-click `C-BOM.exe`
   - Application launches immediately
   - Create your first C-BOM

✅ **Best for:** Quick startup, no technical setup, end users

---

### Option 2: Source Code (For Developers)

**Allows customization and contribution to the project.**

1. **Install Python:**
   - Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
   - Install to your computer (don't skip the "Add Python to PATH" option)

2. **Get the Code:**

   **Method A - With Git:**
   ```bash
   git clone https://github.com/ibrahim9924/C-BOM.git
   cd C-BOM
   ```

   **Method B - Without Git:**
   - Go to: `https://github.com/ibrahim9924/C-BOM`
   - Click **Code** → **Download ZIP**
   - Extract the ZIP file
   - Open PowerShell/Command Prompt in the extracted folder

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python main.py
   ```

✅ **Best for:** Developers, customization, contributing

---

## Detailed Setup Guide

### Windows Setup (Step-by-Step)

#### Step 1: Verify Python Installation
```bash
python --version
```

Should show `Python 3.8.0` or higher.

If you get "not found":
- Install Python from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation
- Restart Command Prompt/PowerShell after installation

#### Step 2: Clone or Download
```bash
# Using Git:
git clone https://github.com/ibrahim9924/C-BOM.git
cd C-BOM

# Or: Download ZIP and extract manually
```

#### Step 3: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- pytest (for testing)
- pytest-cov (for coverage reports)
- Other required packages

#### Step 5: Run the Application
```bash
python main.py
```

GUI window should open.

---

### macOS/Linux Setup

#### Step 1: Install Python
```bash
# macOS with Homebrew:
brew install python@3.11

# Linux (Ubuntu/Debian):
sudo apt-get install python3.11 python3.11-venv
```

#### Step 2: Clone Repository
```bash
git clone https://github.com/ibrahim9924/C-BOM.git
cd C-BOM
```

#### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Run
```bash
python main.py --web
# or
python main.py
```

---

## Verify Installation

### Test 1: Check Python
```bash
python --version
```

Output should be: `Python 3.8.x` or higher

### Test 2: Check Imports
```bash
python -c "from cbom import models; print('✓ C-BOM installed correctly')"
```

### Test 3: Run Application
```bash
python main.py
```

GUI should open. If it does, you're set! ✅

### Test 4: Run Tests (Optional)
```bash
pytest tests/ -v
```

All tests should pass.

---

## Run Modes

### GUI Mode (GUI)
```bash
python main.py
# Opens graphical interface window
```

### Web Dashboard
```bash
python main.py --web
# Open: http://localhost:5000
```

### Command Line
```bash
python main.py --cli
# Command-line interface
```

---

## Troubleshooting

### "Python not found"
**Solution:**
1. Install Python from [python.org](https://www.python.org)
2. Make sure to check "Add Python to PATH" during installation
3. Restart your terminal/PowerShell
4. Try again: `python --version`

### "Module not found" or "No module named 'cbom'"
**Solution:**
```bash
# Make sure you're in the C-BOM folder:
cd c:\path\to\C-BOM

# Install dependencies:
pip install -r requirements.txt

# Try running again:
python main.py
```

### "tkinter not available"
**Solution:**

**Windows:**
```bash
pip install tk
```

**macOS:**
```bash
brew install python-tk@3.11
```

**Linux (Ubuntu):**
```bash
sudo apt-get install python3.11-tk
```

### Application won't start
**Try:**
1. Check Python version: `python --version` (must be 3.8+)
2. Verify dependencies: `pip list`
3. Try web mode: `python main.py --web`
4. Check for errors: `python main.py 2>&1` (shows full error)

### Port 5000 already in use
**Solution:**
```bash
python main.py --web --port 8080
# Then visit: http://localhost:8080
```

---

## System Requirements

### Minimum (For EXE)
- Windows 7 or later
- 100 MB disk space
- No internet required after download

### Recommended (For Source Code)
- Python 3.8+
- 500 MB disk space
- Internet connection (for pip install)
- Text editor or IDE

### Operating Systems
- ✅ Windows 7+
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu 18.04+, Fedora 30+, etc.)

---

## Environment Setup

### Using Virtual Environment (Recommended)

**Why?** Keeps project dependencies separate from system Python.

```bash
# Create virtual environment
python -m venv cbom_env

# Activate it
# Windows:
cbom_env\Scripts\activate
# macOS/Linux:
source cbom_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python main.py

# Deactivate when done
deactivate
```

---

## Getting Updates

### Update from GitHub
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Download New Release
1. Go to [Releases](https://github.com/ibrahim9924/C-BOM/releases)
2. Download latest `C-BOM.exe`
3. Replace old .exe with new one

---

## Uninstallation

### Remove Source Code
```bash
# Delete the C-BOM folder
rm -r C-BOM
```

### Remove Virtual Environment
```bash
# Delete the venv folder
rm -r cbom_env
# or cbom_env for Windows
```

### Remove EXE
```
1. Delete C-BOM.exe
2. Delete any configuration files created by the app
```

---

## Support

- 📖 **Docs:** See [README.md](README.md)
- 🚀 **Quick Start:** See [QUICKSTART.md](QUICKSTART.md)
- 🐛 **Issues:** Report bugs on GitHub
- 💡 **Questions:** Ask in GitHub Discussions

---

## Next Steps

1. ✅ Successfully installed? Great!
2. 📖 Read [QUICKSTART.md](QUICKSTART.md) for usage
3. 🎯 Follow [README.md](README.md) for examples
4. 🔍 Start creating your first C-BOM

---

**Ready?** Launch the app:
```bash
python main.py
```

Enjoy managing your cryptographic assets! 🔐
