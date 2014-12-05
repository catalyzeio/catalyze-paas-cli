from __future__ import absolute_import

from catalyze import config
import urllib

def list(session, env_id):
    route = "%s/v1/environments/%s/services" % (config.paas_host, env_id)
    return session.get(route, verify = True)

def initiate_rake(session, env_id, svc_id, task_name):
    route = "%s/v1/environments/%s/services/%s/rake/%s" % \
            (config.paas_host, env_id, svc_id, urllib.quote(task_name, "").replace(" ", "%20"),)
    return session.post(route, body, verify = True)

def redeploy(session, env_id, svc_id):
    route = "%s/v1/environments/%s/services/%s/redeploy" % (config.paas_host, env_id, svc_id)
    return session.post(route, {}, verify = True)
