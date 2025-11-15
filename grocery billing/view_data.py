# view_data.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "billing.db"

def show_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, item, price, quantity, total, date FROM purchases ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No purchases found.")
        return
    for r in rows:
        print(r)

if __name__ == "__main__":
    show_all()
