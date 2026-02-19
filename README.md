#  C-BOM  Cryptographic Bill of Materials

**C-BOM** is a security tool for tracking, validating, and managing all cryptographic assets in a system  algorithms, keys, certificates, cipher suites, and more.

[![Tests](https://github.com/ibrahim199924/C-BOM/actions/workflows/tests.yml/badge.svg)](https://github.com/ibrahim199924/C-BOM/actions)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is a Cryptographic Bill of Materials?

A **C-BOM** (Cryptographic Bill of Materials) is an inventory of every cryptographic primitive used in a system  similar to a software BOM but focused on cryptography. It helps security teams:

- Identify weak or broken algorithms (MD5, SHA-1, DES, RC4)
- Track key expiration and rotation schedules
- Audit compliance with FIPS 140-2, PCI-DSS, and HIPAA
- Monitor known CVEs affecting cryptographic libraries
- Respond quickly to cryptographic vulnerabilities (e.g., post-quantum migration)

---

## Features

- **Asset Management**  Add, remove, and view cryptographic assets with full metadata
- **Auto-status Detection**  Automatically flags weak algorithms as `deprecated` or `vulnerable`
- **Risk Scoring**  Each asset gets a risk level: CRITICAL / HIGH / MEDIUM / LOW
- **BOM Validation**  Per-asset validation with detailed error reporting
- **Security Charts**  Risk distribution doughnut chart, asset-type bar chart, validation overview chart
- **Security Score**  Overall BOM health score (0100)
- **Audit Log**  Every add/remove action is timestamped and logged
- **Export**  Download your BOM as JSON or CSV
- **Version Control**  Track BOM history and changes over time
- **Hierarchical BOMs**  Model complex systems with sub-assemblies
- **Web UI**  Clean browser-based dashboard (Flask)
- **CLI Mode**  Scriptable command-line interface
- **Desktop App**  Packaged as a standalone Windows `.exe`

---

## Quick Start

### Run from source

```bash
# Install dependencies
pip install -r requirements.txt

# Web UI (recommended)
python main.py --web
# Then open http://localhost:5000

# CLI mode
python main.py --cli
```

### Windows Desktop App

Download `C-BOM.exe` from [Releases](https://github.com/ibrahim199924/C-BOM/releases), double-click to launch. No Python required.

---

## Web Interface

| Section | Description |
|---------|-------------|
| **Dashboard** | Security score, risk distribution chart, asset-type chart, audit log |
| **Assets** | Full asset table with color-coded risk badges and  weak-algorithm warnings |
| **Add Asset** | Live algorithm checker, auto-detects status, key-length validation |
| **Validate** | Per-asset validation report with valid/invalid chart |
| **Export** | Download BOM as JSON or CSV |

---

## Asset Fields

| Field | Description | Example |
|-------|-------------|---------|
| **ID** | Unique identifier (uppercase) | `AES-GCM-1` |
| **Name** | Human-readable name | `AES-256 Database Encryption` |
| **Type** | `algorithm`, `key`, `certificate`, `cipher_suite`, `library` | `algorithm` |
| **Algorithm** | Cryptographic algorithm name | `AES-256-GCM` |
| **Key Length** | Key size in bits | `256` |
| **Status** | `active`, `deprecated`, `vulnerable`, `expired`, `planned` | Auto-detected |

---

## Risk Levels

| Level | Trigger |
|-------|---------|
|  **CRITICAL** | Status is `vulnerable` or asset is expired |
|  **HIGH** | Weak algorithm (SHA-1, 3DES, etc.) or `deprecated` status |
|  **MEDIUM** | CVSS score  4.0 |
|  **LOW** | Strong algorithm, active, no known issues |

---

## Weak / Broken Algorithms (Auto-Flagged)

| Algorithm | Status Assigned | Why |
|-----------|----------------|-----|
| MD5 | `vulnerable` | Completely broken, hash collisions trivially found |
| DES | `vulnerable` | 56-bit key, brute-forceable in hours |
| RC4 | `vulnerable` | Multiple statistical biases, broken in TLS |
| SHA-1 | `deprecated` | Collision attacks demonstrated (SHAttered) |
| 3DES | `deprecated` | Sweet32 birthday attack |
| RC2, RC5 | `vulnerable` | Weak and obsolete |
| SSLv2, SSLv3 | `vulnerable` | Protocol-level vulnerabilities (POODLE, DROWN) |

---

## Project Structure

```
C-BOM/
 cbom/
    __init__.py         # Package exports
    models.py           # CryptoAsset, CryptoBOM data models
    validator.py        # CryptoValidator, CryptoBOMValidator
    web_ui.py           # Flask web dashboard
    version_control.py  # BOM version history
    hierarchical.py     # HierarchicalCryptoBOM
    gui.py              # Tkinter GUI (optional)
 tests/
    test_cbom.py        # pytest test suite
 main.py                 # Entry point (--cli / --web / --gui)
 app_launcher.py         # Desktop app launcher
 examples.py             # Usage examples
 requirements.txt
 README.md
```

---

## Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=cbom
```

---

## Building the Desktop App

```bash
pip install pyinstaller pillow
python create_icon.py
pyinstaller --onefile --windowed --icon=cbom.ico --name="C-BOM" --add-data "cbom;cbom" app_launcher.py
# Output: dist/C-BOM.exe
```

---

## Requirements

- Python 3.8+
- Flask 3.x
- No external database  all data is in-memory (export to JSON/CSV to persist)

---

## License

MIT  see [LICENSE](LICENSE)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
