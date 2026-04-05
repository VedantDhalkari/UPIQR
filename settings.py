"""
Settings Module
Application and shop settings configuration
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from ui_components import AnimatedButton, PageHeader
from auth import verify_admin_pin


class SettingsModule(ctk.CTkFrame):
    """Application settings interface with premium grid layout"""
    
    def __init__(self, parent, db_manager, current_user=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.current_user = current_user
        
        # Header
        PageHeader(self, title="⚙️ Application Settings").pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Main layout container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=6) # Left side (Shop Details)
        self.main_container.grid_columnconfigure(1, weight=4) # Right side (Printer, Admin, About)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        self.entries = {}
        
        self._create_left_panel()
        self._create_right_panel()
        
    def _create_left_panel(self):
        # Left Panel - Shop Details
        left_panel = ctk.CTkFrame(self.main_container, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG, border_width=1, border_color=config.COLOR_BORDER)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, config.SPACING_MD))
        
        # Inner scrollable frame for shop details
        scroll_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent", scrollbar_button_color=config.COLOR_PRIMARY)
        scroll_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        header_label = ctk.CTkLabel(
            scroll_frame,
            text="🏢 Shop Configuration",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        header_label.pack(pady=(0, config.SPACING_LG), anchor="w")
        
        # Details grid
        fields_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        fields_frame.pack(fill="x", expand=True)
        fields_frame.grid_columnconfigure(0, weight=1)
        fields_frame.grid_columnconfigure(1, weight=1)
        
        settings_fields = [
            ("Shop Name", config.SETTING_SHOP_NAME, "Trading Name", 0, 0),
            ("Phone Number", config.SETTING_SHOP_PHONE, "Primary Contact", 0, 1),
            ("Email Address", config.SETTING_SHOP_EMAIL, "Contact Email", 1, 0),
            ("GSTIN / Tax ID", config.SETTING_GST_NUMBER, "Business Tax Number", 1, 1),
            ("Invoice Prefix", config.SETTING_BILL_PREFIX, "e.g., INV-", 2, 0)
        ]
        
        for label, key, placeholder, r, c in settings_fields:
            wrapper = ctk.CTkFrame(fields_frame, fg_color="transparent")
            wrapper.grid(row=r, column=c, sticky="ew", padx=config.SPACING_SM, pady=config.SPACING_SM)
            
            ctk.CTkLabel(wrapper, text=label, font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold")).pack(anchor="w", pady=(0, 2))
            entry = ctk.CTkEntry(wrapper, height=config.INPUT_HEIGHT, placeholder_text=placeholder, border_color=config.COLOR_BORDER, border_width=1)
            entry.insert(0, self.db.get_setting(key) or "")
            entry.pack(fill="x")
            self.entries[key] = entry
            
        # Address (Full width)
        addr_wrapper = ctk.CTkFrame(fields_frame, fg_color="transparent")
        addr_wrapper.grid(row=3, column=0, columnspan=2, sticky="ew", padx=config.SPACING_SM, pady=config.SPACING_SM)
        ctk.CTkLabel(addr_wrapper, text="Full Address", font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold")).pack(anchor="w", pady=(0, 2))
        addr_entry = ctk.CTkEntry(addr_wrapper, height=config.INPUT_HEIGHT, placeholder_text="Complete Business Address", border_color=config.COLOR_BORDER, border_width=1)
        addr_entry.insert(0, self.db.get_setting(config.SETTING_SHOP_ADDRESS) or "")
        addr_entry.pack(fill="x")
        self.entries[config.SETTING_SHOP_ADDRESS] = addr_entry
        
        # Base Font Size Options
        scale_wrapper = ctk.CTkFrame(fields_frame, fg_color="transparent")
        scale_wrapper.grid(row=4, column=0, sticky="ew", padx=config.SPACING_SM, pady=config.SPACING_SM)
        ctk.CTkLabel(scale_wrapper, text="Base Font Size (px)", font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold")).pack(anchor="w", pady=(0, 2))
        
        self.scale_combo = ctk.CTkComboBox(
            scale_wrapper, 
            values=["8", "10", "12", "14", "16", "18"],
            height=config.INPUT_HEIGHT,
            border_color=config.COLOR_BORDER,
            border_width=1
        )
        # Set scale combo with fallback
        try:
            current_font = self.db.get_setting("base_font_size") or "12"
            self.scale_combo.set(current_font)
        except:
            self.scale_combo.set("12")
        self.scale_combo.pack(fill="x")
        
        # Save Button
        save_btn = AnimatedButton(
            scroll_frame,
            text="💾 Save All Settings",
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_SUCCESS,
            hover_color="#059669",
            command=self._save_settings
        )
        save_btn.pack(pady=config.SPACING_XL, anchor="center")


    def _create_right_panel(self):
        # Right Panel — wrapped in scrollable frame so all options are always visible
        right_outer = ctk.CTkFrame(self.main_container, fg_color="transparent")
        right_outer.grid(row=0, column=1, sticky="nsew")
        right_outer.grid_columnconfigure(0, weight=1)
        right_outer.grid_rowconfigure(0, weight=1)

        right_panel = ctk.CTkScrollableFrame(
            right_outer, fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY)
        right_panel.pack(fill="both", expand=True)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # ── UPI Payment Settings
        upi_card = ctk.CTkFrame(right_panel, fg_color=config.COLOR_BG_CARD,
                                corner_radius=config.RADIUS_LG,
                                border_width=1, border_color=config.COLOR_BORDER)
        upi_card.pack(fill="x", pady=(0, config.SPACING_MD))
        
        ctk.CTkLabel(upi_card, text="📲 UPI Payment Settings",
                     font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
                     text_color=config.COLOR_PRIMARY).pack(pady=(config.SPACING_LG, config.SPACING_SM),
                                                           padx=config.SPACING_LG, anchor="w")
        
        upi_form = ctk.CTkFrame(upi_card, fg_color="transparent")
        upi_form.pack(fill="x", padx=config.SPACING_LG, pady=(0, config.SPACING_MD))
        
        ctk.CTkLabel(upi_form, text="UPI ID (e.g. shop@ybl)",
                     font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold")).pack(anchor="w")
        self.upi_entry = ctk.CTkEntry(upi_form, height=config.INPUT_HEIGHT,
                                       placeholder_text="yourshop@upi/ybl/paytm")
        self.upi_entry.insert(0, self.db.get_setting("upi_id") or "")
        self.upi_entry.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(upi_form, text="Shop Name (shown on QR)",
                     font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold")).pack(anchor="w")
        self.shop_name_upi_entry = ctk.CTkEntry(upi_form, height=config.INPUT_HEIGHT,
                                                 placeholder_text="Shree Ganesha Silk")
        self.shop_name_upi_entry.insert(0, self.db.get_setting("shop_name") or "")
        self.shop_name_upi_entry.pack(fill="x", pady=(0, 8))
        
        def save_upi():
            upi = self.upi_entry.get().strip()
            sn = self.shop_name_upi_entry.get().strip()
            if upi: self.db.update_setting("upi_id", upi)
            if sn: self.db.update_setting("shop_name", sn)
            messagebox.showinfo("Saved", "UPI settings saved!")
        
        AnimatedButton(upi_form, text="💾 Save UPI Settings", height=32,
                       fg_color=config.COLOR_SUCCESS, command=save_upi).pack(fill="x")
        
        # Hardware / Printer
        printer_card = ctk.CTkFrame(right_panel, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG, border_width=1, border_color=config.COLOR_BORDER)
        printer_card.pack(fill="x", pady=(0, config.SPACING_MD))
        
        ctk.CTkLabel(printer_card, text="🖨️ Printer Integration", font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"), text_color=config.COLOR_PRIMARY).pack(pady=(config.SPACING_LG, config.SPACING_SM), padx=config.SPACING_LG, anchor="w")
        
        self.printer_combo = ctk.CTkComboBox(
            printer_card,
            values=self._get_printers() or ["Default"],
            height=config.INPUT_HEIGHT,
            border_color=config.COLOR_BORDER,
            border_width=1
        )
        current_printer = self.db.get_setting("printer_name")
        self.printer_combo.set(current_printer if current_printer else "Default")
        self.printer_combo.pack(fill="x", padx=config.SPACING_LG, pady=(0, config.SPACING_LG))
        
        # Admin Actions
        admin_card = ctk.CTkFrame(right_panel, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG, border_width=1, border_color=config.COLOR_BORDER)
        admin_card.pack(fill="x", pady=(0, config.SPACING_MD))
        
        ctk.CTkLabel(admin_card, text="🛡️ Security & Backup", font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"), text_color=config.COLOR_PRIMARY).pack(pady=(config.SPACING_LG, config.SPACING_SM), padx=config.SPACING_LG, anchor="w")
        
        self.switches = {}
        switch_frame = ctk.CTkFrame(admin_card, fg_color="transparent")
        switch_frame.pack(fill="x", padx=config.SPACING_LG, pady=(0, config.SPACING_MD))
        
        ctk.CTkLabel(switch_frame, text="Global Security", font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold")).pack(anchor="w", pady=(0, 5))
        
        # Login Password Switch
        pwd_val = self.db.get_setting(config.SETTING_REQUIRE_LOGIN_PASSWORD)
        pwd_var = ctk.StringVar(value=pwd_val if pwd_val is not None else "1")
        self.switches[config.SETTING_REQUIRE_LOGIN_PASSWORD] = pwd_var
        
        pwd_switch = ctk.CTkSwitch(switch_frame, text="Require Password on Login", variable=pwd_var, onvalue="1", offvalue="0")
        pwd_switch.pack(anchor="w", pady=(0, config.SPACING_SM))
        
        # Admin PIN Switch (Master)
        pin_val = self.db.get_setting(config.SETTING_REQUIRE_ADMIN_PIN)
        pin_var = ctk.StringVar(value=pin_val if pin_val is not None else "1")
        self.switches[config.SETTING_REQUIRE_ADMIN_PIN] = pin_var
        
        pin_switch = ctk.CTkSwitch(switch_frame, text="Require PIN for Actions", variable=pin_var, onvalue="1", offvalue="0")
        pin_switch.pack(anchor="w", pady=(0, config.SPACING_SM))
        
        ctk.CTkLabel(switch_frame, text="Module Specific PIN Locks", font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        # Module Toggles
        self._add_module_toggle(switch_frame, "🔒 Lock Stock Inventory", config.SETTING_PIN_STOCK)
        self._add_module_toggle(switch_frame, "🔒 Lock New Purchase (GRN)", config.SETTING_PIN_NEW_STOCK)
        self._add_module_toggle(switch_frame, "🔒 Lock Bills & Invoices", config.SETTING_PIN_BILLS)
        self._add_module_toggle(switch_frame, "🔒 Lock Reports", config.SETTING_PIN_REPORTS)
        self._add_module_toggle(switch_frame, "🔒 Lock Settings", config.SETTING_PIN_SETTINGS)
        
        
        btn_frame = ctk.CTkFrame(admin_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=config.SPACING_LG, pady=(0, config.SPACING_LG))
        
        AnimatedButton(btn_frame, text="👥 Manage Users & Permissions", height=config.BUTTON_HEIGHT, fg_color="#0EA5E9", hover_color="#0284C7", command=self._manage_users).pack(fill="x", pady=(0, config.SPACING_SM))
        AnimatedButton(btn_frame, text="🔐 Change Admin PIN", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_WARNING, hover_color="#D97706", command=self._change_pin).pack(fill="x", pady=(0, config.SPACING_SM))
        AnimatedButton(btn_frame, text="🔑 Change Admin Password", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_SECONDARY, hover_color="#9333EA", command=self._change_admin_password).pack(fill="x", pady=(0, config.SPACING_SM))
        
        backup_row = ctk.CTkFrame(btn_frame, fg_color="transparent")
        backup_row.pack(fill="x")
        AnimatedButton(backup_row, text="⚡ Quick Backup", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_INFO, hover_color="#2563EB", command=self._backup_database_quick).pack(side="left", fill="x", expand=True, padx=(0, 2))
        AnimatedButton(backup_row, text="📂 Custom Backup", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_INFO, hover_color="#2563EB", command=self._backup_database).pack(side="right", fill="x", expand=True, padx=(2, 0))
        
        # About
        about_card = ctk.CTkFrame(right_panel, fg_color=config.COLOR_BG_CARD, corner_radius=config.RADIUS_LG, border_width=1, border_color=config.COLOR_PRIMARY)
        about_card.pack(fill="x", expand=True, side="bottom")
        
        about_text = f"""{config.APP_NAME}
Version {config.VERSION}

{config.COMPANY}
{config.APP_SUBTITLE}

A premium inventory and billing solution 
with an elegantly streamlined UI."""
        
        ctk.CTkLabel(about_card, text=about_text, font=ctk.CTkFont(size=config.FONT_SIZE_SMALL), text_color=config.COLOR_TEXT_PRIMARY, justify="center").pack(padx=config.SPACING_LG, pady=config.SPACING_XL, expand=True)

    def _add_module_toggle(self, parent, text, key):
        val = self.db.get_setting(key)
        var = ctk.StringVar(value=val if val is not None else "1")
        self.switches[key] = var
        switch = ctk.CTkSwitch(parent, text=text, variable=var, onvalue="1", offvalue="0")
        switch.pack(anchor="w", pady=(0, config.SPACING_XS), padx=10)

    def _save_settings(self):
        """Save settings"""
        try:
            for key, entry in self.entries.items():
                value = entry.get().strip()
                if value:
                    self.db.update_setting(key, value)
                    
            if hasattr(self, 'switches'):
                for key, var in self.switches.items():
                    self.db.update_setting(key, var.get())
            
            # Save printer
            printer = self.printer_combo.get()
            if printer and printer != "Default":
                self.db.update_setting("printer_name", printer)
            else:
                self.db.update_setting("printer_name", "") # Clear if default
                
            # Save Base Font Size
            base_font_size = self.scale_combo.get()
            self.db.update_setting("base_font_size", base_font_size)
            
            messagebox.showinfo("Success", "Settings saved successfully! Some changes may require an application restart.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def _manage_users(self):
        """Open user management and permissions dialog"""
        if not verify_admin_pin(self.winfo_toplevel(), db_manager=self.db):
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manage Users & Permissions")
        dialog.geometry("600x500")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 600) // 2
        y = (dialog.winfo_screenheight() - 500) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Split layout
        left_f = ctk.CTkFrame(dialog, width=200, fg_color=config.COLOR_BG_CARD)
        left_f.pack(side="left", fill="y", padx=10, pady=10)
        left_f.pack_propagate(False)
        
        right_f = ctk.CTkFrame(dialog, fg_color=config.COLOR_BG_CARD)
        right_f.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(left_f, text="Users", font=("Arial", 14, "bold")).pack(pady=10)
        users_listbox = ctk.CTkScrollableFrame(left_f, fg_color="transparent")
        users_listbox.pack(fill="both", expand=True)
        
        self.selected_user_id = None
        
        def load_users():
            for widget in users_listbox.winfo_children(): widget.destroy()
            users = self.db.execute_query("SELECT user_id, username, role FROM users WHERE role != 'admin'")
            for uid, uname, role in users:
                btn = ctk.CTkButton(users_listbox, text=f"{uname}\n({role})", fg_color="transparent", 
                                  text_color=config.COLOR_TEXT_PRIMARY, hover_color=config.COLOR_BG_HOVER,
                                  command=lambda id=uid, n=uname: load_user_details(id, n))
                btn.pack(fill="x", pady=2)
                
        # Rights UI
        detail_header = ctk.CTkLabel(right_f, text="Select a user to edit permissions", font=("Arial", 14, "bold"))
        detail_header.pack(pady=10)
        
        perms_frame = ctk.CTkScrollableFrame(right_f, fg_color="transparent")
        perms_frame.pack(fill="both", expand=True, padx=10)
        
        modules = [
            ("billing", "New Bill"), ("stock", "Stock"), ("new_stock", "New Stock"),
            ("search", "Search"), ("reports", "Reports"), ("bills", "Manage Bills"),
            ("purchases", "Purchases"), ("suppliers", "Supplier Master"), ("salesmen", "Salesman Master"),
            ("settings", "Settings")
        ]
        
        perm_vars = {}
        for key, name in modules:
            var = ctk.BooleanVar(value=False)
            perm_vars[key] = var
            cb = ctk.CTkCheckBox(perms_frame, text=name, variable=var)
            cb.pack(anchor="w", pady=5)
            # hide checkboxes initially
            cb.pack_forget()
            
        def load_user_details(uid, uname):
            self.selected_user_id = uid
            detail_header.configure(text=f"Permissions for {uname}")
            
            import json
            res = self.db.execute_query("SELECT permissions FROM users WHERE user_id=?", (uid,))
            perms = {}
            if res and res[0][0]:
                try: perms = json.loads(res[0][0])
                except Exception: pass
                
            for cb in perms_frame.winfo_children(): cb.pack(anchor="w", pady=5)
            
            for key, var in perm_vars.items():
                var.set(perms.get(key, False))
                
        def save_perms():
            if not self.selected_user_id:
                messagebox.showwarning("Select User", "Please select a user first.", parent=dialog)
                return
            import json
            new_perms = {key: var.get() for key, var in perm_vars.items()}
            try:
                self.db.execute_query(
                    "UPDATE users SET permissions=? WHERE user_id=?",
                    (json.dumps(new_perms), self.selected_user_id)
                )
                messagebox.showinfo(
                    "Saved",
                    "Permissions updated successfully!\n"
                    "The user must log out and log in again for changes to take effect.",
                    parent=dialog
                )
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to save: {ex}", parent=dialog)
            
        save_btn = ctk.CTkButton(right_f, text="Save Permissions", fg_color=config.COLOR_SUCCESS, command=save_perms)
        
        def show_create_user():
            # Add user logic quickly inside the same dialog area
            add_d = ctk.CTkToplevel(dialog)
            add_d.title("Add New User")
            add_d.geometry("300x250")
            add_d.transient(dialog)
            add_d.grab_set()
            
            ctk.CTkLabel(add_d, text="Username").pack(pady=(10, 0))
            un_ent = ctk.CTkEntry(add_d)
            un_ent.pack(pady=(0, 10))
            
            ctk.CTkLabel(add_d, text="Password").pack()
            pw_ent = ctk.CTkEntry(add_d, show="*")
            pw_ent.pack(pady=(0, 10))
            
            def do_add():
                un = un_ent.get().strip()
                pw = pw_ent.get().strip()
                if not un or not pw: return
                import hashlib
                pw_hash = hashlib.sha256(pw.encode()).hexdigest()
                try:
                    self.db.execute_query("INSERT INTO users (username, password_hash, role, permissions) VALUES (?, ?, 'salesman', '{}')", (un, pw_hash))
                    load_users()
                    add_d.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed: {str(e)}", parent=add_d)
                    
            ctk.CTkButton(add_d, text="Create", command=do_add).pack(pady=10)
            
        btn_action = ctk.CTkFrame(left_f, fg_color="transparent")
        btn_action.pack(side="bottom", fill="x", pady=10)
        ctk.CTkButton(btn_action, text="+ Add User", width=120, command=show_create_user).pack()
        
        save_btn.pack(pady=10)
        load_users()

    
    def _change_pin(self):
        """Change admin PIN"""
        if not verify_admin_pin(self.winfo_toplevel(), db_manager=self.db):
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Admin PIN")
        dialog.geometry("400x350")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        ctk.CTkLabel(main_frame, text="Enter New PIN", font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold")).pack(pady=(config.SPACING_LG, config.SPACING_SM))
        
        new_pin_entry = ctk.CTkEntry(main_frame, height=config.INPUT_HEIGHT, placeholder_text="New PIN", show="*", justify="center")
        new_pin_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        confirm_pin_entry = ctk.CTkEntry(main_frame, height=config.INPUT_HEIGHT, placeholder_text="Confirm PIN", show="*", justify="center")
        confirm_pin_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        def save_new_pin():
            new_pin = new_pin_entry.get()
            confirm_pin = confirm_pin_entry.get()
            
            if not new_pin or len(new_pin) < 4:
                messagebox.showerror("Error", "PIN must be at least 4 characters", parent=dialog)
                return
            if new_pin != confirm_pin:
                messagebox.showerror("Error", "PINs do not match", parent=dialog)
                return
            
            self.db.update_setting("admin_pin", new_pin)
            messagebox.showinfo("Success", f"PIN changed successfully!", parent=dialog)
            dialog.destroy()
        
        btn = ctk.CTkButton(main_frame, text="Save PIN", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_PRIMARY, command=save_new_pin)
        btn.pack(pady=config.SPACING_LG)
        
    def _change_admin_password(self):
        """Change admin password"""
        if not verify_admin_pin(self.winfo_toplevel(), db_manager=self.db):
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Admin Password")
        dialog.geometry("400x320")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        ctk.CTkLabel(main_frame, text="Change Admin Password", font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold")).pack(pady=(config.SPACING_LG, config.SPACING_SM))
        
        old_pw_entry = ctk.CTkEntry(main_frame, height=config.INPUT_HEIGHT, placeholder_text="Current Password", show="*", justify="center")
        old_pw_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        new_pw_entry = ctk.CTkEntry(main_frame, height=config.INPUT_HEIGHT, placeholder_text="New Password", show="*", justify="center")
        new_pw_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        confirm_pw_entry = ctk.CTkEntry(main_frame, height=config.INPUT_HEIGHT, placeholder_text="Confirm New Password", show="*", justify="center")
        confirm_pw_entry.pack(fill="x", padx=config.SPACING_XL, pady=config.SPACING_SM)
        
        def save_new_password():
            old_pw = old_pw_entry.get()
            new_pw = new_pw_entry.get()
            confirm_pw = confirm_pw_entry.get()
            
            if not old_pw or not new_pw or not confirm_pw:
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return
                
            if new_pw != confirm_pw:
                messagebox.showerror("Error", "New passwords do not match", parent=dialog)
                return
                
            import hashlib
            old_hash = hashlib.sha256(old_pw.encode()).hexdigest()
            new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
            
            users = self.db.execute_query("SELECT user_id, password_hash FROM users WHERE role = 'admin'")
            if not users:
                messagebox.showerror("Error", "Admin user not found in database", parent=dialog)
                return
                
            if users[0][1] != old_hash:
                messagebox.showerror("Error", "Current password is incorrect", parent=dialog)
                return
                
            admin_id = users[0][0]
            self.db.execute_query("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, admin_id))
            
            messagebox.showinfo("Success", "Admin password successfully updated!", parent=dialog)
            dialog.destroy()
            
        btn = ctk.CTkButton(main_frame, text="Save Password", height=config.BUTTON_HEIGHT, fg_color=config.COLOR_PRIMARY, command=save_new_password)
        btn.pack(pady=config.SPACING_LG)
    
    def _backup_database_quick(self):
        """Quick backup to a local 'backups' folder without prompts"""
        from shutil import copy2
        from datetime import datetime
        import os
        
        try:
            backup_dir = os.path.join(os.getcwd(), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"boutique_backup_quick_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_name)
            
            copy2(config.DB_NAME, backup_path)
            messagebox.showinfo("Success", f"Database quickly backed up!\nSaved to: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to quick backup database: {str(e)}")

    def _backup_database(self):
        """Backup database with folder selection"""
        from shutil import copy2
        from datetime import datetime
        from tkinter import filedialog
        import os
        
        try:
            # Ask user for backup directory
            backup_dir = filedialog.askdirectory(
                title="Select Backup Folder",
                parent=self.winfo_toplevel()
            )
            
            if not backup_dir:
                return # User cancelled
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"boutique_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_name)
            
            copy2(config.DB_NAME, backup_path)
            messagebox.showinfo("Success", f"Database backed up successfully!\nSaved to: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to backup database: {str(e)}")
    
    def _get_printers(self):
        """Get list of printers using PowerShell"""
        try:
            import subprocess
            cmd = "powershell \"Get-Printer | Select-Object -ExpandProperty Name\""
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                printers = [p.strip() for p in result.stdout.split('\n') if p.strip()]
                return ["Default"] + printers
            return ["Default"]
        except:
            return ["Default"]
