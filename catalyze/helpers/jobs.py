from __future__ import absolute_import

from catalyze import config

def list(session, env_id, svc_id):
    route = "%s/v1/environments/%s/services/%s/jobs" % (config.paas_host, env_id, svc_id)
    return session.get(route, verify = True)

def retrieve(session, env_id, svc_id, job_id):
    route = "%s/v1/environments/%s/services/%s/jobs/%s" % (config.paas_host, env_id, svc_id, job_id)
    return session.get(route, verify = True)

def retrieve_brrgc_task(session, env_id, svc_id, task_id):
    route = "%s/v1/environments/%s/services/%s/brrgc/task/%s" % (config.paas_host, env_id, svc_id, task_id)
    return session.get(route, verify = True)

def poll_brrgc_task(session, env_id, svc_id, task_id):
    while True:
        task = retrieve_brrgc_task(session, env_id, svc_id, task_id)
        print(task)
        return task

def poll_until_complete(session, env_id, svc_id, job_id):
    while True:
        job = retrieve(session, env_id, svc_id, job_id)
        if job["status"] not in ["scheduled", "queued", "started", "running"]:
            if job["status"] == "finished":
                return job
            else:
                print("\nError - job ended in status '%s'. Check log for details.")
                sys.exit(1)
            break
        sys.stdout.write(".")
        time.sleep(2)
