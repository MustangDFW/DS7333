#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 20:54:54 2020

@author: bblanchard
"""

import os
import pandas as pd
import logging
import logging.config
import pickle

# Start the logger
logging.config.dictConfig({
    'version':1,
    'disable_existing_loggers': False,
    'handlers':{
        'fileHandler':{
            'class': 'logging.FileHandler',
            'formatter': 'myFormatter',
            'filename': 'app_log.txt'
        }
    },        
    'loggers':{
        '':{
            'handlers': ['fileHandler'],
            'level': 'DEBUG'
        }
    },
    'formatters':{
        'myFormatter':{
            'format': '%(levelname)s - %(asctime)s - Module: %(module)s - %(message)s',
            'datefmt': '%m-%d-%Y %I:%M:%S %p'
        }
    }
})

LOGGER = logging.getLogger(__name__)

########################################
##### Utility functions
########################################

def get_cwd():
    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        LOGGER.info('Successfully mapped to the script directory')
    except:
        os.chdir('/Users/bblanchard006/Downloads/All Data by State')
        LOGGER.info('Directory successfully mapped to the local directory')

    active_dir = os.getcwd()
    return active_dir

def main():
    
    get_cwd()
    files = os.listdir()
    
    print('Collecting State Abbreviations')
    state_abbr = pd.read_csv('state_abbreviations.csv')
    state_abbr.set_index('Description',inplace=True)
    state_abbr = state_abbr.to_dict()['Code']
    LOGGER.info('State abbreviations collected')
    
    print('Collecting NAICS Code Mappings')
    naics_map = pd.read_csv('2-6 digit_2017_Codes.csv')
    naics_map['2017 NAICS US   Code'] = naics_map['2017 NAICS US   Code'].astype(int).astype(str)
    naics_map.set_index('2017 NAICS US   Code',inplace=True)
    naics_map = naics_map.to_dict()['2017 NAICS US Title']
    LOGGER.info('NAICS code mapping completed')
    
    small_loans_list = []
    
    print('Compiling State Level Loan Data')
    for key, value in state_abbr.items():
        if key in files:
            print('Gathering {} Loan Data - <$150k'.format(key))
            temp_source = 'foia_up_to_150k_'+value+'.csv'
            temp_df = pd.read_csv(os.getcwd()+os.sep+key+os.sep+temp_source)
            temp_df['Source File'] = temp_source
            temp_df['Loan Category'] = 'Under $150k'
            small_loans_list.append(temp_df)
            LOGGER.info('{} Loan Data - <$150k processed successfully'.format(key))
    
    small_loans_df = pd.concat(small_loans_list, sort=False)    
    LOGGER.info('Small loan dataframe created')
    
    print('Compiling >$150k Loan Data - All States')
    large_loans_df = pd.read_csv(os.getcwd()+os.sep+'150k plus'+os.sep+'foia_150k_plus.csv')
    large_loans_df['Source File'] = 'foia_150k_plus.csv'
    large_loans_df['Loan Category'] = 'Over $150k'
    LOGGER.info('Large loan dataframe created')
    
    print('Consolidating Loan Data')
    all_loans_df = pd.concat([small_loans_df, large_loans_df], sort=False)
    LOGGER.info('Loan frame consolidated successfully')
        
    all_loans_df['NAICSCode'] = all_loans_df['NAICSCode']
    all_loans_df['NAICS Description'] = all_loans_df['NAICSCode'].astype(str).str[:6].map(naics_map)
    all_loans_df['NAICS Category'] = all_loans_df['NAICSCode'].astype(str).str[:2].map(naics_map)
    all_loans_df['NAICS Sub-Category'] = all_loans_df['NAICSCode'].astype(str).str[:3].map(naics_map)
    
    sample = all_loans_df.sample(frac=0.01)
    sample.to_csv('Sample PPP Loans.csv', index=False)
    
    print('Writing Loan Data to Local Directory')
    all_loans_df.to_csv('All PPP Loans.csv', index=False)
    LOGGER.info('Loan frame successfully saved locally')


########################################
##### Executable function
########################################

if __name__ == '__main__':
    main()
    
    