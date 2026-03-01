
import config
from database import DatabaseManager
from invoice_generator import InvoiceGenerator
from datetime import datetime

# Initialize
db = DatabaseManager('boutique_database.db')
generator = InvoiceGenerator(db)

# Dummy Data
data = {
    "bill_number": "TEST-LOGO-001",
    "date": datetime.now().strftime("%Y-%m-%d"),
    "customer_name": "Test Customer",
    "customer_phone": "1234567890",
    "payment_method": "Cash",
    "subtotal": 1000.0,
    "discount_percent": 0,
    "discount_amount": 0,
    "gst_amount": 50.0,
    "grand_total": 1050.0,
    "is_estimate": False
}

items = [
    {"sku": "SKU001", "name": "Test Saree", "qty": 1, "rate": 1000.0, "amount": 1000.0}
]

# Generate
try:
    pdf_path = generator._create_pdf(data, items)
    print(f"Success! PDF generated at: {pdf_path}")
except Exception as e:
    print(f"Error generating PDF: {e}")
    import traceback
    traceback.print_exc()
