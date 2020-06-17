#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:51:56 2019

@author: bblanchard006
"""

import pandas as pd
import os
import copy
import pandas_profiling

os.chdir('/Users/bblanchard006/Desktop/SMU/QTW/Week 7')
os.getcwd()

df = pd.read_csv('car_data.txt', sep='\t')
df.columns.tolist()
df.profile_report(title="Auto Dataset")

#Q1: What is the maximum and minimum mpg for Ford and Chevy cars with more than 150 HP?

# One Options
car_makes = list(set(list(df.Auto)))

ford = [x for x in car_makes if 'Ford' in x]
chevy = [x for x in car_makes if 'Chev' in x]

ford_chevy_cars = ford + chevy

ford_chevy_df = df[df['Auto'].isin(ford_chevy_cars)]

# Another Option
ford_chevy_df = df[(df.Auto.str.contains('Ford') | df.Auto.str.contains('Chev'))]

meet_hp_reqs = ford_chevy_df[ford_chevy_df.HP > 150] # None
meet_hp_reqs = ford_chevy_df[ford_chevy_df.HP > 120] # 3 left
meet_hp_reqs['MPG'].min() # 17
meet_hp_reqs['MPG'].max() # 19.2

# and Another Option

df[(df.Auto.str.contains('Ford') | df.Auto.str.contains('Chev')) & (df.HP > 120)]['MPG'].min() # 17
df[(df.Auto.str.contains('Ford') | df.Auto.str.contains('Chev')) & (df.HP > 120)]['MPG'].max() # 19.2

#Q2: What is the median weight of cars in produced in 1970, 1972, and 1974?

# No data

#Q3: What are all the non-American cars with displacement >100 but not more than 200?

# No data

#Q4: What is the average MPG for each year for 6 cylinder cars? Do not include 1974. Or Fords.

# No yearly data; calculate in aggregate

new_df = copy.deepcopy(df)
new_df['Ford_Filter'] = new_df['Auto'].apply(lambda x: 1 if 'Ford' in x else 0)
new_df['MPG'].mean() # 24.76052631578947
new_df[new_df['Ford_Filter'] == 0]['MPG'].mean() # 25.27647058823529
