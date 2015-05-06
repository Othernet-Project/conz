"""
Misc utility functions

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import textwrap

COLS = os.getenv('COLUMNS', 79)


def rewrap(s, width=COLS):
    """ Join all lines from input string and wrap it at specified width """
    s = ' '.join([l.strip() for l in s.strip().split('\n')])
    return '\n'.join(textwrap.wrap(s, width))


def rewrap_long(s, width=COLS):
    """ Rewrap longer texts with paragraph breaks (two consecutive LF) """
    paras = s.split('\n\n')
    return '\n\n'.join(rewrap(p) for p in paras)


def striplines(s):
    """ Strip whitespace from each line of input string """
    return '\n'.join([l.strip() for l in s.strip().split('\n')])


def safeint(s):
    """ Convert the string to int without raising errors """
    try:
        return int(s.strip())
    except (TypeError, ValueError):
        return None
