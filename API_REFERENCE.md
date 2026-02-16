# C-BOM API Reference

## Component Class

### Constructor
```python
Component(
    id: str,
    name: str,
    category: str,
    quantity: int,
    unit_cost: float,
    supplier: Optional[str] = None,
    part_number: Optional[str] = None,
    description: Optional[str] = None,
    datasheet_url: Optional[str] = None,
    lead_time_days: Optional[int] = None,
    manufacturer: Optional[str] = None
)
```

### Methods
- `total_cost() -> float` - Calculate total cost (quantity × unit_cost)
- `to_dict() -> Dict` - Convert to dictionary
- `from_dict(data: Dict) -> Component` - Create from dictionary

## ComponentBOM Class

### Constructor
```python
ComponentBOM(project_name: str, description: str = "")
```

### Methods
- `add_component(component: Component, user: str = "unknown") -> None`
- `remove_component(component_id: str, user: str = "unknown") -> None`
- `get_component(component_id: str) -> Optional[Component]`
- `update_component(component_id: str, user: str = "unknown", **kwargs) -> None`
- `get_total_cost() -> float`
- `get_components_by_category(category: str) -> List[Component]`
- `get_summary() -> Dict`
- `export_json(filename: str) -> None`
- `export_csv(filename: str) -> None`
- `import_json(filename: str) -> None`
- `get_audit_log(component_id: Optional[str] = None) -> List[BOMAudits]`
- `display_summary() -> str` - Formatted summary text
- `display_components() -> str` - Formatted components table

## ComponentValidator Class

### Static Methods
- `validate_component(component: Component) -> Tuple[bool, List[str]]`
  - Returns: (is_valid, list_of_errors)
  - Checks: ID format, name length, category, quantity, cost, lead time, datasheet URL

- `validate_batch(components: List[Component]) -> Tuple[bool, dict]`
  - Returns: (all_valid, results_dict)
  - Results dict contains: total, valid, invalid, errors

## BOMValidator Class

### Static Methods
- `validate_bom(bom: ComponentBOM) -> Tuple[bool, List[str]]`
  - Returns: (is_valid, list_of_errors)
  - Checks: project name, duplicate IDs, component validity, minimum components, supplier coverage

- `get_bom_warnings(bom: ComponentBOM) -> List[str]`
  - Returns: non-critical warnings
  - Warns about: missing part numbers, missing datasheets, missing manufacturers, category imbalance

- `validate_bom_completeness(bom: ComponentBOM) -> dict`
  - Returns: {"overall": percentage, "details": {field: percentage}}
  - Checks: part_number, datasheet, supplier, manufacturer, lead_time coverage

## VersionControl Class

### Constructor
```python
VersionControl(bom: ComponentBOM, version_dir: str = ".cbom_versions")
```

### Methods
- `create_version(message: str = "", user: str = "unknown") -> str`
  - Returns: version_id (timestamp string)

- `get_version_history() -> List[Dict]`
  - Returns: list of version metadata

- `load_version(version_id: str) -> Optional[Dict]`
  - Returns: complete version data or None

- `get_version_diff(version_id1: str, version_id2: str) -> Dict`
  - Returns: {"added": [], "removed": [], "modified": [], "cost_change": float}

- `restore_version(version_id: str) -> bool`
  - Returns: success status

- `cleanup_old_versions(keep_count: int = 10) -> int`
  - Returns: number of deleted versions

## HierarchicalBOM Class

### Constructor
```python
HierarchicalBOM(name: str, description: str = "")
```

### Methods
- `add_subassembly(sub_bom: 'HierarchicalBOM') -> None`
- `add_component(component: Component) -> None`
- `remove_component(component_id: str) -> None`
- `get_all_components(flatten: bool = False) -> Dict[str, Component]`
  - If flatten=True: returns flat dictionary
  - If flatten=False: returns hierarchical structure

- `get_total_cost() -> float` - Includes sub-assemblies
- `get_component_count() -> int` - Includes sub-assemblies
- `get_hierarchy_summary() -> Dict` - Comprehensive hierarchy stats
- `get_by_path(path: str) -> Optional['HierarchicalBOM']`
  - Path format: "Main/Sub1/Sub2"

- `display_tree(indent: int = 0) -> str` - Formatted tree view
- `flatten_to_bom() -> ComponentBOM` - Convert to simple BOM
- `export_hierarchy_json(filename: str) -> None`

## CBOMGUI Class (Tkinter GUI)

### Constructor
```python
CBOMGUI(root: tk.Tk)
```

### Main Methods
- `setup_ui() -> None` - Initialize UI
- `new_project() -> None` - Create new BOM
- `add_component_dialog() -> None` - Add component dialog
- `edit_component_dialog() -> None` - Edit component dialog
- `delete_component_dialog() -> None` - Delete component dialog
- `validate_bom() -> None` - Run validation and show results
- `view_audit_log() -> None` - Display audit log
- `view_version_history() -> None` - Display version history
- `save_project() -> None` - Save to JSON
- `open_project() -> None` - Load from JSON
- `export_json() -> None` - Export to JSON
- `export_csv() -> None` - Export to CSV

### Usage
```python
import tkinter as tk
from cbom.gui import CBOMGUI

root = tk.Tk()
app = CBOMGUI(root)
root.mainloop()
```

## BOMAudits Class

Represents audit log entry:
```python
BOMAudits(
    timestamp: str,
    action: str,  # 'added', 'removed', 'updated'
    component_id: str,
    component_name: str,
    old_value: Optional[Dict] = None,
    new_value: Optional[Dict] = None,
    user: str = "unknown"
)
```

## Common Workflows

### Create and Save BOM
```python
from cbom import Component, ComponentBOM

bom = ComponentBOM("Project Name", "Description")
bom.add_component(Component(
    id="R1", name="Resistor", category="Resistors",
    quantity=10, unit_cost=0.05
))
bom.export_json("my_bom.json")
```

### Load and Validate
```python
bom = ComponentBOM("", "")
bom.import_json("my_bom.json")

from cbom import BOMValidator
is_valid, errors = BOMValidator.validate_bom(bom)
```

### Track Changes
```python
from cbom import VersionControl

vc = VersionControl(bom)
vc.create_version("Initial version")
# Make changes...
vc.create_version("Added components")
history = vc.get_version_history()
```

### Create Hierarchy
```python
from cbom import HierarchicalBOM

root = HierarchicalBOM("Device")
sub1 = HierarchicalBOM("Subsystem 1")
root.add_subassembly(sub1)
```

## Error Handling

All methods include proper error handling:
- `ValueError` - For invalid operations (duplicate IDs, not found, etc.)
- Validation returns errors in list format
- GUI shows errors via messagebox dialogs

## Tips

1. Always validate before exporting critical BOMs
2. Create versions before making major changes
3. Use meaningful version messages for tracking
4. Export in CSV for spreadsheet sharing
5. Use hierarchical BOMs for complex products
6. Check completeness metrics to improve data quality
7. Review audit log for change tracking
