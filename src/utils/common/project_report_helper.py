import os
from src.utils.common.common_helper import read_config
from loguru import logger
from flask import session
from src.utils.databases.mysql_helper import MySqlHelper
from from_root import from_root
config_args = read_config("./config.yaml")

log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")


class ProjectReports:    
    @staticmethod
    def insert_record_eda(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
             VALUES ('{session.get('pid')}','2','{actionName}','{input}', {isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('id')} details uploaded successfully for EDA!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('pid')} details upload failed for EDA!")

    @staticmethod
    def insert_record_dp(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('pid')}','3','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('pid')} details uploaded successfully for Data Preprocessing!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('pid')} details upload failed for Data Preprocessing!")

    @staticmethod
    def insert_record_fe(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('pid')}','4','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('pid')} details uploaded successfully for Feature Engineering!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('pid')} details upload failed for Feature Engineering!")
    
    
    @staticmethod
    def insert_record_ml(actionName, input='', output='', isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`)
            VALUES ('{session.get('pid')}','5','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            logger.info(f"{session.get('pid')} details uploaded successfully for Machine Learning!")
            rowcount = mysql.insert_record(query)
        except Exception as e:
            logger.error(f"{session.get('pid')} details upload failed for Machine Learning!")
    
    @staticmethod
    def add_active_module(moduleId):
        # if 'mysql' not in st.session_state:
        # ProjectReports.make_mysql_connection()
        # print("called")
        # mysql=st.session_state['mysql']
        # query=f"""Update tblProjects SET Status={moduleId} Where Id={session.get('id')}"""
        # rowcount = mysql.insert_record(query)
        pass
    
        """[summary]
        Method To Add Project Actions Report
        """
    @staticmethod
    def insert_project_action_report(projectActionId, input='', output=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query = f"""INSERT INTO 
            tblProject_Actions_Reports(`ProjectId`, `ProjectActionId`, `Input`, `Output`)
            VALUES ('{session.get('pid')}','{projectActionId}','{input}','{output}')"""
            
            rowcount = mysql.insert_record(query)
        except Exception as e:
            print(e)
