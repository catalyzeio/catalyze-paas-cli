from __future__ import absolute_import

import json, click, sys, tty, termios
from select import select
from ws4py.client.threadedclient import WebSocketClient
from catalyze import cli, client, project, output, config
from catalyze.helpers import services

console_closed = False

@cli.command("console", short_help = "Open a secure console to a service")
@click.argument("service_label")
@click.argument("command", required = False, default = None)
def open_console(service_label, command):
    """
Opens a secure console to a code or database service.

For code services, a command is required. This command is executed as root in the context of the application root directory.

For database services, no command is needed - instead, the appropriate command for the database type is run. For example, for a postgres database, psql is run.
"""
    global console_closed
    settings = project.read_settings()
    session = client.acquire_session(settings)

    service_id = services.get_by_label(session, settings["environmentId"], service_label)

    output.write("Opening console to service '%s'" % (service_id))

    task_id = services.request_console(session, settings["environmentId"], service_id, command)["taskId"]

    output.write("Waiting for the console to be ready... This might take a bit.")

    job_id = services.poll_console_job(session, settings["environmentId"], service_id, task_id)
    creds = services.get_console_tokens(session, settings["environmentId"], service_id, job_id)

    try:
        url = creds["url"].replace("http", "ws")
        token = creds["token"]
        output.write("Connecting...")

        sslopt = {}
        if "skip_cert_validation" in config.behavior:
            sslopt["check_hostname"] = False
        ws = ConsoleClient(url, ssl_options = sslopt, headers = [("X-Console-Token", token)])
        ws.daemon = False
        ws.connect()

        with ContextedConsole() as c:
            while not console_closed:
                data = c.get_data()
                if data:
                    ws.send(data)
    finally:
        output.write("Cleaning up")
        services.destroy_console(session, settings["environmentId"], service_id, job_id)

def emulate_console(ws):
    output.write("I am a test")

class ConsoleClient(WebSocketClient):
    def opened(self):
        output.write("Connection opened")

    def closed(self, code, reason):
        global console_closed
        output.write("Connection closed: %s (%s))" % (reason, str(code)))
        console_closed = True

    def received_message(self, message):
        output.write(message, sameline = True)

class ContextedConsole:
    def __enter__(self):
        self._settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._settings)

    def get_data(self):
        if sys.stdin in select([sys.stdin], [], [], 1)[0]:
            return sys.stdin.read(1)
        return False
