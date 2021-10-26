from flask import Flask, redirect, url_for, render_template, request, session
import re
from src.utils.databases.mysql_helper import MySqlHelper
from werkzeug.utils import secure_filename
import os
import time
from src.utils.common.common_helper import decrypt, read_config, unique_id_generator,Hashing,encrypt
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
from logger.logger import Logger

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

mysql = MySqlHelper(host, port, user, password, database)
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
            query=f'''
            select tp.Id,tp.Name,tp.Description,tp.Cassandra_Table_Name,ts.Name,ts.Indetifier,tp.Pid
            from tblProjects as tp
            join tblProjectStatus as ts
            on ts.Id=tp.Status
            where tp.UserId={session.get('id')} and tp.IsActive=1
            order by 1 desc;'''
            
            projects = mysql.fetch_all(query)
            project_lists=[]
            
            for project in projects:
                projectid = encrypt(f"{project[6]}&{project[0]}").decode("utf-8")
                project_lists.append(project+(projectid,))
                
            return render_template('index.html',projects=project_lists)
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
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                timestamp = round(time.time() * 1000)
                name=name.replace(" ","_")
                table_name = f"{name}_{timestamp}"
                file = f"src/store/{filename}"
                
                df=pd.read_csv(file)
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
                account = mysql.fetch_one(f'SELECT * FROM tblUsers WHERE Email = "{email}" AND Password = "{Hashing.hash_value(password)}"')
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
                    rowcount = mysql.insert_record(f'INSERT INTO tblUsers (Name, Email, Password, AuthToken) VALUES ("{username}", "{email}", "{hashed_password}", "pankajtest")')
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
            session['project_name']=values[0]
            mongodb.get_collection_data(values[0])
            return redirect(url_for('module'))
        else:
             return redirect(url_for('/'))
    except Exception  as e:
            print(e)
            
@app.route('/module')
def module():
    try:
        if 'pid' in session:
            return render_template('help.html')
        else:
            return redirect(url_for('/'))
    except Exception  as e:
            print(e)
            
@app.route('/eda/<action>')
def eda(action):
    try:
        if 'pid' in session:
            if action=="5point":
                log.info(log_type='ACTION', log_message='Redirect To Eda 5 Point!')
                return render_template('eda/5point.html')
            elif action=="show":
                log.info(log_type='ACTION', log_message='Redirect To Eda Show Dataset!')
                return render_template('eda/showdataset.html')
            else:
                return render_template('eda/help.html')
        else:
            return redirect(url_for('/'))
    except Exception  as e:
            print(e)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
