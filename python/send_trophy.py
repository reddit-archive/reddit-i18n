#!/usr/bin/python
import datetime
import logging
import sqlite3
import sys
import time

try:
    from r2.models import admintools
except ImportError:
    print >> sys.stderr, "Unable to import admintools"

import transifex
import transifex.history
import transifex.pm


TROPHY_EVENTS = ('project_resource_translated',)
TABLES = {'messages': '(user text, lang_uid text, date text)'}


def uid_from_lang(lang):
    # This intentionally chokes if lang is None.
    # lang of None is an indicator that transifex.history isn't
    # properly figuring out the languages from the timeline HTML
    return lang.replace(" ", "_").replace("(", "").replace(")", "").lower()


def iter_trophy_events(filename):
    # Put "Event" in the local namespace so the scary eval() works
    Event = transifex.history.Event
    with open(filename) as events:
        # super scary eval. input file should be trusted
        for event in events:
            event = eval(event)
            if event.kind in TROPHY_EVENTS:
                yield event


def get_cursor(config):
    db_path = config.get('local', 'db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    # TABLES is a trusted source
    for table in TABLES:
        try:
            cursor.execute('select count(*) from ' + table)
        except sqlite3.OperationalError:
            cursor.execute('create table ' + table + ' ' + TABLES[table])
    return cursor


SEEN_SQL = "SELECT * from messages WHERE user = ? AND lang_uid = ?"
INSERT_SQL = "INSERT INTO messages VALUES (?, ?, ?)"
def seen(cursor, user, lang_uid, date_txt):
    existing = cursor.execute(SEEN_SQL, (user, lang_uid)).fetchall()
    if not existing:
        cursor.execute(INSERT_SQL, (user, lang_uid, date_txt))
    return existing


def do_trophies(cursor, config, tx_session, filename):
    # Ensure that admintools import succeeded
    assert admintools
    project = config.get('site', 'project')
    trophy_url = config.get('site', 'remote') + '/projects/p/' + project
    for event in iter_trophy_events(filename):
        logging.info("Checking event %s", (event,))
        date_txt = datetime.date.today().isoformat()
        lang_uid = uid_from_lang(event.lang)
        if seen(cursor, event.user, lang_uid, date_txt):
            logging.info("User %s already has been sent trophy PM for %s",
                         event.user, lang_uid)
            continue
        logging.info("Sending Transifex PM with trophy link")
        description = '%s -- %s' % (event.lang, date_txt)
        claim_url = admintools.create_award_claim_code(lang_uid, 'i18n',
                                                       description, trophy_url)
        fmt_info = {'user': event.user, 'lang': event.lang, 'url': claim_url}
        subject = config.get('award', 'subject') % fmt_info
        body = config.get('award', 'message') % fmt_info

        transifex.pm.post_message(config, tx_session, event.user, subject,
                                  body)
        time.sleep(0.5)


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    config = transifex.config_from_filepath(args[1])
    infile = args[2]
    cursor = get_cursor(config)
    tx_session = transifex.create_transifex_session(config)
    do_trophies(cursor, config, tx_session, infile)


if __name__ == '__main__':
    main(sys.argv)

