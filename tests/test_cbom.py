"""
Test suite for C-BOM
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cbom import Component, ComponentBOM, ComponentValidator, BOMValidator, HierarchicalBOM


class TestComponent:
    """Test Component class"""
    
    def test_component_creation(self):
        """Test creating a component"""
        comp = Component(
            id="R1",
            name="Resistor 10k",
            category="Resistors",
            quantity=10,
            unit_cost=0.05
        )
        assert comp.id == "R1"
        assert comp.name == "Resistor 10k"
        assert comp.total_cost() == 0.5
    
    def test_component_validation(self):
        """Test component validation"""
        # Valid component
        valid_comp = Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=5, unit_cost=0.10
        )
        is_valid, errors = ComponentValidator.validate_component(valid_comp)
        assert is_valid
        assert len(errors) == 0
    
    def test_component_invalid_id(self):
        """Test invalid component ID"""
        invalid_comp = Component(
            id="r-1", name="Resistor", category="Resistors",
            quantity=5, unit_cost=0.10
        )
        is_valid, errors = ComponentValidator.validate_component(invalid_comp)
        assert not is_valid
        assert len(errors) > 0


class TestComponentBOM:
    """Test ComponentBOM class"""
    
    def test_bom_creation(self):
        """Test creating a BOM"""
        bom = ComponentBOM("Test Project")
        assert bom.project_name == "Test Project"
        assert len(bom.components) == 0
    
    def test_add_component(self):
        """Test adding components"""
        bom = ComponentBOM("Test Project")
        comp = Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        )
        bom.add_component(comp)
        assert len(bom.components) == 1
        assert bom.get_component("R1") == comp
    
    def test_add_duplicate_component(self):
        """Test adding duplicate component"""
        bom = ComponentBOM("Test Project")
        comp = Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        )
        bom.add_component(comp)
        
        with pytest.raises(ValueError):
            bom.add_component(comp)
    
    def test_remove_component(self):
        """Test removing component"""
        bom = ComponentBOM("Test Project")
        comp = Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        )
        bom.add_component(comp)
        bom.remove_component("R1")
        assert len(bom.components) == 0
    
    def test_total_cost(self):
        """Test total cost calculation"""
        bom = ComponentBOM("Test Project")
        bom.add_component(Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        ))
        bom.add_component(Component(
            id="C1", name="Capacitor", category="Capacitors",
            quantity=5, unit_cost=0.10
        ))
        
        # 10 * 0.05 + 5 * 0.10 = 0.5 + 0.5 = 1.0
        assert bom.get_total_cost() == 1.0


class TestValidator:
    """Test validation classes"""
    
    def test_bom_validation(self):
        """Test BOM validation"""
        bom = ComponentBOM("Test Project")
        bom.add_component(Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        ))
        
        is_valid, errors = BOMValidator.validate_bom(bom)
        assert is_valid
        assert len(errors) == 0
    
    def test_bom_completeness(self):
        """Test BOM completeness check"""
        bom = ComponentBOM("Test Project")
        bom.add_component(Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05,
            supplier="Test Supplier", part_number="ABC123"
        ))
        
        completeness = BOMValidator.validate_bom_completeness(bom)
        assert completeness["overall"] > 0
        assert "details" in completeness


class TestHierarchicalBOM:
    """Test hierarchical BOM"""
    
    def test_hierarchy_creation(self):
        """Test creating hierarchical BOM"""
        main = HierarchicalBOM("Main Assembly")
        sub = HierarchicalBOM("Sub Assembly")
        
        main.add_subassembly(sub)
        assert "Sub Assembly" in main.children
    
    def test_hierarchy_components(self):
        """Test adding components to hierarchy"""
        main = HierarchicalBOM("Main Assembly")
        main.add_component(Component(
            id="R1", name="Resistor", category="Resistors",
            quantity=10, unit_cost=0.05
        ))
        
        assert len(main.components) == 1
        assert main.get_component_count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
