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

from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib.commands import _BaseCommand
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import HangupCommand
from linphonelib.commands import HookStatusCommand
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib import LinphoneException
from linphonelib import LinphoneEOFException
from linphonelib import CommandTimeoutException
from linphonelib import NoActiveCallException
from mock import Mock
from mock import sentinel
from unittest import TestCase
from linphonelib.exceptions import ExtensionNotFoundException


class TestAnswerCommand(TestCase):

    def test_handle_result_no_call(self):
        c = AnswerCommand()
        result_index = c._param_list().index('There are no calls to answer.')

        self.assertRaises(LinphoneException, c._handle_result, result_index)

    def test_build_command_string(self):
        result = AnswerCommand._build_command_string()

        assert_that(result, equal_to('answer'))


class TestCallCommand(TestCase):

    def test_handle_result_not_found(self):
        c = CallCommand(sentinel.exten)
        result_index = c._param_list().index('Not Found')

        self.assertRaises(ExtensionNotFoundException, c._handle_result, result_index)

    def test_build_command_string(self):
        result = CallCommand('1001')._build_command_string()

        assert_that(result, equal_to('call 1001'))


class TestHangupCommand(TestCase):

    def test_build_command_string(self):
        result = HangupCommand()._build_command_string()

        assert_that(result, equal_to('terminate'))

    def test_handle_result_no_call(self):
        c = HangupCommand()
        result_index = c._param_list().index('No active calls')

        self.assertRaises(NoActiveCallException, c._handle_result, result_index)


class TestHookStatus(TestCase):

    def test_build_command_string(self):
        result = HookStatusCommand()._build_command_string()

        assert_that(result, equal_to('status hook'))

    def test_phone_answered(self):
        c = HookStatusCommand()
        result_index = c._param_list().index('hook=answered duration=\d+ ".*" <sip:.*>')

        hook_status = c._handle_result(result_index)

        assert_that(hook_status, equal_to(c.HookStatus.ANSWERED))

    def test_phone_ringing(self):
        c = HookStatusCommand()
        result_index = c._param_list().index('Incoming call from ".*" <sip:.*>')

        hook_status = c._handle_result(result_index)

        assert_that(hook_status, equal_to(c.HookStatus.RINGING))

    def test_phone_off_hook(self):
        c = HookStatusCommand()
        result_index = c._param_list().index('hook=offhook')

        hook_status = c._handle_result(result_index)

        assert_that(hook_status, equal_to(c.HookStatus.OFFHOOK))


class TestRegisterCommand(TestCase):

    def setUp(self):
        self._uname = 'name'
        self._passwd = 'secret'
        self._hostname = '127.0.0.1'

    def test_handle_result_failure(self):
        c = RegisterCommand(self._uname, self._passwd, self._hostname)
        result_index = c._param_list().index('Registration on sip:.* failed:.*')

        self.assertRaises(LinphoneException, c._handle_result, result_index)

    def test_build_command_string(self):
        command_string = RegisterCommand('abc', '5eCr37', '127.0.0.1')._build_command_string()

        assert_that(command_string, equal_to('register sip:abc@127.0.0.1 127.0.0.1 5eCr37'))


class TestUnregisterCommand(TestCase):

    def test_handle_result_failure(self):
        c = UnregisterCommand()
        result_index = c._param_list().index('unregistered')

        self.assertRaises(LinphoneException, c._handle_result, result_index)

    def test_build_command_string(self):
        command = UnregisterCommand()._build_command_string()

        assert_that(command, equal_to('unregister'))


class TestBaseCommand(TestCase):

    def test_timeout_exception(self):
        mocked_process = Mock()
        mocked_process.expect.side_effect = pexpect.TIMEOUT('')

        c = _BaseCommand()
        c._build_command_string = lambda: ''

        self.assertRaises(CommandTimeoutException, c.execute, mocked_process)

    def test_eof_exception(self):
        mocked_process = Mock()
        mocked_process.expect.side_effect = pexpect.EOF('')

        c = _BaseCommand()
        c._build_command_string = lambda: ''

        self.assertRaises(LinphoneEOFException, c.execute, mocked_process)
