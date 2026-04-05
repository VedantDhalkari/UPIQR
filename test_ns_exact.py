import traceback
import customtkinter as ctk

app = ctk.CTk()

try:
    from database import DatabaseManager
    from invoice_generator import InvoiceGenerator
    from purchase_invoice_generator import PurchaseInvoiceGenerator
    
    db = DatabaseManager('shop_database.db')
    ig = InvoiceGenerator(db)
    pig = PurchaseInvoiceGenerator(db)
    
    print("Testing NewStock exactly as in main.py...")
    
    from new_stock import NewStockModule
    kwargs = {}
    
    # Try EXACTLY what main.py does:
    ns = NewStockModule(
        app,
        db_manager=db,
        purchase_invoice_generator=pig,
        on_new_supplier=lambda: print("sup"),
        **kwargs
    )
    ns.pack(fill="both", expand=True)
    
    print("new_stock OK, packing didn't crash.")

except Exception as e:
    print("CRASH!")
    traceback.print_exc()
