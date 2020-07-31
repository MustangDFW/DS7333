#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 14:22:55 2020
@author: bablanchard
"""

import pandas as pd
import subprocess
import os
import json
from datetime import timezone

# Set your working directory (should be the folder containing your model and jar files)
os.chdir('/Users/bblanchard006/Desktop/SMU/QTW/Week 13')

# Read in the raw data
hold_out_df = pd.read_csv('hold_out_data.csv')

hold_out_df['launched'] = pd.to_datetime(hold_out_df['launched'])
hold_out_df['launched'] = hold_out_df['launched'].apply(lambda x: x.replace(tzinfo=timezone.utc).timestamp()).astype(int)

hold_out_df['deadline'] = pd.to_datetime(hold_out_df['deadline'])
hold_out_df['deadline'] = hold_out_df['deadline'].apply(lambda x: x.replace(tzinfo=timezone.utc).timestamp()).astype(int)

# The following lines allow you to score a single record with your model
single_instance = hold_out_df.head(1)

get_keys = single_instance.columns.tolist()
get_values = single_instance.head(1).values.tolist()

df_dict = {get_keys[i]: get_values[0][i] for i in range(len(get_keys))} 
df_dict = json.dumps(df_dict)

# These are the inputs needed to make the subprocess call
gen_model_arg = os.getcwd() + os.sep + 'h2o-genmodel.jar'
best_model_id = 'grid_25f24703_bddb_41c6_bcb5_e05f5e794442_model_42' # Change the model id if you build your own
mojo_model_args = os.getcwd() + os.sep + best_model_id + '.zip'
h2o_predictor_class = 'water.util.H2OPredictor'
json_data = str(df_dict)

# Excecute the scoring
output = subprocess.check_output(['java' , '-Xmx4g', '-cp', gen_model_arg, h2o_predictor_class,mojo_model_args, json_data], shell=False).decode()   

# Format the results in a dataframe for additional analysis
pf = pd.read_json(output, orient='index')

# The following lines allow you to score a batch file using your model
batch_instance = hold_out_df.head(10)

get_keys = batch_instance.columns.tolist()
get_values = batch_instance.values.tolist()

dict_list = []
for x in range(0,len(get_values)):
    df_dict = {get_keys[i]: get_values[x][i] for i in range(len(get_keys))}
    dict_list.append(df_dict)
    
df_dict = json.dumps(dict_list)

# These are the inputs needed to make the subprocess call
gen_model_arg = os.getcwd() + os.sep + 'h2o-genmodel.jar'
best_model_id = 'grid_25f24703_bddb_41c6_bcb5_e05f5e794442_model_42' # Change the model id if you build your own
mojo_model_args = os.getcwd() + os.sep + best_model_id + '.zip'
h2o_predictor_class = 'water.util.H2OPredictor'
json_data = str(df_dict)

# Excecute the scoring
output = subprocess.check_output(['java' , '-Xmx4g', '-cp', gen_model_arg, h2o_predictor_class,mojo_model_args, json_data], shell=False).decode()   

# Format the results in a dataframe for additional analysis
pf = pd.read_json(output, orient='records')

