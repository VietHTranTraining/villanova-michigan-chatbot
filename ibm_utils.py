from watson_developer_cloud import DiscoveryV1
from config import DISCOVERY_USERNAME, DISCOVERY_PASSWORD
from env_config import ENV_CONFIG
import json
import os

discovery = DiscoveryV1(
    username = DISCOVERY_USERNAME,
    password = DISCOVERY_PASSWORD,
    version = '2017-11-07'
)

ENV_NAME = 'mm-env'
CONFIG_NAME = 'mm-config'
COLLECTION_NAME = 'mm-collection'
ARTICLES_DIR = './articles'
ENV_ID = None
CONFIG_ID = None
COLLECTION_ID = None

def validate_env():
    if ENV_ID is None:
        return False
    try:
        env_info = discovery.get_environment(ENV_ID)
    except:
        return False
    return True

def validate_config():
    if (ENV_ID is None) or (CONFIG_ID is None):
        return False
    try:
        config_info = discovery.get_configuration(ENV_ID, CONFIG_ID)
    except:
        return False
    return True

def validate_collection():
    if (ENV_ID is None) or (CONFIG_ID is None) or (COLLECTION_NAME is None):
        return False
    try:
        collection_info = discovery.get_collection(ENV_ID, COLLECTION_ID)
    except:
        return False
    return True

def list_envs():
    environments = discovery.list_environments()
    return environments

def list_configs():
    if not validate_env():
        print("list_envs error: Environment ID invalid or not yet set")
        return None
    configs = discovery.list_configurations(ENV_ID)
    return configs 

def list_collections():
    if not validate_env():
        print("list_collections error: Environment ID invalid or not yet set")
        return None 
    elif not validate_config():
        print("list_collections error: Configuration ID invalid or not yet set")
        return None 
    collections = discovery.list_collections(ENV_ID)
    return collections

def delete_env():
    del_env = discovery.delete_environment(ENV_ID)

def delete_config():
    del_config = discovery.delete_configuration(CONFIG_ID)

def delete_collection():
    del_collection = discovery.delete_collection(ENV_ID, COLLECTION_ID)

def get_env():
    global ENV_ID
    envs = list_envs()
    if envs is not None:
        for env in envs['environments']:
            if env["name"] == ENV_NAME:
                ENV_ID = env['environment_id']
                return True
    return False

def get_config():
    global CONFIG_ID
    if not validate_env():
        print("create_config error: Environment ID invalid or not yet set")
        return False
    configs = list_configs()
    if configs is not None:
        for config in configs['configurations']:
            if config["name"] == CONFIG_NAME:
                CONFIG_ID = config['configuration_id']
                return True
    return False

def get_collection():
    global COLLECTION_ID
    if not validate_env():
        print("create_collection error: Environment ID invalid or not yet set")
        return False
    elif not validate_config():
        print("create_collection error: Configuration ID invalid or not yet set")
        return False
    collections = list_collections()
    if collections is not None:
        for collection in collections['collections']:
            if collection["name"] == COLLECTION_NAME:
                COLLECTION_ID = collection['collection_id']
                return True

def create_env():
    global ENV_ID
    if get_env():
        return True
    new_env = None
    try:
        new_env = discovery.create_environment(
            name = ENV_NAME,
            description = "Environment"
        )
    except Exception as ex:
        print str(ex)
        return False
    ENV_ID = new_env['environment_id']
    return True

def create_config():
    global CONFIG_ID
    if get_config():
        return True
    new_config = None
    try:
        new_config = discovery.create_configuration(ENV_ID,  
                ENV_CONFIG['name'], 
                ENV_CONFIG['description'], 
                ENV_CONFIG['workflow']['conversions'], 
                ENV_CONFIG['workflow']['enrichments'], 
                ENV_CONFIG['workflow']['normalizations'])
    except Exception as ex:
        print str(ex)
        return False
    CONFIG_ID = new_config['configuration_id']
    return True

def create_collection():
    global COLLECTION_ID
    if get_collection():
        return True
    new_collection = None
    try:
        new_collection = discovery.create_collection(environment_id = ENV_ID, 
                configuration_id = CONFIG_ID, 
                name = COLLECTION_NAME, 
                description = 'Collection of March Madness 2018 news articles', 
                language = 'en')
    except Exception as ex:
        print str(ex)
        return False
    COLLECTION_ID = new_collection['collection_id']
    return True

def add_doc(file_name):
    if not validate_env():
        print("add_doc error: Environment ID invalid or not yet set")
        return False
    elif not validate_collection():
        print("add_doc error: Collection ID invalid or not yet set")
        return False
    try:
        with open(os.path.join(os.getcwd(), file_name)) as fileinfo:
              add_doc = discovery.add_document(ENV_ID, COLLECTION_ID, file=fileinfo)
              print json.dumps(add_doc, indent = 2)
    except Exception as ex:
        print(str(ex))
        return False
    return True

def add_all_docs():
    print("Adding documents...")
    file_names = [os.path.join(ARTICLES_DIR, fl) 
                  for fl in os.listdir(ARTICLES_DIR) 
                    if os.path.isfile(os.path.join(ARTICLES_DIR, fl))]
    for file_name in file_names:
        if not add_doc(file_name):
            print "Add file " + file_name + " failed"
            return False
    return True

def search(query):
    result = discovery.query(environment_id = ENV_ID,
            collection_id = COLLECTION_ID,
            query = query, count = 20)
    # print(json.dumps(result, indent = 2))
    return result

def startup_discovery():
    if not get_env():
        print("Get environment failed")
    elif not get_config():
        print("Get configuration failed")
    elif not get_collection():
        print("Get collection failed")
    else:
        print("Startup success")

