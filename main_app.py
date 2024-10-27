import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty

from db_setup import DBSetup
from db_operations import DBOperations
from db_queries import DBQueries

db_name = 'bank_transactions.db'
db_setup = DBSetup(db_name)
db_operations = DBOperations(db_name)
db_queries = DBQueries(db_name)


logging.basicConfig(level=logging.INFO)


class WindowManager(ScreenManager):
    pass

class TransactionLayout(BoxLayout):
    screen = ObjectProperty(None)

class BaseTransactionsScreen(Screen):
    transactions = []  
    page_size = 20     
    current_page = 1   
    total_pages = 1    
    transaction_type_filter = None  # all transactions, credit or debit

    def on_enter(self):
        # Fetch transactions from the database when entering the screen
        self.fetch_transactions()
        self.current_page = 1  
        self.load_page()
        self.update_pagination_controls()

    def fetch_transactions(self):
        self.transactions = db_queries.fetch_transactions(self.transaction_type_filter)
        logging.info(f"Fetched {len(self.transactions)} transactions for {self.transaction_type_filter or 'all'}")

    def load_page(self):
        self.ids.transaction_layout.ids.transactions_box.clear_widgets()

        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, len(self.transactions))
        transactions_to_display = self.transactions[start_index:end_index]

        for idx, transaction in enumerate(transactions_to_display):
            transaction_id, date, receiver_deliverer, description, amount, transaction_type, category_name = transaction

            background_color = (0.2, 0.2, 0.2, 1) if idx % 2 == 0 else (0.15, 0.15, 0.15, 1)

            transaction_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=40,  
                spacing=5,
                padding=(5, 5)
            )

            transaction_row.add_widget(self.create_table_cell(date, 0.1, background_color))
            transaction_row.add_widget(self.create_table_cell(receiver_deliverer, 0.25, background_color))
            transaction_row.add_widget(self.create_table_cell(description, 0.35, background_color))
            transaction_row.add_widget(self.create_table_cell(str(amount), 0.1, background_color))
            transaction_row.add_widget(self.create_table_cell(transaction_type, 0.1, background_color))
            transaction_row.add_widget(self.create_table_cell(category_name or '', 0.1, background_color))

            self.ids.transaction_layout.ids.transactions_box.add_widget(transaction_row)

    def create_table_cell(self, text, size_hint_x, background_color):
        label = Label(
            text=text,
            size_hint_x=size_hint_x,
            size_hint_y=None,
            height=40,
            halign='left',   
            valign='middle',
            #text_size=(0, None),
            shorten=True,    
            shorten_from='right' 
        )
        label.bind(size=self._update_rect)
        with label.canvas.before:
            Color(*background_color)
            label.rect = Rectangle(size=label.size, pos=label.pos)
        return label

    def _update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def update_pagination_controls(self):
        self.total_pages = max(1, (len(self.transactions) + self.page_size - 1) // self.page_size)
        page_numbers = self.get_page_numbers()

        for i, page_number in enumerate(page_numbers):
            button = self.ids.transaction_layout.ids.get(f'page_{i+1}')
            if button:
                button.text = str(page_number)
                button.on_press = lambda page=page_number: self.go_to_page(page)
                if page_number == self.current_page:
                    button.background_color = (0.3, 0.5, 0.9, 1)
                else:
                    button.background_color = (1, 1, 1, 1)
            else:
                button.opacity = 0
                button.disabled = True

    def get_page_numbers(self):
        if self.total_pages <= 3:
            return list(range(1, self.total_pages + 1))
        elif self.current_page == 1:
            return [1, 2, 3]
        elif self.current_page == self.total_pages:
            return [self.total_pages - 2, self.total_pages - 1, self.total_pages]
        else:
            return [self.current_page - 1, self.current_page, self.current_page + 1]

    def go_to_page(self, page_num):
        self.total_pages = max(1, (len(self.transactions) + self.page_size - 1) // self.page_size)
        self.current_page = max(1, min(page_num, self.total_pages))
        self.load_page()
        self.update_pagination_controls()

    def go_to_first_page(self):
        self.go_to_page(1)

    def go_to_previous_page(self):
        if self.current_page > 1:
            self.go_to_page(self.current_page - 1)

    def go_to_next_page(self):
        self.total_pages = max(1, (len(self.transactions) + self.page_size - 1) // self.page_size)
        if self.current_page < self.total_pages:
            self.go_to_page(self.current_page + 1)

    def go_to_last_page(self):
        self.total_pages = max(1, (len(self.transactions) + self.page_size - 1) // self.page_size)
        self.go_to_page(self.total_pages)

class TransactionsScreen(BaseTransactionsScreen):
    transaction_type_filter = None 

class CreditScreen(BaseTransactionsScreen):
    transaction_type_filter = 'credit'

class DebitScreen(BaseTransactionsScreen):
    transaction_type_filter = 'debit'

class HomeScreen(Screen):
    pass

class BankTransactionsApp(App):
    def build(self):
        return Builder.load_file('main.kv')

if __name__ == '__main__':
    BankTransactionsApp().run()
