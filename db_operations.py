# db_operations.py

import csv
import logging
from typing import List, Tuple
from db_setup import DBSetup
from dummy_data import (
    shops, gas_stations, internet_telecom, utility_providers,
    financial_services, salaries, names, locations
)

class DBOperations(DBSetup):
    def __init__(self, db_name: str = 'bank_transactions.db'):
        super().__init__(db_name)

        self.categories = {
            'groceries': shops,
            'gas_stations': gas_stations,
            'utilities': utility_providers,
            'internet_telecom': internet_telecom,
            'financial_services': financial_services,
            'salaries': salaries,
            'names': names,
        }

    def insert_categories(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            for category in self.categories.keys():
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name)
                    VALUES (?)
                ''', (category,))

            # incase unkown category, add 'other'
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name)
                VALUES ('other')
            ''')
            conn.commit()
            logging.info("Inserted categories")

    def insert_locations(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            for location in locations:
                cursor.execute('''
                    INSERT OR IGNORE INTO locations (name)
                    VALUES (?)
                ''', (location,))
            conn.commit()
            logging.info("Inserted locations")

    def import_csv_to_db(self, csv_file: str):
        try:
            # Reading in the csv file
            with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                transactions: List[Tuple] = []
                for row in reader:
                    amount = float(row['amount'])
                    transaction_type = 'credit' if row['debit_credit'] == 'K' else 'debit'
                    transactions.append((
                        row['date'],
                        row['receiver_deliverer'],
                        row.get('details', ''),
                        amount,
                        transaction_type
                    ))

            # Writing to database
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT INTO transactions (date, receiver_deliverer, description, amount, transaction_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', transactions)
                conn.commit()
                logging.info(f"Imported data from {csv_file} into transactions table")

            # Assign categories and locations
            self.assign_categories_to_transactions()
            self.assign_locations_to_transactions()

            # Insert into delivered and received tables
            self.insert_into_delivered_received()

        except Exception as e:
            logging.error(f"Failed to import CSV: {e}")

    def assign_categories_to_transactions(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            # Fetch all transactions
            cursor.execute('SELECT id, receiver_deliverer FROM transactions')
            transactions = cursor.fetchall()

            for transaction_id, receiver_deliverer in transactions:
                # Strip out location information for category matching
                receiver_name = receiver_deliverer.split('\\')[0]
                category_assigned = False

                for category, names_list in self.categories.items():
                    if receiver_name in names_list:
                        # Get category_id
                        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
                        category_id = cursor.fetchone()[0]

                        # Assign category to transaction
                        cursor.execute('''
                            INSERT OR IGNORE INTO transaction_categories (transaction_id, category_id)
                            VALUES (?, ?)
                        ''', (transaction_id, category_id))
                        category_assigned = True
                        break

                if not category_assigned:
                    # Assign 'other' category
                    cursor.execute('SELECT id FROM categories WHERE name = ?', ('other',))
                    category_id = cursor.fetchone()[0]

                    # Assign 'other' category to transaction
                    cursor.execute('''
                        INSERT OR IGNORE INTO transaction_categories (transaction_id, category_id)
                        VALUES (?, ?)
                    ''', (transaction_id, category_id))

            conn.commit()
            logging.info("Assigned categories to transactions")

    def assign_locations_to_transactions(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            # Fetch all transactions
            cursor.execute('SELECT id, receiver_deliverer FROM transactions')
            transactions = cursor.fetchall()

            for transaction_id, receiver_deliverer in transactions:
                # Extract location from receiver_deliverer
                if '\\' in receiver_deliverer:
                    _, location = receiver_deliverer.split('\\', 1)

                    # Check if the location already exists in the locations table
                    cursor.execute('SELECT id FROM locations WHERE name = ?', (location,))
                    result = cursor.fetchone()

                    if result:
                        location_id = result[0]
                    else:
                        # Insert the new location into the locations table
                        cursor.execute('INSERT INTO locations (name) VALUES (?)', (location,))
                        location_id = cursor.lastrowid

                    # Assign the location to the transaction in the transaction_locations table
                    cursor.execute('''
                        INSERT OR IGNORE INTO transaction_locations (transaction_id, location_id)
                        VALUES (?, ?)
                    ''', (transaction_id, location_id))

            conn.commit()
            logging.info("Assigned locations to transactions")

    def insert_into_delivered_received(self):
        with self.connect() as conn:
            cursor = conn.cursor()

            # Insert into delivered_transactions
            cursor.execute('''
                INSERT INTO delivered_transactions (date, receiver_deliverer, description, amount)
                SELECT date, receiver_deliverer, description, amount
                FROM transactions
                WHERE transaction_type = 'debit';
            ''')

            # Insert into received_transactions
            cursor.execute('''
                INSERT INTO received_transactions (date, receiver_deliverer, description, amount)
                SELECT date, receiver_deliverer, description, amount
                FROM transactions
                WHERE transaction_type = 'credit';
            ''')

            conn.commit()
            logging.info("Inserted data into delivered and received tables")
