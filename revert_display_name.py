#!/usr/bin/env python
'''Temporary script to revert the "Display-Name" and
"Display-Name-en" metadata that the transifex client
strips out when running "tx pull".

'''
import fileinput
import os
import sys

def read_display_name_lines(filename, backup_suffix=".bak"):
    lines = []
    with open(filename + backup_suffix) as bak:
        for line in bak:
            if line.startswith('"Display-Name'):
                lines.append(line)
            if len(lines) >= 2:
                break
        else:
            raise ValueError("Could not find Display-Name lines "
                             "in: %s" % bak.name)
    return lines


def write_display_name_lines(filename, lines):
    written = False
    for line in fileinput.input(filename, inplace=1, backup=".dn.bak"):
        if not written and line.startswith('"Content-Transfer-Encoding'):
            for l in lines:
                sys.stdout.write(l)
            written = True
        sys.stdout.write(line)


def handle_lang(lang_path, po_file="r2.po"):
    filename = os.path.join(lang_path, po_file)
    lines = read_display_name_lines(filename)
    write_display_name_lines(filename, lines)


if __name__ == "__main__":
    handle_lang(sys.argv[1])
