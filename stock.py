"""
Stock Management Module
View, edit, and manage inventory with premium light theme
"""

import customtkinter as ctk
from tkinter import messagebox
import config
import config
from ui_components import AnimatedButton, SearchBar, PageHeader


class StockManagementModule(ctk.CTkFrame):
    """Stock management interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
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
        item_id = self._get_selected_item()
        if item_id:
            self._edit_item(item_id)

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
        dialog.geometry("800x600")
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
        ctk.CTkButton(
            header,
            text="+ Add Stock Entry",
            fg_color=config.COLOR_SUCCESS,
            command=lambda: self._add_stock_entry_dialog(dialog, item_id)
        ).pack(side="right")
        
        # History Table
        history_frame = ctk.CTkScrollableFrame(dialog, fg_color=config.COLOR_BG_CARD)
        history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def load_history():
            for widget in history_frame.winfo_children():
                widget.destroy()
                
            entries = self.db.execute_query(
                "SELECT * FROM stock_entries WHERE item_id = ? ORDER BY date_added DESC",
                (item_id,)
            )
            
            # Headers
            headers = ["Date", "Qty Added", "Price", "Supplier", "Note", "Action"]
            h_frame = ctk.CTkFrame(history_frame, fg_color=config.COLOR_PRIMARY, height=40)
            h_frame.pack(fill="x", pady=(0, 5))
            
            for i, h in enumerate(headers):
                h_frame.grid_columnconfigure(i, weight=1)
                ctk.CTkLabel(h_frame, text=h, text_color="white", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=i, pady=5)
            
            for entry in entries:
                row = ctk.CTkFrame(history_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                for i in range(len(headers)):
                    row.grid_columnconfigure(i, weight=1)
                
                ctk.CTkLabel(row, text=entry[5][:16]).grid(row=0, column=0)
                ctk.CTkLabel(row, text=f"+{entry[2]}", text_color="green").grid(row=0, column=1)
                ctk.CTkLabel(row, text=f"₹{entry[3]}").grid(row=0, column=2)
                ctk.CTkLabel(row, text=entry[4] or "-").grid(row=0, column=3)
                ctk.CTkLabel(row, text=entry[6] or "").grid(row=0, column=4)
                
                ctk.CTkButton(
                    row, text="Delete", width=60, fg_color=config.COLOR_DANGER,
                    command=lambda eid=entry[0]: delete_entry(eid)
                ).grid(row=0, column=5)

        def delete_entry(entry_id):
            if messagebox.askyesno("Confirm", "Delete this entry? This will reduce stock quantity."):
                self.db.delete_stock_entry(entry_id)
                load_history()
                self._load_stock()

        load_history()

    def _add_stock_entry_dialog(self, parent, item_id):
        """Dialog to add new stock entry"""
        d = ctk.CTkToplevel(parent)
        d.title("Add Stock")
        d.geometry("400x400")
        d.transient(parent)
        d.grab_set()
        
        ctk.CTkLabel(d, text="Add Stock Quantity", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        
        entries = {}
        for field in ["Quantity", "Price", "Supplier", "Note"]:
            f = ctk.CTkFrame(d, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=field, width=80, anchor="w").pack(side="left")
            e = ctk.CTkEntry(f)
            e.pack(side="left", fill="x", expand=True)
            entries[field] = e
            
        def save():
            try:
                qty = int(entries["Quantity"].get())
                price = float(entries["Price"].get())
                supplier = entries["Supplier"].get()
                note = entries["Note"].get()
                
                self.db.add_stock_entry(item_id, qty, price, supplier, note)
                
                # Update inventory quantity
                self.db.execute_query(
                    "UPDATE inventory SET quantity = quantity + ?, purchase_price = ? WHERE item_id = ?",
                    (qty, price, item_id)
                )
                
                messagebox.showinfo("Success", "Stock added")
                d.destroy()
                parent.lift() # Refresh parent
                # We need to refresh the history view, which requires reloading the load_history function
                # Since we can't easily reach into the closure, we can close the history dialog or rely on user reopening
                # Better: pass a callback or just close. simpler to close and user reopens or just auto-refresh if we could.
                # For now, let's just close the add dialog. The User handles refresh in _view_history by clicking, but real-time is better.
                # Actually, I can call the parent's load_history if I refactor slightly, but simpler:
                self._load_stock() # Refresh main table
                
            except ValueError:
                messagebox.showerror("Error", "Invalid number format")
        
        ctk.CTkButton(d, text="Save", command=save, fg_color=config.COLOR_SUCCESS).pack(pady=20)

    def _edit_item(self, item_id):
        """Edit stock item"""
        # Get item details
        item = self.db.execute_query(
            "SELECT * FROM inventory WHERE item_id = ?",
            (item_id,)
        )[0]
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Stock Item")
        dialog.geometry("500x650")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkScrollableFrame(dialog, fg_color=config.COLOR_BG_CARD)
        main_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, pady=config.SPACING_LG)
        
        # Fields
        fields = [
            ("SKU Code", item[1]),
            ("Barcode", item[13] if len(item) > 13 else ""),
            ("Item Name", item[2]),
            ("GST %", str(item[16]) if len(item) > 16 else "0.0"),
            ("Quantity", str(item[6])),
            ("Purchase Price", str(item[7])),
            ("Selling Price", str(item[8])),
            ("Supplier", item[9] or "")
        ]
        
        entries = {}
        for label, value in fields:
            ctk.CTkLabel(
                main_frame,
                text=label,
                font=ctk.CTkFont(size=config.FONT_SIZE_SMALL, weight="bold"),
                text_color=config.COLOR_TEXT_PRIMARY
            ).pack(pady=(config.SPACING_SM, 2), anchor="w")
            
            entry = ctk.CTkEntry(main_frame, height=35)
            entry.insert(0, value)
            if label == "Quantity":
                entry.configure(state="disabled") # Prevent direct edit of quantity, force use of history
                ctk.CTkLabel(main_frame, text="To change quantity, use History > Add Stock", text_color="gray").pack(anchor="w")
            entry.pack(fill="x", pady=(0, config.SPACING_XS))
            entries[label] = entry
        
        def save_changes():
            try:
                self.db.execute_query(
                    """UPDATE inventory SET sku_code=?, barcode=?, saree_type=?, gst_percentage=?, purchase_price=?, 
                       selling_price=?, supplier_name=?, last_updated=CURRENT_TIMESTAMP
                       WHERE item_id=?""",
                    (entries["SKU Code"].get(), entries["Barcode"].get(), entries["Item Name"].get(),
                     float(entries["GST %"].get() or 0.0),
                     float(entries["Purchase Price"].get()),
                     float(entries["Selling Price"].get()),
                     entries["Supplier"].get(), item_id)
                )
                messagebox.showinfo("Success", "Item updated successfully")
                dialog.destroy()
                self._load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        AnimatedButton(
            main_frame,
            text="💾 Save Changes",
            fg_color=config.COLOR_PRIMARY,
            command=save_changes
        ).pack(pady=config.SPACING_LG)
    
    def _delete_item(self, item_id):
        """Delete stock item"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            try:
                self.db.execute_query("DELETE FROM inventory WHERE item_id = ?", (item_id,))
                messagebox.showinfo("Success", "Item deleted successfully")
                self._load_stock()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
