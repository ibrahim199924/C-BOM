"""
Version control module for tracking cryptographic BOM changes
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from .models import CryptoBOM


class VersionControl:
    """Manages version history of cryptographic BOMs"""
    
    def __init__(self, bom: CryptoBOM, version_dir: str = ".cbom_versions"):
        self.bom = bom
        self.version_dir = Path(version_dir)
        self.version_dir.mkdir(exist_ok=True)
        self.version_history: List[Dict] = []
    
    def create_version(self, message: str = "", user: str = "unknown") -> str:
        """
        Create a new version of the cryptographic BOM
        Returns: version ID
        """
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_file = self.version_dir / f"{self.bom.project_name}_{version_id}.json"
        
        version_data = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "user": user,
            "bom_summary": self.bom.get_summary(),
            "components_count": len(self.bom.assets),
        }
        
        # Save BOM data
        bom_export = {
            "metadata": self.bom.get_summary(),
            "assets": [asset.to_dict() for asset in self.bom.assets.values()],
            "audit_log": [
                {
                    "timestamp": audit.timestamp,
                    "action": audit.action,
                    "asset_id": audit.asset_id,
                    "asset_name": audit.asset_name,
                    "user": audit.user
                }
                for audit in self.bom.audit_log
            ]
        }
        
        with open(version_file, 'w') as f:
            json.dump(bom_export, f, indent=2)
        
        self.version_history.append(version_data)
        return version_id
    
    def get_version_history(self) -> List[Dict]:
        """Get list of all versions"""
        return self.version_history.copy()
    
    def load_version(self, version_id: str) -> Optional[Dict]:
        """Load a specific version"""
        version_file = self.version_dir / f"{self.bom.project_name}_{version_id}.json"
        
        if not version_file.exists():
            return None
        
        with open(version_file, 'r') as f:
            return json.load(f)
    
    def get_version_diff(self, version_id1: str, version_id2: str) -> Dict:
        """Compare two versions"""
        v1_data = self.load_version(version_id1)
        v2_data = self.load_version(version_id2)
        
        if not v1_data or not v2_data:
            return {"error": "One or both versions not found"}
        
        v1_assets = {a['id']: a for a in v1_data.get('assets', [])}
        v2_assets = {a['id']: a for a in v2_data.get('assets', [])}
        
        diff = {
            "added": [],
            "removed": [],
            "modified": [],
        }
        
        # Find added and modified
        for asset_id, asset_data in v2_assets.items():
            if asset_id not in v1_assets:
                diff["added"].append(asset_id)
            elif v1_assets[asset_id] != asset_data:
                diff["modified"].append(asset_id)
        
        # Find removed
        for asset_id in v1_assets:
            if asset_id not in v2_assets:
                diff["removed"].append(asset_id)
        
        return diff
    
    def restore_version(self, version_id: str) -> bool:
        """Restore a previous version"""
        version_data = self.load_version(version_id)
        if not version_data:
            return False
        
        # Clear current assets
        self.bom.assets.clear()
        
        # Load assets from version
        for asset_data in version_data.get('assets', []):
            from .models import CryptoAsset
            asset = CryptoAsset.from_dict(asset_data)
            self.bom.assets[asset.id] = asset
        
        self.bom.last_modified = datetime.now().isoformat()
        return True
    
    def cleanup_old_versions(self, keep_count: int = 10) -> int:
        """Delete old versions, keeping only the most recent"""
        if len(self.version_history) <= keep_count:
            return 0
        
        deleted_count = 0
        versions_to_delete = self.version_history[:-keep_count]
        
        for version_info in versions_to_delete:
            version_file = self.version_dir / f"{self.bom.project_name}_{version_info['version_id']}.json"
            if version_file.exists():
                version_file.unlink()
                deleted_count += 1
        
        self.version_history = self.version_history[-keep_count:]
        return deleted_count
