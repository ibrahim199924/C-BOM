"""
GUI module for C-BOM using tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from .models import Component, ComponentBOM
from .validator import ComponentValidator, BOMValidator
from .version_control import VersionControl
from .hierarchical import HierarchicalBOM


class CBOMGUI:
    """Main GUI application for C-BOM"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Component Bill of Materials (C-BOM)")
        self.root.geometry("1200x700")
        
        self.bom: Optional[ComponentBOM] = None
        self.version_control: Optional[VersionControl] = None
        self.current_file: Optional[str] = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export as JSON", command=self.export_json)
        file_menu.add_command(label="Export as CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Component", command=self.add_component_dialog)
        edit_menu.add_command(label="Edit Component", command=self.edit_component_dialog)
        edit_menu.add_command(label="Delete Component", command=self.delete_component_dialog)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate BOM", command=self.validate_bom)
        tools_menu.add_command(label="View Audit Log", command=self.view_audit_log)
        tools_menu.add_command(label="Version History", command=self.view_version_history)
        
        # Main content
        self.create_main_content()
    
    def create_main_content(self):
        """Create main content area"""
        # Top frame for project info
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Project Name:").pack(side=tk.LEFT, padx=5)
        self.project_name_var = tk.StringVar(value="Untitled Project")
        ttk.Entry(info_frame, textvariable=self.project_name_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(info_frame, text="Description:").pack(side=tk.LEFT, padx=5)
        self.project_desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.project_desc_var, width=40).pack(side=tk.LEFT, padx=5)
        
        # Summary frame
        summary_frame = ttk.LabelFrame(self.root, text="BOM Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=4, width=80, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Components frame
        components_frame = ttk.LabelFrame(self.root, text="Components", padding=10)
        components_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(components_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Add Component", command=self.add_component_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_component_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_component_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_components).pack(side=tk.LEFT, padx=5)
        
        # Components tree
        columns = ('ID', 'Name', 'Category', 'Qty', 'Unit Cost', 'Total Cost', 'Supplier', 'Part #')
        self.components_tree = ttk.Treeview(components_frame, columns=columns, height=15)
        self.components_tree.pack(fill=tk.BOTH, expand=True)
        
        # Column headings
        self.components_tree.heading('#0', text='#')
        self.components_tree.column('#0', width=30)
        
        for col in columns:
            self.components_tree.heading(col, text=col)
            if col == 'ID':
                self.components_tree.column(col, width=60)
            elif col == 'Name':
                self.components_tree.column(col, width=150)
            else:
                self.components_tree.column(col, width=100)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Create initial empty BOM
        self.create_new_bom()
    
    def create_new_bom(self):
        """Create a new empty BOM"""
        self.bom = ComponentBOM(self.project_name_var.get(), self.project_desc_var.get())
        self.version_control = VersionControl(self.bom)
        self.refresh_display()
        self.status_var.set("Created new BOM")
    
    def new_project(self):
        """Create new project"""
        if self.bom and len(self.bom.components) > 0:
            if not messagebox.askyesno("Confirm", "Current project has components. Create new anyway?"):
                return
        
        self.create_new_bom()
        self.current_file = None
        self.status_var.set("New project created")
    
    def add_component_dialog(self):
        """Open dialog to add component"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Component")
        dialog.geometry("500x600")
        
        fields = {
            'id': ('Component ID', ''),
            'name': ('Name', ''),
            'category': ('Category', ''),
            'quantity': ('Quantity', '1'),
            'unit_cost': ('Unit Cost ($)', '0.00'),
            'supplier': ('Supplier', ''),
            'part_number': ('Part Number', ''),
            'description': ('Description', ''),
            'datasheet_url': ('Datasheet URL', ''),
            'lead_time_days': ('Lead Time (days)', ''),
            'manufacturer': ('Manufacturer', '')
        }
        
        entries = {}
        
        for i, (key, (label, default)) in enumerate(fields.items()):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            entry = ttk.Entry(dialog, width=40)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=10, pady=5)
            entries[key] = entry
        
        def save_component():
            try:
                lead_time = entries['lead_time_days'].get()
                lead_time = int(lead_time) if lead_time else None
                
                unit_cost = float(entries['unit_cost'].get())
                quantity = int(entries['quantity'].get())
                
                component = Component(
                    id=entries['id'].get(),
                    name=entries['name'].get(),
                    category=entries['category'].get(),
                    quantity=quantity,
                    unit_cost=unit_cost,
                    supplier=entries['supplier'].get() or None,
                    part_number=entries['part_number'].get() or None,
                    description=entries['description'].get() or None,
                    datasheet_url=entries['datasheet_url'].get() or None,
                    lead_time_days=lead_time,
                    manufacturer=entries['manufacturer'].get() or None
                )
                
                # Validate
                is_valid, errors = ComponentValidator.validate_component(component)
                if not is_valid:
                    messagebox.showerror("Validation Error", "\n".join(errors))
                    return
                
                self.bom.add_component(component)
                self.refresh_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"Component {component.id} added successfully")
                self.status_var.set(f"Added component {component.id}")
            
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save", command=save_component).grid(row=len(fields), column=1, pady=20)
    
    def edit_component_dialog(self):
        """Edit selected component"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        selected = self.components_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a component to edit")
            return
        
        component_id = selected[0]
        component = self.bom.get_component(component_id)
        
        if not component:
            messagebox.showerror("Error", "Component not found")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Component - {component_id}")
        dialog.geometry("500x600")
        
        fields = {
            'name': ('Name', component.name),
            'category': ('Category', component.category),
            'quantity': ('Quantity', str(component.quantity)),
            'unit_cost': ('Unit Cost ($)', f"{component.unit_cost:.2f}"),
            'supplier': ('Supplier', component.supplier or ''),
            'part_number': ('Part Number', component.part_number or ''),
            'description': ('Description', component.description or ''),
            'datasheet_url': ('Datasheet URL', component.datasheet_url or ''),
            'lead_time_days': ('Lead Time (days)', str(component.lead_time_days) if component.lead_time_days else ''),
            'manufacturer': ('Manufacturer', component.manufacturer or '')
        }
        
        entries = {}
        
        for i, (key, (label, default)) in enumerate(fields.items()):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky=tk.W, padx=10, pady=5)
            entry = ttk.Entry(dialog, width=40)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=10, pady=5)
            entries[key] = entry
        
        def save_changes():
            try:
                updates = {}
                for key, entry in entries.items():
                    if key == 'quantity':
                        updates[key] = int(entry.get())
                    elif key == 'unit_cost':
                        updates[key] = float(entry.get())
                    elif key == 'lead_time_days':
                        val = entry.get()
                        updates[key] = int(val) if val else None
                    else:
                        val = entry.get()
                        updates[key] = val if val else None
                
                self.bom.update_component(component_id, **updates)
                self.refresh_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"Component {component_id} updated successfully")
                self.status_var.set(f"Updated component {component_id}")
            
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Save Changes", command=save_changes).grid(row=len(fields), column=1, pady=20)
    
    def delete_component_dialog(self):
        """Delete selected component"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        selected = self.components_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a component to delete")
            return
        
        component_id = selected[0]
        component = self.bom.get_component(component_id)
        
        if messagebox.askyesno("Confirm", f"Delete component {component_id} ({component.name})?"):
            self.bom.remove_component(component_id)
            self.refresh_display()
            messagebox.showinfo("Success", f"Component {component_id} deleted")
            self.status_var.set(f"Deleted component {component_id}")
    
    def refresh_components(self):
        """Refresh component display"""
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh all display elements"""
        if not self.bom:
            return
        
        # Update summary
        summary = self.bom.get_summary()
        summary_text = (
            f"Components: {summary['total_components']} | "
            f"Total Cost: ${summary['total_cost']:.2f} | "
            f"Categories: {len(summary['categories'])} | "
            f"Modified: {summary['last_modified'].split('T')[0]}"
        )
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary_text)
        self.summary_text.config(state=tk.DISABLED)
        
        # Update components tree
        for item in self.components_tree.get_children():
            self.components_tree.delete(item)
        
        for i, component in enumerate(self.bom.components.values(), 1):
            values = (
                component.id,
                component.name,
                component.category,
                component.quantity,
                f"${component.unit_cost:.2f}",
                f"${component.total_cost():.2f}",
                component.supplier or "N/A",
                component.part_number or "N/A"
            )
            self.components_tree.insert('', tk.END, iid=component.id, text=str(i), values=values)
    
    def save_project(self):
        """Save project"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
        
        if self.current_file:
            try:
                self.bom.export_json(self.current_file)
                self.version_control.create_version(f"Saved {self.bom.project_name}")
                messagebox.showinfo("Success", f"Project saved to {self.current_file}")
                self.status_var.set(f"Saved to {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def open_project(self):
        """Open project"""
        file = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file:
            try:
                self.bom = ComponentBOM("", "")
                self.bom.import_json(file)
                self.version_control = VersionControl(self.bom)
                self.current_file = file
                self.project_name_var.set(self.bom.project_name)
                self.project_desc_var.set(self.bom.description)
                self.refresh_display()
                messagebox.showinfo("Success", f"Project loaded from {file}")
                self.status_var.set(f"Opened {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open: {str(e)}")
    
    def export_json(self):
        """Export as JSON"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file:
            try:
                self.bom.export_json(file)
                messagebox.showinfo("Success", f"Exported to {file}")
                self.status_var.set(f"Exported to {file}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def export_csv(self):
        """Export as CSV"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file:
            try:
                self.bom.export_csv(file)
                messagebox.showinfo("Success", f"Exported to {file}")
                self.status_var.set(f"Exported to {file}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def validate_bom(self):
        """Validate current BOM"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        is_valid, errors = BOMValidator.validate_bom(self.bom)
        warnings = BOMValidator.get_bom_warnings(self.bom)
        completeness = BOMValidator.validate_bom_completeness(self.bom)
        
        result_text = ""
        
        if is_valid:
            result_text += "✓ BOM is VALID\n\n"
        else:
            result_text += "✗ BOM has ERRORS:\n"
            for error in errors:
                result_text += f"  • {error}\n"
            result_text += "\n"
        
        if warnings:
            result_text += "⚠ WARNINGS:\n"
            for warning in warnings[:10]:  # Show first 10
                result_text += f"  • {warning}\n"
        
        result_text += f"\nCompleteness: {completeness['overall']:.1f}%\n"
        result_text += "Field Coverage:\n"
        for field, pct in completeness['details'].items():
            result_text += f"  {field}: {pct:.1f}%\n"
        
        messagebox.showinfo("BOM Validation", result_text)
        self.status_var.set("BOM validated")
    
    def view_audit_log(self):
        """View audit log"""
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return
        
        audit_log = self.bom.get_audit_log()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Audit Log")
        dialog.geometry("800x500")
        
        text = tk.Text(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for audit in reversed(audit_log[-50:]):  # Show last 50
            entry = f"[{audit.timestamp}] {audit.action.upper()} - {audit.component_id} ({audit.component_name}) by {audit.user}\n"
            text.insert(tk.END, entry)
        
        text.config(state=tk.DISABLED)
    
    def view_version_history(self):
        """View version history"""
        if not self.version_control:
            messagebox.showerror("Error", "No version control available")
            return
        
        history = self.version_control.get_version_history()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Version History")
        dialog.geometry("600x400")
        
        text = tk.Text(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if not history:
            text.insert(tk.END, "No versions created yet")
        else:
            for version in reversed(history):
                entry = (
                    f"[{version['version_id']}] {version['message']}\n"
                    f"  Components: {version['components_count']} | Cost: ${version['total_cost']:.2f}\n\n"
                )
                text.insert(tk.END, entry)
        
        text.config(state=tk.DISABLED)


def launch_gui():
    """Launch the GUI application"""
    try:
        root = tk.Tk()
        app = CBOMGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        raise


if __name__ == "__main__":
    launch_gui()
