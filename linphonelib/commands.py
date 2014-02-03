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


from linphonelib.exceptions import ExtensionNotFoundException
from linphonelib.exceptions import LinphoneException
from linphonelib.exceptions import NoActiveCallException
from linphonelib.base_command import BaseCommand
from linphonelib.base_command import pattern


class AnswerCommand(BaseCommand):

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


class CallCommand(BaseCommand):

    def __init__(self, exten):
        self._exten = exten

    def __eq__(self, other):
        return self._exten == other._exten

    @pattern('Call answered by <sip:.*>.')
    @pattern('Remote ringing.')
    @pattern('Call \d+ to <sip:.*> ringing.')
    def handle_success(self):
        pass

    @pattern('Not Found')
    def handle_not_found(self):
        raise ExtensionNotFoundException('Failed to call %s' % self._exten)

    def _build_command_string(self):
        return 'call %s' % self._exten


class HangupCommand(BaseCommand):

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


class HookStatusCommand(BaseCommand):

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


class RegisterCommand(BaseCommand):

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


class UnregisterCommand(BaseCommand):

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
