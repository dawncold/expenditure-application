# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import time
import tornado.web
import db


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(list_applications())


def new_application(title, freight, items, comment=None):
    conn = db.get_connection()
    conn.isolation_level = None

    cur = db.get_cursor(conn)
    try:
        subtotal = sum(item['total'] for item in items)
        cur.execute('BEGIN TRANSACTION')
        cur.execute('''
            INSERT INTO expenditure_application(title, subtotal, freight, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (title, subtotal, int(freight), comment, int(time.time())))
        application_id = cur.lastrowid
        values = tuple((application_id, item['title'], item['link'], item['price'], item['quantity'], item['discount'], item['total']) for item in items)
        cur.executemany('''
            INSERT INTO expenditure_application_item(application_id, title, link, price, quantity, discount, total)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ''', values)
    except:
        cur.execute('ROLLBACK')
    else:
        cur.execute('COMMIT')


def list_applications():
    conn = db.get_connection()
    cur = db.get_cursor(conn)
    cur.execute('SELECT * FROM expenditure_application')
    applications = cur.fetchall()
    cur.execute('SELECT * FROM expenditure_application_item')
    application_items = cur.fetchall()
    return dict(applications=applications, application_items=application_items)


if __name__ == '__main__':

    from pprint import pprint
    pprint(list_applications())
