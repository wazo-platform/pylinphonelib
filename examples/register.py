# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
