#!/usr/bin/env python3

from hexy import Hexy

jeff = Hexy() # I've named my Hexy Jeff.  No particular reason, just seemed like a good name.
jeff.connect()
jeff.goto_last_position()
jeff.stop()
jeff.disconnect()
