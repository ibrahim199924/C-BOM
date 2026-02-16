# Example usage of C-BOM library

from cbom import Component, ComponentBOM, BOMValidator, VersionControl, HierarchicalBOM

def example_basic_bom():
    """Create a basic BOM"""
    bom = ComponentBOM("Electronics Project", "Simple LED circuit")
    
    # Add resistor
    bom.add_component(Component(
        id="R1",
        name="Resistor 220 Ohm",
        category="Resistors",
        quantity=5,
        unit_cost=0.02,
        supplier="ElectroSupply",
        part_number="RES-220",
        manufacturer="TDK"
    ))
    
    # Add capacitor
    bom.add_component(Component(
        id="C1",
        name="Capacitor 10uF",
        category="Capacitors",
        quantity=3,
        unit_cost=0.10,
        supplier="ElectroSupply",
        part_number="CAP-10UF",
        manufacturer="Murata"
    ))
    
    # Add LED
    bom.add_component(Component(
        id="LED1",
        name="LED Red 5mm",
        category="Optoelectronics",
        quantity=10,
        unit_cost=0.15,
        supplier="ElectroSupply",
        part_number="LED-RED-5MM",
        manufacturer="Kingbright"
    ))
    
    return bom


def example_hierarchical_bom():
    """Create a hierarchical BOM"""
    main = HierarchicalBOM("Complete Device", "Full device assembly")
    
    # Create sub-assemblies
    power = HierarchicalBOM("Power Supply", "Power management")
    signal = HierarchicalBOM("Signal Processing", "Signal processor module")
    
    main.add_subassembly(power)
    main.add_subassembly(signal)
    
    # Add components to power supply
    power.add_component(Component(
        id="IC-PSU", name="LDO Regulator", category="ICs",
        quantity=1, unit_cost=0.50, supplier="DigiKey",
        part_number="AMS1117"
    ))
    
    # Add components to signal processor
    signal.add_component(Component(
        id="IC-PROC", name="Microcontroller", category="ICs",
        quantity=1, unit_cost=5.00, supplier="Arrow",
        part_number="ATmega328"
    ))
    
    return main


def example_validation():
    """Demonstrate validation"""
    bom = example_basic_bom()
    
    # Validate BOM
    is_valid, errors = BOMValidator.validate_bom(bom)
    print(f"BOM Valid: {is_valid}")
    
    if not is_valid:
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
    
    # Get warnings
    warnings = BOMValidator.get_bom_warnings(bom)
    print(f"\nWarnings: {len(warnings)}")
    for warning in warnings[:5]:
        print(f"  - {warning}")
    
    # Check completeness
    completeness = BOMValidator.validate_bom_completeness(bom)
    print(f"\nBOM Completeness: {completeness['overall']}%")
    print("Field Coverage:")
    for field, pct in completeness['details'].items():
        print(f"  {field}: {pct}%")


def example_version_control():
    """Demonstrate version control"""
    bom = example_basic_bom()
    vc = VersionControl(bom)
    
    # Create initial version
    v1 = vc.create_version("Initial BOM")
    print(f"Created version: {v1}")
    
    # Make changes
    bom.add_component(Component(
        id="R2", name="Resistor 1k", category="Resistors",
        quantity=2, unit_cost=0.03, supplier="ElectroSupply"
    ))
    
    # Create second version
    v2 = vc.create_version("Added 1k resistor")
    print(f"Created version: {v2}")
    
    # View history
    print("\nVersion History:")
    for version in vc.get_version_history():
        print(f"  {version['version_id']}: {version['message']}")
    
    # Compare versions
    if len(vc.get_version_history()) >= 2:
        diff = vc.get_version_diff(v1, v2)
        print(f"\nDifferences between {v1} and {v2}:")
        print(f"  Added: {diff['added']}")
        print(f"  Cost change: ${diff['cost_change']:.2f}")


def main():
    """Run all examples"""
    print("=" * 60)
    print("C-BOM Examples")
    print("=" * 60)
    
    print("\n1. Basic BOM Example")
    print("-" * 60)
    bom = example_basic_bom()
    print(bom.display_summary())
    print(bom.display_components())
    
    print("\n2. Hierarchical BOM Example")
    print("-" * 60)
    h_bom = example_hierarchical_bom()
    print(h_bom.display_tree())
    print(f"\nTotal Components: {h_bom.get_component_count()}")
    print(f"Total Cost: ${h_bom.get_total_cost():.2f}")
    
    print("\n3. Validation Example")
    print("-" * 60)
    example_validation()
    
    print("\n4. Version Control Example")
    print("-" * 60)
    example_version_control()
    
    print("\n5. Export Examples")
    print("-" * 60)
    bom = example_basic_bom()
    bom.export_json("example_bom.json")
    bom.export_csv("example_bom.csv")
    print("Exported to example_bom.json and example_bom.csv")


if __name__ == "__main__":
    main()
