from flask import Flask, redirect, url_for, render_template, request, session, send_file, jsonify
from src.model.custom.classification_models import ClassificationModels
from src.model.custom.regression_models import RegressionModels
from src.model.custom.clustering_models import ClusteringModels
from werkzeug.wrappers import Response
from io import BytesIO
import re
from src.preprocessing.preprocessing_helper import Preprocessing
from src.constants.constants import ENCODING_TYPES, FEATURE_SELECTION_METHODS_CLASSIFICATION, NUMERIC_MISSING_HANDLER, \
    OBJECT_MISSING_HANDLER, PROJECT_TYPES, SUPPORTED_DATA_TYPES, SUPPORTED_SCALING_TYPES, TWO_D_GRAPH_TYPES
from src.utils.databases.mysql_helper import MySqlHelper
from werkzeug.utils import secure_filename
import os
import time
from src.utils.common.common_helper import decrypt, read_config, unique_id_generator, Hashing, encrypt
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
from src.utils.common.data_helper import load_data, update_data, get_filename, csv_to_json, to_tsv, csv_to_excel
from src.eda.eda_helper import EDA
import numpy as np
import json
import plotly
import plotly.figure_factory as ff
from pandas_profiling import ProfileReport
from src.utils.common.plotly_helper import PlotlyHelper
from src.utils.common.project_report_helper import ProjectReports
from src.utils.common.common_helper import immutable_multi_dict_to_str

from src.utils.common.cloud_helper import aws_s3_helper
from src.utils.common.cloud_helper import gcp_browser_storage
from src.utils.common.cloud_helper import azure_data_helper
from src.utils.common.database_helper import mysql_data_helper, mongo_data_helper
from src.utils.common.database_helper import cassandra_connector
from src.feature_engineering.feature_engineering_helper import FeatureEngineering
from src.routes.routes_api import app_api
from loguru import logger

# Yaml Config File
config_args = read_config("./config.yaml")

log_path = os.path.join(os.getcwd(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.add(sink=log_path, format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}", level="INFO")

logger.info('Fetching Data from configuration file')
# SQL Connection code
host = config_args['secrets']['host']
port = config_args['secrets']['port']
user = config_args['secrets']['user']
password = config_args['secrets']['password']
database = config_args['secrets']['database']

logger.info('Initializing Databases')
mysql = MySqlHelper.get_connection_obj()
mongodb = MongoHelper()

template_dir = config_args['dir_structure']['template_dir']
static_dir = config_args['dir_structure']['static_dir']

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.register_blueprint(app_api)
logger.info('App Started')

app.secret_key = config_args['secrets']['key']
app.config["UPLOAD_FOLDER"] = config_args['dir_structure']['upload_folder']
app.config["MAX_CONTENT_PATH"] = config_args['secrets']['MAX_CONTENT_PATH']


@app.context_processor
def context_processor():
    loggedin = False
    if 'loggedin' in session:
        loggedin = True

    return dict(loggedin=loggedin)


@app.route('/', methods=['GET', 'POST'], )
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
        logger.error(e)


status = None
download_status = None


@app.route('/project', methods=['GET', 'POST'])
def project(df=None, table_name=None):
    global status, download_status
    try:
        if 'loggedin' in session:
            if request.method == "GET":
                return render_template('new_project.html', loggedin=True, project_types=PROJECT_TYPES)
            else:
                source_type = request.form['source_type']
                if source_type == 'uploadFile':
                    name = request.form['project_name']
                    description = request.form['project_desc']
                    print(source_type, name, description)
                    if len(request.files) > 0:
                        f = request.files['file']

                    ALLOWED_EXTENSIONS = ['csv', 'tsv', 'json']
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
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)

                    filename = secure_filename(f.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(file_path)
                    timestamp = round(time.time() * 1000)
                    name = name.replace(" ", "_")
                    table_name = f"{name}_{timestamp}"

                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith('.tsv'):
                        df = pd.read_csv(file_path, sep='\t')
                    elif file_path.endswith('.json'):
                        df = pd.read_json(file_path)
                    else:
                        msg = 'This file format is currently not supported'
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)

                    project_id = unique_id_generator()
                    inserted_rows = mongodb.create_new_project(project_id, df)

                    if inserted_rows > 0:
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
                            logger.info(msg)
                            return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)
                    else:
                        msg = "Error while creating new Project"
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)

                elif source_type == 'uploadResource':
                    name = request.form['project_name']
                    description = request.form['project_desc']
                    resource_type = request.form['resource_type']

                    if not name.strip():
                        msg = 'Please enter project name'
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)
                    elif not description.strip():
                        msg = 'Please enter project description'
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)

                    if resource_type == "awsS3bucket":
                        region_name = request.form['region_name']
                        aws_access_key_id = request.form['aws_access_key_id']
                        aws_secret_access_key = request.form['aws_secret_access_key']
                        bucket_name = request.form['bucket_name']
                        file_name = request.form['file_name']
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                        aws_s3 = aws_s3_helper(region_name, aws_access_key_id, aws_secret_access_key)
                        conn_msg = aws_s3.check_connection(bucket_name, file_name)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('new_project.html', msg=conn_msg, project_types=PROJECT_TYPES)

                        download_status = aws_s3.download_file_from_s3(bucket_name, file_name, file_path)
                        logger.info(name, description, resource_type, download_status, file_path)

                    elif resource_type == "gcpStorage":
                        credentials_file = request.files['GCP_credentials_file']
                        bucket_name = request.form['bucket_name']
                        file_name = request.form['file_name']
                        credentials_filename = secure_filename(credentials_file.filename)
                        credentials_file_path = os.path.join(app.config['UPLOAD_FOLDER'], credentials_filename)
                        credentials_file.save(credentials_file_path)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                        logger.info(credentials_file_path, file_path, file_name, bucket_name)
                        gcp = gcp_browser_storage(credentials_file_path)
                        conn_msg = gcp.check_connection(bucket_name, file_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('new_project.html', msg=conn_msg, project_types=PROJECT_TYPES)

                        download_status = gcp.download_file_from_bucket(file_name, file_path, bucket_name)
                        logger.info(download_status)

                    elif resource_type == "mySql":
                        host = request.form['host']
                        port = request.form['port']
                        user = request.form['user']
                        password = request.form['password']
                        database = request.form['database']
                        table_name = request.form['table_name']
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], (table_name + ".csv"))
                        logger.info(file_path)

                        mysql_data = mysql_data_helper(host, port, user, password, database)
                        conn_msg = mysql_data.check_connection(table_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('new_project.html', msg=conn_msg, project_types=PROJECT_TYPES)

                        download_status = mysql_data.retrive_dataset_from_table(table_name, file_path)
                        logger.info(conn_msg)

                    elif resource_type == "cassandra":
                        secure_connect_bundle = request.files['secure_connect_bundle']
                        client_id = request.form['client_id']
                        client_secret = request.form['client_secret']
                        keyspace = request.form['keyspace']
                        table_name = request.form['table_name']
                        data_in_tabular = request.form['data_in_tabular']
                        secure_connect_bundle_filename = secure_filename(secure_connect_bundle.filename)
                        secure_connect_bundle_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                                       secure_connect_bundle_filename)
                        secure_connect_bundle.save(secure_connect_bundle_file_path)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], (table_name + ".csv"))
                        logger.info(secure_connect_bundle_file_path, file_path)

                        cassandra_db = cassandra_connector(secure_connect_bundle_file_path, client_id, client_secret,
                                                           keyspace)
                        conn_msg = cassandra_db.check_connection(table_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('new_project.html', msg=conn_msg, project_types=PROJECT_TYPES)

                        if data_in_tabular == 'true':
                            download_status = cassandra_db.retrive_table(table_name, file_path)
                            logger.info(download_status)
                        elif data_in_tabular == 'false':
                            download_status = cassandra_db.retrive_uploded_dataset(table_name, file_path)
                            logger.info(download_status)

                    elif resource_type == "mongodb":
                        mongo_db_url = request.form['mongo_db_url']
                        mongo_database = request.form['mongo_database']
                        collection = request.form['collection']
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], (collection + ".csv"))
                        mongo_helper = mongo_data_helper(mongo_db_url)
                        conn_msg = mongo_helper.check_connection(mongo_database, collection)
                        if conn_msg != 'Successful':
                            print(conn_msg)
                            return render_template('new_project.html', msg=conn_msg)

                        download_status = mongo_helper.retrive_dataset(mongo_database, collection, file_path)
                        print(name, description, resource_type, download_status, file_path)

                    elif resource_type == "azureStorage":
                        azure_connection_string = request.form['azure_connection_string']
                        container_name = request.form['container_name']
                        file_name = request.form['file_name']
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
                        azure_helper = azure_data_helper(azure_connection_string)
                        conn_msg = azure_helper.check_connection(container_name, file_name)

                        if conn_msg != 'Successful':
                            print(conn_msg)
                            return render_template('new_project.html', msg=conn_msg)

                        download_status = azure_helper.download_file(container_name, file_name, file_path)
                        print(download_status)

                        project_id = unique_id_generator()
                        inserted_rows = mongodb.create_new_project(project_id, df)

                        if inserted_rows > 0:
                            logger.info('Project Created')
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
                                logger.info(msg)
                                return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)
                        else:
                            msg = "Error while creating new Project"
                            logger.info(msg)
                            return render_template('new_project.html', msg=msg)
                    else:
                        msg = "Error while creating new Project"
                        logger.info(msg)
                        return render_template('new_project.html', msg=msg, project_types=PROJECT_TYPES)
        else:
            return redirect(url_for('login'))

    except Exception as e:
        logger.error(e)
        return render_template('new_project.html', msg=e.__str__())


@app.route('/login', methods=['GET', 'POST'])
def login():
    global msg
    if 'loggedin' in session:
        logger.info('Redirect To Main Page')
        return redirect('/')
    else:
        if request.method == "GET":
            logger.info('Login Template Rendering')
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
                    logger.info('Login Successful')
                    return redirect('/')
                else:
                    msg = 'Incorrect username / password !'
                    logger.error(msg)
            return render_template('login.html', msg=msg)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    else:
        if request.method == "GET":
            logger.info('Signup Template Rendering')
            return render_template('signup.html')
        else:
            msg = None
            if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
                username = request.form['username']
                password = request.form['password']
                confirm_password = request.form['confirm-password']
                email = request.form['email']
                account = mysql.fetch_one(f'SELECT * FROM tblUsers WHERE Email = "{email}"')
                logger.info('Checking Database')
                if account:
                    msg = 'EmailId already exists !'
                elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                    msg = 'Invalid email address !'
                elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'Username must contain only characters and numbers !'
                elif not username or not password or not email:
                    msg = 'Please fill out the form !'
                elif confirm_password != password:
                    msg = 'Password and Confirm password are not same!'
                else:
                    hashed_password = Hashing.hash_value(password)
                    rowcount = mysql.insert_record(
                        f'INSERT INTO tblUsers (Name, Email, Password, AuthToken) VALUES ("{username}", "{email}", "{hashed_password}", "pankajtest")')
                    if rowcount > 0:
                        return redirect(url_for('login'))
            elif request.method == 'POST':
                msg = 'Please fill out the form !'
                logger.error(msg)
            logger.info(msg)
            return render_template('signup.html', msg=msg)


@app.route('/exportFile/<id>', methods=['GET'])
def exportForm(id):
    if 'loggedin' in session:
        logger.info('Redirect To Export File Page')
        return render_template('exportFile.html', data={"id": id})
    else:
        return redirect(url_for('login'))


@app.route('/exportFile', methods=['POST'])
def exportFile():
    try:
        if 'loggedin' in session:
            logger.info('Export File')
            fileType = request.form['fileType']
            filename = get_filename()

            if fileType == 'csv':
                with open(filename) as fp:
                    content = fp.read()
                return Response(
                    content,
                    mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=test.csv"})

            elif fileType == 'tsv':
                filename = filename.rsplit('.', 1)[0]
                to_tsv()
                with open(filename + '.tsv') as fp:
                    content = fp.read()

                if os.path.isfile(filename + '.tsv'):
                    os.remove(filename + '.tsv')
                else:
                    print(filename + '.tsv file doesnt exist')
                return Response(
                    content,
                    mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=test.tsv"})

            elif fileType == 'excel':
                wb = csv_to_excel()

                file_stream = BytesIO()
                wb.save(file_stream)
                file_stream.seek(0)

                filename = filename.rsplit('.', 1)[0]
                if os.path.isfile(filename + '.xlsx'):
                    os.remove(filename + '.xlsx')
                else:
                    print(filename + '.xlsx file doesnt exist')

                return send_file(file_stream, attachment_filename="tdd-excel.xlsx", as_attachment=True)

            elif fileType == 'json':
                content = csv_to_json(filename)
                return Response(
                    content,
                    mimetype="text/json",
                    headers={"Content-disposition": "attachment; filename=test.json"})

        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.info(e)
        return render_template('exportFile.html', msg=e.__str__())


@app.route('/deletePage/<id>', methods=['GET'])
def renderDeleteProject(id):
    if 'loggedin' in session:
        logger.info('Redirect To Delete Project Page')
        return render_template('deleteProject.html', data={"id": id})
    else:
        return redirect(url_for('login'))


@app.route('/deleteProject/<id>', methods=['GET'])
def deleteProject(id):
    if 'loggedin' in session:
        if id:
            mysql.delete_record(f'UPDATE tblProjects SET IsActive=0 WHERE Id={id}')
            logger.info('Data Successfully Deleted From Database')
            return redirect(url_for('index'))
        else:
            logger.info('Redirect to index invalid id')
            return redirect(url_for('index'))
    else:
        logger.info('Login Needed')
        return redirect(url_for('login'))


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('pid', None)
    session.pop('project_name', None)
    logger.info('Thanks For Using System!')
    return redirect(url_for('login'))


@app.route('/stream/<pid>')
def stream(pid):
    try:
        data = decrypt(pid)
        if data:
            values = data.split("&")
            session['pid'] = values[1]
            session['project_name'] = values[0]
            logger.info(values[0])
            logger.info(values[1])
            mongodb.get_collection_data(values[0])
            logger.info('inside data')
            return redirect(url_for('module'))
        else:
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)


@app.route('/module')
def module():
    try:
        if 'pid' in session:
            logger.info('Redirected to help page')
            return render_template('help.html')
        else:
            logger.info('Redirected to login')
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)


@app.route('/eda/<action>')
def eda(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "5point":
                    ProjectReports.insert_record_eda('5 Points Summary')
                    logger.info('Redirect To Eda Data summary')
                    summary = EDA.five_point_summary(df)
                    data = summary.to_html()
                    return render_template('eda/5point.html', data=data)
                elif action == "profiler":
                    ProjectReports.insert_record_eda('Profiler')
                    logger.info('Redirect To Eda Show Dataset!')
                    pr = ProfileReport(df, explorative=True, minimal=True,
                                       correlations={"cramers": {"calculate": False}})
                    pr.to_widgets()
                    pr.to_file("your_report.html")
                elif action == "show":
                    ProjectReports.insert_record_eda('Show Dataset')
                    logger.info('Redirect To Eda Show Dataset!')
                    data = EDA.get_no_records(df, 100)
                    data = data.to_html()
                    topselected = True
                    bottomSelected = False
                    selectedCount = 100
                    return render_template('eda/showdataset.html', data=data, length=len(df),
                                           bottomSelected=bottomSelected, topselected=topselected, action=action,
                                           selectedCount=selectedCount, columns=df.columns)
                elif action == "missing":
                    ProjectReports.insert_record_eda('Missing Value')
                    logger.info('Redirect To Eda Show Dataset!')
                    df = EDA.missing_cells_table(df)
                    graphJSON = PlotlyHelper.barplot(df, x='Column', y='Missing values')
                    pie_graphJSON = PlotlyHelper.pieplot(df, names='Column', values='Missing values',
                                                         title='Missing Values')

                    data = df.drop('Column', axis=1, inplace=True)
                    data = df.to_html()
                    return render_template('eda/missing_values.html', action=action, data=data, barplot=graphJSON,
                                           pieplot=pie_graphJSON)

                elif action == "outlier":
                    ProjectReports.insert_record_eda('Outlier')
                    logger.info('Redirect To outlier')
                    df = EDA.z_score_outlier_detection(df)
                    graphJSON = PlotlyHelper.barplot(df, x='Features', y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(
                        df.sort_values(by='Total outliers', ascending=False).loc[:10, :], names='Features',
                        values='Total outliers', title='Top 10 Outliers')
                    data = df.to_html()
                    logger.info('Showing data on outlier page')
                    return render_template('eda/outliers.html', data=data, method='zscore', action=action,
                                           barplot=graphJSON, pieplot=pie_graphJSON)

                elif action == "correlation":
                    ProjectReports.insert_record_eda('Correlation')
                    pearson_corr = EDA.correlation_report(df, 'pearson')
                    persion_data = list(np.around(np.array(pearson_corr.values), 2))
                    fig = ff.create_annotated_heatmap(persion_data, x=list(pearson_corr.columns),
                                                      y=list(pearson_corr.columns), colorscale='Viridis')
                    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                    logger.info('Showing data on correlation page')
                    return render_template('eda/correlation.html', data=graphJSON, columns=list(pearson_corr.columns),
                                           action=action, method='pearson')

                elif action == "plots":
                    ProjectReports.insert_record_eda('Plots')
                    logger.info('Redirected to Plots')
                    return render_template('eda/plots.html', columns=list(df.columns),
                                           graphs_2d=TWO_D_GRAPH_TYPES, action=action, x_column="", y_column="")
                else:
                    logger.info('Showing EDA help')
                    return render_template('eda/help.html')
            else:
                logger.info('Data frame is None')
                return None

        else:
            return redirect(url_for('/'))
    except Exception as e:
        ProjectReports.insert_record_eda(e)
        logger.error(e)


@app.route('/eda/<action>', methods=['POST'])
def eda_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "show":
                    logger.info('Redirect To Eda Show Dataset!')
                    range = request.form['range']
                    optradio = request.form['optradio']
                    columns_for_list = df.columns
                    columns = request.form.getlist('columns')
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Show', input=input_str)

                    if len(columns) > 0:
                        df = df.loc[:, columns]

                    data = EDA.get_no_records(df, int(range), optradio)
                    data = data.to_html()
                    topselected = True if optradio == 'top' else False
                    bottomSelected = True if optradio == 'bottom' else False
                    logger.info('Sending Data on front end')
                    return render_template('eda/showdataset.html', data=data, length=len(df),
                                           bottomSelected=bottomSelected, topselected=topselected, action=action,
                                           selectedCount=range, columns=columns_for_list)
                elif action == "correlation":
                    logger.info('Redirect To correlation')
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
                        logger.info('Sending Data on front end')
                        return render_template('eda/correlation.html', data=graphJSON,
                                               columns=list(df.columns), action=action, method=method)
                    else:
                        return render_template('eda/help.html')

                elif action == "outlier":
                    logger.info('Redirected to outlier page')
                    method = request.form['method']
                    lower = 25
                    upper = 75
                    if method == "iqr":
                        lower = request.form['lower']
                        upper = request.form['upper']
                        df = EDA.outlier_detection_iqr(df, int(lower), int(upper))
                    else:
                        df = EDA.z_score_outlier_detection(df)

                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Outlier', input=input_str)

                    graphJSON = PlotlyHelper.barplot(df, x='Features', y='Total outliers')
                    pie_graphJSON = PlotlyHelper.pieplot(
                        df.sort_values(by='Total outliers', ascending=False).loc[:9, :], names='Features',
                        values='Total outliers', title='Top 10 Outliers')
                    data = df.to_html()
                    logger.info('Sending Data on the front end')
                    return render_template('eda/outliers.html', data=data, method=method, action=action, lower=lower,
                                           upper=upper, barplot=graphJSON, pieplot=pie_graphJSON)

                elif action == "plots":
                    logger.info('Redirected to Plots')
                    selected_graph_type = request.form['graph']
                    x_column = request.form['xcolumn']
                    y_column = request.form['ycolumn']
                    input_str = immutable_multi_dict_to_str(request.form)
                    ProjectReports.insert_record_eda('Plot', input=input_str)

                    if selected_graph_type == "Scatter Plot":
                        graphJSON = PlotlyHelper.scatterplot(df, x=x_column, y=y_column, title='Scatter Plot')
                        logger.info('Displaying scatter plot')

                    elif selected_graph_type == "Pie Chart":
                        graphJSON = PlotlyHelper.scatterplot(df, x=x_column, y=y_column, title='Scatter Plot')
                        logger.info('Displaying pie Chart')

                    elif selected_graph_type == "Bar Graph":
                        graphJSON = PlotlyHelper.barplot(df, x=x_column, y=y_column)
                        logger.info('Displaying Bar Graph')

                    elif selected_graph_type == "Histogram":
                        graphJSON = PlotlyHelper.histogram(df, x=x_column, y=y_column)
                        logger.info('Displaying Histogram')

                    elif selected_graph_type == "Line Chart":
                        graphJSON = PlotlyHelper.line(df, x=x_column, y=y_column)
                        logger.info('Displaying Line Chart')

                    logger.info('Loading plot on front end')
                    return render_template('eda/plots.html', selected_graph_type=selected_graph_type,
                                           columns=list(df.columns), graphs_2d=TWO_D_GRAPH_TYPES,
                                           action=action, graphJSON=graphJSON, x_column=x_column, y_column=y_column)

                else:
                    logger.info('Redirected to help page')
                    return render_template('eda/help.html')
            else:
                logger.info('Data frame is None')

        else:
            return redirect(url_for('/'))
    except Exception as e:
        ProjectReports.insert_record_eda(e)
        logger.error(e)


@app.route('/dp/<action>')
def data_preprocessing(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "delete-columns":
                    logger.info('Redirect To Delete Columns!')
                    return render_template('dp/delete_columns.html', columns=list(df.columns), action=action)
                elif action == "duplicate-data":
                    duplicate_data = df[df.duplicated()].head(500)
                    data = duplicate_data.to_html()
                    logger.info('Redirect To Handle Duplicate Data!')
                    return render_template('dp/duplicate.html', columns=list(df.columns), action=action, data=data,
                                           duplicate_count=len(duplicate_data))

                elif action == "outlier":
                    logger.info('Redirect To Handler Outlier!')
                    columns = Preprocessing.col_seperator(df, 'Numerical_columns')
                    return render_template('dp/outliers.html', columns=columns, action=action)

                elif action == "missing-values":
                    logger.info('Redirect To Missing-Values!')
                    columns = list(df.columns)
                    return render_template('dp/missing_values.html', columns=columns, action=action)

                elif action == "delete-outlier" or action == "remove-duplicate-data":
                    logger.info('Redirect To Handler Outlier!')
                    columns = Preprocessing.col_seperator(df, 'Numerical_columns')
                    return redirect('/dp/outlier')

                elif action == "imbalance-data":
                    logger.info('Redirect To Handle Imbalance Data!')
                    columns = list(df.columns)
                    return render_template('dp/handle_imbalance.html', action=action, columns=columns)
                else:
                    return render_template('eda/help.html')
            else:
                logger.critical('Data Frame is None')

        else:
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)


@app.route('/dp/<action>', methods=['POST'])
def data_preprocessing_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                if action == "delete-columns":
                    logger.info('Redirect To Delete Columns!')
                    columns = request.form.getlist('columns')
                    df = Preprocessing.delete_col(df, columns)
                    df = update_data(df)
                    return render_template('dp/delete_columns.html', columns=list(df.columns), action=action,
                                           status='success')

                elif action == "duplicate-data":
                    logger.info('Redirect To Handle Duplicate Data!')
                    columns = request.form.getlist('columns')
                    if len(columns) > 0:
                        df = df[df.duplicated(columns)]
                    else:
                        df = df[df.duplicated()]
                    data = df.head(500).to_html()
                    return render_template('dp/duplicate.html', columns=list(df.columns), action=action,
                                           data=data, duplicate_count=len(df), selected_column=','.join(columns))

                elif action == "remove-duplicate-data":
                    logger.info('Redirect To Handle Duplicate Data POST API')
                    columns = request.form['selected_column']

                    if len(columns) > 0:
                        data = df.drop_duplicates(subset=list(columns.split(",")), keep='last')
                    else:
                        data = df.drop_duplicates(keep='last')

                    df = update_data(data)

                    duplicate_data = df[df.duplicated()]
                    data = duplicate_data.head(500).to_html()
                    return render_template('dp/duplicate.html', columns=list(df.columns), action="duplicate-data",
                                           data=data,
                                           duplicate_count=len(duplicate_data), success=True)

                elif action == "outlier":
                    logger.info('Redirected to outlier POST API')
                    method = request.form['method']
                    column = request.form['columns']
                    lower = 25
                    upper = 75
                    graphJSON = ""
                    pie_graphJSON = ""
                    columns = Preprocessing.col_seperator(df, 'Numerical_columns')
                    outliers_list = []
                    logger.info(f'Method {method}')
                    logger.info(f'Columns {column}')
                    if method == "iqr":
                        # lower = request.form['lower']
                        # upper = request.form['upper']
                        result = EDA.outlier_detection_iqr(df.loc[:, [column]], int(lower), int(upper))
                        if len(result) > 0:
                            graphJSON = PlotlyHelper.boxplot(df, column)
                        data = result.to_html()

                        outliers_list = EDA.outlier_detection(list(df.loc[:, column]), 'iqr')
                        unique_outliers = np.unique(outliers_list)
                    else:
                        result = EDA.z_score_outlier_detection(df.loc[:, [column]])
                        if len(result) > 0:
                            list_ = list(df[~df.loc[:, column].isnull()][column])
                            graphJSON = PlotlyHelper.distplot(list_, column)
                        data = result.to_html()

                        outliers_list = EDA.outlier_detection(list(df.loc[:, column]), 'z-score')
                        unique_outliers = np.unique(outliers_list)

                    df_outliers = pd.DataFrame(pd.Series(outliers_list).value_counts(), columns=['value']).reset_index(
                        level=0)
                    if len(df_outliers) > 0:
                        pie_graphJSON = PlotlyHelper.pieplot(df_outliers, names='index', values='value',
                                                             title='Missing Values Count')

                    logger.info('Sending Data on the front end')
                    return render_template('dp/outliers.html', columns=columns, method=method, selected_column=column,
                                           outliers_list=outliers_list, unique_outliers=unique_outliers,
                                           pie_graphJSON=pie_graphJSON,
                                           action=action, data=data,
                                           outliercount=result['Total outliers'][0] if len(
                                               result['Total outliers']) > 0 else 0,
                                           graphJSON=graphJSON)

                elif action == "missing-values":
                    logger.info('Redirect To Missing Values POST API!')
                    if 'method' in request.form:
                        method = request.form['method']
                        selected_column = request.form['selected_column']
                        success = False
                        logger.info(f'Method {method}')
                        logger.info(f'Columns {selected_column}')
                        if method == 'Mean':
                            df[selected_column] = Preprocessing.fill_numerical(df, 'Mean', [selected_column])
                        elif method == 'Median':
                            df[selected_column] = Preprocessing.fill_numerical(df, 'Median', [selected_column])
                        elif method == 'Arbitrary Value':
                            df[selected_column] = Preprocessing.fill_numerical(df, 'Median', [selected_column],
                                                                               request.form['arbitrary'])
                        elif method == 'Interpolate':
                            df[selected_column] = Preprocessing.fill_numerical(df, 'Interpolate', [selected_column],
                                                                               request.form['interpolate'])
                        elif method == 'Mode':
                            df[selected_column] = Preprocessing.fill_categorical(df, 'Mode', selected_column)
                        elif method == 'New Category':
                            df[selected_column] = Preprocessing.fill_categorical(df, 'New Category', selected_column,
                                                                                 request.form['newcategory'])
                        elif method == 'Select Exist':
                            df[selected_column] = Preprocessing.fill_categorical(df, 'New Category', selected_column,
                                                                                 request.form['selectcategory'])

                        df = update_data(df)
                        success = True
                        columns = list(df.columns)
                        logger.info('Sending Data on Front End')
                        return render_template('dp/missing_values.html', columns=columns, action=action,
                                               success=success)
                    else:
                        logger.info('Method is not present in request.form')
                        columns = list(df.columns)
                        selected_column = request.form['columns']
                        data = EDA.missing_cells_table(df.loc[:, [selected_column]])
                        null_value_count = 0
                        unique_category = []
                        outlier_handler_methods = []
                        if len(data) > 0:
                            unique_category = list(df[df[selected_column].notna()][selected_column].unique())
                            null_value_count = data['Missing values'][0]
                            if df[selected_column].dtype == 'object':
                                outlier_handler_methods = OBJECT_MISSING_HANDLER

                            else:
                                outlier_handler_methods = NUMERIC_MISSING_HANDLER

                        data = data.to_html()
                        logger.info('Sending Data on Front End')
                        return render_template('dp/missing_values.html', unique_category=unique_category,
                                               columns=columns, selected_column=selected_column, action=action,
                                               data=data, null_value_count=null_value_count,
                                               handler_methods=outlier_handler_methods)

                elif action == "delete-outlier":
                    logger.info('Delete outlier')
                    values = request.form.getlist('columns')
                    selected_column = request.form['selected_column']
                    columns = Preprocessing.col_seperator(df, 'Numerical_columns')
                    df = df[~df[selected_column].isin(list(values))]
                    df = update_data(df)
                    logger.info('Sending Data on Front End')
                    return render_template('dp/outliers.html', columns=columns, action="outlier", status="success")

                elif action == "imbalance-data":
                    logger.info('Redirected to Imbalanced Data')
                    try:
                        if 'perform_action' in request.form:
                            target_column = request.form['target_column']
                            method = request.form['method']
                            range = request.form['range']
                            logger.info(f'{target_column} {method} {range}')

                            if method == 'OS':
                                new_df = Preprocessing.over_sample(df, target_column, float(range))
                            elif method == 'US':
                                new_df = Preprocessing.under_sample(df, target_column, float(range))
                            else:
                                new_df = Preprocessing.smote_technique(df, target_column, float(range))

                            df = update_data(new_df)
                            logger.info('Sending New Data on the front end')
                            return render_template('dp/handle_imbalance.html', columns=list(df.columns),
                                                   target_column=target_column, success=True)
                        else:
                            logger.info('perform_action was not found on request form')
                            target_column = request.form['target_column']
                            df_counts = pd.DataFrame(df.groupby(target_column).count()).reset_index(level=0)
                            y = list(pd.DataFrame(df.groupby(target_column).count()).reset_index(level=0).columns)[-1]
                            graphJSON = PlotlyHelper.barplot(df_counts, x=target_column, y=y)
                            pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=target_column, values=y, title='')

                            logger.info('Sending Data on Handle Imbalance page')
                            return render_template('dp/handle_imbalance.html', columns=list(df.columns),
                                                   target_column=target_column, action="imbalance-data",
                                                   pie_graphJSON=pie_graphJSON, graphJSON=graphJSON,
                                                   perform_action=True)

                    except Exception as e:
                        logger.error(e)
                        return render_template('dp/handle_imbalance.html', action=action, columns=list(df.columns),
                                               error=str(e))


                else:
                    return redirect('dp/help.html')
            else:
                logger.critical('DataFrame has no Data')

        else:
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)


@app.route('/fe/<action>', methods=['GET'])
def feature_engineering(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                data = df.head().to_html()
                if action == 'help':
                    return render_template('fe/help.html')
                elif action == 'handle-datatype':
                    return render_template('fe/handle_datatype.html', action=action,
                                           columns=df.dtypes.apply(lambda x: x.name).to_dict(),
                                           supported_dtypes=SUPPORTED_DATA_TYPES)
                elif action == 'encoding':
                    return render_template('fe/encoding.html', encoding_types=ENCODING_TYPES,
                                           columns=list(df.columns[df.dtypes == 'object']), action=action)
                elif action == 'change-column-name':
                    return render_template('fe/change_column_name.html', columns=list(df.columns), action=action)
                elif action == 'scaling':
                    return render_template('fe/scaling.html', scaler_types=SUPPORTED_SCALING_TYPES,
                                           columns=list(df.columns[df.dtypes != 'object']))
                elif action == 'feature_selection':
                    return render_template('fe/feature_selection.html',
                                           methods=FEATURE_SELECTION_METHODS_CLASSIFICATION,
                                           columns_len=df.shape[1] - 1)
                elif action == 'dimension_reduction':
                    ### Check this remove target column
                    data = df.head(200).to_html()
                    return render_template('fe/dimension_reduction.html', action=action, data=data)

                elif action == 'train_test_split':
                    return render_template('fe/train_test_split.html', data=data)
                else:
                    return 'Non-Implemented Action'
            else:
                return 'No Data'
        else:
            return redirect(url_for('/'))
    except Exception as e:
        print(e)


@app.route('/fe/<action>', methods=['POST'])
def feature_engineering_post(action):
    try:
        if 'pid' in session:
            df = load_data()
            if df is not None:
                data = df.head().to_html()
                if action == 'handle-datatype':
                    try:
                        selected_column = request.form['column']
                        datatype = request.form['datatype']
                        df = FeatureEngineering.change_data_type(df, selected_column, datatype)
                        df = update_data(df)
                        return render_template('fe/handle_datatype.html', status="success", action=action,
                                               columns=df.dtypes.apply(lambda x: x.name).to_dict(),
                                               supported_dtypes=SUPPORTED_DATA_TYPES)

                    except Exception as e:
                        return render_template('fe/handle_datatype.html', status="error", action=action,
                                               columns=df.dtypes.apply(lambda x: x.name).to_dict(),
                                               supported_dtypes=SUPPORTED_DATA_TYPES)
                elif action == 'change-column-name':
                    try:
                        selected_column = request.form['selected_column']
                        column_name = request.form['column_name']
                        df = FeatureEngineering.change_column_name(df, selected_column, column_name.strip())
                        df = update_data(df)
                        return render_template('fe/change_column_name.html', status="success", columns=list(df.columns),
                                               action=action)
                    except Exception as e:
                        return render_template('fe/change_column_name.html', status="error", columns=list(df.columns),
                                               action=action)
                elif action == 'encoding':
                    try:
                        encoding_type = request.form['encoding_type']
                        columns = request.form.getlist('columns')
                        d = {'success': True}
                        df_ = df.loc[:, columns]
                        scaling_method = request.form['scaling_method']
                        if encoding_type == "Base N Encoder":
                            df_ = FeatureEngineering.encodings(df_, columns, encoding_type,
                                                               base=int(request.form['base']))
                        elif encoding_type == "Target Encoder":
                            df_ = FeatureEngineering.encodings(df_, columns, encoding_type,
                                                               n_components=request.form['target'])
                        elif encoding_type == "Hash Encoder":
                            """This is remaining to handle"""
                            df_ = FeatureEngineering.encodings(df_, columns, encoding_type,
                                                               n_components=int(request.form['hash']))
                        else:
                            df_ = FeatureEngineering.encodings(df_, columns, encoding_type)

                        df = Preprocessing.delete_col(df, columns)
                        frames = [df, df_]
                        df = pd.concat(frames)
                        df = update_data(df)
                        return render_template('fe/encoding.html', status="success", encoding_types=ENCODING_TYPES,
                                               columns=list(df.columns[df.dtypes == 'object']), action=action)
                    except Exception as e:
                        return render_template('fe/encoding.html', status="error", encoding_types=ENCODING_TYPES,
                                               columns=list(df.columns[df.dtypes == 'object']), action=action)

                elif action == 'scaling':
                    try:
                        scaling_method = request.form['scaling_method']
                        columns = request.form.getlist('columns')
                        if len(columns) <= 0:
                            raise Exception("Column can not be zero")

                        df[columns] = FeatureEngineering.scaler(df[columns], scaling_method)
                        df = update_data(df)
                        return render_template('fe/scaling.html', status="success",
                                               scaler_types=SUPPORTED_SCALING_TYPES,
                                               columns=list(df.columns[df.dtypes != 'object']))

                    except:
                        return render_template('fe/scaling.html', status="error", scaler_types=SUPPORTED_SCALING_TYPES,
                                               columns=list(df.columns[df.dtypes != 'object']))
                elif action == 'feature_selection':
                    return render_template('fe/feature_selection.html', data=data)
                elif action == 'dimension_reduction':
                    # Check this remove target column
                    try:
                        df_ = df.loc[:, df.columns != 'Label']
                        no_pca_selected = request.form['range']
                        df_, evr_ = FeatureEngineering.dimenstion_reduction(df_, len(df_.columns))
                        df_ = df_[:, :int(no_pca_selected)]
                        df_evr = pd.DataFrame()
                        data = pd.DataFrame(df_, columns=[f"Col_{col + 1}" for col in np.arange(0, df_.shape[1])])
                        data['Label'] = df.loc[:, 'Label']
                        df = update_data(data)
                        data = df.head(200).to_html()
                        return render_template('fe/dimension_reduction.html', status="success", action=action,
                                               data=data)
                    except Exception as e:
                        print(e)
                        return render_template('fe/dimension_reduction.html', status="error", action=action, data=data)
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
            with open(r"logger\logs\logs.log") as file_in:
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
                    return render_template('model_training/train_test_split.html', data=data, columns=columns_for_list,
                                           action='train_test_split')
                elif action == 'auto_training':
                    data = df.head().to_html()
                    return render_template('model_training/auto_training.html', data=data)
                elif action == 'custom_training':
                    typ = "Classification"
                    if typ == "Regression":
                        return render_template('model_training/regression.html')
                    elif typ == "Classification":
                        return render_template('model_training/classification.html', action=action)
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
    global X_test
    global X_train
    global y_test
    global y_train

    try:
        if 'pid' in session:
            df = load_data()
            data = df.head().to_html()
            if df is not None:
                if action == 'help':
                    return render_template('model_training/help.html')
                elif action == 'train_test_split':
                    typ = "Regression"
                    if typ == "Regression":
                        fe = FeatureEngineering()
                        percent = int(request.form['range'])
                        target = request.form['columns']
                        Random_State = int(request.form['Random_State'])
                        df = pd.read_csv(r'AMES_Final_DF.csv')
                        X = df.drop(target, axis=1)
                        y = df[target]
                        X_train, X_test, y_train, y_test = FeatureEngineering.train_test_Split(cleanedData=X,
                                                                                               label=y,
                                                                                               test_size=(1 - (
                                                                                                           percent / 100)),
                                                                                               random_state=Random_State)

                        X = df.drop(target, axis=1)
                        y = df[target]
                        X_train, X_test, y_train, y_test = fe.train_test_Split(cleanedData=X, label=y,
                                                                               test_size=(1 - (percent / 100)),
                                                                               random_state=Random_State)
                        return render_template('model_training/train_test_split.html', data=data)

                    elif typ == 'Classification':
                        return render_template('model_training/auto_training.html')
                    else:
                        return render_template('model_training/auto_training.html')


                elif action == 'custom_training':

                    typ = "Classification"
                    data = next(request.form.items())[1]
                    data = dict(json.loads(data))
                    path = os.path.join(os.getcwd(), 'artifacts', 'models', 'yourModel.pkl')
                    modelName = data["method"]
                    result = None

                    if typ == "Classification":
                        try:
                            model = ClassificationModels(X_train, X_test, y_train, y_test, path=path)
                            if modelName == 'LogisticRegression':
                                penalty = data.get('penalty', 'l1')
                                dual = bool(data.get('dual', False))
                                tol = float(data.get('dual', 0.0001))
                                C = float(data.get('dual', 1.0))
                                fit_intercept = bool(data.get('dual', True))
                                intercept_scaling = int(data.get('dual', 1))
                                class_weight = data.get('dual', None)
                                random_state = int(data.get('dual', 101))
                                solver = data.get('dual', 'lbfgs')
                                max_iter = int(data.get('dual', 100))
                                multi_class = data.get('dual', 'auto')
                                verbose = int(data.get('dual', 0))
                                warm_start = bool(data.get('warm_start', False))
                                n_jobs = data.get('n_jobs', None)
                                l1_ratio = data.get('l1_ratio', None)

                                result = model.logistic_regression_classifier(penalty=penalty, dual=dual, tol=tol, C=C,
                                                                              fit_intercept=fit_intercept,
                                                                              intercept_scaling=intercept_scaling,
                                                                              class_weight=class_weight,
                                                                              random_state=random_state, solver=solver,
                                                                              max_iter=max_iter,
                                                                              multi_class=multi_class, verbose=verbose,
                                                                              warm_start=warm_start, n_jobs=n_jobs,
                                                                              l1_ratio=l1_ratio)

                            elif modelName == 'SVC':
                                C = int(data.get('C', 1.0))
                                kernel = data.get('kernel', 'rbf')
                                degree = int(data.get('degree', 3))
                                gamma = data.get('gamma', 'scale')
                                coef0 = float(data.get('coef0', 0.0))
                                shrinking = data.get('shrinking', True)
                                probability = data.get('probability', False)
                                tol = float(data.get('tol', 0.001))
                                cache_size = int(data.get('cache_size', 200))
                                class_weight = data.get('class_weight', None)
                                verbose = bool(data.get('verbose', False))
                                max_iter = int(data.get('max_iter', -1))
                                decision_function_shape = data.get('decision_function_shape', 'ovr')
                                break_ties = bool(data.get('break_ties', False))
                                random_state = int(data.get('random_state', 101))

                                result = model.support_vector_classifier(C=C, kernel=kernel, degree=degree,
                                                                         gamma=gamma, coef0=coef0, shrinking=shrinking,
                                                                         probability=probability, tol=tol,
                                                                         cache_size=cache_size,
                                                                         class_weight=class_weight,
                                                                         verbose=verbose, max_iter=max_iter,
                                                                         decision_function_shape=decision_function_shape,
                                                                         break_ties=break_ties,
                                                                         random_state=random_state)

                            elif modelName == "KNeighborsClassifier":
                                n_neighbors = int(data.get('n_neighbors', 5))
                                weights = data.get('weights', 'uniform')
                                algorithm = data.get('algorithm', 'auto')
                                leaf_size = int(data.get('leaf_size', 30))
                                p = int(data.get('p', 2))
                                metric = data.get('metric', 'minkowski')
                                metric_params = data.get('metric_params', None)
                                n_jobs = data.get('n_jobs', None)

                                result = model.k_neighbors_classifier(n_neighbors=n_neighbors, weights=weights,
                                                                      algorithm=algorithm,
                                                                      leaf_size=leaf_size, p=p, metric=metric,
                                                                      metric_params=metric_params, n_jobs=n_jobs)

                            elif modelName == "DecisionTreeClassifier":
                                criterion = data.get('criterion', 'gini')
                                splitter = data.get('splitter', 'best')
                                max_depth = int(data.get("max_depth", 5))
                                min_samples_split = int(data.get("min_samples_split", 2))
                                min_samples_leaf = int(data.get("min_samples_leaf", 1))
                                min_weight_fraction_leaf = float(data.get("min_weight_fraction_leaf", 0.0))
                                max_features = None
                                random_state = None
                                max_leaf_nodes = None
                                min_impurity_decrease = float(data.get("min_impurity_decrease", 0.0))
                                class_weight = None
                                ccp_alpha = float(data.get("ccp_alpha", 0.0))

                                result = model.decision_tree_classifier(criterion=criterion, splitter=splitter,
                                                                        max_depth=max_depth,
                                                                        min_samples_split=min_samples_split,
                                                                        min_samples_leaf=min_samples_leaf,
                                                                        min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                        max_features=max_features,
                                                                        random_state=random_state,
                                                                        max_leaf_nodes=max_leaf_nodes,
                                                                        min_impurity_decrease=min_impurity_decrease,
                                                                        class_weight=class_weight, ccp_alpha=ccp_alpha)

                            elif modelName == "RandomForestClassifier":
                                n_estimators = int(data.get("n_estimators", 100))
                                criterion = data.get("criterion", 'gini')
                                max_depth = None
                                min_samples_split = int(data.get("min_samples_split", 2))
                                min_samples_leaf = int(data.get("min_samples_leaf", 1))
                                min_weight_fraction_leaf = float(data.get("min_weight_fraction_leaf", 0.0))
                                max_features = data.get("max_features", 'auto')
                                max_leaf_nodes = None
                                min_impurity_decrease = float(data.get("min_impurity_decrease", 0.0))
                                bootstrap = bool(data.get("bootstrap", True))
                                oob_score = False,
                                n_jobs = None
                                random_state = None
                                verbose = int(data.get("verbose", 0))
                                warm_start = False
                                class_weight = None
                                ccp_alpha = float(data.get("ccp_alpha", 0.0))
                                max_samples = None

                                result = model.random_forest_classifier(n_estimators=n_estimators, criterion=criterion,
                                                                        max_depth=max_depth,
                                                                        min_samples_split=min_samples_split,
                                                                        min_samples_leaf=min_samples_leaf,
                                                                        min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                        max_features=max_features,
                                                                        max_leaf_nodes=max_leaf_nodes,
                                                                        min_impurity_decrease=min_impurity_decrease,
                                                                        bootstrap=bootstrap, oob_score=oob_score,
                                                                        n_jobs=n_jobs, random_state=random_state,
                                                                        verbose=verbose,
                                                                        warm_start=warm_start,
                                                                        class_weight=class_weight,
                                                                        ccp_alpha=ccp_alpha, max_samples=max_samples)

                            elif modelName == 'GradientBoostClassifier':
                                loss = data.get("loss", 'deviance')
                                learning_rate = float(data.get("learning_rate", 0.1))
                                n_estimators = int(data.get("n_estimators", 100))
                                subsample = float(data.get("subsample", 1.0))
                                criterion = 'friedman_mse'
                                min_samples_split = int(data.get("min_samples_split", 2))
                                min_samples_leaf = int(data.get("min_samples_leaf", 1))
                                min_weight_fraction_leaf = float(data.get("min_weight_fraction_leaf", 0.0))
                                max_depth = int(data.get("max_depth", 3))
                                min_impurity_decrease = float(data.get(0.0))
                                init = None
                                random_state = None
                                max_features = None
                                verbose = int(data.get("verbose", 0))
                                max_leaf_nodes = None
                                warm_start = False
                                validation_fraction = float(data.get("validation_fraction", 0.1))
                                n_iter_no_change = None
                                tol = float(data.get("tol", 0.0001))
                                ccp_alpha = float(data.get("ccp_alpha", 0.0))

                                result = model.gradient_boosting_classifier(loss=loss, learning_rate=learning_rate,
                                                                            n_estimators=n_estimators,
                                                                            subsample=subsample, criterion=criterion,
                                                                            min_samples_split=min_samples_split,
                                                                            min_samples_leaf=min_samples_leaf,
                                                                            min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                            max_depth=max_depth,
                                                                            min_impurity_decrease=min_impurity_decrease,
                                                                            init=init,
                                                                            random_state=random_state,
                                                                            max_features=max_features,
                                                                            verbose=verbose,
                                                                            max_leaf_nodes=max_leaf_nodes,
                                                                            warm_start=warm_start,
                                                                            validation_fraction=validation_fraction,
                                                                            n_iter_no_change=n_iter_no_change, tol=tol,
                                                                            ccp_alpha=ccp_alpha)

                            elif modelName == "AdaBoostClassifier":
                                base_estimator = data.get("base_estimator", None)
                                n_estimators = int(data.get("n_estimators", 50))
                                learning_rate = float(data.get("learning_rate", 1.0))
                                algorithm = data.get("algorithm", 'SAMME.R')
                                random_state = int(data.get("random_state", 101))

                                result = model.ada_boost_classifier(base_estimator=base_estimator,
                                                                    n_estimators=n_estimators,
                                                                    learning_rate=learning_rate,
                                                                    algorithm=algorithm, random_state=random_state)
                            else:
                                pass
                        except Exception as e:
                            logger.error(e)

                    elif typ == "Regression":
                        try:
                            model = RegressionModels(X_train, X_test, y_train, y_test, path=path)
                            if modelName == "linear":
                                fit_intercept = True
                                copy_X = True
                                n_jobs = None
                                positive = False

                                result = model.linear_regression_regressor(fit_intercept=fit_intercept, copy_X=copy_X,
                                                                           n_jobs=n_jobs,
                                                                           positive=positive)
                            elif modelName == "ridge":
                                alpha = 1.0
                                fit_intercept = True
                                copy_X = True
                                max_iter = None
                                tol = 0.001
                                solver = 'auto'
                                positive = False
                                random_state = None

                                result = model.ridge_regressor(alpha=alpha, fit_intercept=fit_intercept, copy_X=copy_X,
                                                               max_iter=max_iter, tol=tol, solver=solver,
                                                               positive=positive,
                                                               random_state=random_state)

                            elif modelName == "lasso":
                                alpha = 1.0
                                fit_intercept = True
                                precompute = False
                                copy_X = True
                                max_iter = 1000
                                tol = 0.0001
                                warm_start = False
                                positive = False
                                random_state = None
                                selection = 'cyclic'

                                result = model.lasso_regressor(alpha=alpha, fit_intercept=fit_intercept,
                                                               precompute=precompute,
                                                               copy_X=copy_X,
                                                               max_iter=max_iter, tol=tol, warm_start=warm_start,
                                                               positive=positive,
                                                               random_state=random_state, selection=selection)

                            elif modelName == "elastic":
                                alpha = 1.0
                                l1_ratio = 0.5
                                fit_intercept = True
                                precompute = False
                                max_iter = 1000
                                copy_X = True
                                tol = 0.0001
                                warm_start = False
                                positive = False
                                random_state = None
                                selection = 'cyclic'

                                result = model.elastic_net_regressor(alpha=alpha, l1_ratio=l1_ratio,
                                                                     fit_intercept=fit_intercept,
                                                                     precompute=precompute,
                                                                     copy_X=copy_X, max_iter=max_iter, tol=tol,
                                                                     warm_start=warm_start,
                                                                     positive=positive,
                                                                     random_state=random_state, selection=selection)
                            elif modelName == "decision_tree":
                                criterion = 'squared_error'
                                splitter = 'best'
                                max_depth = None
                                min_samples_split = 2
                                min_samples_leaf = 1
                                min_weight_fraction_leaf = 0.0
                                max_features = None
                                random_state = None
                                max_leaf_nodes = None
                                min_impurity_decrease = 0.0
                                ccp_alpha = 0.0

                                result = model.decision_tree_regressor(criterion=criterion, splitter=splitter,
                                                                       max_depth=max_depth,
                                                                       min_samples_split=min_samples_split,
                                                                       min_samples_leaf=min_samples_leaf,
                                                                       min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                       max_features=max_features,
                                                                       random_state=random_state,
                                                                       max_leaf_nodes=max_leaf_nodes,
                                                                       min_impurity_decrease=min_impurity_decrease,
                                                                       ccp_alpha=ccp_alpha)
                            elif modelName == "random_forest":
                                n_estimators = 100
                                criterion = 'squared_error'
                                max_depth = None
                                min_samples_split = 2
                                min_samples_leaf = 1
                                min_weight_fraction_leaf = 0.0
                                max_features = 'auto'
                                max_leaf_nodes = None
                                min_impurity_decrease = 0.0
                                bootstrap = True
                                oob_score = False
                                n_jobs = None
                                random_state = None
                                verbose = 0
                                warm_start = False
                                ccp_alpha = 0.0
                                max_samples = None

                                result = model.random_forest_regressor(n_estimators=n_estimators, criterion=criterion,
                                                                       max_depth=max_depth,
                                                                       min_samples_split=min_samples_split,
                                                                       min_samples_leaf=min_samples_leaf,
                                                                       min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                       max_features=max_features,
                                                                       max_leaf_nodes=max_leaf_nodes,
                                                                       min_impurity_decrease=min_impurity_decrease,
                                                                       bootstrap=bootstrap,
                                                                       oob_score=oob_score, n_jobs=n_jobs,
                                                                       random_state=random_state,
                                                                       verbose=verbose, warm_start=warm_start,
                                                                       ccp_alpha=ccp_alpha,
                                                                       max_samples=max_samples)
                            elif modelName == "svr":
                                kernel = 'rbf'
                                degree = 3
                                gamma = 'scale'
                                coef0 = 0.0
                                tol = 0.001
                                C = 1.0
                                epsilon = 0.1
                                shrinking = True
                                cache_size = 200
                                verbose = False
                                max_iter = - 1

                                result = model.support_vector_regressor(kernel=kernel, degree=degree, gamma=gamma,
                                                                        coef0=coef0,
                                                                        tol=tol, C=C,
                                                                        epsilon=epsilon,
                                                                        shrinking=shrinking, cache_size=cache_size,
                                                                        verbose=verbose, max_iter=max_iter)
                            elif modelName == "adr":
                                base_estimator = None
                                n_estimators = 50
                                learning_rate = 1.0
                                loss = 'linear'
                                random_state = None

                                result = model.ada_boost_regressor(base_estimator=base_estimator,
                                                                   n_estimators=n_estimators,
                                                                   learning_rate=learning_rate, loss=loss,
                                                                   random_state=random_state)

                            elif modelName == "gbr":
                                loss = 'squared_error'
                                learning_rate = 0.1
                                n_estimators = 100
                                subsample = 1.0
                                criterion = 'friedman_mse'
                                min_samples_split = 2
                                min_samples_leaf = 1
                                min_weight_fraction_leaf = 0.0
                                max_depth = 3
                                min_impurity_decrease = 0.0
                                init = None
                                random_state = None
                                max_features = None
                                alpha = 0.9
                                verbose = 0
                                max_leaf_nodes = None
                                warm_start = False
                                validation_fraction = 0.1
                                n_iter_no_change = None
                                tol = 0.0001
                                ccp_alpha = 0.0

                                result = model.gradient_boosting_regressor(loss=loss, learning_rate=learning_rate,
                                                                           n_estimators=n_estimators,
                                                                           subsample=subsample, criterion=criterion,
                                                                           min_samples_split=min_samples_split,
                                                                           min_samples_leaf=min_samples_leaf,
                                                                           min_weight_fraction_leaf=min_weight_fraction_leaf,
                                                                           max_depth=max_depth,
                                                                           min_impurity_decrease=min_impurity_decrease,
                                                                           init=init,
                                                                           random_state=random_state,
                                                                           max_features=max_features,
                                                                           alpha=alpha,
                                                                           verbose=verbose,
                                                                           max_leaf_nodes=max_leaf_nodes,
                                                                           warm_start=warm_start,
                                                                           validation_fraction=validation_fraction,
                                                                           n_iter_no_change=n_iter_no_change, tol=tol,
                                                                           ccp_alpha=ccp_alpha)
                            else:
                                pass
                            return render_template('model_training/classification.html')
                        except Exception as e:
                            logger.error(e)

                    elif typ == 'Clustering':
                        try:
                            model = ClusteringModels(X_train, X_test, path=path)

                            if modelName == "KMeans":
                                n_clusters = 8
                                init = 'k-means++'
                                n_init = 10
                                max_iter = 300
                                tol = 0.0001
                                verbose = 0
                                random_state = None
                                copy_x = True
                                algorithm = 'auto'

                                result = model.kmeans_clustering(n_clusters=n_clusters, init=init, n_init=n_init,
                                                                 max_iter=max_iter, tol=tol,
                                                                 verbose=verbose, random_state=random_state,
                                                                 copy_x=copy_x,
                                                                 algorithm=algorithm)
                            elif modelName == "DBSCAN":
                                eps = 0.5
                                min_samples = 5
                                metric = 'euclidean'
                                metric_params = None
                                algorithm = 'auto'
                                leaf_size = 30
                                p = None
                                n_jobs = None

                                result = model.dbscan_clustering(eps=eps, min_samples=min_samples, metric=metric,
                                                                 metric_params=metric_params,
                                                                 algorithm=algorithm, leaf_size=leaf_size, p=p,
                                                                 n_jobs=n_jobs)
                            elif modelName == "AgglomerativeClustering":
                                n_clusters = 2
                                affinity = 'euclidean'
                                memory = None
                                connectivity = None
                                compute_full_tree = 'auto'
                                linkage = 'ward'
                                distance_threshold = None
                                compute_distances = False

                                result = model.agglomerative_clustering(n_clusters=n_clusters, affinity=affinity,
                                                                        memory=memory,
                                                                        connectivity=connectivity,
                                                                        compute_full_tree=compute_full_tree,
                                                                        linkage=linkage,
                                                                        distance_threshold=distance_threshold,
                                                                        compute_distances=compute_distances)
                            else:
                                pass
                        except Exception as e:
                            logger.error(e)
                else:
                    return "Non Implemented Method"
        else:
            logger.critical('DataFrame has no data')
    except Exception as e:
        logger.error(e)


@app.route('/Machine/<action>', methods=['GET'])
def machine(action):
    return render_template('Machine/system.html')


@app.route('/scheduler/<action>', methods=['GET'])
def scheduler_get(action):
    if action == 'help':
        return render_template('scheduler/help.html')

    if action == 'Training_scheduler':
        return render_template('scheduler/Training_scheduler.html', action=action, localdate=None)


@app.route('/scheduler/<action>', methods=['POST'])
def scheduler_post(action):
    if action == 'help':
        return render_template('scheduler/help.html')

    if action == 'Training_scheduler':
        return render_template('scheduler/Training_scheduler.html')


# Missing data Api
@app.route('/api/missing-data', methods=['GET', 'POST'])
def missing_data():
    try:
        df = load_data()
        selected_column = request.json['selected_column']
        method = request.json['method']
        new_df = None
        if method == 'Mean' or method == 'Median' or method == 'Arbitrary Value' or method == 'Interpolate':
            before = {}
            after = {}
            list_ = list(df[~df.loc[:, selected_column].isnull()][selected_column])
            before['graph'] = PlotlyHelper.distplot(list_, selected_column)
            before['skewness'] = Preprocessing.find_skewness(list_)
            before['kurtosis'] = Preprocessing.find_kurtosis(list_)

            if method == 'Mean':
                new_df = Preprocessing.fill_numerical(df, 'Mean', [selected_column])
            elif method == 'Median':
                new_df = Preprocessing.fill_numerical(df, 'Median', [selected_column])
            elif method == 'Arbitrary Value':
                new_df = Preprocessing.fill_numerical(df, 'Median', [selected_column], request.json['Arbitrary_Value'])
            elif method == 'Interpolate':
                new_df = Preprocessing.fill_numerical(df, 'Interpolate', [selected_column], request.json['Interpolate'])
            else:
                pass

            new_list = list(new_df.loc[:, selected_column])

            after['graph'] = PlotlyHelper.distplot(new_list, selected_column)
            after['skewness'] = Preprocessing.find_skewness(new_list)
            after['kurtosis'] = Preprocessing.find_kurtosis(new_list)

            d = {
                'success': True,
                'before': before,
                'after': after
            }
            return jsonify(d)

        if method == 'Mode' or method == 'New Category' or method == 'Select Exist':
            before = {}
            after = {}
            df_counts = pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
            y = list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:, 1].values)
            pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column, values=y, title='')
            before['graph'] = pie_graphJSON

            if method == 'Mode':
                df[selected_column] = Preprocessing.fill_categorical(df, 'Mode', selected_column)
                df_counts = pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y = list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:, 1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column, values=y, title='')

                after['graph'] = pie_graphJSON
            elif method == 'New Category':
                df[selected_column] = Preprocessing.fill_categorical(df, 'New Category', selected_column,
                                                                     request.json['newcategory'])
                df_counts = pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y = list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:, 1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column, values=y, title='')
                after['graph'] = pie_graphJSON

            elif method == 'Select Exist':
                df[selected_column] = Preprocessing.fill_categorical(df, 'Select Exist', selected_column,
                                                                     request.json['selectcategory'])
                df_counts = pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0)
                y = list(pd.DataFrame(df.groupby(selected_column).count()).reset_index(level=0).iloc[:, 1].values)
                pie_graphJSON = PlotlyHelper.pieplot(df_counts, names=selected_column, values=y, title='')

                after['graph'] = pie_graphJSON

            d = {
                'success': True,
                'before': before,
                'after': after
            }
            return jsonify(d)

    except Exception as e:
        print(e)
        return jsonify({'success': False})


# Feature Encoding Api
@app.route('/api/encoding', methods=['GET', 'POST'])
def fe_encoding():
    try:
        df = load_data()
        encoding_type = request.json['encoding_type']
        columns = request.json['columns']
        d = {'success': True}
        df = df.loc[:, columns]
        if encoding_type == "Base N Encoder":
            df = FeatureEngineering.encodings(df, columns, encoding_type, base=request.json['base'])
        elif encoding_type == "Target Encoder":
            df = FeatureEngineering.encodings(df, columns, encoding_type, n_components=request.json['target'])
        elif encoding_type == "Hash Encoder":
            """This is remaining to handle"""
            df = FeatureEngineering.encodings(df, columns, encoding_type, n_components=request.json['hash'])
        else:
            df = FeatureEngineering.encodings(df, columns, encoding_type)
        data = df.head(200).to_html()
        d['data'] = data
        return jsonify(d)

    except Exception as e:
        print(e)
        return jsonify({'success': False})


# Dimension Reduction Api
@app.route('/api/pca', methods=['POST'])
def fe_pca():
    try:
        df = load_data()
        df_ = df.loc[:, df.columns != 'Label']
        df_, evr_ = FeatureEngineering.dimenstion_reduction(df_, len(df_.columns))
        d = {'success': True}

        df_evr = pd.DataFrame()
        df_evr['No of Components'] = np.arange(0, len(evr_)) + 1
        df_evr['Variance %'] = evr_.round(2)

        data = pd.DataFrame(df_, columns=[f"Col_{col + 1}" for col in np.arange(0, df_.shape[1])]).head(200).to_html()
        graph = PlotlyHelper.line(df_evr, 'No of Components', 'Variance %')

        d['data'] = data
        d['graph'] = graph
        d['no_pca'] = len(evr_)
        return jsonify(d)

    except Exception as e:
        print(e)
        return jsonify({'success': False})


# Feature Selection Api
@app.route('/api/feature_selection', methods=['POST'])
def fe_feature_selection():
    try:
        df = load_data()
        df_ = df.loc[:, df.columns != 'Label']
        method = request.json['method']
        d = {'success': True}

        if method == "Find Constant Features":
            threshold = request.json['threshold']
            high_variance_columns = FeatureEngineering.feature_selection(df_, 'Label', method,
                                                                         threshold=float(threshold))
            high_variance_columns = list(high_variance_columns)
            low_variance_columns = [col for col in df_.columns if col not in high_variance_columns]
            d['high_variance_columns'] = high_variance_columns
            d['low_variance_columns'] = list(low_variance_columns)

        elif method == "Mutual Info Classification" or method == "Extra Trees Classifier":
            df_ = FeatureEngineering.feature_selection(df_, df.loc[:, 'Label'], method)
            graph = PlotlyHelper.barplot(df_, 'Feature', 'Value')
            d['graph'] = graph

        elif method == "Correlation":
            graph = PlotlyHelper.heatmap(df)
            d['graph'] = graph

        return jsonify(d)

    except Exception as e:
        print(e)
        return jsonify({'success': False})


if __name__ == '__main__':
    if mysql is None or mongodb is None:
        print("Not Able To connect With Database (Check Mongo and Mysql Connection)")
    else:
        app.run(host="127.0.0.1", port=5000, debug=True)
