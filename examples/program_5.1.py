# I hereby disclaim all copyright to the contents of this file,
# program_5.1.py, and place it into the public domain.
#   -- Michael Hobbs


from candygram import *


def start():
    return spawn(loop, 0)


def loop(val):
    r = Receiver()
    r["increment"] = loop, val + 1
    return r()
