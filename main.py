"""
Main Application Entry Point
Shree Ganesha Silk System with Premium Light Theme
"""

# ==========================================================
# COMMERCIAL PROTECTION ENFORCEMENT
# ==========================================================
import sys
try:
    from license_manager import EnterpriseProtector
    protector = EnterpriseProtector()
    protector.enforce_commercial_license()
except ImportError:
    import tkinter as ui_fail
    from tkinter import messagebox as msg_fail
    root = ui_fail.Tk()
    root.withdraw()
    msg_fail.showerror("Fatal Error", "Security Module Missing or Tampered. Application Terminated.")
    sys.exit(-1)
# ==========================================================

import customtkinter as ctk
from tkinter import messagebox
import config
import os
import logging

# Setup Logging
logging.basicConfig(
    filename='debug.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from database import DatabaseManager
from invoice_generator import InvoiceGenerator
from purchase_invoice_generator import PurchaseInvoiceGenerator
from auth import LoginScreen
from dashboard import Dashboard
from billing import BillingModule
from bill_management import BillManagementModule
from purchase_management import PurchaseManagementModule
from stock import StockManagementModule
from new_stock import NewStockModule
from search import GlobalSearchModule
from reports import ReportsModule
from settings import SettingsModule
from supplier_module import SupplierMasterModule
from salesman_module import SalesmanMasterModule


class BoutiqueManagementApp(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"{config.APP_NAME} - {config.APP_SUBTITLE}")
        self.geometry(f"{config.WINDOW_DEFAULT_WIDTH}x{config.WINDOW_DEFAULT_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        self.state("zoomed") # Start maximized
        
        # Set theme to light mode
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Initialize database
        self.db = DatabaseManager(config.DB_NAME)
        self.invoice_generator = InvoiceGenerator(self.db)
        self.purchase_invoice_generator = PurchaseInvoiceGenerator(self.db)
        
        # Current user
        self.current_user = None
        
        # Dashboard reference
        # Dashboard reference
        self.dashboard = None
        
        # Global Shortcuts (F1-F12)
        # Bind to root window so they work everywhere
        self.bind_all("<F1>", lambda e: self._global_navigate("dashboard"))
        self.bind_all("<F2>", lambda e: self._global_navigate("billing"))
        self.bind_all("<F3>", lambda e: self._global_navigate("stock"))
        self.bind_all("<F4>", lambda e: self._global_navigate("new_stock"))
        self.bind_all("<F5>", lambda e: self._global_navigate("search"))
        self.bind_all("<F6>", lambda e: self._global_navigate("reports"))
        self.bind_all("<F7>", lambda e: self._global_navigate("bills"))
        self.bind_all("<F8>", lambda e: self._global_navigate("purchases"))
        self.bind_all("<F9>", lambda e: self._global_open_calculator())
        self.bind_all("<F10>", lambda e: self._global_navigate("settings"))
        
        # UI widget scaling removed in favor of explicit base_font_size in modules
        
        # Initialize UI
        self.show_login_screen()

    def _global_navigate(self, screen):
        """Helper to navigate if dashboard is active"""
        if self.dashboard and self.current_user:
            try:
                self.dashboard._navigate(screen)
            except: pass

    def _global_open_calculator(self):
        """Helper to open calculator if dashboard active"""
        if self.dashboard:
            try:
                self.dashboard._open_calculator()
            except: pass
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        # Check if login is explicitly disabled
        req_pwd = self.db.get_setting(config.SETTING_REQUIRE_LOGIN_PASSWORD)
        if req_pwd == "0":
            # Auto login as admin
            try:
                user = self.db.execute_query("SELECT user_id, username, role FROM users WHERE role = 'admin' LIMIT 1")
                if user:
                    self._on_login_success({"id": user[0][0], "username": user[0][1], "role": user[0][2]})
                    return
            except Exception: pass
            
        login_screen = LoginScreen(
            self,
            on_login_success=self._on_login_success,
            db_manager=self.db
        )
        login_screen.pack(fill="both", expand=True)
    
    def _on_login_success(self, user: dict):
        """Handle successful login — load permissions from DB"""
        self.current_user = user
        # Load stored permissions for non-admin users
        if user.get('role') != 'admin':
            try:
                import json
                res = self.db.execute_query(
                    "SELECT permissions FROM users WHERE user_id = ?",
                    (user['id'],)
                )
                if res and res[0][0]:
                    user['permissions'] = json.loads(res[0][0])
                else:
                    user['permissions'] = {}
            except Exception:
                user['permissions'] = {}
        else:
            user['permissions'] = {}  # Admin has all access — dict unused
        self.show_dashboard()
    
    def show_dashboard(self):
        """Display main dashboard with sidebar"""
        self.clear_window()
        
        # Create dashboard
        self.dashboard = Dashboard(
            self,
            current_user=self.current_user,
            db_manager=self.db,
            on_navigate=self._handle_navigation
        )
        self.dashboard.pack(fill="both", expand=True)
    
    def _handle_navigation(self, screen: str, **kwargs):
        """Handle navigation from dashboard sidebar"""
        if screen == "logout":
            self._logout()
            return
        
        # Check Admin PIN for restricted sections
        module_pin_setting = None
        if screen == "stock": module_pin_setting = config.SETTING_PIN_STOCK
        elif screen == "new_stock": module_pin_setting = config.SETTING_PIN_NEW_STOCK
        elif screen == "reports": module_pin_setting = config.SETTING_PIN_REPORTS
        elif screen == "settings": module_pin_setting = config.SETTING_PIN_SETTINGS
        elif screen == "bills": module_pin_setting = config.SETTING_PIN_BILLS
        elif screen == "purchases": module_pin_setting = config.SETTING_PIN_BILLS
            
        if module_pin_setting:
            req_pin = self.db.get_setting(module_pin_setting)
            # If explicit module setting is 0 (Disabled), bypass the pin dialog, 
            # otherwise defer to the global PIN check.
            if req_pin != "0": 
                if not self._check_admin_pin():
                    if self.dashboard and self.dashboard.active_screen != screen:
                        self.dashboard._navigate(self.dashboard.active_screen)
                    return

        # --- Permission check for non-admin users ---
        if screen not in ("logout", "dashboard", "calculator") and self.current_user:
            if self.current_user.get('role') != 'admin':
                perms = self.current_user.get('permissions', {})
                # If perms explicitly says False for this screen, or if it's a restricted screen not mentioned as True
                if not perms.get(screen, False):
                    messagebox.showwarning(
                        "Access Denied",
                        f"You do not have permission to access '{screen}'.\n"
                        "Please contact your administrator."
                    )
                    return

        # Clear current content
        for widget in self.dashboard.content_frame.winfo_children():
            widget.destroy()
            
        try:
            if screen == "dashboard":
                # Reload dashboard content
                self.dashboard.load_dashboard_content()
            elif screen == "billing":
                BillingModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    invoice_generator=self.invoice_generator,
                    current_user=self.current_user,
                    **kwargs # Pass sale_id if present
                ).pack(fill="both", expand=True)
            elif screen == "purchases":
                PurchaseManagementModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    invoice_generator=self.invoice_generator,
                    purchase_invoice_generator=self.purchase_invoice_generator,
                    on_edit_purchase=lambda pid: self.dashboard._navigate("new_stock", purchase_id=pid)
                ).pack(fill="both", expand=True)
            elif screen == "stock":
                StockManagementModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    on_add_stock=lambda item_id=None, purchase_id=None: (
                        self.dashboard._navigate("new_stock", purchase_id=purchase_id)
                        if purchase_id
                        else self.dashboard._navigate("new_stock", prefill_item_id=item_id)
                    )
                ).pack(fill="both", expand=True)
            elif screen == "new_stock":
                NewStockModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    purchase_invoice_generator=self.purchase_invoice_generator,
                    on_new_supplier=lambda: self.dashboard._navigate("suppliers"),
                    **kwargs
                ).pack(fill="both", expand=True)
            elif screen == "search":
                GlobalSearchModule(
                    self.dashboard.content_frame,
                    db_manager=self.db
                ).pack(fill="both", expand=True)
            elif screen == "reports":
                ReportsModule(
                    self.dashboard.content_frame,
                    db_manager=self.db
                ).pack(fill="both", expand=True)
            elif screen == "settings":
                SettingsModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    current_user=self.current_user
                ).pack(fill="both", expand=True)
            elif screen == "bills":
                BillManagementModule(
                    self.dashboard.content_frame,
                    db_manager=self.db,
                    invoice_generator=self.invoice_generator,
                    on_edit_sale=lambda sid: self.dashboard._navigate("billing", sale_id=sid)
                ).pack(fill="both", expand=True)
            elif screen == "suppliers":
                SupplierMasterModule(
                    self.dashboard.content_frame,
                    db_manager=self.db
                ).pack(fill="both", expand=True)
            elif screen == "salesmen":
                SalesmanMasterModule(
                    self.dashboard.content_frame,
                    db_manager=self.db
                ).pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            err_msg = traceback.format_exc()
            logging.error(f"Navigation error to {screen}: {err_msg}")
            print("NAVIGATION CRASH:", err_msg)
            import tkinter.messagebox
            tkinter.messagebox.showerror("Module Error", f"Failed to load module {screen}\n\n{str(e)}\n\nCheck debug.log for details.")

    

    def _check_admin_pin(self) -> bool:
        """Prompt for Admin PIN"""
        req_pin = self.db.get_setting(config.SETTING_REQUIRE_ADMIN_PIN)
        if req_pin == "0":
            return True
            
        dialog = ctk.CTkInputDialog(
            text="Enter Admin PIN to access:",
            title="Restricted Access"
        )
        
        # Center the dialog
        dialog_width = 300
        dialog_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        pin = dialog.get_input()
        
        stored_pin = self.db.get_setting("admin_pin") or config.ADMIN_PIN
        
        if pin == stored_pin:
            return True
        elif pin is not None: # User entered something but wrong
            messagebox.showerror("Access Denied", "Incorrect PIN")
            return False
        return False # Cancelled

    def _logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.dashboard = None
            self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.winfo_children():
            widget.destroy()


# Main Entry Point
if __name__ == "__main__":
    app = BoutiqueManagementApp()
    app.mainloop()
