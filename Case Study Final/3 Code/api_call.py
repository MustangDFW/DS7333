#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 23:07:57 2020

@author: bablanchard
"""

import json
import requests
import pandas as pd
from datetime import timezone

header = {'Content-Type': 'application/json', \
                  'Accept': 'application/json'}

def load_process_data():
    
    hold_out_df = pd.read_csv('hold_out_data.csv')
    
    date_fields = [
            'launched',
            'deadline',
    ]
    
    for d in date_fields:
        hold_out_df[d] = pd.to_datetime(hold_out_df[d])
        hold_out_df[d] = hold_out_df[d].apply(lambda x: x.replace(tzinfo=timezone.utc).timestamp()).astype(int)
        
    return hold_out_df

def get_scoring_instances(scoring_df, single_instance = True, batch_values = 5):
    
    if single_instance:
        instances = scoring_df.sample()
        instance_dict = instances.to_json(orient='records')
    else:
        instances = scoring_df.head(batch_values)
        get_keys = instances.columns.tolist()
        get_values = instances.values.tolist()
        
        dict_list = []
        for x in range(0,len(get_values)):
            df_dict = {get_keys[i]: get_values[x][i] for i in range(len(get_keys))}
            dict_list.append(df_dict)
            
        instance_dict = json.dumps(dict_list)
        
    return instance_dict, instances

def call_model(records_to_score):
    
    resp = requests.post("http://127.0.0.1:8080/predict", \
                        data = json.dumps(records_to_score),\
                        headers= header)    

    if resp.status_code == 200:
        print(resp.status_code)
        pred_values = resp.json()
        pred_values = pd.read_json(pred_values['predictions'], orient='records')
    else:
        print(resp.status_code)

    return pred_values

def manual_load():

    # Load JSON natively
    dframe = [{
               "ID":1177451632,
               "name":"The Everyday Project",
               "category":"Experimental",
               "main_category":"Film & Video",
               "currency":"USD",
               "deadline":1403136000,
               "goal":50.0,
               "launched":1400627298,
               "pledged":223.0,
               "state":"successful",
               "backers":35,
               "country":"US",
               "usd pledged":223.0,
               "usd_pledged_real":223.0,
               "usd_goal_real":50.0,
               "launch_month":8,
               "launch_dow":5,
               "duration":21,
    }]
    dframe = json.dumps(dframe)
    
    resp = requests.post("http://127.0.0.1:8080/predict", \
                        data = json.dumps(dframe),\
                        headers= header)
    
    if resp.status_code == 200:
        print(resp.status_code)
        pred_values = resp.json()
        pred_values = pd.read_json(pred_values['predictions'], orient='records')
    else:
        print(resp.status_code)
        
    scoring_records = pd.read_json(dframe)
    actuals_with_predictions = pd.concat([scoring_records.reset_index(drop=True), pred_values], axis=1)
    return actuals_with_predictions

def main():
    
    scoring_dataset = load_process_data()   
    scoring_json, scoring_records = get_scoring_instances(scoring_dataset, single_instance = False, batch_values = 10)
    scored_values = call_model(scoring_json)

    actuals_with_predictions = pd.concat([scoring_records.reset_index(drop=True), scored_values], axis=1)
    return actuals_with_predictions

##############################################################################################################
##### Execute the Main Function ##############################################################################
##############################################################################################################

#if __name__ == "__main__":    
#    main()

#### Local Testing ####
#actuals_with_predictions_manual = manual_load()
    

