import hashlib
from database import DatabaseManager

db = DatabaseManager('boutique_database.db')

# Generate the hash for "admin 123"
new_hash_123 = hashlib.sha256('admin 123'.encode()).hexdigest()

# Generate the hash for "admin"
new_hash_default = hashlib.sha256('admin'.encode()).hexdigest()

# Update the main admin user to use "admin 123"
db.execute_query(f"UPDATE users SET password_hash = '{new_hash_123}' WHERE username = 'admin'")

# Just in case, also ensure the default admin hash is updated if there's an admin user
print("Password for 'admin' reset successfully.")
db.disconnect()
