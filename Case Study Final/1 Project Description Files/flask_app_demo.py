#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 22:49:12 2020

@author: bablanchard
"""

from flask import Flask, jsonify, request
import pandas as pd
import os
import subprocess
import json

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    
    test_json = request.json
    test = pd.read_json(test_json, orient='records') 
    record_ids = test['ID']
    
    try:
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
    except:
        os.chdir('/Users/bblanchard006/Desktop/SMU/QTW/Week 13')
     
    gen_model_arg = os.getcwd() + os.sep + 'h2o-genmodel.jar'
    best_model_id = 'grid_25f24703_bddb_41c6_bcb5_e05f5e794442_model_42' # UPDATE MODEL ID HERE
    mojo_model_args = os.getcwd() + os.sep + best_model_id + '.zip'
    h2o_predictor_class = 'water.util.H2OPredictor'
    json_data = str(test_json)
    
    output = subprocess.check_output(['java' , '-Xmx4g', '-cp', gen_model_arg, h2o_predictor_class,mojo_model_args, json_data], shell=False).decode()   
    pf = pd.read_json(output, orient='records')
    full_frame = pd.concat([record_ids.reset_index(drop=True), pf], axis=1)
     
    responses = jsonify(predictions=full_frame.to_json(orient="records"))
    responses.status_code = 200

    return (responses)

@app.route("/answers") #allow both GET and POST requests
def answers():
    return '''
    <!DOCTYPE html>
    <html>
    <body>
    
    <h1>Campaign Inputs</h1>
    
    <form action="result" method="post">    

      Campaign Name: <input name="name" type="text" value="The Everyday Project"><br><br>
    
      Goal Amount: 1 <input type="range" min="1" max="50000" value="25000" class="slider" name="goal"> 50000
      <br><br>

      Month of Launch: <input name="launch_month" type="text" value="8"><br><br>
    
      Weekday of Launch: <input name="launch_dow" type="text" value="3""><br><br>
    
      Duration of Campaign: <input name="duration" type="text" value="21"><br><br>

      Select Main Category: <select name="main_category">
        <option value="Film & Video">Film & Video</option>
        <option value="Music">Music</option>
        <option value="Publishing">Publishing</option>
        <option value="Games">Games</option>
        <option value="Technology">Technology</option>
        <option value="Design">Design</option>
        <option value="Art">Art</option>
        <option value="Food">Food</option> 
        <option value="Fashion">Fashion</option>  
        </select>
      <br><br>

      Select Country: <select name="country">
        <option value="US">US</option>
        <option value="GB">GB</option>
        <option value="CA">CA</option>
        <option value="AU">AU</option>
      </select>
      <br><br>
      
      <input type="submit" value="Submit"><br>
    </form>
    
    </body>
    </html>
    '''

    return 

@app.route('/result', methods=['POST','GET'])
def result():

    if request.method == 'POST':
        name = request.form['name']
        main_category = request.form['main_category']
        goal = request.form['goal']
        country = request.form['country']
        launch_month = request.form['launch_month']
        launch_dow = request.form['launch_dow']
        duration = request.form['duration']

        dframe = [{
                   "name":name,
#                   "category":category,
                   "main_category":main_category,
                   "goal":goal,
                   "country":country,
                   "launch_month":launch_month,
                   "launch_dow":launch_dow,
                   "duration":duration,
        }]
        
        dframe = json.dumps(dframe)

    try:
        test_json = dframe
        test = pd.read_json(test_json, orient='records')

    except Exception as e:
        raise e
        
    gen_model_arg = os.getcwd() + os.sep + 'h2o-genmodel.jar'
    best_model_id = 'grid_25f24703_bddb_41c6_bcb5_e05f5e794442_model_42' # UPDATE MODEL ID HERE
    mojo_model_args = os.getcwd() + os.sep + best_model_id + '.zip'
    h2o_predictor_class = 'water.util.H2OPredictor'
    json_data = str(test_json)
    
    output = subprocess.check_output(['java' , '-Xmx4g', '-cp', gen_model_arg, h2o_predictor_class,mojo_model_args, json_data], shell=False).decode()   
    pf = pd.read_json(output, orient='records')

    full_frame = pd.concat([test.reset_index(drop=True), pf], axis=1)
    responses = jsonify(predictions=full_frame.to_json(orient="records"))
    responses.status_code = 200

    class_count = len(full_frame['classProbabilities'].iloc[0])  
    class_labels = []
    
    for c in range(class_count):
        class_labels.append('Class '+str(c+1)+' Probability')
    full_frame [class_labels] = pd.DataFrame(full_frame['classProbabilities'].values.tolist(), index= full_frame.index)   

    del full_frame['classProbabilities']
    full_frame = full_frame.rename(columns={'name':'Campaign Name','labelIndex':'Predicted Label ID','label':'Predicted Label'})
    full_frame_T = full_frame.T
    full_frame_T = full_frame_T.rename(columns={0:'Values'})
    html = (
        full_frame_T.style
        .set_properties(**{'font-size': '9pt'
                           , 'font-family': 'Calibri'
        })
        .render()
    )
    
    return html

if __name__ == '__main__':
    app.run(debug=True, port=8080)
     



