from __future__ import absolute_import

import sys

def write(*args, **kwargs):
    stream = kwargs["stream"] if "stream" in kwargs else sys.stdout
    stream.write(" ".join([str(v) for v in args]) + ("\n" if "sameline" not in kwargs or not kwargs["sameline"] else ""))
    stream.flush()

def error(message, exit = True, exit_code = -1):
    write("ERROR: " + str(message), stream = sys.stderr)
    if exit:
        sys.exit(exit_code)
