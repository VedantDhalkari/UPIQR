"""
Supplier Master Module
Full CRUD for suppliers — premium formatting matching Purchase/Bill theme
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import config
from ui_components import AnimatedButton, PageHeader
from datetime import datetime


class SupplierMasterModule(ctk.CTkFrame):
    """Supplier master interface — premium two-pane layout with full CRUD"""

    def __init__(self, parent, db_manager, **kwargs):
        # Prevent CustomTkinter from crashing on unknown navigation attributes
        kwargs.pop("current_user", None)
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.db = db_manager
        self.selected_supplier_id = None

        # Apply Base Font Size
        try:
            self.base_size = int(self.db.get_setting("base_font_size") or 12)
        except:
            self.base_size = 12

        self.font_sm  = max(self.base_size - 2, 8)
        self.font_md  = max(self.base_size - 1, 9)
        self.font_lg  = self.base_size
        self.font_xl  = max(self.base_size + 2, 14)
        self.font_xxl = max(self.base_size + 4, 16)

        # ── Header Row ────────────────────────────────────────────────
        hdr_row = ctk.CTkFrame(self, fg_color="transparent")
        hdr_row.pack(fill="x", pady=(0, config.SPACING_SM))

        PageHeader(hdr_row, title="🏭 Supplier Master").pack(side="left")

        # Keyboard hint label
        ctk.CTkLabel(
            hdr_row,
            text="Ctrl+N = New  |  F5 = Refresh  |  Del = Delete  |  Enter/Dbl-Click = Edit",
            font=("Arial", self.font_sm), text_color="gray"
        ).pack(side="left", padx=20)

        AnimatedButton(
            hdr_row, text="+ New Supplier [Ctrl+N]",
            width=170, height=34,
            fg_color=config.COLOR_SUCCESS,
            command=self._open_supplier_form
        ).pack(side="right", padx=config.SPACING_SM)

        # ── Main two-pane layout ──────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # Left: Supplier list
        list_card = ctk.CTkFrame(
            body, fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1, border_color=config.COLOR_BORDER
        )
        list_card.grid(row=0, column=0, sticky="nsew", padx=(0, config.SPACING_SM))

        # Search bar
        search_row = ctk.CTkFrame(list_card, fg_color="transparent")
        search_row.pack(fill="x", padx=10, pady=(10, 5))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._load_suppliers())
        ctk.CTkEntry(
            search_row, textvariable=self.search_var,
            placeholder_text="🔍  Search by name, phone, category, city...",
            height=34,
            font=("Arial", self.font_md)
        ).pack(fill="x")

        # Treeview
        cols = ("id", "name", "phone", "category", "agent", "city")
        tree_frame = ctk.CTkFrame(list_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        style = ttk.Style()
        row_height = max(int(self.base_size * 2.5), 22)
        style.configure(
            "Supplier.Treeview",
            background="white", foreground="#1E293B",
            rowheight=row_height, fieldbackground="white",
            font=("Arial", self.base_size)
        )
        style.configure(
            "Supplier.Treeview.Heading",
            background=config.COLOR_PRIMARY, foreground="white",
            font=("Arial", self.base_size, "bold"), relief="flat"
        )
        style.map("Supplier.Treeview", background=[('selected', '#BFDBFE')])
        style.map("Supplier.Treeview.Heading",
                  background=[('active', config.COLOR_PRIMARY_DARK)])

        self.tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            height=20, style="Supplier.Treeview"
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        col_cfg = [
            ("id",       "ID",            0,   "center"),
            ("name",     "Supplier Name", 180, "w"),
            ("phone",    "Phone",         110, "center"),
            ("category", "Category",      110, "w"),
            ("agent",    "Agent/Rep",     120, "w"),
            ("city",     "City",          100, "center"),
        ]
        for col, hdr, w, anch in col_cfg:
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w, anchor=anch)
        self.tree.column("id", width=0, stretch=False)

        self.tree.tag_configure('even', background="#F8FAFC")
        self.tree.tag_configure('odd',  background="white")

        self.tree.bind("<<TreeviewSelect>>", self._on_supplier_select)
        self.tree.bind("<Double-1>", lambda e: self._open_supplier_form(edit=True))
        self.tree.bind("<Return>",   lambda e: self._open_supplier_form(edit=True))
        self.tree.bind("<Delete>",   lambda e: self._delete_supplier())

        # Right: Detail panel
        self.detail_card = ctk.CTkScrollableFrame(
            body, fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1, border_color=config.COLOR_BORDER
        )
        self.detail_card.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()
        self._load_suppliers()

        # Global shortcuts
        self.after(100, self._bind_shortcuts)

    def _bind_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            top.bind("<Control-n>", lambda e: self._open_supplier_form(), add="+")
            top.bind("<F5>",        lambda e: self._load_suppliers(), add="+")
            self.bind("<Destroy>",  lambda e: self._unbind_shortcuts())
        except:
            pass

    def _unbind_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            top.unbind("<Control-n>")
            top.unbind("<F5>")
        except:
            pass

    # ── Placeholder ───────────────────────────────────────────────────
    def _show_placeholder(self):
        for w in self.detail_card.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.detail_card,
            text="🏭\n\nSelect a supplier\nto view details",
            text_color="gray",
            font=("Arial", self.font_lg)
        ).pack(pady=60)

    # ── Data ──────────────────────────────────────────────────────────
    def _load_suppliers(self):
        q = self.search_var.get().strip()
        if q:
            rows = self.db.execute_query(
                """SELECT supplier_id, name, phone, category, agent_name, city
                   FROM suppliers
                   WHERE name LIKE ? OR phone LIKE ? OR category LIKE ?
                      OR agent_name LIKE ? OR city LIKE ?
                   ORDER BY name""",
                (f"%{q}%",) * 5)
        else:
            rows = self.db.execute_query(
                """SELECT supplier_id, name, phone, category, agent_name, city
                   FROM suppliers ORDER BY name""")

        for r in self.tree.get_children():
            self.tree.delete(r)
        for idx, row in enumerate(rows or []):
            tag = 'even' if idx % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=row, tags=(tag,))

    def _on_supplier_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        if not vals:
            return
        self.selected_supplier_id = vals[0]
        self._load_detail_panel(vals[0])

    def _load_detail_panel(self, sup_id):
        for w in self.detail_card.winfo_children():
            w.destroy()

        sup = self.db.execute_query(
            "SELECT * FROM suppliers WHERE supplier_id = ?", (sup_id,))
        if not sup:
            return
        s = sup[0]
        # s: (id, name, phone, email[maybe], address, city, state, gstin, category, agent_name, transport, notes, created_at)
        # Layout depends on column order — use safe index access

        def _safe(idx):
            try:
                return s[idx] if len(s) > idx else None
            except:
                return None

        # ── Name header ───────────────────────────────────────────────
        name_lbl = ctk.CTkLabel(
            self.detail_card, text=_safe(1) or "Unknown",
            font=("Arial", self.font_xxl, "bold"),
            text_color=config.COLOR_PRIMARY
        )
        name_lbl.pack(pady=(16, 2), padx=12, anchor="w")

        cat_agent = []
        if _safe(8): cat_agent.append(f"Category: {_safe(8)}")
        if _safe(9): cat_agent.append(f"Agent: {_safe(9)}")
        ctk.CTkLabel(
            self.detail_card,
            text="  |  ".join(cat_agent) if cat_agent else "No category/agent set",
            font=("Arial", self.font_md), text_color="gray"
        ).pack(anchor="w", padx=12, pady=(0, 4))

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=6)

        # ── Detail rows ───────────────────────────────────────────────
        def _row(icon, label, val):
            if not val:
                return
            f = ctk.CTkFrame(self.detail_card, fg_color="transparent")
            f.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                f, text=f"{icon} {label}:",
                font=("Arial", self.font_md, "bold"),
                width=130, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                f, text=str(val),
                font=("Arial", self.font_md),
                text_color=config.COLOR_TEXT_PRIMARY
            ).pack(side="left", padx=4)

        _row("📞", "Phone",     _safe(2))
        _row("✉️",  "Email",    _safe(3))
        _row("📍", "Address",  _safe(4))
        _row("🏙️", "City",     _safe(5))
        _row("🗺️",  "State",   _safe(6))
        _row("📎", "GSTIN",    _safe(7))
        _row("🚚", "Transport",_safe(10))
        _row("🗒️",  "Notes",   _safe(11))

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=8)

        # ── Purchase History & Filters ───────────────────────────────────
        filter_f = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        filter_f.pack(fill="x", padx=12, pady=4)
        
        ctk.CTkLabel(filter_f, text="📅 Date Filter (DD-MM-YYYY):", font=("Arial", self.font_md, "bold")).pack(anchor="w")
        
        entry_f = ctk.CTkFrame(filter_f, fg_color="transparent")
        entry_f.pack(fill="x", pady=4)
        
        self.supplier_start_date = ctk.CTkEntry(entry_f, width=110, placeholder_text="Start Date")
        self.supplier_start_date.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(entry_f, text="to").pack(side="left", padx=5)
        
        self.supplier_end_date = ctk.CTkEntry(entry_f, width=110, placeholder_text="End Date")
        self.supplier_end_date.pack(side="left", padx=5)
        
        def apply_filter():
            self._refresh_supplier_history(s[0])
            
        AnimatedButton(entry_f, text="🔍 Filter", width=70, height=28, fg_color=config.COLOR_PRIMARY, command=apply_filter).pack(side="left", padx=10)
        
        self.history_frame = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        self.history_frame.pack(fill="both", expand=True, pady=10)
        
        self._refresh_supplier_history(s[0])

        # ── Action Buttons ────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)
        AnimatedButton(
            btn_row, text="✏️ Edit [Enter]", width=120, height=34,
            fg_color=config.COLOR_WARNING,
            command=lambda: self._open_supplier_form(edit=True)
        ).pack(side="left", padx=(0, 6))
        AnimatedButton(
            btn_row, text="🗑️ Delete [Del]", width=120, height=34,
            fg_color=config.COLOR_DANGER,
            command=self._delete_supplier
        ).pack(side="left")

    def _refresh_supplier_history(self, supplier_id):
        for w in self.history_frame.winfo_children():
            w.destroy()
            
        if not supplier_id:
            return
            
        start_val = self.supplier_start_date.get().strip()
        end_val = self.supplier_end_date.get().strip()
        
        date_query = ""
        params = [supplier_id]
        
        try:
            if start_val:
                dt_start = datetime.strptime(start_val, "%d-%m-%Y")
                date_query += " AND COALESCE(bill_date, purchase_date) >= ?"
                params.append(dt_start.strftime("%Y-%m-%d 00:00:00"))
            if end_val:
                dt_end = datetime.strptime(end_val, "%d-%m-%Y")
                date_query += " AND COALESCE(bill_date, purchase_date) <= ?"
                params.append(dt_end.strftime("%Y-%m-%d 23:59:59"))
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use DD-MM-YYYY format (e.g., 31-12-2023)")
            return
            
        # ── Recent Purchases ──────────────────────────────────────────
        ctk.CTkLabel(
            self.history_frame, text="📦 Filtered Purchases (Up to 50)",
            font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY
        ).pack(anchor="w", padx=12, pady=(0, 4))

        try:
            purch = self.db.execute_query(
                f"""SELECT purchase_date, bill_date, invoice_number, total_amount
                   FROM purchases
                   WHERE supplier_id = ? {date_query} ORDER BY purchase_id DESC LIMIT 50""",
                tuple(params)) or []
        except Exception as e:
            print(f"Supplier history query error: {e}")
            purch = []

        if purch:
            for p in purch:
                raw_date = p[1] if p[1] else p[0]
                date_str = str(raw_date)[:10] if raw_date else "N/A"
                f = ctk.CTkFrame(
                    self.detail_card,
                    fg_color=config.COLOR_BG_HOVER,
                    corner_radius=6
                )
                f.pack(fill="x", padx=12, pady=2)
                ctk.CTkLabel(
                    f,
                    text=f"📅 {date_str}  |  Bill: {p[2] or '-'}  |  ₹{(p[3] or 0):,.2f}",
                    font=("Arial", self.font_md)
                ).pack(side="left", padx=8, pady=4)
        else:
            ctk.CTkLabel(
                self.detail_card, text="No purchases yet.",
                font=("Arial", self.font_sm), text_color="gray"
            ).pack(padx=12, anchor="w")

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=8)

        # ── Recent Stock Entries ──────────────────────────────────────
        ctk.CTkLabel(
            self.detail_card, text="📋 Recent Stock Entries",
            font=("Arial", self.font_xl, "bold"),
            text_color=config.COLOR_PRIMARY
        ).pack(anchor="w", padx=12, pady=(0, 4))

        entries = self.db.execute_query(
            """SELECT se.date_added, i.saree_type, se.quantity_added, se.purchase_price
               FROM stock_entries se
               JOIN inventory i ON se.item_id = i.item_id
               WHERE se.supplier_name = ? ORDER BY se.date_added DESC LIMIT 8""",
            (_safe(1),)) or []

        if entries:
            for e in entries:
                f = ctk.CTkFrame(
                    self.detail_card,
                    fg_color=config.COLOR_BG_HOVER,
                    corner_radius=6
                )
                f.pack(fill="x", padx=12, pady=2)
                date_str = str(e[0])[:10] if e[0] else "N/A"
                ctk.CTkLabel(
                    f,
                    text=f"📅 {date_str}  |  {e[1]}  Qty: {e[2]}  @₹{e[3]:,.2f}",
                    font=("Arial", self.font_md)
                ).pack(side="left", padx=8, pady=4)
        else:
            ctk.CTkLabel(
                self.detail_card, text="No stock entries yet.",
                font=("Arial", self.font_sm), text_color="gray"
            ).pack(padx=12, anchor="w")

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=8)

        # ── Action Buttons ────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)
        AnimatedButton(
            btn_row, text="✏️ Edit [Enter]", width=120, height=34,
            fg_color=config.COLOR_WARNING,
            command=lambda: self._open_supplier_form(edit=True)
        ).pack(side="left", padx=(0, 6))
        AnimatedButton(
            btn_row, text="🗑️ Delete [Del]", width=120, height=34,
            fg_color=config.COLOR_DANGER,
            command=self._delete_supplier
        ).pack(side="left")

    # ── Form ──────────────────────────────────────────────────────────
    def _open_supplier_form(self, edit=False):
        existing = None
        if edit:
            if not self.selected_supplier_id:
                messagebox.showwarning("Select Supplier", "Please select a supplier first.")
                return
            rows = self.db.execute_query(
                "SELECT * FROM suppliers WHERE supplier_id = ?",
                (self.selected_supplier_id,))
            if rows:
                existing = rows[0]

        d = ctk.CTkToplevel(self)
        d.title("Edit Supplier" if edit else "New Supplier")
        d.geometry("580x700")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        d.update_idletasks()
        sw = d.winfo_screenwidth(); sh = d.winfo_screenheight()
        d.geometry(f"+{(sw - 580) // 2}+{(sh - 700) // 2}")

        # Header strip
        hdr = ctk.CTkFrame(d, fg_color=config.COLOR_PRIMARY, corner_radius=0, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text="✏️ Edit Supplier" if edit else "➕ New Supplier",
            font=("Arial", self.font_xxl, "bold"),
            text_color="white"
        ).pack(side="left", padx=16, pady=10)

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        def _field(label, idx=None, placeholder=""):
            lf = ctk.CTkFrame(scroll, fg_color="transparent")
            lf.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(
                lf, text=label,
                font=("Arial", self.font_md, "bold"),
                anchor="w"
            ).pack(fill="x")
            e = ctk.CTkEntry(lf, height=34, placeholder_text=placeholder,
                             font=("Arial", self.font_md))
            if existing and idx is not None and len(existing) > idx and existing[idx]:
                e.insert(0, str(existing[idx]))
            e.pack(fill="x")
            return e

        e_name      = _field("Supplier Name *",                    1, "Full name of supplier")
        e_phone     = _field("Phone Number",                       2, "10-digit mobile")
        e_email     = _field("Email",                              3, "supplier@email.com")
        e_addr      = _field("Address",                            4, "Street address")
        e_city      = _field("City",                               5)
        e_state     = _field("State",                              6)
        e_gstin     = _field("GSTIN",                              7, "22AAAAA0000A1Z5")

        # Category combo
        ctk.CTkLabel(scroll, text="Category", font=("Arial", self.font_md, "bold")).pack(anchor="w")
        cat_combo = ctk.CTkComboBox(
            scroll, height=34,
            font=("Arial", self.font_md),
            values=["Saree Supplier", "Cloth Supplier", "Zari Supplier",
                    "Agent", "Distributor", "Wholesaler", "Transport", "Other"]
        )
        if existing and len(existing) > 8 and existing[8]:
            cat_combo.set(existing[8])
        cat_combo.pack(fill="x", pady=(0, 8))

        e_agent     = _field("Sales Agent / Representative Name",  9)
        e_transport = _field("Transport / Logistics Partner",      10)
        e_notes     = _field("Notes / Remarks",                    11)

        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showerror("Error", "Supplier name is required.", parent=d)
                return
            vals = (
                name, e_phone.get().strip(), e_email.get().strip(),
                e_addr.get().strip(), e_city.get().strip(), e_state.get().strip(),
                e_gstin.get().strip(), cat_combo.get(),
                e_agent.get().strip(), e_transport.get().strip(), e_notes.get().strip()
            )
            try:
                if edit and existing:
                    self.db.execute_query(
                        """UPDATE suppliers SET name=?, phone=?, email=?, address=?,
                           city=?, state=?, gstin=?, category=?, agent_name=?,
                           transport=?, notes=?
                           WHERE supplier_id=?""",
                        (*vals, existing[0]))
                else:
                    self.db.execute_query(
                        """INSERT INTO suppliers
                           (name, phone, email, address, city, state, gstin,
                            category, agent_name, transport, notes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        vals)
                messagebox.showinfo("Saved", "Supplier saved successfully!", parent=d)
                d.destroy()
                self._load_suppliers()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=d)

        AnimatedButton(
            scroll, text="💾 Save Supplier [Ctrl+S / Enter]",
            height=38, fg_color=config.COLOR_SUCCESS, command=save
        ).pack(fill="x", pady=12)

        d.bind("<Return>",   lambda e: save())
        d.bind("<Control-s>", lambda e: save())
        e_name.focus_set()

    # ── Delete ────────────────────────────────────────────────────────
    def _delete_supplier(self):
        if not self.selected_supplier_id:
            messagebox.showwarning("Select Supplier", "Please select a supplier first.")
            return
        # Get name for confirmation
        res = self.db.execute_query(
            "SELECT name FROM suppliers WHERE supplier_id = ?",
            (self.selected_supplier_id,))
        name = res[0][0] if res else "this supplier"

        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{name}'?\n\nNote: Existing purchases referencing this supplier will NOT be deleted."
        ):
            try:
                self.db.execute_query(
                    "DELETE FROM suppliers WHERE supplier_id = ?",
                    (self.selected_supplier_id,))
                self.selected_supplier_id = None
                self._show_placeholder()
                self._load_suppliers()
            except Exception as ex:
                messagebox.showerror("Error", f"Delete failed: {ex}")
