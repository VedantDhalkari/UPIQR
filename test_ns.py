import traceback
import customtkinter as ctk
from new_stock import NewStockModule
from database import DatabaseManager

app = ctk.CTk()
db = DatabaseManager('shop_database.db')
try:
    ns = NewStockModule(app, db, None)
    print("NewStockModule loaded successfully!")
except Exception as e:
    print('Error loading NewStockModule:')
    traceback.print_exc()
