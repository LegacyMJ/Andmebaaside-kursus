# db_setup.py

import sqlite3
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

class DBSetup:
    def __init__(self, db_name: str = 'bank_transactions.db'):
        self.db_name = db_name

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            # transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    receiver_deliverer TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    transaction_type TEXT CHECK(transaction_type IN ('credit', 'debit')) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

            # index on date for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);')

            # categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );
            ''')

            # locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );
            ''')

            # transaction_categories table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transaction_categories (
                    transaction_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    PRIMARY KEY (transaction_id, category_id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                );
            ''')

            # transaction_locations table (many-to-many relationship)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transaction_locations (
                    transaction_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    PRIMARY KEY (transaction_id, location_id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                    FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
                );
            ''')

            # delivered_transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delivered_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    receiver_deliverer TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

            # received_transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS received_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    receiver_deliverer TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')

            conn.commit()
            logging.info("All tables created successfully.")

    def drop_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            tables = [
                'transactions', 'categories', 'locations',
                'transaction_categories', 'transaction_locations',
                'delivered_transactions', 'received_transactions'
            ]
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS {table};')
                logging.info(f"Dropped table: {table}")
            conn.commit()

    def clear_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            tables = [
                'transactions', 'categories', 'locations',
                'transaction_categories', 'transaction_locations',
                'delivered_transactions', 'received_transactions'
            ]
            for table in tables:
                cursor.execute(f'DELETE FROM {table};')
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
                logging.info(f"Cleared table: {table}")
            conn.commit()
