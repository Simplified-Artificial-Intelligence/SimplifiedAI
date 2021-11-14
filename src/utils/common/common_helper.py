import pickle
import uuid
import yaml
import hashlib
from cryptography.fernet import Fernet
import json
import os
from flask import session
from pickle import dump,load
from from_root import from_root

from src.constants.model_params import Params_Mappings

def read_config(config):
    with open(config) as config:
        content = yaml.safe_load(config)

    return content


def unique_id_generator():
    random = uuid.uuid4()
    unique_id = "PID" + str(random)

    return unique_id


class Hashing:
    @staticmethod
    def hash_value(value):
        hash_object = hashlib.md5(value.encode('utf-8'))
        return hash_object.hexdigest()


# we will be encrypting the below string.
def encrypt(message):
    key = b'r7T4WUAHgeAFSwwWVauOdCDsvWugU4xWxlLR1OKayI4='
    fernet = Fernet(key)
    encMessage = fernet.encrypt(message.encode())
    return encMessage


def decrypt(message):
    key = b'r7T4WUAHgeAFSwwWVauOdCDsvWugU4xWxlLR1OKayI4='
    fernet = Fernet(key)
    encMessage = fernet.decrypt(message.encode())
    return encMessage.decode("utf-8")


def immutable_multi_dict_to_str(immutable_multi_dict,flat=False):
    input_str = immutable_multi_dict.to_dict(flat)
    input_str = { key: value if len(value)>1 else value[0] for key, value in input_str.items() }
    return json.dumps(input_str)

def save_project_encdoing(encoder):
    path=os.path.join(from_root(),'artifacts',session.get('project_name'))
    if not os.path.exists(path):
        os.mkdir(path)
        
    file_name=os.path.join(path,'encoder.pkl')  
    dump(encoder, open(file_name, 'wb'))
    

    
def save_project_scaler(encoder):
    path=os.path.join(from_root(),'artifacts',session.get('project_name'))
    if not os.path.exists(path):
        os.mkdir(path)
        
    file_name=os.path.join(path,'scaler.pkl')  
    dump(encoder, open(file_name, 'wb'))
    
    
def save_project_model(model):
    path=os.path.join(from_root(),'artifacts',session.get('project_name'))
    if not os.path.exists(path):
        os.mkdir(path)
        
    file_name=os.path.join(path,'model_temp.pkl')  
    dump(model, open(file_name, 'wb'))
    
def load_project_model(model):
    path=os.path.join(from_root(),'artifacts',session.get('project_name'),'model_temp.pkl')
    if os.path.exists(path):
        model=pickle.load(path)
        return model
    else:
        None
    
    
def get_param_value(obj,value):
        if obj['dtype']=="boolean":
            return Params_Mappings[value]
        elif obj['dtype']=="string":
            return str(value)
        elif obj['dtype']=="int":
             if obj['accept_none'] and value=="":
                 return None
             else:
                 return int(value)
        elif obj['dtype']=="float":
            if obj['accept_none'] and value=="":
                return None
            else:
                return float(value)   
