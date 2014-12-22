from __future__ import absolute_import

import click
from catalyze import cli, client, git, project
from catalyze.helpers import environments, services

@cli.command(short_help = "Associates a local repository with an environment.")
@click.argument("env_label")
@click.option("--remote", help = "The git remote to be created", default = "catalyze")
def associate(env_label, remote):
    """Associates the git repository in the current directory. This caches the session token and the environment ID, and creates a git remote."""
    session = client.acquire_session()
    for env in environments.list(session):
        if env["data"]["name"] == env_label:
            settings = {
                    "token": session.token,
                    "environmentId": env["environmentId"]
                }
            for svc in services.list(session, env["environmentId"]):
                if svc["data"]["type"] == "code":
                    if remote in git.remote_list():
                        git.remote_remove(remote)
                    git.remote_add(remote, svc["data"]["source"])
                    settings["serviceId"] = svc["serviceId"]
                    project.save_settings(settings)
                    print("\"%s\" remote added." % (remote,))
                    return
            print("No code service found for \"%s\" environment (%s)" % (env_label, env["environmentId"]))
            return
    print("No environment with label \"%s\" found." % (env_label,))

@cli.command()
def disassociate():
    """Remove association with environment."""
    project.clear_settings()
    print("Association cleared.")
