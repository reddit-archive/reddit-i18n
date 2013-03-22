#!/usr/bin/python
import datetime
import os
import sys
import webbrowser

import requests
import transifex


ENDPOINT = 'http://www.reddit.com'
GIVE = '/api/givetrophy'

TROPHY = 't6_s'
TROPHY_URL = 'https://www.transifex.com/projects/p/reddit'

TROPHY_EVENTS = ('project_resource_translated',)


Event = transifex.Event


def get_secret():
    return os.environ['TROPHYSECRET']


def give_trophy(user, lang, date=None):
    path = ENDPOINT + GIVE
    if date is None:
        date = datetime.date.today()
    description = lang + ' -- ' + date.isoformat()
    data = {'secret': get_secret(),
            'fullname': TROPHY,
            'url': TROPHY_URL,
            'recipient': user,
            'description': description,
            'api_type': 'json'}
    response = requests.post(path, data=data)
    print response
    if not response.ok:
        raise StandardError("Failed to trophy", user, lang, response)


def iter_trophy_events(filename):
    with open(filename) as events:
        # super scary eval. input file should be trusted
        for event in events:
            event = eval(event)
            if event.kind in TROPHY_EVENTS:
                yield event


def do_trophies(filename, open_browser=True):
    seen_users = set()
    for event in iter_trophy_events(filename):
        key = (event.user.lower(), event.lang.lower())
        if key in seen_users:
            continue
        else:
            seen_users.add(key)
        if open_browser:
            webbrowser.open_new_tab('http://www.reddit.com/user/%(user)s' %
                                    event._asdict())
        prompt = ("Give trophy to %(user)s for work on %(lang)s?\n"
                  "See http://www.reddit.com/user/%(user)s\n"
                  "(Last sent translation: %(when)s) [y/n]: " % event._asdict())
        give = raw_input(prompt)
        if give.lower().strip() == 'y':
            give_trophy(event.user, event.lang)
            print "Trophy awarded"
        else:
            print "Skipped!"


def main(args):
    infile = args[1]
    assert infile
    open_browser = '--no-browser' not in args
    do_trophies(args[1], open_browser=open_browser)


if __name__ == '__main__':
    main(sys.argv)

