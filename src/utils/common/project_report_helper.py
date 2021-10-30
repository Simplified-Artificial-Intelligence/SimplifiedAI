

from flask import Flask, redirect, url_for, render_template, request, session
from src.utils.databases.mysql_helper import MySqlHelper



class ProjectReports:    
    @staticmethod
    def insert_record_eda(actionName, input='', output='',isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query=f"""INSERT INTO tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`) VALUES ('{session.get('id')}','2','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            
            rowcount = mysql.insert_record(query)
        except Exception as e:
            print(e)
        
        
    @staticmethod
    def insert_record_dp(actionName, input='', output='',isSuccessed=1, errorMessage=''):
        try:
            mysql = MySqlHelper.get_connection_obj()

            query=f"""INSERT INTO tblProjectReports(`Projectid`, `ModuleId`, `ActionName`, `Input`, `IsSuccessed`, `Output`, `ErrorMessage`) VALUES ('{session.get('id')}','2','{actionName}','{input}',{isSuccessed},'{output}','{errorMessage}')"""
            
            rowcount = mysql.insert_record(query)
        except Exception as e:
            print(e)

    
    @staticmethod
    def add_active_module(moduleId):
        # if 'mysql' not in st.session_state:
        #     ProjectReports.make_mysql_connection()
        # print("called")
        # mysql=st.session_state['mysql']
        # query=f"""Update tblProjects SET Status={moduleId} Where Id={session.get('id')}"""
        # rowcount = mysql.insert_record(query)
        pass
        