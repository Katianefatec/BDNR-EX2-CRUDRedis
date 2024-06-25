import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import redis
from bson.objectid import ObjectId

#Conexão Redis
REDIS_HOST = 'redis-18617.c73.us-east-1-2.ec2.redns.redis-cloud.com'
REDIS_PORT = 18617
REDIS_PASSWORD = '5nw4ieMH6iz6zYrJlrznK85lofLPfhxW'
conR = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

def converter_objectid_para_string(documento):
    if isinstance(documento, ObjectId):
        return str(documento)
    if isinstance(documento, dict):
        return {chave: converter_objectid_para_string(valor) for chave, valor in documento.items()}
    if isinstance(documento, list):
        return [converter_objectid_para_string(item) for item in documento]
    return documento


def set_data(key, data):
    """Armazena dados no Redis."""
    conR.set(key, json.dumps(converter_objectid_para_string(data))) 

def get_data(key):
    """Recupera dados do Redis."""
    data = conR.get(key)
    if data:
        try:
            return json.loads(data.decode('utf-8')) 
        except json.JSONDecodeError:
            return None  
    else:
        return None

def delete_data(key):
    """Exclui dados do Redis."""
    conR.delete(key)
