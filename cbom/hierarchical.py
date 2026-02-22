"""
Hierarchical cryptographic BOM support for complex asset structures
"""

from typing import Dict, List, Optional
from .models import CryptoAsset, CryptoBOM


class HierarchicalCryptoBOM:
    """Manages hierarchical cryptographic BOMs with categories and dependencies"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.parent_id: Optional[str] = None
        self.children: Dict[str, 'HierarchicalCryptoBOM'] = {}
        self.assets: Dict[str, CryptoAsset] = {}
        self.level = 0
    
    def add_subassembly(self, sub_bom: 'HierarchicalCryptoBOM') -> None:
        """Add a sub-category/sub-system"""
        sub_bom.parent_id = self.name
        sub_bom.level = self.level + 1
        self.children[sub_bom.name] = sub_bom
    
    def add_asset(self, asset: CryptoAsset) -> None:
        """Add a cryptographic asset to this category level"""
        if asset.id in self.assets:
            raise ValueError(f"Asset {asset.id} already exists at this level")
        self.assets[asset.id] = asset
    
    def remove_asset(self, asset_id: str) -> None:
        """Remove an asset from this category"""
        if asset_id not in self.assets:
            raise ValueError(f"Asset {asset_id} not found")
        del self.assets[asset_id]
    
    def get_all_assets(self, flatten: bool = False) -> Dict[str, CryptoAsset]:
        """
        Get all assets including those in sub-categories
        If flatten=True, returns flat dict. If False, returns hierarchical dict.
        """
        if flatten:
            all_assets = self.assets.copy()
            for child_bom in self.children.values():
                all_assets.update(child_bom.get_all_assets(flatten=True))
            return all_assets
        else:
            result = {
                "level": self.level,
                "name": self.name,
                "assets": self.assets.copy(),
                "children": {}
            }
            for child_name, child_bom in self.children.items():
                result["children"][child_name] = child_bom.get_all_assets(flatten=False)
            return result
    
    def get_asset_count(self) -> int:
        """Get total asset count including sub-categories"""
        count = len(self.assets)
        for child_bom in self.children.values():
            count += child_bom.get_asset_count()
        return count
    
    def get_critical_count(self) -> int:
        """Get count of critical/vulnerable assets"""
        count = sum(1 for a in self.assets.values() if a.risk_level() == "CRITICAL")
        for child_bom in self.children.values():
            count += child_bom.get_critical_count()
        return count
    
    def get_hierarchy_summary(self) -> Dict:
        """Get summary of the hierarchical structure"""
        summary = {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "assets_at_level": len(self.assets),
            "total_assets": self.get_asset_count(),
            "critical_assets": self.get_critical_count(),
            "sub_categories": len(self.children),
            "children": {}
        }
        
        for child_name, child_bom in self.children.items():
            summary["children"][child_name] = child_bom.get_hierarchy_summary()
        
        return summary
    
    def get_by_path(self, path: str) -> Optional['HierarchicalCryptoBOM']:
        """
        Get a sub-category by path (e.g., "TLS/Certificates/Intermediate")
        Returns None if path not found
        """
        parts = path.split("/")
        current = self
        
        for part in parts:
            if part == self.name:
                continue
            if part in current.children:
                current = current.children[part]
            else:
                return None
        
        return current
    
    def display_tree(self, indent: int = 0) -> str:
        """Get formatted tree view of the hierarchy"""
        lines = []
        prefix = "  " * indent
        
        lines.append(f"{prefix}├─ {self.name}")
        if self.description:
            lines.append(f"{prefix}│  Description: {self.description}")
        
        lines.append(f"{prefix}│  Assets: {len(self.assets)}, Critical: {self.get_critical_count()}")
        
        for asset in self.assets.values():
            risk = asset.risk_level()
            lines.append(f"{prefix}│  ├─ {asset.id}: {asset.name} [{risk}]")
        
        for i, (child_name, child_bom) in enumerate(self.children.items()):
            child_tree = child_bom.display_tree(indent + 1)
            lines.append(child_tree)
        
        return "\n".join(lines)
    
    def flatten_to_bom(self) -> CryptoBOM:
        """Convert hierarchical BOM to flat CryptoBOM"""
        flat_bom = CryptoBOM(self.name, self.description)
        
        # Collect all assets
        all_assets = self.get_all_assets(flatten=True)
        for asset in all_assets.values():
            flat_bom.assets[asset.id] = asset
        
        return flat_bom
    
    def export_hierarchy_json(self, filename: str) -> None:
        """Export the complete hierarchy to JSON"""
        import json
        
        def hierarchical_to_dict(hbom: 'HierarchicalCryptoBOM') -> Dict:
            return {
                "name": hbom.name,
                "description": hbom.description,
                "level": hbom.level,
                "assets": [asset.to_dict() for asset in hbom.assets.values()],
                "children": {
                    child_name: hierarchical_to_dict(child_bom)
                    for child_name, child_bom in hbom.children.items()
                }
            }
        
        data = hierarchical_to_dict(self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
