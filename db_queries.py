# db_queries.py

import logging
from db_setup import DBSetup

class DBQueries(DBSetup):

    def fetch_transactions(self, transaction_type: str = None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if transaction_type:
                cursor.execute('''
                    SELECT t.id, t.date, t.receiver_deliverer, t.description,
                           t.amount, t.transaction_type, c.name
                    FROM transactions t
                    LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                    LEFT JOIN categories c ON tc.category_id = c.id
                    WHERE t.transaction_type = ?
                ''', (transaction_type,))
            else:
                cursor.execute('''
                    SELECT t.id, t.date, t.receiver_deliverer, t.description,
                           t.amount, t.transaction_type, c.name
                    FROM transactions t
                    LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                    LEFT JOIN categories c ON tc.category_id = c.id
                ''')
            transactions = cursor.fetchall()
            logging.info(f"Fetched {len(transactions)} transactions")
            return transactions

    def fetch_transactions_with_categories(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.date, t.receiver_deliverer, t.description,
                       t.amount, t.transaction_type, c.name
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                LEFT JOIN categories c ON tc.category_id = c.id
            ''')
            transactions = cursor.fetchall()
            logging.info(f"Fetched {len(transactions)} transactions with categories")
            return transactions

    def search_transactions_by_name(self, name: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.date, t.receiver_deliverer, t.description,
                       t.amount, t.transaction_type, c.name
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                LEFT JOIN categories c ON tc.category_id = c.id
                WHERE t.receiver_deliverer LIKE ?
            ''', ('%' + name + '%',))
            transactions = cursor.fetchall()
            logging.info(f"Found {len(transactions)} transactions matching name '{name}'")
            return transactions

    def search_transactions_by_category(self, category_name: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.date, t.receiver_deliverer, t.description,
                       t.amount, t.transaction_type, c.name
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                LEFT JOIN categories c ON tc.category_id = c.id
                WHERE c.name LIKE ?
            ''', ('%' + category_name + '%',))
            transactions = cursor.fetchall()
            logging.info(f"Found {len(transactions)} transactions in category '{category_name}'")
            return transactions

    def search_transactions_by_location(self, location: str):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.date, t.receiver_deliverer, t.description,
                       t.amount, t.transaction_type, c.name, l.name
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                LEFT JOIN categories c ON tc.category_id = c.id
                LEFT JOIN transaction_locations tl ON t.id = tl.transaction_id
                LEFT JOIN locations l ON tl.location_id = l.id
                WHERE l.name LIKE ?
            ''', ('%' + location + '%',))
            transactions = cursor.fetchall()
            logging.info(f"Found {len(transactions)} transactions in location '{location}'")
            return transactions

    def fetch_transaction_by_id(self, transaction_id: int):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.id, t.date, t.receiver_deliverer, t.description,
                       t.amount, t.transaction_type, c.name
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                LEFT JOIN categories c ON tc.category_id = c.id
                WHERE t.id = ?
            ''', (transaction_id,))
            transaction = cursor.fetchone()
            logging.info(f"Fetched transaction with ID {transaction_id}")
            return transaction

    def fetch_transactions_in_timeframe(self, start_date: str, end_date: str, transaction_type: str = None):
        with self.connect() as conn:
            cursor = conn.cursor()
            if transaction_type:
                cursor.execute('''
                    SELECT t.id, t.date, t.receiver_deliverer, t.description,
                        t.amount, t.transaction_type, c.name
                    FROM transactions t
                    LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                    LEFT JOIN categories c ON tc.category_id = c.id
                    WHERE t.date BETWEEN ? AND ?
                    AND t.transaction_type = ?
                ''', (start_date, end_date, transaction_type))
            else:
                cursor.execute('''
                    SELECT t.id, t.date, t.receiver_deliverer, t.description,
                        t.amount, t.transaction_type, c.name
                    FROM transactions t
                    LEFT JOIN transaction_categories tc ON t.id = tc.transaction_id
                    LEFT JOIN categories c ON tc.category_id = c.id
                    WHERE t.date BETWEEN ? AND ?
                ''', (start_date, end_date))

            transactions = cursor.fetchall()
            logging.info(f"Fetched {len(transactions)} transactions between {start_date} and {end_date}")
            return transactions
