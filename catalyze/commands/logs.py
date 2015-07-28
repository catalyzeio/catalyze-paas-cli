from __future__ import absolute_import

import click
from catalyze import cli, client, project, output
from catalyze.helpers import AESCrypto, services, jobs
import os, os.path
import requests
import tempfile, base64, binascii, shutil

@cli.command("logs", short_help = "Download log files")
@click.argument("database_label")
@click.argument("task_type", help = "Either 'backup' or 'restore' depending on if you're downloading backup/export logs or restore/import logs")
@click.argument("task_id", help = "The ID of the backup, restore, import, or export job")
@click.option("--file", type=click.Path(exists = False), help = "Optionally specifies a file to dump the logs to. Otherwise they will be printed to the console.")
def logs(database_label, task_type, task_id, file):
    """Download and view logs for backup and restore tasks as well as import and export"""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    output.write("Looking up service...")
    service_id = services.get_by_label(session, settings["environmentId"], database_label)

    job = jobs.retrieve(session, settings["environmentId"], service_id, task_id)

    output.write("Retrieving %s logs for task %s ..." % (database_label, task_id))
    url = services.get_temporary_logs_url(session, settings["environmentId"], service_id, task_type, task_id)
    r = requests.get(url, stream=True)
    basename = os.path.basename(file)
    dir = tempfile.mkdtemp()
    tmp_filepath = os.path.join(dir, basename)
    with open(tmp_filepath, 'wb+') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    decryption = AESCrypto.Decryption(tmp_filepath, job["backup"]["key"], job["backup"]["iv"])
    decrypted_basename = os.path.basename(file)
    decrypted_dir = tempfile.mkdtemp()
    decrypted_tmp_filepath = os.path.join(decrypted_dir, decrypted_basename)
    decryption.decrypt(decrypted_tmp_filepath)
    if file is not None:
        shutil.copy(decrypted_tmp_filepath, file)
        output.write("Logs written to %s", (file,))
    else:
        with open(decrypted_tmp_filepath, 'r') as f:
            for line in f:
                output.write(line)
    os.remove(tmp_filepath)
    os.remove(decrypted_tmp_filepath)
