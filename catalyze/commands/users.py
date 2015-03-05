from __future__ import absolute_import

import click
from catalyze import cli, client, project, output
from catalyze.helpers import environments

@cli.command(short_help = "Retrieve your user ID")
def whoami():
    """Prompts for login, and prints out your ID so that you can be added to an environment by someone else."""
    session = client.acquire_session()
    output.write("user ID = " + session.user_id)

@cli.command(short_help = "Add a user to the environment")
@click.argument("user_id")
def adduser(user_id):
    """Adds another user to the associated environment. The ID required is found via 'catalyze whoami'."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    environments.add_user(session, settings["environmentId"], user_id)
    output.write("Added.")

@cli.command(short_help = "Remove a user from the environment")
@click.argument("user_id")
def rmuser(user_id):
    """Removes another user from the associated environment. The ID required is found via 'catalyze whoami'."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    environments.remove_user(session, settings["environmentId"], user_id)
    output.write("Removed.")

@cli.command(short_help = "List users for the environment")
def users():
    """Lists users in the associated environment."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    for user in environments.list_users(session, settings["environmentId"])["users"]:
        if user == settings["user_id"]:
            output.write("%s (you)" % (user,))
        else:
            output.write(user)
