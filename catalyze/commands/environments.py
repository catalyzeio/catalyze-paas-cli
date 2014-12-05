from __future__ import absolute_import

from catalyze import cli, client, config, project
from catalyze.helpers import environments

@cli.command("environments")
def list_environments():
    """Lists all environments you own."""
    settings = project.read_settings(required = False)
    session = client.acquire_session(settings)
    envs = environments.list(session)
    for env in envs:
        print("%s: %s (state: %s)" % (env["data"]["name"], env["environmentId"], env["state"]))
    if len(envs) == 0:
        print("no environments found")
