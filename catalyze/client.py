from __future__ import absolute_import

from catalyze import config, project, output
import requests, json, getpass, os, sys, ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import requests.packages.urllib3.contrib.pyopenssl
requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()

class AuthError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ClientError(Exception):
    def __init__(self, resp):
        message = resp
        if type(resp) is requests.Response:
            try:
                message = resp.json()
            except ValueError:
                message = {"errors": [{"message": resp.text, "code": -1}]}
        Exception.__init__(self, message)

previous_hook = sys.excepthook

def excepthook(exc_type, value, traceback):
    if exc_type in [AuthError, ClientError]:
        if type(value.message) is dict:
            if "errors" in value.message:
                errors = value.message["errors"]
                if len(errors) == 0:
                    output.error("Unknown error")
                else:
                    for error in errors:
                        if "title" in error:
                            output.error("%(title)s (%(description)s)" % error)
                        else:
                            output.error("%(message)s (%(code)d)" % error)
            elif "title" in value.message and "description" in value.message:
                output.error("%(title)s (%(description)s)" % value.message)
            else:
                output.error(value)
        else:
            output.error(value)
    else:
        previous_hook(exc_type, value, traceback)

sys.excepthook = excepthook

def is_ok(resp):
    return resp.status_code >= 200 and resp.status_code < 300

class ForcedTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block = False):
        self.poolmanager = PoolManager(num_pools = connections,
            maxsize = maxsize,
            block = block,
            ssl_version = ssl.PROTOCOL_TLSv1)

class Session:
    def __init__(self, token = None, user_id = None, username = None, password = None):
        self.session = requests.Session()
        self.session.mount("https://", ForcedTLSAdapter())
        self.session.verify = "skip_cert_validation" not in config.behavior
        if token is None:
            self.sign_in(username, password)
        else:
            self.token = token
            self.user_id = user_id

    def _build_headers(self):
        return {
            "X-Api-Key": config.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.token,
            "X-CLI-Version": config.version
        }

    def get(self, url, verify = False):
        resp = self.session.get(url, headers = self._build_headers())
        if verify:
            if is_ok(resp):
                return None if not resp.text else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def post(self, url, body, verify = False):
        resp = self.session.post(url, headers = self._build_headers(), data = json.dumps(body))
        if verify:
            if is_ok(resp):
                return None if not resp.text else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def post_file(self, url, form, verify = False):
        headers = self._build_headers()
        del headers["Content-Type"]
        resp = self.session.post(url, headers = headers, files = form)
        if verify:
            if is_ok(resp):
                return None if not resp.text else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def put(self, url, body, verify = False):
        resp = self.session.put(url, headers = self._build_headers(), data = json.dumps(body))
        if verify:
            if is_ok(resp):
                return None if not resp.text else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def delete(self, url, verify = False):
        resp = self.session.delete(url, headers = self._build_headers())
        if verify:
            if is_ok(resp):
                return None if not resp.text else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def sign_in(self, username, password):
        resp = self.session.post(config.baas_host + "/v2/auth/signin", headers = {
                "X-Api-Key": config.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json"
            }, data = json.dumps({
                "username": username,
                "password": password
            }))
        if is_ok(resp):
            j = resp.json()
            self.token = j["sessionToken"]
            self.user_id = j["usersId"]
        else:
            raise AuthError(resp.json())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

def acquire_session(settings = None):
    if settings is not None and "token" in settings and "user_id" in settings:
        session = Session(token = settings["token"], user_id = settings["user_id"])
        resp = session.get(config.baas_host + "/v2/auth/verify")
        if resp.status_code == 200:
            return session
        elif resp.status_code == 401:
            output.write("Session has timed out. Please re-enter credentials.")
    username = os.getenv("CATALYZE_USERNAME") or config.username
    if username is None:
        username = raw_input("Username: ") if "username" not in config.behavior else config.behavior["username"]
    password = os.getenv("CATALYZE_PASSWORD") or config.password
    if password is None:
        password = getpass.getpass("Password: ")
    session = Session(username = username, password = password)
    if settings is not None:
        settings["token"] = session.token
        settings["user_id"] = session.user_id
        project.save_settings(settings)
    return session
