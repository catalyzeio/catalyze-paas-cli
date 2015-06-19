from __future__ import absolute_import

from catalyze import config, output

def metadata(session, pod_id):
    route = "%s/v1/pods/metadata" % (config.paas_host,)
    for pod in session.get(route, verify = True):
        if pod["id"] == pod_id:
            return pod
    output.error("Could not find the pod associated with this environment. Please contact Catalyze support. Please include your environment ID - found via \"catalyze support-ids\"")
