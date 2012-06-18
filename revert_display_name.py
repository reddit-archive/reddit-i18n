#!/usr/bin/env python
'''Temporary script to revert the "Display-Name" and
"Display-Name-en" metadata that the transifex client
strips out when running "tx pull".

'''
import fileinput
import os
import subprocess
import sys

COMMAND = "git show HEAD:%s | grep -i display-name"
def get_display_name(filename):
    lines = subprocess.check_output(COMMAND % filename, shell=True)
    return lines


def has_display_name(filename):
    with open(filename) as f:
        contents = f.read().lower()
        return '\n"display-name' in contents


def write_display_name_lines(filename, lines):
    written = False
    if has_display_name(filename):
        print "%s already has Display-Name lines" % filename
        return
    for line in fileinput.input(filename, inplace=1, backup=".dn.bak"):
        if not written and line.startswith('"Content-Transfer-Encoding'):
            for l in lines:
                sys.stdout.write(l)
            written = True
        sys.stdout.write(line)


def handle_lang(lang_path, po_file="r2.po"):
    filename = os.path.join(lang_path, po_file)
    lines = get_display_name(filename)
    write_display_name_lines(filename, lines)


if __name__ == "__main__":
    handle_lang(sys.argv[1])
