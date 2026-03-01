"""
Reports Module
Sales analytics and reporting with premium visualizations
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import tkinter
import config
from charts import EarningsBarChart
from ui_components import PageHeader, AnimatedButton
import csv
from tkinter import messagebox, filedialog, ttk
from tkcalendar import DateEntry
import os


class ReportsModule(ctk.CTkFrame):
    """Reports and analytics interface"""
    
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.db = db_manager
        
        # Header
        PageHeader(self, title="📈 Reports & Analytics").pack(fill="x", pady=(0, config.SPACING_LG))
        
        # Period selector
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        ctk.CTkLabel(
            selector_frame,
            text="Select Period:",
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, config.SPACING_SM))
        
        self.period_var = tkinter.StringVar(value="week")
        
        ctk.CTkRadioButton(
            selector_frame,
            text="Today",
            variable=self.period_var,
            value="today",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        ctk.CTkRadioButton(
            selector_frame,
            text="This Week",
            variable=self.period_var,
            value="week",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        ctk.CTkRadioButton(
            selector_frame,
            text="This Month",
            variable=self.period_var,
            value="month",
            fg_color=config.COLOR_PRIMARY,
            command=self._load_reports
        ).pack(side="left", padx=config.SPACING_SM)
        
        # Date Range Filter
        date_frame = ctk.CTkFrame(selector_frame, fg_color="transparent")
        date_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(date_frame, text="Start Date:", font=("Arial", config.FONT_SIZE_BODY)).pack(side="left")
        self.start_date_entry = DateEntry(date_frame, width=12, background=config.COLOR_PRIMARY,
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.start_date_entry.pack(side="left", padx=(config.SPACING_SM, 2))
        
        ctk.CTkLabel(date_frame, text="End Date:", font=("Arial", config.FONT_SIZE_BODY)).pack(side="left", padx=(10, 2))
        self.end_date_entry = DateEntry(date_frame, width=12, background=config.COLOR_PRIMARY,
                                        foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.end_date_entry.pack(side="left", padx=2)
        
        ctk.CTkButton(
            selector_frame,
            text="Go",
            width=50,
            fg_color=config.COLOR_SECONDARY,
            command=lambda: self._load_reports(custom=True)
        ).pack(side="left", padx=config.SPACING_SM)
        
        
        # Export Buttons
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        ctk.CTkLabel(
            export_frame, 
            text="Export Data:", 
            font=ctk.CTkFont(size=config.FONT_SIZE_BODY, weight="bold")
        ).pack(side="left", padx=(0, config.SPACING_SM))
        
        ctk.CTkButton(
            export_frame,
            text="📥 Export Sales",
            fg_color=config.COLOR_SUCCESS,
            height=30,
            command=self._export_sales
        ).pack(side="left", padx=config.SPACING_SM)
        
        ctk.CTkButton(
            export_frame,
            text="📥 Export Stock",
            fg_color=config.COLOR_INFO,
            height=30,
            command=self._export_stock
        ).pack(side="left", padx=config.SPACING_SM)

        # Reports content
        self.reports_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        self.reports_frame.pack(fill="both", expand=True)
        
        self._load_reports()
    
    def _export_csv(self, filename, headers, data):
        """Helper to export data to CSV"""
        try:
            # Ask user for location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"{filename}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(data)
                
            messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
            os.startfile(os.path.dirname(file_path))
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    def _export_sales(self):
        """Export sales history"""
        headers = ["Bill No", "Date", "Customer Name", "Phone", "Items", "Amount", "Method", "Created By"]
        data = self.db.execute_query(
            """SELECT s.bill_number, s.sale_date, s.customer_name, s.customer_phone, 
               COUNT(si.item_id), s.final_amount, s.payment_method, s.created_by
               FROM sales s
               LEFT JOIN sale_items si ON s.sale_id = si.sale_id
               GROUP BY s.sale_id
               ORDER BY s.sale_date DESC"""
        )
        self._export_csv("sales_report", headers, data)

    def _export_stock(self):
        """Export inventory data"""
        headers = ["SKU", "Type", "Material", "Color", "Design", "Qty", "Purchase Price", "Selling Price", "Supplier", "Category", "Last Updated"]
        data = self.db.execute_query(
            """SELECT sku_code, saree_type, material, color, design, quantity, 
               purchase_price, selling_price, supplier_name, category, last_updated
               FROM inventory ORDER BY sku_code"""
        )
        self._export_csv("stock_inventory", headers, data)

    def _load_reports(self, custom=False):
        """Load reports for selected period"""
        # Clear content
        for widget in self.reports_frame.winfo_children():
            widget.destroy()
        
        period = self.period_var.get()
        start_date = None
        end_date = None
        
        if custom:
            try:
                s_txt = self.start_date_entry.get()
                e_txt = self.end_date_entry.get()
                # Basic validation
                datetime.strptime(s_txt, "%Y-%m-%d")
                datetime.strptime(e_txt, "%Y-%m-%d")
                start_date = s_txt
                end_date = e_txt
                self.period_var.set("custom") # Uncheck others
                period_label = f"{s_txt} to {e_txt}"
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        else:
             # Existing logic for predefined periods
             if period == "today":
                start_date = datetime.now().strftime("%Y-%m-%d")
                end_date = start_date
                period_label = "Today"
             elif period == "week":
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
                period_label = "This Week"
             else: # month
                start_date = datetime.now().strftime("%Y-%m-01")
                end_date = datetime.now().strftime("%Y-%m-%d")
                period_label = "This Month"
        
        # Store for export (optional, not implemented yet but good practice)
        self.current_start_date = start_date
        self.current_end_date = end_date
        
        # Summary metrics
        metrics_frame = ctk.CTkFrame(self.reports_frame, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, config.SPACING_LG))
        
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Get period data
        
        # Get period data
        sales_data = self.db.execute_query(
            """SELECT COUNT(*), COALESCE(SUM(final_amount), 0), 
               COALESCE(AVG(final_amount), 0)
               FROM sales 
               WHERE DATE(sale_date) BETWEEN ? AND ?""",
            (start_date, end_date)
        )[0]
        
        # Create metric cards
        self._create_metric_card(
            metrics_frame, 0, "Total Sales", 
            f"₹{sales_data[1]:,.2f}", config.COLOR_PRIMARY
        )
        self._create_metric_card(
            metrics_frame, 1, "Transactions", 
            str(sales_data[0]), config.COLOR_SUCCESS
        )
        self._create_metric_card(
            metrics_frame, 2, "Average Sale", 
            f"₹{sales_data[2]:,.2f}", config.COLOR_INFO
        )
        
        # Total items sold
        total_items = self.db.execute_query(
            """SELECT COALESCE(SUM(si.quantity), 0)
               FROM sale_items si
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?""",
            (start_date, end_date)
        )[0][0]
        
        self._create_metric_card(
            metrics_frame, 3, "Items Sold", 
            str(total_items), config.COLOR_WARNING
        )
        
        # Earnings chart
        # Earnings chart - Need date range logic in DB or here
        # For custom range, we can pass "custom" and dates, but existing method takes period string
        # We will reuse "week" logic (daily breakdown) for custom if range is small, or "month" (daily)
        # Actually simplest is to reuse get_sales_by_period but allowing custom dates
        # I'll modify the chart data fetching logic manually here since I don't want to change DB signature right now
        
        chart_query = """SELECT DATE(sale_date) as day, SUM(final_amount)
                   FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?
                   GROUP BY day ORDER BY day"""
        sales_time_data = self.db.execute_query(chart_query, (start_date, end_date))
        if sales_time_data:
            chart_data = [(label or "N/A", amount or 0) for label, amount in sales_time_data]
        else:
            chart_data = []
        
        earnings_chart = EarningsBarChart(
            self.reports_frame,
            data=chart_data,
            period=period_label
        )
        earnings_chart.pack(fill="both", expand=True, pady=(0, config.SPACING_LG))
        
        # Top selling items
        top_items_frame = ctk.CTkFrame(
            self.reports_frame,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_LG,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        top_items_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            top_items_frame,
            text="Top Selling Items",
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_3, weight="bold"),
            text_color=config.COLOR_TEXT_PRIMARY
        ).pack(pady=config.SPACING_LG, padx=config.SPACING_LG, anchor="w")
        
        # Get top items
        top_items = self.db.execute_query(
            """SELECT si.item_name, SUM(si.quantity) as qty, SUM(si.total_price) as total
               FROM sale_items si
               JOIN sales s ON si.sale_id = s.sale_id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?
               GROUP BY si.item_name
               ORDER BY qty DESC
               LIMIT 10""",
            (start_date, end_date)
        )
        
        scroll_frame = ctk.CTkScrollableFrame(
            top_items_frame,
            fg_color="transparent",
            scrollbar_button_color=config.COLOR_PRIMARY
        )
        scroll_frame.pack(fill="both", expand=True, padx=config.SPACING_LG, 
                         pady=(0, config.SPACING_LG))
        
        if top_items:
            for idx, (item_name, qty, total) in enumerate(top_items):
                bg = config.COLOR_BG_HOVER if idx % 2 == 0 else "transparent"
                item_frame = ctk.CTkFrame(scroll_frame, fg_color=bg)
                item_frame.pack(fill="x", pady=1)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"{idx+1}. {item_name}",
                    font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                    text_color=config.COLOR_TEXT_PRIMARY
                ).pack(side="left", padx=config.SPACING_MD, pady=config.SPACING_SM)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"Qty: {qty} | Total: ₹{total:,.2f}",
                    font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
                    text_color=config.COLOR_TEXT_SECONDARY
                ).pack(side="right", padx=config.SPACING_MD, pady=config.SPACING_SM)
        else:
            ctk.CTkLabel(
                scroll_frame,
                text="No sales data available",
                font=ctk.CTkFont(size=config.FONT_SIZE_BODY),
                text_color=config.COLOR_TEXT_SECONDARY
            ).pack(pady=config.SPACING_XL)
    
    def _create_metric_card(self, parent, column, title, value, color):
        """Create a metric card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=config.COLOR_BG_CARD,
            corner_radius=config.RADIUS_MD,
            border_width=1,
            border_color=config.COLOR_BORDER
        )
        card.grid(row=0, column=column, padx=config.SPACING_XS if column < 3 else 0, sticky="ew")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=config.FONT_SIZE_SMALL),
            text_color=config.COLOR_TEXT_SECONDARY
        ).pack(pady=(config.SPACING_MD, config.SPACING_XS))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=config.FONT_SIZE_HEADING_2, weight="bold"),
            text_color=color
        ).pack(pady=(0, config.SPACING_MD))
