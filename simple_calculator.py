# Simple Calculator in Python

import numpy
import math

def welcome():
    print('''Welcome to my calculator, 100% made in Python.''')

def calculate():
    
    operation = input('''
    Please type in the math operation you would like to complete:
    + for addition
    - for subtraction
    * for multiplication
    / for division
    ''')

    number_1 = int(input("Enter the first number: "))
    number_2 = int(input("Enter the second number: "))

    if operation == '+':
        print('{} + {} = '.format(number_1, number_2))
        print(number_1 + number_2)

    elif operation == '-':
        print('{} - {} = '.format(number_1, number_2))
        print(number_1 - number_2)

    elif operation == '*':
        print('{} * {} = '.format(number_1, number_2))
        print(number_1 * number_2)

    elif operation == '/':
        print('{} / {} = '.format(number_1, number_2))
        print(number_1 / number_2)

    else:
        print("You have not typed a valid operator, please run the program again.")

def again():
    
    calc_again = input('''
    Do you want to run the calculator again? Please type Y for Yes or N for No.
    ''')
    
    # If the user types "Y"
    if calc_again == 'Y':
        calculate()
        
    elif calc_again == 'N':
        print("Thanks for using my calculator!")
    
    else:
        again()

welcome()
calculate()
again()