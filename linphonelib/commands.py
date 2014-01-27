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

import pexpect

from linphonelib.exceptions import CommandTimeoutException
from linphonelib.exceptions import ExtensionNotFoundException
from linphonelib.exceptions import LinphoneException
from linphonelib.exceptions import LinphoneEOFException
from linphonelib.exceptions import NoActiveCallException


def pattern(pattern):
    def decorator(f):
        def decorated(self, *args):
            self._handlers.append((pattern, f))
            return f(self, *args)
        return decorated
    return decorator


class _BaseCommandMeta(type):

    def __new__(meta, name, bases, dct):
        if '_handlers' not in dct:
            dct['_handlers'] = []
        return super(_BaseCommandMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        return super(_BaseCommandMeta, cls).__init__(name, bases, dct)


class _BaseCommand(object):

    __metaclass__ = _BaseCommandMeta

    def execute(self, process):
        cmd_string = self._build_command_string()
        process.sendline(cmd_string)
        try:
            result = process.expect(self._param_list())
        except pexpect.TIMEOUT:
            raise CommandTimeoutException(self.__class__.__name__)
        except pexpect.EOF:
            raise LinphoneEOFException(self.__class__.__name__)
        else:
            self._handle_result(result)

    def _param_list(self):
        return [p[0] for p in self._handlers]
        # return list(itertools.chain(self._successes, self._fails))

    def _handle_result(self, result):
        self._handlers[result]()


class AnswerCommand(_BaseCommand):

    def __eq__(self, other):
        return type(self) == type(other)

    @pattern('Call \d+ with .* connected.')
    def handle_connected(self):
        pass

    @pattern('There are no calls to answer.')
    def handle_no_call(self):
        raise NoActiveCallException()

    @staticmethod
    def _build_command_string():
        return 'answer'


class CallCommand(_BaseCommand):

    def __init__(self, exten):
        self._exten = exten

    def __eq__(self, other):
        return self._exten == other._exten

    @pattern('Call answered by <sip:.*>.')
    @pattern('Remote ringing.')
    def handle_success(self):
        pass

    @pattern('Not Found')
    def handle_not_found(self):
        raise ExtensionNotFoundException('Failed to call %s' % self._exten)

    def _build_command_string(self):
        return 'call %s' % self._exten


class HangupCommand(_BaseCommand):

    def __eq__(self, other):
        return type(self) == type(other)

    def _build_command_string(self):
        return 'terminate'

    @pattern('Call ended')
    def handle_success(self):
        pass

    @pattern('No active calls')
    def handle_no_active_calls(self):
        raise NoActiveCallException()

    @pattern('Could not stop the call with id \d+')
    @pattern('Could not stop the active call.')
    def handle_count_not_stop_the_call(self):
        raise LinphoneException('Hangup failed')


class HookStatus(object):
    OFFHOOK = 0
    RINGING = 1
    ANSWERED = 2


class HookStatusCommand(_BaseCommand):

    def __eq__(self, other):
        return self.__class__ == other.__class__

    @pattern('hook=offhook')
    def handle_offhook(self):
        return HookStatus.OFFHOOK

    @pattern('Incoming call from ".*" <sip:.*>')
    def handle_ringing(self):
        return HookStatus.RINGING

    @pattern('hook=answered duration=\d+ ".*" <sip:.*>')
    def handle_answered(self):
        return HookStatus.ANSWERED

    def _build_command_string(self):
        return 'status hook'


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

    @pattern('Registration on sip:.* successful.')
    def handle_success(self):
        pass

    @pattern('Registration on sip:.* failed:.*')
    def handle_failure(self):
        raise LinphoneException('Registration failed')

    def _build_command_string(self):
        cmd_string = 'register sip:%(name)s@%(host)s %(host)s %(passwd)s'
        return cmd_string % {'name': self._uname,
                             'passwd': self._passwd,
                             'host': self._hostname}


class UnregisterCommand(_BaseCommand):

    def __eq__(self, other):
        return type(other) == type(self)

    @pattern('Unregistration on sip:.* done.')
    def handle_success(self):
        pass

    @pattern('unregistered')
    def handle_not_registered(self):
        raise LinphoneException('Unregister failed')

    def _build_command_string(self):
        return 'unregister'
