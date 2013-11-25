# -*- coding: utf-8 -*-

import sys

from linphonelib import Session
from linphonelib import registering


def usage():
    print '''\
Usage:
    python register.py name secret hostname port
'''


def run(uname, secret, hostname, port):
    with registering(Session(uname, secret, hostname, port)) as s:
        print 'registered', s
        s.call('1001')


def main():
    if len(sys.argv) != 5:
        usage()
        return
    run(*sys.argv[1:])

if __name__ == '__main__':
    main()
