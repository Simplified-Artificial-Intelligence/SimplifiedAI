import os
from flask import session
import pandas as pd

updated_time=None

def get_filename():
    try:
        project_name=session.get('project_name')
        filename=os.path.join(os.path.join('src','data'),f"{project_name}.csv")
        return filename
        
    except Exception as e:
        print(e)
    finally:
        pass
    
    
def load_data():
    try:
        filename=get_filename()
        df=pd.read_csv(filename)
        return df
        
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
    



