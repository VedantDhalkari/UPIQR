import hashlib
from database import DatabaseManager

db = DatabaseManager('boutique_database.db')

pw = 'admin 123'
expected_hash = hashlib.sha256(pw.encode()).hexdigest()

users = db.execute_query("SELECT user_id, username, password_hash FROM users WHERE username='admin'")
print("Users:", users)
if users:
    actual_hash = users[0][2]
    print("Expected Hash for 'admin 123':", expected_hash)
    print("Actual Hash in DB            :", actual_hash)
    print("Match? :", expected_hash == actual_hash)
else:
    print("No admin user found in DB!")

print("Fixing it now...")
db.execute_query("UPDATE users SET password_hash = ? WHERE username = 'admin'", (expected_hash,))
print("Updated!")
users = db.execute_query("SELECT user_id, username, password_hash FROM users WHERE username='admin'")
print("Rechecked Actual Hash in DB:", users[0][2])
db.disconnect()
