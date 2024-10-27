import random
import pandas as pd
from datetime import datetime, timedelta
import dummy_data 

def generate_transaction_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    transactions = []
    index = 1

    # Opening balance
    opening_balance = 10000
    transactions.append([index, date_range[0].strftime('%Y-%m-%d'), '', 'Opening balance', opening_balance, 'EUR', 'K'])
    index += 1

    # monthly subscriptions and salary payments
    subscriptions_last_paid = {service: None for service in dummy_data.internet_telecom + dummy_data.utility_providers + dummy_data.insurance_companies}
    salary_last_received = {person: None for person in dummy_data.names}

    for date in date_range:
        # numr of transactions per day (0 to 5)
        num_transactions = random.randint(0, 5)
        
        for _ in range(num_transactions):
            category_choice = random.choices(
                ['shops', 'gas_stations', 'people', 'salaries', 'subscriptions'],
                weights=[0.5, 0.2, 0.2, 0.05, 0.05],
                k=1
            )[0]

            if category_choice == 'shops':
                receiver_deliverer = f"{random.choice(dummy_data.shops)}\\{random.choice(dummy_data.locations)}"
                amount = round(random.uniform(5, 500), 2)
                debit_credit = 'D'
            elif category_choice == 'gas_stations':
                receiver_deliverer = f"{random.choice(dummy_data.gas_stations)}\\{random.choice(dummy_data.locations)}"
                amount = round(random.uniform(10, 100), 2)
                debit_credit = 'D'
            elif category_choice == 'people':
                receiver_deliverer = random.choice(dummy_data.names)
                amount = round(random.uniform(10, 1000), 2)
                debit_credit = random.choice(['D', 'K'])  
            elif category_choice == 'salaries':
                available_people_for_salary = [
                    person for person in dummy_data.names
                    if salary_last_received[person] is None or (date - salary_last_received[person]).days > 30
                ]
                if available_people_for_salary:
                    receiver_deliverer = random.choice(available_people_for_salary)
                    salary_last_received[receiver_deliverer] = date
                    amount = round(random.uniform(1000, 5000), 2) # salary
                    debit_credit = 'K'
                else:
                    continue 
            elif category_choice == 'subscriptions':
                available_subscriptions = [
                    service for service in (dummy_data.internet_telecom + dummy_data.utility_providers + dummy_data.insurance_companies)
                    if subscriptions_last_paid[service] is None or (date - subscriptions_last_paid[service]).days > 30
                ]
                if available_subscriptions:
                    receiver_deliverer = f"{random.choice(available_subscriptions)}\\{random.choice(dummy_data.locations)}"
                    subscriptions_last_paid[receiver_deliverer] = date
                    amount = round(random.uniform(20, 200), 2)
                    debit_credit = 'D'
                else:
                    continue  

            # Generate description
            if category_choice == 'salaries' or category_choice == 'people':
                description = f"Salary from {receiver_deliverer}" if category_choice == 'salaries' else f"Transaction with {receiver_deliverer}"
            else:
                card_number = f"'5555******4444 {date.strftime('%d.%m.%y')}"
                description = f"{card_number}  {receiver_deliverer}"

            # Append the transaction
            transactions.append([
                index, 
                date.strftime('%Y-%m-%d'), 
                receiver_deliverer, 
                description, 
                abs(amount), 
                'EUR', 
                debit_credit
            ])
            index += 1


    # Debit turnover
    debit_turnover = 6000
    transactions.append([index, date_range[-1].strftime('%Y-%m-%d'), '', 'Turnover', debit_turnover, 'EUR', 'D'])
    index += 1

    # Credit turnover
    credit_turnover = 5000
    transactions.append([index, date_range[-1].strftime('%Y-%m-%d'), '', 'Turnover', credit_turnover, 'EUR', 'K'])
    index += 1

    # Closing balance 
    closing_balance = round(opening_balance + credit_turnover - debit_turnover, 2)
    transactions.append([index, date_range[-1].strftime('%Y-%m-%d'), '', 'Closing balance', closing_balance, 'EUR', 'K'])

    df = pd.DataFrame(transactions, columns=['id', 'date', 'receiver_deliverer', 'details', 'amount', 'currency', 'debit_credit'])
    return df

start_date = '2020-01-01'
end_date = '2024-12-31'

df_transactions = generate_transaction_data(start_date, end_date)

df_transactions.to_csv('dummyset.csv', index=False)
print(f"Dataset with {len(df_transactions)} transactions saved as 'dummyset.csv'.")
