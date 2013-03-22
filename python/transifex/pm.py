#!/usr/bin/python
import logging
import os
import sys

import requests 

import transifex

MESSAGE_SEND_PATH = '/messages/compose/'


def post_message(config, session, recipient, subject, message):
    path = config.get('site', 'remote') + MESSAGE_SEND_PATH
    headers =  {'Referer': path}
    csrf = session.cookies['csrftoken']
    params = {'body': message,
              'csrfmiddlewaretoken': csrf,
              'recipient': recipient,
              'send_message': 'Send ',
              'subject': subject}
    logging.info("POSTing to: %s", path)
    logging.info("subject: %(subject)s\nrecipient: %(recipient)s" % params)
    logging.debug("body: %(body)s" % params)

    response = session.post(path, data=params, headers=headers)
    logging.info(response)
    if not response.ok:
        raise StandardError("Something went wrong", response)
    else:
        return response


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    cmd, configpath, user, subject, body = sys.argv
    config = transifex.config_from_filepath(configpath)
    session = transifex.create_transifex_session(config)
    import time; time.sleep(1)
    post_message(config, session, user, subject, body)


if __name__ == '__main__':
    main(sys.argv)
