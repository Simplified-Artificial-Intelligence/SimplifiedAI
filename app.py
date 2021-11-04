from enum import unique
from dns.rcode import NOERROR
from flask import Flask, redirect, url_for, render_template, request, session,jsonify
import re
from src.preprocessing.preprocessing_helper import Preprocessing
from src.constants.constants import NUMERIC_MISSING_HANDLER, OBJECT_MISSING_HANDLER, TWO_D_GRAPH_TYPES
from src.utils.databases.mysql_helper import MySqlHelper
from werkzeug.utils import secure_filename
import os
import time
from src.utils.common.common_helper import decrypt, read_config, unique_id_generator, Hashing, encrypt
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
from logger.logger import Logger
from src.utils.common.data_helper import load_data, update_data
from src.eda.eda_helper import EDA
import numpy as np
import json
import plotly
import plotly.figure_factory as ff
from pandas_profiling import ProfileReport
from src.utils.common.plotly_helper import PlotlyHelper
from src.utils.common.project_report_helper import ProjectReports
from src.utils.common.common_helper import immutable_multi_dict_to_str
from sklearn.model_selection import train_test_split
from src.model.auto.Auto_regression import ModelTrain_Regression
from sklearn.preprocessing import StandardScaler
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
log = Logger()
log.info(log_type='INFO', log_message='Check Configuration Files')

# Yaml Config File
config_args = read_config("./config.yaml")

# common Root Path
common_path = config_args['logs']['logger']

# Admin Path Setting
admin_log_file_path = config_args["logs"]['adminlogs_dir']
admin_file_name = config_args["logs"]['adminlogs_file']
admin_path = os.path.join(common_path, admin_log_file_path, admin_file_name)
# user Path Setting
user_log_file_path = config_args["logs"]['adminlogs_dir']
user_file_name = config_args["logs"]['adminlogs_file']
user_path = os.path.join(common_path, admin_log_file_path, admin_file_name)

# SQL Connection code
host = config_args['secrets']['host']
port = config_args['secrets']['port']
user = config_args['secrets']['user']
password = config_args['secrets']['password']
database = config_args['secrets']['database']

# mysql = MySqlHelper(host, port, user, password, database)
mysql = MySqlHelper.get_connection_obj()
mongodb = MongoHelper()

template_dir = config_args['dir_structure']['template_dir']
static_dir = config_args['dir_structure']['static_dir']

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
log.info(log_type='INFO', log_message='App Started')

app.secret_key = config_args['secrets']['key']
app.config["UPLOAD_FOLDER"] = config_args['dir_structure']['upload_folder']
app.config["MAX_CONTENT_PATH"] = config_args['secrets']['MAX_CONTENT_PATH']


@app.context_processor
def context_processor():
    loggedin = False
    if 'loggedin' in session:
        loggedin = True

    return dict(loggedin=loggedin)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if 'loggedin' in session:
            query = f'''
            select tp.Id,tp.Name,tp.Description,tp.Cassandra_Table_Name,ts.Name,ts.Indetifier,tp.Pid
            from tblProjects as tp
            join tblProjectStatus as ts
            on ts.Id=tp.Status
            where tp.UserId={session.get('id')} and tp.IsActive=1
            order by 1 desc;'''

            projects = mysql.fetch_all(query)
            project_lists = []

            for project in projects:
                projectid = encrypt(f"{project[6]}&{project[0]}").decode("utf-8")
                project_lists.append(project + (projectid,))

            return render_template('index.html', projects=project_lists)
        else:
            return redirect(url_for('login'))
    except Exception as e:
        pass


@app.route('/project', methods=['GET', 'POST'])
def project():
    global status
    try:
        if 'loggedin' in session:
            if request.method == "GET":
                return render_template('new_project.html', loggedin=True)
            else:
                name = request.form['name']
                description = request.form['description']
                f = request.files['file']

                ALLOWED_EXTENSIONS = ['csv', 'tsv', 'json', 'xml']
                msg = ''
                if not name.strip():
                    msg = 'Please enter project name'
                elif not description.strip():
                    msg = 'Please enter project description'
                elif f.filename.strip() == '':
                    msg = 'Please select a file to upload'
                elif f.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                    msg = 'This file format is not allowed, please select mentioned one'
                if msg:
                    return render_template('new_project.html', msg=msg)

                filename = secure_filename(f.filename)
                file_path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(file_path)
                timestamp = round(time.time() * 1000)
                name = name.replace(" ", "_")
                table_name = f"{name}_{timestamp}"
                
                df=pd.read_csv(file_path)
                project_id=unique_id_generator()
                inserted_rows=mongodb.create_new_project(project_id,df)
                               
                if inserted_rows>0:
                    userId = session.get('id')
                    status = 1
                    query = f"""INSERT INTO tblProjects (UserId, Name, Description, Status, 
                   Cassandra_Table_Name,Pid) VALUES
                   ("{userId}", "{name}", "{description}", "1", "{table_name}","{project_id}")"""

                    rowcount = mysql.insert_record(query)
                    if rowcount > 0:
                        return redirect(url_for('index'))
                    else:
                        msg = "Error while creating new Project"
                return render_template('new_project.html', msg=msg)
        else:
            return redirect(url_for('login'))

    except Exception as e:
        pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    global msg
    if 'loggedin' in session:
        log.info(log_type='ACTION', log_message='Redirect To Main Page')
        return redirect('/')
    else:
        if request.method == "GET":
            log.info(log_type='ACTION', log_message='Login Template Rendering')
            return render_template('login.html')
        else:
            if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
                email = request.form['email']
                password = request.form['password']
                account = mysql.fetch_one(
                    f'SELECT * FROM tblUsers WHERE Email = "{email}" AND Password = "{Hashing.hash_value(password)}"')
                if account:
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    log.info(log_type='INFO', log_message='Login Successful')
                    return redirect('/')
                else:
                    msg = 'Incorrect username / password !'
                    log.info(log_type='ERROR', log_message=msg)
            return render_template('login.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    else:
        if request.method == "GET":
            log.info(log_type='ACTION', log_message='Signup Template Rendering')
            return render_template('signup.html')
        else:
            msg = None
            if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
                username = request.form['username']
                password = request.form['password']
                confirm_password = request.form['confirm-password']
                email = request.form['email']
                account = mysql.fetch_one(f'SELECT * FROM tblUsers WHERE Email = "{email}"')
                log.info(log_type='ACTION', log_message='Checking Database')
                if account:
                    msg = 'EmailId already exists !'
                    log.info(log_type='ERROR', log_message=msg)
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address !'
                    log.info(log_type='ERROR', log_message=msg)
                elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'Username must contain only characters and numbers !'
                    log.info(log_type='ERROR', log_message=msg)
                elif not username or not password or not email:
                    msg = 'Please fill out the form !'
                    log.info(log_type='ERROR', log_message=msg)
                elif confirm_password != password:
                    msg = 'Password and Confirm password are not same!'
                    log.info(log_type='ERROR', log_message=msg)
                else:
                    hashed_password = Hashing.hash_value(password)
                    # PANKAJ AUTH TOKEN PENDING
                    rowcount = mysql.insert_record(
                        f'INSERT INTO tblUsers (Name, Email, Password, AuthToken) VALUES ("{username}", "{email}", "{hashed_password}", "pankajtest")')
                    log.info(log_type='INFO', log_message='Data added successful')
                    if rowcount > 0:
                        return redirect(url_for('login'))
            elif request.method == 'POST':
                msg = 'Please fill out the form !'
                log.info(log_type='ERROR', log_message=msg)
            return render_template('signup.html', msg=msg)


@app.route('/deletePage/<id>', methods=['GET'])
def renderDeleteProject(id):
    if 'loggedin' in session:
        log.info(log_type='ACTION', log_message='Redirect To Delete Project Page')
        return render_template('deleteProject.html', data={"id": id})
    else:
        return redirect(url_for('login'))


@app.route('/deleteProject/<id>', methods=['GET'])
def deleteProject(id):
    if 'loggedin' in session:
        if id:
            mysql.delete_record(f'UPDATE tblProjects SET IsActive=0 WHERE Id={id}')
            log.info(log_type='INFO', log_message='Data Successfully Deleted From Database')
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('pid', None)
    session.pop('project_name', None)
    log.info(log_type='INFO', log_message='Thanks For Using System!')
    return redirect(url_for('login'))


@app.route('/stream/<pid>')
def stream(pid):
    try:
        data = decrypt(pid)
        if data:
            values = data.split("&")
            session['pid'] = values[1]
            session['project_name'] = values[0]
            print(values[0], values[1])
            mongodb.get_collection_data(values[0])
            print('inside data')
            return redirect(url_for('module'))
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)


@app.route('/module')
def module():
    try:
        if 'pid' in session:
            return render_template('help.html')
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)


@app.route('/eda/<action>')
def eda(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action=="5point":
                    ProjectReports.insert_record_eda('5 Points Summary')
                    log.info(log_type='% Point Summary', log_message='Redirect To Eda 5 Point!')
                    summary=EDA.five_point_summary(df)
                    data=summary.to_html()
                    return render_template('eda/5point.html',data=data)
                elif action=="profiler":
                    ProjectReports.insert_record_eda('Profiler')
                    log.info(log_type='Show Profiler Report', log_message='Redirect To Eda Show Dataset!')
                    pr = ProfileReport(df, explorative=True, minimal=True,
                                       correlations={"cramers": {"calculate": False}})
                    pr.to_widgets()
                    pr.to_file("your_report.html")
                elif action=="show":
                    ProjectReports.insert_record_eda('Show Dataset')
                    log.info(log_type='Show Dataset', log_message='Redirect To Eda Show Dataset!')
                    data=EDA.get_no_records(df,100)
                    data=data.to_html()
                    topselected=True
                    bottomSelected=False
                    selectedCount=100
                    return render_template('eda/showdataset.html',data=data,length=len(df),
                                           bottomSelected=bottomSelected,topselected=topselected,action=action,selectedCount=selectedCount,columns=df.columns)
                elif action=="missing":
                    ProjectReports.insert_record_eda('Missing Value')
                    log.info(log_type='Missing Value Report', log_message='Redirect To Eda Show Dataset!')
                    df=EDA.missing_cells_table(df)
                    
                    graphJSON =  PlotlyHelper.barplot(df, x='Column',y='Missing values')
                    pie_graphJSON = PlotlyHelper.pieplot(df, names='Column',values='Missing values',title='Missing Values')
                    
                    data=df.drop('Column', axis=1, inplace=True)
                    data=df.to_html()
                    return render_template('eda/missing_values.html',action=action,data=data,barplot=graphJSON,pieplot=pie_graphJSON)
                
                elif action=="outlier":
                    ProjectReports.insert_record_eda('Outlier')
                    log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    df = EDA.z_score_outlier_detection(df)
                    graphJSON = PlotlyHelper.barplot(df, x='Features', y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(
                        df.sort_values(by='Total outliers', ascending=False).loc[:10, :], names='Features',
                        values='Total outliers', title='Top 10 Outliers')
                    data=df.to_html()
                    return render_template('eda/outliers.html',data=data,method='zscore',action=action,barplot=graphJSON,pieplot=pie_graphJSON)
                
                
                elif action=="correlation":
                    ProjectReports.insert_record_eda('Correlation')
                    pearson_corr=EDA.correlation_report(df,'pearson')
                    persion_data=list(np.around(np.array(pearson_corr.values),2))
                    fig = ff.create_annotated_heatmap(persion_data, x=list(pearson_corr.columns),
                                                      y=list(pearson_corr.columns), colorscale='Viridis')
                    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    return render_template('eda/correlation.html',data=graphJSON,columns=list(pearson_corr.columns),action=action,method='pearson')
                
                elif action=="plots":
                    ProjectReports.insert_record_eda('Plots')
                    return render_template('eda/plots.html',columns=list(df.columns),
                                           graphs_2d=TWO_D_GRAPH_TYPES,action=action,x_column="",y_column="")
                else:
                    return render_template('eda/help.html')
            else:
                return 'Hello'

        else:
            return redirect(url_for('/'))
    except Exception as e:
        ProjectReports.insert_record_eda(e)
        print(e)


@app.route('/eda/<action>', methods=['POST'])
def eda_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "show":
                    range = request.form['range']
                    optradio = request.form['optradio']
                    columns_for_list = df.columns
                    columns = request.form.getlist('columns')
                    log.info(log_type='Show Dataset', log_message='Redirect To Eda Show Dataset!')
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Show', input=input_str)
                    
                    if len(columns)>0:
                        df=df.loc[:,columns]
                        
                    data=EDA.get_no_records(df,int(range),optradio)
                    data=data.to_html()
                    topselected=True if optradio=='top' else False
                    bottomSelected=True if optradio=='bottom' else False
                    return render_template('eda/showdataset.html',data=data,length=len(df),
                                           bottomSelected=bottomSelected,topselected=topselected,action=action,selectedCount=range,columns=columns_for_list)
                elif action=="correlation":
                    method = request.form['method']
                    columns = request.form.getlist('columns')

                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Correlation', input=input_str)
                    
                    if method is not None:
                        # df=df.loc[:,columns]
                        _corr = EDA.correlation_report(df, method)
                        if len(columns) == 0:
                            columns = _corr.columns

                        _corr = _corr.loc[:, columns]
                        _data = list(np.around(np.array(_corr.values), 2))
                        fig = ff.create_annotated_heatmap(_data, x=list(_corr.columns),
                                                          y=list(_corr.index), colorscale='Viridis')
                        # fig = ff.create_annotated_heatmap(_data, colorscale='Viridis')
                        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                        return render_template('eda/correlation.html', data=graphJSON,
                                               columns=list(df.columns), action=action, method=method)
                    else:
                        return render_template('eda/help.html')

                elif action == "outlier":
                    method = request.form['method']
                    lower = 25
                    upper = 75
                    if method == "iqr":
                        lower = request.form['lower']
                        upper = request.form['upper']
                        df = EDA.outlier_detection_iqr(df, int(lower), int(upper))
                    else:
                        df=EDA.z_score_outlier_detection(df)

                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Outlier', input=input_str)
                    
                    graphJSON =  PlotlyHelper.barplot(df, x='Features',y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(df.sort_values(by='Total outliers',ascending=False).loc[:9,:], names='Features',values='Total outliers',title='Top 10 Outliers')    

                    log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    data = df.to_html()
                    return render_template('eda/outliers.html', data=data, method=method, action=action, lower=lower,
                                           upper=upper, barplot=graphJSON, pieplot=pie_graphJSON)

                elif action == "plots":
                    """All Polots for all kind of features????"""
                    selected_graph_type = request.form['graph']
                    x_column = request.form['xcolumn']
                    y_column = request.form['ycolumn']
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Plot', input=input_str)
                    
                    if selected_graph_type=="Scatter Plot":
                        graphJSON =  PlotlyHelper.scatterplot(df, x=x_column,y=y_column,title='Scatter Plot')                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    
                    elif selected_graph_type=="Pie Chart":
                        graphJSON =  PlotlyHelper.scatterplot(df, x=x_column,y=y_column,title='Scatter Plot')                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                    elif selected_graph_type=="Bar Graph":
                        graphJSON =  PlotlyHelper.barplot(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                    
                    elif selected_graph_type=="Histogram":
                        graphJSON =  PlotlyHelper.histogram(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                    elif selected_graph_type=="Line Chart":
                        graphJSON =  PlotlyHelper.line(df, x=x_column,y=y_column)                    
                        log.info(log_type='Outlier Value Report', log_message='Redirect To Eda Show Dataset!')
                        
                        
                    return render_template('eda/plots.html',selected_graph_type=selected_graph_type,
                                           columns=list(df.columns),graphs_2d=TWO_D_GRAPH_TYPES,
                                           action=action,graphJSON=graphJSON,x_column=x_column,y_column=y_column)

                else:
                    return render_template('eda/help.html')
            else:
                """Manage This"""
                pass

        else:
            return redirect(url_for('/'))
    except Exception  as e:
        ProjectReports.insert_record_eda(e)
            
            
@app.route('/dp/<action>')
def data_preprocessing(action):
    try:
        if 'pid' in session:
            df=None
            df=load_data()
            if df is not None:
                if action=="delete-columns":
                    log.info(log_type='Delete Columns', log_message='Redirect To Delete Columns!')
                    return render_template('dp/delete_columns.html',columns=list(df.columns),action=action)
                elif action=="duplicate-data":
                    duplicate_data=df[df.duplicated()].head(500)
                    data=duplicate_data.to_html()  
                    log.info(log_type='Duplicate Data', log_message='Redirect To Handle Duplicate Data!')
                    return render_template('dp/duplicate.html',columns=list(df.columns),action=action,data=data,duplicate_count=len(duplicate_data))
                
                elif action=="outlier":
                    columns=Preprocessing.col_seperator(df,'Numerical_columns')
                    log.info(log_type='Handle Outlier', log_message='Redirect To Handler Outlier!')
                    return render_template('dp/outliers.html',columns=columns,action=action)

                elif action=="missing-values":
                    columns=list(df.columns)
                    log.info(log_type='Handle Outlier', log_message='Redirect To Handler Outlier!')
                    return render_template('dp/missing_values.html',columns=columns,action=action)
                
                elif  action=="delete-outlier" or action=="remove-duplicate-data":
                    columns=Preprocessing.col_seperator(df,'Numerical_columns')
                    log.info(log_type='Handle Outlier', log_message='Redirect To Handler Outlier!')
                    return redirect(('/dp/outlier'))
                        
                elif  action=="imbalance-data":
                    columns=list(df.columns)
                    log.info(log_type='Handle Outlier', log_message='Redirect To Handle Imbalance Data!')
                    return render_template('dp/handle_imbalance.html',action=action,columns=columns)
                else:
                    return render_template('eda/help.html')
            else:
                """Manage This"""
                pass
            
        else:
            return redirect(url_for('/'))
    except Exception  as e:
            print(e)
            
            
@app.route('/dp/<action>',methods=['POST'])
def data_preprocessing_post(action):
    try:
        if 'pid' in session:
            df=None
            df=load_data()
            template='dp/help.html'
            if df is not None:
                if action=="delete-columns":
                    columns = request.form.getlist('columns')
                    df=Preprocessing.delete_col(df,columns)
                    df=update_data(df)
                    log.info(log_type='Delete Columns', log_message='Redirect To Delete Columns!')
                    return render_template('dp/delete_columns.html',columns=list(df.columns),action=action,status='success')
                
                elif action=="duplicate-data":
                    columns = request.form.getlist('columns')
                    if len(columns)>0:
                        df=df[df.duplicated(columns)]
                    else:
                        df=df[df.duplicated()]
                    data=df.head(500).to_html()  
                    log.info(log_type='Duplicate Data', log_message='Redirect To Handle Duplicate Data!')
                    return render_template('dp/duplicate.html',columns=list(df.columns),action=action,
                                           data=data,duplicate_count=len(df),selected_column=','.join(columns))
                    
                elif action=="remove-duplicate-data":
                    columns =request.form['selected_column']
                    
                    if len(columns)>0:
                        data=df.drop_duplicates(subset=list(columns.split(",")), keep='last')  
                    else:
                        data=df.drop_duplicates(keep='last') 
                                        
                    df=update_data(data)
                    
                    duplicate_data=df[df.duplicated()]
                    data=duplicate_data.head(500).to_html()  
                    log.info(log_type='Duplicate Data', log_message='Redirect To Handle Duplicate Data!')
                    return render_template('dp/duplicate.html',columns=list(df.columns),action="duplicate-data",data=data,
                                           duplicate_count=len(duplicate_data),success=True)
                
                elif action=="outlier":
                    method = request.form['method']
                    column = request.form['columns']
                    lower=25
                    upper=75
                    graphJSON=""
                    pie_graphJSON=""
                    columns=Preprocessing.col_seperator(df,'Numerical_columns')
                    outliers_list=[]
                    if method=="iqr":
                        # lower = request.form['lower']
                        # upper = request.form['upper']
                        result=EDA.outlier_detection_iqr(df.loc[:,[column]],int(lower),int(upper))
                        if len(result)>0:
                            graphJSON =  PlotlyHelper.boxplot(df,column)  
                        data=result.to_html()
                        
                        outliers_list=EDA.outlier_detection(list(df.loc[:,column]),'iqr')
                        unique_outliers=np.unique(outliers_list)
                    else:
                        result=EDA.z_score_outlier_detection(df.loc[:,[column]])
                        if len(result)>0:
                            list_=list(df[~df.loc[:,column].isnull()][column])
                            graphJSON =  PlotlyHelper.distplot(list_,column)  
                        data=result.to_html()   
                        
                        outliers_list=EDA.outlier_detection(list(df.loc[:,column]),'z-score')
                        unique_outliers=np.unique(outliers_list)
                    
                    df_outliers=pd.DataFrame(pd.Series(outliers_list).value_counts(),columns=['value']).reset_index(level=0)
                    if len(df_outliers)>0:
                        pie_graphJSON = PlotlyHelper.pieplot(df_outliers, names='index',values='value',title='Missing Values Count') 
                        
                    log.info(log_type='Outlier Report', log_message='Post: Redirect To Delete Columns!')
                    return render_template('dp/outliers.html',columns=columns,method=method,selected_column=column,
                                           outliers_list=outliers_list,unique_outliers=unique_outliers,pie_graphJSON=pie_graphJSON,
                                           action=action,data=data,
                                           outliercount=result['Total outliers'][0] if len(result['Total outliers'])>0 else 0,
                                           graphJSON=graphJSON)
                    
                
                elif action=="missing-values":
                    if 'method' in request.form:
                         method=request.form['method']
                         selected_column=request.form['selected_column']
                         success=False
                         if method=='Mean':
                             df[selected_column]=Preprocessing.fill_numerical(df,'Mean',[selected_column])
                         elif method=='Median':
                             df[selected_column]=Preprocessing.fill_numerical(df,'Median',[selected_column])
                         elif method=='Arbitrary Value':
                             df[selected_column]=Preprocessing.fill_numerical(df,'Median',[selected_column],request.form['arbitrary'])
                         elif method=='Interpolate':
                              df[selected_column]=Preprocessing.fill_numerical(df,'Interpolate',[selected_column],request.form['interpolate'])
                         elif method=='Mode':
                              df[selected_column]=Preprocessing.fill_categorical(df,'Mode',selected_column)
                         elif method=='New Category':
                              df[selected_column]=Preprocessing.fill_categorical(df,'New Category',selected_column,request.form['newcategory'])
                         elif method=='Select Exist':
                              df[selected_column]=Preprocessing.fill_categorical(df,'New Category',selected_column,request.form['selectcategory'])
                                
                         df=update_data(df)
                         success=True
                         columns=list(df.columns)
                         return render_template('dp/missing_values.html',columns=columns,action=action,success=success)
                    else:
                        columns=list(df.columns)
                        selected_column=request.form['columns']
                        data=EDA.missing_cells_table(df.loc[:,[selected_column]])
                        null_value_count=0
                        unique_category=[]
                        outlier_handler_methods=[]
                        if len(data)>0:
                            unique_category=list(df[df[selected_column].notna()][selected_column].unique())
                            null_value_count=data['Missing values'][0]
                            if df[selected_column].dtype=='object':
                                outlier_handler_methods=OBJECT_MISSING_HANDLER
                                
                            else:
                                outlier_handler_methods=NUMERIC_MISSING_HANDLER
                            
                        
                        data=data.to_html()
                        log.info(log_type='Handle Outlier', log_message='Redirect To Handler Outlier!')
                        return render_template('dp/missing_values.html',unique_category=unique_category,columns=columns,selected_column=selected_column,action=action,data=data,null_value_count=null_value_count,handler_methods=outlier_handler_methods)
                    
                elif action=="delete-outlier":
                    values = request.form.getlist('columns')
                    selected_column=request.form['selected_column']
                    columns=Preprocessing.col_seperator(df,'Numerical_columns')
                    df=df[~df[selected_column].isin(list(values))]
                    df=update_data(df)
                    log.info(log_type='Delete Outlier', log_message='Redirect To Handler Outlier!')
                    return render_template('dp/outliers.html',columns=columns,action="outlier",status="success")
                
                elif action=="imbalance-data":
                    try:
                        if 'perform_action' in request.form:
                            target_column=request.form['target_column']
                            method=request.form['method']
                            range=request.form['range']
                            
                            if method=='OS':
                                new_df=Preprocessing.over_sample(df,target_column,float(range))
                            elif method=='US':
                                new_df=Preprocessing.under_sample(df,target_column,float(range))   
                            else:
                                new_df=Preprocessing.smote_technique(df,target_column,float(range)) 
                            
                            df=update_data(new_df)  
                            return render_template('dp/handle_imbalance.html',columns=list(df.columns),target_column=target_column,success=True)
                        else:
                            target_column=request.form['target_column']
                            df_counts=pd.DataFrame(df.groupby(target_column).count()).reset_index(level=0)
                            y=list(pd.DataFrame(df.groupby(target_column).count()).reset_index(level=0).columns)[-1]
                            graphJSON =  PlotlyHelper.barplot(df_counts, x=target_column,y=y)
                            pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=target_column,values=y,title='')
                            
                            log.info(log_type='Delete Outlier', log_message='Redirect To Handler Outlier!')
                            return render_template('dp/handle_imbalance.html',columns=list(df.columns),target_column=target_column,action="imbalance-data",
                                                pie_graphJSON=pie_graphJSON,graphJSON=graphJSON,perform_action=True)
                                
                    except Exception as e:
                         return render_template('dp/handle_imbalance.html',action=action,columns=list(df.columns),error=str(e))
                        
                
                else:
                    return redirect('dp/help.html')
            else:
                """Manage This"""
                pass
            
        else:
            return redirect(url_for('/'))
    except Exception  as e:
            print(e)
            
    except Exception as e:
        print(e)


@app.route('/feature_engineering/<action>', methods=['GET'])
def feature_engineering(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                data = df.head().to_html()
                if action == 'help':
                    return render_template('feature_engineering/help.html')
                elif action == 'handleDatetime':
                    dt_splitted = False
                    not_dt_splitted = True
                    selectedCount = 100
                    return render_template('feature_engineering/handleDatetime.html', data=data, length=len(df),
                                           not_dt_splitted=not_dt_splitted, dt_splitted=dt_splitted, action=action,
                                           selectedCount=selectedCount, columns=df.columns)
                elif action == 'encoding':
                    return render_template('feature_engineering/encoding.html', data=data, columns=df.columns, action=action)
                elif action == 'scaling':
                    return render_template('feature_engineering/scaling.html', data=data)
                elif action == 'feature_selection':
                    return render_template('feature_engineering/feature_selection.html', data=data)
                elif action == 'dimension_reduction':
                    return render_template('feature_engineering/dimension_reduction.html', data=data)
                elif action == 'train_test_split':
                    return render_template('feature_engineering/train_test_split.html', data=data)
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)


@app.route('/feature_engineering/<action>', methods=['POST'])
def feature_engineering_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                data = df.head().to_html()
                if action == 'help':
                    return render_template('feature_engineering/help.html')
                
                elif action == 'handleDatetime':
                    dt_splitted = False
                    not_dt_splitted = True
                    selectedCount = 100
                    columns = request.form.getlist('columns')
                    print(columns)
                    data = df[columns].to_html()
                    return render_template('feature_engineering/handleDatetime.html', data=data, length=len(df),
                                           not_dt_splitted=not_dt_splitted, dt_splitted=dt_splitted, action=action,
                                           selectedCount=selectedCount, columns=df.columns)
                elif action == 'encoding':
                    df = pd.read_csv(r'AMES_Final_DF.csv')
                    Categorical_columns = df.select_dtypes(include='object')
                    custom = True
                    selectall=False
                    return render_template('feature_engineering/encoding.html', data=data, custom=custom, selectall=selectall, action=action, columns=Categorical_columns.columns)
                elif action == 'scaling':
                    try:
                        df = pd.read_csv(r'AMES_Final_DF.csv')
                        X = df.drop('SalePrice', axis=1)
                        y = df['SalePrice']
                        obj = FeatureEngineering()
                        scaler = request.form['scaler']
                        data = obj.scaler_(X, scaler)
                    except:
                        return render_template('feature_engineering/encoding.html', data=data)
                    return render_template('feature_engineering/scaling.html', data=data)
                elif action == 'feature_selection':
                    return render_template('feature_engineering/feature_selection.html', data=data)
                elif action == 'dimension_reduction':
                    return render_template('feature_engineering/dimension_reduction.html', data=data)
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))

    except Exception as e:
        print(e)


@app.route('/systemlogs/<action>', methods=['GET'])
def systemlogs(action):
    try:
        if action == 'terminal':
            lines = []
            with open(r"C:\Users\ketan\Desktop\Project\Projectathon\logger\logs\logs.log") as file_in:
                for line in file_in:
                    lines.append(line)
            print(lines)
            file_in.close()
            return render_template('systemlogs/terminal.html', logs=lines)
        else:
            return 'Not Visible'
    except Exception as e:
        print(e)


@app.route('/model_training/<action>', methods=['GET'])
def model_training(action):
    try:
        if 'pid' in session:
            df = load_data()
            data = df.head().to_html()
            if df is not None:
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'train_test_split':
                    columns_for_list = df.columns
                    return render_template('model_training/train_test_split.html', data=data, columns = columns_for_list, action='train_test_split')
                elif action == 'auto_training':
                    data = df.head().to_html()
                    return render_template('model_training/auto_training.html', data=data)
                elif action == 'custom_training':
                    typ = "Regression"
                    if typ == "Regression":
                        return render_template('model_training/regression.html')
                    elif typ == "Classification":
                        return render_template('model_training/classification.html')
                    elif typ == "Clustering":
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


X_train, X_test, y_train, y_test = None, None, None, None


@app.route('/model_training/<action>', methods=['POST'])
def model_training_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            data = df.head().to_html()
            if df is not None:
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'train_test_split':
                    global X_test
                    global X_train
                    global y_test
                    global y_train

                    percent = int(request.form['range'])
                    target = request.form['columns']
                    Random_State = int(request.form['Random_State'])
                    df = pd.read_csv(r'C:\Users\ketan\Desktop\Project\Projectathon\AMES_Final_DF.csv')
                    X = df.drop(target, axis=1)
                    y = df[target]
                    X_train, X_test, y_train, y_test = FeatureEngineering.train_test_Split(self=None, cleanedData=X, label=y, test_size=(1-(percent/100)), random_state=Random_State)
                    return render_template('model_training/train_test_split.html', data=data)
                elif action == 'auto_training':
                    typ = 'Regression'
                    if typ == 'Regression':

                        scaler = StandardScaler()
                        X_train = scaler.fit_transform(X_train)
                        X_test = scaler.transform(X_test)
                        data = ModelTrain_Regression(X_train, X_test, y_train, y_test, True)
                        return render_template('model_training/auto_training.html', data=data.results().to_html())
                    elif typ == 'Classification':
                        return render_template('model_training/auto_training.html')
                    else:
                        pass
                        return render_template('model_training/auto_training.html')
                elif action == 'custom_training':
                    return render_template('model_training/custom_training.html')
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)

@app.route('/Machine/<action>', methods=['GET'])
def machine(action):
    return render_template('Machine/system.html')


    """APIS"""
@app.route('/api/missing-data', methods=['GET', 'POST'])
def missing_data():
    try:
        df = load_data()
        selected_column=request.json['selected_column']
        method=request.json['method']
        if method=='Mean' or  method=='Median' or  method=='Arbitrary Value' or  method=='Interpolate':
            before={}
            after={}
            list_=list(df[~df.loc[:,selected_column].isnull()][selected_column])
            before['graph'] =  PlotlyHelper.distplot(list_,selected_column)  
            before['skewness'] =  Preprocessing.find_skewness(list_)  
            before['kurtosis'] =  Preprocessing.find_kurtosis(list_)  
            
            if method=='Mean':
                new_df=Preprocessing.fill_numerical(df,'Mean',[selected_column])
            elif method=='Median':
                new_df=Preprocessing.fill_numerical(df,'Median',[selected_column])
            elif method=='Arbitrary Value':
                new_df=Preprocessing.fill_numerical(df,'Median',[selected_column],request.json['Arbitrary_Value'])
            elif method=='Interpolate':
                new_df=Preprocessing.fill_numerical(df,'Interpolate',[selected_column],request.json['Interpolate'])
            
                
            new_list=list(new_df.loc[:,selected_column])
            
            after['graph'] =  PlotlyHelper.distplot(new_list,selected_column)  
            after['skewness'] =  Preprocessing.find_skewness(new_list)  
            after['kurtosis'] =  Preprocessing.find_kurtosis(new_list)    
                      
            d={
                'success':True,
                'before':before,
                'after':after
            }
            return jsonify(d)

        if method=='Mode' or  method=='New Category' or  method=='Select Exist':
            before={}
            after={}
            df_counts=pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
            y=list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:,1].values)
            pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column,values=y,title='')
            before['graph']=pie_graphJSON  
            
            if method=='Mode':
                df[selected_column]=Preprocessing.fill_categorical(df,'Mode',selected_column)
                df_counts=pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y=list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:,1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column,values=y,title='')  
                
                after['graph'] =  pie_graphJSON
            elif method=='New Category':
                df[selected_column]=Preprocessing.fill_categorical(df,'New Category',selected_column,request.json['newcategory'])
                df_counts=pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y=list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:,1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column,values=y,title='') 
                after['graph'] =  pie_graphJSON
                
            elif method=='Select Exist':
                df[selected_column]=Preprocessing.fill_categorical(df,'New Category',selected_column,request.json['selectcategory'])
                df_counts=pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y=list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:,1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column,values=y,title='')  
                
                after['graph'] =  pie_graphJSON
                                      
            d={
                'success':True,
                'before':before,
                'after':after
            }
            return jsonify(d)

    except Exception as e:
       return jsonify({'success':False})

    return "Hello World!"
if __name__ == '__main__':
    if mysql is None or mongodb is None:
        print("OOPS!!!!Somethong went wrong")
    else:
        app.run(host="127.0.0.1", port=5000, debug=True)


