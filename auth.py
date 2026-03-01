"""
Authentication Module
Premium login screen and PIN verification dialogs
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable
import config


class LoginScreen(ctk.CTkFrame):
    """Premium split-screen login interface"""
    
    def __init__(self, parent, on_login_success: Callable, db_manager, **kwargs):
        """
        Create login screen
        
        Args:
            parent: Parent widget
            on_login_success: Callback function when login succeeds (receives user dict)
            db_manager: DatabaseManager instance
        """
        super().__init__(parent, fg_color=config.COLOR_BG_MAIN, **kwargs)
        
        self.on_login_success = on_login_success
        self.db = db_manager
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.85)
        
        # Left panel - Branding (40%)
        left_panel = ctk.CTkFrame(
            container,
            fg_color=config.COLOR_PRIMARY,
            corner_radius=config.RADIUS_XL
        )
        left_panel.place(relx=0, rely=0, relwidth=0.4, relheight=1)
        
        # Gradient effect simulation with overlays
        gradient_overlay = ctk.CTkFrame(
            left_panel,
            fg_color=config.COLOR_PRIMARY_LIGHT,
            corner_radius=config.RADIUS_XL
        )
        gradient_overlay.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)
        
        # Logo and branding
        import os
        from PIL import Image
        
        brand_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        brand_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(120, 120))
            logo_label = ctk.CTkLabel(brand_frame, text="", image=logo_img)
        except Exception:
            logo_label = ctk.CTkLabel(
                brand_frame,
                text=config.ICON_LOGO,
                font=ctk.CTkFont(size=80)
            )
        
        logo_label.pack(pady=(0, config.SPACING_LG))
        
        app_name = ctk.CTkLabel(
            brand_frame,
            text=config.APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=config.COLOR_TEXT_WHITE
        )
        app_name.pack(pady=(0, config.SPACING_SM))
        
        subtitle = ctk.CTkLabel(
            brand_frame,
            text=config.APP_SUBTITLE,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_WHITE
        )
        subtitle.pack(pady=(0, config.SPACING_SM))
        
        version = ctk.CTkLabel(
            brand_frame,
            text=f"Version {config.VERSION}",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_WHITE
        )
        version.pack()
        
        # Right panel - Login form (60%)
        right_panel = ctk.CTkFrame(
            container,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_XL
        )
        right_panel.place(relx=0.42, rely=0, relwidth=0.58, relheight=1)
        
        # Form content
        form_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)
        
        # Welcome heading
        welcome_label = ctk.CTkLabel(
            form_frame,
            text="Welcome Back!",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_2, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        welcome_label.pack(pady=(0, config.SPACING_SM))
        
        subtitle_label = ctk.CTkLabel(
            form_frame,
            text="Please sign in to continue",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, config.SPACING_XL))
        
        # Username field
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(config.SPACING_LG, config.SPACING_XS))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            height=config.INPUT_HEIGHT_LG,
            placeholder_text="Enter your username",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.username_entry.pack(fill="x", pady=(0, config.SPACING_MD))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        password_label.pack(anchor="w", pady=(config.SPACING_SM, config.SPACING_XS))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            height=config.INPUT_HEIGHT_LG,
            placeholder_text="Enter your password",
            show="*",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.password_entry.pack(fill="x", pady=(0, config.SPACING_XL))
        
        # Login button
        login_button = ctk.CTkButton(
            form_frame,
            text="Sign In",
            height=config.BUTTON_HEIGHT_LG,
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            corner_radius=config.RADIUS_MD,
            command=self._handle_login
        )
        login_button.pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Info box with default credentials
        info_frame = ctk.CTkFrame(
            form_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_INFO
        )
        info_frame.pack(fill="x", pady=(config.SPACING_LG, 0))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"ℹ️ Default Login\nUsername: {config.DEFAULT_USERNAME}\nPassword: {config.DEFAULT_PASSWORD}",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_INFO,
            justify="left"
        )
        info_label.pack(padx=config.SPACING_MD, pady=config.SPACING_MD)
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self._handle_login())
        
        # Focus username
        self.username_entry.focus()
    
    def _handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password")
            return
        
        # Verify credentials
        user = self.db.verify_user(username, password)
        
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Error", "Invalid username or password")
            self.password_entry.delete(0, "end")
            self.password_entry.focus()


class AdminPINDialog(ctk.CTkToplevel):
    """Modern PIN verification dialog"""
    
    def __init__(self, parent, db_manager=None, **kwargs):
        """
        Create PIN dialog
        
        Args:
            parent: Parent window
            db_manager: Database manager instance
        """
        super().__init__(parent, **kwargs)
        
        self.db = db_manager
        self.result = None
        
        # Window configuration
        self.title("Admin Verification")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Make modal
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_XL, pady=config.SPACING_XL)
        
        # Icon
        icon_label = ctk.CTkLabel(
            main_frame,
            text="🔐",
            font=ctk.CTkFont(size=60)
        )
        icon_label.pack(pady=(config.SPACING_LG, config.SPACING_SM))
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Admin Verification Required",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=(0, config.SPACING_SM))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Please enter admin PIN to continue",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, config.SPACING_LG))
        
        # PIN entry
        self.pin_entry = ctk.CTkEntry(
            main_frame,
            height=config.INPUT_HEIGHT_LG,
            placeholder_text="Enter PIN",
            show="*",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3),
            justify="center",
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.pin_entry.pack(fill="x", padx=config.SPACING_XL, pady=(0, config.SPACING_LG))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=config.SPACING_XL)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            height=config.BUTTON_HEIGHT,
            width=150,
            fg_color=config.COLOR_TEXT_SECONDARY,
            hover_color="#4B5563",
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=(0, config.SPACING_SM))
        
        verify_btn = ctk.CTkButton(
            button_frame,
            text="Verify",
            height=config.BUTTON_HEIGHT,
            width=150,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            command=self._on_verify
        )
        verify_btn.pack(side="right")
        
        # Bind Enter key
        self.pin_entry.bind("<Return>", lambda e: self._on_verify())
        
        # Focus PIN entry
        self.pin_entry.focus()
    
    def _on_verify(self):
        """Handle verify button"""
        pin = self.pin_entry.get()
        
        stored_pin = config.ADMIN_PIN
        if self.db:
            db_pin = self.db.get_setting("admin_pin")
            if db_pin:
                stored_pin = db_pin
        
        if pin == stored_pin:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN", parent=self)
            self.pin_entry.delete(0, "end")
            self.pin_entry.focus()
    
    def _on_cancel(self):
        """Handle cancel button"""
        self.result = False
        self.destroy()
    
    def get_result(self) -> bool:
        """
        Get verification result
        
        Returns:
            True if PIN verified, False otherwise
        """
        self.wait_window()
        return self.result == True


def verify_admin_pin(parent, db_manager=None) -> bool:
    """
    Show PIN dialog and verify admin access
    
    Args:
        parent: Parent window
        db_manager: Database manager instance
        
    Returns:
        True if PIN verified, False otherwise
    """
    if db_manager:
        req_pin = db_manager.get_setting(config.SETTING_REQUIRE_ADMIN_PIN)
        if req_pin == "0":
            return True
            
    dialog = AdminPINDialog(parent, db_manager=db_manager)
    return dialog.get_result()
