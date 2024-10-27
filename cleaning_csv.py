import pandas as pd

df = pd.read_csv('statement.csv', delimiter=';')

df = df[['Date', 'Beneficiary/Payer', 'Details', 'Amount', 'Currency', 'Debit/Credit']]

df.rename(columns={
    'Date': 'date',
    'Beneficiary/Payer': 'receiver_deliverer',
    'Details': 'description',
    'Amount': 'amount',
    'Debit/Credit': 'debit_credit'
}, inplace=True)

# Correct date format
df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce').dt.strftime('%Y-%m-%d')

# Amount as numeric
df['amount'] = df['amount'].str.replace(',', '.').str.replace(' ', '')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# ID
df.insert(0, 'ID', df.index + 1)

# Saving
df.to_csv('transactions.csv', index=False)

print(df.head())