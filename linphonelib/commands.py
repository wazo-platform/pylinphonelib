# -*- coding: utf-8 -*-

import linphonelib


class _BaseCommand(object):

    def execute(self, _process):
        raise NotImplementedError('execute')


class RegisterCommand(_BaseCommand):

    def __init__(self, uname, passwd, hostname):
        self._uname = uname
        self._passwd = passwd
        self._hostname = hostname

    def __eq__(self, other):
        return (
            self._uname == other._uname
            and self._passwd == other._passwd
            and self._hostname == other._hostname
        )

    def execute(self, process):
        process.sendline(self._build_command_string())
        success = 'Registration on sip:%s successful.' % self._hostname
        fail = 'Registration on sip:%s failed:' % self._hostname
        result = process.expect([fail, success])
        if result == 0:
            raise linphonelib.LinphoneException('Registration failed')
