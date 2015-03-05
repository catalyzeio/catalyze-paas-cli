from __future__ import absolute_import

from catalyze import cli, client, config, project, output
from catalyze.helpers import services
import click

@cli.command(short_help = "Redeploy without pushing")
def redeploy():
    """Redeploy an environment's service manually."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = settings["serviceId"]
    output.write("Redeploying " + service_id)
    services.redeploy(session, settings["environmentId"], service_id)
    output.write("Redeploy successful, check status and logs for updates")
