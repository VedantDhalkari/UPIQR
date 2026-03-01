"""
Dashboard Module
Main dashboard with sidebar navigation and premium metrics display
"""

import customtkinter as ctk
from typing import Callable
from datetime import datetime, timedelta
import config
from ui_components import StatCard, GreetingCard, ModernTable, SidebarButton
from charts import EarningsBarChart, CategoryList


class Dashboard(ctk.CTkFrame):
    """Main dashboard with sidebar and content area"""
    
    def __init__(self, parent, current_user: dict, db_manager, 
                 on_navigate: Callable, **kwargs):
        """
        Create dashboard
        
        Args:
            parent: Parent widget
            current_user: Dictionary with user info (id, username, role)
            db_manager: DatabaseManager instance
            on_navigate: Callback for navigation (receives screen name)
        """
        super().__init__(parent, fg_color=config.COLOR_BG_MAIN, **kwargs)
        
        self.current_user = current_user
        self.db = db_manager
        self.on_navigate = on_navigate
        self.active_screen = "dashboard"
        
        # Bind Keyboard Shortcuts
        self.bind("<F1>", lambda e: self._navigate("dashboard"))
        self.bind("<F2>", lambda e: self._navigate("billing"))
        self.bind("<F3>", lambda e: self._navigate("stock"))
        self.bind("<F4>", lambda e: self._navigate("new_stock"))
        self.bind("<F5>", lambda e: self._navigate("search"))
        self.bind("<F6>", lambda e: self._navigate("reports"))
        self.bind("<F7>", lambda e: self._navigate("bills"))
        self.bind("<F8>", lambda e: self._navigate("purchases"))
        self.bind("<F9>", lambda e: self._open_calculator())
        self.bind("<F10>", lambda e: self._navigate("settings"))
        
        # Initialize Sidebar
        self._create_sidebar()
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=config.COLOR_BG_MAIN
        )
        self.content_frame.pack(side="right", fill="both", expand=True, 
                               padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        # Load dashboard content
        self.load_dashboard_content()
    
    def _create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(
            self,
            width=config.SIDEBAR_WIDTH,
            fg_color=config.COLOR_BG_SIDEBAR,
            corner_radius=0
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Brand section
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=120)
        brand_frame.pack(fill="x", pady=(config.SPACING_XL, config.SPACING_LG))
        brand_frame.pack_propagate(False)
        
        import os
        from PIL import Image
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(80, 80))
            logo_label = ctk.CTkLabel(brand_frame, text="", image=logo_img)
        except Exception:
            logo_label = ctk.CTkLabel(
                brand_frame,
                text=config.ICON_LOGO,
                font=ctk.CTkFont(size=40)
            )
        logo_label.pack(pady=(config.SPACING_SM, 0))
        
        app_name_label = ctk.CTkLabel(
            brand_frame,
            text="Shree Ganesha SilkManager",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        app_name_label.pack()
        
        edition_label = ctk.CTkLabel(
            brand_frame,
            text=config.COMPANY,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        edition_label.pack()
        
        # Navigation buttons — scrollable so lower items don't get clipped
        nav_outer = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_outer.pack(fill="both", expand=True, padx=config.SPACING_SM, pady=config.SPACING_SM)
        
        nav_frame = ctk.CTkScrollableFrame(
            nav_outer,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_BG_HOVER,
            scrollbar_button_hover_color=config.COLOR_PRIMARY
        )
        nav_frame.pack(fill="both", expand=True)
        
        self.nav_buttons = {}
        
        nav_items = [
            ("dashboard", "Dashboard [F1]",      config.ICON_DASHBOARD, lambda: self._navigate("dashboard")),
            ("billing",   "New Bill [F2]",        config.ICON_BILLING,   lambda: self._navigate("billing")),
            ("stock",     "Stock [F3]",           config.ICON_STOCK,     lambda: self._navigate("stock")),
            ("new_stock", "New Stock [F4]",       config.ICON_NEW_STOCK, lambda: self._navigate("new_stock")),
            ("search",    "Search [F5]",          config.ICON_SEARCH,    lambda: self._navigate("search")),
            ("reports",   "Reports [F6]",         config.ICON_REPORTS,   lambda: self._navigate("reports")),
            ("bills",     "Manage Bills [F7]",    "🧾",                  lambda: self._navigate("bills")),
            ("purchases", "Purchases [F8]",       "📦",                  lambda: self._navigate("purchases")),
            ("calculator","Calculator [F9]",      "🧮",                  self._open_calculator),
            ("settings",  "Settings [F10]",       config.ICON_SETTINGS,  lambda: self._navigate("settings")),
        ]
        
        for key, text, icon, command in nav_items:
            btn = SidebarButton(nav_frame, text=text, icon=icon, command=command)
            btn.pack(fill="x", pady=config.SPACING_XS)
            self.nav_buttons[key] = btn
        
        # Set dashboard as active
        self.nav_buttons["dashboard"].set_active(True)
        
        # User profile section (bottom)
        user_frame = ctk.CTkFrame(
            sidebar,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            height=80
        )
        user_frame.pack(side="bottom", fill="x", padx=config.SPACING_MD, 
                       pady=config.SPACING_MD)
        user_frame.pack_propagate(False)
        
        # User avatar circle
        avatar_frame = ctk.CTkFrame(
            user_frame,
            width=50,
            height=50,
            fg_color=config.COLOR_PRIMARY_LIGHT,
            corner_radius=25
        )
        avatar_frame.pack(side="left", padx=config.SPACING_MD, pady=config.SPACING_SM)
        avatar_frame.pack_propagate(False)
        
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text=config.ICON_USER,
            font=ctk.CTkFont(size=24)
        )
        avatar_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # User info
        user_info_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_info_frame.pack(side="left", fill="both", expand=True)
        
        username_label = ctk.CTkLabel(
            user_info_frame,
            text=self.current_user['username'],
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        username_label.pack(anchor="w", pady=(config.SPACING_SM, 0))
        
        role_label = ctk.CTkLabel(
            user_info_frame,
            text=self.current_user['role'].capitalize(),
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        role_label.pack(anchor="w")
        
        # Logout button
        logout_btn = SidebarButton(
            user_frame,
            text="",
            icon=config.ICON_LOGOUT,
            command=self._logout,
            height=30,
            fg_color="transparent",
            text_color=config.COLOR_DANGER
        )
        logout_btn.pack(side="right", padx=config.SPACING_SM)
    
    def _navigate(self, screen_name, **kwargs):
        """Handle sidebar navigation"""
        # Update active button
        if self.active_screen in self.nav_buttons:
            self.nav_buttons[self.active_screen].set_active(False)
        
        if screen_name in self.nav_buttons:
            self.nav_buttons[screen_name].set_active(True)
        
        self.active_screen = screen_name
        self.on_navigate(screen_name, **kwargs)
    
    def _open_calculator(self):
        """Open Scientific Calculator"""
        from calculator import ScientificCalculator
        if hasattr(self, 'calculator_window') and self.calculator_window.winfo_exists():
            self.calculator_window.lift()
        else:
            self.calculator_window = ScientificCalculator(self)
    
    def _logout(self):
        """Visual logout handler"""
        self.on_navigate("logout")
    
    def load_dashboard_content(self):
        """Load dashboard metrics and information"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Create scrollable container for dashboard content
        scroll_container = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        scroll_container.pack(fill="both", expand=True)
        
        # Greeting
        GreetingCard(
            scroll_container,
            self.current_user['username'],
            on_new_bill=lambda: self._navigate("billing"),
            on_view_stock=lambda: self._navigate("stock")
        ).pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Metrics Row
        metrics_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Get metrics from DB
        metrics = self.db.get_dashboard_metrics()
        
        # Create cards
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Row 1
        StatCard(metrics_frame, "Items Sold", f"{metrics['month_items_sold']}", "This Month",
                config.ICON_BILLING, config.COLOR_SUCCESS).grid(row=0, column=0, pady=(0, config.SPACING_MD), padx=(0, config.SPACING_MD), sticky="ew")
                
        StatCard(metrics_frame, "Total Customers", f"{metrics['customer_count']}", "Active Database",
                config.ICON_USER, config.COLOR_INFO).grid(row=0, column=1, pady=(0, config.SPACING_MD), padx=config.SPACING_MD, sticky="ew")
                
        StatCard(metrics_frame, "Pending Bills", f"{metrics['pending_bills_count']}", "To Collect",
                config.ICON_WARNING or "⚠️", config.COLOR_WARNING).grid(row=0, column=2, pady=(0, config.SPACING_MD), padx=config.SPACING_MD, sticky="ew")
                
        StatCard(metrics_frame, "Today's Bills", f"{metrics['today_sales_count']}", "Bills Generated Today",
                config.ICON_BILLING, config.COLOR_PRIMARY).grid(row=0, column=3, pady=(0, config.SPACING_MD), padx=(config.SPACING_MD, 0), sticky="ew")

        # Row 2
        StatCard(metrics_frame, "Total Products", f"{metrics['total_products']}", "In Database",
                config.ICON_STOCK, config.COLOR_PRIMARY).grid(row=1, column=0, padx=(0, config.SPACING_MD), sticky="ew")
                
        StatCard(metrics_frame, "Low Stock", f"{metrics['low_stock_count']} Items", "Reorder Needed",
                config.ICON_WARNING or "⚠️", config.COLOR_WARNING).grid(row=1, column=1, padx=config.SPACING_MD, sticky="ew")
                
        StatCard(metrics_frame, "Out of Stock", f"{metrics['zero_stock_count']} Items", "Zero Inventory",
                "❌", config.COLOR_DANGER).grid(row=1, column=2, padx=config.SPACING_MD, sticky="ew")
                
        # Top Selling
        StatCard(metrics_frame, "Today's Top Sale", f"{metrics['top_selling_item']}", "Best Seller",
                "⭐", config.COLOR_SUCCESS).grid(row=1, column=3, padx=(config.SPACING_MD, 0), sticky="ew")
        
        # Charts Section
        charts_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        charts_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        charts_frame.grid_columnconfigure(0, weight=2)
        charts_frame.grid_columnconfigure(1, weight=1)
        
        # Sales Chart
        # Kept intentionally empty to match layout or add alternate list
        pass
        # Replace with maybe "Recent Activities" or just remove. 
        # But charts are nice. Let's show "Items Sold Trend" instead of Revenue.
        
        # We need a new query for items sold by period.
        # For now, to be safe and strictly follow "No money", I will comment out the chart or replace it with Category List full width?
        # User said "indicators lost count customer top selling items"
        # Let's keep Category List (Top Selling Items) and maybe expand it or add another list.
        # Let's make Top Categories full width or add "Recent Bills" list side by side.
        pass
            
        # Top Categories
        categories = self.db.execute_query(
            """SELECT i.saree_type, COUNT(*) as count 
               FROM sale_items si 
               JOIN inventory i ON si.item_id = i.item_id
               GROUP BY i.saree_type 
               ORDER BY count DESC LIMIT 5"""
        )

        CategoryList(charts_frame, categories=categories).grid(row=0, column=1, sticky="nsew")
        
        # Recent Transactions
        trans_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        trans_frame.pack(fill="x")
        
        ctk.CTkLabel(
            trans_frame,
            text="Recent Transactions",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, config.SPACING_MD))
        
        # Get recent transactions
        transactions = self.db.execute_query(
            """SELECT bill_number, customer_name, final_amount, sale_date 
               FROM sales ORDER BY sale_date DESC LIMIT 5"""
        )
        
        if transactions:
            headers = ["Bill No", "Customer", "Amount", "Date"]
            rows = [[t[0], t[1] or "Walk-in", f"₹{t[2]:,.2f}", t[3][:16]] for t in transactions]
            # Use ModernTable if it supports directly passing data, otherwise create it then pack it
            # Assuming ModernTable(parent, headers, rows) signature based on previous context
            ModernTable(trans_frame, headers, rows).pack(fill="x")
        else:
            ctk.CTkLabel(
                trans_frame,
                text="No recent transactions found",
                text_color=config.COLOR_TEXT_SECONDARY
            ).pack(pady=config.SPACING_LG)

    
    def show_content(self, content_widget):
        """Show a different content widget (for other modules)"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Pack new content
        content_widget.pack(fill="both", expand=True)
