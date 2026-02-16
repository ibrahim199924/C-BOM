# Cryptographic Bill of Materials (C-BOM)

A comprehensive Python tool for managing component bills of materials with advanced features including version control, hierarchical BOMs, validation, and a user-friendly GUI.

## Features

- **Component Management**: Add, edit, and delete components with detailed properties
- **BOM Tracking**: Manage complete bills of materials with cost analysis
- **Validation**: Comprehensive validation for components and BOMs
- **Version Control**: Track changes and maintain BOM history
- **Hierarchical BOMs**: Support for assemblies and sub-assemblies
- **Export/Import**: Support for JSON and CSV formats
- **Audit Logging**: Track all changes with timestamps and user information
- **GUI Interface**: User-friendly tkinter-based graphical interface
- **CLI Mode**: Command-line interface for scripting and automation

## Installation

1. Clone or download the project
2. Install Python 3.7+
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode (Default)

```bash
python main.py
```

### CLI Mode

```bash
python main.py --cli
```

## Quick Start

### Creating a BOM Programmatically

```python
from cbom import Component, ComponentBOM

# Create a new BOM
bom = ComponentBOM("My Project", "Description of the project")

# Add components
bom.add_component(Component(
    id="R1",
    name="Resistor 10k Ohm",
    category="Resistors",
    quantity=10,
    unit_cost=0.05,
    supplier="ElectroSupply",
    part_number="RS-10K"
))

# View summary
print(bom.display_summary())
print(bom.display_components())

# Export
bom.export_json("my_bom.json")
bom.export_csv("my_bom.csv")
```

### Validation

```python
from cbom import BOMValidator

is_valid, errors = BOMValidator.validate_bom(bom)
if is_valid:
    print("BOM is valid!")
else:
    print("BOM has errors:")
    for error in errors:
        print(f"  - {error}")

# Check completeness
completeness = BOMValidator.validate_bom_completeness(bom)
print(f"BOM Completeness: {completeness['overall']}%")
```

### Version Control

```python
from cbom import VersionControl

vc = VersionControl(bom)
version_id = vc.create_version("Initial BOM")
print(f"Created version: {version_id}")

# View history
history = vc.get_version_history()
for version in history:
    print(f"  {version['version_id']}: {version['message']}")
```

### Hierarchical BOMs

```python
from cbom import HierarchicalBOM, Component

main = HierarchicalBOM("Main Assembly", "Main circuit board")
sub = HierarchicalBOM("Power Supply", "Power management circuit")

main.add_subassembly(sub)

main.add_component(Component(
    id="Q1", name="Transistor", category="Semiconductors",
    quantity=1, unit_cost=0.50
))

print(main.display_tree())
```

## Project Structure

```
C-BOM/
├── cbom/                      # Main package
│   ├── __init__.py           # Package initialization
│   ├── models.py             # Core data models
│   ├── validator.py          # Validation logic
│   ├── version_control.py    # Version control system
│   ├── hierarchical.py       # Hierarchical BOM support
│   └── gui.py                # GUI interface
├── tests/
│   └── test_cbom.py          # Test suite
├── docs/                      # Documentation
├── main.py                    # Entry point
├── config.json               # Configuration
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## GUI Features

- **Project Management**: Create, open, and save BOM projects
- **Component Editor**: Add, edit, and delete components with validation
- **Cost Analysis**: Real-time calculation of total BOM cost
- **Export Options**: Export to JSON or CSV format
- **Validation Tools**: Built-in BOM validation and completeness checking
- **Audit Log**: View detailed history of all changes
- **Version History**: Track and manage BOM versions

## Validation Features

- Component ID format validation
- Cost reasonableness checks
- Supplier verification for expensive items
- Completeness metrics (part numbers, datasheets, suppliers, etc.)
- Warnings for missing information

## Data Model

### Component

A single component in the BOM with properties:
- `id`: Unique identifier
- `name`: Component name
- `category`: Component category
- `quantity`: Quantity in BOM
- `unit_cost`: Cost per unit
- `supplier`: Supplier name
- `part_number`: Supplier part number
- `description`: Detailed description
- `datasheet_url`: Link to datasheet
- `lead_time_days`: Expected delivery time
- `manufacturer`: Component manufacturer

### ComponentBOM

A complete bill of materials containing:
- Components
- Project metadata
- Audit log
- Version information
- Tags and categories

### HierarchicalBOM

A hierarchical structure supporting:
- Parent-child relationships
- Component aggregation
- Cost rollup
- Tree visualization

## Running Tests

```bash
pytest tests/test_cbom.py -v
```

## Configuration

Edit `config.json` to customize:
- Default export format
- Version control settings
- Audit logging options
- GUI theme preferences

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guide
- All tests pass
- New features include test coverage
- Documentation is updated

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue in the project repository.

## Roadmap

- [ ] Database backend support
- [ ] Multi-user collaboration
- [ ] Advanced cost analysis and forecasting
- [ ] Integration with supplier APIs
- [ ] Mobile app support
- [ ] Cloud synchronization

---

**C-BOM v1.0.0** - Professional Cryptographic Bill of Materials Management
