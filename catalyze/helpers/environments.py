from __future__ import absolute_import

from catalyze import config

def list(session):
    route = "%s/v1/environments" % (config.paas_host,)
    return session.get(route, verify = True)

def retrieve(session, env_id, source = "spec"):
    route = "%s/v1/environments/%s?source=%s" % (config.paas_host, env_id, source)
    return session.get(route, verify = True)
