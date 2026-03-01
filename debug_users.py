import hashlib
from database import DatabaseManager
import pprint

db = DatabaseManager('boutique_database.db')

print("All users in DB:")
users = db.execute_query("SELECT user_id, username, password_hash, role FROM users")
for u in users:
    print(u)

print("\nSimulating 'admin' with 'admin 123':")
# simulate what database.py does:
password_hash = hashlib.sha256('admin 123'.encode()).hexdigest()
print(f"Computed Hash for 'admin 123': {password_hash}")

res = db.execute_query(
    "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
    ('admin', password_hash)
)
print("Verify Result:", res)

print("\nSimulating 'admin' with 'admin':")
password_hash2 = hashlib.sha256('admin'.encode()).hexdigest()
res2 = db.execute_query(
    "SELECT user_id, username, role FROM users WHERE username = ? AND password_hash = ?",
    ('admin', password_hash2)
)
print("Verify Result:", res2)

db.disconnect()
