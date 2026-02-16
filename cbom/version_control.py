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
            "components_count": len(self.bom.components),
            "total_cost": self.bom.get_total_cost()
        }
        
        # Save BOM data
        bom_export = {
            "metadata": self.bom.get_summary(),
            "components": [comp.to_dict() for comp in self.bom.components.values()],
            "audit_log": [
                {
                    "timestamp": audit.timestamp,
                    "action": audit.action,
                    "component_id": audit.component_id,
                    "component_name": audit.component_name,
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
        
        v1_components = {c['id']: c for c in v1_data.get('components', [])}
        v2_components = {c['id']: c for c in v2_data.get('components', [])}
        
        diff = {
            "added": [],
            "removed": [],
            "modified": [],
            "cost_change": v2_data['metadata']['total_cost'] - v1_data['metadata']['total_cost']
        }
        
        # Find added and modified
        for comp_id, comp_data in v2_components.items():
            if comp_id not in v1_components:
                diff["added"].append(comp_id)
            elif v1_components[comp_id] != comp_data:
                diff["modified"].append(comp_id)
        
        # Find removed
        for comp_id in v1_components:
            if comp_id not in v2_components:
                diff["removed"].append(comp_id)
        
        return diff
    
    def restore_version(self, version_id: str) -> bool:
        """Restore a previous version"""
        version_data = self.load_version(version_id)
        if not version_data:
            return False
        
        # Clear current components
        self.bom.components.clear()
        
        # Load components from version
        for comp_data in version_data.get('components', []):
            from .models import Component
            component = Component.from_dict(comp_data)
            self.bom.components[component.id] = component
        
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
