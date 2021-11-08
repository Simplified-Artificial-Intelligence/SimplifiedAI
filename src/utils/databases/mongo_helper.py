import pymongo
import pandas as pd
import time
from src.utils.common.common_helper import read_config
import os

config_args = read_config(r"C:\Users\pankaj\Desktop\ml\auto neuron\Projectathon\config.yaml")


class MongoHelper:

    def __init__(self):
        try:
            path = config_args['secrets']['mongo']
            self.client = pymongo.MongoClient(path)
            self.db = self.client['Auto-neuron']
            print("Mongodb Connection Established")
        except Exception as e:
            print('Here')
            print(e)
        
    def create_new_project(self, collection_name, df):
        """[summary]
            Create New Project and Upload data
        Args:
            collection_name ([type]): [description]
            df ([type]): [description]
        """
        try:
            collection = self.db[collection_name]
            df.reset_index(inplace=True)
            begin = time.time()
            
            self.delete_collection_data(collection_name)
            rec = collection.insert_many(df.to_dict('records'))
            end = time.time()
            print(f"Your data is uploaded. Total time taken: {end - begin} seconds.")
            
            if rec:
                return len(rec.inserted_ids)
            return 0
        except Exception as e:
            print(e)
        
    def delete_collection_data(self, collection_name):
        """[summary]
        Delete Collection Data
        Args:
            collection_name ([type]): [description]
        """
        try:
            begin = time.time()
            collection = self.db[collection_name]
            collection.delete_many({})
            end = time.time()  
            print(f"All records deleted. Total time taken: {end - begin} seconds.")
        except Exception as e:
            print(e)
            
    def get_collection_data(self, project_name):
        """[summary]
            Get Collection Data
        Args:
            project_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        try:
            path = os.path.join(os.path.join('src', 'data'), f"{project_name}.csv")
            backup_path = os.path.join(os.path.join('src', 'data'), f"{project_name}_backup.csv")
            if os.path.exists(path):
                df = pd.read_csv(path)
                return df
            else:
                begin = time.time()
                collection = self.db[project_name]
                df = pd.DataFrame(list(collection.find()))
                end = time.time()  
                df.to_csv(path)
                df.to_csv(backup_path)
                return df

        except Exception as e:
            print(e)
        
        
