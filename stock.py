"""
Stock Management Module
View, edit, and manage inventory with premium light theme
"""

import customtkinter as ctk
from tkinter import messagebox
import config
from ui_components import AnimatedButton, SearchBar, PageHeader


class StockManagementModule(ctk.CTkFrame):
    """Stock management interface"""
    
    def __init__(self, parent, db_manager, on_add_stock=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.on_add_stock = on_add_stock
        
        # Header
        PageHeader(self, title="📦 Stock Management").pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Search bar
        search_bar = SearchBar(
            self,
            placeholder="Search by SKU, Type, Color, Material...",
            on_search=self._on_search
        )
        search_bar.pack(fill="x", pady=(0, config.SPACING_LG))
        self.search_entry = search_bar.entry
        
        # Action Buttons
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, config.SPACING_SM))
        
        ctk.CTkButton(self.action_frame, text="✎ Edit Item", fg_color=config.COLOR_INFO, command=self._edit_selected).pack(side="left", padx=5)
        ctk.CTkButton(self.action_frame, text="🕒 View History / Add Stock", fg_color=config.COLOR_WARNING, command=self._history_selected).pack(side="left", padx=5)
        ctk.CTkButton(self.action_frame, text="🗑 Delete Item", fg_color=config.COLOR_DANGER, command=self._delete_selected).pack(side="left", padx=5)
        
        # Stock table (Treeview)
        from tkinter import ttk
        tree_container = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#CCC", corner_radius=0)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        
        # Apply Base Font Size
        try:
            base_size = int(self.db.get_setting("base_font_size") or 12)
        except:
            base_size = 12
            
        row_height = max(int(base_size * 2.5), 20)
        
        style.configure("Stock.Treeview", background="white", foreground="black", rowheight=row_height, fieldbackground="white", font=("Arial", base_size))
        style.configure("Stock.Treeview.Heading", background=config.COLOR_PRIMARY, foreground="white", font=("Arial", base_size, "bold"))
        style.map("Stock.Treeview", background=[('selected', '#B4D5F0')])

        self.columns = ("item_id", "sku", "barcode", "name", "qty", "purchase", "selling", "supplier", "date")
        self.tree = ttk.Treeview(tree_container, columns=self.columns, show="headings", style="Stock.Treeview")
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("item_id", "ID", 0),
            ("sku", "SKU", 100),
            ("barcode", "Barcode", 130),
            ("name", "Item Name", 200),
            ("qty", "Qty", 80),
            ("purchase", "Purchase ₹", 100),
            ("selling", "Selling ₹", 100),
            ("supplier", "Supplier", 150),
            ("date", "Date", 120)
        ]
        
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col not in ("name", "supplier") else "w")
            
        self.tree.column("item_id", width=0, stretch=False) # Hide ID

        self.tree.bind("<Double-1>", lambda e: self._edit_selected())
        
        # Tags for row colors
        self.tree.tag_configure('low_stock', background="#FEF3C7")
        self.tree.tag_configure('normal_even', background="#F9FAFB")
        self.tree.tag_configure('normal_odd', background="white")
        
        self._load_stock()
    
    def _on_search(self, query):
        """Handle search"""
        self._load_stock(query)
    
    def _load_stock(self, search_query=""):
        """Load stock data"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Get stock data
        query = """SELECT item_id, sku_code, barcode, saree_type, material, color, quantity,
                   purchase_price, selling_price, supplier_name, added_date
                   FROM inventory"""
        params = []
        
        if search_query:
            query += " WHERE sku_code LIKE ? OR barcode LIKE ? OR saree_type LIKE ? OR supplier_name LIKE ?"
            params = [f"%{search_query}%"] * 4
            
        query += " ORDER BY added_date DESC"
        
        items = self.db.execute_query(query, tuple(params))
        
        for idx, item in enumerate(items):
            item_id = item[0]
            sku = item[1]
            barcode = item[2] or ""
            name = item[3][:50]
            qty = item[6]
            purchase = f"₹{item[7]:.0f}"
            selling = f"₹{item[8]:.0f}"
            supplier = (item[9] or "N/A")[:30]
            date_str = item[10][:10] if item[10] else "N/A"
            
            tags = ()
            if qty <= config.LOW_STOCK_THRESHOLD:
                tags = ('low_stock',)
            else:
                tags = ('normal_even' if idx % 2 == 0 else 'normal_odd',)
                
            self.tree.insert("", "end", values=(item_id, sku, barcode, name, qty, purchase, selling, supplier, date_str), tags=tags)
            
    def _get_selected_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an item from the list first.")
            return None
        return self.tree.item(sel[0])['values'][0] # item_id

    def _edit_selected(self):
        """Redirect to New Stock — open the last purchase that included this item for editing.
        If no purchase record exists, open New Stock pre-filled with this item barcode."""
        item_id = self._get_selected_item()
        if not item_id:
            return
        if not self.on_add_stock:
            messagebox.showerror("Error", "Redirection to New Stock failed.")
            return
        # Find the latest purchase that contained this item
        res = self.db.execute_query(
            """SELECT pi.purchase_id FROM purchase_items pi
               WHERE pi.item_id = ?
               ORDER BY pi.purchase_item_id DESC LIMIT 1""",
            (item_id,)
        )
        if res and res[0][0]:
            # Open that purchase in New Stock for editing
            self.on_add_stock(item_id=item_id, purchase_id=res[0][0])
        else:
            # No purchase record — open New Stock pre-filled with barcode
            self.on_add_stock(item_id=item_id, purchase_id=None)

    def _history_selected(self):
        item_id = self._get_selected_item()
        if item_id:
            self._view_history(item_id)

    def _delete_selected(self):
        item_id = self._get_selected_item()
        if item_id:
            self._delete_item(item_id)

    def _view_history(self, item_id):
        """View and manage purchase history for an item"""
        # Get item details
        item = self.db.execute_query("SELECT * FROM inventory WHERE item_id = ?", (item_id,))[0]
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Stock History - {item[1]}")
        dialog.geometry("900x600")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            header,
            text=f"Stock History: {item[1]} ({item[2]})",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        # Add Entry Button
        def _route_to_new_stock():
            dialog.destroy()
            if self.on_add_stock:
                self.on_add_stock(item_id)
                
        ctk.CTkButton(
            header,
            text="+ Add Stock via Purchase",
            fg_color=config.COLOR_SUCCESS,
            command=_route_to_new_stock
        ).pack(side="right")
        
        # History Table Container
        tree_container = ctk.CTkFrame(dialog, fg_color="white", border_width=1, border_color="#CCC", corner_radius=0)
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        from tkinter import ttk
        style = ttk.Style()
        style.theme_use("default")
        
        columns = ("entry_id", "date", "qty", "price", "supplier", "note")
        self.history_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=vsb.set)
        self.history_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("date", "Date", 150),
            ("qty", "Qty Added", 100),
            ("price", "Price", 100),
            ("supplier", "Supplier", 150),
            ("note", "Note", 200)
        ]
        
        self.history_tree.heading("entry_id", text="ID")
        self.history_tree.column("entry_id", width=0, stretch=False)
        
        for col, text, width in headings:
            self.history_tree.heading(col, text=text)
            self.history_tree.column(col, width=width, anchor="center" if col in ("qty", "price") else "w")

        def load_history():
            for row in self.history_tree.get_children():
                self.history_tree.delete(row)
                
            entries = self.db.execute_query(
                "SELECT entry_id, date_added, quantity_added, purchase_price, supplier_name, admin_note FROM stock_entries WHERE item_id = ? ORDER BY date_added DESC",
                (item_id,)
            )
            for entry in entries:
                date_str = entry[1][:16] if entry[1] else ""
                qty_str = f"+{entry[2]}" if entry[2] > 0 else str(entry[2])
                self.history_tree.insert("", "end", values=(entry[0], date_str, qty_str, f"{entry[3]:.2f}", entry[4] or "-", entry[5] or ""))

        def _on_history_double_click(event):
            region = self.history_tree.identify("region", event.x, event.y)
            if region != "cell": return
            
            column = self.history_tree.identify_column(event.x)
            row_id = self.history_tree.identify_row(event.y)
            if not row_id: return
            
            col_idx = int(column[1:]) - 1
            col_name = columns[col_idx]
            
            editable_cols = {"qty": "quantity_added", "price": "purchase_price", "supplier": "supplier_name", "note": "admin_note"}
            if col_name not in editable_cols: return
            
            db_field = editable_cols[col_name]
            
            x, y, w, h = self.history_tree.bbox(row_id, column)
            import tkinter.ttk as ttk
            edit_entry = ttk.Entry(self.history_tree, font=("Arial", 12))
            edit_entry.place(x=x, y=y, width=w, height=h)
            
            item_vals = self.history_tree.item(row_id)['values']
            entry_id = item_vals[0]
            current_val = str(item_vals[col_idx]).replace("+", "").replace("₹", "")
            edit_entry.insert(0, current_val)
            edit_entry.focus_set()
            edit_entry.select_range(0, 'end')
            
            def save_edit(e=None):
                val = edit_entry.get().strip()
                try:
                    if db_field in ("quantity_added", "purchase_price"):
                        val = float(val) if val else 0.0
                        if db_field == "quantity_added":
                            old_qty_res = self.db.execute_query("SELECT quantity_added FROM stock_entries WHERE entry_id = ?", (entry_id,))
                            if old_qty_res:
                                old_qty = old_qty_res[0][0]
                                diff = int(float(str(val))) - old_qty
                                self.db.execute_query("UPDATE inventory SET quantity = quantity + ? WHERE item_id = ?", (diff, item_id))
                        val = val if db_field == "purchase_price" else int(float(str(val)))
                    
                    self.db.execute_query(f"UPDATE stock_entries SET {db_field} = ? WHERE entry_id = ?", (val, entry_id))
                    load_history()
                    self._load_stock()
                except ValueError:
                    pass
                edit_entry.destroy()
                
            edit_entry.bind("<Return>", save_edit)
            edit_entry.bind("<FocusOut>", save_edit)
            edit_entry.bind("<Escape>", lambda e: edit_entry.destroy())

        def delete_entry():
            sel = self.history_tree.selection()
            if not sel: return
            entry_id = self.history_tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Confirm", "Delete this entry? This will reduce stock quantity."):
                self.db.delete_stock_entry(entry_id)
                load_history()
                self._load_stock()

        self.history_tree.bind("<Double-1>", _on_history_double_click)
        self.history_tree.bind("<Delete>", lambda e: delete_entry())
        self.history_tree.bind("<BackSpace>", lambda e: delete_entry())
        
        ctk.CTkLabel(dialog, text="Tip: Double-click Qty, Price, Supplier, or Note to edit quickly.", text_color="gray").pack(pady=(0, 10))
        
        load_history()



    def _delete_item(self, item_id):
        """Delete stock item"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            try:
                self.db.execute_query("DELETE FROM inventory WHERE item_id = ?", (item_id,))
                messagebox.showinfo("Success", "Item deleted successfully")
                self._load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
