# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import redis
from tasktiger import TaskTiger
from flask import Flask
from flask_admin import Admin
from tasktiger_admin import TaskTigerView


def run_admin(host, port, db, password, listen_host, listen):
    conn = redis.Redis(host, int(port or 6379), int(db or 0), password)
    tiger = TaskTiger(setup_structlog=True, connection=conn)
    app = Flask(__name__)
    admin = Admin(app, url='/')
    admin.add_view(TaskTigerView(tiger, name='TaskTiger', endpoint='tasktiger'))
    app.run(host=listen_host, port=int(listen or 5000))


if __name__ == '__main__':
    run_admin('127.0.0.1', 6379, 0, None, '127.0.0.1', 5000)
