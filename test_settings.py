import traceback
import customtkinter as ctk
from settings import SettingsModule
from database import DatabaseManager

app = ctk.CTk()
db = DatabaseManager('shop_database.db')
try:
    sm = SettingsModule(app, db_manager=db, current_user={"username": "admin", "role": "admin"})
    print("SettingsModule loaded successfully!")
except Exception as e:
    print('Error loading SettingsModule:')
    traceback.print_exc()
