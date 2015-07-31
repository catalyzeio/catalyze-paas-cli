from __future__ import absolute_import

from catalyze import output
from catalyze.helpers import AESCrypto, services, jobs
import os, os.path, uuid
import requests
import tempfile, shutil


def dump(session, settings, service_label, service_id, task_id, task_type, file):
    """
    Downloads and decrypts the logs for a given job. This job is typically a backup, restore, import, or
    export job. These logs are written to the path :param file: or output to the console if file is None.
    This should be called after every backup, restore, import, or export job.

    :param session: the project settings
    :param settings: the current session
    :param service_label: the human readable name of the service
    :param service_id: the unique identifier of the service
    :param task_id: the ID of the task for which the logs are being retrieved, this **should not** be a job ID
    :param task_type: the type of task for which the logs are being retrieved (`backup` or `restore`)
    :param file: the name of the file to dump the logs to or None for console output
    :return:
    """
    output.write("Retrieving %s logs for task %s ..." % (service_label, task_id))
    # translate the task_id into a job
    job = jobs.retrieve_from_task_id(session, settings["environmentId"], task_id)
    url = services.get_temporary_logs_url(session, settings["environmentId"], service_id, task_type, job["id"])
    r = requests.get(url, stream=True)
    basename = os.path.basename(str(uuid.uuid4()))
    dir = tempfile.mkdtemp()
    tmp_filepath = os.path.join(dir, basename)
    with open(tmp_filepath, 'wb+') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    decryption = AESCrypto.Decryption(tmp_filepath, job[task_type]["key"], job[task_type]["iv"])
    decrypted_tmp_filepath = os.path.join(dir, str(uuid.uuid4()))
    decryption.decrypt(decrypted_tmp_filepath)
    if file is not None:
        shutil.copy(decrypted_tmp_filepath, file)
        output.write("Logs written to %s", (file,))
    else:
        output.write("-------------------------- Begin %s logs --------------------------" % (service_label,))
        with open(decrypted_tmp_filepath, 'r') as f:
            for line in f:
                output.write(line)
        output.write("--------------------------  End %s logs  --------------------------" % (service_label,))
    os.remove(tmp_filepath)
    os.remove(decrypted_tmp_filepath)
    os.removedirs(dir)
