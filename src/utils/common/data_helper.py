import os
from flask import sessions
import pandas as pd

from utils.common.common_helper import decrypt

updated_time=None

def get_filename():
    try:
        project_name=sessions.get('project_name')
        path=os.path.join(os.path.join('src','data'),f"{project_name}.csv")
        filename=os.path.join(path,f"{project_name}.csv")
        return filename
        
    except Exception as e:
        print(e)
    finally:
        pass
    
    
def load_data(datetime=None):
    try:
        filename=get_filename()
        df=pd.read_csv(filename)
        temp_df=df
        return temp_df
        
    except Exception as e:
        print(e)
    finally:
        pass

def update_data(df):
    try:
        filename=get_filename()
        os.remove(filename)
        df.to_csv(filename)
        return df
        
    except Exception as e:
        print(e)
    finally:
        pass
    



