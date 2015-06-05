from __future__ import absolute_import

import click
from catalyze import cli, client, git, project, output
from catalyze.helpers import environments, services

@cli.command("support-ids", short_help = "Prints out various helpful IDs.")
def support_ids():
    """Prints out various helpful IDs that can be pasted into support tickets."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    del settings["token"]
    for pair in settings.items():
        output.write("%s: %s" % pair)