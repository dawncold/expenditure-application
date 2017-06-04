# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import os
import sys
import logging
import tornado.ioloop
import tornado.web
import jinja2
from tornado_jinja2 import Jinja2Loader
from expenditure_application.main import ApplicationsHandler, ApplicationHandler, ApplicationApprovalHandler, \
    ApplicationRejectionHandler, NewApplicationHandler, MailNotificationHandler

LOGGER = logging.getLogger('expenditure_application')
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))


def make_app():
    template_path = os.path.join(os.path.dirname(__file__), 'expenditure_application/templates')
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    settings = dict(
        template_loader=jinja2_loader,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        debug=False
    )
    return tornado.web.Application([
        (r'/', tornado.web.RedirectHandler, dict(url='/applications')),
        (r'/notify', MailNotificationHandler),
        (r'/applications', ApplicationsHandler),
        (r'/applications/new', NewApplicationHandler),
        (r'/applications/(\d+)', ApplicationHandler),
        (r'/applications/(\d+)/approval', ApplicationApprovalHandler),
        (r'/applications/(\d+)/rejection', ApplicationRejectionHandler),
    ], **settings)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888, address='127.0.0.1')
    tornado.ioloop.IOLoop.current().start()
