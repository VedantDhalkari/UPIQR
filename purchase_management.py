"""
Purchase Management Module
View, Edit, Delete and Reprint past stock purchases
"""

import customtkinter as ctk
from tkinter import messagebox, ttk, simpledialog
import config
from ui_components import AnimatedButton, SearchBar, PageHeader
import os


class PurchaseManagementModule(ctk.CTkFrame):
    """Purchase management interface with full CRUD"""

    def __init__(self, parent, db_manager, invoice_generator, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.db = db_manager
        self.invoice_gen = invoice_generator

        # Font sizing
        try:
            self.base_size = int(self.db.get_setting("base_font_size") or 12)
        except:
            self.base_size = 12
        self.font_sm = max(self.base_size - 1, 9)
        self.font_md = self.base_size
        self.font_lg = self.base_size + 2
        self.font_xl = self.base_size + 4

        # Header
        PageHeader(self, title="📦 Purchase History").pack(fill="x", pady=(0, config.SPACING_LG))

        # ── Tools bar ──────────────────────────────────────────────
        tools_frame = ctk.CTkFrame(self, fg_color="transparent")
        tools_frame.pack(fill="x", pady=(0, config.SPACING_SM))

        self.search_entry = SearchBar(
            tools_frame,
            placeholder="Search by bill no., supplier, transport or LR No...",
            on_search=self._on_search
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, config.SPACING_SM))

        # Refresh button
        AnimatedButton(
            tools_frame, text="🔄 Refresh", width=90,
            fg_color=config.COLOR_SECONDARY, height=36,
            command=self._refresh
        ).pack(side="right", padx=5)

        # ── Action buttons bar ─────────────────────────────────────
        btn_bar = ctk.CTkFrame(self, fg_color="transparent")
        btn_bar.pack(fill="x", pady=(0, config.SPACING_SM))

        AnimatedButton(
            btn_bar, text="👁 View Details [Dbl-Click]",
            fg_color=config.COLOR_PRIMARY, height=36,
            command=self._view_selected
        ).pack(side="left", padx=(0, 6))

        AnimatedButton(
            btn_bar, text="✏️ Edit Purchase",
            fg_color=config.COLOR_WARNING, height=36,
            command=self._edit_selected
        ).pack(side="left", padx=6)

        AnimatedButton(
            btn_bar, text="🗑 Delete Purchase",
            fg_color=config.COLOR_DANGER, height=36,
            command=self._delete_selected
        ).pack(side="left", padx=6)

        AnimatedButton(
            btn_bar, text="🖨️ Print Invoice",
            fg_color=config.COLOR_INFO, height=36,
            command=self._print_selected
        ).pack(side="right", padx=5)

        # ── Summary stat strip ─────────────────────────────────────
        self.summary_bar = ctk.CTkFrame(self, fg_color=config.COLOR_BG_CARD, height=42,
                                        border_width=1, border_color=config.COLOR_BORDER,
                                        corner_radius=config.RADIUS_MD)
        self.summary_bar.pack(fill="x", pady=(0, config.SPACING_SM))
        self.summary_bar.pack_propagate(False)

        self.total_lbl = ctk.CTkLabel(
            self.summary_bar, text="Total Purchases: 0  |  Grand Total: ₹0.00",
            font=ctk.CTkFont(size=self.font_md, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        self.total_lbl.pack(side="left", padx=15, pady=8)

        # ── Treeview container ─────────────────────────────────────
        tree_container = ctk.CTkFrame(self, fg_color="white",
                                      border_width=1, border_color="#CCCCCC",
                                      corner_radius=0)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")

        row_height = max(int(self.base_size * 2.5), 22)
        style.configure("Purchase.Treeview",
                        background="white", foreground="#1E293B",
                        rowheight=row_height, fieldbackground="white",
                        font=("Arial", self.base_size))
        style.configure("Purchase.Treeview.Heading",
                        background=config.COLOR_PRIMARY, foreground="white",
                        font=("Arial", max(self.base_size, 11), "bold"),
                        relief="flat")
        style.map("Purchase.Treeview",
                  background=[('selected', '#BFDBFE')])
        style.map("Purchase.Treeview.Heading",
                  background=[('active', config.COLOR_PRIMARY_DARK)])

        self.columns = ("id", "bill_no", "date", "supplier", "transport", "lr_no",
                        "gst", "expenses", "total", "agent")
        self.tree = ttk.Treeview(tree_container, columns=self.columns,
                                 show="headings", style="Purchase.Treeview")

        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        column_defs = [
            ("id",        "ID",            60,  "center"),
            ("bill_no",   "Bill No.",      110, "center"),
            ("date",      "Date",          110, "center"),
            ("supplier",  "Supplier",      200, "w"),
            ("transport", "Transport",     120, "center"),
            ("lr_no",     "LR No.",        110, "center"),
            ("gst",       "GST",           90,  "e"),
            ("expenses",  "Other Exp.",    100, "e"),
            ("total",     "Total Amount",  130, "e"),
            ("agent",     "Agent",         110, "center"),
        ]
        for col, text, width, anchor in column_defs:
            self.tree.heading(col, text=text,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=width, anchor=anchor, minwidth=40)

        self.tree.tag_configure('normal_even', background="#F8FAFC")
        self.tree.tag_configure('normal_odd',  background="white")

        # Double-click to view
        self.tree.bind("<Double-1>", lambda e: self._view_selected())

        # Delete key shortcut — use after() so toplevel is available
        self.after(100, self._setup_shortcuts)

        self._load_purchases()

    # ── Data Loading ────────────────────────────────────────────────

    def _setup_shortcuts(self):
        """Bind Delete key safely after toplevel is available"""
        try:
            top = self.winfo_toplevel()
            top.bind("<Delete>", lambda e: self._delete_shortcut(), add="+")
            self.bind("<Destroy>", lambda e: self._remove_shortcuts())
        except Exception:
            pass

    def _remove_shortcuts(self):
        """Unbind our Delete key when this widget is destroyed"""
        try:
            self.winfo_toplevel().unbind("<Delete>")
        except Exception:
            pass

    def _refresh(self):
        self._load_purchases()

    def _on_search(self, query):
        self._load_purchases(query)

    def _load_purchases(self, search_query=""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        base_query = """
            SELECT p.purchase_id, p.invoice_number, p.purchase_date, p.bill_date,
                   s.name, p.transport, p.lr_no,
                   p.gst_amount, p.other_expenses, p.total_amount, p.agent_name
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        """

        if search_query:
            base_query += """
                WHERE CAST(p.purchase_id AS TEXT) LIKE ?
                   OR p.invoice_number LIKE ?
                   OR s.name LIKE ?
                   OR p.transport LIKE ?
                   OR p.lr_no LIKE ?
            """
            like_q = f"%{search_query}%"
            base_query += " ORDER BY p.purchase_id DESC LIMIT 200"
            results = self.db.execute_query(base_query, (like_q,) * 5)
        else:
            base_query += " ORDER BY p.purchase_id DESC LIMIT 200"
            results = self.db.execute_query(base_query)

        grand_total = 0.0
        count = 0

        if results:
            for idx, row in enumerate(results):
                # row: 0=id 1=invoice_no 2=purchase_date 3=bill_date
                #       4=supplier 5=transport 6=lr_no
                #       7=gst 8=expenses 9=total 10=agent
                purchase_id   = row[0]
                bill_no       = row[1] or "-"
                raw_date      = row[3] if row[3] else row[2]
                date_str      = self._fmt_date(raw_date)
                supplier      = row[4] or "N/A"
                transport     = row[5] or "-"
                lr_no         = row[6] or "-"
                gst           = row[7] or 0
                expenses      = row[8] or 0
                total         = row[9] or 0
                agent         = row[10] or "-"

                grand_total  += total
                count        += 1

                tag = 'normal_even' if idx % 2 == 0 else 'normal_odd'
                self.tree.insert("", "end", values=(
                    purchase_id, bill_no, date_str, supplier,
                    transport, lr_no,
                    f"₹{gst:,.2f}", f"₹{expenses:,.2f}",
                    f"₹{total:,.2f}", agent
                ), tags=(tag,))

        self.total_lbl.configure(
            text=f"Total Purchases: {count}  |  Grand Total: ₹{grand_total:,.2f}"
        )

    def _fmt_date(self, raw):
        """Convert any date str to DD-MM-YYYY"""
        if not raw:
            return "N/A"
        raw = str(raw)[:10]  # keep YYYY-MM-DD part
        try:
            parts = raw.split("-")
            if len(parts) == 3:
                y, m, d = parts
                return f"{d}-{m}-{y}"
        except:
            pass
        return raw

    # ── Sorting ─────────────────────────────────────────────────────

    def _sort_by(self, col):
        """Toggle sort on clicked column"""
        data = [(self.tree.set(child, col), child)
                for child in self.tree.get_children("")]
        try:
            data.sort(key=lambda x: float(x[0].replace("₹", "").replace(",", "")))
        except:
            data.sort()
        for idx, (_, child) in enumerate(data):
            self.tree.move(child, "", idx)
            tag = 'normal_even' if idx % 2 == 0 else 'normal_odd'
            self.tree.item(child, tags=(tag,))

    # ── Selection helpers ────────────────────────────────────────────

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required",
                                   "Please select a purchase first.", parent=self)
            return None
        return self.tree.item(sel[0])['values'][0]  # purchase_id

    def _delete_shortcut(self):
        if self.tree.focus():
            self._delete_selected()

    # ── View Details ─────────────────────────────────────────────────

    def _view_selected(self):
        pid = self._get_selected_id()
        if pid:
            self._show_detail_dialog(pid)

    def _show_detail_dialog(self, purchase_id):
        # Fetch purchase details
        prow = self.db.execute_query("""
            SELECT p.purchase_id, p.invoice_number, p.bill_date, p.purchase_date,
                   s.name, p.transport, p.lr_no, p.gst_amount, p.other_expenses,
                   p.total_amount, p.agent_name
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.purchase_id = ?
        """, (purchase_id,))
        if not prow:
            return
        pr = prow[0]

        # Items
        items = self.db.execute_query("""
            SELECT pi.sku_code, pi.item_name, pi.quantity, pi.purchase_rate,
                   pi.sale_rate, pi.total_amount, pi.gst_percentage
            FROM purchase_items pi
            WHERE pi.purchase_id = ?
            ORDER BY pi.pur_item_id
        """, (purchase_id,))

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Purchase Details — ID {purchase_id}")
        dialog.geometry("800x640")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.lift()

        # Header strip
        head = ctk.CTkFrame(dialog, fg_color=config.COLOR_PRIMARY, corner_radius=0, height=48)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(
            head, text=f"📦 Purchase #{purchase_id}  •  Bill: {pr[1] or '-'}",
            font=ctk.CTkFont(size=self.font_xl, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=16, pady=10)

        # Info grid
        info_fr = ctk.CTkFrame(dialog, fg_color=config.COLOR_BG_CARD,
                               corner_radius=0, border_width=1, border_color=config.COLOR_BORDER)
        info_fr.pack(fill="x", padx=12, pady=(10, 6))
        info_fr.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def info_cell(parent, row, col, label, value, color=config.COLOR_TEXT_PRIMARY):
            ctk.CTkLabel(parent, text=label,
                         font=ctk.CTkFont(size=self.font_sm),
                         text_color="gray").grid(row=row*2, column=col, sticky="w", padx=10, pady=(6, 0))
            ctk.CTkLabel(parent, text=value,
                         font=ctk.CTkFont(size=self.font_md, weight="bold"),
                         text_color=color).grid(row=row*2+1, column=col, sticky="w", padx=10, pady=(0, 6))

        info_cell(info_fr, 0, 0, "Date", self._fmt_date(pr[2] or pr[3]))
        info_cell(info_fr, 0, 1, "Supplier", pr[4] or "—")
        info_cell(info_fr, 0, 2, "Transport", pr[5] or "—")
        info_cell(info_fr, 0, 3, "LR No.", pr[6] or "—")
        info_cell(info_fr, 1, 0, "GST Amount", f"₹{(pr[7] or 0):,.2f}")
        info_cell(info_fr, 1, 1, "Other Expenses", f"₹{(pr[8] or 0):,.2f}")
        info_cell(info_fr, 1, 2, "Grand Total", f"₹{(pr[9] or 0):,.2f}",
                  color=config.COLOR_SUCCESS)
        info_cell(info_fr, 1, 3, "Agent", pr[10] or "—")

        # Items table
        ctk.CTkLabel(dialog, text="📋 Items",
                     font=ctk.CTkFont(size=self.font_lg, weight="bold"),
                     text_color=config.COLOR_PRIMARY).pack(anchor="w", padx=14, pady=(4, 2))

        tbl_fr = ctk.CTkFrame(dialog, fg_color="white",
                              border_width=1, border_color="#CCCCCC", corner_radius=0)
        tbl_fr.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        style = ttk.Style()
        style.configure("PurDet.Treeview",
                        background="white", foreground="#1E293B",
                        rowheight=max(int(self.base_size * 2.2), 20),
                        fieldbackground="white",
                        font=("Arial", self.base_size))
        style.configure("PurDet.Treeview.Heading",
                        background=config.COLOR_PRIMARY, foreground="white",
                        font=("Arial", self.base_size, "bold"), relief="flat")

        item_cols = ("sku", "name", "gst%", "qty", "rate", "sale_rate", "total")
        itree = ttk.Treeview(tbl_fr, columns=item_cols,
                             show="headings", style="PurDet.Treeview")

        vsb2 = ttk.Scrollbar(tbl_fr, orient="vertical", command=itree.yview)
        itree.configure(yscrollcommand=vsb2.set)
        itree.pack(side="left", fill="both", expand=True)
        vsb2.pack(side="right", fill="y")

        for col_id, hdr, wid, anch in [
            ("sku",      "SKU",       75,  "center"),
            ("name",     "Item Name", 220, "w"),
            ("gst%",     "GST %",     65,  "center"),
            ("qty",      "Qty",       55,  "center"),
            ("rate",     "Pur. Rate", 100, "e"),
            ("sale_rate","Sale Rate", 100, "e"),
            ("total",    "Total",     110, "e"),
        ]:
            itree.heading(col_id, text=hdr)
            itree.column(col_id, width=wid, anchor=anch)

        itree.tag_configure('even', background="#F8FAFC")

        if items:
            for idx, it in enumerate(items):
                gst_pct = it[6] if len(it) > 6 and it[6] else 0
                itree.insert("", "end",
                             values=(it[0], it[1], f"{gst_pct}%", it[2],
                                     f"₹{it[3]:,.2f}", f"₹{it[4]:,.2f}",
                                     f"₹{it[5]:,.2f}"),
                             tags=('even' if idx % 2 == 0 else '',))
        else:
            itree.insert("", "end", values=("—", "No items found", "", "", "", "", ""))

        # Bottom buttons
        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 12))

        AnimatedButton(btn_row, text="🖨️ Print Invoice",
                       fg_color=config.COLOR_INFO,
                       command=lambda: self._print_invoice(purchase_id)).pack(side="left", padx=4)
        AnimatedButton(btn_row, text="✏️ Edit",
                       fg_color=config.COLOR_WARNING,
                       command=lambda: [dialog.destroy(), self._edit_dialog(purchase_id)]).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Close",
                      fg_color="transparent", border_width=1,
                      text_color="gray",
                      command=dialog.destroy).pack(side="right", padx=4)

    # ── Edit Purchase ─────────────────────────────────────────────────

    def _edit_selected(self):
        pid = self._get_selected_id()
        if pid:
            self._edit_dialog(pid)

    def _edit_dialog(self, purchase_id):
        prow = self.db.execute_query("""
            SELECT p.purchase_id, p.invoice_number, p.bill_date,
                   s.name, p.transport, p.lr_no, p.gst_amount,
                   p.other_expenses, p.agent_name
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.purchase_id = ?
        """, (purchase_id,))
        if not prow:
            return
        pr = prow[0]

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Purchase #{purchase_id}")
        dialog.geometry("480x480")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.lift()

        head = ctk.CTkFrame(dialog, fg_color=config.COLOR_WARNING, corner_radius=0, height=44)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text=f"✏️ Edit Purchase #{purchase_id}",
                     font=ctk.CTkFont(size=self.font_lg, weight="bold"),
                     text_color="white").pack(side="left", padx=12, pady=10)

        form = ctk.CTkScrollableFrame(dialog, fg_color="transparent",
                                      scrollbar_button_color=config.COLOR_PRIMARY)
        form.pack(fill="both", expand=True, padx=16, pady=12)

        def field(label, default_val):
            ctk.CTkLabel(form, text=label,
                         font=ctk.CTkFont(size=self.font_sm, weight="bold")).pack(anchor="w", pady=(8, 2))
            e = ctk.CTkEntry(form, height=34)
            e.insert(0, str(default_val) if default_val else "")
            e.pack(fill="x")
            return e

        e_bill     = field("Bill No.", pr[1])
        e_date     = field("Bill Date (DD-MM-YYYY)", self._fmt_date(pr[2]))
        e_supplier = field("Supplier Name", pr[3])
        e_transport= field("Transport", pr[4])
        e_lr       = field("LR No.", pr[5])
        e_gst      = field("GST Amount (₹)", pr[6])
        e_exp      = field("Other Expenses (₹)", pr[7])
        e_agent    = field("Agent Name", pr[8])

        def save():
            try:
                # Parse DD-MM-YYYY → YYYY-MM-DD
                raw_date = e_date.get().strip()
                try:
                    p = raw_date.split("-")
                    db_date = f"{p[2]}-{p[1]}-{p[0]}" if len(p) == 3 else raw_date
                except:
                    db_date = raw_date

                # Find supplier id (or create)
                sup_name = e_supplier.get().strip()
                res = self.db.execute_query(
                    "SELECT supplier_id FROM suppliers WHERE name=?", (sup_name,))
                if res:
                    sup_id = res[0][0]
                else:
                    sup_id = self.db.execute_insert(
                        "INSERT INTO suppliers (name) VALUES (?)", (sup_name,))

                gst_val = float(e_gst.get() or 0)
                exp_val = float(e_exp.get() or 0)

                # Recalculate total from items
                items_total = self.db.execute_query(
                    "SELECT COALESCE(SUM(total_amount), 0) FROM purchase_items WHERE purchase_id=?",
                    (purchase_id,))
                items_sum = items_total[0][0] if items_total else 0
                new_total = items_sum + gst_val + exp_val

                self.db.execute_query("""
                    UPDATE purchases SET
                        invoice_number=?, bill_date=?, supplier_id=?,
                        transport=?, lr_no=?, gst_amount=?,
                        other_expenses=?, agent_name=?, total_amount=?
                    WHERE purchase_id=?
                """, (e_bill.get().strip(), db_date, sup_id,
                      e_transport.get().strip(), e_lr.get().strip(),
                      gst_val, exp_val, e_agent.get().strip(),
                      new_total, purchase_id))

                messagebox.showinfo("Saved", "Purchase updated successfully!", parent=dialog)
                dialog.destroy()
                self._load_purchases()
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to save: {ex}", parent=dialog)

        AnimatedButton(form, text="💾 Save Changes",
                       fg_color=config.COLOR_SUCCESS,
                       command=save).pack(pady=16, fill="x")

    # ── Delete Purchase ───────────────────────────────────────────────

    def _delete_selected(self):
        pid = self._get_selected_id()
        if not pid:
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete Purchase #{pid} and all its items?\n"
                                   "⚠ Inventory quantities will NOT be auto-restored.",
                                   parent=self):
            return
        try:
            self.db.execute_query(
                "DELETE FROM purchase_items WHERE purchase_id=?", (pid,))
            self.db.execute_query(
                "DELETE FROM purchases WHERE purchase_id=?", (pid,))
            messagebox.showinfo("Deleted", f"Purchase #{pid} deleted.", parent=self)
            self._load_purchases()
        except Exception as ex:
            messagebox.showerror("Error", f"Delete failed: {ex}", parent=self)

    # ── Print Invoice ─────────────────────────────────────────────────

    def _print_selected(self):
        pid = self._get_selected_id()
        if pid:
            self._print_invoice(pid)

    def _print_invoice(self, purchase_id):
        try:
            path = self.invoice_gen.generate_purchase_invoice(purchase_id)
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open invoice: {str(e)}", parent=self)
