from __future__ import absolute_import

from catalyze import config, output

def list(session):
    route = "%s/v1/environments?pageSize=1000" % (config.paas_host,)
    return session.get(route, verify = True)

def retrieve(session, env_id, source = "spec"):
    route = "%s/v1/environments/%s?source=%s" % (config.paas_host, env_id, source)
    return session.get(route, verify = True)

def list_users(session, env_id):
    route = "%s/v1/environments/%s/users" % (config.paas_host, env_id)
    return session.get(route, verify = True)

def add_user(session, env_id, user_id):
    route = "%s/v1/environments/%s/users/%s" % (config.paas_host, env_id, user_id)
    return session.post(route, {}, verify = True)

def remove_user(session, env_id, user_id):
    route = "%s/v1/environments/%s/users/%s" % (config.paas_host, env_id, user_id)
    return session.delete(route, verify = True)
