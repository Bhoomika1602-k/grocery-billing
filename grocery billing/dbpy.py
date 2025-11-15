# db.py
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "billing.db"

def init_db():
    """Create purchases table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            price REAL,
            quantity INTEGER,
            total REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_purchase(item: str, price: float, quantity: int, total: float):
    """Save a single purchase row into the DB."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO purchases (item, price, quantity, total, date) VALUES (?, ?, ?, ?, ?)",
        (item, price, quantity, total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
