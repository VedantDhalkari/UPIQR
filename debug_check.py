import sqlite3
import hashlib
from database import DatabaseManager

db = DatabaseManager('boutique_database.db')

print("Old Admin PIN:", db.get_setting("admin_pin"))
db.update_setting("admin_pin", "9999")
print("New Admin PIN:", db.get_setting("admin_pin"))

users = db.execute_query("SELECT user_id, password_hash FROM users WHERE role = 'admin'")
if users:
    print("Old Hash:", users[0][1])
    new_hash = hashlib.sha256("newpass".encode()).hexdigest()
    db.execute_query("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, users[0][0]))
    users2 = db.execute_query("SELECT user_id, password_hash FROM users WHERE role = 'admin'")
    print("New Hash:", users2[0][1])
else:
    print("No admin user found")
    
db.disconnect()
