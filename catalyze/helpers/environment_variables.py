from __future__ import absolute_import

from catalyze import config

def list(session, env_id, svc_id):
    route = "%s/v1/services/%s/env" % (config.paas_host, svc_id)
    return session.get(route, verify = True)

def set(session, env_id, svc_id, body):
    route = "%s/v1/services/%s/env" % (config.paas_host, svc_id)
    return session.post(route, body, verify = True)

def unset(session, env_id, svc_id, key):
    route = "%s/v1/services/%s/env/%s" % (config.paas_host, svc_id, key)
    return session.delete(route, verify = True)
