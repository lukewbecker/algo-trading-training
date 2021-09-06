# This script prints out "Hello World!" and writes it to a .csv


import pandas as pd
import time

words_to_print = "Hello World!"

print(words_to_print)

pd.to_csv('hello_word.csv')