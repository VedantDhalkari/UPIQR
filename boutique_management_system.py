"""
Shree Ganesha SilkDeveloped by VedStacK Industries
A comprehensive inventory and billing solution for Women's Ethnic Wear Boutique
Created with CustomTkinter for modern, premium UI/UX
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os
from pathlib import Path
import hashlib
import json
from typing import Optional, List, Dict, Tuple
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# Application Configuration
class Config:
    APP_NAME = "Shree Ganesha Silk"
    VERSION = "1.0.0"
    DB_NAME = "boutique_database.db"
    ADMIN_PIN = "1234"  # Change this for production
    LOGO_PATH = "logo.png"  # Place your logo here
    
    # Theme Colors - Elegant Shree Ganesha SilkTheme
    COLOR_PRIMARY = "#8B0000"  # Deep Maroon
    COLOR_SECONDARY = "#FFD700"  # Gold
    COLOR_ACCENT = "#C76D7E"  # Rose Gold
    COLOR_BG_DARK = "#1a1a1a"
    COLOR_BG_LIGHT = "#f5f5f5"
    COLOR_TEXT_LIGHT = "#ffffff"
    COLOR_TEXT_DARK = "#333333"
    
    # GST Configuration
    GST_RATE = 5  # 5% GST for textiles
    
    # Low stock threshold
    LOW_STOCK_THRESHOLD = 5

# Database Manager
class DatabaseManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Create all necessary tables"""
        self.connect()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Stock/Inventory table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku_code TEXT UNIQUE NOT NULL,
                saree_type TEXT NOT NULL,
                material TEXT NOT NULL,
                color TEXT NOT NULL,
                design TEXT,
                quantity INTEGER NOT NULL,
                purchase_price REAL NOT NULL,
                selling_price REAL NOT NULL,
                supplier_name TEXT,
                category TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sales/Bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                gst_amount REAL NOT NULL,
                final_amount REAL NOT NULL,
                payment_method TEXT,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        ''')
        
        # Sale Items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                sale_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                sku_code TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
                FOREIGN KEY (item_id) REFERENCES inventory(item_id)
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        ''')
        
        # Create default admin user if not exists
        try:
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", password_hash, "admin")
            )
        except sqlite3.IntegrityError:
            pass
        
        # Initialize settings
        self._initialize_settings()
        
        self.conn.commit()
        self.disconnect()
    
    def _initialize_settings(self):
        """Initialize default settings"""
        default_settings = {
            "shop_name": "Shree Ganesha Silk",
            "shop_address": "123 Fashion Street, City",
            "shop_phone": "+91 9876543210",
            "shop_email": "info@elitesarees.com",
            
            "bill_prefix": "ESB",
            "theme_mode": "dark"
        }
        
        for key, value in default_settings.items():
            try:
                self.cursor.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            except sqlite3.IntegrityError:
                pass
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a query and return results"""
        self.connect()
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()
        self.conn.commit()
        self.disconnect()
        return results
    
    def execute_insert(self, query: str, params: tuple = ()):
        """Execute insert query and return last row id"""
        self.connect()
        self.cursor.execute(query, params)
        last_id = self.cursor.lastrowid
        self.conn.commit()
        self.disconnect()
        return last_id
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        result = self.execute_query(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,)
        )
        return result[0][0] if result else None
    
    def update_setting(self, key: str, value: str):
        """Update a setting value"""
        self.execute_query(
            "UPDATE settings SET setting_value = ? WHERE setting_key = ?",
            (value, key)
        )

# PDF Invoice Generator
class InvoiceGenerator:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.invoices_dir = Path("invoices")
        self.invoices_dir.mkdir(exist_ok=True)
    
    def generate_invoice(self, sale_id: int) -> str:
        """Generate PDF invoice for a sale"""
        # Get sale details
        sale_data = self.db.execute_query(
            """SELECT bill_number, customer_name, customer_phone, total_amount,
               discount_percent, discount_amount, gst_amount, final_amount,
               payment_method, sale_date FROM sales WHERE sale_id = ?""",
            (sale_id,)
        )[0]
        
        # Get sale items
        items_data = self.db.execute_query(
            """SELECT sku_code, item_name, quantity, unit_price, total_price
               FROM sale_items WHERE sale_id = ?""",
            (sale_id,)
        )
        
        # Get shop details
        shop_name = self.db.get_setting("shop_name")
        shop_address = self.db.get_setting("shop_address")
        shop_phone = self.db.get_setting("shop_phone")
        shop_email = self.db.get_setting("shop_email")
        gst_number = self.db.get_setting("gst_number")
        
        # Create PDF
        bill_number = sale_data[0]
        filename = self.invoices_dir / f"{bill_number}.pdf"
        
        doc = SimpleDocTemplate(str(filename), pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8B0000'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        # Shop Header
        story.append(Paragraph(shop_name, title_style))
        story.append(Paragraph(f"{shop_address}", header_style))
        story.append(Paragraph(f"Phone: {shop_phone} | Email: {shop_email}", header_style))
        story.append(Paragraph(f"GSTIN: {gst_number}", header_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice details
        story.append(Paragraph(f"<b>INVOICE</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        invoice_info = [
            ["Bill No:", bill_number, "Date:", sale_data[9][:10]],
            ["Customer:", sale_data[1] or "Walk-in", "Phone:", sale_data[2] or "N/A"]
        ]
        
        t = Table(invoice_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Items table
        items_table_data = [
            ["SKU", "Item Description", "Qty", "Rate", "Amount"]
        ]
        
        for item in items_data:
            items_table_data.append([
                item[0],
                item[1],
                str(item[2]),
                f"₹{item[3]:.2f}",
                f"₹{item[4]:.2f}"
            ])
        
        items_table = Table(items_table_data, colWidths=[1.2*inch, 3*inch, 0.8*inch, 1.2*inch, 1.3*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totals
        totals_data = [
            ["", "", "", "Subtotal:", f"₹{sale_data[3]:.2f}"],
            ["", "", "", f"Discount ({sale_data[4]}%):", f"- ₹{sale_data[5]:.2f}"],
            ["", "", "", f"GST ({Config.GST_RATE}%):", f"₹{sale_data[6]:.2f}"],
            ["", "", "", "Grand Total:", f"₹{sale_data[7]:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[1.2*inch, 3*inch, 0.8*inch, 1.2*inch, 1.3*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, 0), (-1, -1), 10),
            ('LINEABOVE', (3, -1), (-1, -1), 2, colors.black),
            ('FONTSIZE', (3, -1), (-1, -1), 12),
            ('TEXTCOLOR', (3, -1), (-1, -1), colors.HexColor('#8B0000')),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        story.append(Paragraph("Thank you for shopping with us!", header_style))
        story.append(Paragraph("*Terms & Conditions Apply", styles['Italic']))
        
        # Build PDF
        doc.build(story)
        return str(filename)

# Main Application Class
class BoutiqueManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"{Config.APP_NAME} - Management System")
        self.geometry("1400x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize database
        self.db = DatabaseManager(Config.DB_NAME)
        self.invoice_generator = InvoiceGenerator(self.db)
        
        # Current user
        self.current_user = None
        
        # Initialize UI
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login screen"""
        self.clear_window()
        
        # Create main frame
        login_frame = ctk.CTkFrame(self, fg_color=Config.COLOR_BG_DARK)
        login_frame.pack(fill="both", expand=True)
        
        # Create center frame
        center_frame = ctk.CTkFrame(login_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=20)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            center_frame,
            text=Config.APP_NAME,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        )
        title_label.pack(pady=(40, 10), padx=60)
        
        subtitle_label = ctk.CTkLabel(
            center_frame,
            text="Developed by VedStacK Industries",
            font=ctk.CTkFont(size=14),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username
        username_label = ctk.CTkLabel(
            center_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        username_label.pack(pady=(10, 5), padx=40, anchor="w")
        
        username_entry = ctk.CTkEntry(
            center_frame,
            width=300,
            height=40,
            placeholder_text="Enter username"
        )
        username_entry.pack(pady=(0, 15), padx=40)
        
        # Password
        password_label = ctk.CTkLabel(
            center_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        password_label.pack(pady=(10, 5), padx=40, anchor="w")
        
        password_entry = ctk.CTkEntry(
            center_frame,
            width=300,
            height=40,
            placeholder_text="Enter password",
            show="*"
        )
        password_entry.pack(pady=(0, 30), padx=40)
        
        # Login button
        def login():
            username = username_entry.get()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            result = self.db.execute_query(
                "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            if result:
                self.current_user = {
                    "id": result[0][0],
                    "username": result[0][1],
                    "role": result[0][2]
                }
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        
        login_button = ctk.CTkButton(
            center_frame,
            text="Login",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Config.COLOR_SECONDARY,
            text_color=Config.COLOR_TEXT_DARK,
            hover_color=Config.COLOR_ACCENT,
            command=login
        )
        login_button.pack(pady=(0, 40), padx=40)
        
        # Bind enter key
        password_entry.bind('<Return>', lambda e: login())
    
    def verify_admin_pin(self) -> bool:
        """Verify admin PIN for protected sections"""
        dialog = ctk.CTkInputDialog(
            text="Enter Admin PIN:",
            title="Admin Verification"
        )
        pin = dialog.get_input()
        
        if pin == Config.ADMIN_PIN:
            return True
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN")
            return False
    
    def show_dashboard(self):
        """Display main dashboard"""
        self.clear_window()
        
        # Create main container
        main_container = ctk.CTkFrame(self, fg_color=Config.COLOR_BG_DARK)
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        sidebar = ctk.CTkFrame(main_container, width=250, fg_color=Config.COLOR_PRIMARY, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo/Title in sidebar
        logo_label = ctk.CTkLabel(
            sidebar,
            text=Config.APP_NAME,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        )
        logo_label.pack(pady=(30, 10), padx=20)
        
        user_label = ctk.CTkLabel(
            sidebar,
            text=f"Welcome, {self.current_user['username']}",
            font=ctk.CTkFont(size=12),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        user_label.pack(pady=(0, 30), padx=20)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🛒 New Bill", self.show_billing_screen),
            ("📦 Stock Management", lambda: self.show_stock_management() if self.verify_admin_pin() else None),
            ("➕ New Stock Entry", lambda: self.show_new_stock_entry() if self.verify_admin_pin() else None),
            ("🔍 Global Search", self.show_global_search),
            ("📊 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings),
            ("🚪 Logout", self.show_login_screen)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                sidebar,
                text=text,
                width=220,
                height=45,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color=Config.COLOR_TEXT_LIGHT,
                hover_color=Config.COLOR_ACCENT,
                anchor="w",
                command=command
            )
            btn.pack(pady=5, padx=15)
        
        # Main content area
        self.content_frame = ctk.CTkFrame(main_container, fg_color=Config.COLOR_BG_DARK)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Load dashboard content
        self.load_dashboard_content()
    
    def load_dashboard_content(self):
        """Load dashboard metrics and information"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 30), anchor="w")
        
        # Metrics frame
        metrics_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, 30))
        
        # Get today's sales
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = self.db.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0) 
               FROM sales WHERE DATE(sale_date) = ?""",
            (today,)
        )[0]
        
        # Get total inventory value
        inventory_value = self.db.execute_query(
            "SELECT COALESCE(SUM(quantity * selling_price), 0) FROM inventory"
        )[0][0]
        
        # Get low stock items
        low_stock = self.db.execute_query(
            "SELECT COUNT(*) FROM inventory WHERE quantity <= ?",
            (Config.LOW_STOCK_THRESHOLD,)
        )[0][0]
        
        # Total items
        total_items = self.db.execute_query("SELECT COUNT(*) FROM inventory")[0][0]
        
        # Create metric cards
        metrics_data = [
            ("Today's Sales", f"₹{today_sales[1]:,.2f}", f"{today_sales[0]} Bills", Config.COLOR_SECONDARY),
            ("Inventory Value", f"₹{inventory_value:,.2f}", f"{total_items} Items", "#4CAF50"),
            ("Low Stock Alert", f"{low_stock} Items", "Need Restock", "#FF5252" if low_stock > 0 else "#4CAF50"),
        ]
        
        for i, (title, value, subtitle, color) in enumerate(metrics_data):
            card = ctk.CTkFrame(metrics_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
            card.grid(row=0, column=i, padx=15, sticky="ew")
            metrics_frame.grid_columnconfigure(i, weight=1)
            
            card_title = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14),
                text_color=Config.COLOR_TEXT_LIGHT
            )
            card_title.pack(pady=(20, 5), padx=20)
            
            card_value = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            card_value.pack(pady=5, padx=20)
            
            card_subtitle = ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(size=12),
                text_color=Config.COLOR_TEXT_LIGHT
            )
            card_subtitle.pack(pady=(5, 20), padx=20)
        
        # Recent transactions
        recent_frame = ctk.CTkFrame(self.content_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        recent_frame.pack(fill="both", expand=True)
        
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="Recent Transactions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        recent_title.pack(pady=20, padx=20, anchor="w")
        
        # Create table frame
        table_frame = ctk.CTkFrame(recent_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Get recent sales
        recent_sales = self.db.execute_query(
            """SELECT bill_number, customer_name, final_amount, sale_date
               FROM sales ORDER BY sale_date DESC LIMIT 10"""
        )
        
        # Create headers
        headers = ["Bill No", "Customer", "Amount", "Date"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                table_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=Config.COLOR_SECONDARY
            )
            lbl.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Add data rows
        for i, sale in enumerate(recent_sales, 1):
            ctk.CTkLabel(table_frame, text=sale[0], text_color=Config.COLOR_TEXT_LIGHT).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(table_frame, text=sale[1] or "Walk-in", text_color=Config.COLOR_TEXT_LIGHT).grid(row=i, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(table_frame, text=f"₹{sale[2]:,.2f}", text_color=Config.COLOR_TEXT_LIGHT).grid(row=i, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(table_frame, text=sale[3][:16], text_color=Config.COLOR_TEXT_LIGHT).grid(row=i, column=3, padx=10, pady=5, sticky="w")
    
    def show_billing_screen(self):
        """Display billing interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="New Bill / Invoice",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Main layout: Left (search/items) and Right (cart/summary)
        main_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = ctk.CTkFrame(main_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Search section
        search_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=20)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="Search Items (SKU/Name/Color)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        search_label.pack(anchor="w", pady=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            width=400,
            height=40,
            placeholder_text="Type to search..."
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        # Items display
        items_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        items_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Right panel - Cart
        right_panel = ctk.CTkFrame(main_frame, width=450, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        cart_title = ctk.CTkLabel(
            right_panel,
            text="Cart Items",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        )
        cart_title.pack(pady=20, padx=20, anchor="w")
        
        # Cart items frame
        cart_items_frame = ctk.CTkScrollableFrame(right_panel, fg_color="transparent", height=300)
        cart_items_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Customer details
        customer_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(customer_frame, text="Customer Name (Optional):", text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w", pady=(0, 5))
        customer_name_entry = ctk.CTkEntry(customer_frame, height=35)
        customer_name_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(customer_frame, text="Phone (Optional):", text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w", pady=(0, 5))
        customer_phone_entry = ctk.CTkEntry(customer_frame, height=35)
        customer_phone_entry.pack(fill="x", pady=(0, 10))
        
        # Discount
        ctk.CTkLabel(customer_frame, text="Discount %:", text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w", pady=(0, 5))
        discount_entry = ctk.CTkEntry(customer_frame, height=35, placeholder_text="0")
        discount_entry.pack(fill="x")
        
        # Summary
        summary_frame = ctk.CTkFrame(right_panel, fg_color=Config.COLOR_BG_DARK, corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=20)
        
        subtotal_label = ctk.CTkLabel(summary_frame, text="Subtotal: ₹0.00", font=ctk.CTkFont(size=14), text_color=Config.COLOR_TEXT_LIGHT)
        subtotal_label.pack(pady=5, padx=15, anchor="w")
        
        discount_label = ctk.CTkLabel(summary_frame, text="Discount: ₹0.00", font=ctk.CTkFont(size=14), text_color=Config.COLOR_TEXT_LIGHT)
        discount_label.pack(pady=5, padx=15, anchor="w")
        
        gst_label = ctk.CTkLabel(summary_frame, text=f"GST ({Config.GST_RATE}%): ₹0.00", font=ctk.CTkFont(size=14), text_color=Config.COLOR_TEXT_LIGHT)
        gst_label.pack(pady=5, padx=15, anchor="w")
        
        total_label = ctk.CTkLabel(summary_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color=Config.COLOR_SECONDARY)
        total_label.pack(pady=10, padx=15, anchor="w")
        
        # Cart storage
        cart = []
        
        def update_summary():
            """Update cart summary"""
            subtotal = sum(item['total'] for item in cart)
            discount_percent = float(discount_entry.get() or 0)
            discount_amount = subtotal * (discount_percent / 100)
            after_discount = subtotal - discount_amount
            gst_amount = after_discount * (Config.GST_RATE / 100)
            total = after_discount + gst_amount
            
            subtotal_label.configure(text=f"Subtotal: ₹{subtotal:,.2f}")
            discount_label.configure(text=f"Discount ({discount_percent}%): ₹{discount_amount:,.2f}")
            gst_label.configure(text=f"GST ({Config.GST_RATE}%): ₹{gst_amount:,.2f}")
            total_label.configure(text=f"Total: ₹{total:,.2f}")
        
        def add_to_cart(item_data):
            """Add item to cart"""
            # Check if item already in cart
            for cart_item in cart:
                if cart_item['item_id'] == item_data['item_id']:
                    if cart_item['quantity'] < item_data['available_qty']:
                        cart_item['quantity'] += 1
                        cart_item['total'] = cart_item['quantity'] * cart_item['price']
                    else:
                        messagebox.showwarning("Stock Limit", "Cannot add more than available quantity")
                        return
                    break
            else:
                cart.append({
                    'item_id': item_data['item_id'],
                    'sku': item_data['sku'],
                    'name': item_data['name'],
                    'price': item_data['price'],
                    'quantity': 1,
                    'total': item_data['price'],
                    'available_qty': item_data['available_qty']
                })
            
            refresh_cart()
        
        def refresh_cart():
            """Refresh cart display"""
            for widget in cart_items_frame.winfo_children():
                widget.destroy()
            
            for i, item in enumerate(cart):
                item_frame = ctk.CTkFrame(cart_items_frame, fg_color=Config.COLOR_BG_DARK, corner_radius=8)
                item_frame.pack(fill="x", pady=5)
                
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
                
                ctk.CTkLabel(info_frame, text=f"{item['name']}", font=ctk.CTkFont(size=12, weight="bold"), text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"SKU: {item['sku']} | ₹{item['price']}", font=ctk.CTkFont(size=10), text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w")
                
                qty_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                qty_frame.pack(side="right", padx=10)
                
                def make_decrease(idx):
                    return lambda: decrease_qty(idx)
                
                def make_increase(idx):
                    return lambda: increase_qty(idx)
                
                def make_remove(idx):
                    return lambda: remove_item(idx)
                
                ctk.CTkButton(qty_frame, text="-", width=30, height=30, command=make_decrease(i)).pack(side="left", padx=2)
                ctk.CTkLabel(qty_frame, text=str(item['quantity']), width=40, text_color=Config.COLOR_TEXT_LIGHT).pack(side="left", padx=5)
                ctk.CTkButton(qty_frame, text="+", width=30, height=30, command=make_increase(i)).pack(side="left", padx=2)
                ctk.CTkButton(qty_frame, text="✕", width=30, height=30, fg_color="#FF5252", hover_color="#D32F2F", command=make_remove(i)).pack(side="left", padx=(10, 0))
            
            update_summary()
        
        def decrease_qty(idx):
            if cart[idx]['quantity'] > 1:
                cart[idx]['quantity'] -= 1
                cart[idx]['total'] = cart[idx]['quantity'] * cart[idx]['price']
                refresh_cart()
        
        def increase_qty(idx):
            if cart[idx]['quantity'] < cart[idx]['available_qty']:
                cart[idx]['quantity'] += 1
                cart[idx]['total'] = cart[idx]['quantity'] * cart[idx]['price']
                refresh_cart()
            else:
                messagebox.showwarning("Stock Limit", "Cannot exceed available quantity")
        
        def remove_item(idx):
            cart.pop(idx)
            refresh_cart()
        
        def search_items(event=None):
            """Search and display items"""
            query = search_entry.get().strip()
            
            for widget in items_frame.winfo_children():
                widget.destroy()
            
            if len(query) < 2:
                return
            
            results = self.db.execute_query(
                """SELECT item_id, sku_code, saree_type, material, color, selling_price, quantity
                   FROM inventory 
                   WHERE (sku_code LIKE ? OR saree_type LIKE ? OR color LIKE ? OR material LIKE ?)
                   AND quantity > 0
                   LIMIT 20""",
                (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
            )
            
            for item in results:
                item_card = ctk.CTkFrame(items_frame, fg_color=Config.COLOR_BG_DARK, corner_radius=10)
                item_card.pack(fill="x", pady=5)
                
                info_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
                
                name_text = f"{item[2]} - {item[3]} ({item[4]})"
                ctk.CTkLabel(info_frame, text=name_text, font=ctk.CTkFont(size=13, weight="bold"), text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"SKU: {item[1]} | Stock: {item[6]}", font=ctk.CTkFont(size=11), text_color=Config.COLOR_TEXT_LIGHT).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"₹{item[5]:,.2f}", font=ctk.CTkFont(size=14, weight="bold"), text_color=Config.COLOR_SECONDARY).pack(anchor="w")
                
                add_btn = ctk.CTkButton(
                    item_card,
                    text="Add to Cart",
                    width=120,
                    height=35,
                    fg_color=Config.COLOR_SECONDARY,
                    text_color=Config.COLOR_TEXT_DARK,
                    hover_color=Config.COLOR_ACCENT,
                    command=lambda i=item: add_to_cart({
                        'item_id': i[0],
                        'sku': i[1],
                        'name': f"{i[2]} - {i[3]} ({i[4]})",
                        'price': i[5],
                        'available_qty': i[6]
                    })
                )
                add_btn.pack(side="right", padx=15, pady=10)
        
        search_entry.bind('<KeyRelease>', search_items)
        
        def complete_sale():
            """Complete the sale and generate invoice"""
            if not cart:
                messagebox.showerror("Error", "Cart is empty")
                return
            
            try:
                # Calculate totals
                subtotal = sum(item['total'] for item in cart)
                discount_percent = float(discount_entry.get() or 0)
                discount_amount = subtotal * (discount_percent / 100)
                after_discount = subtotal - discount_amount
                gst_amount = after_discount * (Config.GST_RATE / 100)
                total = after_discount + gst_amount
                
                # Generate bill number
                bill_prefix = self.db.get_setting("bill_prefix")
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                bill_number = f"{bill_prefix}{timestamp}"
                
                # Insert sale
                sale_id = self.db.execute_insert(
                    """INSERT INTO sales (bill_number, customer_name, customer_phone,
                       total_amount, discount_percent, discount_amount, gst_amount,
                       final_amount, payment_method, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bill_number, customer_name_entry.get() or None,
                     customer_phone_entry.get() or None, subtotal, discount_percent,
                     discount_amount, gst_amount, total, "Cash",
                     self.current_user['username'])
                )
                
                # Insert sale items and update inventory
                for item in cart:
                    self.db.execute_insert(
                        """INSERT INTO sale_items (sale_id, item_id, sku_code, item_name,
                           quantity, unit_price, total_price)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (sale_id, item['item_id'], item['sku'], item['name'],
                         item['quantity'], item['price'], item['total'])
                    )
                    
                    # Update inventory
                    self.db.execute_query(
                        "UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?",
                        (item['quantity'], item['item_id'])
                    )
                
                # Generate invoice
                invoice_path = self.invoice_generator.generate_invoice(sale_id)
                
                messagebox.showinfo(
                    "Success",
                    f"Sale completed!\nBill Number: {bill_number}\nInvoice saved: {invoice_path}"
                )
                
                # Clear cart
                cart.clear()
                refresh_cart()
                customer_name_entry.delete(0, 'end')
                customer_phone_entry.delete(0, 'end')
                discount_entry.delete(0, 'end')
                search_entry.delete(0, 'end')
                
                # Ask if want to open invoice
                if messagebox.askyesno("Open Invoice", "Do you want to open the invoice?"):
                    os.startfile(invoice_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
        
        # Checkout button
        checkout_btn = ctk.CTkButton(
            right_panel,
            text="Complete Sale & Generate Invoice",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=Config.COLOR_SECONDARY,
            text_color=Config.COLOR_TEXT_DARK,
            hover_color=Config.COLOR_ACCENT,
            command=complete_sale
        )
        checkout_btn.pack(side="bottom", fill="x", padx=20, pady=20)
    
    def show_stock_management(self):
        """Display stock management interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Stock Management",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Search and filter frame
        filter_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 20))
        
        search_entry = ctk.CTkEntry(
            filter_frame,
            width=300,
            height=40,
            placeholder_text="Search by SKU, Type, Color..."
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            filter_frame,
            text="Refresh",
            width=100,
            height=40,
            command=lambda: load_stock()
        )
        refresh_btn.pack(side="left")
        
        # Stock table frame
        table_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color=Config.COLOR_PRIMARY)
        table_frame.pack(fill="both", expand=True)
        
        def load_stock(search_query=""):
            """Load and display stock"""
            for widget in table_frame.winfo_children():
                widget.destroy()
            
            # Headers
            headers = ["SKU", "Type", "Material", "Color", "Qty", "Purchase Price", "Selling Price", "Supplier", "Actions"]
            header_frame = ctk.CTkFrame(table_frame, fg_color=Config.COLOR_BG_DARK)
            header_frame.pack(fill="x", pady=(0, 10))
            
            for i, header in enumerate(headers):
                lbl = ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=Config.COLOR_SECONDARY,
                    width=120 if i < 8 else 150
                )
                lbl.grid(row=0, column=i, padx=5, pady=10)
            
            # Get stock data
            if search_query:
                items = self.db.execute_query(
                    """SELECT item_id, sku_code, saree_type, material, color, quantity,
                       purchase_price, selling_price, supplier_name
                       FROM inventory
                       WHERE sku_code LIKE ? OR saree_type LIKE ? OR color LIKE ? OR material LIKE ?
                       ORDER BY added_date DESC""",
                    (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")
                )
            else:
                items = self.db.execute_query(
                    """SELECT item_id, sku_code, saree_type, material, color, quantity,
                       purchase_price, selling_price, supplier_name
                       FROM inventory ORDER BY added_date DESC"""
                )
            
            # Display items
            for item in items:
                item_frame = ctk.CTkFrame(table_frame, fg_color=Config.COLOR_BG_DARK)
                item_frame.pack(fill="x", pady=2)
                
                # Highlight low stock
                bg_color = "#FF5252" if item[5] <= Config.LOW_STOCK_THRESHOLD else Config.COLOR_BG_DARK
                if item[5] <= Config.LOW_STOCK_THRESHOLD:
                    item_frame.configure(fg_color=bg_color, border_color="#FF0000", border_width=1)
                
                data = [item[1], item[2], item[3], item[4], str(item[5]), 
                       f"₹{item[6]}", f"₹{item[7]}", item[8] or "N/A"]
                
                for i, value in enumerate(data):
                    lbl = ctk.CTkLabel(
                        item_frame,
                        text=value,
                        text_color=Config.COLOR_TEXT_LIGHT,
                        width=120
                    )
                    lbl.grid(row=0, column=i, padx=5, pady=8)
                
                # Action buttons
                action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                action_frame.grid(row=0, column=8, padx=5, pady=5)
                
                def make_edit(item_id):
                    return lambda: edit_item(item_id)
                
                def make_delete(item_id):
                    return lambda: delete_item(item_id)
                
                ctk.CTkButton(
                    action_frame,
                    text="Edit",
                    width=60,
                    height=30,
                    fg_color=Config.COLOR_ACCENT,
                    command=make_edit(item[0])
                ).pack(side="left", padx=2)
                
                ctk.CTkButton(
                    action_frame,
                    text="Delete",
                    width=60,
                    height=30,
                    fg_color="#FF5252",
                    hover_color="#D32F2F",
                    command=make_delete(item[0])
                ).pack(side="left", padx=2)
        
        def edit_item(item_id):
            """Edit stock item"""
            # Get item details
            item = self.db.execute_query(
                "SELECT * FROM inventory WHERE item_id = ?",
                (item_id,)
            )[0]
            
            # Create edit dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Edit Stock Item")
            dialog.geometry("500x600")
            dialog.transient(self)
            dialog.grab_set()
            
            # Form fields
            fields = [
                ("SKU Code", item[1]),
                ("Saree Type", item[2]),
                ("Material", item[3]),
                ("Color", item[4]),
                ("Design", item[5] or ""),
                ("Quantity", str(item[6])),
                ("Purchase Price", str(item[7])),
                ("Selling Price", str(item[8])),
                ("Supplier", item[9] or ""),
                ("Category", item[10] or "")
            ]
            
            entries = {}
            for i, (label, value) in enumerate(fields):
                ctk.CTkLabel(dialog, text=label).pack(pady=(10, 0), padx=20, anchor="w")
                entry = ctk.CTkEntry(dialog, width=460)
                entry.insert(0, value)
                entry.pack(pady=(0, 5), padx=20)
                entries[label] = entry
            
            def save_changes():
                try:
                    self.db.execute_query(
                        """UPDATE inventory SET sku_code=?, saree_type=?, material=?, color=?,
                           design=?, quantity=?, purchase_price=?, selling_price=?, 
                           supplier_name=?, category=?, last_updated=CURRENT_TIMESTAMP
                           WHERE item_id=?""",
                        (entries["SKU Code"].get(), entries["Saree Type"].get(),
                         entries["Material"].get(), entries["Color"].get(),
                         entries["Design"].get(), int(entries["Quantity"].get()),
                         float(entries["Purchase Price"].get()),
                         float(entries["Selling Price"].get()),
                         entries["Supplier"].get(), entries["Category"].get(), item_id)
                    )
                    messagebox.showinfo("Success", "Item updated successfully")
                    dialog.destroy()
                    load_stock()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update: {str(e)}")
            
            ctk.CTkButton(
                dialog,
                text="Save Changes",
                command=save_changes,
                fg_color=Config.COLOR_SECONDARY,
                text_color=Config.COLOR_TEXT_DARK
            ).pack(pady=20)
        
        def delete_item(item_id):
            """Delete stock item"""
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
                try:
                    self.db.execute_query("DELETE FROM inventory WHERE item_id = ?", (item_id,))
                    messagebox.showinfo("Success", "Item deleted successfully")
                    load_stock()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete: {str(e)}")
        
        # Search functionality
        def search_stock(event=None):
            load_stock(search_entry.get())
        
        search_entry.bind('<KeyRelease>', search_stock)
        
        # Initial load
        load_stock()
    
    def show_new_stock_entry(self):
        """Display new stock entry form"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Add New Stock",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Form frame
        form_frame = ctk.CTkFrame(self.content_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Create scrollable form
        scroll_frame = ctk.CTkScrollableFrame(form_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Form fields
        fields = [
            "SKU Code*",
            "Saree Type*",
            "Material*",
            "Color*",
            "Design",
            "Quantity*",
            "Purchase Price*",
            "Selling Price*",
            "Supplier Name",
            "Category"
        ]
        
        entries = {}
        
        for field in fields:
            label = ctk.CTkLabel(
                scroll_frame,
                text=field,
                font=ctk.CTkFont(size=13),
                text_color=Config.COLOR_TEXT_LIGHT
            )
            label.pack(pady=(15, 5), anchor="w")
            
            entry = ctk.CTkEntry(scroll_frame, height=40, width=500)
            entry.pack(pady=(0, 5))
            entries[field] = entry
        
        # Buttons frame
        button_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        def save_stock():
            """Save new stock item"""
            try:
                # Validate required fields
                required = ["SKU Code*", "Saree Type*", "Material*", "Color*", "Quantity*", "Purchase Price*", "Selling Price*"]
                for field in required:
                    if not entries[field].get():
                        messagebox.showerror("Error", f"{field.replace('*', '')} is required")
                        return
                
                # Insert into database
                self.db.execute_insert(
                    """INSERT INTO inventory (sku_code, saree_type, material, color, design,
                       quantity, purchase_price, selling_price, supplier_name, category)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (entries["SKU Code*"].get(), entries["Saree Type*"].get(),
                     entries["Material*"].get(), entries["Color*"].get(),
                     entries["Design"].get() or None, int(entries["Quantity*"].get()),
                     float(entries["Purchase Price*"].get()),
                     float(entries["Selling Price*"].get()),
                     entries["Supplier Name"].get() or None,
                     entries["Category"].get() or None)
                )
                
                messagebox.showinfo("Success", "Stock item added successfully!")
                
                # Clear form
                for entry in entries.values():
                    entry.delete(0, 'end')
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "SKU Code already exists")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for quantity and prices")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add stock: {str(e)}")
        
        def clear_form():
            """Clear all form fields"""
            for entry in entries.values():
                entry.delete(0, 'end')
        
        ctk.CTkButton(
            button_frame,
            text="Save Stock",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Config.COLOR_SECONDARY,
            text_color=Config.COLOR_TEXT_DARK,
            hover_color=Config.COLOR_ACCENT,
            command=save_stock
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Clear Form",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#666666",
            hover_color="#555555",
            command=clear_form
        ).pack(side="left", padx=10)
    
    def show_global_search(self):
        """Display global search interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Global Search",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Search frame
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 20))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            width=500,
            height=50,
            placeholder_text="Search bills, customers, items, SKU codes...",
            font=ctk.CTkFont(size=14)
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            width=150,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Config.COLOR_SECONDARY,
            text_color=Config.COLOR_TEXT_DARK,
            command=lambda: perform_search()
        )
        search_btn.pack(side="left")
        
        # Results frame
        results_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color=Config.COLOR_PRIMARY)
        results_frame.pack(fill="both", expand=True)
        
        def perform_search():
            """Perform global search"""
            query = search_entry.get().strip()
            
            if not query:
                messagebox.showwarning("Empty Search", "Please enter a search term")
                return
            
            # Clear results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            # Search bills
            ctk.CTkLabel(
                results_frame,
                text="Bills / Invoices",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=Config.COLOR_SECONDARY
            ).pack(pady=20, anchor="w", padx=20)
            
            bills = self.db.execute_query(
                """SELECT bill_number, customer_name, customer_phone, final_amount, sale_date
                   FROM sales
                   WHERE bill_number LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
                   ORDER BY sale_date DESC LIMIT 10""",
                (f"%{query}%", f"%{query}%", f"%{query}%")
            )
            
            if bills:
                for bill in bills:
                    bill_frame = ctk.CTkFrame(results_frame, fg_color=Config.COLOR_BG_DARK, corner_radius=10)
                    bill_frame.pack(fill="x", padx=20, pady=5)
                    
                    ctk.CTkLabel(
                        bill_frame,
                        text=f"Bill: {bill[0]} | Customer: {bill[1] or 'Walk-in'} | Amount: ₹{bill[3]:,.2f} | Date: {bill[4][:16]}",
                        text_color=Config.COLOR_TEXT_LIGHT
                    ).pack(pady=10, padx=15, anchor="w")
            else:
                ctk.CTkLabel(results_frame, text="No bills found", text_color=Config.COLOR_TEXT_LIGHT).pack(padx=20, anchor="w")
            
            # Search inventory
            ctk.CTkLabel(
                results_frame,
                text="Inventory Items",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=Config.COLOR_SECONDARY
            ).pack(pady=(30, 20), anchor="w", padx=20)
            
            items = self.db.execute_query(
                """SELECT sku_code, saree_type, material, color, quantity, selling_price
                   FROM inventory
                   WHERE sku_code LIKE ? OR saree_type LIKE ? OR material LIKE ? OR color LIKE ?
                   LIMIT 10""",
                (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
            )
            
            if items:
                for item in items:
                    item_frame = ctk.CTkFrame(results_frame, fg_color=Config.COLOR_BG_DARK, corner_radius=10)
                    item_frame.pack(fill="x", padx=20, pady=5)
                    
                    ctk.CTkLabel(
                        item_frame,
                        text=f"SKU: {item[0]} | {item[1]} - {item[2]} ({item[3]}) | Stock: {item[4]} | Price: ₹{item[5]:,.2f}",
                        text_color=Config.COLOR_TEXT_LIGHT
                    ).pack(pady=10, padx=15, anchor="w")
            else:
                ctk.CTkLabel(results_frame, text="No items found", text_color=Config.COLOR_TEXT_LIGHT).pack(padx=20, anchor="w")
        
        search_entry.bind('<Return>', lambda e: perform_search())
    
    def show_reports(self):
        """Display reports interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Reports & Analytics",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Report cards
        reports_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        reports_frame.pack(fill="both", expand=True)
        
        # Today's report
        today_card = ctk.CTkFrame(reports_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        today_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            today_card,
            text="Today's Sales Report",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        ).pack(pady=20, padx=20, anchor="w")
        
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = self.db.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0), COALESCE(SUM(total_amount), 0),
               COALESCE(SUM(discount_amount), 0), COALESCE(SUM(gst_amount), 0)
               FROM sales WHERE DATE(sale_date) = ?""",
            (today,)
        )[0]
        
        stats_text = f"""
        Total Bills: {today_data[0]}
        Gross Amount: ₹{today_data[2]:,.2f}
        Total Discount: ₹{today_data[3]:,.2f}
        GST Collected: ₹{today_data[4]:,.2f}
        Net Sales: ₹{today_data[1]:,.2f}
        """
        
        ctk.CTkLabel(
            today_card,
            text=stats_text,
            font=ctk.CTkFont(size=13),
            text_color=Config.COLOR_TEXT_LIGHT,
            justify="left"
        ).pack(pady=(0, 20), padx=20, anchor="w")
        
        # Monthly report
        month_card = ctk.CTkFrame(reports_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        month_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            month_card,
            text="This Month's Report",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        ).pack(pady=20, padx=20, anchor="w")
        
        month_start = datetime.now().strftime("%Y-%m-01")
        month_data = self.db.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0)
               FROM sales WHERE DATE(sale_date) >= ?""",
            (month_start,)
        )[0]
        
        month_stats_text = f"""
        Total Bills: {month_data[0]}
        Total Sales: ₹{month_data[1]:,.2f}
        Average Bill Value: ₹{(month_data[1] / month_data[0] if month_data[0] > 0 else 0):,.2f}
        """
        
        ctk.CTkLabel(
            month_card,
            text=month_stats_text,
            font=ctk.CTkFont(size=13),
            text_color=Config.COLOR_TEXT_LIGHT,
            justify="left"
        ).pack(pady=(0, 20), padx=20, anchor="w")
        
        # Low stock report
        low_stock_card = ctk.CTkFrame(reports_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        low_stock_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            low_stock_card,
            text="Low Stock Items",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        ).pack(pady=20, padx=20, anchor="w")
        
        low_stock_items = self.db.execute_query(
            """SELECT sku_code, saree_type, color, quantity
               FROM inventory WHERE quantity <= ?
               ORDER BY quantity ASC LIMIT 10""",
            (Config.LOW_STOCK_THRESHOLD,)
        )
        
        if low_stock_items:
            for item in low_stock_items:
                ctk.CTkLabel(
                    low_stock_card,
                    text=f"SKU: {item[0]} | {item[1]} ({item[2]}) - Stock: {item[3]}",
                    text_color="#FF5252"
                ).pack(pady=2, padx=20, anchor="w")
        else:
            ctk.CTkLabel(
                low_stock_card,
                text="All items are well stocked!",
                text_color="#4CAF50"
            ).pack(pady=10, padx=20, anchor="w")
        
        ctk.CTkLabel(low_stock_card, text="").pack(pady=10)
    
    def show_settings(self):
        """Display settings interface"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=Config.COLOR_TEXT_LIGHT
        )
        title.pack(pady=(0, 20), anchor="w")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color=Config.COLOR_PRIMARY, corner_radius=15)
        settings_frame.pack(fill="both", expand=True, padx=50, pady=20)
        
        scroll_frame = ctk.CTkScrollableFrame(settings_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Shop details
        ctk.CTkLabel(
            scroll_frame,
            text="Shop Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Config.COLOR_SECONDARY
        ).pack(pady=(0, 20), anchor="w")
        
        settings_fields = [
            ("Shop Name", "shop_name"),
            ("Address", "shop_address"),
            ("Phone", "shop_phone"),
            ("Email", "shop_email"),
            ("GST Number", "gst_number"),
            ("Bill Prefix", "bill_prefix")
        ]
        
        entries = {}
        
        for label, key in settings_fields:
            ctk.CTkLabel(
                scroll_frame,
                text=label,
                font=ctk.CTkFont(size=13),
                text_color=Config.COLOR_TEXT_LIGHT
            ).pack(pady=(15, 5), anchor="w")
            
            entry = ctk.CTkEntry(scroll_frame, height=40, width=500)
            entry.insert(0, self.db.get_setting(key) or "")
            entry.pack(pady=(0, 5))
            entries[key] = entry
        
        def save_settings():
            """Save settings"""
            try:
                for key, entry in entries.items():
                    self.db.update_setting(key, entry.get())
                messagebox.showinfo("Success", "Settings saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
        
        ctk.CTkButton(
            scroll_frame,
            text="Save Settings",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Config.COLOR_SECONDARY,
            text_color=Config.COLOR_TEXT_DARK,
            hover_color=Config.COLOR_ACCENT,
            command=save_settings
        ).pack(pady=30)

# Main Entry Point
if __name__ == "__main__":
    app = BoutiqueManagementApp()
    app.mainloop()
