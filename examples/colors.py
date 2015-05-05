#!/usr/bin/python

import itertools

import conz


cn = conz.Console()

MSG = 'Quick brown fox jumps over the lazy old dog'

FG = ('black', 'red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'white')
BG = FG + (None,)
STYLES = (None, 'bold', 'italic', 'underline', 'blink', 'reverse')

for combo in itertools.product(BG, STYLES, FG):
    bg, style, fg = combo
    if bg == fg:
        # Skip stuff that's the same color for fg/bg because it doesn't make
        # sense
        continue
    s = '{f} with {s} style on {b}'.format(f=fg, b=bg or 'default',
                                           s=style or 'no')
    cn.pstd(cn.color.color(s, color=fg, style=style, bg=bg))
