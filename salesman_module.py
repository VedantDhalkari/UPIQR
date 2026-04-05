"""
Salesman Master Module
Full CRUD for salesmen — premium two-pane layout with unique number support
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import config
from ui_components import AnimatedButton, PageHeader
from datetime import datetime


class SalesmanMasterModule(ctk.CTkFrame):
    """Salesman master interface — premium two-pane layout with full CRUD"""

    def __init__(self, parent, db_manager, **kwargs):
        # Safely remove common navigation keywords before passing to super()
        kwargs.pop("current_user", None)
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.db = db_manager
        self.selected_salesman_id = None

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

        PageHeader(hdr_row, title="👔 Salesman Master").pack(side="left")

        ctk.CTkLabel(
            hdr_row,
            text="Ctrl+N = New  |  F5 = Refresh  |  Del = Delete  |  Enter/Dbl-Click = Edit",
            font=("Arial", self.font_sm), text_color="gray"
        ).pack(side="left", padx=20)

        AnimatedButton(
            hdr_row, text="+ New Salesman [Ctrl+N]",
            width=170, height=34,
            fg_color=config.COLOR_SUCCESS,
            command=self._open_salesman_form
        ).pack(side="right", padx=config.SPACING_SM)

        # ── Main two-pane layout ──────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # Left: Salesman list
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
        self.search_var.trace_add("write", lambda *a: self._load_salesmen())
        ctk.CTkEntry(
            search_row, textvariable=self.search_var,
            placeholder_text="🔍  Search by name, phone or unique no...",
            height=34,
            font=("Arial", self.font_md)
        ).pack(fill="x")

        # ── Treeview with explicit fresh style ────────────────────────
        cols = ("id", "unique_number", "name", "phone", "status")
        tree_frame = ctk.CTkFrame(list_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Use a UNIQUE style name to avoid collision with Billing.Treeview
        style = ttk.Style()
        row_height = max(int(self.base_size * 2.5), 24)
        # Apply style AFTER theme — we force our own style independently
        style.configure(
            "SalesmanV2.Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            rowheight=row_height,
            fieldbackground="#FFFFFF",
            font=("Arial", self.base_size),
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "SalesmanV2.Treeview.Heading",
            background=config.COLOR_PRIMARY,
            foreground="white",
            font=("Arial", self.base_size, "bold"),
            relief="flat",
            padding=(4, 6)
        )
        style.map("SalesmanV2.Treeview",
                  background=[('selected', '#BFDBFE')],
                  foreground=[('selected', '#1E3A8A')])
        style.map("SalesmanV2.Treeview.Heading",
                  background=[('active', config.COLOR_PRIMARY_DARK)])

        self.tree = ttk.Treeview(
            tree_frame, columns=cols, show="headings",
            height=20, style="SalesmanV2.Treeview"
        )
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        col_cfg = [
            ("id",            "ID",            0,   "center"),
            ("unique_number", "Unique No.",    100, "center"),
            ("name",          "Salesman Name", 200, "w"),
            ("phone",         "Phone",         130, "center"),
            ("status",        "Status",        80,  "center"),
        ]
        for col, hdr, w, anch in col_cfg:
            self.tree.heading(col, text=hdr, anchor="center")
            self.tree.column(col, width=w, anchor=anch, minwidth=w if w > 0 else 0)
        self.tree.column("id", width=0, stretch=False, minwidth=0)

        # Row color tags — use background/foreground ONLY (not reliant on theme)
        self.tree.tag_configure('active',   foreground="#166534", background="#F0FDF4")
        self.tree.tag_configure('inactive', foreground="#9CA3AF", background="#F9FAFB")
        self.tree.tag_configure('even',     background="#F8FAFC", foreground="#1E293B")
        self.tree.tag_configure('odd',      background="#FFFFFF", foreground="#1E293B")

        self.tree.bind("<<TreeviewSelect>>", self._on_salesman_select)
        self.tree.bind("<Double-1>", lambda e: self._open_salesman_form(edit=True))
        self.tree.bind("<Return>",   lambda e: self._open_salesman_form(edit=True))
        self.tree.bind("<Delete>",   lambda e: self._delete_salesman())

        # Right: Detail panel
        self.detail_card = ctk.CTkScrollableFrame(
            body, fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1, border_color=config.COLOR_BORDER
        )
        self.detail_card.grid(row=0, column=1, sticky="nsew")

        self._show_placeholder()
        self._load_salesmen()

        # Global shortcuts
        self.after(100, self._bind_shortcuts)

    def _bind_shortcuts(self):
        try:
            top = self.winfo_toplevel()
            top.bind("<Control-n>", lambda e: self._open_salesman_form(), add="+")
            top.bind("<F5>",        lambda e: self._load_salesmen(), add="+")
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
            text="👔\n\nSelect a salesman\nto view details",
            text_color="gray",
            font=("Arial", self.font_lg)
        ).pack(pady=60)

    # ── Data ──────────────────────────────────────────────────────────
    def _load_salesmen(self):
        q = self.search_var.get().strip()
        try:
            if q:
                rows = self.db.execute_query(
                    """SELECT salesman_id, unique_number, name, phone, status
                       FROM salesmen
                       WHERE name LIKE ? OR phone LIKE ? OR unique_number LIKE ?
                       ORDER BY name""",
                    (f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                rows = self.db.execute_query(
                    "SELECT salesman_id, unique_number, name, phone, status FROM salesmen ORDER BY name")
            # If we get here, unique_number column exists
            self._has_unique_no_column = True
        except Exception:
            # Fallback if column missing
            self._has_unique_no_column = False
            try:
                rows = self.db.execute_query(
                    "SELECT salesman_id, '' AS unique_number, name, phone, status FROM salesmen ORDER BY name")
            except:
                rows = []

        for r in self.tree.get_children():
            self.tree.delete(r)

        for idx, row in enumerate(rows or []):
            # row = (salesman_id, unique_number, name, phone, status)
            status = row[4] if len(row) > 4 else "Active"
            if status == "Active":
                tag = 'active'
            else:
                tag = 'inactive'
            self.tree.insert("", "end", values=row, tags=(tag,))

    def _on_salesman_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        if not vals:
            return
        self.selected_salesman_id = vals[0]
        self._load_detail_panel(vals[0])

    def _fetch_salesman(self, s_id):
        """Fetch salesman safely, handling schema with or without unique_number."""
        try:
            res = self.db.execute_query(
                """SELECT salesman_id, name, phone, address, joined_date, status, unique_number
                   FROM salesmen WHERE salesman_id = ?""", (s_id,))
        except:
            try:
                res = self.db.execute_query(
                    "SELECT salesman_id, name, phone, address, joined_date, status FROM salesmen WHERE salesman_id = ?",
                    (s_id,))
            except:
                res = []
        return res[0] if res else None

    def _load_detail_panel(self, s_id):
        for w in self.detail_card.winfo_children():
            w.destroy()

        s = self._fetch_salesman(s_id)
        if not s:
            return

        # s: (0=id, 1=name, 2=phone, 3=address, 4=joined_date, 5=status, 6=unique_number[optional])
        def _safe(idx):
            try:
                return s[idx] if len(s) > idx else None
            except:
                return None

        # ── Name header ───────────────────────────────────────────────
        status = _safe(5) or "Active"
        status_color = config.COLOR_SUCCESS if status == "Active" else "gray"
        unique_num = _safe(6)  # index 6 = unique_number

        ctk.CTkLabel(
            self.detail_card, text=_safe(1) or "Unknown",
            font=("Arial", self.font_xxl, "bold"),
            text_color=config.COLOR_PRIMARY
        ).pack(pady=(16, 2), padx=12, anchor="w")

        ctk.CTkLabel(
            self.detail_card, text=f"Status: {status}",
            font=("Arial", self.font_md, "bold"),
            text_color=status_color
        ).pack(anchor="w", padx=12, pady=(0, 4))

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=6)

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

        if unique_num:
            _row("🔢", "Unique No.", unique_num)
        _row("📞", "Phone",   _safe(2))
        _row("📍", "Address", _safe(3))
        if _safe(4):
            _row("📅", "Joined", str(_safe(4))[:10])

        ctk.CTkFrame(self.detail_card, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=8)

        # ── Sales History & Filters ───────────────────────────────────
        filter_f = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        filter_f.pack(fill="x", padx=12, pady=4)
        
        ctk.CTkLabel(filter_f, text="📅 Date Filter (DD-MM-YYYY):", font=("Arial", self.font_md, "bold")).pack(anchor="w")
        
        entry_f = ctk.CTkFrame(filter_f, fg_color="transparent")
        entry_f.pack(fill="x", pady=4)
        
        self.salesman_start_date = ctk.CTkEntry(entry_f, width=110, placeholder_text="Start Date")
        self.salesman_start_date.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(entry_f, text="to").pack(side="left", padx=5)
        
        self.salesman_end_date = ctk.CTkEntry(entry_f, width=110, placeholder_text="End Date")
        self.salesman_end_date.pack(side="left", padx=5)
        
        def apply_filter():
            self._refresh_salesman_history(_safe(1))
            
        AnimatedButton(entry_f, text="🔍 Filter", width=70, height=28, fg_color=config.COLOR_PRIMARY, command=apply_filter).pack(side="left", padx=10)
        
        self.history_frame = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        self.history_frame.pack(fill="both", expand=True, pady=10)
        
        self._refresh_salesman_history(_safe(1))

        # ── Action Buttons ────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)
        AnimatedButton(
            btn_row, text="✏️ Edit [Enter]", width=120, height=34,
            fg_color=config.COLOR_WARNING,
            command=lambda: self._open_salesman_form(edit=True)
        ).pack(side="left", padx=(0, 6))
        AnimatedButton(
            btn_row, text="🗑️ Delete [Del]", width=120, height=34,
            fg_color=config.COLOR_DANGER,
            command=self._delete_salesman
        ).pack(side="left")

    def _refresh_salesman_history(self, salesman_name):
        for w in self.history_frame.winfo_children():
            w.destroy()
            
        if not salesman_name:
            return
            
        start_val = self.salesman_start_date.get().strip()
        end_val = self.salesman_end_date.get().strip()
        
        date_query = ""
        params = [salesman_name]
        
        try:
            if start_val:
                dt_start = datetime.strptime(start_val, "%d-%m-%Y")
                date_query += " AND sale_date >= ?"
                params.append(dt_start.strftime("%Y-%m-%d 00:00:00"))
            if end_val:
                dt_end = datetime.strptime(end_val, "%d-%m-%Y")
                date_query += " AND sale_date <= ?"
                params.append(dt_end.strftime("%Y-%m-%d 23:59:59"))
        except ValueError:
            messagebox.showerror("Invalid Date", "Please use DD-MM-YYYY format (e.g., 31-12-2023)")
            return
            
        # ── Sales summary ─────────────────────────────────────────────
        try:
            summary = self.db.execute_query(
                f"""SELECT COUNT(*), COALESCE(SUM(final_amount), 0)
                   FROM sales WHERE salesman = ? {date_query}""",
                tuple(params))
            if summary and summary[0][0] > 0:
                total_bills, total_amount = summary[0]
                stats_f = ctk.CTkFrame(self.history_frame, fg_color=config.COLOR_PRIMARY, corner_radius=8)
                stats_f.pack(fill="x", padx=12, pady=(0, 8))
                ctk.CTkLabel(
                    stats_f,
                    text=f"📊 Total Bills: {total_bills}   |   Total Sales: \u20B9{total_amount:,.2f}",
                    font=("Arial", self.font_lg, "bold"), text_color="white"
                ).pack(pady=10, padx=12)
        except Exception as e:
            print(f"Summary query error: {e}")

        # ── Recent Sales ──────────────────────────────────────────────
        ctk.CTkLabel(
            self.history_frame, text="🧾 Filtered Sales (Up to 50)",
            font=("Arial", self.font_xl, "bold"), text_color=config.COLOR_PRIMARY
        ).pack(anchor="w", padx=12, pady=(0, 4))

        try:
            sales = self.db.execute_query(
                f"""SELECT sale_date, bill_number, final_amount FROM sales
                   WHERE salesman = ? {date_query} ORDER BY sale_date DESC LIMIT 50""",
                tuple(params)) or []
        except Exception as e:
            print(f"Sales query error: {e}")
            sales = []

        if sales:
            for idx, sl in enumerate(sales):
                date_str = str(sl[0])[:16] if sl[0] else "N/A" # Include time
                f = ctk.CTkFrame(self.history_frame, fg_color="#F8FAFC" if idx % 2 == 0 else "white", corner_radius=6)
                f.pack(fill="x", padx=12, pady=1)
                ctk.CTkLabel(
                    f, text=f"📅 {date_str}  |  Bill: {sl[1]}  |  \u20B9{sl[2]:,.2f}",
                    font=("Arial", self.font_md)
                ).pack(side="left", padx=8, pady=4)
        else:
            ctk.CTkLabel(
                self.history_frame, text="No sales recorded for this period.",
                font=("Arial", self.font_sm), text_color="gray"
            ).pack(padx=12, anchor="w")
            
        ctk.CTkFrame(self.history_frame, height=1, fg_color=config.COLOR_BORDER).pack(fill="x", padx=12, pady=8)

    # ── Form ──────────────────────────────────────────────────────────
    def _open_salesman_form(self, edit=False):
        existing = None
        if edit:
            if not self.selected_salesman_id:
                messagebox.showwarning("Select Salesman", "Please select a salesman first.")
                return
            existing = self._fetch_salesman(self.selected_salesman_id)

        d = ctk.CTkToplevel(self)
        d.title("Edit Salesman" if edit else "New Salesman")
        d.geometry("440x520")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        d.update_idletasks()
        sw = d.winfo_screenwidth(); sh = d.winfo_screenheight()
        d.geometry(f"+{(sw - 440) // 2}+{(sh - 520) // 2}")

        # Header strip
        hdr = ctk.CTkFrame(d, fg_color=config.COLOR_PRIMARY, corner_radius=0, height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr,
            text="✏️ Edit Salesman" if edit else "➕ New Salesman",
            font=("Arial", self.font_xxl, "bold"),
            text_color="white"
        ).pack(side="left", padx=16, pady=10)

        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        # existing: (0=id, 1=name, 2=phone, 3=address, 4=joined_date, 5=status, 6=unique_number)
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

        e_name   = _field("Salesman Name *", 1, "Full name")
        e_unique = _field("Unique No. / Employee ID", 6, "e.g. S-001  (must be unique)")
        e_phone  = _field("Phone Number",    2, "10-digit mobile")
        e_addr   = _field("Address",         3)

        # Status combo
        ctk.CTkLabel(scroll, text="Status", font=("Arial", self.font_md, "bold")).pack(anchor="w")
        status_combo = ctk.CTkComboBox(
            scroll, height=34,
            font=("Arial", self.font_md),
            values=["Active", "Inactive"]
        )
        existing_status = existing[5] if existing and len(existing) > 5 and existing[5] else "Active"
        status_combo.set(existing_status)
        status_combo.pack(fill="x", pady=(0, 8))

        def save():
            name = e_name.get().strip()
            unique_no = e_unique.get().strip() or None  # store NULL if empty
            phone = e_phone.get().strip()
            addr  = e_addr.get().strip()
            status = status_combo.get()

            if not name:
                messagebox.showerror("Error", "Salesman name is required.", parent=d)
                return

            try:
                has_col = getattr(self, '_has_unique_no_column', True)
                if edit and existing:
                    if has_col:
                        self.db.execute_query(
                            """UPDATE salesmen SET name=?, phone=?, address=?, status=?, unique_number=?
                               WHERE salesman_id=?""",
                            (name, phone, addr, status, unique_no, existing[0]))
                    else:
                        self.db.execute_query(
                            "UPDATE salesmen SET name=?, phone=?, address=?, status=? WHERE salesman_id=?",
                            (name, phone, addr, status, existing[0]))
                else:
                    if has_col:
                        self.db.execute_query(
                            """INSERT INTO salesmen (name, phone, address, status, unique_number)
                               VALUES (?, ?, ?, ?, ?)""",
                            (name, phone, addr, status, unique_no))
                    else:
                        self.db.execute_query(
                            "INSERT INTO salesmen (name, phone, address, status) VALUES (?, ?, ?, ?)",
                            (name, phone, addr, status))
                messagebox.showinfo("Saved", "Salesman saved successfully!", parent=d)
                d.destroy()
                self._load_salesmen()
            except Exception as ex:
                err = str(ex)
                if "unique_number" in err and "no such column" in err.lower():
                    # Last resort fallback save
                    self._has_unique_no_column = False
                    save() # retry
                    return
                if "UNIQUE constraint failed: salesmen.unique_number" in err:
                    messagebox.showerror("Error", f"Unique No. '{unique_no}' is already used by another salesman.", parent=d)
                elif "UNIQUE constraint failed: salesmen.name" in err:
                    messagebox.showerror("Error", f"A salesman named '{name}' already exists.", parent=d)
                else:
                    messagebox.showerror("Error", f"Save failed: {err}", parent=d)

        AnimatedButton(
            scroll, text="💾 Save [Ctrl+S / Enter]",
            height=38, fg_color=config.COLOR_SUCCESS, command=save
        ).pack(fill="x", pady=12)

        d.bind("<Return>",    lambda e: save())
        d.bind("<Control-s>", lambda e: save())
        e_name.focus_set()

    # ── Delete ────────────────────────────────────────────────────────
    def _delete_salesman(self):
        if not self.selected_salesman_id:
            messagebox.showwarning("Select Salesman", "Please select a salesman first.")
            return
        res = self.db.execute_query(
            "SELECT name FROM salesmen WHERE salesman_id = ?",
            (self.selected_salesman_id,))
        name = res[0][0] if res else "this salesman"

        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{name}'?\n\nNote: Their sales history will remain intact."
        ):
            try:
                self.db.execute_query(
                    "DELETE FROM salesmen WHERE salesman_id = ?",
                    (self.selected_salesman_id,))
                self.selected_salesman_id = None
                self._show_placeholder()
                self._load_salesmen()
            except Exception as ex:
                messagebox.showerror("Error", f"Delete failed: {ex}")
