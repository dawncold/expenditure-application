# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import sys
import os
import sqlite3
import logging
import contextlib
import config
from decimal import Decimal
from collection import DictObject


LOGGER = logging.getLogger(__name__)


def get_connection():
    def dict_factory(cursor, row):
        d = DictObject()
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    if not os.path.exists(config.DB_FILE_PATH):
        os.mkdir(config.DB_FILE_PATH)
    sqlite3.register_adapter(Decimal, lambda d: int(d))
    conn_ = sqlite3.connect('{}/{}'.format(config.DB_FILE_PATH, config.DB_FILE_NAME))
    conn_.row_factory = dict_factory
    return conn_


def get_cursor(conn):
    return conn.cursor()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('only support one argument')
        exit(-1)
    migration_file = sys.argv[1]
    if not os.path.exists(migration_file):
        print('can not find migration file: {}'.format(migration_file))
        exit(-1)
    with open(migration_file) as f:
        migration_script = f.read()
    LOGGER.debug(migration_script)
    with contextlib.closing(get_connection()) as conn:
        cur = conn.cursor()
        try:
            cur.executescript(migration_script)
        except:
            conn.rollback()
        else:
            conn.commit()
