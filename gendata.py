#!/usr/bin/env python
import gettext
import json
import os
import cPickle as pickle
import subprocess
import sys


def completion_info(pofile):
    '''Given a path to a pofile, return a tuple of:
    (number of strings with translations, total number of strings)
    
    '''
    cmd = "msgattrib  %s --no-obsolete --no-wrap %s | grep '^msgid' | wc -l"
    translated = subprocess.check_output(cmd % ("--translated", pofile), shell=True)
    untranslated = subprocess.check_output(cmd % ("--untranslated", pofile), shell=True)
    translated = int(translated.strip())
    untranslated = int(untranslated.strip())
    return translated, translated + untranslated


def build_data(datafilename):
    '''Create an r2.data file for a given language. r2.data is JSON formatted
    metadata about the translation, with the display name, english name,
    info on number of translated/untranslated strings, and whether
    or not the language is currently enabled
    
    '''
    prefix = datafilename[:-4]
    pofile = prefix + "po"
    lang_dir = os.path.dirname(os.path.dirname(datafilename))
    lang = os.path.basename(lang_dir)
    directory = os.path.dirname(lang_dir)
    translator = gettext.translation("r2", directory, [lang])
    lang_info = translator.info()
    num_completed, num_total = completion_info(pofile)
    completion = float(num_completed) / float(num_total) * 100.0
    print "%s: appears %i%% complete" % (lang, completion)
    
    en_name = lang_info['display-name-en']
    if not en_name:
        raise ValueError("display-name-en not set for " + lang)
    disp_name = lang_info['display-name']
    if not disp_name:
        raise ValueError("display-name not set for " + lang)
    
    data = {'en_name': en_name,
            'name': disp_name,
            'num_completed': num_completed or 0,
            'num_total': num_total or 1,
            '_is_enabled': lang_info.get("enabled", True),
            }
    with open(datafilename, "w") as datafile:
        json.dump(data, datafile)


if __name__ == '__main__':
    build_data(sys.argv[1])
