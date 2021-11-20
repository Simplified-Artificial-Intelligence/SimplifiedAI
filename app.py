from flask import Flask, redirect, url_for, render_template, request, session, send_file, send_from_directory
from werkzeug.wrappers import Response
import re
from src.constants.constants import PROJECT_TYPES, ProjectActions
from src.utils.databases.mysql_helper import MySqlHelper
from werkzeug.utils import secure_filename
import os
import time
from src.utils.common.common_helper import decrypt, read_config, unique_id_generator, Hashing, encrypt
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
from src.constants.constants import REGRESSION_MODELS, CLASSIFICATION_MODELS, CLUSTERING_MODELS, ALL_MODELS, TIMEZONE
from src.utils.common.data_helper import load_data, csv_to_json, to_tsv, csv_to_excel, update_data
from src.utils.common.cloud_helper import aws_s3_helper
from src.utils.common.cloud_helper import gcp_browser_storage
from src.utils.common.cloud_helper import azure_data_helper
from src.utils.common.database_helper import mysql_data_helper, mongo_data_helper
from src.utils.common.database_helper import cassandra_connector
from src.utils.common.project_report_helper import ProjectReports
from src.routes.routes_api import app_api
from loguru import logger
from src.routes.routes_eda import app_eda
from src.routes.routes_dp import app_dp
from src.routes.routes_fe import app_fe
from src.routes.routes_training import app_training
from from_root import from_root
import scheduler
from openpyxl import load_workbook

import numpy as np
import pandas as pd
import zipfile
import pathlib
import io
# Yaml Config File
config_args = read_config("./config.yaml")

log_path = os.path.join(from_root(), config_args['logs']['logger'], config_args['logs']['generallogs_file'])
logger.remove()
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
logger.info('App Started')

app.register_blueprint(app_api)
app.register_blueprint(app_eda)
app.register_blueprint(app_dp)
app.register_blueprint(app_fe)
app.register_blueprint(app_training)

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
            select tp.Id,tp.Name,tp.Description,tp.Cassandra_Table_Name,
            ts.Name,ts.Indetifier,tp.Pid,tp.TargetColumn,tpy.Name
            from tblProjects as tp
            join tblProjectType as tpy
                on tpy.Id=tp.ProjecTtype
            join tblProjectStatus as ts
                on ts.Id=tp.Status
            where tp.UserId={session.get('id')} and tp.IsActive=1
            order by 1 desc'''

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
        return render_template('500.html', exception=e)



@app.route('/project', methods=['GET', 'POST'])
def project():
    # df = None, table_name = None
    try:
        if 'loggedin' in session:
            download_status = None
            file_path = None
            if request.method == "GET":
                return render_template('new_project.html', loggedin=True, project_types=PROJECT_TYPES)
            else:
                source_type = request.form['source_type']
                f = None
                if source_type == 'uploadFile':
                    name = request.form['project_name']
                    description = request.form['project_desc']
                    project_type = request.form['project_type']
                    print(source_type, name, description)
                    if len(request.files) > 0:
                        f = request.files['file']

                    ALLOWED_EXTENSIONS = ['csv', 'tsv', 'json']
                    message = ''
                    if not name.strip():
                        message = 'Please enter project name'
                    elif not description.strip():
                        message = 'Please enter project description'
                    elif f.filename.strip() == '':
                        message = 'Please select a file to upload'
                    elif f.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                        message = 'This file format is not allowed, please select mentioned one'

                    if message:
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)

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
                        message = 'This file format is currently not supported'
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)

                    project_id = unique_id_generator()
                    inserted_rows = mongodb.create_new_project(project_id, df)

                    if inserted_rows > 0:
                        userId = session.get('id')
                        status = 1
                        query = f"""INSERT INTO tblProjects (UserId, Name, Description, Status, 
                       Cassandra_Table_Name,Pid,ProjectType) VALUES
                       ("{userId}", "{name}", "{description}", "1", "{table_name}","{project_id}","{project_type}")"""

                        rowcount = mysql.insert_record(query)
                        if rowcount > 0:
                            return redirect(url_for('index'))
                        else:
                            message = "Error while creating new Project"
                            logger.info(message)
                            return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)
                    else:
                        message = "Error while creating new Project"
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)

                elif source_type == 'uploadResource':
                    name = request.form['project_name']
                    description = request.form['project_desc']
                    resource_type = request.form['resource_type']

                    if not name.strip():
                        message = 'Please enter project name'
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)
                    elif not description.strip():
                        message = 'Please enter project description'
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)

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

                    else:
                        return render_template('new_project.html', msg="Select Any Various Resource Type!!")

                    if download_status == 'Successful':
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
                            return render_template('new_project.html', msg=msg)

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
                                message = "Error while creating new Project"
                                logger.info(message)
                                return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)
                        else:
                            message = "Error while creating new Project"
                            logger.info(message)
                            return render_template('new_project.html', msg=message)
                    else:
                        message = "Error while creating new Project"
                        logger.info(message)
                        return render_template('new_project.html', msg=message, project_types=PROJECT_TYPES)
        else:
            return redirect(url_for('login'))

    except Exception as e:
        logger.error(e)
        return render_template('new_project.html', msg=e.__str__())


@app.route('/edit-project/<pid>', methods=['GET', 'POST'])
def edit_project(pid):
    query = f'''select tp.Name,tp.Description,tp.TargetColumn,tpy.Name from tblProjects as tp
            join tblProjectType as tpy on tpy.Id=tp.ProjecTtype
            where tp.Pid='{pid}';'''
    print(pid)
    data = mysql.fetch_one(query)

    project_data = {'project_name': data[0], 'project_desp': data[1],
                    'project_type': data[3], 'target_col': data[2]}
    return render_template('edit_project.html', project_types=PROJECT_TYPES, data=project_data)


@app.route('/prediction_file/<action>', methods=['GET', 'POST'])
def prediction(action):
    if 'loggedin' in session:
        try:
            print(request.method)
            if request.method == "POST":
                download_status = None
                file_path = None
                source_type = request.form['source_type']
                print(source_type)

                if source_type == 'uploadFile':

                    ALLOWED_EXTENSIONS = ['csv', 'tsv', 'json', 'xlsx']
                    # message = ''
                    # if f.filename.strip() == '':
                    #     message = 'Please select a file to upload'
                    # elif f.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                    #     message = 'This file format is not allowed, please select mentioned one'
                    # if message:
                    #     print(message)
                    #     return render_template('prediction.html', msg=message)

                    f = request.files['file']
                    filename = secure_filename(f.filename)
                    file_path = os.path.join('artifacts', f'{action}', filename)
                    f.save(file_path)
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith('.tsv'):
                        df = pd.read_csv(file_path, sep='\t')
                    elif file_path.endswith('.json'):
                        df = pd.read_json(file_path)
                    elif file_path.endswith('.xlsx'):
                        df = pd.read_excel(file_path)
                    else:
                        msg = 'This file format is currently not supported'
                        return render_template('prediction.html', msg=msg)

                    return redirect(url_for('index'))

                elif source_type == 'uploadResource':
                    resource_type = request.form['resource_type']

                    if resource_type == "awsS3bucket":
                        region_name = request.form['region_name']
                        aws_access_key_id = request.form['aws_access_key_id']
                        aws_secret_access_key = request.form['aws_secret_access_key']
                        bucket_name = request.form['bucket_name']
                        file_name = request.form['file_name']
                        file_path = os.path.join('src/temp_data_store', file_name)
                        aws_s3 = aws_s3_helper(region_name, aws_access_key_id, aws_secret_access_key)
                        conn_msg = aws_s3.check_connection(bucket_name, file_name)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

                        download_status = aws_s3.download_file_from_s3(bucket_name, file_name, file_path)
                        logger.info(resource_type, download_status, file_path)

                    elif resource_type == "gcpStorage":
                        credentials_file = request.files['GCP_credentials_file']
                        bucket_name = request.form['bucket_name']
                        file_name = request.form['file_name']
                        credentials_filename = secure_filename(credentials_file.filename)
                        credentials_file_path = os.path.join(app.config['UPLOAD_FOLDER'], credentials_filename)
                        credentials_file.save(credentials_file_path)
                        file_path = os.path.join('src/temp_data_store', file_name)
                        logger.info(credentials_file_path, file_path, file_name, bucket_name)
                        gcp = gcp_browser_storage(credentials_file_path)
                        conn_msg = gcp.check_connection(bucket_name, file_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

                        download_status = gcp.download_file_from_bucket(file_name, file_path, bucket_name)
                        logger.info(download_status)

                    elif resource_type == "mySql":
                        host = request.form['host']
                        port = request.form['port']
                        user = request.form['user']
                        password = request.form['password']
                        database = request.form['database']
                        table_name = request.form['table_name']
                        file_path = os.path.join('src/temp_data_store', table_name)
                        logger.info(file_path)

                        mysql_data = mysql_data_helper(host, port, user, password, database)
                        conn_msg = mysql_data.check_connection(table_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

                        download_status = mysql_data.retrive_dataset_from_table(table_name, file_path)
                        logger.info(download_status)

                    elif resource_type == "cassandra":
                        secure_connect_bundle = request.files['secure_connect_bundle']
                        client_id = request.form['client_id']
                        client_secret = request.form['client_secret']
                        keyspace = request.form['keyspace']
                        table_name = request.form['table_name']
                        data_in_tabular = request.form['data_in_tabular']
                        secure_connect_bundle_filename = secure_filename(secure_connect_bundle.filename)
                        secure_connect_bundle_file_path = os.path.join(r'src/temp_data_store',
                                                                       secure_connect_bundle_filename)
                        secure_connect_bundle.save(secure_connect_bundle_file_path)
                        file_path = os.path.join('src/temp_data_store', f"{table_name}.csv")
                        logger.info(secure_connect_bundle_file_path, file_path)

                        cassandra_db = cassandra_connector(secure_connect_bundle_file_path, client_id, client_secret,
                                                           keyspace)
                        conn_msg = cassandra_db.check_connection(table_name)
                        logger.info(conn_msg)
                        if conn_msg != 'Successful':
                            logger.info(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

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
                        file_path = os.path.join('src/temp_data_store', f"{collection}.csv")
                        mongo_helper = mongo_data_helper(mongo_db_url)
                        conn_msg = mongo_helper.check_connection(mongo_database, collection)
                        if conn_msg != 'Successful':
                            print(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

                        download_status = mongo_helper.retrive_dataset(mongo_database, collection, file_path)
                        logger.info(download_status)

                    elif resource_type == "azureStorage":
                        azure_connection_string = request.form['azure_connection_string']
                        container_name = request.form['container_name']
                        file_name = request.form['file_name']
                        file_path = os.path.join('src/temp_data_store', file_name)
                        azure_helper = azure_data_helper(azure_connection_string)
                        conn_msg = azure_helper.check_connection(container_name, file_name)

                        if conn_msg != 'Successful':
                            print(conn_msg)
                            return render_template('prediction.html', msg=conn_msg)

                        download_status = azure_helper.download_file(container_name, file_name, file_path)
                        logger.info(download_status)
                    else:
                        # Implement something here
                        pass

                    if download_status == 'Successful':

                        if file_path.endswith('.csv'):
                            df = pd.read_csv(file_path)
                        elif file_path.endswith('.tsv'):
                            df = pd.read_csv(file_path, sep='\t')
                        elif file_path.endswith('.json'):
                            df = pd.read_json(file_path)
                        elif file_path.endswith('.xlsx'):
                            df = pd.read_excel(file_path)
                        else:
                            msg = 'This file format is currently not supported'
                            return render_template('prediction.html', msg=msg)

                        print(df)
                        return redirect(url_for('index'))
                    else:
                        return render_template('prediction.html', loggedin=True, data={'pid': action},
                                               msg="Failed to download the file!!")
            else:
                return render_template('prediction.html', loggedin=True)

        except Exception as e:
            return render_template('prediction.html', loggedin=True, msg=e.__str__())

    else:
        return redirect(url_for('login'))


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


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 404 status explicitly
    return render_template('500.html',msg=str(e)), 500

@app.route('/export-resources/<pid>', methods=['GET','POST'])
def exportResources(pid):
    try:
        if 'loggedin' in session:
            if request.method=='GET':
                folder_path = os.path.join(from_root(), config_args['dir_structure']['artifacts_dir'], pid)
                if not os.path.exists(folder_path):
                    return render_template('export-resources.html',status="error", msg="No resources found to export, please train your model first")
                logger.info('Redirect To Export Reources Page')
                return render_template('export-resources.html',status="success",pid=pid)
            else:
                folder_path = os.path.join(from_root(), config_args['dir_structure']['artifacts_dir'], pid)
                
                
                """Get Projects Actions"""
                query_ = f"""
                        Select tblProjectActions.Name , Input,Output from  tblProject_Actions_Reports 
                        Join tblProjectActions on tblProject_Actions_Reports.ProjectActionId=tblProjectActions.Id
                        join tblProjects on tblProjects.Id=tblProject_Actions_Reports.ProjectId
                        where PId="{pid}"
                        """
                action_performed = mysql.fetch_all(query_)
                
                """Save Actions file"""
                if len(action_performed)>0:
                    df=pd.DataFrame(action_performed,columns=['Action','Input','Output'])
                    df.to_csv(os.path.join(folder_path,'actions.csv'))
                    
                base_path = pathlib.Path(folder_path)
                data = io.BytesIO()
                with zipfile.ZipFile(data, mode='w') as z:
                    for f_name in base_path.iterdir():
                        z.write(f_name)
                data.seek(0)
                return Response(
                    data,
                    mimetype='application/zip',
                    headers={"Content-disposition": f"attachment; filename=data.zip"})
        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.info(e)
        return render_template('export-resources.html',status="error", msg=str(e))
    
    
@app.route('/exportFile/<pid>/<project_name>', methods=['GET'])
def exportForm(pid,project_name):
    if 'loggedin' in session:
        logger.info('Redirect To Export File Page')
        return render_template('exportFile.html',
                               data={"project_name": project_name, "project_id": pid})
    else:
        return redirect(url_for('login'))


@app.route('/exportFile/<project_id>/<project_name>', methods=['POST'])
def exportFile(project_id,project_name):
    try:
        if 'loggedin' in session:
            logger.info('Export File')

            fileType = request.form['fileType']
            print(project_id, project_name)
            if fileType != "":
                download_status, file_path = mongodb.download_collection_data(project_id, 'csv')
                if download_status != "Successful":
                    render_template('exportFile.html',
                                    data={"project_name": project_name, "project_id": project_id},
                                    msg="OOPS something went wrong!!")

            if fileType == 'csv':
                content = pd.read_csv(file_path)
                return Response(content.to_csv(index=False), mimetype="text/csv",
                                headers={"Content-disposition": f"attachment; filename={project_name}.csv"})

            elif fileType == 'tsv':
                content = pd.read_csv(file_path)
                return Response(content.to_csv(sep='\t', index=False), mimetype="text/tsv",
                                headers={"Content-disposition": f"attachment; filename={project_name}.tsv"})

            elif fileType == 'xlsx':
                content = pd.read_csv(file_path)
                content.to_excel(os.path.join(app.config["UPLOAD_FOLDER"], f'{project_name}.xlsx'), index=False)
                return send_from_directory(directory=app.config["UPLOAD_FOLDER"], path=f'{project_name}.xlsx',
                                           as_attachment=True)

            elif fileType == 'json':
                content = pd.read_csv(file_path)
                return Response(content.to_json(), mimetype="text/json",
                                headers={"Content-disposition": f"attachment; filename={project_name}.json"})
            else:
                return render_template('exportFile.html', data={"project_name": project_name, "project_id": project_id},
                                       msg="Select Any File Type!!")

        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.info(e)
        return render_template('exportFile.html', data={"project_name": project_name, "project_id": project_id},
                               msg=e.__str__())


@app.route('/exportProject/<project_name>/<project_id>', methods=['GET', 'POST'])
def exportCloudDatabaseFile(project_name, project_id):
    try:
        global download_status
        if 'loggedin' in session:
            print(project_name, project_id)
            logger.info('Export File')
            source_type = request.form['source_type']

            if source_type == 'uploadCloud':
                cloudType = request.form['cloudType']

                if cloudType == 'awsS3bucket':
                    region_name = request.form['region_name']
                    aws_access_key_id = request.form['aws_access_key_id']
                    aws_secret_access_key = request.form['aws_secret_access_key']
                    bucket_name = request.form['aws_bucket_name']
                    file_type = request.form['fileTypeAws']

                    aws_s3 = aws_s3_helper(region_name, aws_access_key_id, aws_secret_access_key)
                    conn_msg = aws_s3.check_connection(bucket_name, 'none')

                    if conn_msg != 'File does not exist!!':
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, file_type)
                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = aws_s3.push_file_to_s3(bucket_name, file_path,
                                                           f'{project_name}_{timestamp}.{file_type}')
                    if upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f"{project_name}_{timestamp}.{file_type} pushed to {bucket_name} bucket")
                    return redirect(url_for('index'))

                elif cloudType == 'azureStorage':
                    azure_connection_string = request.form['azure_connection_string']
                    container_name = request.form['container_name']
                    file_type = request.form['fileTypeAzure']
                    azure_helper = azure_data_helper(azure_connection_string)
                    conn_msg = azure_helper.check_connection(container_name, 'none')

                    if conn_msg != 'File does not exist!!':
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, file_type)
                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = azure_helper.upload_file(file_path, container_name,
                                                             f'{project_name}_{timestamp}.{file_type}')
                    if upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f"{project_name}_{timestamp}.{file_type} pushed to {container_name} container")
                    return redirect(url_for('index'))

                elif cloudType == 'gcpStorage':
                    credentials_file = request.files['GCP_credentials_file']
                    bucket_name = request.form['gcp_bucket_name']
                    file_type = request.form['fileTypeGcp']
                    credentials_filename = secure_filename(credentials_file.filename)
                    credentials_file_path = os.path.join(app.config['UPLOAD_FOLDER'], credentials_filename)
                    credentials_file.save(credentials_file_path)
                    gcp = gcp_browser_storage(credentials_file_path)
                    conn_msg = gcp.check_connection(bucket_name, 'none')
                    if conn_msg != 'File does not exist!!':
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, file_type)
                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = gcp.upload_to_bucket(f'{project_name}_{timestamp}.{file_type}', file_path,
                                                         bucket_name)

                    if upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f"{project_name}_{timestamp}.{file_type} pushed to {bucket_name} bucket")
                    return redirect(url_for('index'))

                else:
                    return render_template('exportFile.html',
                                           data={"project_name": project_name, "project_id": project_id},
                                           msg="Select Any Cloud Type!!")

            elif source_type == 'uploadDatabase':
                databaseType = request.form['databaseType']

                if databaseType == 'mySql':
                    host = request.form['host']
                    port = request.form['port']
                    user = request.form['user']
                    password = request.form['password']
                    database = request.form['database']

                    mysql_data = mysql_data_helper(host, port, user, password, database)
                    conn_msg = mysql_data.check_connection('none')

                    if conn_msg != "table does not exist!!":
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, "csv")
                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = mysql_data.push_file_to_table(file_path, f'{project_name}_{timestamp}')
                    if download_status != 'Successful' or upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f'{project_name}_{timestamp} table created in {database} database')
                    return redirect(url_for('index'))

                elif databaseType == 'cassandra':
                    secure_connect_bundle = request.files['secure_connect_bundle']
                    client_id = request.form['client_id']
                    client_secret = request.form['client_secret']
                    keyspace = request.form['keyspace']
                    secure_connect_bundle_filename = secure_filename(secure_connect_bundle.filename)
                    secure_connect_bundle_file_path = os.path.join(app.config['UPLOAD_FOLDER'],
                                                                   secure_connect_bundle_filename)
                    secure_connect_bundle.save(secure_connect_bundle_file_path)

                    cassandra_db = cassandra_connector(secure_connect_bundle_file_path, client_id, client_secret,
                                                       keyspace)
                    conn_msg = cassandra_db.check_connection('none')
                    if conn_msg != 'table does not exist!!':
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, "csv")

                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = cassandra_db.push_dataframe_to_table(pd.read_csv(file_path),
                                                                         f'{project_name}_{timestamp}')
                    if download_status != 'Successful' or upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f'{project_name}_{timestamp} table created in {keyspace} keyspace')
                    return redirect(url_for('index'))

                elif databaseType == 'mongodb':
                    mongo_db_url = request.form['mongo_db_url']
                    mongo_database = request.form['mongo_database']
                    mongo_helper = mongo_data_helper(mongo_db_url)
                    conn_msg = mongo_helper.check_connection(mongo_database, 'none')
                    if conn_msg != "collection does not exits!!":
                        logger.info(conn_msg)
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=conn_msg)
                    download_status, file_path = mongodb.download_collection_data(project_id, "csv")
                    if download_status != "Successful":
                        render_template('exportFile.html',
                                        data={"project_name": project_name, "project_id": project_id},
                                        msg="OOPS something went wrong!!")
                    timestamp = round(time.time() * 1000)
                    upload_status = mongo_helper.push_dataset(mongo_database, f'{project_name}_{timestamp}', file_path)
                    if download_status != 'Successful' or upload_status != 'Successful':
                        return render_template('exportFile.html',
                                               data={"project_name": project_name, "project_id": project_id},
                                               msg=upload_status)
                    print(f'{project_name}_{timestamp} collection created in {mongo_database} database')
                    return redirect(url_for('index'))

                else:
                    return render_template('exportFile.html',
                                           data={"project_name": project_name, "project_id": project_id},
                                           msg="Select Any Database Type!!")
            else:
                return render_template('exportFile.html',
                                       data={"project_name": project_name, "project_id": project_id},
                                       msg="Select Any Cloud or Database")
        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.info(e)
        return render_template('exportFile.html', data={"project_name": project_name}, msg=e.__str__())


@app.route('/projectReport/<id>', methods=['GET', 'POST'])
def projectReport(id):
    if 'loggedin' in session:
        logger.info('Redirect To Project Report Page')
        records, projectStatus = ProjectReports.get_record_by_pid(id, None)
        return render_template('projectReport.html', data={"id": id, "moduleId": None}, records=records.to_html(),
                               projectStatus=projectStatus)
    else:
        return redirect(url_for('login'))


@app.route('/deletePage/<id>', methods=['GET'])
def renderDeleteProject(id):
    if 'loggedin' in session:
        logger.info('Redirect To Delete Project Page')
        return render_template('deleteProject.html', data={"id": id})
    else:
        return redirect(url_for('login'))


@app.route('/target-column', methods=['GET', 'POST'])
def setTargetColumn():
    try:
        if 'loggedin' in session and 'id' in session and session['project_type'] != 3 and session[
            'target_column'] is None:
            logger.info('Redirect To Target Column Page')
            df = load_data()
            columns = list(df.columns)
            if request.method == "GET":
                return render_template('target_column.html', columns=columns)
            else:
                status = "error"
                id = session.get('pid')
                target_column = request.form['column']
                rows_count = mysql.delete_record(f'UPDATE tblProjects SET TargetColumn="{target_column}" WHERE Id={id}')
                status = "success"
                # add buttom here
                if status == "success":
                    return render_template('target_column.html', columns=columns)
                else:
                    return redirect('/module')

        else:
            logger.info('Redirect To Home Page')
            return redirect('/')
    except Exception as e:
        logger.error(f'{e}, Occur occurred in target-columns.')
        return render_template('500.html', exception=e)
        # return redirect('/')


@app.route('/deleteProject/<id>', methods=['GET'])
def deleteProject(id):
    if 'loggedin' in session:
        try:
            if id:
                mysql.delete_record(f'UPDATE tblProjects SET IsActive=0 WHERE Pid="{id}"')
                logger.info('Data Successfully Deleted From Database')
                mongodb.drop_collection(id)
                # log.info(log_type='INFO', log_message='Data Successfully Deleted From Database')
                return redirect(url_for('index'))
            else:
                logger.info('Redirect to index invalid id')
                return redirect(url_for('index'))
        except Exception as ex:
            logger.info(str(ex))
            return render_template('500.html', exception=ex)
    else:
        logger.info('Login Needed')
        return redirect(url_for('login'))


"""[summary]
Route for logout
Raises:
    Exception: [description]
Returns:
    [type]: [description]
"""


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('pid', None)
    session.pop('project_name', None)
    session.pop('project_type', None)
    session.pop('target_column', None)
    logger.info('Thanks For Using System!')
    return redirect(url_for('login'))


"""[summary]
Entry Point on Any Project when click on project name
Raises:
    Exception: [description]
Returns:
    [type]: [description]
"""


@app.route('/stream/<pid>')
def stream(pid):
    try:
        data = decrypt(pid)
        if data:
            values = data.split("&")
            session['pid'] = values[1]
            session['project_name'] = values[0]
            query_ = f"Select ProjectType, TargetColumn from tblProjects  where id={session['pid']}"
            project_logger = logger.add(sink=f"./logger/projectlogs/{values[0]}.log",
                                        format="[{time:YYYY-MM-DD HH:mm:ss.SSS} - {level} - {module} ] - {message}",
                                        level="INFO")
            info = mysql.fetch_one(query_)
            if info:
                session['project_type'] = info[0]
                if info[0] != 3:
                    session['target_column'] = info[1]

            mongodb.get_collection_data(values[0])
            return redirect(url_for('module'))
        else:
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)
        return render_template('500.html', exception=e)


@app.route('/module')
def module():
    try:
        if 'pid' in session:
            logger.info(f'Inside {session["project_name"]}')
            return render_template('help.html')
        else:
            logger.info('Redirected to login')
            return redirect(url_for('/'))
    except Exception as e:
        logger.error(e)
        return render_template('500.html', exception=e)


@app.route('/systemlogs/<action>', methods=['GET'])
def systemlogs(action):
    try:
        if action == 'terminal':
            lines = []
            with open(r"logger\logs\logs.log") as file_in:
                for line in file_in:
                    lines.append(line)
            file_in.close()
            return render_template('systemlogs/terminal.html', logs=lines)
        else:
            return 'Not Visible'
    except Exception as e:
        logger.error(f"{e} In System Logs API")
        return render_template('500.html', exception=e)


@app.route('/history/actions', methods=['GET'])
def history():
    try:
        my_collection = mysql.fetch_all(f''' Select Name, Input,Output,ActionDate 
        from tblProject_Actions_Reports 
        Join tblProjectActions on tblProject_Actions_Reports.ProjectActionId=tblProjectActions.Id 
        where ProjectId ="{session['pid']}"''')
        
        data=""
        if len(my_collection)>0:
            df=pd.DataFrame(np.array(my_collection),columns=['Action','Input','Output','DateTime'])
            data=df.to_html()
        return render_template('history/actions.html',status="success", data=data)
    except Exception as e:
        logger.info(e)
        ProjectReports.insert_record_dp(f'Error In History Page :{str(e)}')
        return render_template('history/actions.html',status="error", msg=str(e))
    
    
@app.route('/custom-script', methods=['GET','POST'])
def custom_script():
    try:
        if 'loggedin' in session:
            df = load_data()
            if df is not None:
                logger.info('Redirect To Custom Script')
                ProjectReports.insert_record_fe('Redirect To Custom Script')
                data = df.head(1000).to_html()
                if request.method=='GET':
                    return render_template('custom-script.html',status="success",data=data)
                else:
                    df=load_data()
                    code = request.form['code']
                    
                    ## Double quote is not allowed
                    if '"' in code:
                       return render_template('custom-script.html',status="error", msg="Double quote is not allowed")
        
                    if code is not None:
                        exec(code)
                        update_data(df)
                        ProjectReports.insert_project_action_report(ProjectActions.CUSTOM_SCRIPT.value,code)
                        return redirect('/eda/show')
                    else:
                        return render_template('custom-script.html',status="error", msg="Code snippets is not valid")
            else:
                return redirect(url_for('/'))
        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.info(e)
        ProjectReports.insert_record_fe(f'Error In Custom Script: {str(e)}')
        return render_template('custom-script.html',status="error", msg=str(e))


@app.route('/scheduler/<action>', methods=['GET'])
def scheduler_get(action):
    try:
        df = load_data()
        if 'loggedin' in session:
            if df is not None:
                if action == 'help':
                    return render_template('scheduler/help.html')

                if action == 'Training_scheduler':
                    # To get the trained
                    Model_Trained, model_name,TargetColumn, pid  = mysql.fetch_one(f"""select Model_Trained, Model_Name,TargetColumn, pid  from tblProjects Where Id={session.get('pid')}""")
                    query = f""" select a.pid ProjectId , a.TargetColumn TargetName, 
                                a.Model_Name ModelName, 
                                b.Schedule_date, 
                                b.schedule_time ,
                                a.Model_Trained, 
                                b.train_status ,
                                b.email, 
                                b.deleted
                                from tblProjects as a
                                join tblProject_scheduler as b on a.Pid = b.ProjectId where b.ProjectId = '{pid}'
                                """
                    result = mysql.fetch_one(query)
                    print(result)
                    if Model_Trained == 0:
                        # Create Scheduler
                        if result is None:
                            return render_template('scheduler/add_new_scheduler.html',
                                                action=action,
                                                model_name=model_name,
                                                target=session['target_column'])
                        # Show created scheduler
                        if result is not None:
                            responseData = [{
                                "project_id": pid,
                                "mode_names": model_name,
                                "target_col_name": TargetColumn,
                                "status": result[6],
                                "date": result[3],
                                "time": result[4],
                                "email_send": result[7]
                            }]

                            # From here we have run our scheduler 
                            # after scheduling set 1 in tbl projects 
                            # then set 1 in tbl scheduler
                            return render_template('scheduler/Training_scheduler.html', action=action,
                                                responseData=responseData)

                        else:
                            return "Error in card creation"

                    if Model_Trained == 1:
                        # Retrain for scheduler
                        if result is None:
                            return "You have to Retrain your model to create a scheduler"

                        # Send email
                        if result is not None and result[6] == 1:
                            return "Email Has to be sent here"

                    else:
                        return render_template('scheduler/add_new_scheduler.html', action=action, ALL_MODELS=ALL_MODELS)

                if action == "add_scheduler":
                    return render_template('scheduler/add_new_scheduler.html', action=action, ALL_MODELS=ALL_MODELS, TIMEZONE=TIMEZONE)
                
                if action == 'deleteScheduler':
                    pid  = mysql.fetch_one(f"""select pid from tblProjects Where Id={session.get('pid')}""")
                    query = f'DELETE FROM tblProject_scheduler WHERE ProjectId = "{pid[0]}" '
                    mysql.delete_record(query)
                    print('Scheduled Process deleted')
                    return redirect('/scheduler/Training_scheduler')          
            else:
                return "No data"
        else:
            return redirect(url_for('login'))

    except Exception as e:
        logger.error(f"{e} In scheduler")
        return render_template('500.html', exception=e)


@app.route('/scheduler/<action>', methods=['POST'])
def scheduler_post(action):
    try:
        if 'loggedin' in session:
            Model_Trained, model_name,TargetColumn, pid  = mysql.fetch_one(f"""select Model_Trained, Model_Name,TargetColumn, pid  from tblProjects Where Id={session.get('pid')}""")
            if action == 'help':
                return render_template('scheduler/help.html')

            if action == 'Create_scheduler':
                date = request.form['date']
                time = request.form['time']
                email = request.form['email']

                query = f''' INSERT INTO tblProject_scheduler 
                             (ProjectId,Schedule_date,schedule_time,email,train_status,deleted)
                            values('{pid}','{date}','{time}','{email}' ,0,0) '''
                
                mysql.update_record(query)
                return redirect('/scheduler/Training_scheduler')
        

        else:
            return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"{e} In scheduler")
        return render_template('500.html', exception=e)


if __name__ == '__main__':
    if mysql is None or mongodb is None:
        print("Not Able To connect With Database (Check Mongo and Mysql Connection)")
    else:
        app.run(host="127.0.0.1", port=8000, debug=True)