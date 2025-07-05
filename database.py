import sqlite3
from typing import List
import pandas as pd

DB_FILE = "expenses.db"

def create_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            source_file TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_transactions(df: pd.DataFrame):
    conn = create_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO transactions (date, description, amount, category, source_file)
            VALUES (?, ?, ?, ?, ?)
        ''', (row['date'], row['description'], row['amount'], row['category'], row['source_file']))

    conn.commit()
    conn.close()

def fetch_all_transactions() -> pd.DataFrame:
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def clear_transactions():
    conn = create_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()