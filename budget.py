#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function
from datetime import datetime
#from numba import jit # numba compiles Python code into optimized machine code while leveraging Just-in-Time compilation process
#from tdqm import tdqm # Progress bar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sqlite3
import timeit # %timeit before commands to check time

""" Budgeting """

#------------------------------------------------------------------------------
# Plotting parameters
#------------------------------------------------------------------------------
# rc: run command / runtime configuration
# plt.rcParams.keys() to print available **kwargs
# plt.rcdefaults() to reset parameters to default
params = {# Figure
          'figure.figsize': [20, 15],
          'figure.dpi': 300,
          'figure.autolayout': True, # tight_layout()          
          # Font
          'font.family': 'serif',
          'font.size': 30,
          'font.serif': 'Computer Modern Roman',          
          # Axes
          'axes.titlesize': 30,
          'axes.labelsize': 30,
          # Ticks
          'xtick.labelsize': 20,
          'xtick.major.size': 20,
          'xtick.minor.size': 20,
          'ytick.labelsize': 20,
          'ytick.major.size': 20,
          'ytick.minor.size': 20,          
          # Legend
          'legend.loc': 'best',
          'legend.fancybox': True,          
          # Backend
          'agg.path.chunksize': 10000, # Prevent hard coded limit overflowing when saving plots as .pdf
          'backend': 'pdf',
          'savefig.directory': 'Plots/',
          'savefig.format': 'pdf',
          'savefig.dpi': 300,
          'text.usetex': True,
          }
plt.rcParams.update(params)
del params


#------------------------------------------------------------------------------
# TODO:
# Data aggregation: import from downloaded CSV data
#------------------------------------------------------------------------------
#data_location = './Budget_Data/'


#------------------------------------------------------------------------------
# Data aggregation: manually input income
#------------------------------------------------------------------------------
# Monthly, rounding to 2 decimal places
monthly_income_gross = 3058.46
monthly_income_net = np.round(monthly_income_gross*0.62230215827, 2)

# Annual, rounding to 2 decimal places
annual_income_gross = np.round(monthly_income_gross*13.92, 2)
annual_income_net = np.round(monthly_income_net*13.92, 2)

# Available budget per month
available_needs = np.round(monthly_income_net*0.5, 2) # Rent, utilities
available_wants = np.round(monthly_income_net*0.25, 2) # Food, pocket money
available_savings = np.round(monthly_income_net*0.1, 2) # High-yield savings account
available_investments = np.round(monthly_income_net*0.1, 2) # ETFs
available_investments_options = np.round(monthly_income_net*0.05, 2) # Options

print(
f'''Budget allocation: 50% on needs, 30% on wants, 20% on savings.
Income: €{monthly_income_net:.2f}/month:
€{available_needs:.2f} available for needs,
€{available_wants:.2f} available for wants,
€{available_savings:.2f} available for savings,
€{available_investments:.2f} available for investments (ETFs),
€{available_investments_options:.2f} available for investments (options).'''
)


#------------------------------------------------------------------------------
# Data aggregation: use SQL to import expenditures from database
#------------------------------------------------------------------------------
# Personal use, updating db locally. SQLite is fine as it is abstraction around a single file
# MySQL is overkill since there aren't multiple users writing to single database   
    
# Do NOT use f-strings, format(), or %-style formatting in SQL queries,
# as it opens up vulnerability to SQL injection.

def init():
    '''
    Use SQLite3 to connect to database file.
    Creates an expenses table in file (YYYY-MM-mmm).db if it does not already exist.
    '''
    # Use current year and month as filename
    filename = datetime.now().strftime('%Y-%m-%b')
    # TODO: change f-string to scrubbed string
    conn = sqlite3.connect(f'./Budget_Data/{filename}.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses(
                    category string,
                    amount number,
                    notes string,
                    date string)''')
    conn.commit()
    c.close()
    conn.close()
    pass


def log(category, amount, notes=''):
    '''
    Log an expenditure into the database
    
    INPUTS:
        category: string
        amount: float
        notes (optional): string
    '''
    filename = datetime.now().strftime('%Y-%m-%b')
    conn = sqlite3.connect(f'./Budget_Data/{filename}.db')
    c = conn.cursor()
    
    category = str(category).lower()
    notes = str(notes).capitalize()
    date = str(datetime.now())
    params = (category, amount, notes, date)
    
    c.executemany('INSERT INTO expenses VALUES (?,?,?,?)', (params,))
    conn.commit()
    c.close()
    conn.close()
    pass


def view(keyword=None):
    '''
    Views all expenditures (of a specified category if given)
    
    INPUTS:
        keyword (string): category or notes search for.
    '''
    filename = datetime.now().strftime('%Y-%m-%b')
    conn = sqlite3.connect(f'./Budget_Data/{filename}.db')
    c = conn.cursor()
    
    if keyword:
        keyword = str(keyword).lower()
        c.execute('SELECT * FROM expenses WHERE category=? ORDER BY amount DESC', (keyword,))
        results = c.fetchall()
        c.execute('SELECT sum(amount) FROM expenses WHERE category=?', (keyword,))
        total = c.fetchone()[0]
        for i, v in enumerate(results):
            print(results[i], '\n')
        print(f'Total spent on {keyword}: €{total:.2f}')
    
    else:
        c.execute('SELECT * FROM expenses ORDER BY amount DESC')
        results = c.fetchall()
        c.execute('SELECT sum(amount) FROM expenses')
        total = c.fetchone()[0]    
        for i, v in enumerate(results):
            print(results[i], '\n')
        print(f'Total spent: €{total:.2f}')
    
    c.close()
    conn.close()
    pass

def total(keyword=None):
    '''
    Returns all expenditures (of a specified category if given)
    
    INPUTS:
        keyword (string): category or notes to search for
    
    OUTPUTS:
        total (float): total expenses (in category)
    '''
    filename = datetime.now().strftime('%Y-%m-%b')
    conn = sqlite3.connect(f'./Budget_Data/{filename}.db')
    c = conn.cursor()    
    if keyword:
        keyword = str(keyword).lower()
        c.execute('SELECT sum(amount) FROM expenses WHERE category=?', (keyword,))
    else:
        c.execute('SELECT sum(amount) FROM expenses')
    total = c.fetchone()[0]
    c.close()
    conn.close()
    return total


init()

log('needs', 800., 'rent')
log('needs', 100., 'electricity')
log('needs', 150., 'common costs: water, gas, and heating')
log('needs', 20., 'garbage')
log('needs', 30., 'insurance: health, personal, housing')
log('wants', 50., 'internet')
log('wants', 250.16, 'food')

view()
view('needs')
view('wants')

total()

needs_spent = total('needs')
wants_spent = total('wants')

#------------------------------------------------------------------------------
# Data aggregation: manually input expenditures
#------------------------------------------------------------------------------
# Class template for manual input instances
class Expenditure:    
    def __init__(self, name, amount, category, subcategory=None, notes=None):
        self.name = f'{name.capitalize()}'              # str.capitalize(name)
        self.amount = float('{:.2f}'.format(amount))    # 2 decimal places
        self.category = f'{category.capitalize()}'
        if subcategory:
            self.subcategory = f'{subcategory.capitalize()}'
        if notes:
            self.notes = f'{notes.capitalize()}'
        pass
    
    def create_from_input():
        return Expenditure(
        input('Expenditure name: '),
        float(input('Amount: €')),
        input('Expenditure category: ')
        )
    
    def total_in_category():
        # pseudocode: if category == category: np.sum(amount)
        total = None
        return total
    pass

# Manually input expenses
rent =          Expenditure('rent',800,'needs','rent')
electricity =   Expenditure('electricity',100,'needs','utilities')
common_costs =  Expenditure('common costs',150,'needs','utilities') # Water, gas, and heating
water =         Expenditure('water',30,'needs','utilities')
gas =           Expenditure('gas',20,'needs','utilities')
garbage =       Expenditure('garbage',20,'needs','utilities')
insurance =     Expenditure('insurance',30,'needs','insurance') # Health and housing insurance
internet =      Expenditure('internet',50,'needs','utilities')
food =          Expenditure('food',250,'needs','food')

# Basic version works.
# TODO: Convert class into writing into a persistant database


#------------------------------------------------------------------------------
# Data manipulation
#------------------------------------------------------------------------------
# Sum needs and check amount left. If over budget, take deficit from wants
needs_spent = rent.amount + electricity.amount + water.amount + gas.amount \
              + internet.amount + food.amount
needs_left = available_needs - needs_spent

if needs_left > 0:
    print(f'Needs left over after bills: €{needs_left:.2f}')
elif needs_left < 0:
    print(f'Needs over budget by: €({needs_left:.2f}) \n'
          f'Subtracting €({needs_left:.2f}) from wants budget.')
    available_wants += needs_left
    print(f'Updated: €{available_wants:.2f} available for wants')

# Wants
wants = Expenditure('wants',available_wants,'wants','wants')
"""
wants_spent = 0
print('Enter expenses (enter a blank line to exit): ')
while True:
    line = input()
    if line == '':
        break
    if line:
        manual_input = Expenditure.create_from_input()
        wants_spent += manual_input.amount

wants_left = available_wants - wants_spent
if wants_left > 0:
    print(f'Wants left over to go into savings: €{wants_left:.2f}')
elif wants_left < 0:
    print(f'Wants over budget by: €({wants_left:.2f})')
"""
# Savings
savings = Expenditure('savings',available_savings,'savings','savings')


#------------------------------------------------------------------------------
# Visualisation
#------------------------------------------------------------------------------
# Make working plot first before putting into functions
'''
# Plot needs into table
fig, ax = plt.subplots()

# hide axes
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')

needs_names = np.array([rent.name, electricity.name, water.name, \
                        gas.name, internet.name, food.name])
needs_amounts = np.array([rent.amount, electricity.amount, water.amount, \
                        gas.amount, internet.amount, food.amount])

# [needs_amounts] lets pandas know they are rows
df = pd.DataFrame([needs_amounts], columns=needs_names)
ax.table(cellText=df.values, colLabels=df.columns, loc='center')
fig.tight_layout()
plt.show()
'''

"""
@jit
def plot_pie(save_as):
    #pie_fig = plt.figure()
    #plot = pie_fig.add_subplot(111)
    
    # Make data: I have 3 groups and 7 subgroups
    group_names = ['Needs', 'Savings' , 'Wants']
    group_size = [available_needs, available_savings, available_wants]
    subgroup_names = [rent.name, electricity.name, water.name, gas.name,
                      internet.name, internet.name, food.name,
                      savings.name, wants.name]
    subgroup_size = [rent.amount, electricity.amount, water.amount, gas.amount, 
                      internet.amount, internet.amount, food.amount, 
                      savings.amount, wants.amount]
     
    # Create colors
    a, b, c=[plt.cm.Blues, plt.cm.Reds, plt.cm.Greens]
     
    # First Ring (outside)
    fig, ax = plt.subplots()
    ax.axis('equal')
    mypie, _ = ax.pie(group_size, radius=1.3, labels=group_names, colors=[a(0.6), b(0.6), c(0.6)] )
    plt.setp( mypie, width=0.3, edgecolor='white')
     
    # Second Ring (Inside)
    mypie2, _ = ax.pie(subgroup_size, radius=1.3-0.3, labels=subgroup_names, labeldistance=0.7, 
                       colors=[a(0.5), a(0.4), a(0.3), b(0.5), b(0.4), c(0.6), c(0.5), c(0.4), c(0.3), c(0.2)])
    plt.setp( mypie2, width=0.4, edgecolor='white')
    plt.margins(0,0)
     
    # show it
    plt.show()
    
    if save_as:
        pie_fig.savefig('Plots/{}_pie.pdf'.format(str(save_as)))
    
    return None
"""

#------------------------------------------------------------------------------
# End
#------------------------------------------------------------------------------
