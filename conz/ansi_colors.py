"""
Class for working with ANSI escape sequences for colorizing

Copyright 2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os
import sys


BORING_PLATFORMS = ['PocketPC', 'win32']


class Color:
    COLORS = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'purple': '35',
        'cyan': '36',
        'white': '37',
    }

    BACKGROUNDS = {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'purple': '45',
        'cyan': '46',
        'white': '47',
    }

    STYLES = {
        'bold': '1',
        'dim': '2',
        'italic': '3',
        'underline': '4',
        'blink': '5',
        'reverse': '7',
    }

    RESET = 0

    def __init__(self):
        isatty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        isplat = sys.platform not in BORING_PLATFORMS
        isenv = os.getenv('ANSI_COLORS_DISABLED') is None
        self.enabled = isatty and isplat and isenv

    def _esc(self, code):
        if not self.enabled:
            return ''
        return '\033[{}m'.format(code)

    def _wrap(self, s, codes=[RESET]):
        codes = ''.join(self._esc(c) for c in codes)
        return '{}{}{}'.format(codes, s, self._esc(self.RESET))

    def color(self, s, color='default', style=None, bg=None):
        codes = []
        fg = self.COLORS[color]
        if style:
            fg += ';' + self.STYLES[style]
        codes.append(fg)
        if bg:
            codes.append(self.BACKGROUNDS[bg])
        return self._wrap(s, codes)

    def black(self, s, style=None, bg=None):
        return self.color(s, 'black', style, bg)

    def red(self, s, style=None, bg=None):
        return self.color(s, 'red', style, bg)

    def green(self, s, style=None, bg=None):
        return self.color(s, 'green', style, bg)

    def yellow(self, s, style=None, bg=None):
        return self.color(s, 'yellow', style, bg)

    def blue(self, s, style=None, bg=None):
        return self.color(s, 'blue', style, bg)

    def purple(self, s, style=None, bg=None):
        return self.color(s, 'purple', style, bg)

    def cyan(self, s, style=None, bg=None):
        return self.color(s, 'cyan', style, bg)

    def white(self, s, style=None, bg=None):
        return self.color(s, 'white', style, bg)


# Singleton, use this
color = Color()
