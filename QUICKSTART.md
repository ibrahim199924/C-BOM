# C-BOM Quick Start Guide

## Installation

1. Navigate to the project directory:
```bash
cd c:\Users\ibrah\Documents\C-BOM
```

2. Install dependencies (pytest is optional, for testing):
```bash
pip install -r requirements.txt
```

## Launching the Application

### GUI Mode (Recommended)
```bash
python main.py
```

This opens the full graphical interface where you can:
- Create new projects
- Add components with all details
- View real-time cost calculations
- Export to JSON/CSV
- Validate BOMs
- View change history

### CLI Mode (Quick Demo)
```bash
python main.py --cli
```

This demonstrates the tool by creating an example electronics BOM and exporting it.

### View Examples
```bash
python examples.py
```

Shows comprehensive usage examples including:
- Creating basic BOMs
- Validating data
- Using version control
- Creating hierarchical structures

## First Steps

### 1. Create a New Project
- Launch `python main.py`
- File → New Project
- Enter project name and description
- Click OK

### 2. Add Components
- Click "Add Component" button
- Fill in component details:
  - **ID**: Unique identifier (e.g., R1, C1)
  - **Name**: Full component name
  - **Category**: Component type (Resistors, ICs, etc.)
  - **Quantity**: How many you need
  - **Unit Cost**: Price per unit
  - **Supplier**: Where to buy (optional)
  - **Part Number**: Supplier's part number (optional)
  - **Lead Time**: Expected delivery days (optional)

### 3. Review Your BOM
- Components appear in the tree view
- Summary shows total count and cost
- Table columns show all details at a glance

### 4. Validate Your Work
- Tools → Validate BOM
- See validation errors (if any)
- Check completeness percentage
- Review warnings for missing data

### 5. Save Your Work
- File → Save
- Choose location for JSON file
- BOMs can be reopened later

### 6. Export Data
- File → Export as JSON (for backup/sharing)
- File → Export as CSV (for spreadsheets like Excel)

## Common Tasks

### Edit a Component
1. Click on component in list
2. Click "Edit" button
3. Modify fields
4. Click "Save Changes"

### Delete a Component
1. Click on component in list
2. Click "Delete" button
3. Confirm deletion

### View Change History
- Tools → Audit Log
- See all changes with timestamps
- Identify who made changes and when

### Compare Versions
- Tools → Version History
- See all saved versions
- Check cost and component changes

## Tips & Best Practices

### Good Practices
✓ Add suppliers for expensive components
✓ Include part numbers for future ordering
✓ Add datasheets for reference
✓ Keep descriptions brief but meaningful
✓ Group similar components in categories
✓ Save regularly

### Validation Tips
✓ Run validation before finalizing
✓ Aim for >80% completeness
✓ Add missing suppliers for items >$100
✓ Use consistent category names
✓ Fill in part numbers for all components

### Organization Tips
✓ Use meaningful component IDs (R1, R2 for resistors)
✓ Group by component type
✓ Add descriptions for unusual components
✓ Include lead times for long-delivery items
✓ Link to datasheets when available

## Keyboard Shortcuts

In the component tree:
- Double-click to edit
- Delete key to remove
- Enter to add new (if implemented)

## File Formats

### JSON Format
```json
{
  "metadata": { ... },
  "components": [ ... ],
  "audit_log": [ ... ]
}
```
Best for: Backup, version control, complete data preservation

### CSV Format
```
id,name,category,quantity,unit_cost,...
R1,Resistor 10k,Resistors,10,0.05,...
```
Best for: Spreadsheets, sharing with non-technical users, printing

## Troubleshooting

### GUI doesn't launch
- Ensure tkinter is installed: `pip install tk`
- Try CLI mode: `python main.py --cli`

### "Module not found" errors
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python path: `python -c "import cbom; print('OK')"`

### Can't save file
- Check directory permissions
- Ensure disk space available
- Try different directory

### Validation errors
- Check component IDs (uppercase letters/numbers only)
- Ensure quantities are positive
- Verify costs are non-negative

## Project Structure

```
C-BOM/
├── cbom/              # Main application code
├── tests/             # Test suite
├── main.py            # Entry point
├── examples.py        # Example usage
├── README.md          # Full documentation
├── API_REFERENCE.md   # Technical reference
└── SETUP_COMPLETE.md  # Setup details
```

## Next Features to Try

1. **Hierarchical BOMs**: Import examples.py to see nested assemblies
2. **Validation**: Tools → Validate to check data quality
3. **Exports**: Try different export formats
4. **Version Control**: Save versions and compare changes

## Getting Help

- See `README.md` for full documentation
- Check `API_REFERENCE.md` for technical details
- Run `examples.py` to see all features in action
- Review test cases in `tests/test_cbom.py`

## Performance Notes

- Handles hundreds of components efficiently
- JSON exports work well up to thousands of components
- GUI remains responsive with 500+ components
- Version history stored in filesystem (.cbom_versions folder)

---

**You're ready to use C-BOM!** 🚀

Start with `python main.py` and begin managing your component BOMs!
