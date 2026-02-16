## C-BOM Development Instructions

### Project Overview
C-BOM is a comprehensive Component Bill of Materials management tool with version control, hierarchical BOMs, validation, and GUI interface.

### Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   - **GUI Mode**: `python main.py`
   - **CLI Mode**: `python main.py --cli`

### Project Structure

- `cbom/` - Main package with core functionality
  - `models.py` - Component and BOM data models
  - `validator.py` - Validation logic for components and BOMs
  - `version_control.py` - Version control and history tracking
  - `hierarchical.py` - Hierarchical BOM support
  - `gui.py` - Tkinter GUI interface

- `tests/` - Test suite with pytest

- `main.py` - Entry point for the application

### Development Tasks

1. **Feature Implementation** - Add new features following the existing code patterns
2. **Testing** - Add tests in `tests/test_cbom.py` for new functionality
3. **Documentation** - Update README.md and code comments
4. **Bug Fixes** - Address issues while maintaining backward compatibility

### Key Classes and Methods

- `Component` - Individual component model
- `ComponentBOM` - Main BOM management class
- `ComponentValidator` - Validates individual components
- `BOMValidator` - Validates complete BOMs
- `VersionControl` - Manages BOM version history
- `HierarchicalBOM` - Supports assemblies and sub-assemblies
- `CBOMGUI` - Main GUI application

### Running Tests

```bash
pytest tests/test_cbom.py -v
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for functions
- Document public methods with docstrings
- Keep functions focused and modular
