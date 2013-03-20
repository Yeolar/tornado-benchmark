#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 2013-03-20.  Copyright (C) Yeolar <yeolar@gmail.com>
#

import os


SETTINGS_FILE = [
    'settings.py',
    os.path.join(os.environ['HOME'], '.torbench_settings.py'),
]

DEFAULT_SETTINGS = '''\
max_clients = 10
multi_processes = 0

log_info_format = 'cost:[%s] code:[%s] url:[%s]'
log_warning_format = 'cost:[%s] code:[%s] url:[%s] error:[%s]'
checker_log_format = 'cost:[%.3f] url:[%s] code:[%d] keyword:[%s] retry:[%d/%d] %s'

url_template = ''
'''

def setup_settings():
    for file in SETTINGS_FILE:
        if os.path.isfile(file):
            return file

    file = SETTINGS_FILE[-1]
    with open(file, 'w') as f:
        f.write(DEFAULT_SETTINGS)
    return file

