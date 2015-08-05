from __future__ import absolute_import

import click
from catalyze import cli, client, project, output
from catalyze.helpers import AESCrypto, environments, services, tasks, pods, logs
import os, os.path, sys
import requests
from Crypto import Random
from Crypto.Cipher import AES
import tempfile, shutil, base64, binascii, struct

@cli.group("db", short_help = "Interact with database services")
def db():
    """Interact with database services."""

@db.command("import", short_help = "Imports data into a database")
@click.argument("database_label")
@click.argument("filepath", type=click.Path(exists = True))
@click.option("--mongo-collection", default = None, help = "The name of a specific mongo collection to import into. Only applies for mongo imports.")
@click.option("--mongo-database", default = None, help = "The name of the mongo database to import into, if not using the default. Only applies for mongo imports.")
@click.option("--wipe-first", is_flag = True, default = False, help = "If set, empties the database before importing. This should not be used lightly.")
def cmd_import(database_label, filepath, mongo_collection, mongo_database, wipe_first, postgres_database = None, mysql_database = None):
    """Imports a file into a chosen database service.

The import is accomplished by encrypting the file and uploading it to Catalyze. An automated service processes the file according to the passed parameters. The command offers the option to either wait until the processing is finished (and be notified of the end result), or to just kick it off.

The type of file depends on the database. For postgres and mysql, this should be a single SQL script with the extension "sql". For mongo, this should be a tar'd, gzipped archive of the dump that you wish to import, with the extension "tar.gz".

If there is an unexpected error, please contact Catalyze support (support@catalyze.io).
"""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    output.write("Looking up service...")
    service_id = services.get_by_label(session, settings["environmentId"], database_label)

    environment = environments.retrieve(session, settings["environmentId"])
    pod = pods.metadata(session, environment["podId"])
    padding_required = pod["importRequiresLength"]

    output.write("Importing '%s' to %s (%s)" % (filepath, database_label, service_id))
    basename = os.path.basename(filepath)
    dir = tempfile.mkdtemp()
    key = Random.new().read(32)
    iv = Random.new().read(AES.block_size)
    output.write("Encrypting...")
    try:
        enc_filepath = os.path.join(dir, basename)
        with open(filepath, 'rb') as file:
            with open(enc_filepath, 'wb') as tf:
                if padding_required:
                    filesize = os.path.getsize(filepath)
                    output.write("File size = %d" % (filesize,))
                    tf.write(struct.pack("<Q", filesize))
                
                contents = file.read()
                contents += b'\0' * (AES.block_size - len(contents) % AES.block_size)
                cipher = AES.new(key, mode = AES.MODE_CBC, IV = iv)
                tf.write(cipher.encrypt(contents))

        with open(enc_filepath, 'rb') as file:
            options = {}
            if mongo_collection is not None:
                options["mongoCollection"] = mongo_collection
            if mongo_database is not None:
                options["mongoDatabase"] = mongo_database
            if postgres_database is not None:
                options["pgDatabase"] = postgres_database
            if mysql_database is not None:
                options["mysqlDatabase"] = mysql_database

            output.write("Uploading...")
            upload_url = services.get_temporary_upload_url(session, settings["environmentId"], service_id)
            resp = services.initiate_import(session, settings["environmentId"],
                    service_id, upload_url, file,
                    base64.b64encode(binascii.hexlify(key)),
                    base64.b64encode(binascii.hexlify(iv)),
                    wipe_first, options)

            task_id = resp["id"]
            output.write("Processing import... (id = %s)" % (task_id,))
            job = tasks.poll_status(session, settings["environmentId"], task_id, exit_on_error=False)
            output.write("\nImport complete (end status = '%s')" % (job["status"],))
            logs.dump(session, settings, database_label, service_id, task_id, "restore", None)
            if job["status"] != "finished":
                sys.exit(-1)
    finally:
        shutil.rmtree(dir)

@db.command("export", short_help = "Exports data from a database")
@click.argument("database_label")
@click.argument("filepath", type=click.Path(exists=False))
def cmd_export(database_label, filepath):
    """Exports all data from a chosen database service.

The export command is accomplished by first creating a backup of the database. Then requesting a temporary access URL to the encrypted backup file. The file is downloaded, decrypted, and stored at the provided location.

If there is an unexpected error, please contact Catalyze support (support@catalyze.io).
"""
    settings = project.read_settings()
    session = client.acquire_session(settings)
    service_id = services.get_by_label(session, settings["environmentId"], database_label)
    task_id = services.create_backup(session, settings["environmentId"], service_id)
    print("Export started (task ID = %s)" % (task_id,))
    output.write("Polling until export finishes.")
    job = tasks.poll_status(session, settings["environmentId"], task_id, exit_on_error=False)
    if job["status"] != "finished":
        output.write("\nExport finished with illegal status \"%s\", aborting." % (job["status"],))
        logs.dump(session, settings, database_label, service_id, task_id, "backup", None)
        sys.exit(-1)
    output.write("\nEnded in status '%s'" % (job["status"],))
    backup_id = job["id"]
    output.write("Downloading...")
    url = services.get_temporary_url(session, settings["environmentId"], service_id, backup_id)
    r = requests.get(url, stream=True)
    basename = os.path.basename(filepath)
    dir = tempfile.mkdtemp()
    tmp_filepath = os.path.join(dir, basename)
    with open(tmp_filepath, 'wb+') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    output.write("Decrypting...")
    decryption = AESCrypto.Decryption(tmp_filepath, job["backup"]["key"], job["backup"]["iv"])
    decryption.decrypt(filepath)
    os.remove(tmp_filepath)
    output.write("%s exported successfully to %s" % (database_label, filepath))
    logs.dump(session, settings, database_label, service_id, task_id, "backup", None)
