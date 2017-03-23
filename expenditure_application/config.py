# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
from expenditure_application.collection import DictObject

DB_FILE_PATH = 'var'
DB_FILE_NAME = 'core.db'
SECURE_CONFIG_FILE = '.config'
DOMAIN = 'ea.youth2009.org'

secure_config = None


def read_secure_config(config_file_path):
    with open(config_file_path) as f:
        config_lines = f.readlines()

    config = DictObject()
    for line in config_lines:
        line = line.strip()
        if line:
            k, v = line.split('=')
            config[k] = v
    return config

if secure_config is None:
    secure_config = read_secure_config(SECURE_CONFIG_FILE)
