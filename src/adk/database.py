import sqlite3
import logging
import os

logging.basicConfig(level=logging.INFO)
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "adk.db")

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT NOT NULL,
            residential_address TEXT NOT NULL,
            residential_city TEXT NOT NULL,
            residential_state TEXT NOT NULL,
            residential_zip TEXT NOT NULL,
            residential_country TEXT NOT NULL,
            age INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # insert sample data
    cursor.execute('''
        INSERT INTO users (username, password, phone_number, email, residential_address, residential_city, residential_state, residential_zip, residential_country, age)
        VALUES
            ('john_doe', 'password123', '123-456-7890', 'john@example.com', '123 Main St', 'New York', 'NY', '10001', 'USA', 30),
            ('jane_doe', 'password456', '987-654-3210', 'jane@example.com', '456 Elm St', 'Los Angeles', 'CA', '90001', 'USA', 25)
    ''')
    conn.commit()
    conn.close()

def access_database(query:str) -> dict:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return {
        "status": "success",
        "data": results
    }