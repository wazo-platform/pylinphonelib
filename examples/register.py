# -*- coding: utf-8 -*-

import sys

from linphonelib import Session
from linphonelib import LinphoneException


def usage():
    print '''\
Usage:
    python register.py name secret hostname port
'''


def run(uname, secret, hostname, port):
    s = Session(uname, secret, hostname, port)
    try:
        s.register()
    except LinphoneException:
        print 'Failed to register'
        return
    s.unregister()


def main():
    if len(sys.argv) != 5:
        usage()
        return
    run(*sys.argv[1:])

if __name__ == '__main__':
    main()
