# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, print_function, division
import logging
import requests
from requests.auth import HTTPBasicAuth
from collection import DictObject
from config import secure_config

LOGGER = logging.getLogger(__name__)

MAILGUN_API_BASE_URL = 'https://api.mailgun.net/v3'


def send_mail(subject, html):
    data = DictObject(to=secure_config.mailgun_to, subject=subject, html=html)
    data['from'] = secure_config.mailgun_from
    response = None
    try:
        response = requests.post('{}/{}/messages'.format(MAILGUN_API_BASE_URL, secure_config.mailgun_domain),
                                 auth=HTTPBasicAuth('api', secure_config.mailgun_api_key), data=data)
        response.raise_for_status()
    except Exception:
        LOGGER.exception('Got exception when send mail to {}, {}'.format(data.to, response.content if response else ''))
        raise
    else:
        LOGGER.info(response.content)
        print(response.content)


if __name__ == '__main__':
    send_mail('test', '<h1>nothing</h1>')
