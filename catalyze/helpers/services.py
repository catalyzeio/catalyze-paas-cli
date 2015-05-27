from __future__ import absolute_import

from catalyze import config, output
from catalyze.client import ClientError, is_ok
import urllib, json, time

def list(session, env_id):
    route = "%s/v1/environments/%s?source=pod" % (config.paas_host, env_id)
    return session.get(route, verify = True)["data"]["services"]

def initiate_rake(session, env_id, svc_id, task_name):
    route = "%s/v1/environments/%s/services/%s/rake/%s" % \
            (config.paas_host, env_id, svc_id, urllib.quote(task_name, "").replace(" ", "%20"),)
    return session.post(route, {}, verify = True)

def redeploy(session, env_id, svc_id):
    route = "%s/v1/environments/%s/services/%s/redeploy" % (config.paas_host, env_id, svc_id)
    return session.post(route, {}, verify = True)

def get_by_label(session, env_id, label):
    for service in list(session, env_id):
        if service["label"] == label:
            return service["id"]
    output.error("Could not find service with label '%s'" % (label,))

def list_backups(session, env_id, svc_id, page_number, page_size):
    route = "%s/v1/environments/%s/services/%s/backup?pageNum=%d&pageSize=%d" % \
            (config.paas_host, env_id, svc_id, int(page_number), int(page_size))
    return session.get(route, verify = True)

def create_backup(session, env_id, svc_id):
    route = "%s/v1/environments/%s/services/%s/backup" % (config.paas_host, env_id, svc_id)
    body = {
        "archiveType": "cf",
        "encryptionType": "aes"
    }
    return session.post(route, body, verify = True)["taskId"]

def restore_backup(session, env_id, svc_id, backup_id):
    route = "%s/v1/environments/%s/services/%s/restore/%s" % (config.paas_host, env_id, svc_id, backup_id)
    body = {
        "archiveType": "cf",
        "encryptionType": "aes"
    }
    return session.post(route, body, verify = True)["taskId"]

def initiate_import(session, env_id, svc_id, file, key, iv, wipe_first, options):
    parameters = {
        "key": key,
        "iv": iv,
        "wipeBeforeImport": wipe_first,
        "options": options
    }
    route = "%s/v1/environments/%s/services/%s/db/import" % (config.paas_host, env_id, svc_id)
    return session.post_file(route, {"file": file, "parameters": ("parameters.json", json.dumps(parameters), "application/json")}, verify = True)

def initiate_worker(session, env_id, svc_id, target):
    route = "%s/v1/environments/%s/services/%s/background" % (config.paas_host, env_id, svc_id)
    return session.post(route, {
        "target": target
    }, verify = True)

def request_console(session, env_id, svc_id, command = None):
    route = "%s/v1/environments/%s/services/%s/console" % (config.paas_host, env_id, svc_id)
    body = {}
    if command is not None:
        body["command"] = command
    resp = session.post(route, body, verify = False)
    if resp.status_code == 404:
        output.error("This hosting environment does not yet support secure console.")
    elif not is_ok(resp):
        raise ClientError(resp)
    else:
        return resp.json()

def console_job_status(session, env_id, svc_id, task_id):
    route = "%s/v1/environments/%s/services/%s/console/status/%s" % (config.paas_host, env_id, svc_id, task_id)
    return session.get(route, verify = True)

def poll_console_job(session, env_id, svc_id, task_id):
    while True:
        resp = console_job_status(session, env_id, svc_id, task_id)
        if resp["jobId"] is not None:
            return resp["jobId"]
        time.sleep(2)
        output.write(".", sameline = True)

def get_console_tokens(session, env_id, svc_id, job_id):
    route = "%s/v1/environments/%s/services/%s/console/token/%s" % (config.paas_host, env_id, svc_id, job_id)
    return session.get(route, verify = True)

def destroy_console(session, env_id, svc_id, job_id):
    route = "%s/v1/environments/%s/services/%s/console/%s" % (config.paas_host, env_id, svc_id, job_id)
    return session.delete(route, verify = True)
