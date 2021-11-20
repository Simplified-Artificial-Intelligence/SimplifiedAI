import schedule
import time
import pymongo
from src.utils.databases.mysql_helper import MySqlHelper
import pandas as pd
import os
from from_root import from_root


def get_data():
    mysql = MySqlHelper.get_connection_obj()
    query = "SELECT Pid from tblProjects where pid like 'PID%';"
    pid = mysql.fetch_all(query)
    return pid


def delete_data_from_mongo(projectId=None):
    CONNECTION_URL = f"mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    client = pymongo.MongoClient(CONNECTION_URL)
    dataBase = client["Auto-neuron"]
    collection = dataBase[projectId]
    if collection.drop() is None:
        current_data = dataBase.list_collection_names()
        if projectId in current_data:
            return 'Still present inside mongodb'
        else:
            return 'Deleted', dataBase


def upload_checkpoint(projectId=None, data_path=None):
    data = pd.read_csv(data_path)
    check, dataBase = delete_data_from_mongo(projectId)
    if check == 'Deleted':
        collection = dataBase[projectId]
        collection.insert_many(data.to_dict('records'))
        return 'SuccessFully Replaced'
    elif check == 'Still present inside mongodb':
        return 'Still present inside mongodb'
    else:
        print(check)
        return 'unidentified Error'


def get_user_details(projectId=None):
    mysql = MySqlHelper.get_connection_obj()
    query = f"""select Pid,Name,Id,UserId,CreateDate from auto_neuron.tblProjects 
               where UserId = (select UserId from auto_neuron.tblProjects 
               where Pid = '{projectId}' and IsActive = 1)
               """
    result = mysql.fetch_all(query)
    return result


def get_names_from_files(path=None):
    backup_files = []
    normal_files = []
    result = os.listdir(path)
    for i in result[1:]:
        if i.replace('.csv', '').endswith('_backup'):
            backup_files.append(i.replace('.csv', ''))
        else:
            normal_files.append(i.replace('.csv', ''))

    return backup_files, normal_files


def file_path(path=None, backup=None, normal=None):
    backup_data_path = []
    normal_data_path = []

    for i in backup:
        backup_data_path.append(os.path.join(path, i + '.csv'))
    for i in normal:
        normal_data_path.append(os.path.join(path, i + '.csv'))

    return normal_data_path, backup_data_path


def data_updater(path=os.path.join(from_root(),'src','data')):
    backup, normal = get_names_from_files(path)
    normal_data_path, backup_data_path = file_path(path, backup, normal)
    print(normal_data_path)
    print(backup_data_path)

    for pid, data_path in zip(normal, normal_data_path):
        result = upload_checkpoint(pid, data_path)
        print(result)
        if result == 'SuccessFully Replaced':
            os.remove(data_path)
            print('Data removed from Data folder')

    for pid, data_path in zip(backup, backup_data_path):
        os.remove(data_path)
        print('Backup Files Removed')
    

schedule.every(1).minutes.do(data_updater)

while True:
    schedule.run_pending()
    time.sleep(1)
