from __future__ import absolute_import

from catalyze import config, project
import requests, json, getpass, os

class AuthError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class ClientError(Exception):
    def __init__(self, resp):
        Exception.__init__(self, "%d: %s" % (resp.status_code, resp.text))

def is_ok(resp):
    return resp.status_code >= 200 and resp.status_code < 300

class Session:
    def __init__(self, token = None, username = None, password = None):
        self.session = requests.Session()
        self.session.verify = "skip_cert_validation" not in config.behavior
        if token is None:
            self.sign_in(username, password)
        else:
            self.token = token

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
                return None if resp.status_code == 204 else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def post(self, url, body, verify = False):
        resp = self.session.post(url, headers = self._build_headers(), data = json.dumps(body))
        if verify:
            if is_ok(resp):
                return None if resp.status_code == 204 else resp.json()
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
                return None if resp.status_code == 204 else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def put(self, url, body, verify = False):
        resp = self.session.put(url, headers = self._build_headers(), data = json.dumps(body))
        if verify:
            if is_ok(resp):
                return None if resp.status_code == 204 else resp.json()
            else:
                raise ClientError(resp)
        else:
            return resp

    def delete(self, url, verify = False):
        resp = self.session.delete(url, headers = self._build_headers())
        if verify:
            if is_ok(resp):
                return None if resp.status_code == 204 else resp.json()
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
        else:
            raise AuthError(resp.json())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

def acquire_session(settings = None):
    if settings is not None and "token" in settings:
        session = Session(token = settings["token"])
        resp = session.get(config.baas_host + "/v2/auth/verify")
        if resp.status_code == 200:
            return session
        elif resp.status_code == 401:
            print("Session has timed out. Please re-enter credentials.")
    username = os.getenv("CATALYZE_USERNAME")
    if username is None:
        username = raw_input("Username: ") if "username" not in config.behavior else config.behavior["username"]
    password = os.getenv("CATALYZE_PASSWORD")
    if password is None:
        password = getpass.getpass("Password: ")
    session = Session(username = username, password = password)
    if settings is not None:
        settings["token"] = session.token
        project.save_settings(settings)
    return session
