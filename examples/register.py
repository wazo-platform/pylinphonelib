# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from linphonelib import Session, registering


def usage():
    print('Usage:')
    print('    python register.py name secret hostname port')


def run(uname, secret, hostname, port):
    with registering(Session(uname, secret, hostname, port)) as s:
        print('registered', s)
        s.call('1001')


def main():
    if len(sys.argv) != 5:
        usage()
        return
    run(*sys.argv[1:])


if __name__ == '__main__':
    main()
