# C-BOM: Cryptographic Bill of Materials Management Tool

**C-BOM** is a comprehensive Python-based tool for managing and auditing cryptographic assets in your organization. Track algorithms, encryption keys, certificates, libraries, and cipher suites with full vulnerability scanning, compliance checking, and version control.

## 🔐 What is a Cryptographic Bill of Materials?

A **C-BOM** tracks all cryptographic components used in your systems:

- **Algorithms** - AES, RSA, SHA, ECDSA, TLS versions, etc.
- **Keys** - Encryption keys with lifecycle management
- **Certificates** - TLS/SSL certificates and their expiration dates
- **Libraries** - Cryptographic libraries (OpenSSL, libcrypto, etc.)
- **Cipher Suites** - Combinations of cryptographic algorithms

## ✨ Key Features

✅ **Cryptographic Asset Management**
   - Add, track, and manage all cryptographic components
   - Monitor algorithm strength and security posture
   - Track key rotation schedules and expiration dates

✅ **Vulnerability Scanning**
   - Detect known CVEs and vulnerable algorithms
   - CVSS score tracking
   - Automatic risk assessment

✅ **Compliance Checking**
   - FIPS 140-2 validation
   - PCI DSS compliance
   - HIPAA and other standards

✅ **Version Control**
   - Track changes to your cryptographic inventory
   - Audit trail of all modifications
   - Compare versions to identify changes

✅ **Hierarchical Organization**
   - Organize assets by category (TLS, Encryption, Hashing, etc.)
   - Support for nested asset hierarchies
   - Dependency tracking

✅ **Multiple Interfaces**
   - **CLI** - Command line for automation
   - **Web** - Browser-based with Flask
   - **GUI** - Desktop application with tkinter

✅ **Export & Import**
   - JSON for version control and backup
   - CSV for spreadsheet analysis
   - Full audit logs

## 🚀 Quick Start

### Installation

```bash
# Clone or download C-BOM
cd C-BOM

# Install dependencies
pip install -r requirements.txt

# Optional: Install Flask for web interface
pip install flask
```

### Run

```bash
# CLI Mode
python main.py --cli

# Web Mode (browser)
python main.py --web

# GUI Mode
python main.py

# Help
python main.py --help
```

## 📋 Example Usage

```python
from cbom import CryptoAsset, CryptoBOM
from cbom.validator import CryptoBOMValidator

# Create a BOM
bom = CryptoBOM("My Organization", "Cryptographic inventory")

# Add assets
asset = CryptoAsset(
    id="AES-1",
    name="AES-256-GCM",
    asset_type="algorithm",
    algorithm="AES-256-GCM",
    key_length=256,
    cipher_mode="GCM",
    purpose="encryption",
    library="OpenSSL 3.0.1",
    status="active",
    compliance=["FIPS 140-2", "PCI-DSS"],
    rotation_schedule="90 days"
)
bom.add_asset(asset)

# Check security posture
posture = CryptoBOMValidator.get_security_posture(bom)
print(f"Security Score: {posture['security_score']}/100")

# Get recommendations
recommendations = CryptoBOMValidator.get_bom_recommendations(bom)
for rec in recommendations:
    print(f"- {rec}")

# Export
bom.export_json("crypto_inventory.json")
bom.export_csv("crypto_inventory.csv")
```

## 📊 Asset Types

| Type | Purpose | Example |
|------|---------|---------|
| **algorithm** | Cryptographic algorithms | AES, RSA, SHA-256, TLS 1.3 |
| **key** | Cryptographic keys | RSA-2048 keys, AES-256 keys |
| **certificate** | X.509 certificates | TLS certificates, code signing certs |
| **library** | Crypto libraries | OpenSSL, libcrypto, Bouncy Castle |
| **cipher_suite** | Combined algorithms | TLS cipher suites, key exchange methods |

## 🔍 Validation & Compliance

C-BOM automatically:
- ✅ Validates algorithm strength
- ✅ Checks FIPS 140-2 compliance
- ✅ Verifies PCI DSS compliance
- ✅ Detects expired certificates/keys
- ✅ Tracks known CVEs
- ✅ Monitors key rotation schedules
- ✅ Identifies weak/deprecated algorithms

## 📁 Project Structure

```
C-BOM/
├── cbom/                    # Main package
│   ├── models.py           # CryptoAsset and CryptoBOM classes
│   ├── validator.py        # Validation and compliance checking
│   ├── version_control.py  # Version management and history
│   ├── hierarchical.py     # Hierarchical BOMs for complex structures
│   ├── gui.py              # Desktop GUI interface
│   ├── web_ui.py           # Web browser interface
│   └── __init__.py         # Package initialization
├── tests/                  # Test suite
│   └── test_cbom.py
├── main.py                 # Entry point (CLI, GUI, Web modes)
├── examples.py             # Usage examples
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 📚 Documentation

- **API_REFERENCE.md** - Complete API documentation for all classes and methods
- **QUICKSTART.md** - Getting started guide with step-by-step examples
- **LAUNCH_MODES.md** - Detailed guide for CLI, Web, and GUI modes
- **BUILD_STATUS.md** - Build information and feature status

## 🎯 Use Cases

1. **Security Audits** - Inventory all cryptographic components in your systems
2. **Compliance Reporting** - Generate FIPS 140-2 and PCI DSS compliance reports
3. **Vulnerability Management** - Track CVEs and plan remediation
4. **Key Lifecycle Management** - Schedule key rotations and certificate renewals
5. **Supply Chain Security** - Audit cryptographic dependencies in software
6. **Incident Response** - Quickly identify affected systems and assets

## 🔐 Security Features

- **Vulnerability Database** - Track known CVEs and CVSS scores
- **Risk Scoring** - Automatic risk assessment (0-100 scale)
- **Compliance Checking** - Standards validation (FIPS, PCI-DSS, HIPAA)
- **Audit Logging** - Full change history with timestamps and users
- **Expiration Tracking** - Certificate and key lifecycle management
- **Dependency Analysis** - Identify related vulnerabilities

## 💾 Data Persistence

- **JSON Format** - Full asset data for version control and backup
- **CSV Export** - Spreadsheet-compatible format for analysis
- **Audit Logs** - Complete history of all changes
- **Version Control** - Snapshot-based versioning with diffs

## 🛠️ Supported Standards

- ✅ **FIPS 140-2** - Federal Information Processing Standards
- ✅ **PCI DSS** - Payment Card Industry Data Security Standard
- ✅ **HIPAA** - Health Insurance Portability and Accountability Act
- ✅ **SOC 2** - Service Organization Control

## 🔒 Risk Levels

C-BOM calculates risk based on:
- **CRITICAL** - Expired assets, vulnerable algorithms, known exploits
- **HIGH** - CVSS 7.0+, weak algorithms, deprecated standards
- **MEDIUM** - CVSS 4.0-6.9, suboptimal key lengths
- **LOW** - Strong algorithms, current standards, proper key lengths

## 📝 API Quick Reference

### Creating and Managing Assets

```python
# Create asset
asset = CryptoAsset(
    id="AES-1",
    name="AES-256-GCM",
    asset_type="algorithm",
    algorithm="AES-256-GCM",
    key_length=256,
    cipher_mode="GCM",
    purpose="encryption",
    library="OpenSSL 3.0.1",
    status="active",
    compliance=["FIPS 140-2"],
    vulnerability_score=0.0,
    rotation_schedule="90 days"
)

# Add to BOM
bom.add_asset(asset)

# Query assets
critical_assets = bom.get_critical_assets()
vulnerable_assets = bom.get_vulnerable_assets()
expired_assets = bom.get_expired_assets()

# Check compliance
compliance = bom.get_compliance_status("FIPS 140-2")
```

### Validation and Analysis

```python
from cbom.validator import CryptoBOMValidator

# Validate BOM
is_valid, errors = CryptoBOMValidator.validate_bom(bom)

# Get security posture
posture = CryptoBOMValidator.get_security_posture(bom)

# Check compliance
fips_status = CryptoBOMValidator.check_compliance(bom, "FIPS 140-2")

# Get recommendations
recommendations = CryptoBOMValidator.get_bom_recommendations(bom)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📜 License

MIT License - See LICENSE file for details

## 📞 Support

For help and documentation:
- Check **API_REFERENCE.md** for detailed API documentation
- See **QUICKSTART.md** for getting started
- Review **examples.py** for code examples
- Read **LAUNCH_MODES.md** for mode-specific instructions

---

**Made with 🔐 for better cryptographic security**

*Current Version: 2.0.0 (Cryptographic Focus)*
