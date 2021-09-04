# Run this file to update the kucoin holdings sheet in google sheets.

import time

def kucoin_append():
    
    # First importing the needed libraries:

    import pandas as pd
    import numpy as np


    import os
    import requests
    import json
    import base64
    import time
    import base64
    import hmac
    import hashlib

    # Now importing the env file so the script can access the KuCoin API keys:
    import env

    # Defining the api keys with their own variables:
    api_key = env.kc_api_key
    api_s = env.kc_secret_api
    api_pp = env.kc_passphrase
    api_uid = env.kc_uid

    # creating the api keys for use in the calls:
    api_key = env.kc_api_key
    api_secret = env.kc_secret_api
    api_passphrase = env.kc_passphrase
    url = 'https://api.kucoin.com/api/v1/accounts'
    now = int(time.time() * 1000)
    str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
    signature = base64.b64encode(
    hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
    passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
    headers = {
    "KC-API-SIGN": signature,
    "KC-API-TIMESTAMP": str(now),
    "KC-API-KEY": api_key,
    "KC-API-PASSPHRASE": passphrase,
    "KC-API-KEY-VERSION": str(2)
    }

    # Getting the base response with the top level account values:
    response = requests.request('get', url, headers=headers)


    # Creating the account dataframe using the response request I just created:
    df = pd.DataFrame.from_dict(response.json()['data'])

    # Column cleanup:
    df.drop(columns = 'id', inplace = True)

    # Getting prices for coins:
    coin_list = df['currency'].unique().tolist()

    # USDC and USDT don't work in this list because they are "equivalent" of USD, so it comes back as a NoneType, leading to a none-type error later if I don't remove them from the list at this point.
    coin_list.remove('USDC')
    coin_list.remove('USDT')
    
    # This for loop will create a list of prices by calling each crypto within my 'coin_list' list. 

    price_list = []
    for coin in coin_list:
        prices = float(requests.get(f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={coin}-USDT').json()['data']['price'])
    #     print(prices), print(type(prices))
        price_list.append(prices)

    # Now creating a dictionary of the coin prices:
    coin_dict = {"coin":coin_list, "price":price_list}

    # Dataframe from the dictionary:
    df_prices = pd.DataFrame(coin_dict)

    # creating a copy dataframe of the acct info (this step can be dropped in future)
    account = df[df['type'] == 'trade'].copy()
    account = account.reset_index(drop = True)
    account.rename(columns = {'type': "act_name"}, inplace = True)


    # Now should be able to join the two dataframes. I have to join the two dataframes first before I can multiply columns to create the "$ value" column which is the end goal here.

    # Merge, inner join:

    holdings_append = account.merge(df_prices, left_on = 'currency', right_on = 'coin', how = 'left')

    # Now changing the value types of the columns with numbers in them from objects to float64:
    holdings_append['balance'] = holdings_append.balance.astype(float)
    holdings_append['available'] = holdings_append.available.astype(float)
    holdings_append['holds'] = holdings_append.holds.astype(float)

    # Now working through adding calculated columns that I'll later select from if it doesn't return 'nan':

    holdings_append['value_tmp'] = round(holdings_append.price * holdings_append.balance, 2)

    holdings_append["dollar_value"] = np.where(holdings_append['value_tmp'].notnull(), holdings_append['value_tmp'], holdings_append['balance'])
    holdings_append.dollar_value = holdings_append.dollar_value.round(2)

    # Dropping extra columns:
    holdings_append.drop(columns = ['coin', 'value_tmp'], inplace = True)

    # Adding date column, and changing date to the dataframe index:
    # holdings.insert(0, 'date', pd.to_datetime('today').strftime('%Y-%m-%d'))
    holdings_append.insert(0, 'date', pd.to_datetime('now').replace(microsecond=0))
    holdings_append.date = pd.to_datetime(holdings_append.date)
    holdings_append = holdings_append.set_index('date').sort_index()

    # printing out result, and saving to csv and Excel.
    return holdings_append

    # holdings.to_csv("account_holdings_index_test.csv")
    # holdings.to_csv("account_holdings_no_index.csv", index = False)


    # holdings.to_excel("account_holdings_index.xlsx")
    # holdings.to_excel("account_holdings_no_index.xlsx", index = False)

print("CSV written successfully.")
    
holdings_append = kucoin_append()   


# THIS CODE works to append to the csv file itself. Only works if there is an existing file. I will add the if statement later that'll check if a file exists and create a new one, or use the append function:
holdings_append.to_csv('data.csv', mode = 'a', header = False)

print("File appended")

# Uploading to Google sheets

import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(credentials)

spreadsheet = client.open('Crypto-Data')

with open('data.csv', 'r') as file_obj:
    content = file_obj.read()
    client.import_csv(spreadsheet.id, data=content)
    
print("Google sheet updated with newest data.")

# Updating the local SQLite database.
import sqlite3 as sql
import pandas as pd

# This line must be run first to setup the connection.
conn = sql.connect('/Users/luke/projects/github/algo-trading-experiments/kucoin.db')

# This code checks to see if the SQLite database has a table named "holdings".
holdings_test = pd.read_sql("SELECT * FROM sqlite_master WHERE type = 'table' AND name = 'holdings';", conn)

# Now the code checks if the table exists, and if so appends the newest holdings dataframe to the sqlite database.
if holdings_test.name.count() > 0:
    holdings_append.to_sql('holdings', con = conn, if_exists = 'append')
else:
    # This line creates a table called "holdings" if the table doesn't exist.
    holdings_append.to_sql('holdings', con = conn)
    
import time

t = int(5)

def countdown(t):
    print(f"Script will exit in {t} seconds")
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end = "\r")
        time.sleep(1)
        t -= 1
    print("Limitless Holdings database and Google Sheets have been updated. Have a nice day!")
    
countdown(t)
