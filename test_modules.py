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
    
    print("Testing modules...")
    
    from new_stock import NewStockModule
    ns = NewStockModule(app, db_manager=db, purchase_invoice_generator=pig)
    print("new_stock OK")
    
    from purchase_management import PurchaseManagementModule
    pm = PurchaseManagementModule(app, db_manager=db, invoice_generator=ig, purchase_invoice_generator=pig)
    print("purchase_management OK")
    
    from bill_management import BillManagementModule
    bm = BillManagementModule(app, db_manager=db, invoice_generator=ig)
    print("bill_management OK")
    
    from reports import ReportsModule
    rm = ReportsModule(app, db_manager=db)
    print("reports OK")
    
    from stock import StockManagementModule
    sm = StockManagementModule(app, db_manager=db)
    print("stock OK")

except Exception as e:
    print("CRASH!")
    traceback.print_exc()
