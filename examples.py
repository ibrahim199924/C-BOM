# Example usage of C-BOM Cryptographic Bill of Materials library

from cbom import CryptoAsset, CryptoBOM, CryptoBOMValidator, VersionControl, HierarchicalCryptoBOM

def example_tls_security_bom():
    """Example: Create a TLS/Security focused BOM with cryptographic assets"""
    bom = CryptoBOM("TLS/Security Audit", "Cryptographic assets for TLS/SSL infrastructure")
    
    # Add AES encryption algorithm
    bom.add_asset(CryptoAsset(
        id="AES-1",
        name="AES-256-GCM",
        asset_type="algorithm",
        algorithm="AES-256-GCM",
        key_length=256,
        cipher_mode="GCM",
        purpose="encryption",
        status="active",
        compliance=["FIPS 140-2", "PCI-DSS"],
        vulnerability_score=1.0
    ))
    
    # Add RSA key exchange
    bom.add_asset(CryptoAsset(
        id="RSA-1",
        name="RSA-2048 Key Exchange",
        asset_type="key",
        algorithm="RSA",
        key_length=2048,
        purpose="key_exchange",
        status="active",
        compliance=["FIPS 140-2"],
        vulnerability_score=2.5
    ))
    
    # Add TLS 1.3 cipher suite
    bom.add_asset(CryptoAsset(
        id="TLS13",
        name="TLS 1.3",
        asset_type="cipher_suite",
        algorithm="TLS 1.3",
        purpose="encryption",
        status="active",
        compliance=["FIPS 140-2", "PCI-DSS", "HIPAA"],
        vulnerability_score=0.5
    ))
    
    # Add deprecated SHA-1 (vulnerability example)
    bom.add_asset(CryptoAsset(
        id="SHA1-LEGACY",
        name="SHA-1 Hashing (Legacy)",
        asset_type="algorithm",
        algorithm="SHA-1",
        key_length=160,
        purpose="hashing",
        status="deprecated",
        known_cves=["CVE-2020-XXXX"],
        vulnerability_score=9.8
    ))
    
    return bom


def example_key_management_bom():
    """Example: Key management and lifecycle tracking"""
    bom = CryptoBOM("Key Management System", "Enterprise key inventory")
    
    # Add master key
    bom.add_asset(CryptoAsset(
        id="MK-001",
        name="Master Encryption Key",
        asset_type="key",
        algorithm="AES-256",
        key_length=256,
        purpose="encryption",
        status="active",
        compliance=["FIPS 140-2", "HIPAA"],
        rotation_schedule="Yearly",
        vulnerability_score=0.0
    ))
    
    # Add certificate
    bom.add_asset(CryptoAsset(
        id="CERT-001",
        name="TLS Certificate (Example.com)",
        asset_type="certificate",
        algorithm="RSA-2048",
        key_length=2048,
        purpose="signing",
        status="active",
        compliance=["PCI-DSS"],
        vulnerability_score=1.0
    ))
    
    # Add cryptographic library
    bom.add_asset(CryptoAsset(
        id="OPENSSL-1",
        name="OpenSSL",
        asset_type="library",
        algorithm="Multiple",
        version="3.0.0",
        status="active",
        compliance=["FIPS 140-2"],
        vulnerability_score=2.5
    ))
    
    return bom


def example_compliance_check():
    """Example: Run compliance checks on cryptographic BOM"""
    bom = example_tls_security_bom()
    
    # Validate BOM
    is_valid, messages = CryptoBOMValidator.validate_bom(bom)
    
    print("\n=== COMPLIANCE CHECK ===")
    print(f"Valid: {is_valid}")
    if not is_valid:
        for msg in messages:
            print(f"  - {msg}")
    
    # Get security posture
    posture = CryptoBOMValidator.get_security_posture(bom)
    print(f"\nSecurity Score: {posture['security_score']:.1f}/100")
    print(f"Risk Level: {posture['risk_level']}")
    
    # Get recommendations
    recommendations = CryptoBOMValidator.get_bom_recommendations(bom)
    if recommendations:
        print("\nRecommendations:")
        for rec in recommendations[:3]:
            print(f"  - {rec}")
    
    return bom


def example_vulnerability_tracking():
    """Example: Track and identify vulnerabilities"""
    bom = CryptoBOM("Vulnerability Tracking", "Track known CVEs in crypto stack")
    
    # Add vulnerable algorithm
    bom.add_asset(CryptoAsset(
        id="MD5-1",
        name="MD5 Hashing (Deprecated)",
        asset_type="algorithm",
        algorithm="MD5",
        purpose="hashing",
        status="vulnerable",
        known_cves=["CVE-2008-1385", "CVE-2005-4353"],
        vulnerability_score=9.8
    ))
    
    # Add outdated SSL
    bom.add_asset(CryptoAsset(
        id="SSL2",
        name="SSL 2.0 (Outdated)",
        asset_type="cipher_suite",
        algorithm="SSL 2.0",
        status="vulnerable",
        known_cves=["CVE-1995-XXXX"],
        vulnerability_score=10.0
    ))
    
    # Get vulnerable assets
    vulnerable = bom.get_vulnerable_assets()
    print("\n=== VULNERABLE ASSETS ===")
    for asset in vulnerable:
        print(f"{asset.id}: {asset.name}")
        print(f"  CVEs: {', '.join(asset.known_cves) if asset.known_cves else 'None'}")
        print(f"  Risk: {asset.risk_level()}")
    
    return bom


def example_hierarchical_crypto_bom():
    """Example: Hierarchical organization of crypto assets"""
    # Create parent BOM
    main = HierarchicalCryptoBOM(
        "Enterprise Cryptography",
        "Complete enterprise crypto infrastructure"
    )
    
    # Add TLS encryption sub-assembly
    tls_assembly = HierarchicalCryptoBOM(
        "TLS Encryption",
        "TLS and encryption algorithms"
    )
    
    tls_assembly.add_asset(CryptoAsset(
        id="TLS-AES",
        name="AES for TLS",
        asset_type="algorithm",
        algorithm="AES-256-GCM",
        status="active"
    ))
    
    # Add key management sub-assembly
    key_assembly = HierarchicalCryptoBOM(
        "Key Management",
        "Key generation and storage"
    )
    
    key_assembly.add_asset(CryptoAsset(
        id="KEY-GEN",
        name="PRNG",
        asset_type="library",
        algorithm="ChaCha20",
        status="active"
    ))
    
    # Add sub-assemblies to main
    main.add_sub_assembly("tls", tls_assembly)
    main.add_sub_assembly("keys", key_assembly)
    
    print("\n=== HIERARCHICAL BOM ===")
    print(main.get_hierarchy_summary())
    
    return main


if __name__ == "__main__":
    print("C-BOM Cryptographic Bill of Materials Examples\n")
    
    # Example 1: TLS Security BOM
    print("=" * 50)
    print("Example 1: TLS Security BOM")
    print("=" * 50)
    bom1 = example_tls_security_bom()
    summary = bom1.get_summary()
    print(f"Total Assets: {summary['total_assets']}")
    print(f"Critical Risk Assets: {summary['critical_risk']}")
    print(f"Vulnerable Assets: {summary['vulnerable_assets']}")
    
    # Example 2: Key Management BOM
    print("\n" + "=" * 50)
    print("Example 2: Key Management BOM")
    print("=" * 50)
    bom2 = example_key_management_bom()
    summary = bom2.get_summary()
    print(f"Total Assets: {summary['total_assets']}")
    print(f"Critical Risk Assets: {summary['critical_risk']}")
    
    # Example 3: Compliance Check
    print("\n" + "=" * 50)
    print("Example 3: Compliance Check")
    print("=" * 50)
    example_compliance_check()
    
    # Example 4: Vulnerability Tracking
    print("\n" + "=" * 50)
    print("Example 4: Vulnerability Tracking")
    print("=" * 50)
    example_vulnerability_tracking()
    
    # Example 5: Hierarchical BOM
    print("\n" + "=" * 50)
    print("Example 5: Hierarchical BOM")
    print("=" * 50)
    example_hierarchical_crypto_bom()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)
