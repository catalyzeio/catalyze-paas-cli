from __future__ import absolute_import

from catalyze import config

def list(session, env_id, svc_id):
    route = "%s/v1/environments/%s/services/%s/jobs" % (config.paas_host, env_id, svc_id)
    return session.get(route, verify = True)

def retrieve(session, env_id, svc_id, job_id):
    route = "%s/v1/environments/%s/services/%s/jobs/%s" % (config.paas_host, env_id, svc_id, job_id)
    return session.get(route, verify = True)
