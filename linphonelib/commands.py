# -*- coding: utf-8 -*-

import linphonelib
import pexpect


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
        cmd_string = self._build_command_string(self._uname, self._passwd, self._hostname)
        process.sendline(cmd_string)
        success = 'Registration on sip:%s successful.' % self._hostname
        fail = 'Registration on sip:%s failed:.*' % self._hostname
        result = process.expect([success, fail, pexpect.EOF, pexpect.TIMEOUT])
        if result == 1:
            raise linphonelib.LinphoneException('Registration failed')
        elif result == 2:
            raise linphonelib.LinphoneException('Registration returned no result')
        elif result == 3:
            raise linphonelib.LinphoneException('pexpect timeout on registration')

    @staticmethod
    def _build_command_string(uname, passwd, hostname):
        cmd_string = 'register sip:%(name)s@%(host)s %(host)s %(passwd)s'
        return cmd_string % {'name': uname, 'passwd': passwd, 'host': hostname}


class UnregisterCommand(_BaseCommand):

    def __eq__(self, other):
        return type(other) == type(self)

    def execute(self, process):
        cmd_string = self._build_command_string()
        process.sendline(cmd_string)
        success = 'Unregistration on sip:.* done.'
        fail = 'unregistered'
        result = process.expect([success, fail, pexpect.EOF, pexpect.TIMEOUT])
        if result != 0:
            raise linphonelib.LinphoneException('Unregister failed')

    @staticmethod
    def _build_command_string():
        return 'unregister'
