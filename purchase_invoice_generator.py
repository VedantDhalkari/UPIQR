"""
Purchase Invoice Generator Module
Generates professional PDF invoices for Purchases using ReportLab 
with premium purple branding and perfectly separated tabular format.
"""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import config

PURPLE_COLOR = colors.HexColor('#5E2A7E')
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

class PurchaseInvoiceGenerator:
    """Handles PDF purchase invoice generation matching a perfect tabular format."""

    def __init__(self, db_manager):
        self.db = db_manager
        self.invoices_dir = Path.cwd() / config.INVOICES_DIR
        self.invoices_dir.mkdir(exist_ok=True)

    def generate_purchase_invoice(self, purchase_id: int) -> str:
        """
        Generate PDF invoice for a purchase.
        
        Args:
            purchase_id: Purchase ID from database
            
        Returns:
            Path to generated PDF file
        """
        # Get purchase details
        purchase_data = self.db.execute_query(
            """SELECT p.purchase_id, p.invoice_number, p.purchase_date, p.total_amount, 
                      p.gst_amount, p.other_expenses, p.notes, 
                      s.name, s.phone, s.address, s.gstin, p.bill_date, p.transport, p.lr_no
               FROM purchases p
               LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
               WHERE p.purchase_id = ?""",
            (purchase_id,)
        )[0]
        
        # Get purchase items
        items_data = self.db.execute_query(
            """SELECT sku_code, item_name, quantity, purchase_rate, total_amount, gst_percentage
               FROM purchase_items WHERE purchase_id = ?""",
            (purchase_id,)
        )
        
        invoice_data = {
            "bill_number": purchase_data[1] or f"PUR-{purchase_data[0]}",
            "date": purchase_data[11] or purchase_data[2][:10], 
            "supplier_name": purchase_data[7] or "Unknown Supplier", 
            "supplier_phone": purchase_data[8] or "N/A",
            "transport": purchase_data[12] or "N/A",
            "lr_no": purchase_data[13] or "N/A",
            "subtotal": purchase_data[3] - (purchase_data[4] + purchase_data[5]),
            "gst_amount": purchase_data[4],
            "other_expenses": purchase_data[5],
            "grand_total": purchase_data[3] + purchase_data[5] # Amount + Expenses
        }
        
        items = []
        for item in items_data:
            item_name = item[1]
            if item[2] < 0:
                item_name += " (Returned/Replaced)"
                
            items.append({
                "sku": item[0],
                "name": item_name,
                "qty": item[2],
                "rate": item[3],
                "gst_pct": item[5] or 0.0,
                "amount": item[4]
            })
            
        return self._create_pdf(invoice_data, items)
        
    def _create_pdf(self, data: dict, items: list) -> str:
        """Internal method to create PDF with the perfectly separated tabular layout."""
        bill_number = data["bill_number"]
        
        # We append a timestamp to purchase bills to avoid overwriting regular bills with the same ref ID
        safe_bill_no = "".join([c for c in str(bill_number) if c.isalnum() or c in ('-', '_')])
        filename = self.invoices_dir / f"Purchase_{safe_bill_no}_{datetime.now().strftime('%Y%m%d%H%M')}.pdf"
        filename = filename.resolve()

        doc = SimpleDocTemplate(
            str(filename),
            pagesize=A4,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        def draw_header_footer(canvas, doc):
            canvas.saveState()
            
            # Draw Header Box
            canvas.setStrokeColor(PURPLE_COLOR)
            canvas.setLineWidth(2)
            # Main outer border for the header
            header_y = A4[1] - 2 * inch
            canvas.rect(0.5 * inch, header_y, A4[0] - 1.0 * inch, 1.5 * inch, stroke=1, fill=0)
            
            # Title Background
            canvas.setFillColor(PURPLE_COLOR)
            canvas.rect(0.5 * inch, A4[1] - 0.8 * inch, A4[0] - 1.0 * inch, 0.3 * inch, stroke=1, fill=1)
            
            # Title Text
            canvas.setFillColor(colors.white)
            canvas.setFont(FONT_BOLD, 14)
            canvas.drawCentredString(A4[0] / 2.0, A4[1] - 0.72 * inch, "PURCHASE INVOICE / RECEIVING NOTE")
            
            # Logo
            import os, sys
            try:
                if hasattr(sys, '_MEIPASS'):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(base_path, config.LOGO_PATH)
                canvas.drawImage(logo_path, A4[0] - 1.6 * inch, header_y + 0.1 * inch, width=1.0 * inch, height=1.0 * inch, preserveAspectRatio=True)
            except Exception as e:
                print("Logo missing from Purchase PDF generation:", e)
                
            # Supplier Details
            canvas.setFillColor(PURPLE_COLOR)
            canvas.setFont(FONT_BOLD, 11)
            canvas.drawString(0.6 * inch, header_y + 1.0 * inch, "Supplier Name & Details:")
            
            canvas.setFont(FONT_REGULAR, 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(0.6 * inch, header_y + 0.8 * inch, f"Name: {data['supplier_name']}")
            canvas.drawString(0.6 * inch, header_y + 0.6 * inch, f"Phone: {data['supplier_phone']}")
            
            # Transport Details
            canvas.drawString(0.6 * inch, header_y + 0.4 * inch, f"Transport: {data['transport']}")
            canvas.drawString(0.6 * inch, header_y + 0.2 * inch, f"LR No.: {data['lr_no']}")
            
            # Vertical Separator Line
            mid_x = A4[0] / 2.0 + 1 * inch
            canvas.setStrokeColor(PURPLE_COLOR)
            canvas.setLineWidth(1)
            canvas.line(mid_x, header_y, mid_x, header_y + 1.2 * inch)
            
            # Invoice Details (Right Side)
            canvas.setFont(FONT_BOLD, 10)
            canvas.setFillColor(PURPLE_COLOR)
            canvas.drawString(mid_x + 0.1 * inch, header_y + 0.9 * inch, "Bill No.:")
            canvas.drawString(mid_x + 0.1 * inch, header_y + 0.6 * inch, "Bill Date:")
            
            canvas.setFont(FONT_REGULAR, 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(mid_x + 1.0 * inch, header_y + 0.9 * inch, str(data['bill_number']))
            canvas.drawString(mid_x + 1.0 * inch, header_y + 0.6 * inch, data['date'])

            # Footer
            footer_y = 0.5 * inch
            canvas.setFont(FONT_BOLD, 10)
            canvas.setFillColor(PURPLE_COLOR)
            canvas.drawString(0.5 * inch, footer_y + 0.2 * inch, "Generated by Shree Ganesha Silk Management System")
            
            canvas.restoreState()

        story = []
        styles = getSampleStyleSheet()
        
        # Push content down below header
        story.append(Spacer(1, 1.8 * inch))

        # Main Items and Totals Table
        # Columns: Sr.No, Particulars, SKU, Qty, Rate, GST %, Amount
        col_widths = [0.6 * inch, 2.5 * inch, 0.9 * inch, 0.6 * inch, 0.9 * inch, 0.7 * inch, 1.1 * inch]
        
        table_data = [
            ["Sr.", "Particulars", "SKU", "Qty", "Rate", "Rate (w/ GST)", "Amount"]
        ]

        MIN_ROWS = 15
        for idx, item in enumerate(items, 1):
            gst_pct = float(item['gst_pct'] or 0)
            rate_w_gst = item['rate'] * (1 + (gst_pct/100))
            
            table_data.append([
                str(idx),
                item["name"],
                item["sku"] or "",
                str(item["qty"]),
                f"{item['rate']:.2f}",
                f"{rate_w_gst:.2f}",
                f"{item['amount']:.2f}"
            ])
        
        # Fill empty rows for neat tabular structure
        rows_to_add = max(0, MIN_ROWS - len(items))
        for _ in range(rows_to_add):
            table_data.append(["", "", "", "", "", "", ""])

        # Totals section
        total_qty = sum(item["qty"] for item in items)
        total_distinct_items = len(items)
        
        has_tax_discount = data.get('gst_amount', 0) > 0 or data.get('other_expenses', 0) > 0
        
        totals_list = []
        totals_list.append(("Total Items", total_distinct_items))
        totals_list.append(("Total Qty", total_qty))
        
        if has_tax_discount:
            totals_list.append(("Sub Total", data.get('subtotal', 0)))
            if data.get('gst_amount', 0) > 0:
                totals_list.append(("GST Amount", data['gst_amount']))
            if data.get('other_expenses', 0) > 0:
                totals_list.append(("Other Expenses", data['other_expenses']))
                
        totals_list.append(("Grand Total", data['grand_total']))
        
        num_totals = len(totals_list)
        for label, val in totals_list:
            if label in ("Total Items", "Total Qty"):
                val_str = str(int(val))
            else:
                val_str = f"{val:.2f}"
            table_data.append(["", "", "", "", "", label, val_str])
            
        main_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        style_cmds = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Grid for perfectly separated lines
            ('GRID', (0, 0), (-1, -1), 1.0, PURPLE_COLOR),
            # Line separating header from rows
            ('LINEBELOW', (0, 0), (-1, 0), 2, PURPLE_COLOR),
            
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Alignments
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Sr
            ('ALIGN', (1, 1), (1, -(num_totals + 1)), 'LEFT'),    # Particulars
            ('ALIGN', (2, 1), (2, -(num_totals + 1)), 'CENTER'),  # SKU
            ('ALIGN', (3, 1), (3, -(num_totals + 1)), 'CENTER'),  # Qty
            ('ALIGN', (4, 1), (4, -(num_totals + 1)), 'RIGHT'),   # Rate
            ('ALIGN', (5, 1), (5, -(num_totals + 1)), 'CENTER'),  # GST
            ('ALIGN', (6, 1), (6, -(num_totals + 1)), 'RIGHT'),   # Amount
        ]
        
        for i in range(1, num_totals + 1):
            row_idx = -i
            style_cmds.extend([
                ('SPAN', (0, row_idx), (4, row_idx)),
                ('BACKGROUND', (5, row_idx), (5, row_idx), PURPLE_COLOR),
                ('TEXTCOLOR', (5, row_idx), (5, row_idx), colors.white),
                ('FONTNAME', (5, row_idx), (5, row_idx), FONT_BOLD),
                ('ALIGN', (5, row_idx), (5, row_idx), 'CENTER'),
                ('ALIGN', (-1, row_idx), (-1, row_idx), 'RIGHT'),
                ('FONTNAME', (-1, row_idx), (-1, row_idx), FONT_BOLD),
                ('BACKGROUND', (-1, row_idx), (-1, row_idx), colors.HexColor('#F3E8FF')), # Light purple highlight for total amount
            ])
        
        main_table.setStyle(TableStyle(style_cmds))
        story.append(main_table)

        doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
        
        return str(filename)
