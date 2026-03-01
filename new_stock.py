"""
Purchase Management Module (Manage Receiving)
"Perfect" Implementation matching reference requirements
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import config
from ui_components import AnimatedButton, PageHeader, SearchBar
from datetime import datetime
from tkcalendar import DateEntry

class NewStockModule(ctk.CTkFrame):
    """Purchase Management / Manage Receiving"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.cart = [] 
        self.mode = "RECEIVE" # RECEIVE or RETURN
        
        # Apply Base Font Size
        try:
            base_size = int(self.db.get_setting("base_font_size") or 12)
        except:
            base_size = 12
            
        self.font_sm = max(base_size - 2, 8)
        self.font_md = max(base_size - 1, 9)
        self.font_lg = base_size
        self.font_xl = max(base_size + 2, 12)
        
        # Header
        self.header = PageHeader(self, title="📦 Manage Receiving (Purchase)")
        self.header.pack(fill="x", pady=(0, config.SPACING_SM))
        
        # Main Layout: Top Form (Header + Details), Middle (Grid), Bottom (Actions)
        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True)
        
        # 1. Top Section: Party/Supplier/Agent Info
        self._setup_header_form()
        
        # 2. Middle Section: Transaction Details (Dates, Transport, etc.)
        self._setup_transaction_details()
        
        # 3. Item Entry Section
        self._setup_item_entry()
        
        # 4. Grid Section
        self._setup_grid()
        
        # 5. Footer Actions
        self._setup_footer()
        
    def _setup_header_form(self):
        """Top row: Party Name, Supplier Name, Agent Name"""
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        # Grid Layout for fields
        # Row 1: Party Name | Supplier Name | Agent Name
        # Row 2: Category | Item Name | Brand
        
        pad = config.SPACING_SM
        
        # Row 1
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=pad, pady=pad)
        cw.grid_columnconfigure(0, weight=1)
        cw.grid_columnconfigure(1, weight=1)
        cw.grid_columnconfigure(2, weight=1)
        
        # Party Name (Supplier) - This is the main one
        self.party_combo = self._create_labeled_combo(cw, "Party Name / Supplier*", 0, self._get_suppliers() + ["+ Add New"])
        self.supplier_combo = self._create_labeled_input(cw, "Supplier Name (Ref)", 1) # Optional ref
        self.agent_combo = self._create_labeled_input(cw, "Agent Name", 2)
        
        # Row 2 (Filters/Defaults for entry)
        cw2 = ctk.CTkFrame(card, fg_color="transparent")
        cw2.pack(fill="x", padx=pad, pady=(0, pad))
        cw2.grid_columnconfigure(0, weight=1)
        cw2.grid_columnconfigure(1, weight=1)
        cw2.grid_columnconfigure(2, weight=1)
        
        self.cat_filter = self._create_labeled_combo(cw2, "Category", 0, config.STOCK_CATEGORIES)
        self.brand_filter = self._create_labeled_input(cw2, "Brand", 2)
        
    def _setup_transaction_details(self):
        """Second row: Dates, Bill No, Transport, LR No"""
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        pad = config.SPACING_SM
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=pad, pady=pad)
        
        # Columns setup
        for i in range(6): cw.grid_columnconfigure(i, weight=1)
        
        # Fields
        self.grn_entry = self._create_labeled_input(cw, "GRN No (Auto)", 0)
        self.grn_entry.insert(0, "Auto")
        self.grn_entry.configure(state="readonly")
        
        self.bill_no_entry = self._create_labeled_input(cw, "Bill No*", 1)
        
        ctk.CTkLabel(cw, text="Bill Date", font=("Arial", self.font_md)).grid(row=0, column=2, sticky="w", padx=5)
        self.bill_date_entry = DateEntry(cw, width=12, background=config.COLOR_PRIMARY,
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.bill_date_entry.grid(row=1, column=2, sticky="ew", padx=5, pady=2)
        
        self.transport_entry = self._create_labeled_input(cw, "Transport", 3)
        self.lr_no_entry = self._create_labeled_input(cw, "LR No.", 4)
        
        # Mode Switch
        self.mode_switch = ctk.CTkSwitch(cw, text="Mode: Receiving", command=self._toggle_mode,
                                        progress_color=config.COLOR_SUCCESS, fg_color=config.COLOR_DANGER)
        self.mode_switch.select()
        self.mode_switch.grid(row=1, column=5, padx=5, pady=5) # Below label space

    def _setup_item_entry(self):
        """Item Entry Row"""
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        ctk.CTkLabel(card, text="Item Entry", font=("Arial", self.font_lg, "bold"), text_color="gray").pack(anchor="w", padx=10, pady=(5,0))
        
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=5, pady=5)
        
        # Fields: SKU, Barcode, Item Name, Brand, Unit, Pur Rate, Sale Rate, Qty
        fields = ["SKU (Auto)", "Barcode*", "Item Name*", "Brand", "GST %*", "Pur.Rate*", "Sale Rate*", "Qty*"]
        self.entry_vars = {}
        
        for i, f in enumerate(fields):
            cw.grid_columnconfigure(i, weight=1)
            label_text = f
            if "Barcode" in f:
                label_text = "Barcode (Scanner)*"
            
            ctk.CTkLabel(cw, text=label_text, font=("Arial", self.font_sm)).grid(row=0, column=i, sticky="w", padx=2)
            
            entry = ctk.CTkEntry(cw, height=28)
            entry.grid(row=1, column=i, sticky="ew", padx=2, pady=(0, 5))
            
            key = f.split("*")[0].split("(")[0].strip().lower().replace(" ", "_").replace(".", "_")
            self.entry_vars[key] = entry
            
            if key == "sku":
                entry.configure(state="readonly")
            
            if key == "barcode":
                entry.bind("<Return>", self._on_barcode_enter)
                entry.placeholder_text = "Scan/Enter"
                
        # Add Button
        self.add_btn = ctk.CTkButton(cw, text="⬇ Add", width=60, command=self._add_to_grid)
        self.add_btn.grid(row=1, column=len(fields), padx=5)
        
        # Auto-fill first sequenced SKU
        self._prefill_next_sku()

    def _setup_grid(self):
        """Main Data Grid"""
        # Scrollable Grid Container
        self.grid_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent", height=250)
        self.grid_frame.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        
        # Configure Treeview Style
        style = ttk.Style()
        row_height = max(int(self.font_md * 2.5), 20)
        style.theme_use('default')
        style.configure("NewStock.Treeview", background="white", foreground="black", rowheight=row_height, fieldbackground="white", font=("Arial", self.font_md), borderwidth=0)
        style.configure("NewStock.Treeview.Heading", background=config.COLOR_PRIMARY, foreground="white", font=("Arial", max(self.font_md, 12), "bold"), relief="flat")
        style.map("NewStock.Treeview.Heading", background=[('active', config.COLOR_PRIMARY_DARK)])
        style.map("NewStock.Treeview", background=[('selected', '#B4D5F0')])
        
        self.columns = ("sku", "barcode", "category", "brand", "name", "gst_pct", "pur_rate", "sale_rate", "qty", "total")
        self.tree = ttk.Treeview(self.grid_frame, columns=self.columns, show="headings", style="NewStock.Treeview", height=8)
        
        vsb = ttk.Scrollbar(self.grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("sku", "SKU", 80),
            ("barcode", "Barcode", 120),
            ("category", "Category", 100),
            ("brand", "Brand", 100),
            ("name", "Item Name", 250),
            ("gst_pct", "GST %", 60),
            ("pur_rate", "Pur.Rate", 90),
            ("sale_rate", "Sale Rate", 90),
            ("qty", "Qty", 70),
            ("total", "Total", 100)
        ]
        
        for col, text, width in headings:
            self.tree.heading(col, text=text, anchor="center" if col != "name" else "w")
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w", stretch=True if col == "name" else False)
            
        self.tree.bind("<Delete>", lambda e: self._delete_selected_item())
        self.tree.bind("<BackSpace>", lambda e: self._delete_selected_item())
        
        # Action Instruction
        ctk.CTkLabel(self.content_scroll, text="Tip: Select an row and press Delete or Backspace to remove it", font=("Arial", self.font_sm), text_color="gray").pack(anchor="e", padx=20)
        
    def _setup_footer(self):
        """Footer Actions"""
        footer = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD, height=60)
        footer.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        
        left_footer = ctk.CTkFrame(footer, fg_color="transparent")
        left_footer.pack(side="left", padx=10, fill="y")
        
        ctk.CTkLabel(left_footer, text="GST (₹):", font=("Arial", self.font_md)).pack(side="left", padx=5)
        self.gst_entry = ctk.CTkEntry(left_footer, width=80, height=28)
        self.gst_entry.insert(0, "0.00")
        self.gst_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(left_footer, text="Other Expenses (₹):", font=("Arial", self.font_md)).pack(side="left", padx=(15, 5))
        self.expenses_entry = ctk.CTkEntry(left_footer, width=80, height=28)
        self.expenses_entry.insert(0, "0.00")
        self.expenses_entry.pack(side="left", padx=5)
        
        # Totals
        self.total_label = ctk.CTkLabel(footer, text="Total Qty: 0 | Total Amount: ₹0.00", 
                                       font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY)
        self.total_label.pack(side="left", padx=20)
        
        # Buttons
        ctk.CTkButton(footer, text="Esc Close", fg_color="transparent", border_width=1, 
                     text_color="gray", width=80, command=lambda: self.destroy()).pack(side="right", padx=10)
                     
        self.save_btn = AnimatedButton(footer, text="💾 Save Purchase [F10]", command=self._save_purchase, 
                                      fg_color=config.COLOR_SUCCESS, width=150)
        self.save_btn.pack(side="right", padx=10)
        
        # Bind F10 for Save Purchase globally while this frame exists
        self.after(100, lambda: self.winfo_toplevel().bind("<F10>", lambda e: self._save_purchase()))
        self.bind("<Destroy>", lambda e: self.winfo_toplevel().unbind("<F10>"))

    # --- Helpers ---
    def _create_labeled_input(self, parent, label, col):
        ctk.CTkLabel(parent, text=label, font=("Arial", self.font_md)).grid(row=0, column=col, sticky="w", padx=5)
        entry = ctk.CTkEntry(parent, height=28)
        entry.grid(row=1, column=col, sticky="ew", padx=5, pady=2)
        return entry
        
    def _create_labeled_combo(self, parent, label, col, values):
        ctk.CTkLabel(parent, text=label, font=("Arial", self.font_md)).grid(row=0, column=col, sticky="w", padx=5)
        entry = ctk.CTkComboBox(parent, height=28, values=values)
        entry.grid(row=1, column=col, sticky="ew", padx=5, pady=2)
        return entry
        
    def _get_suppliers(self):
        try:
            res = self.db.execute_query("SELECT name FROM suppliers ORDER BY name")
            return [r[0] for r in res] if res else []
        except: return []

    def _toggle_mode(self):
        if self.mode_switch.get():
            self.mode = "RECEIVE"
            self.mode_switch.configure(text="Mode: Receiving", progress_color=config.COLOR_SUCCESS)
            self.add_btn.configure(fg_color=config.COLOR_PRIMARY)
        else:
            self.mode = "RETURN"
            self.mode_switch.configure(text="Mode: Return/Exchange", progress_color=config.COLOR_DANGER)
            self.add_btn.configure(fg_color=config.COLOR_DANGER)

    def _get_next_sku(self):
        """Find highest numerical SKU in DB and Cart to auto-suggest next (starting from 1)"""
        cursor = self.db.execute_query("SELECT sku_code FROM inventory")
        max_num = 0 # Default starting series from 1
        if cursor:
            for row in cursor:
                try:
                    num = int(row[0])
                    if num > max_num: max_num = num
                except ValueError:
                    pass
                    
        for item in self.cart:
            try:
                num = int(item['sku'])
                if num > max_num: max_num = num
            except ValueError:
                pass
                
        return str(max_num + 1)
        
    def _prefill_next_sku(self):
        """Generate and insert next sequential SKU"""
        if 'sku' in self.entry_vars:
            self.entry_vars['sku'].configure(state="normal")
            self.entry_vars['sku'].delete(0, "end")
            self.entry_vars['sku'].insert(0, self._get_next_sku())
            self.entry_vars['sku'].configure(state="readonly")

    def _on_barcode_enter(self, event):
        barcode = self.entry_vars['barcode'].get().strip()
        if not barcode: return
        
        sku = self.entry_vars['sku'].get().strip()
        
        # Check if already in cart
        for item in self.cart:
            if item['barcode'] == barcode:
                messagebox.showwarning("Already Available", f"Barcode {barcode} is already in the cart!")
                return
        
        res = self.db.execute_query("""
            SELECT saree_type, purchase_price, selling_price, brand, gst_percentage 
            FROM inventory WHERE barcode = ?
        """, (barcode,))
        
        if res:
            name, pur, sale, brand, gst_pct = res[0]
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            self.entry_vars['pur_rate'].delete(0, "end"); self.entry_vars['pur_rate'].insert(0, str(pur))
            self.entry_vars['sale_rate'].delete(0, "end"); self.entry_vars['sale_rate'].insert(0, str(sale))
            if brand: 
                self.entry_vars['brand'].delete(0, "end"); self.entry_vars['brand'].insert(0, brand)
            if gst_pct is not None:
                self.entry_vars['gst_%'].delete(0, "end"); self.entry_vars['gst_%'].insert(0, str(gst_pct))
            
            self.entry_vars['qty'].focus_set()
        else:
            self.entry_vars['item_name'].focus_set()

    def _add_to_grid(self):
        try:
            sku = self.entry_vars['sku'].get().strip()
            barcode = self.entry_vars['barcode'].get().strip()
            name = self.entry_vars['item_name'].get().strip()
            qty = int(self.entry_vars['qty'].get() or 0)
            rate = float(self.entry_vars['pur_rate'].get() or 0)
            sale = float(self.entry_vars['sale_rate'].get() or 0)
            brand = self.entry_vars['brand'].get().strip()
            try:
                gst_pct = float(self.entry_vars['gst_%'].get() or 0)
            except ValueError:
                gst_pct = 0.0
            
            if not barcode or not name or qty <= 0:
                messagebox.showerror("Error", "Barcode, Name and Qty required")
                return
            
            # Prevent duplicate barcode in database
            if self.mode == "RECEIVE":
                existing = self.db.execute_query("SELECT 1 FROM inventory WHERE barcode = ?", (barcode,))
                if existing:
                    messagebox.showwarning("Already Available", f"Barcode '{barcode}' is already available in the system!")
                    return
                # Check duplicate in cart
                for item in self.cart:
                    if item['barcode'] == barcode:
                        messagebox.showwarning("Already Available", f"Barcode '{barcode}' is already in the cart!")
                        return
            
            base_total = qty * rate
            total = base_total * (1 + (gst_pct / 100))
            
            item = {
                "sku": sku, "barcode": barcode, "name": name, "brand": brand, "gst_pct": gst_pct,
                "qty": qty, "rate": rate, "sale": sale, "total": total,
                "mode": self.mode, "category": self.cat_filter.get()
            }
            self.cart.append(item)
            self._refresh_grid()
            
            # Clear critical fields and pre-fill next expected SKU
            self.entry_vars['barcode'].delete(0, "end")
            self.entry_vars['item_name'].delete(0, "end")
            self.entry_vars['qty'].delete(0, "end")
            if 'gst_%' in self.entry_vars:
                self.entry_vars['gst_%'].delete(0, "end")
            self._prefill_next_sku()
            self.entry_vars['barcode'].focus_set()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers")

    def _refresh_grid(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        ttl_qty = 0
        ttl_amt = 0
        
        for idx, item in enumerate(self.cart):
            q_val = item['qty'] if item['mode'] == 'RECEIVE' else -item['qty']
            t_val = item['total'] if item['mode'] == 'RECEIVE' else -item['total']
            
            ttl_qty += q_val
            ttl_amt += t_val
            
            vals = (item['sku'], item['barcode'], item['category'], item['brand'], item['name'], f"{item['gst_pct']}%", 
                    f"{item['rate']:.2f}", f"{item['sale']:.2f}", str(q_val), f"{t_val:.2f}")
            
            tags = ('return',) if item['mode'] == 'RETURN' else ()
            self.tree.insert("", "end", values=vals, tags=tags)
            
        self.tree.tag_configure('return', background="#fee2e2")
        
        self.total_label.configure(text=f"Total Qty: {ttl_qty} | Total Amount: ₹{ttl_amt:,.2f}")

    def _delete_selected_item(self):
        sel = self.tree.selection()
        if not sel: return
        
        idx = self.tree.index(sel[0])
        self.cart.pop(idx)
        self._refresh_grid()

    def _save_purchase(self):
        if not self.cart: return
        
        party = self.party_combo.get()
        if not party or party == "+ Add New":
            messagebox.showerror("Error", "Select Party/Supplier")
            return
            
        bill_no = self.bill_no_entry.get()
        if not bill_no:
            messagebox.showerror("Error", "Bill No Required")
            return
            
        # Use a single connection for the entire transaction to prevent locking
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # 1. Supplier
            res = self.db.execute_query("SELECT supplier_id FROM suppliers WHERE name=?", (party,), cursor=cursor)
            if res: sup_id = res[0][0]
            else: sup_id = self.db.execute_insert("INSERT INTO suppliers (name) VALUES (?)", (party,), cursor=cursor)
            
            # 2. Purchase Master
            net_amt = sum(i['total'] if i['mode'] == 'RECEIVE' else -i['total'] for i in self.cart)
            
            try:
                gst_val = float(self.gst_entry.get() or 0)
                exp_val = float(self.expenses_entry.get() or 0)
            except ValueError:
                gst_val, exp_val = 0.0, 0.0
                
            net_amt = net_amt + gst_val + exp_val
            
            # Convert bill_date from dd/mm/yyyy → yyyy-mm-dd for DB storage
            raw_date = self.bill_date_entry.get().strip()
            try:
                dp = raw_date.split("/")
                db_bill_date = f"{dp[2]}-{dp[1]}-{dp[0]}" if len(dp) == 3 else raw_date
            except:
                db_bill_date = raw_date

            pid = self.db.execute_insert(
                """INSERT INTO purchases (supplier_id, invoice_number, total_amount, 
                   gst_amount, other_expenses, agent_name, transport, lr_no, bill_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sup_id, bill_no, net_amt, gst_val, exp_val, self.agent_combo.get(), 
                 self.transport_entry.get(), self.lr_no_entry.get(), db_bill_date),
                 cursor=cursor
            )
            
            # 3. Items
            for item in self.cart:
                # Inventory Update
                res = self.db.execute_query("SELECT item_id FROM inventory WHERE barcode=?", (item['barcode'],), cursor=cursor)
                if res:
                    iid = res[0][0]
                    self.db.execute_query(
                        """UPDATE inventory SET saree_type=?, purchase_price=?, selling_price=?, 
                           brand=?, gst_percentage=?, category=?, supplier_name=?, sku_code=? WHERE item_id=?""",
                        (item['name'], item['rate'], item['sale'], item['brand'], item['gst_pct'], 
                         item['category'], party, item['sku'], iid),
                        cursor=cursor
                    )
                else:
                    # Fix: Add defaults for material, color, design to avoid NOT NULL constraint errors
                    iid = self.db.execute_insert(
                        """INSERT INTO inventory (sku_code, barcode, saree_type, quantity, purchase_price, 
                           selling_price, brand, gst_percentage, category, supplier_name,
                           material, color, design)
                           VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (item['sku'], item['barcode'], item['name'], item['rate'], item['sale'], 
                         item['brand'], item['gst_pct'], item['category'], party,
                         "N/A", "N/A", "N/A"), # Defaults
                        cursor=cursor
                    )
                
                # Qty Update
                qty_change = item['qty'] if item['mode'] == 'RECEIVE' else -item['qty']
                if item['mode'] == 'RECEIVE':
                    self.db.execute_query("UPDATE inventory SET quantity = quantity + ? WHERE item_id=?", (qty_change, iid), cursor=cursor)
                else:
                    self.db.execute_query("UPDATE inventory SET quantity = quantity - ? WHERE item_id=?", (item['qty'], iid), cursor=cursor)
                
                # Purchase Item Record
                self.db.execute_insert(
                    """INSERT INTO purchase_items (purchase_id, item_id, sku_code, item_name, 
                       quantity, purchase_rate, sale_rate, total_amount, brand, gst_percentage)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (pid, iid, item['sku'], item['name'], item['qty'], item['rate'], 
                     item['sale'], item['total'], item['brand'], item['gst_pct']),
                    cursor=cursor
                )
                
                # History
                note = f"Ref: {bill_no} ({'GRN' if item['mode']=='RECEIVE' else 'RET'})"
                self.db.add_stock_entry(iid, qty_change, item['rate'], party, note, cursor=cursor)
            
            conn.commit() # Commit all changes only if everything succeeded
            
            messagebox.showinfo("Success", "Saved Successfully!")
            self.cart = []
            self._refresh_grid()
            self.bill_no_entry.delete(0, "end")
            
        except Exception as e:
            conn.rollback() # Rollback on error
            messagebox.showerror("Error", f"Save Failed: {e}")
        finally:
            conn.close() # Close connection
