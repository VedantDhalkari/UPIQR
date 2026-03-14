"""
Invoice Generator Module
Generates professional PDF invoices using ReportLab with premium purple branding,
matching the exact format of the provided image template.
"""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import config

# --- Configuration & Font Setup ---
# Define the custom purple color from the template image
PURPLE_COLOR = colors.HexColor('#5E2A7E')

# NOTE: To render Marathi text correctly, you must have a Unicode-compliant
# font supporting Devanagari script (e.g., 'NotoSansDevanagari-Regular.ttf')
# placed in a 'fonts' directory within your project.
#
# Uncomment the following lines and ensure the font file exists.
# If the font is not found, the Marathi text will not render correctly.

# try:
#     pdfmetrics.registerFont(TTFont('Marathi', 'fonts/NotoSansDevanagari-Regular.ttf'))
#     pdfmetrics.registerFont(TTFont('Marathi-Bold', 'fonts/NotoSansDevanagari-Bold.ttf'))
#     FONT_REGULAR = 'Marathi'
#     FONT_BOLD = 'Marathi-Bold'
# except Exception as e:
#     print(f"Warning: Could not load Marathi font. Using fallback. Error: {e}")
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'


class InvoiceGenerator:
    """Handles PDF invoice generation matching a specific template."""

    def __init__(self, db_manager):
        """
        Initialize invoice generator.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        # Use absolute path for invoices directory
        self.invoices_dir = Path.cwd() / config.INVOICES_DIR
        self.invoices_dir.mkdir(exist_ok=True)

    def generate_invoice(self, sale_id: int) -> str:
        """
        Generate PDF invoice for a sale.

        Args:
            sale_id: Sale ID from database

        Returns:
            Path to generated PDF file
        """
        # Get sale details (Fetching logic remains the same)
        sale_data = self.db.execute_query(
            """SELECT bill_number, customer_name, customer_phone, total_amount,
               discount_percent, discount_amount, gst_amount, final_amount,
               payment_method, sale_date, amount_paid, balance_due FROM sales WHERE sale_id = ?""",
            (sale_id,)
        )[0]

        # Get sale items
        items_data = self.db.execute_query(
            """SELECT sku_code, item_name, quantity, unit_price, total_price
               FROM sale_items WHERE sale_id = ?""",
            (sale_id,)
        )
        
        # Get payment history
        payments_data = self.db.execute_query(
            """SELECT amount_paid, payment_method, payment_date, activity_note
               FROM payment_history WHERE sale_id = ? ORDER BY payment_date ASC""",
            (sale_id,)
        )

        # Format data for PDF
        invoice_data = {
            "bill_number": sale_data[0],
            "date": sale_data[9][:10],
            "customer_name": sale_data[1] or "",
            "customer_phone": sale_data[2] or "",
            "subtotal": sale_data[3],
            "discount_amount": sale_data[5],
            "gst_amount": sale_data[6],
            "grand_total": sale_data[7],
            "amount_paid": sale_data[10],
            "balance_due": sale_data[11]
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
                "amount": item[4]
            })
            
        payments = []
        for p in payments_data:
            payments.append({
                "amount": p[0],
                "method": p[1],
                "date": p[2][:16] if p[2] else "",
                "note": p[3] or ""
            })

        return self._create_pdf(invoice_data, items, payments)


    def _create_pdf(self, data: dict, items: list, payments: list) -> str:
        """Internal method to create PDF with the specific template layout."""
        # Get shop details from config
        gst_number = self.db.get_setting(config.SETTING_GST_NUMBER)

        bill_number = data["bill_number"]
        filename = self.invoices_dir / f"{bill_number}.pdf"
        filename = filename.resolve()

        # Create the document with specific margins
        doc = SimpleDocTemplate(
            str(filename),
            pagesize=A4,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        # --- Drawing Function for Header and Footer ---
        def draw_header_footer(canvas, doc):
            """Draws the fixed header and footer on every page."""
            canvas.saveState()
            canvas.setStrokeColor(PURPLE_COLOR)
            canvas.setFillColor(PURPLE_COLOR)

            # --- Header ---
            # Logo
            import os, sys
            try:
                if hasattr(sys, '_MEIPASS'):
                    base_path = sys._MEIPASS
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(base_path, config.LOGO_PATH)
                canvas.drawImage(logo_path, 0.7 * inch, A4[1] - 1.75 * inch, width=1.25 * inch, height=1.25 * inch, preserveAspectRatio=True)
            except Exception as e:
                print("Logo missing from PDF generation:", e)
                # Placeholder if logo not found
                canvas.rect(0.5 * inch, A4[1] - 1.75 * inch, 1.25 * inch, 1.25 * inch)
                canvas.drawString(0.7 * inch, A4[1] - 1.1 * inch, "LOGO")

            # Shop Details (Text)
            # Note: Using FONT_BOLD/FONT_REGULAR which might be Helvetica if Marathi font isn't loaded.
            # The Marathi text will not render correctly without the proper font.
            
            # Shop Name
            canvas.setFont(FONT_BOLD, 24)
            # Replace with actual Marathi text if font is available: "श्री गणेशा सिल्क"
            canvas.drawString(1.9 * inch, A4[1] - 0.9 * inch, "Shree Ganesha Silk")

            # Subtitle
            canvas.setFont(FONT_REGULAR, 12)
            # Replace with: "फॅन्सी साड्या आणि कापड दुकान"
            canvas.drawString(1.9 * inch, A4[1] - 1.1 * inch, "Fancy Saree and Cloth Shop")

            # Address & Phone
            canvas.setFont(FONT_REGULAR, 10)
            # Replace with: "गणेश पेठ, गणेश मंदिराजवळ, बसमत,"
            canvas.drawString(1.9 * inch, A4[1] - 1.4 * inch, "Ganesh Peth, Near Ganesh Temple, Basmat,")
            # Replace with: "महाराष्ट्र 431512, भारत"
            canvas.drawString(1.9 * inch, A4[1] - 1.55 * inch, "Maharashtra 431512, India")
            # Replace with: "फोन : +91 72193 93139"
            canvas.drawString(1.9 * inch, A4[1] - 1.75* inch, "Phone : +91 72193 93139")

            # Bill No. / Date Box on the right
            box_x = A4[0] - 2.5 * inch
            box_y = A4[1] - 1.3 * inch
            box_w = 2 * inch
            box_h = 0.8 * inch
            canvas.setLineWidth(0.5)
            canvas.rect(box_x, box_y, box_w, box_h, stroke=1, fill=0)
            canvas.line(box_x, box_y + box_h / 1, box_x + box_w, box_y + box_h / 1)

            # Box Content
            canvas.setFont(FONT_BOLD, 10)
            canvas.drawString(box_x + 5, box_y + box_h / 2 + 12, "BillNo:")
            canvas.drawString(box_x + 5, box_y + 12, "Date:")
            canvas.setFont(FONT_REGULAR, 10)
            canvas.drawString(box_x + 60, box_y + box_h / 2 + 12, str(data["bill_number"]))
            canvas.drawString(box_x + 60, box_y + 12, data["date"])

            # --- Footer ---
            footer_y = 0.8 * inch
            canvas.setFont(FONT_BOLD, 10)

            # Amount in words / Disclaimer
            canvas.setFont(FONT_REGULAR, 9)
            canvas.drawString(0.5 * inch, footer_y + 0.6 * inch, "Heavy work and silk sarees require dry cleaning only, as they have no water damage guarantee.")
            canvas.drawString(0.5 * inch, footer_y + 0.45 * inch, "Damaged sarees can be exchanged within 7 days. No cash refunds.")

            # Draw underline for amount in words
            # canvas.line(1.8 * inch, footer_y + 0.5 * inch, A4[0] - 0.5 * inch, footer_y + 0.5 * inch)

            # GSTIN
            #
            # Signature Block
            sig_x = A4[0] - 2.5 * inch
            canvas.setFont(FONT_BOLD, 12)
            # Replace with: "श्री गणेशा सिल्क"
            canvas.drawString(sig_x + 0.2*inch, footer_y + 0.2 * inch, "For Shree Ganesha Silk")
            canvas.setLineWidth(1)
            canvas.line(sig_x, footer_y - 0.1 * inch, A4[0] - 0.5 * inch, footer_y - 0.1 * inch)
            canvas.setFont(FONT_REGULAR, 10)
            canvas.drawCentredString(sig_x + 1 * inch, footer_y - 0.3 * inch, "Signature")

            canvas.restoreState()

        # --- Build Story Content ---
        story = []
        styles = getSampleStyleSheet()

        # Push content down to avoid overlapping with the fixed header
        story.append(Spacer(1, 2 * inch))

        # Customer Name Section
        # Using a table to create the "Name: ____________" line with correct styling
        name_style = ParagraphStyle('NameStyle', parent=styles['Normal'], fontName=FONT_BOLD, fontSize=11, textColor=PURPLE_COLOR)
        customer_name_paragraph = Paragraph(f"{data['customer_name']}", styles['Normal'])
        
        name_data = [
            [Paragraph("Name :", name_style), customer_name_paragraph]
        ]
        name_table = Table(name_data, colWidths=[0.8 * inch, 6.4 * inch])
        name_table.setStyle(TableStyle([
            ('LINEBELOW', (1, 0), (1, 0), 1, PURPLE_COLOR), # Underline for the name part
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ]))
        story.append(name_table)
        story.append(Spacer(1, 0.2 * inch))

        # --- Main Items and Totals Table ---
        # Define column widths based on the template image
        col_widths = [0.6 * inch, 3 * inch, 1 * inch, 0.7 * inch, 1 * inch, 1.2 * inch]

        # Table Header
        table_data = [
            ["Sr. No.", "Particulars", "SKU", "Qty", "Rate", "Amount"]
        ]

        # Fill with Item Data
        # Ensure a minimum number of rows to match the template look (e.g., 12 rows)
        MIN_ROWS = 12
        for idx, item in enumerate(items, 1):
            table_data.append([
                str(idx),
                item["name"],
                item["sku"] or "", # Display SKU
                str(item["qty"]),
                f"{item['rate']:.2f}",
                f"{item['amount']:.2f}"
            ])
        
        # Add empty rows to fill space
        rows_to_add = max(0, MIN_ROWS - len(items))
        for _ in range(rows_to_add):
            table_data.append(["", "", "", "", "", ""])

        total_qty = sum(item["qty"] for item in items)
        total_distinct_items = len(items)

        # Add Totals Rows dynamically to hide zero values
        totals_list = []
        totals_list.append(("Total Items", total_distinct_items))
        totals_list.append(("Total Qty", total_qty))

        has_tax_discount = data.get('discount_amount', 0) > 0 or data.get('gst_amount', 0) > 0
        if has_tax_discount:
            totals_list.append(("Sub Total", data.get('subtotal', 0)))
        if data.get('discount_amount', 0) > 0:
            totals_list.append(("Discount", data['discount_amount']))
        if data.get('gst_amount', 0) > 0:
            totals_list.append(("GST", data['gst_amount']))
            
        totals_list.append(("Grand Total", data['grand_total']))
        
        paid = data.get('amount_paid') or 0.0
        due = data.get('balance_due') or 0.0
        
        is_purchase = str(data.get("bill_number", "")).startswith("PUR")
        if not is_purchase:
            totals_list.append(("Amount Paid", paid))
            if due > 0:
                totals_list.append(("Balance Due", due))
                
        num_totals = len(totals_list)
        for label, val in totals_list:
            if label in ("Total Items", "Total Qty"):
                val_str = str(int(val))
            else:
                val_str = f"{val:.2f}"
            table_data.append(["", "", "", "", label, val_str])
            
        main_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Define Table Styling
        style_cmds = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), PURPLE_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1.5, PURPLE_COLOR),
            ('TEXTCOLOR', (0, 1), (-1, -1), PURPLE_COLOR),
            ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'), 
            ('ALIGN', (1, 1), (1, -(num_totals + 1)), 'LEFT'), 
            ('ALIGN', (3, 1), (-1, -(num_totals + 1)), 'CENTER'), 
            ('ALIGN', (-1, 1), (-1, -(num_totals + 1)), 'RIGHT'), 
        ]
        
        # Dynamic styling for total rows
        for i in range(1, num_totals + 1):
            row_idx = -i
            style_cmds.extend([
                ('SPAN', (0, row_idx), (3, row_idx)),
                ('BACKGROUND', (4, row_idx), (4, row_idx), PURPLE_COLOR),
                ('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.white),
                ('FONTNAME', (4, row_idx), (4, row_idx), FONT_BOLD),
                ('ALIGN', (4, row_idx), (4, row_idx), 'CENTER'),
                ('ALIGN', (-1, row_idx), (-1, row_idx), 'RIGHT'),
                ('FONTNAME', (-1, row_idx), (-1, row_idx), FONT_BOLD),
            ])
        
        main_table.setStyle(TableStyle(style_cmds))
        story.append(main_table)
        
        # --- Add Payment History Ledger ---
        if payments:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Payment History Ledger", styles['Heading4']))
            
            pay_data = [["Date", "Method", "Activity Note", "Amount Paid"]]
            for p in payments:
                pay_data.append([
                    p["date"], p["method"], p["note"], f"₹{p['amount']:.2f}"
                ])
                
            pay_table = Table(pay_data, colWidths=[1.8 * inch, 1.2 * inch, 2.9 * inch, 1.3 * inch])
            pay_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PURPLE_COLOR),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
                ('GRID', (0, 0), (-1, -1), 0.5, PURPLE_COLOR),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(pay_table)

        # Build the PDF
        # onFirstPage and onLaterPages draw the fixed header/footer
        doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
        
        return str(filename)