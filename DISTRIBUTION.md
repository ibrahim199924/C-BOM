# C-BOM Installation & Distribution Guide

Complete instructions for downloading and setting up C-BOM on someone else's computer.

---

## **Option 1: Compiled Windows EXE (Easiest - No Python Required)**

**For end users who just want to run the app:**

### Steps:

1. **Download the executable:**
   - Go to [GitHub Releases](https://github.com/ibrahim9924/C-BOM/releases)
   - Download `C-BOM.exe`
   - Save to any location (Desktop, Documents, etc.)

2. **Run it:**
   - Double-click `C-BOM.exe`
   - No installation needed, no Python required
   - App launches immediately

✅ **Best for:** Non-technical users, quick deployment, offline use

---

## **Option 2: Source Code Installation (Recommended for Developers)**

**For developers who want to modify or extend the tool:**

### Prerequisites:
- **Python 3.8+** installed ([python.org](https://www.python.org/downloads/))
- **Git** (optional, for cloning)

### Steps:

**1. Get the code:**

```bash
# Option A: Clone from GitHub (requires Git)
git clone https://github.com/ibrahim9924/C-BOM.git
cd C-BOM

# Option B: Download ZIP from GitHub
# Go to https://github.com/ibrahim9924/C-BOM → Code → Download ZIP
# Extract to desired location
# Open terminal/command prompt in that folder
```

**2. Install Python dependencies:**

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` & `pytest-cov` (for testing)
- Standard libraries (flask, tkinter already built-in)

**3. Run the application:**

```bash
# GUI Mode (Recommended)
python main.py

# Web UI Mode (Browser-based dashboard)
python main.py --web
# Then open http://localhost:5000

# CLI Mode (Command-line)
python main.py --cli
```

✅ **Best for:** Developers, customization, active development

---

## **Option 3: Build Custom EXE (For Distribution)**

If you want to **create your own .exe to share with others:**

### Prerequisites:
- Python 3.8+ installed
- All C-BOM source code

### Steps:

**1. Install build tools:**

```bash
pip install pyinstaller pillow
```

**2. Create the app icon:**

```bash
python create_icon.py
```

**3. Build the EXE:**

```bash
pyinstaller --onefile --windowed --icon=cbom.ico --name="C-BOM" --add-data "cbom;cbom" app_launcher.py
```

**4. Find the compiled EXE:**
```
dist/C-BOM.exe  ← Your standalone application
```

✅ **Best for:** Creating custom distributions, packaging for clients

---

## **Installation Comparison**

| Item | Option 1 (EXE) | Option 2 (Source) | Option 3 (Build) |
|------|---|---|---|
| **Python Required** | ❌ No | ✅ Yes | ✅ Yes |
| **Git Required** | ❌ No | ⚠️ Optional | ❌ No |
| **Setup Time** | <1 min | 5-10 min | 10-15 min |
| **Can Modify Code** | ❌ No | ✅ Yes | ✅ Yes |
| **File Size** | ~50-100 MB | ~10 MB | ~50-100 MB |
| **Best For** | End users | Developers | Distribution |

---

## **Quick Start for Non-Technical Users**

```
1. Visit: https://github.com/ibrahim9924/C-BOM
2. Click "Releases" (right sidebar)
3. Download "C-BOM.exe" from latest release
4. Save to Desktop (or any folder)
5. Double-click C-BOM.exe
6. Done! Application opens
```

---

## **Verification After Installation**

After setup, verify it works:

**For GUI:**
```bash
python main.py
# Should open graphical interface with dashboard
```

**For Web:**
```bash
python main.py --web
# Should print: "Running on http://localhost:5000"
# Open that URL in browser
```

**For Testing:**
```bash
pytest tests/test_cbom.py -v
# Should show all tests passing
```

---

## **Troubleshooting**

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python from [python.org](https://www.python.org) |
| "Module not found" | Run `pip install -r requirements.txt` |
| "tkinter not available" | Install: `pip install tk` |
| EXE won't run | Check Windows Defender/antivirus isn't blocking it |
| Port 5000 in use | Use `--port 8080` with `python main.py --web` |

---

## **What Files to Share**

**To share the tool, provide:**

```
Option A (Easiest):
  └─ C-BOM.exe (just the .exe file)

Option B (Full source):
  ├─ All .py files
  ├─ requirements.txt
  ├─ README.md
  └─ cbom/ folder
```

---

## **Release Process**

To publish a new release:

1. **Test everything:**
   ```bash
   pytest tests/test_cbom.py -v
   ```

2. **Update version** in code/README if needed

3. **Build EXE:**
   ```bash
   python create_icon.py
   pyinstaller --onefile --windowed --icon=cbom.ico --name="C-BOM" --add-data "cbom;cbom" app_launcher.py
   ```

4. **Test the EXE:**
   - Run `dist/C-BOM.exe` manually
   - Verify all features work

5. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Release: Version X.Y.Z"
   git push origin main
   ```

6. **Create GitHub Release:**
   - Go to Releases → Draft new release
   - Tag version (e.g., v1.0.0)
   - Upload `dist/C-BOM.exe`
   - Add release notes
   - Publish

---

## **System Requirements**

### Minimum (For EXE):
- Windows 7 or later
- 100 MB disk space
- No internet required after download

### Recommended (For Source):
- Windows 10+ or macOS/Linux with Python 3.8+
- 500 MB disk space
- Internet for pip install
- Text editor or IDE

---

## **Support Resources**

- **Full Documentation**: See [README.md](README.md)
- **API Reference**: See [API_REFERENCE.md](API_REFERENCE.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Development Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **GitHub**: https://github.com/ibrahim9924/C-BOM

---

**Last Updated:** February 23, 2026
