import os
from flask import session
from pandas.core.tools.datetimes import Scalar
from src.utils.common.common_helper import load_project_encdoing, load_project_model, load_project_pca, load_project_scaler, read_config
from loguru import logger
from from_root import from_root
from src.utils.databases.mysql_helper import MySqlHelper
from src.preprocessing.preprocessing_helper import Preprocessing
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
import pandas as pd

config_args = read_config("./config.yaml")
log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")

mysql = MySqlHelper.get_connection_obj()

"""[Function to make prediction]
"""
def make_prediction(df):
    try:
            
        logger.info(f"Started Prediction!!1")
        if df is None:
            logger.info(f"DataFrame is null")
            raise Exception("Data Frame is None")
        else:
            query_ = f"""Select Name, Input,Output,ActionDate from  tblProject_Actions_Reports
                            Join tblProjectActions on tblProject_Actions_Reports.ProjectActionId=tblProjectActions.Id
                            where ProjectId={session['pid']}"""
            action_performed = mysql.fetch_all(query_)
            print(action_performed)
            
            feature_columns=[col for col in df.columns if col!=session['target_column']]
            df=df.loc[:,feature_columns]
            df_org=df
            
            if len(action_performed)>0:
                for action in action_performed:
                    if action[0]=='Delete Column':
                        df=Preprocessing.delete_col(df,action[1].split(","))
                    elif action[0]=='Change Data Type':
                        df=FeatureEngineering.change_data_type(df,action[1],action[2])
                    elif action[0]=='Column Name Change':
                        df=FeatureEngineering.change_column_name(df,action[1],action[2])
                    elif action[0]=='Encdoing':
                        encoder=load_project_encdoing()
                        columns=action[1].split(",")
                        df_=df.loc[:,columns]
                        df_=encoder.transform(df_)
                        df = Preprocessing.delete_col(df, columns)
                        frames = [df, df_]
                        df = pd.concat(frames,axis=1)
                    elif action[0]=='Scalling':
                        scalar=load_project_scaler()
                        columns=df.columns
                        df=scalar.transform(df)
                        df=pd.DataFrame(df,columns=columns)
                    elif action[0]=='PCA':
                        pca=load_project_pca()
                        columns=df.columns
                        df=pca.transform(df)
                        df=pd.DataFrame(df,columns=columns)
                    elif action[0]=='Custom Script':
                        if action[1] is not None:
                            exec(action[1])
                        
                model=load_project_model()
                result=model.predict(df)
                df_org.insert(loc=0, column=session['target_column'], value=result)
                return df_org
                    
            else:
                pass
            
            
        return df

    except Exception as e:
        logger.info('Error in Prediction '+str(e))
        raise e
    