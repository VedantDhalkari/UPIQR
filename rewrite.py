import os

new_content = """class BillingModule(ctk.CTkFrame):
    \"\"\"Billing and invoice creation interface (Tabular)\"\"\"
    
    def __init__(self, parent, db_manager, invoice_generator, current_user, sale_id=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.invoice_gen = invoice_generator
        self.current_user = current_user
        self.cart = []
        self.editing_sale_id = sale_id 
        
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
        title = f"Edit Bill #{sale_id}" if sale_id else "New Bill / Invoice"
        self.header = PageHeader(self, title=title)
        self.header.pack(fill="x", pady=(0, config.SPACING_SM))
        
        # Main scrollable container
        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scroll.pack(fill="both", expand=True)
        
        self._setup_header_form(sale_id)
        self._setup_item_entry()
        self._setup_grid()
        self._setup_footer(sale_id)
        
        if self.editing_sale_id:
            self.after(100, self._load_sale_for_editing)

    def _setup_header_form(self, sale_id):
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=10, pady=10)
        
        for i in range(5): cw.grid_columnconfigure(i, weight=1)
        
        self.bill_no_entry = self._create_labeled_input(cw, "Bill No (Auto)", 0)
        if not sale_id:
            self.bill_no_entry.insert(0, "Auto-Generated")
            self.bill_no_entry.configure(state="readonly")
            
        self.bill_date_entry = self._create_labeled_input(cw, "Bill Date (YYYY-MM-DD)", 1)
        self.bill_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.customer_name_entry = self._create_labeled_input(cw, "Customer Name", 2)
        self.customer_phone_entry = self._create_labeled_input(cw, "Customer Phone", 3)
        
        try:
            res = self.db.execute_query("SELECT final_amount FROM sales ORDER BY sale_id DESC LIMIT 1")
            last_amt = res[0][0] if res else 0.0
        except: last_amt = 0.0
        
        last_bill_frame = ctk.CTkFrame(cw, fg_color=config.COLOR_PRIMARY_LIGHT, corner_radius=config.RADIUS_MD)
        last_bill_frame.grid(row=0, column=4, rowspan=2, padx=10, sticky="e")
        ctk.CTkLabel(last_bill_frame, text="Last Bill Amount:", font=("Arial", self.font_sm, "bold"), text_color=config.COLOR_PRIMARY).pack(padx=10, pady=(5,0))
        self.last_bill_amount_lbl = ctk.CTkLabel(last_bill_frame, text=f"₹{last_amt:,.2f}", font=("Arial", self.font_lg, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        self.last_bill_amount_lbl.pack(padx=10, pady=(0,5))

    def _setup_item_entry(self):
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(5,0))
        ctk.CTkLabel(top_bar, text="Item Entry", font=("Arial", self.font_lg, "bold"), text_color="gray").pack(side="left")
        ctk.CTkButton(top_bar, text="🔍 Search Items", width=120, height=25, fg_color=config.COLOR_SECONDARY, command=self._open_search_dialog).pack(side="right")
        
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=5, pady=5)
        
        fields = ["Barcode/SKU", "Item Name*", "Avail Qty", "Price*", "Qty*"]
        self.entry_vars = {}
        
        for i, f in enumerate(fields):
            cw.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(cw, text=f, font=("Arial", self.font_sm)).grid(row=0, column=i, sticky="w", padx=2)
            
            entry = ctk.CTkEntry(cw, height=28)
            entry.grid(row=1, column=i, sticky="ew", padx=2, pady=(0, 5))
            
            key = f.split("*")[0].split("(")[0].replace("/", "_").replace(" ", "_").lower()
            if key == "avail_qty": entry.configure(state="readonly")
            self.entry_vars[key] = entry
            
            if "barcode" in key:
                entry.bind("<Return>", self._on_sku_enter)
                entry.placeholder_text = "Scan/Enter"
                
        self.current_item_id = None
        self.current_avail_qty = 9999
                
        self.add_btn = ctk.CTkButton(cw, text="⬇ Add", width=60, command=self._add_to_grid)
        self.add_btn.grid(row=1, column=len(fields), padx=5)

    def _setup_grid(self):
        header_frame = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_PRIMARY, height=35, corner_radius=0)
        header_frame.pack(fill="x", padx=config.SPACING_SM)
        
        headers = ["Sr. No", "SKU", "Item Name", "Price", "Qty", "Total", "Action"]
        self.col_weights = [1, 2, 4, 2, 1, 2, 1]
        
        for i, h in enumerate(headers):
            header_frame.grid_columnconfigure(i, weight=self.col_weights[i])
            ctk.CTkLabel(header_frame, text=h, font=("Arial", self.font_md, "bold"), text_color="white").grid(row=0, column=i, sticky="ew")
            
        self.grid_frame = ctk.CTkScrollableFrame(self.content_scroll, fg_color="transparent", height=250)
        self.grid_frame.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        self.grid_frame.grid_columnconfigure(0, weight=2) 
        
    def _setup_footer(self, sale_id):
        footer = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        footer.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        
        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        
        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=20, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(left, text="Subtotal: ₹0.00", font=("Arial", self.font_md), text_color="gray")
        self.subtotal_label.pack(anchor="w", pady=2)
        
        discount_frame = ctk.CTkFrame(left, fg_color="transparent")
        discount_frame.pack(anchor="w", fill="x", pady=2)
        ctk.CTkLabel(discount_frame, text="Discount %:", font=("Arial", self.font_md)).pack(side="left")
        self.discount_entry = ctk.CTkEntry(discount_frame, width=60, height=28)
        self.discount_entry.insert(0, "0")
        self.discount_entry.pack(side="left", padx=10)
        self.discount_entry.bind("<KeyRelease>", lambda e: self._update_summary())
        
        self.total_label = ctk.CTkLabel(left, text="Total: ₹0.00", font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY)
        self.total_label.pack(anchor="w", pady=10)
        
        pay_frame = ctk.CTkFrame(right, fg_color="transparent")
        pay_frame.pack(anchor="e", fill="x", pady=2)
        ctk.CTkLabel(pay_frame, text="Amount Paid (₹):", font=("Arial", self.font_md)).pack(side="left")
        self.amount_paid_entry = ctk.CTkEntry(pay_frame, width=100, height=28)
        self.amount_paid_entry.pack(side="right")
        self.amount_paid_entry.bind("<KeyRelease>", lambda e: self._update_summary())
        
        self.balance_label = ctk.CTkLabel(right, text="Balance Due: ₹0.00", font=("Arial", self.font_lg, "bold"), text_color=config.COLOR_DANGER)
        self.balance_label.pack(anchor="e", pady=10)
        
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(anchor="e", pady=10)
        
        self.whatsapp_btn = AnimatedButton(btn_frame, text="📱 WhatsApp", width=120, height=35, fg_color="#25D366", command=self._send_whatsapp)
        self.whatsapp_btn.pack(side="left", padx=5)
        
        btn_text = "💾 Update Bill" if sale_id else "💳 Complete Sale"
        btn_color = config.COLOR_WARNING if sale_id else config.COLOR_SUCCESS
        self.checkout_btn = AnimatedButton(btn_frame, text=btn_text, width=150, height=35, fg_color=btn_color, command=self._complete_sale)
        self.checkout_btn.pack(side="left", padx=5)

    def _create_labeled_input(self, parent, label, col):
        ctk.CTkLabel(parent, text=label, font=("Arial", self.font_md)).grid(row=0, column=col, sticky="w", padx=5)
        entry = ctk.CTkEntry(parent, height=28)
        entry.grid(row=1, column=col, sticky="ew", padx=5, pady=2)
        return entry

    def _on_sku_enter(self, event):
        sku = self.entry_vars['barcode_sku'].get().strip()
        if not sku: return
        
        res = self.db.execute_query("SELECT item_id, saree_type, brand, material, selling_price, quantity FROM inventory WHERE sku_code = ?", (sku,))
        if res:
            i_id, type_, brand, mat, sale, qty = res[0]
            name = f"{type_} {brand or ''} {mat or ''}".strip()
            self.current_item_id = i_id
            self.current_avail_qty = qty
            
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            self.entry_vars['price'].delete(0, "end"); self.entry_vars['price'].insert(0, str(sale))
            
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end"); self.entry_vars['avail_qty'].insert(0, str(qty))
            self.entry_vars['avail_qty'].configure(state="readonly")
            
            self.entry_vars['qty'].focus_set()
        else:
            self.current_item_id = None
            self.current_avail_qty = 9999
            self.entry_vars['item_name'].focus_set()

    def _open_search_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Search Items")
        d.geometry("600x400")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        
        search_frame = ctk.CTkFrame(d, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search SKU, Name...", width=300)
        search_entry.pack(side="left", padx=5)
        
        results_frame = ctk.CTkScrollableFrame(d, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        def search(e=None):
            q = search_entry.get().strip()
            for w in results_frame.winfo_children(): w.destroy()
            
            if not q: res = self.db.execute_query("SELECT item_id, sku_code, saree_type, brand, selling_price, quantity FROM inventory WHERE quantity > 0 LIMIT 20")
            else: res = self.db.execute_query("SELECT item_id, sku_code, saree_type, brand, selling_price, quantity FROM inventory WHERE (sku_code LIKE ? OR saree_type LIKE ?) AND quantity > 0 LIMIT 20", (f"%{q}%", f"%{q}%"))
            
            for item in res:
                row = ctk.CTkFrame(results_frame)
                row.pack(fill="x", pady=2)
                name = f"{item[2]} {item[3] or ''}"
                ctk.CTkLabel(row, text=f"{item[1]} - {name} (₹{item[4]}) [Qty: {item[5]}]").pack(side="left", padx=10)
                ctk.CTkButton(row, text="Select", width=60, command=lambda i=item, n=name: select(i, n)).pack(side="right", padx=10, pady=5)
                
        def select(item, name):
            self.entry_vars['barcode_sku'].delete(0, "end"); self.entry_vars['barcode_sku'].insert(0, item[1])
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            self.entry_vars['price'].delete(0, "end"); self.entry_vars['price'].insert(0, str(item[4]))
            
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end"); self.entry_vars['avail_qty'].insert(0, str(item[5]))
            self.entry_vars['avail_qty'].configure(state="readonly")
            
            self.current_item_id = item[0]
            self.current_avail_qty = item[5]
            self.entry_vars['qty'].focus_set()
            d.destroy()
            
        search_entry.bind("<KeyRelease>", search)
        search()

    def _add_to_grid(self):
        try:
            sku = self.entry_vars['barcode_sku'].get().strip() or "CUSTOM"
            name = self.entry_vars['item_name'].get().strip()
            price = float(self.entry_vars['price'].get() or 0)
            qty = int(self.entry_vars['qty'].get() or 0)
            
            if not name or qty <= 0:
                messagebox.showerror("Error", "Name and Qty required")
                return
                
            if self.current_item_id and qty > self.current_avail_qty:
                messagebox.showwarning("Stock Limit", f"Only {self.current_avail_qty} available.")
                return
                
            for cart_item in self.cart:
                if cart_item['sku'] == sku and sku != "CUSTOM" and cart_item['name'] == name:
                    if cart_item['quantity'] + qty > self.current_avail_qty:
                        messagebox.showwarning("Stock Limit", "Cannot exceed available quantity")
                        return
                    cart_item['quantity'] += qty
                    cart_item['total'] = cart_item['quantity'] * cart_item['price']
                    break
            else:
                self.cart.append({
                    'item_id': self.current_item_id,
                    'sku': sku,
                    'name': name,
                    'price': price,
                    'quantity': qty,
                    'total': price * qty,
                    'available_qty': self.current_avail_qty
                })
                
            self._refresh_cart()
            
            self.entry_vars['barcode_sku'].delete(0, "end")
            self.entry_vars['item_name'].delete(0, "end")
            self.entry_vars['price'].delete(0, "end")
            self.entry_vars['qty'].delete(0, "end")
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end")
            self.entry_vars['avail_qty'].configure(state="readonly")
            
            self.current_item_id = None
            self.current_avail_qty = 9999
            self.entry_vars['barcode_sku'].focus_set()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers")

    def _refresh_cart(self):
        for w in self.grid_frame.winfo_children(): w.destroy()
        
        for idx, item in enumerate(self.cart):
            row_color = "transparent" if idx % 2 == 0 else config.COLOR_BG_HOVER
            row = ctk.CTkFrame(self.grid_frame, fg_color=row_color)
            row.pack(fill="x", pady=1)
            
            for i in range(7): row.grid_columnconfigure(i, weight=self.col_weights[i])
            
            vals = [str(idx+1), item['sku'], item['name'], f"₹{item['price']:.2f}", str(item['quantity']), f"₹{item['total']:.2f}"]
            for i, v in enumerate(vals):
                ctk.CTkLabel(row, text=v, font=("Arial", self.font_md)).grid(row=0, column=i, sticky="ew")
                
            ctk.CTkButton(row, text="X", width=25, fg_color=config.COLOR_DANGER, command=lambda x=idx: self._remove_item(x)).grid(row=0, column=6)
            
        self._update_summary()

    def _remove_item(self, idx):
        self.cart.pop(idx)
        self._refresh_cart()
"""

with open('d:/files/billing.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = 0
for i, line in enumerate(lines):
    if "def _calculate_totals(self) -> dict:" in line:
        start_idx = i
        break

head = lines[:15]  # Assume lines 0-14 are imports up to "class BillingModule"
tail = lines[start_idx:]

with open('d:/files/billing.py', 'w', encoding='utf-8') as f:
    f.writelines(head)
    f.write(new_content)
    f.write("\\n")
    f.writelines(tail)
