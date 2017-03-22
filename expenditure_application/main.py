# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import time
import logging
from decimal import Decimal, ROUND_FLOOR
import tornado.web
import db
from collection import DictObject
from utils import convert_timestamp_to_utc_datetime, convert_datetime_to_client_timezone, get_current_timestamp

LOGGER = logging.getLogger(__name__)


class ApplicationsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('applications.html', applications=list_applications())


class ApplicationHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        application = get_application(application_id)
        if not application:
            self.send_error(404)
        else:
            self.render('application.html', application=application)


class ApplicationApprovalHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        approve_application(application_id)
        self.write('Thanks! :)')


class ApplicationRejectionHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        reject_application(application_id)
        self.write('Thanks! :(')


def new_application(title, freight, items, comment=None):
    conn = db.get_connection()
    cur = db.get_cursor(conn)
    subtotal = sum(item.total for item in items)
    for item in items:
        item.total = item.price * item.quantity - item.discount
    try:
        cur.execute('''
            INSERT INTO expenditure_application(title, subtotal, freight, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (title, subtotal, int(freight), comment, int(time.time())))
        application_id = cur.lastrowid
        values = tuple((application_id, item.title, item.link, item.price, item.quantity, item.discount, item.total) for item in items)
        cur.executemany('''
            INSERT INTO expenditure_application_item(application_id, title, link, price, quantity, discount, total)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            ''', values)
    except Exception as e:
        LOGGER.exception('Got exception when create application: {}'.format(e.message))
        conn.rollback()
    else:
        LOGGER.info('Create application successfully!')
        conn.commit()


def list_applications():
    conn = db.get_connection()
    cur = db.get_cursor(conn)
    applications = cur.execute('SELECT * FROM expenditure_application').fetchall()
    application_items = cur.execute('SELECT * FROM expenditure_application_item').fetchall()
    application_id2items = {}
    for item in application_items:
        application_id2items.setdefault(item.application_id, []).append(item)
    for application in applications:
        application.line_items = application_id2items.get(application.id, [])
    normalize_applications(applications)
    return applications


def get_application(application_id):
    conn = db.get_connection()
    cur = conn.cursor()
    application = cur.execute('SELECT * FROM expenditure_application WHERE id=?', (application_id, )).fetchone()
    if application:
        application.line_items = cur.execute('SELECT * FROM expenditure_application_item WHERE application_id=?', (application_id, )).fetchall()
        normalize_applications([application])
    return application


def normalize_applications(applications):
    for application in applications:
        application.subtotal = (Decimal(application.subtotal) / 100).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)
        application.freight = (Decimal(application.freight) / 100).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)
        application.total = application.subtotal + application.freight
        application.created_at = convert_datetime_to_client_timezone(convert_timestamp_to_utc_datetime(application.created_at))
        if application.approved_at:
            application.approved_at = convert_datetime_to_client_timezone(convert_timestamp_to_utc_datetime(application.approved_at))
        if application.rejected_at:
            application.rejected_at = convert_datetime_to_client_timezone(convert_timestamp_to_utc_datetime(application.rejected_at))


def approve_application(application_id):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE expenditure_application SET approved_at=? WHERE id=? AND approved_at IS NULL AND rejected_at IS NULL', (get_current_timestamp(),
                                                                                                                                application_id))
    conn.commit()


def reject_application(application_id):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE expenditure_application SET rejected_at=? WHERE id=? AND approved_at IS NULL AND rejected_at IS NULL', (get_current_timestamp(),
                                                                                                                                application_id))
    conn.commit()

if __name__ == '__main__':

    from pprint import pprint
    new_application('title', 10000, [
        DictObject(title='item-title', link='item-link', price=231000, quantity=1, discount=0, total=231000),
        DictObject(title='item-title2', link='item-link2', price=21000, quantity=2, discount=0, total=42000),
    ])
    pprint(list_applications())
