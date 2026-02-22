# C-BOM Cryptographic Bill of Materials - Quick Start Guide

Welcome to **C-BOM**, a tool for managing cryptographic assets. This guide gets you up and running in 5 minutes.

## Installation (1 minute)

```bash
# Navigate to C-BOM directory
cd C-BOM

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Flask for web interface
pip install flask
```

## Launch C-BOM (Choose One Mode)

### 1. Command Line Interface (Fastest)

```bash
python main.py --cli
```

**Output shows:**
- List of all cryptographic assets
- Risk assessment for each asset
- Security posture score
- Vulnerable assets and their CVEs
- Exported files (JSON, CSV)

### 2. Web Browser Interface (Most User-Friendly)

```bash
python main.py --web
```

**Then:**
- Browser opens to `http://localhost:5000`
- Add/manage cryptographic assets visually
- View vulnerability dashboard
- Generate compliance reports
- Export to JSON/CSV

### 3. Desktop GUI (Full-Featured)

```bash
python main.py
```

**Features:**
- Desktop application
- Menu-driven interface
- Component management dialogs
- Real-time validation
- Audit log viewer

## Basic Usage

### Create Your First Cryptographic BOM

```python
from cbom import CryptoAsset, CryptoBOM

# Create a BOM for your organization
bom = CryptoBOM("My Organization", "Cryptographic Asset Inventory")

# Add an encryption algorithm
aes = CryptoAsset(
    id="AES-1",
    name="AES-256-GCM for Data at Rest",
    asset_type="algorithm",
    algorithm="AES-256-GCM",
    key_length=256,
    cipher_mode="GCM",
    purpose="encryption",
    library="OpenSSL 3.0.1",
    version="3.0.1",
    status="active",
    compliance=["FIPS 140-2", "PCI-DSS"],
    rotation_schedule="90 days",
    description="Primary encryption algorithm for all sensitive data"
)
bom.add_asset(aes)

# Add a key
rsa_key = CryptoAsset(
    id="RSA-KEY-1",
    name="RSA-2048 TLS Key",
    asset_type="key",
    algorithm="RSA-2048",
    key_length=2048,
    purpose="key_exchange",
    library="OpenSSL 3.0.1",
    status="active",
    compliance=["FIPS 140-2"],
    rotation_schedule="1 year",
    expiration_date="2027-02-16"
)
bom.add_asset(rsa_key)

# Add a deprecated algorithm (to track for remediation)
sha1_legacy = CryptoAsset(
    id="SHA1-LEGACY",
    name="Legacy SHA-1 Hash",
    asset_type="algorithm",
    algorithm="SHA-1",
    purpose="hashing",
    status="deprecated",
    vulnerability_score=8.5,
    known_cves=["CVE-2020-12345"],
    description="Legacy algorithm - should be replaced with SHA-256"
)
bom.add_asset(sha1_legacy)

# Export your BOM
bom.export_json("my_crypto_inventory.json")
bom.export_csv("my_crypto_inventory.csv")

print(bom.display_summary())
print(bom.display_assets())
```

### Validate and Check Compliance

```python
from cbom.validator import CryptoBOMValidator

# Validate the entire BOM
is_valid, messages = CryptoBOMValidator.validate_bom(bom)
if not is_valid:
    print("Validation errors:")
    for msg in messages:
        print(f"  - {msg}")

# Check security posture
posture = CryptoBOMValidator.get_security_posture(bom)
print(f"Security Score: {posture['security_score']}/100")
print(f"Posture: {posture['posture']}")

# Check FIPS 140-2 compliance
fips_status = CryptoBOMValidator.check_compliance(bom, "FIPS 140-2")
print(f"FIPS Compliant: {fips_status['compliant']}/{fips_status['total']}")

# Get security recommendations
recommendations = CryptoBOMValidator.get_bom_recommendations(bom)
print("\nSecurity Recommendations:")
for rec in recommendations:
    print(f"  ⚠️  {rec}")
```

## Common Tasks

### Add Multiple Assets at Once

```python
# Define multiple assets
assets = [
    CryptoAsset(id="TLS13", name="TLS 1.3", asset_type="cipher_suite", 
                algorithm="TLS 1.3", purpose="authentication", 
                status="active", compliance=["FIPS 140-2"]),
    
    CryptoAsset(id="AES-256", name="AES-256-CBC", asset_type="algorithm",
                algorithm="AES-256-CBC", key_length=256,
                status="active", compliance=["PCI-DSS"]),
]

# Add all to BOM
for asset in assets:
    bom.add_asset(asset)
```

### Find Vulnerable Assets

```python
# Get all assets with vulnerabilities
vulnerable = bom.get_vulnerable_assets()
print(f"Found {len(vulnerable)} vulnerable assets:")
for asset in vulnerable:
    if asset.known_cves:
        print(f"  {asset.id}: {', '.join(asset.known_cves)}")
    else:
        print(f"  {asset.id}: CVSS {asset.vulnerability_score}")

# Get critical risk assets
critical = bom.get_critical_assets()
print(f"\nCRITICAL: {len(critical)} assets need immediate attention")
```

### Check Key Rotation

```python
# Find assets that need rotation
for asset in bom.assets.values():
    if asset.asset_type == "key" and asset.rotation_schedule:
        print(f"{asset.id}: Rotate every {asset.rotation_schedule}")
```

### Export and Share

```python
# Export to JSON (for version control)
bom.export_json("crypto_inventory.json")

# Export to CSV (for Excel/spreadsheets)
bom.export_csv("crypto_inventory.csv")

# CSV includes columns:
# ID, Name, Type, Algorithm, Key Length, Purpose, Status, Risk Level, CVEs, Compliance
```

## Asset Properties Reference

### Required Fields
- `id` - Unique identifier (e.g., "AES-1")
- `name` - Human-readable name
- `asset_type` - One of: algorithm, key, certificate, library, cipher_suite
- `algorithm` - Algorithm name (e.g., "AES-256-GCM")

### Crypto-Specific Fields
- `key_length` - Size in bits (256, 2048, 4096, etc.)
- `cipher_mode` - Encryption mode (GCM, CBC, ECB, etc.)
- `purpose` - encryption, hashing, signing, key_exchange, authentication
- `library` - Crypto library (OpenSSL 3.0.1, libcrypto, etc.)
- `status` - active, deprecated, vulnerable, expired, planned
- `compliance` - List of standards (FIPS 140-2, PCI-DSS, HIPAA)
- `vulnerability_score` - CVSS score (0-10)
- `known_cves` - List of CVE identifiers
- `rotation_schedule` - Key rotation interval (e.g., "90 days")
- `expiration_date` - ISO date format (e.g., "2027-02-16")
- `dependencies` - IDs of related assets

## Risk Levels Explained

| Level | Meaning | Example |
|-------|---------|---------|
| **CRITICAL** | Immediate action needed | Expired certificates, vulnerable algorithms |
| **HIGH** | Should be remediated soon | CVSS 7.0+, weak algorithms |
| **MEDIUM** | Plan for remediation | CVSS 4.0-6.9, suboptimal settings |
| **LOW** | Acceptable | Strong algorithms, current standards |

## Next Steps

1. **Review documentation**:
   - `API_REFERENCE.md` - Full API documentation
   - `LAUNCH_MODES.md` - Detailed mode information
   - `examples.py` - More code examples

2. **Try the web interface**:
   ```bash
   pip install flask
   python main.py --web
   ```

3. **Set up version control**:
   ```bash
   git init
   git add crypto_inventory.json
   git commit -m "Initial cryptographic inventory"
   ```

4. **Schedule regular audits**:
   - Run monthly to check for new CVEs
   - Review key rotation schedules
   - Check compliance status

## Troubleshooting

### "No module named 'flask'"
```bash
pip install flask
```

### GUI won't launch on Windows
```bash
# Use web mode instead
python main.py --web
```

### CSV not exporting
```bash
# Make sure no assets have special characters in names
# Or use JSON export instead
bom.export_json("inventory.json")
```

## Examples

See `examples.py` for more complete examples including:
- Creating hierarchical BOMs
- Version control workflows
- Batch validation
- Compliance checking

---

**Need help?** Check the documentation in README_CRYPTO.md or run:
```bash
python main.py --help
```
