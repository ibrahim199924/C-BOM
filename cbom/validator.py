"""
Validation module for cryptographic assets and BOMs
"""

from typing import List, Tuple, Optional
from .models import CryptoAsset, CryptoBOM
import re


# Common weak/deprecated algorithms
WEAK_ALGORITHMS = {
    "DES": 0.0,  # 3DES variants
    "MD5": 0.0,
    "SHA-1": 0.0,
    "RC4": 0.0,
    "ECB": 0.0,  # Cipher mode
    "CBC": 4.0,  # Weak with padding oracle
    "TLS 1.0": 0.0,
    "TLS 1.1": 0.0,
    "SSL": 0.0
}

# Strong algorithms
STRONG_ALGORITHMS = {
    "AES": 10.0,
    "ChaCha20": 9.0,
    "RSA-2048": 8.0,
    "RSA-4096": 9.5,
    "ECDSA": 9.0,
    "SHA-256": 10.0,
    "SHA-3": 10.0,
    "GCM": 10.0,  # Cipher mode
    "TLS 1.2": 8.0,
    "TLS 1.3": 10.0
}

FIPS_APPROVED = ["AES", "RSA", "ECDSA", "SHA-256", "SHA-384", "SHA-512", "GCM"]
PCI_APPROVED = ["AES", "3DES", "TLS 1.2", "TLS 1.3"]


class CryptoValidator:
    """Validates individual cryptographic assets"""
    
    @staticmethod
    def validate_asset(asset: CryptoAsset) -> Tuple[bool, List[str]]:
        """
        Validate a cryptographic asset
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate ID
        if not asset.id or not isinstance(asset.id, str):
            errors.append("Asset ID must be a non-empty string")
        elif not re.match(r"^[A-Z0-9_\-]+$", asset.id):
            errors.append("Asset ID must contain only uppercase letters, numbers, hyphens, underscores")
        
        # Validate name
        if not asset.name or len(asset.name) < 3:
            errors.append("Asset name must be at least 3 characters long")
        
        # Validate asset type
        valid_types = ["algorithm", "key", "certificate", "library", "cipher_suite"]
        if asset.asset_type not in valid_types:
            errors.append(f"Asset type must be one of: {', '.join(valid_types)}")
        
        # Validate algorithm
        if not asset.algorithm:
            errors.append("Algorithm must be specified")
        
        # Validate key length
        if asset.asset_type == "key" or "key" in asset.purpose:
            if asset.key_length == 0:
                errors.append("Key length must be specified for cryptographic keys")
            elif asset.key_length < 128:
                errors.append("Key length should be at least 128 bits")
        
        # Validate status
        valid_status = ["active", "deprecated", "vulnerable", "expired", "planned"]
        if asset.status not in valid_status:
            errors.append(f"Status must be one of: {', '.join(valid_status)}")
        
        # Check if expired
        if asset.is_expired():
            errors.append("Asset has expired")
        
        # Validate purpose
        valid_purposes = ["encryption", "hashing", "signing", "key_exchange", "authentication"]
        if asset.purpose and asset.purpose not in valid_purposes:
            errors.append(f"Purpose must be one of: {', '.join(valid_purposes)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_algorithm_strength(algorithm: str) -> float:
        """Get cryptographic strength score (0-10)"""
        for weak_algo, score in WEAK_ALGORITHMS.items():
            if weak_algo.lower() in algorithm.lower():
                return score
        
        for strong_algo, score in STRONG_ALGORITHMS.items():
            if strong_algo.lower() in algorithm.lower():
                return score
        
        return 5.0  # Unknown algorithm, medium score
    
    @staticmethod
    def check_fips_compliance(asset: CryptoAsset) -> bool:
        """Check FIPS 140-2 compliance"""
        for approved in FIPS_APPROVED:
            if approved.lower() in asset.algorithm.lower():
                return True
        return False
    
    @staticmethod
    def check_pci_compliance(asset: CryptoAsset) -> bool:
        """Check PCI DSS compliance"""
        for approved in PCI_APPROVED:
            if approved.lower() in asset.algorithm.lower():
                return True
        return False
    
    @staticmethod
    def validate_batch(assets: List[CryptoAsset]) -> Tuple[bool, List[str]]:
        """Validate multiple assets at once"""
        all_errors = []
        
        for asset in assets:
            is_valid, errors = CryptoValidator.validate_asset(asset)
            if not is_valid:
                all_errors.extend([f"{asset.id}: {e}" for e in errors])
        
        return len(all_errors) == 0, all_errors


class CryptoBOMValidator:
    """Validates complete cryptographic BOMs"""
    
    @staticmethod
    def validate_bom(bom: CryptoBOM) -> Tuple[bool, List[str]]:
        """Validate entire BOM for security issues and compliance"""
        errors = []
        warnings = []
        
        if not bom.assets:
            errors.append("BOM contains no cryptographic assets")
            return False, errors
        
        # Validate all assets
        for asset in bom.assets.values():
            is_valid, asset_errors = CryptoValidator.validate_asset(asset)
            if not is_valid:
                errors.extend(asset_errors)
        
        # Check for critical vulnerabilities
        critical_assets = bom.get_critical_assets()
        if critical_assets:
            errors.extend([f"CRITICAL: Asset {a.id} has critical vulnerabilities" for a in critical_assets])
        
        # Check for expired assets
        expired = bom.get_expired_assets()
        if expired:
            errors.extend([f"CRITICAL: Asset {a.id} has expired" for a in expired])
        
        # Check for vulnerable assets
        vulnerable = bom.get_vulnerable_assets()
        if vulnerable:
            for asset in vulnerable:
                cves = '; '.join(asset.known_cves) if asset.known_cves else f"CVSS {asset.vulnerability_score}"
                warnings.append(f"Asset {asset.id} has known vulnerabilities: {cves}")
        
        # Check for deprecated algorithms
        for asset in bom.assets.values():
            strength = CryptoValidator.get_algorithm_strength(asset.algorithm)
            if strength < 4.0:
                warnings.append(f"Asset {asset.id} uses deprecated algorithm: {asset.algorithm}")
        
        # Check key rotation schedules
        for asset in bom.assets.values():
            if asset.asset_type == "key" and not asset.rotation_schedule:
                warnings.append(f"Asset {asset.id}: No key rotation schedule defined")
        
        if errors:
            return False, errors
        
        return True, warnings
    
    @staticmethod
    def get_security_posture(bom: CryptoBOM) -> dict:
        """Get overall security posture of the BOM"""
        critical = len(bom.get_critical_assets())
        vulnerable = len(bom.get_vulnerable_assets())
        expired = len(bom.get_expired_assets())
        total = len(bom.assets)
        
        # Calculate security score (0-100)
        risk_score = (critical * 40 + vulnerable * 20 + expired * 40) / total if total > 0 else 0
        security_score = max(0, 100 - risk_score)
        
        return {
            'total_assets': total,
            'critical': critical,
            'vulnerable': vulnerable,
            'expired': expired,
            'security_score': security_score,
            'posture': 'EXCELLENT' if security_score >= 90 else 'GOOD' if security_score >= 70 else 'FAIR' if security_score >= 50 else 'POOR'
        }
    
    @staticmethod
    def check_compliance(bom: CryptoBOM, standard: str) -> dict:
        """Check compliance with specific standard"""
        compliant = [a for a in bom.assets.values() if a.is_compliant(standard)]
        non_compliant = [a for a in bom.assets.values() if not a.is_compliant(standard)]
        
        return {
            'standard': standard,
            'total': len(bom.assets),
            'compliant': len(compliant),
            'non_compliant': len(non_compliant),
            'percentage': (len(compliant) / len(bom.assets) * 100) if bom.assets else 0
        }
    
    @staticmethod
    def get_bom_recommendations(bom: CryptoBOM) -> List[str]:
        """Get security recommendations for the BOM"""
        recommendations = []
        
        for asset in bom.assets.values():
            # Weak algorithm recommendations
            strength = CryptoValidator.get_algorithm_strength(asset.algorithm)
            if strength < 4.0:
                recommendations.append(f"Replace {asset.algorithm} with a stronger algorithm like AES-256-GCM")
            
            # Key rotation recommendations
            if asset.asset_type == "key" and not asset.rotation_schedule:
                recommendations.append(f"Define key rotation schedule for {asset.id}")
            
            # FIPS compliance recommendations
            if "FIPS 140-2" in asset.compliance and not CryptoValidator.check_fips_compliance(asset):
                recommendations.append(f"Asset {asset.id} claims FIPS 140-2 but uses non-approved algorithm")
            
            # Dependency check recommendations
            if asset.dependencies:
                recommendations.append(f"Review dependencies of {asset.id} for vulnerabilities")
        
        return recommendations
