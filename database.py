"""
Database Manager Module
Handles all SQLite database operations for the Shree Ganesha Silkmanagement system
"""

import sqlite3
import hashlib
from typing import Optional, List, Tuple, Any
import config


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_name: str):
        """
        Initialize database manager
        
        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def get_connection(self):
        """Get a raw connection for transaction management"""
        return sqlite3.connect(self.db_name)
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def initialize_database(self):
        """Create all necessary tables and default data"""
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
        
        # Custom Items for Billing (Placeholder)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku_code TEXT UNIQUE,
                barcode TEXT,
                saree_type TEXT NOT NULL,
                material TEXT,
                color TEXT,
                design TEXT,
                quantity INTEGER DEFAULT 0,
                purchase_price REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                supplier_name TEXT,
                category TEXT,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Suppliers Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                address TEXT,
                gstin TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Purchases Table (GRN / Receiving)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                invoice_number TEXT,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL DEFAULT 0,
                gst_amount REAL DEFAULT 0,
                other_expenses REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
            )
        ''')

        # Purchase Items Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                purchase_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                item_id INTEGER,
                sku_code TEXT,
                item_name TEXT,
                quantity INTEGER NOT NULL,
                purchase_rate REAL NOT NULL,
                mrp REAL,
                sale_rate REAL,
                total_amount REAL,
                FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id),
                FOREIGN KEY (item_id) REFERENCES inventory(item_id)
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
                amount_paid REAL DEFAULT 0,
                balance_due REAL DEFAULT 0,
                payment_status TEXT DEFAULT 'Paid',
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            )
        ''')
        
        # Migration for existing tables - Try adding columns if they don't exist
        # Migration for existing tables - Try adding columns if they don't exist
        try:
            self.cursor.execute("ALTER TABLE sales ADD COLUMN amount_paid REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE sales ADD COLUMN balance_due REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE sales ADD COLUMN payment_status TEXT DEFAULT 'Paid'")
        except: pass
        
        # New Phase 5 Columns
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN agent_name TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN transport TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN lr_no TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN bill_date TEXT") # Store as YYYY-MM-DD
        except: pass
        
        # New Phase 6 Columns
        try:
            self.cursor.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN gst_amount REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchases ADD COLUMN other_expenses REAL DEFAULT 0")
        except: pass

        # Inventory & Purchase Items
        try:
            self.cursor.execute("ALTER TABLE inventory ADD COLUMN brand TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE inventory ADD COLUMN unit TEXT DEFAULT 'PC'")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE inventory ADD COLUMN gst_percentage REAL DEFAULT 0")
        except: pass
        
        try:
            self.cursor.execute("ALTER TABLE purchase_items ADD COLUMN brand TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchase_items ADD COLUMN unit TEXT")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchase_items ADD COLUMN gst_percentage REAL DEFAULT 0")
        except: pass
        try:
            self.cursor.execute("ALTER TABLE purchase_items ADD COLUMN batch_no TEXT")
        except: pass
        
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
        
        # Payment History table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                amount_paid REAL NOT NULL,
                payment_method TEXT NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_note TEXT,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            )
        ''')
        
        # Stock Entries (Purchase History) table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_entries (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                quantity_added INTEGER NOT NULL,
                purchase_price REAL NOT NULL,
                supplier_name TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                admin_note TEXT,
                FOREIGN KEY (item_id) REFERENCES inventory(item_id)
            )
        ''')

        # Create default admin user
        try:
            password_hash = hashlib.sha256(config.DEFAULT_PASSWORD.encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (config.DEFAULT_USERNAME, password_hash, "admin")
            )
        except sqlite3.IntegrityError:
            pass  # User already exists
        
        # Initialize default settings
        self._initialize_settings()
        
        self.conn.commit()
        self.disconnect()
    
    def _initialize_settings(self):
        """Initialize default settings"""
        default_settings = {
            config.SETTING_SHOP_NAME: config.DEFAULT_SHOP_NAME,
            config.SETTING_SHOP_ADDRESS: config.DEFAULT_SHOP_ADDRESS,
            config.SETTING_SHOP_PHONE: config.DEFAULT_SHOP_PHONE,
            config.SETTING_SHOP_EMAIL: config.DEFAULT_SHOP_EMAIL,
            config.SETTING_GST_NUMBER: config.DEFAULT_GST_NUMBER,
            config.SETTING_BILL_PREFIX: config.BILL_PREFIX,
            config.SETTING_THEME_MODE: "light",
            config.SETTING_REQUIRE_LOGIN_PASSWORD: "1",
            config.SETTING_REQUIRE_ADMIN_PIN: "1",
            config.SETTING_PIN_STOCK: "1",
            config.SETTING_PIN_NEW_STOCK: "1",
            config.SETTING_PIN_BILLS: "1",
            config.SETTING_PIN_REPORTS: "1",
            config.SETTING_PIN_SETTINGS: "1"
        }
        
        for key, value in default_settings.items():
            try:
                self.cursor.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (?, ?)",
                    (key, value)
                )
            except sqlite3.IntegrityError:
                pass  # Setting already exists
    
    def execute_query(self, query: str, params: tuple = (), cursor=None) -> List[Tuple]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            cursor: Optional existing cursor for transaction buffer
            
        Returns:
            List of result tuples
        """
        if cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
            
        self.connect()
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            self.conn.commit()
            return results
        finally:
            self.disconnect()
    
    def execute_insert(self, query: str, params: tuple = (), cursor=None) -> int:
        """
        Execute an INSERT query and return the last row ID
        
        Args:
            query: SQL INSERT query string
            params: Query parameters tuple
            cursor: Optional existing cursor for transaction buffer
            
        Returns:
            Last inserted row ID
        """
        if cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
            
        self.connect()
        try:
            self.cursor.execute(query, params)
            last_id = self.cursor.lastrowid
            self.conn.commit()
            return last_id
        finally:
            self.disconnect()

    def add_stock_entry(self, item_id: int, qty: int, price: float, supplier: str, note: str = "", cursor=None):
        """Add a stock entry record"""
        self.execute_insert(
            """INSERT INTO stock_entries (item_id, quantity_added, purchase_price, supplier_name, admin_note)
               VALUES (?, ?, ?, ?, ?)""",
            (item_id, qty, price, supplier, note),
            cursor=cursor
        )

    def get_or_create_custom_item(self) -> int:
        """Create or retrieve a generic custom item for ad-hoc billing"""
        item = self.execute_query("SELECT item_id FROM inventory WHERE sku_code = 'CUSTOM'")
        if item:
            return item[0][0]
            
        return self.execute_insert(
            """INSERT INTO inventory (sku_code, barcode, saree_type, quantity, purchase_price, selling_price)
               VALUES ('CUSTOM', 'CUSTOM', 'Custom Item', 99999, 0, 0)"""
        )

    def get_stock_entries(self, limit: int = 50) -> List[Tuple]:
        """Get recent stock entries with item details"""
        return self.execute_query(
            """SELECT se.entry_id, i.sku_code, i.saree_type, se.quantity_added, 
                      se.purchase_price, se.supplier_name, se.date_added, se.admin_note, se.item_id
               FROM stock_entries se
               JOIN inventory i ON se.item_id = i.item_id
               ORDER BY se.date_added DESC
               LIMIT ?""",
            (limit,)
        )
    
    def delete_stock_entry(self, entry_id: int):
        """Delete a stock entry and revert inventory quantity"""
        # Get entry details first
        entry = self.execute_query("SELECT item_id, quantity_added FROM stock_entries WHERE entry_id = ?", (entry_id,))
        if not entry:
            return
            
        item_id, qty = entry[0]
        
        # Revert inventory
        self.execute_query("UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?", (qty, item_id))
        
        # Delete entry
        self.execute_query("DELETE FROM stock_entries WHERE entry_id = ?", (entry_id,))

    def delete_bill(self, bill_number: str):
        """Delete a bill and revert stock"""
        # Get sale_id
        sale = self.execute_query("SELECT sale_id FROM sales WHERE bill_number = ?", (bill_number,))
        if not sale:
            raise ValueError("Bill not found")
        sale_id = sale[0][0]
        
        # Get items to revert stock
        items = self.execute_query("SELECT item_id, quantity FROM sale_items WHERE sale_id = ?", (sale_id,))
        
        self.connect()
        try:
            # Revert stock
            for item_id, qty in items:
                self.cursor.execute("UPDATE inventory SET quantity = quantity + ? WHERE item_id = ?", (qty, item_id))
            
            # Delete items and sale
            self.cursor.execute("DELETE FROM sale_items WHERE sale_id = ?", (sale_id,))
            self.cursor.execute("DELETE FROM sales WHERE sale_id = ?", (sale_id,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

    def get_bill_details(self, bill_number: str) -> dict:
        """Get full details of a bill including items"""
        sale = self.execute_query(
            """SELECT sale_id, bill_number, customer_name, customer_phone, 
                      total_amount, discount_percent, final_amount, sale_date 
               FROM sales WHERE bill_number = ?""",
            (bill_number,)
        )
        if not sale:
            return None
            
        sale_data = sale[0]
        items = self.execute_query(
            """SELECT item_id, sku_code, item_name, quantity, unit_price, total_price 
               FROM sale_items WHERE sale_id = ?""",
            (sale_data[0],)
        )
        
        return {
            "sale_id": sale_data[0],
            "bill_number": sale_data[1],
            "customer_name": sale_data[2],
            "customer_phone": sale_data[3],
            "subtotal": sale_data[4],
            "discount_percent": sale_data[5],
            "total": sale_data[6],
            "date": sale_data[7],
            "items": [
                {
                    "item_id": i[0],
                    "sku": i[1],
                    "name": i[2],
                    "quantity": i[3],
                    "price": i[4],
                    "total": i[5]
                } for i in items
            ]
        }
    
    def get_setting(self, key: str) -> Optional[str]:
        """
        Get a setting value by key
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        result = self.execute_query(
            "SELECT setting_value FROM settings WHERE setting_key = ?",
            (key,)
        )
        return result[0][0] if result else None
    
    def update_setting(self, key: str, value: str):
        """
        Update or insert a setting value
        
        Args:
            key: Setting key
            value: New value
        """
        self.execute_query(
            "INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
            (key, value)
        )
    
    def verify_user(self, username: str, password: str) -> Optional[dict]:
        """
        Verify user credentials
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User dict with id, username, role or None if invalid
        """
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = self.execute_query(
            "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        if result:
            return {
                "id": result[0][0],
                "username": result[0][1],
                "role": result[0][2]
            }
        return None
    
    def get_dashboard_metrics(self) -> dict:
        """
        Get dashboard metrics
        
        Returns:
            Dictionary with today_sales, month_sales, low_stock_count, total_items
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        month_start = datetime.now().strftime("%Y-%m-01")
        
        # Today's sales
        today_result = self.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0) 
               FROM sales WHERE DATE(sale_date) = ?""",
            (today,)
        )
        
        # Monthly Profit (Est. based on current purchase price)
        month_profit = self.execute_query(
            """SELECT COALESCE(SUM((si.unit_price - i.purchase_price) * si.quantity), 0)
               FROM sale_items si
               JOIN inventory i ON si.item_id = i.item_id
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) >= ?""",
            (month_start,)
        )
        
        # Total Items Sold (Month)
        month_items_sold = self.execute_query(
            """SELECT COALESCE(SUM(si.quantity), 0)
               FROM sale_items si
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) >= ?""",
            (month_start,)
        )
        
        # Stock Value
        stock_value = self.execute_query(
            "SELECT COALESCE(SUM(quantity * purchase_price), 0) FROM inventory"
        )
        
        # Low stock count
        low_stock = self.execute_query(
            "SELECT COUNT(*) FROM inventory WHERE quantity <= ?",
            (config.LOW_STOCK_THRESHOLD,)
        )
        
        # Zero stock count
        zero_stock = self.execute_query(
            "SELECT COUNT(*) FROM inventory WHERE quantity = 0"
        )
        
        # Total products
        total_products = self.execute_query(
            "SELECT COUNT(*) FROM inventory"
        )
        
        # Top selling item today
        top_item = self.execute_query(
            """SELECT i.saree_type, SUM(si.quantity) as qty
               FROM sale_items si
               JOIN inventory i ON si.item_id = i.item_id
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) = ?
               GROUP BY i.item_id
               ORDER BY qty DESC
               LIMIT 1""",
            (today,)
        )
        top_selling = (top_item[0][0][:20] if len(top_item[0][0]) > 20 else top_item[0][0]) if top_item else "None"
        
        return {
            "today_sales_count": today_result[0][0],
            "month_items_sold": month_items_sold[0][0],
            "low_stock_count": low_stock[0][0],
            "zero_stock_count": zero_stock[0][0],
            "total_products": total_products[0][0],
            "top_selling_item": top_selling,
            "pending_bills_count": self.execute_query("SELECT COUNT(*) FROM sales WHERE payment_status != 'Paid'")[0][0],
            "customer_count": self.execute_query("SELECT COUNT(DISTINCT customer_phone) FROM sales")[0][0]
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Tuple]:
        """
        Get recent transactions
        
        Args:
            limit: Number of transactions to retrieve
            
        Returns:
            List of transaction tuples
        """
        return self.execute_query(
            """SELECT bill_number, customer_name, final_amount, sale_date
               FROM sales ORDER BY sale_date DESC LIMIT ?""",
            (limit,)
        )
    
    def get_top_categories(self, limit: int = 5) -> List[Tuple]:
        """
        Get top selling categories
        
        Args:
            limit: Number of categories to retrieve
            
        Returns:
            List of (category, total_sales) tuples
        """
        return self.execute_query(
            """SELECT i.category, SUM(si.total_price) as total_sales
               FROM sale_items si
               JOIN inventory i ON si.item_id = i.item_id
               WHERE i.category IS NOT NULL
               GROUP BY i.category
               ORDER BY total_sales DESC
               LIMIT ?""",
            (limit,)
        )
    
    def get_sales_by_period(self, period: str = "today") -> List[Tuple]:
        """
        Get sales data for a specific period
        
        Args:
            period: "today", "week", or "month"
            
        Returns:
            List of (date, amount) tuples
        """
        from datetime import datetime, timedelta
        
        if period == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            return self.execute_query(
                """SELECT strftime('%H:00', sale_date) as hour, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) = ?
                   GROUP BY hour ORDER BY hour""",
                (today,)
            )
        elif period == "week":
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            return self.execute_query(
                """SELECT DATE(sale_date) as day, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) >= ?
                   GROUP BY day ORDER BY day""",
                (week_ago,)
            )
        else:  # month
            month_start = datetime.now().strftime("%Y-%m-01")
            return self.execute_query(
                """SELECT DATE(sale_date) as day, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) >= ?
                   GROUP BY day ORDER BY day""",
                (month_start,)
            )

    def get_bill_details(self, bill_number: str) -> dict:
        """Get full details of a bill including items"""
        sale = self.execute_query(
            """SELECT sale_id, bill_number, customer_name, customer_phone, 
               total_amount, discount_percent, final_amount, sale_date 
               FROM sales WHERE bill_number = ?""",
            (bill_number,)
        )
        if not sale:
            return None
            
        sale_data = sale[0]
        items = self.execute_query(
            """SELECT item_id, sku_code, item_name, quantity, unit_price, total_price 
               FROM sale_items WHERE sale_id = ?""",
            (sale_data[0],)
        )
        
        return {
            "sale_id": sale_data[0],
            "bill_number": sale_data[1],
            "customer_name": sale_data[2],
            "customer_phone": sale_data[3],
            "subtotal": sale_data[4],
            "discount_percent": sale_data[5],
            "total": sale_data[6],
            "date": sale_data[7],
            "items": [
                {
                    "item_id": i[0],
                    "sku": i[1],
                    "name": i[2],
                    "quantity": i[3],
                    "price": i[4],
                    "total": i[5]
                } for i in items
            ]
        }

    def get_or_create_custom_item(self) -> int:
        """Get or create a placeholder item for custom sales"""
        result = self.execute_query("SELECT item_id FROM inventory WHERE sku_code = 'CUSTOM'")
        if result:
            return result[0][0]
        
        # Create
        return self.execute_insert(
            """INSERT INTO inventory (sku_code, saree_type, material, color, quantity, 
               purchase_price, selling_price, category)
               VALUES ('CUSTOM', 'Custom Item', 'N/A', 'N/A', 999999, 0, 0, 'Other')"""
        )
