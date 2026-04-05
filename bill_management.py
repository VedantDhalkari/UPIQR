"""
Bill Management Module
View, edit, and delete past bills
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import config
from ui_components import AnimatedButton, SearchBar, PageHeader
import os

class BillManagementModule(ctk.CTkFrame):
    """Bill management interface"""
    
    def __init__(self, parent, db_manager, invoice_generator, on_edit_sale=None, **kwargs):
        # Prevent CustomTkinter from crashing on unknown navigation attributes
        kwargs.pop("on_edit_bill", None) 
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        self.invoice_gen = invoice_generator
        self.on_edit_bill = on_edit_sale
        
        # Header
        PageHeader(self, title="🧾 Bill Management").pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Search bar
        search_bar = SearchBar(
            self,
            placeholder="Search by Bill No, Customer Name/Phone...",
            on_search=self._on_search
        )
        search_bar.pack(fill="x", pady=(0, config.SPACING_LG))
        self.search_entry = search_bar.entry
        
        # Action Buttons
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, config.SPACING_SM))
        
        ctk.CTkButton(self.action_frame, text="✏️ Edit / View", fg_color=config.COLOR_WARNING, command=self._edit_selected).pack(side="left", padx=5)
        ctk.CTkButton(self.action_frame, text="💳 Add Payment", fg_color=config.COLOR_SUCCESS, command=self._add_payment_selected).pack(side="left", padx=5)
        ctk.CTkButton(self.action_frame, text="🖨️ Reprint Invoice", fg_color=config.COLOR_SECONDARY, command=self._print_selected).pack(side="left", padx=5)
        ctk.CTkButton(self.action_frame, text="🗑 Delete Bill", fg_color=config.COLOR_DANGER, command=self._delete_selected).pack(side="left", padx=5)

        # Bills table (Treeview)
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
        
        style.configure("Bill.Treeview", background="white", foreground="black", rowheight=row_height, fieldbackground="white", font=("Arial", base_size))
        style.configure("Bill.Treeview.Heading", background=config.COLOR_PRIMARY, foreground="white", font=("Arial", base_size, "bold"))
        style.map("Bill.Treeview", background=[('selected', '#B4D5F0')])

        self.columns = ("sale_id", "bill_no", "date", "customer", "salesman", "items", "total", "method")
        self.tree = ttk.Treeview(tree_container, columns=self.columns, show="headings", style="Bill.Treeview")
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        headings = [
            ("sale_id", "ID", 0), # Hidden mostly or small
            ("bill_no", "Bill No", 100),
            ("date", "Date", 150),
            ("customer", "Customer", 180),
            ("salesman", "Salesman", 140),
            ("items", "Items", 80),
            ("total", "Total ₹", 100),
            ("method", "Payment Status", 110)
        ]
        
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center" if col != "customer" else "w")
            
        self.tree.column("sale_id", width=0, stretch=False) # Hide ID

        self.tree.bind("<Double-1>", lambda e: self._edit_selected())
        
        self._load_bills()
    
    def _on_search(self, query):
        """Handle search"""
        self._load_bills(query)
    
    def _load_bills(self, search_query=""):
        """Load bills data"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        query = """
            SELECT s.sale_id, s.bill_number, s.sale_date, s.customer_name, s.customer_phone,
                   s.final_amount, s.payment_status, COUNT(si.item_id) as item_count, s.salesman
            FROM sales s
            LEFT JOIN sale_items si ON s.sale_id = si.sale_id
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += """ AND (s.bill_number LIKE ? OR s.customer_name LIKE ? OR s.customer_phone LIKE ? OR s.salesman LIKE ?)"""
            params = [f"%{search_query}%"] * 4
            
        query += " GROUP BY s.sale_id ORDER BY s.sale_date DESC LIMIT 100"
        
        bills = self.db.execute_query(query, tuple(params))
        
        for bill in bills:
            sale_id = bill[0]
            bill_no = bill[1]
            date = bill[2][:16]
            customer = f"{bill[3] or 'Walk-in'} {('- ' + bill[4]) if bill[4] else ''}"
            amount = f"₹{bill[5]:.2f}"
            status = bill[6] or 'Paid'
            items = f"{bill[7]} Pcs"
            salesman_val = bill[8] or '-'
            
            self.tree.insert("", "end", values=(sale_id, bill_no, date, customer, salesman_val, items, amount, status))
            
    def _get_selected_sale(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a bill from the list first.")
            return None, None
        item = self.tree.item(sel[0])['values']
        return item[0], item[1] # sale_id, bill_no

    def _print_selected(self):
        sale_id, _ = self._get_selected_sale()
        if sale_id:
            try:
                path = self.invoice_gen.generate_invoice(sale_id)
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open invoice: {str(e)}")

    def _edit_selected(self):
        sale_id, _ = self._get_selected_sale()
        if sale_id and self.on_edit_bill:
            self.on_edit_bill(sale_id)

    def _add_payment_selected(self):
        sale_id, bill_no = self._get_selected_sale()
        if not sale_id: return
        
        # Get bill details
        res = self.db.execute_query("SELECT final_amount, amount_paid, balance_due FROM sales WHERE sale_id=?", (sale_id,))
        if not res: return
        total, paid, balance = res[0]
        
        if balance <= 0:
            messagebox.showinfo("Fully Paid", f"Bill {bill_no} is already fully paid.")
            return
            
        d = ctk.CTkToplevel(self)
        d.title(f"Add Payment - {bill_no}")
        d.geometry("400x400")
        d.transient(self.winfo_toplevel())
        d.grab_set()
        
        ctk.CTkLabel(d, text=f"Record Payment for {bill_no}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(d, text=f"Balance Due: ₹{balance:,.2f}", text_color=config.COLOR_DANGER, font=ctk.CTkFont(size=14)).pack(pady=(0,15))
        
        form = ctk.CTkFrame(d, fg_color="transparent")
        form.pack(fill="x", padx=20)
        
        # Amount
        ctk.CTkLabel(form, text="Payment Amount (₹)*", anchor="w").pack(fill="x")
        amt_entry = ctk.CTkEntry(form)
        amt_entry.insert(0, str(balance))
        amt_entry.pack(fill="x", pady=(0,10))
        
        # Method
        ctk.CTkLabel(form, text="Payment Method*", anchor="w").pack(fill="x")
        method_combo = ctk.CTkComboBox(form, values=["Cash", "UPI", "Card", "Bank Transfer"])
        method_combo.pack(fill="x", pady=(0,10))
        
        # Note
        ctk.CTkLabel(form, text="Activity Note", anchor="w").pack(fill="x")
        note_entry = ctk.CTkEntry(form, placeholder_text="e.g. Partial clearing, Final settlement")
        note_entry.pack(fill="x", pady=(0,20))
        
        def save():
            try:
                p_amt = float(amt_entry.get())
                if p_amt <= 0: raise ValueError
                if p_amt > balance:
                    if not messagebox.askyesno("Confirm", "Amount entered is greater than balance due. Add anyway?"):
                        return
                        
                new_paid = paid + p_amt
                new_balance = max(0, total - new_paid)
                status = "Paid" if new_balance <= 0 else "Partial"
                
                # Insert History
                self.db.execute_insert(
                    "INSERT INTO payment_history (sale_id, amount_paid, payment_method, activity_note) VALUES (?, ?, ?, ?)",
                    (sale_id, p_amt, method_combo.get(), note_entry.get() or "Manual Payment")
                )
                
                # Update Sales Record
                self.db.execute_query(
                    "UPDATE sales SET amount_paid=?, balance_due=?, payment_status=? WHERE sale_id=?",
                    (new_paid, new_balance, status, sale_id)
                )
                
                messagebox.showinfo("Success", "Payment recorded successfully!")
                self._load_bills(self.search_entry.get())
                d.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive amount.")
                
        ctk.CTkButton(d, text="Save Payment", fg_color=config.COLOR_SUCCESS, command=save).pack(pady=10)

    def _delete_selected(self):
        _, bill_no = self._get_selected_sale()
        if not bill_no: return
        
        if messagebox.askyesno("Confirm Delete", f"Delete Bill {bill_no}?\n\nThis will revert stock and cannot be undone."):
            try:
                self.db.delete_bill(bill_number=bill_no) 
                messagebox.showinfo("Success", "Bill deleted successfully.")
                self._load_bills(self.search_entry.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")
