'''
utility module containing util functions for the project
'''
import os
import json

CFG_FILE = "../../config/cfg.json"

def get_config_info():
    """read configuration info from cfg.json file"""
    local_path = os.path.dirname(__file__)
    config_file = os.path.join(local_path, CFG_FILE)
    data = None
    with open(config_file, 'r', encoding="utf-8") as pfile:
        data = json.load(pfile)

    return data

if __name__ == "__main__":
    print(get_config_info())
