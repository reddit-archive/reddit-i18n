#!/usr/bin/python
import collections
import logging
import os
import sys
import time
import transifex

from BeautifulSoup import BeautifulSoup
import requests 

PROJECT_PATH = 'projects/p/%(project)s'
TIMELINE = 'timeline/'


VERBOSE = True


Event = collections.namedtuple('Event', 'kind lang user when')


def dump_events(config, session, outfile, start_at=1, end_at=None):
    with open(outfile, 'w') as write_to:
        for event in iter_timeline(config, session, start_at=start_at, end_at=end_at):
            write_to.write(repr(event))
            write_to.write('\n')


def get_cookie():
    return {'cookie': os.environ['TXCOOKIE']}


def get_timeline_page(config, session, project='reddit', pagenum=1):
    site = config.get('site', 'remote')
    path = '/'.join([site, PROJECT_PATH, TIMELINE]) % {'project': project}
    params = {'page': pagenum}
    logging.info("Getting: %s?page=%s", path, pagenum)
    response = session.get(path, params=params)
    if response.ok:
        return BeautifulSoup(response.content)
    else:
        raise StandardError('Something went wrong', response)


def iter_timeline(config, session, start_at=1, end_at=None, sleep=2):
    page = start_at
    while True:
        soup = get_timeline_page(config, session, pagenum=page)
        table = soup.find('tbody')
        if not table:
            break
        for item in iter_table(table):
            yield item
        logging.info("Latest item: %r", (item,))
        if end_at is not None and page >= end_at:
            break
        page += 1
        time.sleep(sleep)


def iter_table(table):
    rows = table.findAll('tr')
    for row in rows:
        event = decompose_row(row)
        if event:
            yield event


def decompose_row(row):
    action_type = get_type(row)
    user = get_user(row)
    when = get_when(row)
    lang = get_lang(row)
    return Event(action_type, lang, user, when)


def get_type(row):
    span = row.findAll('td')[0].find('span')
    return _attrs(span)['title']


def get_user(row):
    td = row.findAll('td')[1]
    assert 'timelineuser' in _attrs(td)['class']
    return td.text.strip()


def get_when(row):
    td = row.findAll('td')[2]
    assert 'timelinewhen' in _attrs(td)['class']
    return td.text


def get_lang(row):
    td = row.findAll('td')[3]
    text = td.text.strip()
    if text.startswith('A translation for'):
        text = text.split()
        start = len('A translation for'.split())
        end = text.index('was')
        return u' '.join(text[start:end])
    elif 'submitted a ' in text and ' translation ' in text:
        text = text.partition('submitted a ')[2]
        text = text.partition(' translation')[0]
        return text
    else:
        hrefs = td.findAll('a')
        for href in hrefs:
            if '/language/' in _attrs(href)['href']:
                lang = href.text
                return lang[:-len(' language translation')]
    return None


def _attrs(soup):
    return dict(soup.attrs)


def main(args):
    logging.basicConfig(level=logging.DEBUG)
    configpath = args[1]
    assert args[2] == '--page'
    page = int(args[3])
    outfile = args[4]
    assert outfile
    config = transifex.config_from_filepath(configpath)
    session = transifex.create_transifex_session(config)
    dump_events(config, session, outfile, end_at=page)


if __name__ == '__main__':
    main(sys.argv)

