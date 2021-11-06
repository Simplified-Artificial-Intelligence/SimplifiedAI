import schedule
import time
import pymongo

def upload_to_mongo(projectId = None):
    if projectId != None:
        DB_NAME = "iNeuron_AI" # Specifiy a Database Name

        # Connection URL
        CONNECTION_URL = f"mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

        # Establish a connection with mongoDB
        client = pymongo.MongoClient(CONNECTION_URL)

        # Create a DB
        dataBase = client[DB_NAME]

        # Create a Collection Name
        COLLECTION_NAME = "iNeuron_Products"
        collection = dataBase[COLLECTION_NAME]

        # Create a List of Records
        list_of_records = [
            {'companyName': 'iNeuron',
             'product': 'Affordable AI',
             'courseOffered': 'Machine Learning with Deployment'},

            {'companyName': 'iNeuron',
             'product': 'Affordable AI',
             'courseOffered': 'Deep Learning for NLP and Computer vision'},

            {'companyName': 'iNeuron',
             'product': 'Master Program',
             'courseOffered': 'Data Science Masters Program'}
        ]

        # insert above records in the collection
        rec = collection.insert_many(list_of_records)
    else:
        return 'Pleas'

def download_from_mongo():
    DB_NAME = "iNeuron_AI"
    # Connection URL
    CONNECTION_URL = f"mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

    # Establish a connection with mongoDB
    client = pymongo.MongoClient(CONNECTION_URL)
    dataBase = client[DB_NAME]
    COLLECTION_NAME = "iNeuron_Products"
    collection = dataBase[COLLECTION_NAME]

    
schedule.every(10).seconds.do(upload_to_mongo)
schedule.every(10).seconds.do(download_from_mongo)
# Loop so that the scheduling task
# keeps on running all time.
while True:

	# Checks whether a scheduled task
	# is pending to run or not
	schedule.run_pending()
	time.sleep(1)