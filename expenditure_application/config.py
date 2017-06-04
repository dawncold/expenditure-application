# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import os
from jinja2 import Environment, FileSystemLoader
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


def generate_supervisord_config():
    home_path = os.getcwd()
    app_path = '{}/expenditure_application'.format(home_path)
    var_path = '{}/var'.format(home_path)
    log_path = '{}/log'.format(var_path)
    etc_path = '{}/etc'.format(home_path)
    if not os.path.exists(etc_path):
        os.mkdir(etc_path)
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    env = Environment(loader=FileSystemLoader(app_path))
    redis_config = env.get_template('redis.conf.j2').render(var_path=var_path, persist=True, log_path=log_path)
    with open('{}/redis.conf'.format(etc_path), mode=b'wb+') as f:
        f.write(redis_config)

    programs = [
        DictObject(name='redis', command='redis-server {}/redis.conf'.format(etc_path)),
        DictObject(name='worker',
                   command='{}/.env/bin/tasktiger -q mail -m expenditure_application.main'.format(home_path)),
        DictObject(name='app', command='{}/.env/bin/python app.py'.format(home_path))
    ]
    config_content = env.get_template('supervisord.conf.j2').render(var_path=var_path,
                                                                    log_path=log_path,
                                                                    home_path=home_path,
                                                                    programs=programs)
    with open('{}/supervisord.conf'.format(etc_path), mode=b'wb+') as f:
        f.write(config_content)

if __name__ == '__main__':
    generate_supervisord_config()
