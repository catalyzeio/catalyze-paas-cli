from __future__ import absolute_import

import click
from catalyze import cli, client, project
from catalyze.helpers import services

@cli.command()
@click.argument("task_name")
def rake(task_name):
    """Execute a rake task."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    print("Executing Rake Task: {}".format(task_name))
    resp = services.initiate_rake(session, settings["environmentId"], settings["serviceId"], task_name)
    print("Rake task output viewable in the logging server.")
