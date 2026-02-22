# C-BOM Launch Modes - Complete Guide

## Overview

C-BOM now supports three different interface modes:

1. **GUI Mode** (Desktop Application) - tkinter-based
2. **Web Mode** (Browser Interface) - Flask-based
3. **CLI Mode** (Command Line) - Terminal-based

## Launch Options

### 1. GUI Mode (Default)

```bash
python main.py
```

**Features:**
- Full graphical interface with menus
- Dialog-based component management
- Real-time BOM visualization
- Drag-and-drop friendly
- Works on Windows, macOS, Linux

**Requirements:**
- tkinter (usually included with Python)

**If GUI fails:**
- Falls back to Web Mode (if Flask installed)
- Falls back to CLI Mode (always available)

---

### 2. Web Mode (Browser Interface)

```bash
python main.py --web
```

Or with custom port:
```bash
python main.py --web 8080
```

**Features:**
- Access from any web browser
- Responsive design
- Works on any OS with Python
- Network accessible
- Mobile-friendly interface

**Requirements:**
- Flask: `pip install flask`

**Access:**
- Open browser to `http://localhost:5000`
- Or `http://localhost:PORT` if custom port specified

**Web Interface Includes:**
- BOM summary dashboard
- Component management
- Add/edit/delete components
- Real-time validation
- Export to JSON/CSV
- Responsive tables

**Advantages:**
- No installation required for end users
- Share via local network
- Better UI rendering
- Works if tkinter unavailable

---

### 3. CLI Mode (Command Line)

```bash
python main.py --cli
```

**Features:**
- Text-based interface
- Fastest mode
- No GUI dependencies
- Perfect for scripting
- Great for servers/terminals

**What it does:**
- Creates example BOM automatically
- Shows formatted output in terminal
- Exports files (JSON, CSV)
- Perfect for automation

**Advantages:**
- Zero UI dependencies
- Works everywhere
- Fast and lightweight
- Ideal for CI/CD pipelines

---

## Help Information

```bash
python main.py --help
```

Shows all available options and usage.

---

## When to Use Each Mode

### Use GUI Mode When:
- ✅ User prefers visual interface
- ✅ Interactive work needed
- ✅ System has tkinter available
- ✅ Desktop application preferred

### Use Web Mode When:
- ✅ Sharing access across network
- ✅ Want modern responsive UI
- ✅ Mobile access needed
- ✅ tkinter unavailable
- ✅ Running on servers

### Use CLI Mode When:
- ✅ Scripting/automation needed
- ✅ Running in containers/VMs
- ✅ Maximum compatibility needed
- ✅ Terminal-only environments
- ✅ Minimal resource usage

---

## Installation & Setup

### Basic Setup (CLI always works)

```bash
pip install -r requirements.txt
python main.py --cli
```

### For GUI Support

```bash
pip install -r requirements.txt
# tkinter usually pre-installed
python main.py
```

### For Web Interface

```bash
pip install -r requirements.txt
pip install flask
python main.py --web
```

---

## Troubleshooting

### "GUI failed to start" Error

**Solution 1:** Use CLI mode
```bash
python main.py --cli
```

**Solution 2:** Use Web mode
```bash
pip install flask
python main.py --web
```

**Solution 3:** Install tkinter
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS with Homebrew
brew install python-tk
```

### Web Mode Not Working

**Error:** "No module named 'flask'"

**Solution:**
```bash
pip install flask
python main.py --web
```

### Port Already in Use

**If port 5000 is busy:**
```bash
python main.py --web 8080
```

Or find and stop the process using the port.

---

## Automatic Fallback

If you run `python main.py` (no arguments):

1. Tries to launch **GUI Mode**
2. If GUI fails → Tries **Web Mode** (if Flask available)
3. If Web fails → Falls back to **CLI Mode**
4. **CLI Mode** always succeeds (no dependencies)

This ensures the application always works!

---

## Web Interface Features

### Dashboard
- Real-time BOM summary
- Component count
- Total cost calculation
- Category breakdown

### Component Management
- Add new components via form
- View all components in table
- Delete individual components
- Automatic data validation

### Export Options
- Download as JSON (structured data)
- Download as CSV (spreadsheet-compatible)

### Validation
- Full BOM validation
- Error reporting
- Completeness metrics
- Real-time feedback

---

## Performance Notes

| Mode | Memory | CPU | Speed | Network |
|------|--------|-----|-------|---------|
| CLI | ~30 MB | Low | Fastest | N/A |
| GUI | ~100 MB | Low | Fast | N/A |
| Web | ~80 MB | Low | Fast | Local |

---

## Advanced Usage

### Custom Web Configuration

Edit `config.json` to customize web UI settings:
```json
{
  "web": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  }
}
```

### Running Web Server Permanently

```bash
# Using nohup (Unix/Linux)
nohup python main.py --web > cbom.log 2>&1 &

# Using screen (Unix/Linux)
screen -S cbom
python main.py --web
# Press Ctrl+A then D to detach

# Using systemd (Linux)
# Create /etc/systemd/system/cbom.service
[Unit]
Description=C-BOM Web Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/cbom
ExecStart=/usr/bin/python3 main.py --web

[Install]
WantedBy=multi-user.target

# Then: sudo systemctl start cbom
```

### Network Access

To access from other machines on network:

```bash
# Instead of localhost, use machine IP
http://192.168.1.100:5000

# Or enable Flask to bind to all interfaces
# Modify web_ui.py and set host='0.0.0.0'
```

---

## Summary

- **GUI Mode**: Best for interactive desktop use
- **Web Mode**: Best for network sharing and modern UI
- **CLI Mode**: Best for scripting and compatibility
- **Automatic Fallback**: Ensures it always works

Choose the mode that best fits your use case!

---

**Need Help?**
- Check README.md for feature overview
- See QUICKSTART.md for getting started
- Review API_REFERENCE.md for programming
- Run `python main.py --help` for options
