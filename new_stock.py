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
    
    def __init__(self, parent, db_manager, purchase_invoice_generator, purchase_id=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.purchase_invoice_gen = purchase_invoice_generator
        self.cart = [] 
        self.mode = "RECEIVE" # RECEIVE or RETURN
        self.editing_purchase_id = purchase_id
        self.prefill_item_id = kwargs.get("prefill_item_id", None)
        
        # Apply Base Font Size
        try:
            self.base_size = int(self.db.get_setting("base_font_size") or 12)
        except:
            self.base_size = 12
            
        self.font_sm = max(self.base_size - 2, 8)
        self.font_md = max(self.base_size - 1, 9)
        self.font_lg = self.base_size
        self.font_xl = max(self.base_size + 2, 12)
        
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
        
        if self.editing_purchase_id:
            self.after(100, self._load_purchase_for_editing)
        elif self.prefill_item_id:
            self.after(200, self._prefill_from_item_id)
            
    def _prefill_from_item_id(self):
        try:
            res = self.db.execute_query(
                "SELECT barcode FROM inventory WHERE item_id = ?",
                (self.prefill_item_id,)
            )
            if res and res[0][0]:
                self.entry_vars['barcode'].delete(0, 'end')
                self.entry_vars['barcode'].insert(0, res[0][0])
                self._on_barcode_enter(None) # Simulate pressing enter
        except Exception as e:
            print("Prefill error:", e)
            
    def _load_purchase_for_editing(self):
        try:
            p_data = self.db.execute_query(
                "SELECT supplier_id, invoice_number, total_amount, gst_amount, other_expenses, agent_name, transport, lr_no, bill_date FROM purchases WHERE purchase_id = ?",
                (self.editing_purchase_id,)
            )
            if not p_data: return
            s_id, inv_no, t_amt, gst_amt, exp, agent, transp, lr, b_date = p_data[0]
            
            s_name_res = self.db.execute_query("SELECT name FROM suppliers WHERE supplier_id = ?", (s_id,))
            if s_name_res: self.party_combo.set(s_name_res[0][0])
            
            self.bill_no_entry.delete(0, 'end'); self.bill_no_entry.insert(0, inv_no)
            if b_date:
                try: self.bill_date_entry.set_date(datetime.strptime(b_date[:10], '%Y-%m-%d'))
                except: pass
            
            self.gst_entry.delete(0, 'end'); self.gst_entry.insert(0, str(gst_amt))
            self.expenses_entry.delete(0, 'end'); self.expenses_entry.insert(0, str(exp))
            if agent: self.agent_combo.set(agent)
            if transp: self.transport_entry.delete(0, 'end'); self.transport_entry.insert(0, transp)
            if lr: self.lr_no_entry.delete(0, 'end'); self.lr_no_entry.insert(0, lr)
            
            self.save_btn.configure(text="💾 Update Purchase [F10]", fg_color=config.COLOR_WARNING)
            
            try:
                items = self.db.execute_query(
                    "SELECT item_id, sku_code, item_name, quantity, purchase_rate, sale_rate, total_amount, brand, gst_percentage, hsn_code FROM purchase_items WHERE purchase_id = ?",
                    (self.editing_purchase_id,)
                )
            except:
                items = self.db.execute_query(
                    "SELECT item_id, sku_code, item_name, quantity, purchase_rate, sale_rate, total_amount, brand, gst_percentage, '' as hsn_code FROM purchase_items WHERE purchase_id = ?",
                    (self.editing_purchase_id,)
                )
            
            for it in items:
                i_id, sku, name, qty, p_rate, s_rate, t_amt, brand, gst_pct, hsn = it
                barcode = ""
                inv_res = self.db.execute_query("SELECT barcode, category FROM inventory WHERE item_id = ?", (i_id,))
                cat = "Saree"
                if inv_res: 
                    barcode = inv_res[0][0]
                    cat = inv_res[0][1]
                    
                self.cart.append({
                    "sku": sku, "barcode": barcode, "name": name, "hsn_code": hsn or "", "brand": brand, "gst_pct": gst_pct or 0,
                    "qty": qty, "pur_rate": p_rate, "pur_rate_w_gst": t_amt / qty if qty > 0 else p_rate,
                    "sale_rate": s_rate, "total": t_amt, 
                    "gst_amount": t_amt - (qty * p_rate), "mode": "RECEIVE", "category": cat
                })
            self._refresh_grid()
        except Exception as e:
            print("Error loading purchase items:", e)
        
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
        
        # Fields: SKU, Barcode, Item Name, HSN, Brand, Pur Rate, GST, Sale Rate, Qty
        fields = ["SKU (Auto)", "Barcode*", "Item Name*", "HSN*", "Brand", "Pur.Rate*", "GST %*", "Sale Rate*", "Qty*"]
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
        row_height = max(int(self.base_size * 2.5), 20)
        style.theme_use('default')
        style.configure("NewStock.Treeview", background="white", foreground="black", rowheight=row_height, fieldbackground="white", font=("Arial", self.base_size), borderwidth=0)
        style.configure("NewStock.Treeview.Heading", background=config.COLOR_PRIMARY, foreground="white", font=("Arial", self.base_size, "bold"), relief="flat")
        style.map("NewStock.Treeview.Heading", background=[('active', config.COLOR_PRIMARY_DARK)])
        style.map("NewStock.Treeview", background=[('selected', '#B4D5F0')])
        
        self.columns = ("sku", "barcode", "category", "hsn", "brand", "name", "pur_rate", "gst_pct", "pur_rate_gst", "sale_rate", "qty", "total")
        self.tree = ttk.Treeview(self.grid_frame, columns=self.columns, show="headings", style="NewStock.Treeview", height=8)
        
        vsb = ttk.Scrollbar(self.grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("sku", "SKU", 60),
            ("barcode", "Barcode", 100),
            ("category", "Category", 80),
            ("hsn", "HSN", 70),
            ("brand", "Brand", 90),
            ("name", "Item Name", 230),
            ("pur_rate", "Pur.Rate", 80),
            ("gst_pct", "GST %", 60),
            ("pur_rate_gst", "Rate(w/GST)", 90),
            ("sale_rate", "Sale Rate", 80),
            ("qty", "Qty", 60),
            ("total", "Total", 90)
        ]
        
        for col, text, width in headings:
            self.tree.heading(col, text=text, anchor="center" if col != "name" else "w")
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w", stretch=True if col == "name" else False)
            
        self.tree.bind("<Delete>", lambda e: self._delete_selected_item())
        self.tree.bind("<BackSpace>", lambda e: self._delete_selected_item())
        self.tree.bind("<Double-1>", self._on_grid_double_click)
        
        # Action Instruction
        ctk.CTkLabel(self.content_scroll, text="Tip: Double-click a cell to quick-edit. Press Delete or Backspace to remove row.", font=("Arial", self.font_sm), text_color="gray").pack(anchor="e", padx=20)
        
    def _on_grid_double_click(self, event):
        """Runtime Editable Cell in New Stock Grid"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        
        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id: return
        
        col_idx = int(column[1:]) - 1
        col_name = self.columns[col_idx]
        
        editable_cols = {
            "name": "name", "category": "category", "brand": "brand",
            "qty": "qty", "pur_rate": "pur_rate", "sale_rate": "sale_rate", 
            "gst_pct": "gst_pct", "hsn": "hsn_code"
        }
        if col_name not in editable_cols: return
        
        row_index = self.tree.index(row_id)
        item = self.cart[row_index]
        
        x, y, w, h = self.tree.bbox(row_id, column)
        import tkinter.ttk as ttk
        edit_entry = ttk.Entry(self.tree, font=("Arial", self.base_size))
        edit_entry.place(x=x, y=y, width=w, height=h)
        
        current_val = item.get(editable_cols[col_name], "")
        if col_name == "qty":
            current_val = int(current_val)
        edit_entry.insert(0, str(current_val))
        edit_entry.focus_set()
        edit_entry.select_range(0, 'end')
        
        def save_edit(event=None):
            val = edit_entry.get().strip()
            try:
                field = editable_cols[col_name]
                if field in ("hsn_code", "name", "category", "brand"):
                    item[field] = val
                else:
                    item[field] = float(val) if val else 0.0
                    
                # Recalculate totals inline
                if field in ("pur_rate", "gst_pct", "qty"):
                    rate = item.get("pur_rate", 0.0)
                    qty = item.get("qty", 1)
                    gst_pct = item.get("gst_pct", 0.0)
                    gst_amt_per = rate * (gst_pct / 100)
                    pur_w_gst = rate + gst_amt_per
                    item["pur_rate_w_gst"] = pur_w_gst
                    item["total"] = pur_w_gst * qty
                    item["gst_amount"] = gst_amt_per * qty
                    
                self._refresh_grid()
            except ValueError:
                pass
            edit_entry.destroy()
            
        edit_entry.bind("<Return>", save_edit)
        edit_entry.bind("<FocusOut>", save_edit)
        edit_entry.bind("<Escape>", lambda e: edit_entry.destroy())
        
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
        self.total_label = ctk.CTkLabel(footer, text="Total Items 0 Total Qty 0", 
                                       font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY)
        self.total_label.pack(side="left", padx=20)
        self.total_amount_label = ctk.CTkLabel(footer, text="Total Amount: ₹0.00", 
                                       font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY)
        self.total_amount_label.pack(side="left", padx=20)
        
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
        
        try:
            res = self.db.execute_query("""
                SELECT saree_type, hsn_code, purchase_price, selling_price, brand, gst_percentage 
                FROM inventory WHERE barcode = ?
            """, (barcode,))
        except:
            res = self.db.execute_query("""
                SELECT saree_type, '' as hsn_code, purchase_price, selling_price, brand, gst_percentage 
                FROM inventory WHERE barcode = ?
            """, (barcode,))
            
        if res:
            name, hsn, pur, sale, brand, gst_pct = res[0]
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            if hsn: self.entry_vars['hsn'].delete(0, "end"); self.entry_vars['hsn'].insert(0, hsn)
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
            hsn = self.entry_vars['hsn'].get().strip()
            try:
                gst_pct = float(self.entry_vars['gst_%'].get() or 0)
            except ValueError:
                gst_pct = 0.0
            
            if not barcode or not name or qty <= 0:
                messagebox.showerror("Error", "Barcode, Name and Qty required")
                return
                
            if gst_pct > 0 and not hsn:
                messagebox.showerror("Validation Error", "HSN Code is required when GST > 0%")
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
            
            # Smart GST Calculation exactly like Billing
            gst_amount_per_unit = rate * (gst_pct / 100)
            pur_rate_w_gst = rate + gst_amount_per_unit
            
            total = pur_rate_w_gst * qty
            total_gst_for_row = gst_amount_per_unit * qty
            
            item = {
                "sku": sku, "barcode": barcode, "name": name, "hsn_code": hsn, "brand": brand, "gst_pct": gst_pct,
                "qty": qty, "pur_rate": rate, "pur_rate_w_gst": pur_rate_w_gst, "sale_rate": sale, 
                "total": total, "gst_amount": total_gst_for_row,
                "mode": self.mode, "category": self.cat_filter.get()
            }
            self.cart.append(item)
            self._refresh_grid()
            
            # Clear critical fields and pre-fill next expected SKU
            # We DONT clear GST and HSN here so it retains values for consecutive entries
            self.entry_vars['barcode'].delete(0, "end")
            self.entry_vars['item_name'].delete(0, "end")
            self.entry_vars['qty'].delete(0, "end")
            self.entry_vars['pur_rate'].delete(0, "end")
            self.entry_vars['sale_rate'].delete(0, "end")
            self.entry_vars['brand'].delete(0, "end")
            self._prefill_next_sku()
            self.entry_vars['barcode'].focus_set()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers")

    def _refresh_grid(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        ttl_qty = 0
        ttl_amt = 0
        ttl_gst = 0
        
        for idx, item in enumerate(self.cart):
            q_val = item['qty'] if item['mode'] == 'RECEIVE' else -item['qty']
            t_val = item['total'] if item['mode'] == 'RECEIVE' else -item['total']
            g_val = item['gst_amount'] if item.get('mode', 'RECEIVE') == 'RECEIVE' else -item['gst_amount']
            
            ttl_qty += q_val
            ttl_amt += t_val
            ttl_gst += g_val
            
            # Fallback for old items loaded without pur_rate_w_gst
            pur_w_gst = item.get('pur_rate_w_gst', item['pur_rate'] + (item['pur_rate'] * item['gst_pct'] / 100))
            
            vals = (item['sku'], item['barcode'], item['category'], item.get('hsn_code', ''), item['brand'], item['name'], 
                    f"{item['pur_rate']:.2f}", f"{item['gst_pct']}%", f"{pur_w_gst:.2f}", 
                    f"{item['sale_rate']:.2f}", str(q_val), f"{t_val:.2f}")
            
            
            tags = ('return',) if item['mode'] == 'RETURN' else ()
            self.tree.insert("", "end", values=vals, tags=tags)
            
        self.tree.tag_configure('return', background="#fee2e2")
        
        total_items_count = len(self.cart)
        self.total_label.configure(text=f"Total Items {total_items_count} Total Qty {int(ttl_qty)}")
        self.total_amount_label.configure(text=f"Total Amount: ₹{ttl_amt:,.2f}")
        
        # Auto-update GST Footer
        self.gst_entry.delete(0, "end")
        self.gst_entry.insert(0, f"{ttl_gst:.2f}")

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

            if hasattr(self, 'editing_purchase_id') and self.editing_purchase_id:
                pid = self.editing_purchase_id
                
                # Revert old inventory
                old_items = self.db.execute_query("SELECT item_id, quantity FROM purchase_items WHERE purchase_id = ?", (pid,), cursor=cursor)
                if old_items:
                    for item_id, qty in old_items:
                        self.db.execute_query("UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?", (qty, item_id), cursor=cursor)
                
                # Delete old items
                self.db.execute_query("DELETE FROM purchase_items WHERE purchase_id = ?", (pid,), cursor=cursor)
                
                self.db.execute_query(
                    """UPDATE purchases SET supplier_id=?, invoice_number=?, total_amount=?, 
                       gst_amount=?, other_expenses=?, agent_name=?, transport=?, lr_no=?, bill_date=? 
                       WHERE purchase_id=?""",
                    (sup_id, bill_no, net_amt, gst_val, exp_val, self.agent_combo.get(), 
                     self.transport_entry.get(), self.lr_no_entry.get(), db_bill_date, pid),
                     cursor=cursor
                )
            else:
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
                           brand=?, gst_percentage=?, hsn_code=?, category=?, supplier_name=?, sku_code=? WHERE item_id=?""",
                        (item['name'], item['pur_rate'], item['sale_rate'], item['brand'], item['gst_pct'], 
                         item.get('hsn_code', ''), item['category'], party, item['sku'], iid),
                        cursor=cursor
                    )
                else:
                    # Fix: Add defaults for material, color, design to avoid NOT NULL constraint errors
                    iid = self.db.execute_insert(
                        """INSERT INTO inventory (sku_code, barcode, saree_type, quantity, purchase_price, 
                           selling_price, brand, gst_percentage, category, supplier_name,
                           hsn_code, material, color, design)
                           VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (item['sku'], item['barcode'], item['name'], item['pur_rate'], item['sale_rate'], 
                         item['brand'], item['gst_pct'], item['category'], party, item.get('hsn_code', ''),
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
                       quantity, purchase_rate, sale_rate, total_amount, brand, gst_percentage, hsn_code)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (pid, iid, item['sku'], item['name'], item['qty'], item['pur_rate'], 
                     item['sale_rate'], item['total'], item['brand'], item['gst_pct'], item.get('hsn_code', '')),
                    cursor=cursor
                )
                
                # History
                note = f"Ref: {bill_no} ({'GRN' if item['mode']=='RECEIVE' else 'RET'})"
                self.db.add_stock_entry(iid, qty_change, item['pur_rate'], party, note, cursor=cursor)
            
            conn.commit() # Commit all changes only if everything succeeded
            
            # Generate purchase invoice
            try:
                invoice_path = self.purchase_invoice_gen.generate_purchase_invoice(pid)
                invoice_generated = True
            except Exception as pdf_error:
                invoice_generated = False
                invoice_path = None
                print("PDF Error:", pdf_error)

            if invoice_generated:
                if messagebox.askyesno("Success", "Saved Successfully!\n\nWould you like to print the purchase invoice?"):
                    try:
                        import os
                        os.startfile(invoice_path)
                    except:
                        try:
                            import subprocess
                            subprocess.Popen(['start', '', invoice_path], shell=True)
                        except: pass
            else:
                messagebox.showinfo("Success", "Saved Successfully!")
            
            self.cart = []
            self._refresh_grid()
            self.bill_no_entry.delete(0, "end")
            
        except Exception as e:
            conn.rollback() # Rollback on error
            messagebox.showerror("Error", f"Save Failed: {e}")
        finally:
            conn.close() # Close connection
