import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("paylinks.db")

def conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS paylinks (
            token TEXT PRIMARY KEY,
            amount_aed INTEGER NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            gateway_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)