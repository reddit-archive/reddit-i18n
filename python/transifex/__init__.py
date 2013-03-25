#!/usr/bin/python
from ConfigParser import RawConfigParser as Parser
import logging
import os
import sys

import requests 


SIGNIN_PATH = '/signin/'
USERAGENT = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0; scraping '
             'contributors for reddit trophies; email %(email)s with '
             'concerns) Gecko/20100101 Firefox/16.0')


def config_from_filepath(path):
    config = Parser()
    config.readfp(open(path))
    config.get('credentials', 'user')
    config.get('credentials', 'password')
    config.get('site', 'remote')
    return config


def create_transifex_session(config):
    logger = logging.getLogger('transifex')
    session = requests.Session()
    email = config.get('credentials', 'contactemail')
    session.headers.update({'User-Agent': USERAGENT % {'email': email}})
    signin_path = config.get('site', 'remote') + SIGNIN_PATH
    logging.info("Acquiring csrftoken")
    session.get(signin_path)
    logging.info(getattr(session, "response", "<no response info (requests"
                         " module too old>"))
    csrf = session.cookies['csrftoken']
    login_headers = {'Referer': signin_path}
    login_data = {'identification': config.get('credentials', 'user'),
                  'csrfmiddlewaretoken': csrf,
                  'password': config.get('credentials', 'password'),
                  'remember_me': 'on'}
    logging.info("Acquiring sessionid")
    resp = session.post(signin_path, data=login_data, headers=login_headers)
    logging.info(getattr(session, "response", "<no response info (requests"
                         " module too old>"))
    if not resp.ok or not session.cookies.get('sessionid'):
        raise ValueError("Failed to log in", session, resp)
    return session


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    configpath = sys.argv[1]
    config = config_from_filepath(configpath)
    session = create_transifex_session(config)


if __name__ == '__main__':
    main(sys.argv)
