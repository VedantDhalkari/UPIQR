from database import DatabaseManager
import config

db = DatabaseManager('boutique_database.db')

pin = db.get_setting("admin_pin")
print(f"Stored PIN in DB: '{pin}'")
print(f"Fallback Config PIN: '{config.ADMIN_PIN}'")
print("We will force-reset the DB pin to 1234 now...")

db.update_setting("admin_pin", "1234")
print(f"New PIN in DB: '{db.get_setting('admin_pin')}'")

db.disconnect()
