"""
Global Search Module
Search across bills, customers, and inventory
"""

import customtkinter as ctk
from tkinter import messagebox
import config
import config
from ui_components import AnimatedButton, PageHeader


class GlobalSearchModule(ctk.CTkFrame):
    """Global search interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        # Prevent CustomTkinter from crashing on unknown navigation attributes
        kwargs.pop("current_user", None)
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Header
        PageHeader(self, title="🔍 Global Search").pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=config.BUTTON_HEIGHT_LG,
            placeholder_text="Search bills, customers, items, SKU codes...",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            border_color=config.COLOR_BORDER,
            border_width=2
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, config.SPACING_SM))
        
        search_btn = AnimatedButton(
            search_frame,
            text="🔍 Search",
            width=150,
            height=config.BUTTON_HEIGHT_LG,
            fg_color=config.COLOR_PRIMARY,
            hover_color=config.COLOR_PRIMARY_LIGHT,
            command=self._perform_search
        )
        search_btn.pack(side="left")
        
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Results area
        self.results_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.results_frame.pack(fill="both", expand=True)
        self.results_frame.configure(border_width=1, border_color=config.COLOR_BORDER)
        
        # Initial message
        self._show_initial_message()
    
    def _show_initial_message(self):
        """Show initial search message"""
        msg_label = ctk.CTkLabel(
            self.results_frame,
            text="🔍\n\nEnter a search term to find\nbills, customers, or inventory items",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
            text_color=config.COLOR_TEXT_SECONDARY,
            justify="center"
        )
        msg_label.pack(expand=True, pady=config.SPACING_XL * 2)
    
    def _perform_search(self):
        """Perform global search"""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search term")
            return
        
        # Clear results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Search bills
        self._create_section_header("Bills / Invoices", config.ICON_BILLING)
        
        bills = self.db.execute_query(
            """SELECT bill_number, customer_name, customer_phone, final_amount, sale_date
               FROM sales
               WHERE bill_number LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
               ORDER BY sale_date DESC LIMIT 10""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if bills:
            for bill in bills:
                self._create_bill_card(bill)
        else:
            self._create_no_results("No bills found")
        
        # Search inventory
        self._create_section_header("Inventory Items", config.ICON_INVENTORY)
        
        items = self.db.execute_query(
            """SELECT sku_code, saree_type, material, color, quantity, selling_price
               FROM inventory
               WHERE sku_code LIKE ? OR saree_type LIKE ? OR material LIKE ? OR color LIKE ? OR supplier_name LIKE ? OR category LIKE ?
               LIMIT 10""",
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if items:
            for item in items:
                self._create_item_card(item)
        else:
            self._create_no_results("No items found")
            
        # Search Purchases
        self._create_section_header("Purchases / GRNs", "📥")
        
        purchases = self.db.execute_query(
            """SELECT p.invoice_number, s.name, p.total_amount, p.purchase_date, p.notes
               FROM purchases p
               LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
               WHERE p.invoice_number LIKE ? OR s.name LIKE ? OR p.notes LIKE ?
               ORDER BY p.purchase_date DESC LIMIT 10""",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        
        if purchases:
            for purchase in purchases:
                self._create_purchase_card(purchase)
        else:
            self._create_no_results("No purchases found")

    
    def _create_section_header(self, title, icon):
        """Create section header"""
        header_label = ctk.CTkLabel(
            self.results_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_PRIMARY
        )
        header_label.pack(pady=(config.SPACING_LG, config.SPACING_SM), padx=config.SPACING_LG, anchor="w")
    
    def _create_bill_card(self, bill):
        """Create bill result card with actions"""
        bill_no = bill[0]
        name = bill[1] or "Walk-in Customer"
        phone = bill[2] or "N/A"
        amount = bill[3]
        date = bill[4][:10] if bill[4] else ""

        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_XS)
        
        # Info Column
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        # Row 1: Bill No & Amount (Bold)
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x")
        
        ctk.CTkLabel(
            row1, 
            text=f"Bill #{bill_no}", 
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_PRIMARY
        ).pack(side="left")
        
        ctk.CTkLabel(
            row1, 
            text=f"₹{amount:,.2f}", 
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_SUCCESS
        ).pack(side="right")
        
        # Row 2: Customer & Date
        row2 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row2.pack(fill="x", pady=(2, 0))
        
        ctk.CTkLabel(
            row2, 
            text=f"👤 {name}  |  📞 {phone}  |  📅 {date}", 
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(side="left")

        # Actions Column
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        # View Invoice Button
        view_btn = ctk.CTkButton(
            actions_frame,
            text="View Invoice",
            width=100,
            height=32,
            fg_color=config.COLOR_SECONDARY,
            hover_color=config.COLOR_SECONDARY_DARK,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            command=lambda b=bill_no: self._open_invoice(b)
        )
        view_btn.pack(side="right")
    
    def _open_invoice(self, bill_number):
        """Open the PDF invoice for a bill"""
        import os
        from pathlib import Path
        
        # Try to find the invoice
        invoice_path = Path.cwd() / config.INVOICES_DIR / f"{bill_number}.pdf"
        
        if invoice_path.exists():
            try:
                os.startfile(invoice_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open invoice: {e}")
        else:
            # Check if we can regenerate it (optional, for now just show error)
            messagebox.showinfo("Not Found", "Invoice PDF not found. It might not have been generated yet.")
    
    def _create_item_card(self, item):
        """Create item result card"""
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_XS)
        
        text = f"SKU: {item[0]} | {item[1]} - {item[2]} ({item[3]}) | Stock: {item[4]} | Price: ₹{item[5]:,.2f}"
        label = ctk.CTkLabel(
            card,
            text=text,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_PRIMARY
        )
        label.pack(pady=config.SPACING_SM, padx=config.SPACING_MD, anchor="w")

    def _create_purchase_card(self, purchase):
        """Create purchase result card"""
        inv_no = purchase[0] or "N/A"
        supplier = purchase[1] or "Unknown Supplier"
        amount = purchase[2] or 0.0
        date = purchase[3][:10] if purchase[3] else ""
        notes = purchase[4] or ""

        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=config.COLOR_BG_HOVER,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.pack(fill="x", padx=config.SPACING_LG, pady=config.SPACING_XS)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text=f"Inv: {inv_no}",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_PRIMARY
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame,
            text=f" • {date}",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(side="left")
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=f"Supplier: {supplier} | Notes: {notes[:30]}",
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        details_label.pack(anchor="w", pady=(2, 0))
        
        amount_frame = ctk.CTkFrame(card, fg_color="transparent")
        amount_frame.pack(side="right", padx=config.SPACING_MD, pady=config.SPACING_SM)
        
        ctk.CTkLabel(
            amount_frame,
            text=f"₹{amount:,.2f}",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_SUCCESS
        ).pack()

    def _create_no_results(self, message):
        """Create no results message"""
        label = ctk.CTkLabel(
            self.results_frame,
            text=message,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        )
        label.pack(padx=config.SPACING_LG, pady=config.SPACING_SM, anchor="w")
