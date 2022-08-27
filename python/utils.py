#!/usr/bin/env python3

import os
import base64
from datetime import datetime
import subprocess

def db64(s):
    if len(s) % 4 != 0:
        s += "=" * (4 - (len(s) % 4))
    if '_' in s or '-' in s:
        s = base64.urlsafe_b64decode(s)
    else:
        s = base64.b64decode(s)
    return s.decode()


def get_temp_filename():
    random_bytes = os.urandom(5)
    random_str = base64.b32encode(random_bytes).decode()
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    return date_str + "_" + random_str


def get_log_tail(logfile_path, lines=1024):
    s = subprocess.check_output(['tail', '-n', str(lines), logfile_path])
    log_tail = s.decode()
    return log_tail.strip()


if __name__ == "__main__":
    for i in range(100):
        print(get_temp_filename())
