#!/usr/bin/env python3

# based on https://stackoverflow.com/questions/22397289/finding-the-values-of-the-arrow-keys-in-python-why-are-they-triples

# fairly janky and there's probably some prebuilt library to do what I need, but I didn't see it after a couple minutes of searching.

import json
from string import printable
import sys
import termios
import tty

UP='\x1b[A'
DOWN='\x1b[B'
RIGHT='\x1b[C'
LEFT='\x1b[D'
RETURN='\r'
TAB='\t'
UNKNOWN=None
CTRL_C='\u0003'
START_CHARS = [
    '\r',
    '\t',
    '\n',
    '\u001b', # '\x1b'
    '\u0003', # ctrl-c (ctrl-a is \u0001, ctrl-b is \u0002, etc.)
]

KNOWN = [UP,DOWN,LEFT,RIGHT,RETURN,TAB,CTRL_C] + list(printable)

def sprint(*args, **kwargs):
    print(json.dumps(*args, **kwargs))

def _getchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = ''
        while len(ch) < 3:
            nch = sys.stdin.read(1)
            if nch in START_CHARS:
                ch = nch
            else:
                ch += nch
            # sprint(ch)
            if ch in KNOWN:
                return ch
            if ch in printable:
                return ch
            # sprint(ch)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_key():
    k = None
    while(1):
        k = _getchar()
        if k != '':
            break
    if k == CTRL_C:
        raise KeyboardInterrupt()
    return k if k in KNOWN else UNKNOWN
