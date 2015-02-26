from __future__ import absolute_import

from catalyze import cli, client, config, project, output
from catalyze.helpers import services

@cli.command()
def redeploy():
    """Redeploy an environment's service manually."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    output.write("Redeploying")
    services.redeploy(session, settings["environmentId"], settings["serviceId"])
    output.write("Redeploy successful, check status and logs for updates")
