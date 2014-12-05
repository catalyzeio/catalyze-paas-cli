import subprocess

def remote_list():
    return subprocess.check_output(["git", "remote"]).split("\n")

def remote_add(name, url):
    subprocess.check_call(["git", "remote", "add", name, url])

def remote_remove(name):
    subprocess.check_call(["git", "remote", "remove", name])
