import pymongo
import pandas as pd
import time
class mongo_helper():
    def __init__(self):
        try:
            self.client =  pymongo.MongoClient("mongodb+srv://vishal:123@auto-neuron.euorq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
            self.db = self.client['Auto-neuron']
            self.collection = self.db['Auto-neuron']
            print("Connection Established")
        except Exception as e:
            print(e)
            
    def push_csv_to_database(self):
        df = pd.read_csv(r"C:\Users\Dell\Desktop\auto-neuron\src\streamlit\data\main_data.csv")
        df.reset_index(inplace=True)
        df_dict = df.to_dict("records")
        begin = time.time()
        self.collection.insert_many(df_dict)
        end = time.time()
        print(f"Your data is uploaded. Total time taken: {end - begin} seconds.")
        

    def delete_file_from_mongo(self):
        begin = time.time()
        self.collection.delete_many({})
        end = time.time()  
        print(f"All records deleted. Total time taken: {end - begin} seconds.")

mh = mongo_helper()
mh.push_csv_to_database()
