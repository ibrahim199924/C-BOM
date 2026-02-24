"""
GUI module for C-BOM using tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from .models import CryptoAsset, CryptoBOM
from .validator import CryptoValidator, CryptoBOMValidator
from .version_control import VersionControl
from .hierarchical import HierarchicalCryptoBOM


class CBOMGUI:
    """Main GUI application for C-BOM"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("C-BOM - Cryptographic Bill of Materials")
        self.root.geometry("1280x750")

        self.bom: Optional[CryptoBOM] = None
        self.version_control: Optional[VersionControl] = None
        self.current_file: Optional[str] = None

        self.setup_ui()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        """Setup the main UI"""
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
        edit_menu.add_command(label="Add Asset", command=self.add_asset_dialog)
        edit_menu.add_command(label="Edit Asset", command=self.edit_asset_dialog)
        edit_menu.add_command(label="Delete Asset", command=self.delete_asset_dialog)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate BOM", command=self.validate_bom)
        tools_menu.add_command(label="View Audit Log", command=self.view_audit_log)
        tools_menu.add_command(label="Version History", command=self.view_version_history)

        self.create_main_content()

    def create_main_content(self):
        """Create main content area"""
        # Project info row
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text="Project Name:").pack(side=tk.LEFT, padx=5)
        self.project_name_var = tk.StringVar(value="Untitled Project")
        ttk.Entry(info_frame, textvariable=self.project_name_var, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(info_frame, text="Description:").pack(side=tk.LEFT, padx=5)
        self.project_desc_var = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.project_desc_var, width=40).pack(side=tk.LEFT, padx=5)

        # Summary
        summary_frame = ttk.LabelFrame(self.root, text="BOM Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.summary_text = tk.Text(summary_frame, height=3, width=100, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Assets frame
        assets_frame = ttk.LabelFrame(self.root, text="Cryptographic Assets", padding=10)
        assets_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Buttons
        button_frame = ttk.Frame(assets_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Add Asset", command=self.add_asset_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Edit", command=self.edit_asset_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_asset_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_display).pack(side=tk.LEFT, padx=5)

        # Asset tree
        columns = ('ID', 'Name', 'Type', 'Algorithm', 'Key Length', 'Purpose', 'Status', 'Risk', 'CVSS', 'CVEs')
        self.assets_tree = ttk.Treeview(assets_frame, columns=columns, height=18)
        self.assets_tree.pack(fill=tk.BOTH, expand=True)

        self.assets_tree.heading('#0', text='#')
        self.assets_tree.column('#0', width=30)

        widths = {'ID': 80, 'Name': 160, 'Type': 100, 'Algorithm': 130, 'Key Length': 80,
                  'Purpose': 110, 'Status': 90, 'Risk': 70, 'CVSS': 60, 'CVEs': 80}
        for col in columns:
            self.assets_tree.heading(col, text=col)
            self.assets_tree.column(col, width=widths.get(col, 90))

        # Colour tags for risk levels
        self.assets_tree.tag_configure('CRITICAL', foreground='red')
        self.assets_tree.tag_configure('HIGH', foreground='darkorange')
        self.assets_tree.tag_configure('MEDIUM', foreground='goldenrod')
        self.assets_tree.tag_configure('LOW', foreground='green')

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, side=tk.BOTTOM)

        self.create_new_bom()

    # ------------------------------------------------------------------ #
    #  BOM operations                                                      #
    # ------------------------------------------------------------------ #

    def create_new_bom(self):
        self.bom = CryptoBOM(self.project_name_var.get(), self.project_desc_var.get())
        self.version_control = VersionControl(self.bom)
        self.refresh_display()
        self.status_var.set("Created new BOM")

    def new_project(self):
        if self.bom and len(self.bom.assets) > 0:
            if not messagebox.askyesno("Confirm", "Current project has assets. Create new anyway?"):
                return
        self.create_new_bom()
        self.current_file = None
        self.status_var.set("New project created")

    # ------------------------------------------------------------------ #
    #  Add / Edit / Delete dialogs                                         #
    # ------------------------------------------------------------------ #

    def _asset_form(self, title: str, initial=None) -> Optional[dict]:
        """Open a modal form and return field values or None if cancelled."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("600x660")
        dialog.grab_set()

        fields = [
            ('id',                  'Asset ID (UPPERCASE)',                                initial.id if initial else ''),
            ('name',                'Name',                                                initial.name if initial else ''),
            ('asset_type',          'Type (algorithm/key/certificate/library/cipher_suite)',initial.asset_type if initial else 'algorithm'),
            ('algorithm',           'Algorithm (e.g. AES-256-GCM)',                        initial.algorithm if initial else ''),
            ('key_length',          'Key Length (bits, e.g. 256)',                         str(initial.key_length) if initial else '0'),
            ('cipher_mode',         'Cipher Mode (GCM/CBC/...)',                           initial.cipher_mode if initial else ''),
            ('purpose',             'Purpose (encryption/hashing/signing/key_exchange)',   initial.purpose if initial else ''),
            ('library',             'Library (e.g. OpenSSL 3.0)',                          initial.library if initial else ''),
            ('version',             'Version',                                             initial.version if initial else ''),
            ('status',              'Status (active/deprecated/vulnerable/expired/planned)',initial.status if initial else 'active'),
            ('vulnerability_score', 'CVSS Score (0-10)',                                   str(initial.vulnerability_score) if initial else '0.0'),
            ('known_cves',          'CVEs (semicolon-separated)',                          ';'.join(initial.known_cves) if initial else ''),
            ('compliance',          'Compliance Standards (semicolon-separated)',          ';'.join(initial.compliance) if initial else ''),
            ('rotation_schedule',   'Rotation Schedule',                                  initial.rotation_schedule if initial else ''),
            ('expiration_date',     'Expiration Date (ISO format, optional)',              initial.expiration_date if initial else ''),
            ('description',         'Description',                                         initial.description if initial else ''),
        ]

        entries = {}
        for i, (key, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label, font=('TkDefaultFont', 8)).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=2)
            entry = ttk.Entry(dialog, width=35)
            entry.insert(0, default)
            entry.grid(row=i, column=1, sticky=tk.EW, padx=10, pady=2)
            entries[key] = entry

        result = {}

        def on_save():
            result['data'] = {k: e.get() for k, e in entries.items()}
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="Save", command=on_save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=10)

        self.root.wait_window(dialog)
        return result.get('data')

    def _build_asset(self, data: dict, asset_id_override: str = None) -> CryptoAsset:
        """Convert raw form data to a CryptoAsset instance."""
        aid = (asset_id_override or data['id']).strip().upper()
        key_length = int(data['key_length']) if data['key_length'].strip() else 0
        cvss = float(data['vulnerability_score']) if data['vulnerability_score'].strip() else 0.0
        cves = [c.strip() for c in data['known_cves'].split(';') if c.strip()]
        compliance = [c.strip() for c in data['compliance'].split(';') if c.strip()]
        status = data['status'].strip() or CryptoAsset.auto_detect_status(data['algorithm'])

        return CryptoAsset(
            id=aid,
            name=data['name'].strip(),
            asset_type=data['asset_type'].strip(),
            algorithm=data['algorithm'].strip(),
            key_length=key_length,
            cipher_mode=data['cipher_mode'].strip(),
            purpose=data['purpose'].strip(),
            library=data['library'].strip(),
            version=data['version'].strip(),
            status=status,
            vulnerability_score=cvss,
            known_cves=cves,
            compliance=compliance,
            rotation_schedule=data['rotation_schedule'].strip(),
            expiration_date=data['expiration_date'].strip(),
            description=data['description'].strip(),
        )

    def add_asset_dialog(self):
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return

        data = self._asset_form("Add Cryptographic Asset")
        if not data:
            return

        try:
            asset = self._build_asset(data)
            is_valid, errors = CryptoValidator.validate_asset(asset)
            if not is_valid:
                messagebox.showerror("Validation Error", "\n".join(errors))
                return
            self.bom.add_asset(asset)
            self.refresh_display()
            messagebox.showinfo("Success", f"Asset {asset.id} added successfully")
            self.status_var.set(f"Added asset {asset.id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_asset_dialog(self):
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return

        selected = self.assets_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to edit")
            return

        asset_id = selected[0]
        asset = self.bom.get_asset(asset_id)
        if not asset:
            messagebox.showerror("Error", "Asset not found")
            return

        data = self._asset_form(f"Edit Asset - {asset_id}", initial=asset)
        if not data:
            return

        try:
            key_length = int(data['key_length']) if data['key_length'].strip() else 0
            cvss = float(data['vulnerability_score']) if data['vulnerability_score'].strip() else 0.0
            cves = [c.strip() for c in data['known_cves'].split(';') if c.strip()]
            compliance = [c.strip() for c in data['compliance'].split(';') if c.strip()]

            updates = {field: data[field].strip() for field in (
                'name', 'asset_type', 'algorithm', 'cipher_mode', 'purpose',
                'library', 'version', 'status', 'rotation_schedule',
                'expiration_date', 'description'
            )}
            updates['key_length'] = key_length
            updates['vulnerability_score'] = cvss
            updates['known_cves'] = cves
            updates['compliance'] = compliance

            self.bom.update_asset(asset_id, **updates)
            self.refresh_display()
            messagebox.showinfo("Success", f"Asset {asset_id} updated successfully")
            self.status_var.set(f"Updated asset {asset_id}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_asset_dialog(self):
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return

        selected = self.assets_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to delete")
            return

        asset_id = selected[0]
        asset = self.bom.get_asset(asset_id)
        if not asset:
            return

        if messagebox.askyesno("Confirm", f"Delete asset {asset_id} ({asset.name})?"):
            self.bom.remove_asset(asset_id)
            self.refresh_display()
            messagebox.showinfo("Success", f"Asset {asset_id} deleted")
            self.status_var.set(f"Deleted asset {asset_id}")

    # ------------------------------------------------------------------ #
    #  Display refresh                                                     #
    # ------------------------------------------------------------------ #

    def refresh_display(self):
        if not self.bom:
            return

        summary = self.bom.get_summary()
        types_str = ', '.join(f'{k}={v}' for k, v in summary['asset_types'].items()) or 'none'
        summary_text = (
            f"Total Assets: {summary['total_assets']} | "
            f"Critical: {summary['critical_risk']} | "
            f"Vulnerable: {summary['vulnerable_assets']} | "
            f"Expired: {summary['expired_assets']} | "
            f"Types: {types_str}"
        )

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary_text)
        self.summary_text.config(state=tk.DISABLED)

        for item in self.assets_tree.get_children():
            self.assets_tree.delete(item)

        for i, asset in enumerate(self.bom.assets.values(), 1):
            risk = asset.risk_level()
            values = (
                asset.id,
                asset.name,
                asset.asset_type,
                asset.algorithm,
                str(asset.key_length) if asset.key_length else '',
                asset.purpose,
                asset.status,
                risk,
                str(asset.vulnerability_score),
                str(len(asset.known_cves)),
            )
            self.assets_tree.insert('', tk.END, iid=asset.id, text=str(i),
                                    values=values, tags=(risk,))

    # ------------------------------------------------------------------ #
    #  File operations                                                     #
    # ------------------------------------------------------------------ #

    def save_project(self):
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
                if self.version_control:
                    self.version_control.create_version(f"Saved {self.bom.project_name}")
                messagebox.showinfo("Success", f"Project saved to {self.current_file}")
                self.status_var.set(f"Saved to {self.current_file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")

    def open_project(self):
        file = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file:
            try:
                self.bom = CryptoBOM("", "")
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
                self.status_var.set(f"Exported JSON to {file}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def export_csv(self):
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
                self.status_var.set(f"Exported CSV to {file}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------ #
    #  Tools                                                               #
    # ------------------------------------------------------------------ #

    def validate_bom(self):
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return

        is_valid, messages = CryptoBOMValidator.validate_bom(self.bom)
        posture = CryptoBOMValidator.get_security_posture(self.bom)

        result_text = ""
        if is_valid:
            result_text += "BOM is VALID\n\n"
        else:
            result_text += "BOM has ERRORS / WARNINGS:\n"

        for msg in messages:
            result_text += f"  - {msg}\n"

        result_text += f"\nSecurity Score: {posture.get('security_score', 0):.1f}/100\n"
        result_text += f"Posture: {posture.get('posture', 'N/A')}\n"

        messagebox.showinfo("BOM Validation", result_text)
        self.status_var.set("BOM validated")

    def view_audit_log(self):
        if not self.bom:
            messagebox.showerror("Error", "No project loaded")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Audit Log")
        dialog.geometry("800x500")

        text = tk.Text(dialog, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        entries = self.bom.audit_log
        if not entries:
            text.insert(tk.END, "No audit log entries.")
        else:
            for audit in reversed(entries[-50:]):
                line = (f"[{audit.timestamp}] {audit.action.upper()} "
                        f"- {audit.asset_id} ({audit.asset_name}) by {audit.user}\n")
                text.insert(tk.END, line)

        text.config(state=tk.DISABLED)

    def view_version_history(self):
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
                    f"  Assets: {version['components_count']}\n\n"
                )
                text.insert(tk.END, entry)

        text.config(state=tk.DISABLED)
