import pymongo
import pandas as pd
import time
from src.utils.common.common_helper import read_config
import os


config_args = read_config("config.yaml")


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

    def download_collection_data(self, project_id, file_type):
        try:
            print(file_type)
            path = os.path.join(os.path.join('src', 'temp_data_store'), f"{project_id}.{file_type}")
            begin = time.time()
            collection = self.db[project_id]
            df = pd.DataFrame(list(collection.find()))
            df.drop(columns='_id')
            end = time.time()
            if file_type == 'csv':
                df.to_csv(path)
            elif file_type == 'tsv':
                df.to_csv(path, sep='\t')
            elif file_type == 'json':
                print(file_type)
                df.to_json(path)
            elif file_type == 'xlsx':
                df.to_excel(path)
            print(f"Downloded {project_id} collection data from database. Total time taken: {end - begin} seconds.")
            download_status = 'Successful'
            return download_status, path

        except Exception as e:
            print(e.__str__())
            download_status = "Unsuccessful"
            return download_status, path

    def drop_collection(self, collection_name):
        """[summary]
        Delete Collection from mongo
        Args:
            collection_name ([type]): [description]
        """
        try:
            begin = time.time()
            collection = self.db[collection_name]
            collection.drop()
            end = time.time()
            print(f"Dropped {collection_name} collection from database. Total time taken: {end - begin} seconds.")
        except Exception as e:
            print(e)