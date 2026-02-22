# C-BOM: Cryptographic Bill of Materials

A comprehensive **Cryptographic Bill of Materials** management tool with version control, validation, hierarchical support, and multi-interface access (CLI, Web, GUI).

## 🔐 Overview

C-BOM is a specialized asset management system designed for cryptographic infrastructure. It helps organizations:

- **Track** cryptographic assets (algorithms, keys, certificates, libraries)
- **Monitor** vulnerability status and security posture
- **Validate** compliance with security standards (FIPS 140-2, PCI-DSS, HIPAA)
- **Manage** key lifecycle and rotation schedules
- **Audit** all changes with detailed audit trails
- **Export** data in JSON/CSV formats

## ✨ Key Features

### Cryptographic Asset Management
- Track algorithms, keys, certificates, cipher suites, and cryptographic libraries
- Monitor key lengths, cipher modes, and encryption purposes
- Track asset status (active, deprecated, vulnerable, expired)
- Manage dependencies between assets

### Security & Compliance
- **CVSS Risk Scoring**: Automatic vulnerability assessment (0-10)
- **Known CVE Tracking**: Identify vulnerabilities in your crypto stack
- **Compliance Checking**: Validate against FIPS 140-2, PCI-DSS, HIPAA
- **Algorithm Strength Assessment**: Verify key lengths meet modern standards
- **Security Posture Scoring**: Overall BOM security score (0-100)

### Version Control
- Track all changes with timestamps
- Maintain complete audit trail of BOM modifications
- Support for snapshots and rollback capabilities

### Hierarchical BOMs
- Create parent-child relationships between crypto assets
- Build assemblies of related algorithms and keys
- Support for multi-level crypto infrastructure

### Multiple Interfaces
- **CLI**: Command-line interface with detailed output
- **Web UI**: Flask-based dashboard with vulnerability tracking
- **GUI**: Tkinter-based graphical interface
- **API**: RESTful endpoints for programmatic access

## 📋 Requirements

- Python 3.8+
- Flask 3.1.2 (for web mode)
- Tkinter (for GUI mode, usually included with Python)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/C-BOM.git
cd C-BOM
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Quick Start

### CLI Mode (Default)
```bash
python main.py --cli
```

Shows your cryptographic BOM with security assessment, vulnerabilities, and audit log.

### Web Mode
```bash
python main.py --web
```

Opens http://localhost:5000 with interactive dashboard for managing crypto assets.

### GUI Mode
```bash
python main.py --gui
```

Launches graphical interface (Note: Falls back to web mode if graphics unavailable).

### Help
```bash
python main.py --help
```

## 📊 Example Output (CLI)

```
BOM: TLS/Encryption Audit
Description: Track cryptographic assets for security audit

┌─────────────────────────────────────────┐
│ SECURITY POSTURE: 95/100 EXCELLENT ✓   │
│ Assets: 4 | Critical: 0 | Vulnerable: 1│
└─────────────────────────────────────────┘

CRYPTOGRAPHIC ASSETS:
  AES-1        │ AES-256-GCM      │ 256-bit  │ LOW RISK   │ active
  RSA-1        │ RSA-2048         │ 2048-bit │ LOW RISK   │ active
  TLS13        │ TLS 1.3          │ Mixed    │ LOW RISK   │ active
  LEGACY       │ SHA-1 (DEPRECATED)│ 160-bit  │ HIGH RISK  │ vulnerable

VULNERABILITIES:
  ⚠ LEGACY: SHA-1 is deprecated. Use SHA-256 or later.
```

## 🔧 Web Interface

Access the interactive dashboard at `http://localhost:5000`:

- **Dashboard**: Real-time security metrics and vulnerability overview
- **Assets**: Browse all cryptographic assets with risk levels
- **Add Asset**: Add new crypto assets to your inventory
- **Validate**: Check BOM for security issues
- **Export**: Download BOM as JSON or CSV

## 📁 Project Structure

```
c-bom/
├── cbom/                      # Main package
│   ├── __init__.py           # Package exports
│   ├── models.py             # CryptoAsset & CryptoBOM data models
│   ├── validator.py          # Crypto validation logic
│   ├── version_control.py    # Version tracking
│   ├── hierarchical.py       # Hierarchical BOM support
│   ├── gui.py                # Tkinter GUI interface
│   └── web_ui.py             # Flask web interface
├── tests/                     # Test suite
│   └── test_cbom.py          # Unit tests
├── main.py                    # Entry point (CLI/Web/GUI router)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── README_CRYPTO.md           # Detailed crypto documentation
├── QUICKSTART_CRYPTO.md       # Crypto quick start guide
└── examples.py                # Usage examples
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/test_cbom.py -v
```

## 📚 API Reference

### CryptoAsset Model
```python
CryptoAsset(
    id="AES-1",                          # Unique identifier
    name="AES Encryption",               # Human-readable name
    asset_type="algorithm",              # algorithm|key|certificate|library|cipher_suite
    algorithm="AES-256-GCM",             # Algorithm name
    key_length=256,                      # Key length in bits
    cipher_mode="GCM",                   # Cipher mode (GCM, CBC, etc.)
    purpose="encryption",                # encryption|hashing|signing|key_exchange
    status="active",                     # active|deprecated|vulnerable|expired
    compliance=["FIPS 140-2", "PCI-DSS"],# Compliance standards
    vulnerability_score=1.0,             # CVSS score (0-10)
    known_cves=[]                        # List of CVE identifiers
)
```

### CryptoBOM Methods
- `add_asset(asset)` - Add crypto asset
- `remove_asset(asset_id)` - Remove asset
- `get_summary()` - Get BOM overview
- `get_vulnerable_assets()` - List assets with known CVEs
- `get_security_posture()` - Calculate overall security score

## 🔐 Security Standards

C-BOM validates against:
- **FIPS 140-2**: Federal cryptography standards
- **PCI-DSS**: Payment Card Industry standards
- **HIPAA**: Health Insurance Portability standards
- **CVE Database**: Known vulnerabilities tracking

## 🛠️ Configuration

Edit `config.json` to customize:
- Default port for web interface
- Audit log retention
- Export formats
- Validation rules

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review QUICKSTART_CRYPTO.md for examples

## 🎓 Learn More

- [Cryptographic Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [FIPS 140-2 Standards](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.140-2.pdf)
- [CVE Database](https://cve.mitre.org/)

## ⭐ Features in Development

- [ ] Kubernetes integration for secret management
- [ ] SIEM integration for real-time monitoring
- [ ] Machine learning vulnerability prediction
- [ ] Multi-user collaboration with role-based access
- [ ] Hardware security module (HSM) integration
- [ ] Automated certificate renewal tracking

---

**C-BOM** - Secure your cryptographic infrastructure today.
