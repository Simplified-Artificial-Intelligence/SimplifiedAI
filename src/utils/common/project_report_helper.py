

from flask import Flask, redirect, url_for, render_template, request, session

class ProjectReports:    
    @staticmethod
    def insert_record_eda(mysql,actionName, input='', output='',isSuccessed=1, errorMessage=''):
       try:
            query=f"""Update tblProjects SET Status=2 Where Id={session.get('id')}; INSERT INTO tblProjectReports(ProjectId,ModuleId,ActionName,Input,IsSuccessed,Output,ErrorMessage)
                    Values("{session.get('id')}","2","{actionName}","{input}",{isSuccessed},"{output}","{errorMessage}")"""
            rowcount = mysql.insert_record(query)
       except Exception as e:
           print(e)
        
        
    @staticmethod
    def insert_record_dp(mysql,actionName, input='', output='',isSuccessed=1, errorMessage=''):
        try:
            query=f"""Update tblProjects SET Status=3 Where Id={session.get('id')}; INSERT INTO tblProjectReports(ProjectId,ModuleId,ActionName,Input,IsSuccessed,Output,ErrorMessage)
                    Values("{session.get('id')}","3","{actionName}","{input}",{isSuccessed},"{output}","{errorMessage}")"""
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
        