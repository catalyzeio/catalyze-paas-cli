from __future__ import absolute_import

import sys, os, json
from catalyze import output

FILE_PATH = "./.git/catalyze-config.json"

def read_settings(required = True):
    if os.path.isdir("./.git"):
        if os.path.isfile(FILE_PATH):
            with open(FILE_PATH, 'r') as file:
                return json.load(file)
        else:
            if required:
                output.error("No Catalyze environment associated with this local repo. Run \"catalyze associate\" first.")
            return None
    elif required:
        output.error("No git repo found in the current directory.")
    else:
        return None

def save_settings(settings):
    with open(FILE_PATH, 'w') as file:
        json.dump(settings, file)

def clear_settings():
    if os.path.isdir("./.git"):
        if os.path.isfile(FILE_PATH):
            os.remove(FILE_PATH)
