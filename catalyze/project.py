from __future__ import absolute_import

import sys, os, json

FILE_PATH = "./.git/catalyze-config.json"

def read_settings(required = True):
    if os.path.isdir("./.git"):
        if os.path.isfile(FILE_PATH):
            with open(FILE_PATH, 'r') as file:
                return json.load(file)
        else:
            if required:
                print("No Catalyze environment associated with this local repo. Run \"catalyze associate\" first.")
                sys.exit(-1)
            return None
    elif required:
        print("No git repo found in the current directory.")
        sys.exit(-1)
    else:
        return None

def save_settings(settings):
    with open(FILE_PATH, 'w') as file:
        json.dump(settings, file)

def clear_settings():
    if os.path.isdir("./.git"):
        if os.path.isfile(FILE_PATH):
            os.remove(FILE_PATH)
