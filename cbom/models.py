"""
C-BOM Models - Cryptographic Bill of Materials Data Models
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Set
from datetime import datetime
import json
import csv
from pathlib import Path


@dataclass
class CryptoAsset:
    """Represents a cryptographic asset (algorithm, key, certificate, library)"""
    id: str
    name: str
    asset_type: str  # "algorithm", "key", "certificate", "library", "cipher_suite"
    algorithm: str = ""  # e.g., "AES-256-GCM", "RSA-2048", "SHA-256", "TLS 1.3"
    key_length: int = 0  # in bits (256, 2048, 4096, etc.)
    cipher_mode: str = ""  # "GCM", "CBC", "ECB", "CTR", etc.
    purpose: str = ""  # "encryption", "hashing", "signing", "key_exchange"
    library: str = ""  # e.g., "OpenSSL 3.0.1", "libcrypto", "Bouncy Castle"
    version: str = ""
    status: str = "active"  # "active", "deprecated", "vulnerable", "expired", "planned"
    compliance: List[str] = field(default_factory=list)  # ["FIPS 140-2", "PCI-DSS", "HIPAA"]
    vulnerability_score: float = 0.0  # CVSS score (0-10)
    known_cves: List[str] = field(default_factory=list)  # Known CVE identifiers
    rotation_schedule: str = ""  # "90 days", "1 year", "on-demand"
    last_audit_date: str = ""  # ISO format date
    expiration_date: str = ""  # For certificates/keys
    description: str = ""
    dependencies: List[str] = field(default_factory=list)  # Other crypto assets it depends on
    notes: str = ""
    
    def risk_level(self) -> str:
        """Calculate risk level based on vulnerability score and status"""
        if self.status == "vulnerable" or self.is_expired():
            return "CRITICAL"
        if self.vulnerability_score >= 7.0:
            return "HIGH"
        if self.vulnerability_score >= 4.0:
            return "MEDIUM"
        return "LOW"
    
    def is_expired(self) -> bool:
        """Check if asset is expired"""
        if not self.expiration_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.expiration_date)
            return datetime.now() > expiry
        except:
            return False
    
    def is_compliant(self, standard: str) -> bool:
        """Check if meets specific compliance standard"""
        return standard in self.compliance
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> 'CryptoAsset':
        """Create from dictionary"""
        return CryptoAsset(**data)


@dataclass
class BOMAudits:
    """Track changes to cryptographic assets"""
    timestamp: str
    action: str  # 'added', 'removed', 'updated'
    asset_id: str
    asset_name: str
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    user: str = "unknown"


class CryptoBOM:
    """Main C-BOM manager for cryptographic assets"""
    
    def __init__(self, project_name: str, description: str = ""):
        self.project_name = project_name
        self.description = description
        self.assets: Dict[str, CryptoAsset] = {}
        self.created_date = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.audit_log: List[BOMAudits] = []
        self.tags: Set[str] = set()
        self.version = "1.0.0"
    
    def add_asset(self, asset: CryptoAsset, user: str = "unknown") -> None:
        """Add a cryptographic asset to the BOM"""
        if asset.id in self.assets:
            raise ValueError(f"Asset with ID {asset.id} already exists")
        
        self.assets[asset.id] = asset
        self.last_modified = datetime.now().isoformat()
        
        # Log audit
        audit = BOMAudits(
            timestamp=datetime.now().isoformat(),
            action="added",
            asset_id=asset.id,
            asset_name=asset.name,
            new_value=asset.to_dict(),
            user=user
        )
        self.audit_log.append(audit)
    
    def remove_asset(self, asset_id: str, user: str = "unknown") -> None:
        """Remove a cryptographic asset from the BOM"""
        if asset_id not in self.assets:
            raise ValueError(f"Asset with ID {asset_id} not found")
        
        old_asset = self.assets[asset_id]
        del self.assets[asset_id]
        self.last_modified = datetime.now().isoformat()
        
        # Log audit
        audit = BOMAudits(
            timestamp=datetime.now().isoformat(),
            action="removed",
            asset_id=asset_id,
            asset_name=old_asset.name,
            old_value=old_asset.to_dict(),
            user=user
        )
        self.audit_log.append(audit)
    
    def get_asset(self, asset_id: str) -> Optional[CryptoAsset]:
        """Retrieve an asset by ID"""
        return self.assets.get(asset_id)
    
    def update_asset(self, asset_id: str, user: str = "unknown", **kwargs) -> None:
        """Update asset properties"""
        if asset_id not in self.assets:
            raise ValueError(f"Asset with ID {asset_id} not found")
        
        asset = self.assets[asset_id]
        old_values = asset.to_dict().copy()
        
        for key, value in kwargs.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        
        self.last_modified = datetime.now().isoformat()
        
        # Log audit
        audit = BOMAudits(
            timestamp=datetime.now().isoformat(),
            action="updated",
            asset_id=asset_id,
            asset_name=asset.name,
            old_value=old_values,
            new_value=asset.to_dict(),
            user=user
        )
        self.audit_log.append(audit)
    
    def get_assets_by_type(self, asset_type: str) -> List[CryptoAsset]:
        """Get all assets of a specific type"""
        return [asset for asset in self.assets.values() if asset.asset_type == asset_type]
    
    def get_assets_by_risk(self, risk_level: str) -> List[CryptoAsset]:
        """Get all assets with specific risk level"""
        return [asset for asset in self.assets.values() if asset.risk_level() == risk_level]
    
    def get_critical_assets(self) -> List[CryptoAsset]:
        """Get all assets with CRITICAL risk"""
        return self.get_assets_by_risk("CRITICAL")
    
    def get_vulnerable_assets(self) -> List[CryptoAsset]:
        """Get all assets with known vulnerabilities"""
        return [asset for asset in self.assets.values() if asset.vulnerability_score > 0 or asset.known_cves]
    
    def get_expired_assets(self) -> List[CryptoAsset]:
        """Get all expired assets"""
        return [asset for asset in self.assets.values() if asset.is_expired()]
    
    def get_summary(self) -> Dict:
        """Get BOM summary statistics"""
        critical = len(self.get_critical_assets())
        vulnerable = len(self.get_vulnerable_assets())
        expired = len(self.get_expired_assets())
        
        asset_types = {}
        for asset in self.assets.values():
            asset_types[asset.asset_type] = asset_types.get(asset.asset_type, 0) + 1
        
        return {
            'project_name': self.project_name,
            'total_assets': len(self.assets),
            'asset_types': asset_types,
            'critical_risk': critical,
            'vulnerable_assets': vulnerable,
            'expired_assets': expired,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'version': self.version
        }
    
    def get_compliance_status(self, standard: str) -> Dict:
        """Check compliance with a specific standard"""
        compliant = [asset for asset in self.assets.values() if asset.is_compliant(standard)]
        non_compliant = [asset for asset in self.assets.values() if not asset.is_compliant(standard)]
        
        return {
            'standard': standard,
            'total_assets': len(self.assets),
            'compliant': len(compliant),
            'non_compliant': len(non_compliant),
            'compliance_percentage': (len(compliant) / len(self.assets) * 100) if self.assets else 0,
            'non_compliant_assets': [a.id for a in non_compliant]
        }
    
    def export_json(self, filename: str) -> None:
        """Export BOM to JSON"""
        data = {
            'project_name': self.project_name,
            'description': self.description,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'version': self.version,
            'assets': [asset.to_dict() for asset in self.assets.values()],
            'audit_log': [
                {
                    'timestamp': log.timestamp,
                    'action': log.action,
                    'asset_id': log.asset_id,
                    'asset_name': log.asset_name,
                    'user': log.user
                }
                for log in self.audit_log
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_json(self, filename: str) -> None:
        """Import BOM from JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.project_name = data.get('project_name', '')
        self.description = data.get('description', '')
        self.version = data.get('version', '1.0.0')
        
        for asset_data in data.get('assets', []):
            asset = CryptoAsset.from_dict(asset_data)
            self.assets[asset.id] = asset
    
    def export_csv(self, filename: str) -> None:
        """Export BOM to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Name', 'Type', 'Algorithm', 'Key Length', 'Purpose',
                'Status', 'Risk Level', 'Vulnerability Score', 'CVEs', 'Compliance'
            ])
            
            # Data rows
            for asset in self.assets.values():
                writer.writerow([
                    asset.id,
                    asset.name,
                    asset.asset_type,
                    asset.algorithm,
                    asset.key_length,
                    asset.purpose,
                    asset.status,
                    asset.risk_level(),
                    asset.vulnerability_score,
                    ';'.join(asset.known_cves),
                    ';'.join(asset.compliance)
                ])
    
    def display_summary(self) -> str:
        """Display BOM summary as formatted text"""
        summary = self.get_summary()
        
        output = f"""
C-BOM - Cryptographic Bill of Materials
========================================

Project: {summary['project_name']}
Total Assets: {summary['total_assets']}
Critical Risk: {summary['critical_risk']}
Vulnerable Assets: {summary['vulnerable_assets']}
Expired Assets: {summary['expired_assets']}

Asset Types:
"""
        for asset_type, count in summary['asset_types'].items():
            output += f"  {asset_type}: {count}\n"
        
        return output
    
    def display_assets(self) -> str:
        """Display all assets as formatted table"""
        if not self.assets:
            return "No cryptographic assets found.\n"
        
        output = "\nCryptographic Assets:\n"
        output += "-" * 130 + "\n"
        output += f"{'ID':<10} {'Name':<25} {'Type':<15} {'Algorithm':<20} {'Risk':<10} {'CVEs':<10} {'Status':<12}\n"
        output += "-" * 130 + "\n"
        
        for asset in self.assets.values():
            cve_count = len(asset.known_cves)
            output += f"{asset.id:<10} {asset.name:<25} {asset.asset_type:<15} {asset.algorithm:<20} {asset.risk_level():<10} {cve_count:<10} {asset.status:<12}\n"
        
        output += "-" * 130 + "\n"
        return output
    
    def get_audit_log(self) -> str:
        """Display audit log"""
        if not self.audit_log:
            return "No audit log entries.\n"
        
        output = "\nAudit Log:\n"
        output += "-" * 100 + "\n"
        output += f"{'Timestamp':<25} {'Action':<10} {'Asset ID':<10} {'Asset Name':<25} {'User':<15}\n"
        output += "-" * 100 + "\n"
        
        for log in self.audit_log[-10:]:  # Last 10 entries
            output += f"{log.timestamp:<25} {log.action:<10} {log.asset_id:<10} {log.asset_name:<25} {log.user:<15}\n"
        
        output += "-" * 100 + "\n"
        return output
