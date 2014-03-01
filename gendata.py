#!/usr/bin/env python
import collections
import gettext
import json
import os
import cPickle as pickle
import subprocess
import sys


Completion = collections.namedtuple('Completion',
        'lang_code lang_name lines_done total_lines words_done total_words')


def completion_info(pofile, lang_info=None):
    '''Given a path to a pofile, return a tuple of:
    (number of strings with translations, total number of strings)
    
    '''
    cmd = "msgattrib  %s --no-obsolete --no-wrap %s | grep '^msgid' | wc"
    translated = subprocess.check_output(cmd % ("--translated", pofile), shell=True)
    untranslated = subprocess.check_output(cmd % ("--untranslated", pofile), shell=True)
    # `wc` returns three values: line count, word count, character count
    # The lines printed by msgattrib are of the form:
    #     msgid "some string"
    # Subtract the line count from the word count so as not to be counting the
    # `msgid` words.
    translated = [int(x) for x in translated.split()]
    translated_lines = translated[0]
    translated_words = translated[1] - translated_lines
    untranslated = [int(x) for x in untranslated.split()]
    untranslated_lines = untranslated[0]
    untranslated_words = untranslated[1] - untranslated_lines
    if lang_info is None:
        lang_info = get_lang_info(pofile)
    return Completion(lang_info['language'], lang_info['display-name-en'],
                      translated_lines, translated_lines + untranslated_lines,
                      translated_words, translated_words + untranslated_words)


def csv_summary(pofile):
    return ",".join(str(x) for x in completion_info(pofile))


def completion_percent(completion):
    return 100.0 * completion.lines_done / completion.total_lines


def get_lang_info(pofile):
    lang_dir = os.path.dirname(os.path.dirname(pofile))
    lang = os.path.basename(lang_dir)
    directory = os.path.dirname(lang_dir)
    print '%s %s' % (directory, lang)
    translator = gettext.translation("r2", directory, [lang])
    return translator.info()


def build_data(datafilename, verbose=False):
    '''Create an r2.data file for a given language. r2.data is JSON formatted
    metadata about the translation, with the display name, english name,
    info on number of translated/untranslated strings, and whether
    or not the language is currently enabled
    
    '''
    prefix = datafilename[:-4]
    pofile = prefix + "po"
    lang_info = get_lang_info(pofile)
    info = completion_info(pofile)
    if verbose:
        print "%s: appears %i%% complete" % (info.lang, completion_percent(info))
    
    en_name = lang_info['display-name-en']
    if not en_name:
        raise ValueError("display-name-en not set for " + info.lang)
    disp_name = lang_info['display-name']
    if not disp_name:
        raise ValueError("display-name not set for " + info.lang)
    
    data = {'en_name': en_name,
            'name': disp_name,
            'num_completed': info.lines_done or 0,
            'num_total': info.total_lines or 1,
            '_is_enabled': lang_info.get("enabled", True),
            }
    with open(datafilename, "w") as datafile:
        json.dump(data, datafile)


if __name__ == '__main__':
    verbose = '-v' in sys.argv
    if '--csv' in sys.argv:
        if '--header' in sys.argv:
            print ','.join(Completion._fields)
        else:
            print csv_summary(sys.argv[-1])
    else:
        build_data(sys.argv[-1], verbose=verbose)
