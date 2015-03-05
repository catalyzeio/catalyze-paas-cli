from __future__ import absolute_import

import click
from catalyze import cli, client, project, output
from catalyze.helpers import services

@cli.command(short_help = "Start a background worker")
@click.argument("target", default = "worker")#, help = "The name of the Procfile target to invoke as a worker.")
def worker(target):
    """Starts a Procfile target as a worker. Worker containers are intended to be short-lived, one-off tasks."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    output.write("Initiating a background worker for Service: %s (procfile target = \"%s\")" % (settings['serviceId'], target))
    services.initiate_worker(session, settings["environmentId"], settings["serviceId"], target)
    output.write("Worker started.")
