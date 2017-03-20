# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import os
import tornado.ioloop
import tornado.web
from expenditure_application.main import MainHandler


def make_app():
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), 'expenditure_application/templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        debug=True,
        autoescape=None
    )
    return tornado.web.Application([
        (r"/", MainHandler),
    ], **settings)


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
