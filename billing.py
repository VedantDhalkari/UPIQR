import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import subprocess
import webbrowser
import urllib.parse
import qrcode
import io
from PIL import Image, ImageTk
from tkcalendar import DateEntry
import config
from ui_components import AnimatedButton, PageHeader


class BillingModule(ctk.CTkFrame):
    """Billing and invoice creation interface (Tabular)"""
    
    def __init__(self, parent, db_manager, invoice_generator, current_user, sale_id=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.invoice_gen = invoice_generator
        self.current_user = current_user
        self.cart = []
        self.editing_sale_id = sale_id 
        
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
            
        ctk.CTkLabel(cw, text="Bill Date", font=("Arial", self.font_md)).grid(row=0, column=1, sticky="w", padx=5)
        self.bill_date_entry = DateEntry(cw, width=12, background=config.COLOR_PRIMARY,
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.bill_date_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        self.customer_name_entry = self._create_labeled_input(cw, "Customer Name", 2)
        self.customer_phone_entry = self._create_labeled_input(cw, "Customer Phone", 3)
        
        # Phone Validation Setup
        self.phone_var = ctk.StringVar()
        self.customer_phone_entry.configure(textvariable=self.phone_var)
        
        def validate_phone(*args):
            val = self.phone_var.get()
            # Remove anything that isn't a digit
            filtered = ''.join(filter(str.isdigit, val))
            # Restrict to 10 digits
            if len(filtered) > 10:
                filtered = filtered[:10]
            # Update entry if needed
            if val != filtered:
                self.phone_var.set(filtered)
                
        self.phone_var.trace_add("write", validate_phone)
        
        try:
            res = self.db.execute_query("SELECT final_amount FROM sales ORDER BY sale_id DESC LIMIT 1")
            last_amt = res[0][0] if res else 0.0
        except: last_amt = 0.0
        
        last_bill_frame = ctk.CTkFrame(cw, fg_color=config.COLOR_PRIMARY_LIGHT, corner_radius=config.RADIUS_MD)
        last_bill_frame.grid(row=0, column=4, rowspan=2, padx=10, sticky="e")
        ctk.CTkLabel(last_bill_frame, text="Last Bill Amount:", font=("Arial", self.font_sm, "bold"), text_color=config.COLOR_PRIMARY).pack(padx=10, pady=(5,0))
        self.last_bill_amount_lbl = ctk.CTkLabel(last_bill_frame, text=f"₹{last_amt:,.2f}", font=("Arial", self.font_lg, "bold"), text_color=config.COLOR_TEXT_PRIMARY)
        self.last_bill_amount_lbl.pack(padx=10, pady=(0,5))
        
        # Salesman dropdown
        ctk.CTkLabel(cw, text="Salesman", font=("Arial", self.font_md)).grid(row=0, column=5, sticky="w", padx=5)
        salesmen_list = ["-- None --"]
        try:
            sr = self.db.execute_query("SELECT unique_number, name FROM salesmen WHERE status='Active' ORDER BY name")
            if sr:
                salesmen_list += [f"[{r[0]}] {r[1]}" if r[0] else r[1] for r in sr]
        except: pass
        self.salesman_combo = ctk.CTkComboBox(cw, values=salesmen_list, height=28)
        self.salesman_combo.set("-- None --")
        self.salesman_combo.grid(row=1, column=5, sticky="ew", padx=5, pady=2)
        self.salesman_combo.bind("<Return>", self._on_salesman_lookup)
        cw.grid_columnconfigure(5, weight=1)

    def _setup_item_entry(self):
        card = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        card.pack(fill="x", pady=(0, config.SPACING_SM), padx=config.SPACING_SM)
        
        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(5,0))
        ctk.CTkLabel(top_bar, text="Item Entry", font=("Arial", self.font_lg, "bold"), text_color="gray").pack(side="left")
        ctk.CTkButton(top_bar, text="🔍 Search Items", width=120, height=25, fg_color=config.COLOR_SECONDARY, command=self._open_search_dialog).pack(side="right")
        
        cw = ctk.CTkFrame(card, fg_color="transparent")
        cw.pack(fill="x", padx=5, pady=5)
        
        fields = ["Barcode/SKU", "Item Name*", "Avail Qty", "MRP", "Price*", "Qty*"]
        self.entry_vars = {}
        
        for i, f in enumerate(fields):
            cw.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(cw, text=f, font=("Arial", self.font_sm)).grid(row=0, column=i, sticky="w", padx=2)
            
            entry = ctk.CTkEntry(cw, height=28)
            entry.grid(row=1, column=i, sticky="ew", padx=2, pady=(0, 5))
            
            key = f.split("*")[0].split("(")[0].replace("/", "_").replace(" ", "_").lower()
            # ALL fields in entry row are now editable for faster runtime adjustments
            entry.configure(state="normal")
            self.entry_vars[key] = entry
            
            if "barcode" in key:
                entry.bind("<Return>", self._on_sku_enter)
                entry.placeholder_text = "Scan/Enter"
                
        self.current_item_id = None
        self.current_avail_qty = 9999
                
        self.add_btn = ctk.CTkButton(cw, text="⬇ Add [Ctrl+Enter]", width=120, command=self._add_to_grid)
        self.add_btn.grid(row=1, column=len(fields), padx=5)
        
        # Keyboard Shortcuts Binding
        try:
            self.after(150, self._bind_local_shortcuts)
        except: pass

    def _bind_local_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            top.bind("<Control-Return>", lambda e: self._add_to_grid(), add="+")
            top.bind("<F1>", lambda e: self.entry_vars['barcode_sku'].focus_set(), add="+")
            top.bind("<F2>", lambda e: self.discount_entry.focus_set(), add="+")
            top.bind("<F3>", lambda e: self.amount_paid_entry.focus_set(), add="+")
        except: pass

    def _setup_grid(self):
        # Scrollable Grid Container
        self.grid_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent", height=250)
        self.grid_frame.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        
        # Configure Treeview Style — do NOT call style.theme_use() here as it resets ALL styles globally
        style = ttk.Style()
        row_height = max(int(self.base_size * 2.5), 20)
        style.configure("BillingV2.Treeview", background="white", foreground="black", rowheight=row_height, fieldbackground="white", font=("Arial", self.base_size), borderwidth=0)
        style.configure("BillingV2.Treeview.Heading", background=config.COLOR_PRIMARY, foreground="white", font=("Arial", self.base_size, "bold"), relief="flat")
        style.map("BillingV2.Treeview.Heading", background=[('active', config.COLOR_PRIMARY_DARK)])
        style.map("BillingV2.Treeview", background=[('selected', '#B4D5F0')], foreground=[('selected', '#1E3A8A')])
        
        self.columns = ("sr", "sku", "barcode", "name", "mrp", "price", "qty", "total")
        self.tree = ttk.Treeview(self.grid_frame, columns=self.columns, show="headings", style="BillingV2.Treeview", height=8)
        
        vsb = ttk.Scrollbar(self.grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("sr",      "Sr. No",    55),
            ("sku",     "SKU",       100),
            ("barcode", "Barcode",   110),
            ("name",    "Item Name", 260),
            ("mrp",     "MRP",       90),
            ("price",   "Price",     90),
            ("qty",     "Qty",       65),
            ("total",   "Total",     110)
        ]
        
        for col, text, width in headings:
            self.tree.heading(col, text=text, anchor="center" if col != "name" else "w")
            self.tree.column(col, width=width, anchor="center" if col != "name" else "w", stretch=True if col == "name" else False)
            
        # MRP column: gray background to signal read-only
        self.tree.tag_configure('mrp_row', background="#F1F5F9")
        self.tree.bind("<Double-1>", self._on_grid_double_click)
        self.tree.bind("<Delete>", lambda e: self._delete_selected_item())
        self.tree.bind("<BackSpace>", lambda e: self._delete_selected_item())
        
        # Action Instruction
        ctk.CTkLabel(self.content_scroll, text="Tip: Double-click Name, Price or Qty to edit inline. MRP is read-only. Press Delete to remove row.", font=("Arial", self.font_sm), text_color="gray").pack(anchor="e", padx=20)
        
    def _setup_footer(self, sale_id):
        footer = ctk.CTkFrame(self.content_scroll, fg_color=config.COLOR_BG_CARD)
        footer.pack(fill="x", padx=config.SPACING_SM, pady=(0, config.SPACING_SM))
        
        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        
        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=20, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(left, text="Subtotal: ₹0.00", font=("Arial", self.font_md), text_color="gray")
        self.subtotal_label.pack(anchor="w", pady=(2, 0))
        
        self.items_count_label = ctk.CTkLabel(left, text="Total Items 0 Total Qty 0", font=("Arial", self.font_sm), text_color="gray")
        self.items_count_label.pack(anchor="w", pady=(0, 5))
        
        discount_frame = ctk.CTkFrame(left, fg_color="transparent")
        discount_frame.pack(anchor="w", fill="x", pady=2)
        ctk.CTkLabel(discount_frame, text="Discount:", font=("Arial", self.font_md)).pack(side="left")
        
        self.disc_type = ctk.StringVar(value="%")
        ctk.CTkSegmentedButton(discount_frame, values=["%", "₹"], variable=self.disc_type, width=60, command=lambda e: self._update_summary()).pack(side="left", padx=5)
        
        self.discount_entry = ctk.CTkEntry(discount_frame, width=60, height=28)
        self.discount_entry.insert(0, "0")
        self.discount_entry.pack(side="left", padx=5)
        self.discount_entry.bind("<KeyRelease>", lambda e: self._update_summary())
        
        self.discount_label = ctk.CTkLabel(discount_frame, text="Amount: -₹0.00", font=("Arial", self.font_sm), text_color="gray")
        self.discount_label.pack(side="left", padx=(5,0))
        
        gst_frame = ctk.CTkFrame(left, fg_color="transparent")
        gst_frame.pack(anchor="w", fill="x", pady=2)
        ctk.CTkLabel(gst_frame, text="GST:", font=("Arial", self.font_md)).pack(side="left")
        
        self.gst_type = ctk.StringVar(value="%")
        ctk.CTkSegmentedButton(gst_frame, values=["%", "₹"], variable=self.gst_type, width=60, command=lambda e: self._update_summary()).pack(side="left", padx=5)
        
        self.gst_entry = ctk.CTkEntry(gst_frame, width=60, height=28)
        self.gst_entry.insert(0, "0")
        self.gst_entry.pack(side="left", padx=5)
        self.gst_entry.bind("<KeyRelease>", lambda e: self._update_summary())
        
        self.gst_label = ctk.CTkLabel(gst_frame, text="Amount: +₹0.00", font=("Arial", self.font_sm), text_color="gray")
        self.gst_label.pack(side="left", padx=(5,0))
        
        self.total_label = ctk.CTkLabel(left, text="Total: ₹0.00", font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY)
        self.total_label.pack(anchor="w", pady=10)
        
        # Payment Method Dropdown
        pm_frame = ctk.CTkFrame(right, fg_color="transparent")
        pm_frame.pack(anchor="e", fill="x", pady=2)
        ctk.CTkLabel(pm_frame, text="Payment Method:", font=("Arial", self.font_md)).pack(side="left")
        
        self.payment_method_var = ctk.StringVar(value="UPI")
        self.payment_method_combo = ctk.CTkComboBox(
            pm_frame, 
            values=["Cash", "UPI", "Card", "Bank Transfer"],
            variable=self.payment_method_var,
            width=120
        )
        self.payment_method_combo.pack(side="right")
        
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
        
        btn_text = "💾 Update Bill [F10]" if sale_id else "💳 Complete Sale [F10]"
        btn_color = config.COLOR_WARNING if sale_id else config.COLOR_SUCCESS
        self.checkout_btn = AnimatedButton(btn_frame, text=btn_text, width=150, height=35, fg_color=btn_color, command=self._complete_sale)
        self.checkout_btn.pack(side="left", padx=5)
        
        # Bind F10 for Complete Sale globally while this frame exists
        self.after(100, lambda: self.winfo_toplevel().bind("<F10>", lambda e: self._complete_sale()))
        self.bind("<Destroy>", lambda e: self.winfo_toplevel().unbind("<F10>"))

    def _create_labeled_input(self, parent, label, col):
        ctk.CTkLabel(parent, text=label, font=("Arial", self.font_md)).grid(row=0, column=col, sticky="w", padx=5)
        entry = ctk.CTkEntry(parent, height=28)
        entry.grid(row=1, column=col, sticky="ew", padx=5, pady=2)
        return entry

    def _on_sku_enter(self, event):
        sku = self.entry_vars['barcode_sku'].get().strip()
        if not sku: return
        
        # Search by barcode or SKU
        try:
            res = self.db.execute_query(
                "SELECT item_id, saree_type, brand, material, mrp, selling_price, quantity, barcode FROM inventory WHERE sku_code = ? OR barcode = ?", 
                (sku, sku)
            )
        except:
             res = []
        if res:
            i_id, type_, brand, mat, mrp_val, sale, qty, barcode = res[0]
            name = f"{type_} {brand or ''} {mat or ''}".strip()
            self.current_item_id = i_id
            self.current_avail_qty = qty
            self.current_barcode = barcode
            
            # Resolve to the actual SKU for the entry field
            self.entry_vars['barcode_sku'].delete(0, "end")
            self.entry_vars['barcode_sku'].insert(0, sku) # 'sku' here is what was entered/found
            
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            
            # Set MRP (using stored mrp from inventory)
            mrp_to_show = mrp_val if mrp_val and mrp_val > 0 else sale
            self.entry_vars['mrp'].configure(state="normal")
            self.entry_vars['mrp'].delete(0, "end"); self.entry_vars['mrp'].insert(0, str(mrp_to_show))
            self.entry_vars['mrp'].configure(state="readonly")
            
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end"); self.entry_vars['avail_qty'].insert(0, str(qty))
            
            self.entry_vars['price'].configure(state="normal")
            self.entry_vars['price'].delete(0, "end")
            self.entry_vars['price'].insert(0, str(sale))
            
            self.entry_vars['mrp'].configure(state="normal")
            
            self.entry_vars['qty'].focus_set()
        else:
            self.current_item_id = None
            self.current_avail_qty = 9999
            self.current_barcode = ""
            self.entry_vars['item_name'].focus_set()

    def _on_salesman_lookup(self, event=None):
        """Auto-find salesman by typing its unique number and pressing enter."""
        val = self.salesman_combo.get().strip()
        if not val or val == "-- None --":
            return
            
        values = self.salesman_combo.cget("values")
        # Try finding by number: e.g. "101" matches "[101] John"
        for v in values:
            if f"[{val}]" in v:
                self.salesman_combo.set(v)
                return
        
        # Exact match or starts with name
        for v in values:
            if val.lower() in v.lower():
                self.salesman_combo.set(v)
                return

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
            
            if not q: res = self.db.execute_query("SELECT item_id, sku_code, barcode, saree_type, brand, selling_price, quantity FROM inventory WHERE quantity > 0 LIMIT 20")
            else: res = self.db.execute_query("SELECT item_id, sku_code, barcode, saree_type, brand, selling_price, quantity FROM inventory WHERE (sku_code LIKE ? OR barcode LIKE ? OR saree_type LIKE ?) AND quantity > 0 LIMIT 20", (f"%{q}%", f"%{q}%", f"%{q}%"))
            
            for item in res:
                row = ctk.CTkFrame(results_frame)
                row.pack(fill="x", pady=2)
                name = f"{item[3]} {item[4] or ''}"
                barcode_str = f"| B: {item[2]}" if item[2] else ""
                ctk.CTkLabel(row, text=f"{item[1]} {barcode_str} - {name} (₹{item[5]}) [Qty: {item[6]}]").pack(side="left", padx=10)
                ctk.CTkButton(row, text="Select", width=60, command=lambda i=item, n=name: select(i, n)).pack(side="right", padx=10, pady=5)
                
        def select(item, name):
            self.entry_vars['barcode_sku'].delete(0, "end"); self.entry_vars['barcode_sku'].insert(0, item[1]) # Prefill with SKU
            self.entry_vars['item_name'].delete(0, "end"); self.entry_vars['item_name'].insert(0, name)
            
            self.entry_vars['mrp'].configure(state="normal")
            self.entry_vars['mrp'].delete(0, "end"); self.entry_vars['mrp'].insert(0, str(item[5]))
            self.entry_vars['mrp'].configure(state="readonly")            
            
            self.entry_vars['price'].delete(0, "end"); self.entry_vars['price'].insert(0, str(item[5]))
            
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end"); self.entry_vars['avail_qty'].insert(0, str(item[6]))
            self.entry_vars['avail_qty'].configure(state="readonly")
            
            self.current_item_id = item[0]
            self.current_avail_qty = item[5]
            self.current_barcode = item[2]
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
            
            if not name or qty == 0:
                messagebox.showerror("Error", "Name and positive/negative Qty required")
                return
                
            if qty < 0:
                if "(Returned)" not in name:
                    name += " (Returned)"
            elif qty > 0:
                has_return = any(item.get('quantity', 0) < 0 for item in self.cart)
                if has_return and "(Replaced)" not in name:
                    name += " (Replaced)"
                
            if self.current_item_id and qty > self.current_avail_qty:
                messagebox.showwarning("Stock Limit", f"Only {self.current_avail_qty} available.")
                return
                
            for cart_item in self.cart:
                # Merge by item_id (most reliable) or name+sku
                if (self.current_item_id and cart_item['item_id'] == self.current_item_id) or \
                   (not self.current_item_id and cart_item['sku'] == sku and cart_item['name'] == name):
                    
                    if cart_item['quantity'] + qty > self.current_avail_qty:
                        messagebox.showwarning("Stock Limit", "Cannot exceed available quantity")
                        return
                    cart_item['quantity'] += qty
                    cart_item['total'] = cart_item['quantity'] * cart_item['price']
                    break
            else:
                mrp_val = float(self.entry_vars['mrp'].get() or price)  # MRP is locked entry
                self.cart.append({
                    'item_id': self.current_item_id,
                    'sku': sku,
                    'barcode': getattr(self, 'current_barcode', ''),
                    'name': name,
                    'mrp': mrp_val,
                    'price': price,
                    'quantity': qty,
                    'total': price * qty,
                    'available_qty': self.current_avail_qty
                })
                
            self._refresh_cart()
            
            self.entry_vars['barcode_sku'].delete(0, "end")
            self.entry_vars['item_name'].delete(0, "end")
            self.entry_vars['mrp'].configure(state="normal")
            self.entry_vars['mrp'].delete(0, "end")
            self.entry_vars['mrp'].configure(state="readonly")
            self.entry_vars['price'].delete(0, "end")
            self.entry_vars['qty'].delete(0, "end")
            self.entry_vars['avail_qty'].configure(state="normal")
            self.entry_vars['avail_qty'].delete(0, "end")
            self.entry_vars['avail_qty'].configure(state="readonly")
            
            self.current_item_id = None
            self.current_avail_qty = 9999
            self.current_barcode = ""
            self.entry_vars['barcode_sku'].focus_set()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers")

    def _refresh_cart(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for idx, item in enumerate(self.cart):
            mrp_val = item.get('mrp', item['price'])  # MRP stored separately; fallback to price
            vals = (
                str(idx+1),
                item['sku'],
                item.get('barcode', ''),
                item['name'],
                f"{mrp_val:.2f}",
                f"{item['price']:.2f}",
                str(item['quantity']),
                f"{item['total']:.2f}"
            )
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=vals, tags=(tag,))
            
        self.tree.tag_configure('even', background="white", foreground="black")
        self.tree.tag_configure('odd',  background="#F8FAFC", foreground="black")
            
        self._update_summary()

    def _on_grid_double_click(self, event):
        """Handle double click editing on grid for Name, Price or Qty.
        Columns: 0=sr, 1=sku, 2=barcode, 3=name, 4=mrp(readonly), 5=price, 6=qty, 7=total
        """
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell": return
        
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)
        if not row_id: return
        
        col_idx = int(col.replace('#', '')) - 1  # 0-based
        # Allow editing: Name=3, MRP=4, Price=5, Qty=6
        if col_idx not in [3, 4, 5, 6]: return
        
        x, y, w, h = self.tree.bbox(row_id, column=col)
        
        tree_idx = self.tree.index(row_id)
        current_val = self.cart[tree_idx]
        
        if col_idx == 3:   val_to_show = current_val['name']
        elif col_idx == 4: val_to_show = str(current_val.get('mrp', 0))
        elif col_idx == 5: val_to_show = str(current_val['price'])
        elif col_idx == 6: val_to_show = str(current_val['quantity'])
        
        # Entry overlay
        edit_entry = ttk.Entry(self.tree, font=("Arial", self.font_md))
        edit_entry.insert(0, val_to_show)
        edit_entry.place(x=x, y=y, width=w, height=h)
        edit_entry.focus_set()
        edit_entry.select_range(0, 'end')
        
        def save_edit(e, t_idx=tree_idx, c_idx=col_idx, entry_widget=edit_entry):
            new_val = entry_widget.get().strip()
            
            try:
                if c_idx == 3: # Name
                    if new_val: self.cart[t_idx]['name'] = new_val
                elif c_idx == 4: # MRP
                    self.cart[t_idx]['mrp'] = float(new_val)
                elif c_idx == 5: # Price
                    self.cart[t_idx]['price'] = float(new_val)
                    self.cart[t_idx]['total'] = self.cart[t_idx]['price'] * self.cart[t_idx]['quantity']
                elif c_idx == 6: # Qty
                    new_qty = int(new_val)
                    if new_qty != 0:
                        if new_qty <= self.cart[t_idx]['available_qty']:
                            self.cart[t_idx]['quantity'] = new_qty
                            self.cart[t_idx]['total'] = self.cart[t_idx]['price'] * self.cart[t_idx]['quantity']
                        else:
                            messagebox.showwarning("Stock Limit", f"Only {self.cart[t_idx]['available_qty']} available.")
            except ValueError: pass
            
            entry_widget.destroy()
            self._refresh_cart()
            
        edit_entry.bind("<Return>", save_edit)
        edit_entry.bind("<FocusOut>", save_edit)
        edit_entry.bind("<Escape>", lambda e: edit_entry.destroy())

    def _delete_selected_item(self):
        sel = self.tree.selection()
        if not sel: return
        
        idx = self.tree.index(sel[0])
        self.cart.pop(idx)
        self._refresh_cart()
    def _calculate_totals(self) -> dict:
        """Calculate cart totals"""
        subtotal = sum(item['total'] for item in self.cart)
        try:
            discount_val = float(self.discount_entry.get() or 0)
        except ValueError:
            discount_val = 0
            
        if getattr(self, "disc_type", None) and self.disc_type.get() == "₹":
            discount_amount = discount_val
            discount_percent = (discount_amount / subtotal * 100) if subtotal > 0 else 0
        else:
            discount_percent = discount_val
            discount_amount = subtotal * (discount_percent / 100)
            
        after_discount = subtotal - discount_amount
        
        try:
            gst_val = float(self.gst_entry.get() or 0)
        except ValueError:
            gst_val = 0
            
        if getattr(self, "gst_type", None) and self.gst_type.get() == "₹":
            gst_amount = gst_val
            gst_percent = (gst_amount / after_discount * 100) if after_discount > 0 else 0
        else:
            gst_percent = gst_val
            gst_amount = after_discount * (gst_percent / 100)
            
        total = after_discount + gst_amount
        
        return {
            "subtotal": subtotal,
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "gst_percent": gst_percent,
            "gst_amount": gst_amount,
            "total": total
        }

    def _update_summary(self):
        """Update cart summary"""
        totals = self._calculate_totals()
        
        total_qty = sum(item.get('quantity', 0) for item in self.cart)
        total_items = len(self.cart)
        
        self.subtotal_label.configure(text=f"Subtotal: ₹{totals['subtotal']:,.2f}")
        self.items_count_label.configure(text=f"Total Items {total_items} Total Qty {int(total_qty)}")
        self.discount_label.configure(text=f"Discount ({totals['discount_percent']:.1f}%): -₹{totals['discount_amount']:,.2f}")
        self.gst_label.configure(text=f"GST ({totals['gst_percent']:.1f}%): +₹{totals['gst_amount']:,.2f}")
        
        self.total_label.configure(text=f"Total: ₹{totals['total']:,.2f}")
        
        # Update Payment Fields
        try:
            paid_str = self.amount_paid_entry.get().strip()
            if not paid_str:
                paid_val = totals['total']
            else:
                paid_val = float(paid_str)
        except ValueError:
            paid_val = totals['total']
        
        balance = totals['total'] - paid_val
        self.balance_label.configure(text=f"Balance Due: ₹{max(0, balance):,.2f}")
        
        if balance > 0:
             self.balance_label.configure(text_color=config.COLOR_DANGER)
        else:
             self.balance_label.configure(text_color=config.COLOR_SUCCESS)
    
    def _print_invoice(self, filepath: str):
        """Open PDF for printing instead of silent native print to avoid crashes"""
        try:
            opened = self._open_pdf(filepath)
            if opened:
                messagebox.showinfo("Print Options", "The invoice has been opened in your default PDF viewer.\nPlease proceed to print from there.")
            else:
                messagebox.showerror("Error", "Could not open the invoice automatically to print.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print:\n{str(e)}\n\nPlease manually open the PDF.")

    def _open_pdf(self, filepath: str) -> bool:
        """
        Open a PDF file with multiple fallback methods.
        Returns True if successful, False otherwise.
        """
        try:
            # Method 1: os.startfile (Windows primary method)
            os.startfile(filepath)
            return True
        except Exception as e1:
            try:
                 # Method 2: subprocess with default PDF viewer
                 import subprocess
                 subprocess.Popen(['start', '', filepath], shell=True)
                 return True
            except Exception as e2:
                 try:
                      # Method 3: webbrowser fallback
                      import webbrowser
                      webbrowser.open(filepath)
                      return True
                 except: return False
    def _generate_detailed_whatsapp_msg(self, totals, bill_number):
        """Generate detailed WhatsApp receipt"""
        shop_name = "Shree Ganesha Silk"
        date_str = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        
        msg = f"*{shop_name}*\n"
        if bill_number and bill_number != "DRAFT":
            msg += f"🧾 Bill No: {bill_number}\n"
        msg += f"📅 Date: {date_str}\n"
        msg += "--------------------------------\n"
        msg += "*Items Details:*\n"
        
        for idx, item in enumerate(self.cart):
            sr = idx + 1
            msg += f"{sr}. {item['name']}\n"
            msg += f"   Qty: {item['quantity']} × ₹{item['price']:,.2f} = *₹{item['total']:,.2f}*\n"
            
        msg += "--------------------------------\n"
        msg += f"Subtotal: ₹{totals['subtotal']:,.2f}\n"
        if totals['discount_amount'] > 0:
            msg += f"Discount: -₹{totals['discount_amount']:,.2f}\n"
        if totals['gst_amount'] > 0:
            msg += f"GST: +₹{totals['gst_amount']:,.2f}\n"
        
        msg += f"*Total Amount: ₹{totals['total']:,.2f}*\n"
        
        # Payment History from DB if editing
        if hasattr(self, 'editing_sale_id') and self.editing_sale_id:
            try:
                history = self.db.execute_query(
                    "SELECT amount_paid, payment_date FROM payment_history WHERE sale_id = ? ORDER BY payment_date ASC",
                    (self.editing_sale_id,)
                )
                if history:
                    msg += "\n*Payment Ledger:*\n"
                    for h in history:
                        p_date = str(h[1])[:10] if h[1] else ""
                        msg += f"• {p_date}: ₹{h[0]:,.2f}\n"
            except Exception: pass
        
        # Add payment details if available from entry
        try:
            paid_str = self.amount_paid_entry.get().strip()
            total_paid_now = float(paid_str) if paid_str else totals['total']
            balance = max(0, totals['total'] - total_paid_now)
            msg += f"\nTotal Paid: ₹{total_paid_now:,.2f}\n"
            if balance > 0:
                msg += f"Balance Due: ₹{balance:,.2f}\n"
        except: pass
        
        msg += "\nThank you for shopping with us! 🙏"
        return msg

    def _send_whatsapp(self):
        """Send bill details via WhatsApp"""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to cart first.")
            return
            
        phone = self.customer_phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("Missing Phone", "Please enter customer phone number.")
            return
            
        totals = self._calculate_totals()
        
        # If we have recently completed a sale, grab the LAST bill number
        bill_num_preview = "DRAFT"
        if hasattr(self, 'last_generated_bill_no') and self.last_generated_bill_no:
            bill_num_preview = self.last_generated_bill_no
        elif hasattr(self, 'editing_sale_id') and self.editing_sale_id:
             try:
                 bill_num_preview = self.db.execute_query("SELECT bill_number FROM sales WHERE sale_id=?", (self.editing_sale_id,))[0][0]
             except: pass
        
        bill_text = self._generate_detailed_whatsapp_msg(totals, bill_num_preview)
        
        # Append social media links directly per user request
        bill_text += "\n\n🌐 *Connect with us:*"
        bill_text += "\n📍 Location: https://maps.app.goo.gl/re9BT7rKk5q19LqV9"
        bill_text += "\n📸 Instagram: https://www.instagram.com/shri_ganesha_silk/"
        bill_text += "\n👍 Facebook: https://www.facebook.com/share/1Cv2wsR1VE/"
        
        # Encode for URL
        import urllib.parse
        encoded_text = urllib.parse.quote(bill_text)
        
        # Open WhatsApp Web
        import webbrowser
        webbrowser.open(f"https://web.whatsapp.com/send?phone=+91{phone}&text={encoded_text}")

    def _load_sale_for_editing(self):
        """Load sale details into UI"""
        try:
            # Fetch sale details (including payment info which we just added columns for)
            # Note: The query in get_bill_details might need update or we query manually to get paid/due
            # Accessing DB directly here for clarity
            sale_data = self.db.execute_query(
                "SELECT customer_name, customer_phone, discount_percent, amount_paid, gst_amount, final_amount, total_amount FROM sales WHERE sale_id = ?",
                (self.editing_sale_id,)
            )
            
            if not sale_data:
                messagebox.showerror("Error", "Bill not found")
                return
                
            name, phone, disc, paid, gst_amt, final_amt, tot_amt = sale_data[0]
            
            # Since we calculate GST as a percent of (tot_amt - discount), let's backcheck the percent if possible
            # or simply load the discount frame and assume user re-enters gst. But let's try to reverse-engineer %:
            sub = tot_amt
            sub_after_disc = sub - (sub * (disc / 100))
            gst_perc = (gst_amt / sub_after_disc * 100) if sub_after_disc > 0 else 0
            
            # Set fields
            if name: self.customer_name_entry.insert(0, name)
            if phone: self.customer_phone_entry.insert(0, phone)
            
            if hasattr(self, 'disc_type'): self.disc_type.set("%")
            self.discount_entry.insert(0, str(disc))
            
            # Add gst back if exists
            if hasattr(self, 'gst_entry'):
                if hasattr(self, 'gst_type'): self.gst_type.set("%")
                self.gst_entry.delete(0, "end")
                self.gst_entry.insert(0, f"{gst_perc:g}")
            
            self.amount_paid_entry.insert(0, str(paid))
            
            # Fetch items
            items = self.db.execute_query(
                """SELECT si.item_id, si.sku_code, si.item_name, si.quantity, si.unit_price, i.quantity
                   FROM sale_items si
                   LEFT JOIN inventory i ON si.item_id = i.item_id
                   WHERE si.sale_id = ?""",
                (self.editing_sale_id,)
            )
            
            for item in items:
                self.cart.append({
                    'item_id': item[0],
                    'sku': item[1],
                    'name': item[2],
                    'mrp': item[4],   # use sale price as MRP baseline when editing old bill
                    'price': item[4],
                    'quantity': item[3],
                    'total': item[3] * item[4],
                    'available_qty': (item[5] or 0) + item[3] # Available = Current Stock + Qty in Cart (since we holding it)
                })
            
            self._refresh_cart()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bill: {e}")

    def _complete_sale(self):
        """Complete sale and generate invoice with robust error handling"""
        if not self.cart:
            messagebox.showerror("Error", "Cart is empty")
            return
            
        phone = self.customer_phone_entry.get().strip()
        if phone and (len(phone) != 10 or not phone.isdigit()):
            messagebox.showerror("Validation Error", "If provided, please enter a valid 10-digit Customer Phone Number.")
            return
        
        try:
            # Calculate totals
            totals = self._calculate_totals()
            
            # Use a single connection for the transaction
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if self.editing_sale_id:
                # Update existing sale
                sale_id = self.editing_sale_id
                
                # 1. Revert Stock for ORIGINAL items
                old_items = self.db.execute_query("SELECT item_id, quantity FROM sale_items WHERE sale_id = ?", (sale_id,), cursor=cursor)
                for item_id, qty in old_items:
                    self.db.execute_query("UPDATE inventory SET quantity = quantity + ? WHERE item_id = ? AND sku_code != 'CUSTOM'", (qty, item_id), cursor=cursor)

                # 2. Update Sale Record
                payment_status = "Paid"
                try:
                    paid_str = self.amount_paid_entry.get().strip()
                    amount_paid = float(paid_str) if paid_str else totals['total']
                except ValueError:
                    amount_paid = totals['total']
                
                balance = max(0, totals['total'] - amount_paid)
                if balance > 0: payment_status = "Partial" if amount_paid > 0 else "Pending"

                # Get old payment to log difference
                old_paid_res = self.db.execute_query("SELECT amount_paid FROM sales WHERE sale_id=?", (sale_id,), cursor=cursor)
                old_paid = old_paid_res[0][0] if old_paid_res else 0

                self.db.execute_query(
                    """UPDATE sales SET customer_name=?, customer_phone=?, total_amount=?, 
                       discount_percent=?, discount_amount=?, gst_amount=?, final_amount=?, 
                       amount_paid=?, balance_due=?, payment_status=?
                       WHERE sale_id=?""",
                    (self.customer_name_entry.get() or None, self.customer_phone_entry.get() or None,
                     totals['subtotal'], totals['discount_percent'], totals['discount_amount'],
                     totals['gst_amount'], totals['total'], amount_paid, balance, payment_status, sale_id),
                     cursor=cursor
                )
                
                # Log Payment Change if it increased
                diff = amount_paid - old_paid
                if diff > 0:
                    self.db.execute_insert(
                        "INSERT INTO payment_history (sale_id, amount_paid, payment_method, activity_note) VALUES (?, ?, ?, ?)",
                        (sale_id, diff, "Cash", "Exchange / Bill Updated"), cursor=cursor
                    )
                
                # 3. Delete old items
                self.db.execute_query("DELETE FROM sale_items WHERE sale_id = ?", (sale_id,), cursor=cursor)
                
                bill_number = self.db.execute_query("SELECT bill_number FROM sales WHERE sale_id=?", (sale_id,), cursor=cursor)[0][0]
                
            else:
                # NEW SALE LOGIC
                last_id_res = self.db.execute_query("SELECT MAX(sale_id) FROM sales", cursor=cursor)
                next_id = 1
                if last_id_res and last_id_res[0][0]:
                    next_id = last_id_res[0][0] + 1
                
                bill_number = f"ESB-{next_id}"
                
                sale_id = self.db.execute_insert(
                    """INSERT INTO sales (bill_number, customer_name, customer_phone,
                       total_amount, discount_percent, discount_amount, gst_amount,
                       final_amount, payment_method, created_by, salesman)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (bill_number, self.customer_name_entry.get() or None,
                     self.customer_phone_entry.get() or None, totals['subtotal'], totals['discount_percent'],
                     totals['discount_amount'], totals['gst_amount'], totals['total'], self.payment_method_combo.get(),
                     self.current_user['username'],
                     (self.salesman_combo.get() if hasattr(self, 'salesman_combo') and self.salesman_combo.get() != '-- None --' else None)),
                    cursor=cursor
                )
                
                try:
                    paid_str = self.amount_paid_entry.get().strip()
                    amount_paid = float(paid_str) if paid_str else totals['total']
                except ValueError:
                    amount_paid = totals['total'] 
                
                balance_due = max(0, totals['total'] - amount_paid)
                payment_status = "Paid"
                if balance_due > 0:
                    payment_status = "Partial" if amount_paid > 0 else "Pending"
                
                self.db.execute_query(
                    "UPDATE sales SET amount_paid = ?, balance_due = ?, payment_status = ? WHERE sale_id = ?",
                    (amount_paid, balance_due, payment_status, sale_id), cursor=cursor
                )
                
                if amount_paid > 0:
                    self.db.execute_insert(
                        "INSERT INTO payment_history (sale_id, amount_paid, payment_method, activity_note) VALUES (?, ?, ?, ?)",
                        (sale_id, amount_paid, self.payment_method_combo.get(), "Initial Payment"), cursor=cursor
                    )
            
            # Tag items if there is a return/exchange
            has_return = any(item['quantity'] < 0 for item in self.cart)
            if has_return:
                for item in self.cart:
                    if item['quantity'] < 0 and "(Returned)" not in item['name']:
                        item['name'] = f"{item['name']} (Returned)"
                    elif item['quantity'] > 0 and "(Replaced)" not in item['name']:
                        item['name'] = f"{item['name']} (Replaced)"

            # Insert sale items and update inventory
            for item in self.cart:
                item_id_to_store = item['item_id']
                if item_id_to_store is None:
                    item_id_to_store = self.db.get_or_create_custom_item()

                self.db.execute_insert(
                    """INSERT INTO sale_items (sale_id, item_id, sku_code, item_name,
                       quantity, unit_price, total_price, mrp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sale_id, item_id_to_store, item['sku'], item['name'],
                     item['quantity'], item['price'], item['total'], item['mrp']), cursor=cursor
                )
                
                if item['item_id'] and item['sku'] != 'CUSTOM':
                    self.db.execute_query(
                        "UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?",
                        (item['quantity'], item['item_id']), cursor=cursor
                    )
            
            # Commit Database Transaction
            conn.commit()
            
            # Store for WhatsApp
            self.last_generated_bill_no = bill_number
            
            # Generate invoice PDF
            try:
                invoice_path = self.invoice_gen.generate_invoice(sale_id)
                invoice_generated = True
            except Exception as pdf_error:
                invoice_generated = False
                invoice_path = None
                error_msg = str(pdf_error)
            
            # Clear cart first
            self.cart.clear()
            self._refresh_cart()
            self.customer_name_entry.delete(0, 'end')
            self.customer_phone_entry.delete(0, 'end')
            self.discount_entry.delete(0, 'end')
            if hasattr(self, 'gst_entry'):
                self.gst_entry.delete(0, 'end')
                self.gst_entry.insert(0, "0")
            self.amount_paid_entry.delete(0, 'end')
            
            # Reset the item entry row
            if hasattr(self, 'entry_vars'):
                self.entry_vars['barcode_sku'].delete(0, "end")
                self.entry_vars['item_name'].delete(0, "end")
                self.entry_vars['price'].delete(0, "end")
                self.entry_vars['qty'].delete(0, "end")
                self.entry_vars['avail_qty'].configure(state="normal")
                self.entry_vars['avail_qty'].delete(0, "end")
                self.entry_vars['avail_qty'].configure(state="readonly")
                self.current_item_id = None
                self.current_avail_qty = 9999
            
            # Update last bill amount
            try:
                res = self.db.execute_query("SELECT final_amount FROM sales ORDER BY sale_id DESC LIMIT 1")
                last_amt = res[0][0] if res else 0.0
                if hasattr(self, 'last_bill_amount_lbl'):
                    self.last_bill_amount_lbl.configure(text=f"₹{last_amt:,.2f}")
            except Exception:
                pass
            
            # Show success message and handle PDF
            action_text = "Updated" if self.editing_sale_id else "Completed"
            if invoice_generated:
                # Try to open the PDF
                pdf_opened = self._open_pdf(invoice_path)
                
                if pdf_opened:
                    success_msg = (
                        f"✅ Sale {action_text} Successfully!\n\n"
                        f"Bill Number: {bill_number}\n"
                        f"Total Amount: ₹{totals['total']:,.2f}\n\n"
                        f"Invoice PDF has been generated and opened.\n"
                        f"Location: {invoice_path}"
                    )
                else:
                    success_msg = (
                        f"✅ Sale {action_text} Successfully!\n\n"
                        f"Bill Number: {bill_number}\n"
                        f"Total Amount: ₹{totals['total']:,.2f}\n\n"
                        f"⚠️ Could not auto-open PDF.\n"
                        f"Please open manually from:\n{invoice_path}\n\n"
                        f"💡 Tip: Right-click the file and select 'Open with' → PDF viewer"
                    )
                
                messagebox.showinfo("Sale Completed", success_msg)
                
                # Store for WhatsApp before potential clear
                self.last_generated_bill_no = bill_number
                
                # Ask if user wants to print
                if messagebox.askyesno("Print Invoice", "Would you like to print the invoice?"):
                     self._print_invoice(invoice_path)
            else:
                # Sale succeeded but PDF failed
                error_msg = (
                    f"✅ Sale {action_text} Successfully!\n\n"
                    f"Bill Number: {bill_number}\n"
                    f"Total Amount: ₹{totals['total']:,.2f}\n\n"
                    f"⚠️ Warning: PDF invoice generation failed.\n"
                    f"Error: {error_msg}\n\n"
                    f"Sale data is saved in the database.\n"
                    f"You can regenerate the invoice later from Reports."
                )
                messagebox.showwarning("Sale Completed (PDF Failed)", error_msg)
            
            # Reset editing state and clear UI
            self.editing_sale_id = None
            self.checkout_btn.configure(text="💳 Complete Sale", fg_color=config.COLOR_SUCCESS)
            
            # Show UPI QR payment popup if UPI is selected
            if self.payment_method_combo.get() == "UPI" and amount_paid > 0:
                self.after(200, lambda: self._show_upi_qr_popup(bill_number, amount_paid))
            
            # Clear UI for next bill
            self.cart.clear()
            self._refresh_cart()
            if hasattr(self, 'customer_name_entry'):
                self.customer_name_entry.delete(0, 'end')
            if hasattr(self, 'customer_phone_entry'):
                self.customer_phone_entry.delete(0, 'end')
            if hasattr(self, 'discount_entry'):
                self.discount_entry.delete(0, 'end')
                self.discount_entry.insert(0, '0')
            if hasattr(self, 'gst_entry'):
                self.gst_entry.delete(0, 'end')
                self.gst_entry.insert(0, '0')
            if hasattr(self, 'amount_paid_entry'):
                self.amount_paid_entry.delete(0, 'end')
            
            # Reset Bill Number UI to auto-generated
            if hasattr(self, 'bill_no_entry'):
                self.bill_no_entry.configure(state="normal")
                self.bill_no_entry.delete(0, 'end')
                self.bill_no_entry.insert(0, "Auto-Generated")
                self.bill_no_entry.configure(state="readonly")
                
            self.header.set_title("New Bill / Invoice")
            self._update_summary()
                
        except Exception as e:
            # If the DB connection was active, rollback it before exiting
            try: conn.rollback()
            except: pass
            messagebox.showerror("Error", f"Failed to complete sale:\n\n{str(e)}\n\nPlease contact support if this persists.")

    def _show_upi_qr_popup(self, bill_number, amount):
        """Show UPI QR code popup for customer payment"""
        import tkinter as tk
        from PIL import Image, ImageTk
        import io, qrcode
        
        # Fetch UPI ID from settings or use default
        upi_id = self.db.get_setting("upi_id") or "shreeganesha@upi"
        payee_name = self.db.get_setting("shop_name") or "Shree Ganesha Silk"
        
        d = ctk.CTkToplevel(self)
        d.title(f"UPI Payment - Bill {bill_number}")
        d.geometry("460x580")
        d.resizable(False, False)
        d.transient(self.winfo_toplevel())
        d.grab_set()
        
        # Center the dialog
        d.update_idletasks()
        sw = d.winfo_screenwidth(); sh = d.winfo_screenheight()
        x = (sw - 460) // 2; y = (sh - 580) // 2
        d.geometry(f"+{x}+{y}")
        
        # Header
        hdr = ctk.CTkFrame(d, fg_color=config.COLOR_PRIMARY, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text="📲 UPI Payment", font=("Arial", 20, "bold"), text_color="white").pack(pady=12)
        ctk.CTkLabel(hdr, text=f"Bill No: {bill_number}", font=("Arial", 12), text_color="white").pack(pady=(0, 12))
        
        # Amount box
        amt_frame = ctk.CTkFrame(d, fg_color="#f0f9ff", corner_radius=10)
        amt_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(amt_frame, text="Amount to Pay (Edit to regenerate)", font=("Arial", 12), text_color="gray").pack(pady=(10, 2))
        
        self.upi_amt_var = tk.StringVar(value=f"{amount:.2f}")
        amt_entry = ctk.CTkEntry(amt_frame, textvariable=self.upi_amt_var, font=("Arial", 24, "bold"), text_color=config.COLOR_SUCCESS, justify="center")
        amt_entry.pack(pady=(0, 10))
        
        # QR Code Display
        qr_label = ctk.CTkLabel(d, text="")
        qr_label.pack(pady=10)
        
        def generate_qr(*args):
            try:
                curr_amt = float(self.upi_amt_var.get())
                upi_link = f"upi://pay?pa={upi_id}&pn={payee_name.replace(' ', '%20')}&am={curr_amt:.2f}&cu=INR&tn=Bill%20{bill_number}"
                
                qr = qrcode.QRCode(version=1, box_size=8, border=2)
                qr.add_data(upi_link)
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color="black", back_color="white")
                img_byte_arr = io.BytesIO()
                qr_img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                qr_photo = ImageTk.PhotoImage(Image.open(io.BytesIO(img_byte_arr)))
                qr_label.configure(image=qr_photo)
                qr_label.image = qr_photo  # keep reference
                return upi_link
            except ValueError:
                return None
                
        def delayed_qr_gen(e=None):
            d.after(500, generate_qr)
            
        amt_entry.bind("<KeyRelease>", delayed_qr_gen)
        upi_link_initial = generate_qr()
        
        # UPI ID info
        info_frame = ctk.CTkFrame(d, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(info_frame, text="Scan to pay using any UPI app:", font=("Arial", 11), text_color="gray").pack()
        ctk.CTkLabel(info_frame, text=f"BHIM | GPay | PhonePe | Paytm | Amazon Pay", font=("Arial", 11, "bold"), text_color=config.COLOR_PRIMARY).pack(pady=2)
        
        upi_row = ctk.CTkFrame(info_frame, fg_color="#ede9fe", corner_radius=8)
        upi_row.pack(fill="x", pady=5)
        ctk.CTkLabel(upi_row, text=f"UPI ID:  {upi_id}", font=("Arial", 12, "bold"), text_color="#4a0082").pack(side="left", padx=10, pady=6)
        
        def copy_upi():
            d.clipboard_clear()
            d.clipboard_append(upi_id)
            messagebox.showinfo("Copied!", "UPI ID copied to clipboard.")
        
        ctk.CTkButton(upi_row, text="📋 Copy", width=70, height=28, fg_color="#7c3aed", command=copy_upi).pack(side="right", padx=8, pady=6)
        
        # Close button
        ctk.CTkButton(d, text="✅ Payment Done / Close", fg_color=config.COLOR_SUCCESS, height=40, command=d.destroy).pack(fill="x", padx=20, pady=15)

