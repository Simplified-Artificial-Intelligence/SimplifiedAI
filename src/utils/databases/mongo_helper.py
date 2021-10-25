import pymongo
import pandas as pd
import time
import argparse
from src.utils.common.common_helper import read_config

config_args = read_config("./config.yaml")


class MongoHelper():
    def __init__(self):
        try:
            path = config_args['secrets']['mongo']
            self.client = pymongo.MongoClient(path)
            self.db = self.client['Auto-neuron']
            print("Mongodb Connection Established")
        except Exception as e:
            print(e)
        
    def create_new_project(self,collection_name,df):
        """[summary]
            Create New Project and Upload data
        Args:
            collection_name ([type]): [description]
            df ([type]): [description]
        """
        try:
            collection=self.db[collection_name]
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
        
    def delete_collection_data(self,collection_name):
        """[summary]
        Delete Collection Data
        Args:
            collection_name ([type]): [description]
        """
        try:
            begin = time.time()
            collection=self.db[collection_name]
            collection.delete_many({})
            end = time.time()  
            print(f"All records deleted. Total time taken: {end - begin} seconds.")
        except Exception as e:
            print(e)
            
    def get_collection_data(self,project_name):
        """[summary]
            Get Collection Data
        Args:
            project_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        try:
            begin = time.time()
            collection=self.db[project_name]
            df = pd.DataFrame(list(collection.find()))
            end = time.time()  
            print(f"All records deleted. Total time taken: {end - begin} seconds.")
            return df
        except Exception as e:
            print(e)
        
        
def outlier_detection(data,kind:str):
    try:
        if kind == 'Box':
            pass
        elif kind == 'Standard devation':
            outliers=[]
            threshold=3
            mean=np.mean(data)
            std=np.std(data)

            for i in data:
                z_score=(i-mean)/std
                if np.abs(z_score)>threshold:
                    outliers.append(i)
            return outliers      

        elif kind == 'IQR':
            outliers=[]
            q1,q3=np.percentile(data,[25,75])
            iqr=q3-q1
            
            lower_bound_value=q1-1.5*iqr
            upper_bound_value=q3+1.5*iqr
            

            for i in data:
                if i<lower_bound_value or i>upper_bound_value:
                    outliers.append(i)
            return outliers
        
    except Exception as e:
        return e