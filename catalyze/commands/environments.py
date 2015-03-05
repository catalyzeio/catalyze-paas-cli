from __future__ import absolute_import

from catalyze import cli, client, config, project, output
from catalyze.helpers import environments

@cli.command("environments", short_help = "List your environments")
def list_environments():
    """Lists all environments to which you have access."""
    settings = project.read_settings(required = False)
    session = client.acquire_session(settings)
    envs = environments.list(session)
    for env in envs:
        output.write("%s: %s (state: %s)" % (env["data"]["name"], env["environmentId"], env["state"]))
    if len(envs) == 0:
        output.write("no environments found")
