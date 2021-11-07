import schedule
import time
import pymongo
from src.utils.databases.mysql_helper import MySqlHelper
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd
import os

data = pd.read_csv(r'C:\Users\ketan\Desktop\Project\Projectathon\AMES_Final_DF.csv')


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
        backup_data_path.append(os.path.join(path, i+'.csv'))
    for i in normal:
        normal_data_path.append(os.path.join(path, i+'.csv'))

    return normal_data_path, backup_data_path


def data_updater(path=r"C:\Users\ketan\Desktop\Project\Projectathon\src\data"):
    backup, normal = get_names_from_files(path)
    normal_data_path, backup_data_path = file_path(path, backup, normal)
    print(normal_data_path)
    print(backup_data_path)

    for pid, data_path in zip(backup, backup_data_path):
        print(upload_checkpoint(pid, data_path))


#
# schedule.every(10).seconds.do(upload_to_mongo)
# schedule.every(10).seconds.do(download_from_mongo)
# # Loop so that the scheduling task
# # keeps on running all time.
# while True:
#
# 	# Checks whether a scheduled task
# 	# is pending to run or not
# 	schedule.run_pending()
# 	time.sleep(1)

