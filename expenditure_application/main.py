# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import os
import jinja2
from tornado_jinja2 import Jinja2Loader
import time
import logging
import contextlib
import httplib
import json
from decimal import Decimal, ROUND_FLOOR
import tornado.web
import tornado.template
from expenditure_application.mail import send_mail
from expenditure_application.queue import queue
from expenditure_application.db import get_connection, get_cursor
from expenditure_application.collection import DictObject, objectify
from expenditure_application.config import DOMAIN
from utils import convert_timestamp_to_utc_datetime, convert_datetime_to_client_timezone, get_current_timestamp

LOGGER = logging.getLogger(__name__)


def get_template(template_file):
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    return jinja2_loader.load(template_file)


@queue.task
def send_application_mail(application_id):
    application = get_application(application_id)
    if not application:
        return
    send_mail('费用申请：{}'.format(application.title), get_template('application-in-mail.html').render(application=application, domain=DOMAIN))


class ApplicationsHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('applications.html', applications=list_applications())

    def post(self, *args, **kwargs):
        application = objectify(json.loads(self.request.body))
        application_id = new_application(application.title, application.freight, application.line_items, comment=application.comment)
        send_application_mail.delay(application_id)
        self.set_status(httplib.CREATED)


class ApplicationHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        application = get_application(application_id)
        if not application:
            self.send_error(404)
        else:
            self.render('application-in-mail.html', application=application, domain=DOMAIN)


class ApplicationApprovalHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        approve_application(application_id, self.get_argument('ps', default=None))
        self.write('Thanks! :)')


class ApplicationRejectionHandler(tornado.web.RequestHandler):
    def get(self, application_id):
        reject_application(application_id, self.get_argument('ps', default=None))
        self.write('Thanks! :(')


class NewApplicationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('new-application.html')


def new_application(title, freight, items, comment=None):
    with contextlib.closing(get_connection()) as conn:
        cur = get_cursor(conn)
        freight = int(freight)
        freight *= 100
        for item in items:
            item.quantity = int(item.quantity)
            item.price = Decimal(item.price)
            item.discount = Decimal(item.discount)
            item.price *= 100
            item.discount *= 100
            item.total = item.price * item.quantity - item.discount
        subtotal = sum(item.total for item in items)
        try:
            cur.execute('''
                INSERT INTO expenditure_application(title, subtotal, freight, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                ''', (title, subtotal, freight, comment, int(time.time())))
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
            return application_id


def list_applications():
    with contextlib.closing(get_connection()) as conn:
        cur = get_cursor(conn)
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
    with contextlib.closing(get_connection()) as conn:
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
        for item in application.line_items:
            item.price = (Decimal(item.price) / 100).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)
            item.discount = (Decimal(item.discount) / 100).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)
            item.total = (Decimal(item.total) / 100).quantize(Decimal('0.01'), rounding=ROUND_FLOOR)


def approve_application(application_id, ps):
    with contextlib.closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute('''
            UPDATE expenditure_application
            SET approved_at=?, ps=?
            WHERE id=? AND approved_at IS NULL AND rejected_at IS NULL
            ''', (get_current_timestamp(), ps, application_id))
        conn.commit()


def reject_application(application_id, ps):
    with contextlib.closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute('''
            UPDATE expenditure_application
            SET rejected_at=?, ps=?
            WHERE id=? AND approved_at IS NULL AND rejected_at IS NULL
            ''', (get_current_timestamp(), ps, application_id))
        conn.commit()

if __name__ == '__main__':

    from pprint import pprint
    new_application('title', 10000, [
        DictObject(title='item-title', link='item-link', price=231000, quantity=1, discount=0, total=231000),
        DictObject(title='item-title2', link='item-link2', price=21000, quantity=2, discount=0, total=42000),
    ])
    pprint(list_applications())
