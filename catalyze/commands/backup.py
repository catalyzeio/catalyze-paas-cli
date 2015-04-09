from __future__ import absolute_import

import click, json, time
from catalyze import cli, client, project, output
from catalyze.helpers import services, jobs, tasks
from datetime import datetime

def parse_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")

@cli.group()
def backup():
    """Backup and restore services on demand"""

@backup.command("list", short_help = "List created backups")
@click.argument("service_label")#, help = "The name of the service.")
@click.option("--page", default = 1, help = "The page number to view")
@click.option("--page-size", default = 10, help = "The number of items to show per page")
def exec_list(service_label, page, page_size):
    """List all created backups for the service, sorted from oldest to newest."""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = services.get_by_label(session, settings["environmentId"], service_label)
    raw_backups = services.list_backups(session, settings["environmentId"], service_id, page, page_size)
    backup_list = []
    for id, body in raw_backups.items():
        body["id"] = id
        backup_list.append(body)
    backup_list.sort(lambda a, b: int((parse_date(a["created_at"]) - parse_date(b["created_at"])).total_seconds()))
    if len(backup_list) > 0:
        for item in backup_list:
            output.write("%s %s (status = %s)" % (item["id"], item["created_at"], item["status"]))
        if len(backup_list) == page_size and page == 1:
            output.write("(for older backups, try with --page=2 or adjust --page-size)")
    elif page == 1:
        output.write("No backups created yet for this service.")

@backup.command(short_help = "Create a new backup")
@click.argument("service_label")#, help = "The name of the service.")
@click.option("--skip-poll", is_flag = True, default = False, help = "Just start the backup - don't poll.")
def create(service_label, skip_poll):
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = services.get_by_label(session, settings["environmentId"], service_label)
    task_id = services.create_backup(session, settings["environmentId"], service_id)
    print("Backup started (task ID = %s)" % (task_id,))
    if not skip_poll:
        output.write("Polling until backup finishes.")
        status = tasks.poll_status(session, settings["environmentId"], task_id)
        output.write("\nEnded in status '%s'" % (status,))

@backup.command(short_help = "Restore from a backup")
@click.argument("service_label")#, help = "The name of the service.")
@click.argument("backup_id")#, help = "The ID of the backup to be imported (acquired from 'catalyze backup list')")
@click.option("--skip-poll", is_flag = True, default = False, help = "Just start the restore - don't poll.")
def restore(service_label, backup_id, skip_poll):
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = services.get_by_label(session, settings["environmentId"], service_label)
    task_id = services.restore_backup(session, settings["environmentId"], service_id, backup_id)
    output.write("Restoring (task = %s)" % (task_id,))
    if not skip_poll:
        output.write("Polling until restore is complete.")
        status = tasks.poll_status(session, settings["environmentId"], task_id)
        output.write("\nEnded in status '%s'" % (status,))
