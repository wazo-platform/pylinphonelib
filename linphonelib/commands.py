# -*- coding: utf-8 -*-

import itertools
import pexpect

from linphonelib.exceptions import ExtensionNotFoundException
from linphonelib.exceptions import LinphoneException


class _BaseCommand(object):

    _successes = []
    _fails = []
    _defaults = [pexpect.EOF, pexpect.TIMEOUT]

    def execute(self, process):
        cmd_string = self._build_command_string()
        process.sendline(cmd_string)
        result = process.expect(self._param_list())
        self._handle_result(result)

    def _param_list(self):
        return list(itertools.chain(self._successes, self._fails, self._defaults))

    def _handle_result(self, result):
        raise NotImplementedError('No result handler on command %s', self.__class__)


class AnswerCommand(_BaseCommand):

    _successes = ['Call \d+ with .* connected.']
    _fails = ['There are no calls to answer.']

    def _handle_result(self, result):
        if result >= len(self._successes):
            print 'throw'
            raise LinphoneException('Failed to answer the call')

    @staticmethod
    def _build_command_string():
        return 'answer'


class CallCommand(_BaseCommand):

    _successes = [
        'Remote ringing.',
        'Call answered by <sip:.*>.',
    ]
    _fails = ['Not Found']

    def __init__(self, exten):
        self._exten = exten

    def __eq__(self, other):
        return self._exten == other._exten

    def _handle_result(self, result):
        if result == 2:
            raise ExtensionNotFoundException('Failed to call %s' % self._exten)
        elif result > len(self._successes):
            raise LinphoneException('Failed to call %s' % self._exten)

    def _build_command_string(self):
        return 'call %s' % self._exten


class RegisterCommand(_BaseCommand):

    _successes = ['Registration on sip:.* successful.']
    _fails = ['Registration on sip:.* failed:.*']

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

    def _handle_result(self, result):
        if result == 1:
            raise LinphoneException('Registration failed')
        elif result == 2:
            raise LinphoneException('Registration returned no result')
        elif result == 3:
            raise LinphoneException('pexpect timeout on registration')

    def _build_command_string(self):
        cmd_string = 'register sip:%(name)s@%(host)s %(host)s %(passwd)s'
        return cmd_string % {'name': self._uname, 'passwd': self._passwd, 'host': self._hostname}


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
            raise LinphoneException('Unregister failed')

    @staticmethod
    def _build_command_string():
        return 'unregister'
