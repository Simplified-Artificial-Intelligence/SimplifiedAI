from flask import Blueprint, redirect, url_for, render_template, request, session, send_file
from src.constants.model_params import DecisionTreeRegressor_Params, LinearRegression_Params, Ridge_Params, Lasso_Params, ElasticNet_Params, RandomForestRegressor_Params, SVR_params, AdabootRegressor_Params, GradientBoostRegressor_Params, Params_Mappings
from src.model.custom.classification_models import ClassificationModels
from src.model.custom.regression_models import RegressionModels
from src.model.custom.clustering_models import ClusteringModels
from werkzeug.wrappers import Response
from io import BytesIO
import re
from src.preprocessing.preprocessing_helper import Preprocessing
from src.constants.constants import REGRESSION_MODELS
from src.utils.databases.mysql_helper import MySqlHelper
from werkzeug.utils import secure_filename
import os
import time
from src.utils.common.common_helper import decrypt, get_param_value, read_config, unique_id_generator, Hashing, encrypt
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
from src.utils.common.data_helper import load_data, update_data, get_filename, csv_to_json, to_tsv, csv_to_excel
from src.eda.eda_helper import EDA
import numpy as np
import json
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
from src.routes.routes_api import app_api
from loguru import logger
from src.routes.routes_eda import app_eda
from src.routes.routes_dp import app_dp
from src.routes.routes_fe import app_fe
from sklearn.metrics import r2_score,mean_absolute_error,mean_squared_error,mean_squared_log_error
app_training= Blueprint('training', __name__)

@app_training.route('/model_training/<action>', methods=['GET'])
def model_training(action):
    try:
        if 'pid' in session:
            df = load_data()
            data = df.head().to_html()
            if df is not None:
                
                """Check If Prohect type is Regression or Calssificaion and target Columns is not Selected"""
                if session['project_type']!=3 and  session['target_column'] is None:
                        return redirect(url_for('/target-column'))
                    
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'train_test_split':
                    columns_for_list = df.columns
                    return render_template('model_training/train_test_split.html', data=data, columns=columns_for_list,
                                           action='train_test_split')
                elif action == 'auto_training':
                    data = df.head().to_html()
                    return render_template('model_training/auto_training.html', data=data,project_type=session['project_type'],target_column=session['target_column'])
                elif action == 'custom_training':
                    if session['project_type'] == 2:
                        return render_template('model_training/classification.html', action=action,models=REGRESSION_MODELS)
                    elif session['project_type'] == 1:
                        return render_template('model_training/regression.html', action=action,models=REGRESSION_MODELS)
                    elif session['project_type'] == 3:
                        return render_template('model_training/clustering.html')
                    else:
                        return render_template('model_training/custom_training.html')
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)




@app_training.route('/model_training/<action>', methods=['POST'])
def model_training_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'custom_training':
                    try:
                        model = request.form['model']
                        range=int(request.form['range'])
                        random_state=int(request.form['random_state'])
                        
                        target = session['target_column']
                        X = df.drop(target, axis=1)
                        y = df[target]
                        train_model_fun=None
                            
                        X_train, X_test, y_train, y_test = FeatureEngineering.train_test_Split(cleanedData=X,
                                                                                                label=y,
                                                                                                train_size=range/100,
                                                                                                random_state=random_state)
                        model_params={}
                        if model=="LinearRegression":
                            Model_Params=LinearRegression_Params 
                            train_model_fun=RegressionModels.linear_regression_regressor
                        elif model=="Ridge":
                            Model_Params=Ridge_Params 
                            train_model_fun=RegressionModels.ridge_regressor   
                        elif model=="Lasso":
                            Model_Params=Lasso_Params 
                            train_model_fun=RegressionModels.lasso_regressor
                        elif model=="ElasticNet":
                            Model_Params=ElasticNet_Params
                            train_model_fun=RegressionModels.elastic_net_regressor
                        elif model=="DecisionTreeRegressor":
                            Model_Params=DecisionTreeRegressor_Params 
                            train_model_fun=RegressionModels.decision_tree_regressor
                        elif model=="RandomForestRegressor":
                            Model_Params=RandomForestRegressor_Params 
                            train_model_fun=RegressionModels.random_forest_regressor
                        elif model=="SVR":
                            Model_Params=SVR_params 
                            train_model_fun=RegressionModels.svr_regressor                          
                        elif model=="AdaBoostRegressor":
                            Model_Params=AdabootRegressor_Params
                            train_model_fun=RegressionModels.ada_boost_regressor
                        elif model=="GradientBoostingRegressor":
                            Model_Params=GradientBoostRegressor_Params
                            train_model_fun=RegressionModels.gradient_boosting_regressor
                        else:
                            return 'Non-Implemented Action'
                        # if Model_Params == []:
                        #     return 'No model seleccted.'
                        for param in Model_Params:
                            model_params[param['name']]=get_param_value(param,request.form[param['name']])
                        print(model_params)
                        trained_model=train_model_fun(X_train,y_train,True,**model_params)
                        
                        reports=[{"key":"Model Name","value":model},
                            {"key":"Data Size","value":len(df)},
                            {"key":"Trained Data Size","value":len(X_train)},
                            {"key":"Test Data Size","value":len(X_test)}]
                        
                        scores=[]
                        if trained_model is not None:
                            y_pred=trained_model.predict(X_test)
                            scores.append({"key":"r2_score","value":r2_score(y_test,y_pred)})
                            scores.append({"key":"mean_absolute_error","value":mean_absolute_error(y_test,y_pred)})
                            scores.append({"key":"mean_squared_error","value":mean_squared_error(y_test,y_pred)})
                        
                            return render_template('model_training/model_result.html', action=action,status="success",
                                                   reports=reports,scores=scores,model_params=model_params)
                        else:
                            raise Exception("Model Couldn't train, please check parametes")    
                    except Exception as e:
                        return render_template('model_training/regression.html', action=action,models=REGRESSION_MODELS,status="error",msg=str(e))
                    return render_template('model_training/help.html')
                elif action == "auto_training":
                    pass
                else:
                    return "Non Implemented Method"
        else:
            logger.critical('DataFrame has no data')
    except Exception as e:
        logger.error(e)
