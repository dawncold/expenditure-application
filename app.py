# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import os
import tornado.ioloop
import tornado.web
import jinja2
from tornado_jinja2 import Jinja2Loader
from expenditure_application.main import ApplicationsHandler, ApplicationHandler, ApplicationApprovalHandler, ApplicationRejectionHandler


def make_app():
    template_path = os.path.join(os.path.dirname(__file__), 'expenditure_application/templates')
    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), autoescape=False)
    jinja2_loader = Jinja2Loader(jinja2_env)
    settings = dict(
        template_loader=jinja2_loader,
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        debug=True
    )
    return tornado.web.Application([
        (r'/applications', ApplicationsHandler),
        (r'/applications/(\d+)', ApplicationHandler),
        (r'/applications/(\d+)/approval', ApplicationApprovalHandler),
        (r'/applications/(\d+)/rejection', ApplicationRejectionHandler),
    ], **settings)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
