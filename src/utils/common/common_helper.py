import uuid
import yaml
import hashlib
from cryptography.fernet import Fernet

def read_config(config):
    with open(config) as config:
        content = yaml.safe_load(config)

    return content


def unique_id_generator():
    random = uuid.uuid4()
    unique_id = "PID" + str(random)
    
    return unique_id

class Hashing():     
    @staticmethod   
    def hash_value(value):
        hash_object = hashlib.md5(value.encode('utf-8'))
        return hash_object.hexdigest()
    
    
# we will be encryting the below string.

def encrypt(message ):
    key =b'r7T4WUAHgeAFSwwWVauOdCDsvWugU4xWxlLR1OKayI4='
    fernet = Fernet(key)
    encMessage = fernet.encrypt(message.encode())
    return encMessage

def decrypt(message ):
    key =b'r7T4WUAHgeAFSwwWVauOdCDsvWugU4xWxlLR1OKayI4='
    fernet = Fernet(key)
    encMessage = fernet.decrypt(message.encode())
    return encMessage.decode("utf-8")