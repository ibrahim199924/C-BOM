"""
Main entry point for C-BOM (Cryptographic Bill of Materials)
"""

from cbom import CryptoAsset, CryptoBOM
import sys


def cli_mode():
    """Run in CLI mode"""
    print("C-BOM - Cryptographic Bill of Materials Tool")
    print("=============================================\n")
    
    # Create example crypto BOM
    bom = CryptoBOM("TLS/Encryption Audit", "Organization's cryptographic assets inventory")
    
    # Add cryptographic assets
    bom.add_asset(CryptoAsset(
        id="AES-1", name="AES-256-GCM Data Encryption", asset_type="algorithm",
        algorithm="AES-256-GCM", key_length=256, cipher_mode="GCM", purpose="encryption",
        library="OpenSSL 3.0.1", status="active",
        compliance=["FIPS 140-2", "PCI-DSS"], vulnerability_score=0.0,
        rotation_schedule="90 days", description="Primary encryption algorithm"
    ))
    
    bom.add_asset(CryptoAsset(
        id="RSA-1", name="RSA-2048 Key Exchange", asset_type="key",
        algorithm="RSA-2048", key_length=2048, purpose="key_exchange",
        library="OpenSSL 3.0.1", status="active",
        compliance=["FIPS 140-2"], vulnerability_score=0.0,
        rotation_schedule="1 year", description="TLS key exchange"
    ))
    
    bom.add_asset(CryptoAsset(
        id="TLS13", name="TLS 1.3 Cipher Suite", asset_type="cipher_suite",
        algorithm="TLS 1.3", purpose="authentication",
        library="OpenSSL 3.0.1", status="active",
        compliance=["FIPS 140-2", "PCI-DSS"], vulnerability_score=0.0,
        description="Modern TLS protocol"
    ))
    
    bom.add_asset(CryptoAsset(
        id="LEGACY", name="Legacy SHA-1 Hashing", asset_type="algorithm",
        algorithm="SHA-1", purpose="hashing",
        library="OpenSSL 1.1.1", status="deprecated",
        vulnerability_score=8.5, known_cves=["CVE-2020-12345"],
        description="Legacy hash - deprecated, should replace with SHA-256"
    ))
    
    # Display
    print(bom.display_summary())
    print(bom.display_assets())
    print(bom.get_audit_log())
    
    # Export
    bom.export_json("example_cbom.json")
    bom.export_csv("example_cbom.csv")
    
    # Show vulnerability report
    print("\n=== SECURITY POSTURE ===")
    from cbom.validator import CryptoBOMValidator
    posture = CryptoBOMValidator.get_security_posture(bom)
    print(f"Security Score: {posture['security_score']:.1f}/100 ({posture['posture']})")
    print(f"Critical Assets: {posture['critical']}")
    print(f"Vulnerable Assets: {posture['vulnerable']}")
    print(f"Expired Assets: {posture['expired']}\n")


def gui_mode():
    """Run in GUI mode with fallback support"""
    # Try tkinter GUI first
    try:
        import tkinter as tk
        from cbom.gui import CBOMGUI
        
        root = tk.Tk()
        app = CBOMGUI(root)
        root.mainloop()
        return
    except Exception as e:
        print(f"GUI mode unavailable ({type(e).__name__})")
    
    # Try Flask web UI
    try:
        print("\nAttempting to start web interface...\n")
        from cbom.web_ui import create_web_ui
        from cbom import CryptoBOM
        
        bom = CryptoBOM("C-BOM Web Project")
        create_web_ui(bom)
        return
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
    except Exception as e:
        print(f"Web UI unavailable ({type(e).__name__}): {e}")
    
    # Fallback to CLI mode
    print("\nNo GUI available. Running in CLI mode instead...\n")
    cli_mode()


def web_mode(port: int = 5000):
    """Run in web mode"""
    try:
        from cbom.web_ui import create_web_ui
        from cbom import CryptoBOM
        
        bom = CryptoBOM("C-BOM Web Project")
        create_web_ui(bom, port=port)
    except ImportError:
        print("ERROR: Flask is required for web mode")
        print("Install with: pip install flask")
        sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--cli':
            cli_mode()
        elif sys.argv[1] == '--web':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            web_mode(port)
        elif sys.argv[1] == '--help':
            print("C-BOM - Cryptographic Bill of Materials Management Tool")
            print("\nUsage: python main.py [option]")
            print("\nOptions:")
            print("  (no option)   - Launch GUI (with CLI/web fallback)")
            print("  --cli         - Launch CLI mode")
            print("  --web [port]  - Launch web interface (default port 5000)")
            print("  --help        - Show this help message")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        gui_mode()


if __name__ == "__main__":
    main()
