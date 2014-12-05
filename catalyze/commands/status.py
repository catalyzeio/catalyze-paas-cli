from __future__ import absolute_import

import json
from catalyze import cli, client, project
from catalyze.helpers import environments, services

@cli.command()
def status():
    """Check the status of the environment and service."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    env = environments.retrieve(session, settings["environmentId"])
    print("environment state: " + env["state"])
    codes = []
    noncodes = []
    for service in services.list(session, settings["environmentId"]):
        if service["data"]["type"] is not None:
            if service["data"]["type"] == "code":
                codes.append("\t%s (size = %s, build status = %s, deploy status = %s)" % (service["data"]["label"], service["data"]["size"], service["data"]["build_status"], service["data"]["deploy_status"]))
            else:
                noncodes.append("\t%s (size = %s, image = %s, status = %s)" % (service["data"]["label"], service["data"]["size"], service["data"]["name"], service["data"]["deploy_status"]))
        elif service["data"]["name"] == "service_proxy":
            pass
    for item in (codes + noncodes):
        print(item)
