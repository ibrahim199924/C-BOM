# Contributing to C-BOM

Thank you for your interest in contributing to the Cryptographic Bill of Materials project! 

## Getting Started

### Fork & Clone
```bash
git clone https://github.com/your-username/C-BOM.git
cd C-BOM
git remote add upstream https://github.com/original-username/C-BOM.git
```

### Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

## Code Style

We follow PEP 8 with Black formatter:

```bash
# Format your code
black cbom/ tests/

# Check linting
flake8 cbom/ tests/

# Type hints required for all functions
def process_asset(asset: CryptoAsset) -> Dict[str, Any]:
    """Process cryptographic asset."""
    pass
```

## Testing

Write tests for all new features:

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=cbom --cov-report=html

# Run specific test
pytest tests/test_cbom.py::test_crypto_validator -v
```

## Making Changes

### 1. Create Feature Branch
```bash
git checkout -b feature/my-new-feature
```

### 2. Make Your Changes
- Update code in appropriate module
- Add/update tests
- Update documentation
- Add to CHANGELOG

### 3. Commit Messages
Use clear, descriptive commit messages:

```
feat: Add ECDSA key validation
- Implement ECDSA strength validation
- Add tests for P-256 and P-384 curves
- Update validator documentation
```

### 4. Push & Create Pull Request
```bash
git push origin feature/my-new-feature
```

Then open PR on GitHub with:
- Clear title describing changes
- Description of what and why
- Reference any issues (#123)
- Screenshots if UI changes

## Types of Contributions

### Bug Fixes
- Create issue first to discuss
- Reference issue in PR
- Add regression test
- Update CHANGELOG

### Features
- Discuss design in issue first
- Follow existing patterns in code
- Add comprehensive tests (70%+ coverage)
- Update README if user-facing
- Add docstrings

### Documentation
- Fix typos and clarify
- Add examples
- Update API documentation
- Improve guides

### Tests
- Increase test coverage
- Add edge case tests
- Test error conditions

## Code Structure

### Adding New Cryptographic Validators

```python
# In cbom/validator.py

class CryptoValidator:
    @staticmethod
    def validate_algorithm_strength(algorithm: str, key_length: int) -> Tuple[bool, str]:
        """
        Validate algorithm and key length meet security standards.
        
        Args:
            algorithm: Algorithm name
            key_length: Key length in bits
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Implementation
        pass
```

### Adding New Models

```python
# In cbom/models.py

@dataclass
class NewAsset:
    """New cryptographic asset type."""
    id: str
    name: str
    # ... other fields
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate asset."""
        errors = []
        # Validation logic
        return len(errors) == 0, errors
```

## Pull Request Process

1. **Code Review**: Maintainer reviews changes
2. **Tests**: All tests must pass (automated)
3. **Coverage**: Maintain or improve coverage
4. **Approval**: Needs approval from maintainer
5. **Merge**: Squash and merge to main

## Development Checklist

- [ ] Code follows style guide
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] CHANGELOG updated
- [ ] Commit messages descriptive

## Performance Considerations

- Cache validation results when possible
- Lazy load large datasets
- Use efficient data structures
- Profile before optimizing

## Security

- No hardcoded secrets
- Validate all inputs
- Don't log sensitive data
- Follow OWASP guidelines

## Issues & Questions

- **Bug reports**: GitHub Issues with reproduction steps
- **Features**: Create issue before coding
- **Questions**: Discussions tab
- **Security**: Email maintainer privately

## Community

- Be respectful and inclusive
- Help other contributors
- Share knowledge
- Celebrate contributions

## Branch Protection Rules

Main branch is protected:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

## Licensing

By contributing, you agree that your contributions are licensed under the MIT License.

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

---

Thank you for making C-BOM better! 🚀
