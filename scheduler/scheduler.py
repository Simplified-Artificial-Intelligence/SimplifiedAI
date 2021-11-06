import schedule
import time
import pymongo
from src.utils.databases.mysql_helper import MySqlHelper
from src.utils.databases.mongo_helper import MongoHelper
import pandas as pd

def get_data():
    mysql = MySqlHelper.get_connection_obj()
    query = "SELECT Pid from tblProjects where pid like 'PID%';"
    pid = mysql.fetch_all(query)
    return pid


def upload_to_mongo(projectId='PIDed6ab563-51a7-408b-9556-9d48f7916836'):

    if projectId is not None:
        #Specifiy a Database Name
        DB_NAME = "iNeuron_AI"

        # Connection URL
        CONNECTION_URL = f"mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

        # Establish a connection with mongoDB
        client = pymongo.MongoClient(CONNECTION_URL)

        # Create a DB
        dataBase = client[DB_NAME]

        # Create a Collection Name
        COLLECTION_NAME = "iNeuron_Products"
        collection = dataBase[COLLECTION_NAME]

        dataBase.drop_collection('PIDed6ab563-51a7-408b-9556-9d48f7916836')
        print('Dropped')
        # Create a List of Records
        data_json = pd.read_csv(r'C:\Users\ketan\Desktop\Project\Projectathon\src\data\PID36db50ef-8ca6-4715-9cb4-1a9224f68c11.csv')
        data_old = pd.read_csv(r'C:\Users\ketan\Desktop\Project\Projectathon\src\data\PID36db50ef-8ca6-4715-9cb4-1a9224f68c11_backup.csv')


    else:
        return 'Pleas'

upload_to_mongo()

def download_from_mongo():
    DB_NAME = "iNeuron_AI"
    # Connection URL
    CONNECTION_URL = f"mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

    # Establish a connection with mongoDB
    client = pymongo.MongoClient(CONNECTION_URL)
    dataBase = client[DB_NAME]
    COLLECTION_NAME = "iNeuron_Products"
    collection = dataBase[COLLECTION_NAME]

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