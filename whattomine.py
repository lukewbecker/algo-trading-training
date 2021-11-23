import numpy as np
import pandas as pd

import requests

response = requests.get('https://whattomine.com/coins.json')

data = response.json()

df = pd.DataFrame.from_dict(data['coins']).T
df.reset_index(inplace = True)
df.rename(columns = {'index': 'coin'}, inplace = True)

df.insert(0, 'date', pd.to_datetime('now').replace(microsecond=0))
df.date = pd.to_datetime(df.date)
df = df.set_index('date').sort_index()

# Use this if we want to append.
# df.to_csv('whattomine.csv', mode = 'a', header = False)
# print("CSV written successfully.")

# Use this for daily updating of spreadsheet:
df.to_csv("whattomine_list.csv")
print("Updated csv with daily values (non-appended).")

# Use this for daily updating of spreadsheet:
df.to_csv("whattomine_list_history.csv", mode = 'a', header = False)
print("Updated csv with daily values (appended).")

# Updating the local SQLite database.
import sqlite3 as sql
import pandas as pd

# This line must be run first to setup the connection.
conn = sql.connect('/Users/luke/projects/github/algo-trading-experiments/whattomine.db')

# This code checks to see if the SQLite database has a table named "holdings".
holdings_test = pd.read_sql("SELECT * FROM sqlite_master WHERE type = 'table' AND name = 'holdings';", conn)

# Now the code checks if the table exists, and if so appends the newest holdings dataframe to the sqlite database.
if holdings_test.name.count() > 0:
    df.to_sql('holdings', con = conn, if_exists = 'append')
else:
    # This line creates a table called "holdings" if the table doesn't exist.
    df.to_sql('holdings', con = conn)

print("Updated database files.")

print("Successfully ran script.")