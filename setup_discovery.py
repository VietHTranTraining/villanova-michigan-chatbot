# Only executing this once per project

from ibm_utils import *

if __name__ == "__main__":
    if not create_env():
        print("Create environment failed")
    elif not create_config():
        print("Create configuration failed")
    elif not create_collection():
        print("Create collection failed")
    elif not add_all_docs():
        print("Add documents failed")
    else:
        print("Setup Discovery Service success!")
