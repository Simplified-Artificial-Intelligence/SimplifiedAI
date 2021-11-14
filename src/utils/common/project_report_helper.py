import os
from src.utils.common.common_helper import read_config
from loguru import logger
from flask import session
from src.utils.databases.mysql_helper import MySqlHelper
from from_root import from_root
import pandas as pd
config_args = read_config("./config.yaml")

log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")


class ProjectReports:   
    projectStatus = [{'key': 1, 'value': 'Initialized'}, {'key': 2, 'value': 'EDA'}, {'key': 3, 'value': 'Data Processing'}, {'key': 4, 'value': 'Feature Engineering'}, {'key': 5, 'value': 'Model Training'}]

    @staticmethod
    def insert_record_eda(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
             VALUES ('{session.get('id')}','2','{actionName}','{input}', {isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('id')} details uploaded successfully for EDA!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('id')} details upload failed for EDA!")

    @staticmethod
    def insert_record_dp(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('id')}','3','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('id')} details uploaded successfully for Data Preprocessing!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('id')} details upload failed for Data Preprocessing!")

    @staticmethod
    def insert_record_fe(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('id')}','4','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('id')} details uploaded successfully for Feature Engineering!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('id')} details upload failed for Feature Engineering!")
    
    
    @staticmethod
    def insert_record_ml(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('id')}','5','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('id')} details uploaded successfully for Machine Learning!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('id')} details upload failed for Machine Learning!")
    
    @staticmethod
    def add_active_module(moduleId):
        # if 'mysql' not in st.session_state:
        # ProjectReports.make_mysql_connection()
        # print("called")
        # mysql=st.session_state['mysql']
        # query=f"""Update tblProjects SET Status={moduleId} Where Id={session.get('id')}"""
        # rowcount = mysql.insert_record(query)
        pass

    @staticmethod
    def get_record_by_pid(pid, moduleId):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""SHOW COLUMNS FROM tblProjectReports"""
            columns = mysql.fetch_all(query)
            columns = pd.DataFrame(columns)[0].tolist()
            columns.insert(3, 'Module Name')
            columns = columns[3:]

            # query = f"""select tblProjectStatus.Name, tblProjectReports.ActionName, tblProjectReports.Input, tblProjectReports.IsSuccessed, tblProjectReports.Output, tblProjectReports.ErrorMessage, tblProjectReports.CreateDate from tblProjectReports join tblProjectStatus on (tblProjectReports.ModuleId=tblProjectStatus.Id) where tblProjectReports.Projectid = {pid}"""
            # if moduleId != 0:
            #     query = query + f""" and tblProjectReports.ModuleId = {moduleId}"""

            query = f"""select tblProjectStatus.Name, tblProjectReports.ActionName, tblProjectReports.Input, tblProjectReports.IsSuccessed, tblProjectReports.Output, tblProjectReports.ErrorMessage, tblProjectReports.CreateDate from tblProjectReports join tblProjectStatus on (tblProjectReports.ModuleId=tblProjectStatus.Id) where tblProjectReports.Projectid = 33 and tblProjectReports.ModuleId = 3"""
            records = mysql.fetch_all(query)
            records = pd.DataFrame(records, columns=columns)

            logger.info(f"{session.get('id')} details fetched successfully!!!")
            
            return records, ProjectReports.projectStatus
        except Exception as e:
            logger.error(f"{session.get('id')} details upload failed for EDA!")
