"""
Test suite for C-BOM (Cryptographic Bill of Materials)
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cbom import CryptoAsset, CryptoBOM, CryptoValidator, CryptoBOMValidator, HierarchicalCryptoBOM


class TestCryptoAsset:

    def test_asset_creation(self):
        asset = CryptoAsset(id="AES-1", name="AES Encryption", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        assert asset.id == "AES-1"
        assert asset.algorithm == "AES-256-GCM"
        assert asset.key_length == 256

    def test_risk_level_low(self):
        asset = CryptoAsset(id="AES-1", name="AES Encryption", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256, status="active")
        assert asset.risk_level() == "LOW"

    def test_risk_level_high_weak_algo(self):
        asset = CryptoAsset(id="SHA1-1", name="Legacy Hash", asset_type="algorithm", algorithm="SHA-1", key_length=160, status="active")
        assert asset.risk_level() in ("HIGH", "CRITICAL")

    def test_risk_level_critical_vulnerable(self):
        asset = CryptoAsset(id="RC4-1", name="RC4 Stream", asset_type="algorithm", algorithm="RC4", key_length=128, status="vulnerable")
        assert asset.risk_level() == "CRITICAL"

    def test_risk_level_deprecated(self):
        asset = CryptoAsset(id="DES-1", name="DES Key", asset_type="key", algorithm="DES", key_length=56, status="deprecated")
        assert asset.risk_level() in ("HIGH", "CRITICAL")

    def test_auto_detect_status_active(self):
        assert CryptoAsset.auto_detect_status("AES-256-GCM") == "active"

    def test_auto_detect_status_deprecated(self):
        assert CryptoAsset.auto_detect_status("SHA-1") == "deprecated"

    def test_auto_detect_status_vulnerable(self):
        assert CryptoAsset.auto_detect_status("MD5") == "vulnerable"

    def test_is_expired_false(self):
        asset = CryptoAsset(id="CERT-1", name="Cert", asset_type="certificate", algorithm="X.509")
        assert not asset.is_expired()

    def test_is_expired_true(self):
        asset = CryptoAsset(id="CERT-OLD", name="Old Cert", asset_type="certificate", algorithm="X.509", expiration_date="2020-01-01")
        assert asset.is_expired()


class TestCryptoBOM:

    def test_bom_creation(self):
        bom = CryptoBOM("Test BOM")
        assert bom.project_name == "Test BOM"
        assert len(bom.assets) == 0

    def test_add_asset(self):
        bom = CryptoBOM("Test BOM")
        asset = CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        bom.add_asset(asset)
        assert len(bom.assets) == 1
        assert bom.assets["AES-1"] == asset

    def test_add_duplicate_raises(self):
        bom = CryptoBOM("Test BOM")
        asset = CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        bom.add_asset(asset)
        with pytest.raises(ValueError):
            bom.add_asset(asset)

    def test_remove_asset(self):
        bom = CryptoBOM("Test BOM")
        asset = CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        bom.add_asset(asset)
        bom.remove_asset("AES-1")
        assert len(bom.assets) == 0

    def test_get_vulnerable_assets(self):
        bom = CryptoBOM("Test BOM")
        bom.add_asset(CryptoAsset(id="OK-1", name="Good Asset", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        bom.add_asset(CryptoAsset(id="BAD-1", name="Bad Asset", asset_type="algorithm", algorithm="RC4", key_length=128, vulnerability_score=9.0))
        vulnerable = bom.get_vulnerable_assets()
        assert any(a.id == "BAD-1" for a in vulnerable)

    def test_get_summary(self):
        bom = CryptoBOM("Test BOM")
        bom.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        summary = bom.get_summary()
        assert summary["total_assets"] == 1

    def test_audit_log_on_add(self):
        bom = CryptoBOM("Test BOM")
        bom.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        assert len(bom.audit_log) == 1
        assert bom.audit_log[0].action == "added"


class TestCryptoValidator:

    def test_valid_asset(self):
        asset = CryptoAsset(id="AES-1", name="AES Encryption", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        is_valid, errors = CryptoValidator.validate_asset(asset)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_id_lowercase(self):
        asset = CryptoAsset(id="aes-1", name="AES Encryption", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        is_valid, errors = CryptoValidator.validate_asset(asset)
        assert not is_valid

    def test_short_name_invalid(self):
        asset = CryptoAsset(id="AES-1", name="AE", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256)
        is_valid, errors = CryptoValidator.validate_asset(asset)
        assert not is_valid

    def test_key_missing_length(self):
        asset = CryptoAsset(id="KEY-1", name="Signing Key", asset_type="key", algorithm="RSA-2048", key_length=0)
        is_valid, errors = CryptoValidator.validate_asset(asset)
        assert not is_valid

    def test_algorithm_strength_strong(self):
        score = CryptoValidator.get_algorithm_strength("AES-256-GCM")
        assert score >= 8.0

    def test_algorithm_strength_weak(self):
        score = CryptoValidator.get_algorithm_strength("MD5")
        assert score < 4.0


class TestCryptoBOMValidator:

    def test_empty_bom_invalid(self):
        bom = CryptoBOM("Empty")
        is_valid, errors = CryptoBOMValidator.validate_bom(bom)
        assert not is_valid

    def test_valid_bom(self):
        bom = CryptoBOM("Good BOM")
        bom.add_asset(CryptoAsset(id="AES-1", name="AES Encryption", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        is_valid, _ = CryptoBOMValidator.validate_bom(bom)
        assert is_valid

    def test_security_posture(self):
        bom = CryptoBOM("Test BOM")
        bom.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        posture = CryptoBOMValidator.get_security_posture(bom)
        assert "security_score" in posture
        assert 0 <= posture["security_score"] <= 100

    def test_security_score_drops_with_vulnerable(self):
        bom = CryptoBOM("Test BOM")
        bom.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        score_clean = CryptoBOMValidator.get_security_posture(bom)["security_score"]
        bom.add_asset(CryptoAsset(id="RC4-1", name="RC4 Stream", asset_type="algorithm", algorithm="RC4", key_length=128, vulnerability_score=9.0))
        score_vuln = CryptoBOMValidator.get_security_posture(bom)["security_score"]
        assert score_vuln < score_clean


class TestHierarchicalCryptoBOM:

    def test_hierarchy_creation(self):
        main = HierarchicalCryptoBOM("Main System")
        sub = HierarchicalCryptoBOM("TLS Layer")
        main.add_subassembly(sub)
        assert "TLS Layer" in main.children

    def test_hierarchy_asset(self):
        main = HierarchicalCryptoBOM("Main System")
        main.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        assert len(main.assets) == 1

    def test_get_all_assets_flat(self):
        main = HierarchicalCryptoBOM("Main")
        main.add_asset(CryptoAsset(id="AES-1", name="AES Enc", asset_type="algorithm", algorithm="AES-256-GCM", key_length=256))
        sub = HierarchicalCryptoBOM("Sub")
        sub.add_asset(CryptoAsset(id="RSA-1", name="RSA Key", asset_type="key", algorithm="RSA-2048", key_length=2048))
        main.add_subassembly(sub)
        all_assets = main.get_all_assets(flatten=True)
        assert "AES-1" in all_assets
        assert "RSA-1" in all_assets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
