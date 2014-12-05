from __future__ import absolute_import

from catalyze import cli, client, config, project

@cli.command()
def redeploy():
    """Redeploy an environment's service manually."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    print("Redeploying")
    services.redeploy(session, settings["environmentId"], settings["serviceId"])
    print("Redeploy successful, check status and logs for updates")
