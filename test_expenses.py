import sqlite3
import datetime

conn = sqlite3.connect("d:/runingP/files/boutique_database.db")
c = conn.cursor()

try:
    c.execute("INSERT INTO expenses (amount, category, description, expense_date) VALUES (?, ?, ?, ?)", (500.0, "Misc", "Test", "2026-03-13"))
    conn.commit()
    print("Inserted!")
except Exception as e:
    print("Insert error:", e)

res = c.execute("SELECT expense_date, DATE(expense_date) FROM expenses").fetchall()
print("All expenses:")
for r in res: print(r)

today = datetime.datetime.now().strftime("%Y-%m-%d")
exp_data = c.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE DATE(expense_date) BETWEEN ? AND ?", (today, today)).fetchall()
print(f"Total expenses today ({today}):", exp_data[0][0])
