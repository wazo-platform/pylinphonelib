# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib import LinphoneException
from linphonelib import NoActiveCallException
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import HangupCommand
from linphonelib.commands import HoldCommand
from linphonelib.commands import HookStatusCommand
from linphonelib.commands import HookStatus
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib.exceptions import ExtensionNotFoundException, \
    CallDeclinedException
from mock import sentinel
from unittest import TestCase


class TestAnswerCommand(TestCase):

    def test_handle_no_active_calls(self):
        c = AnswerCommand()

        self.assertRaises(NoActiveCallException, c.handle_no_call)


class TestCallCommand(TestCase):

    def test_handle_result_not_found(self):
        c = CallCommand(sentinel.exten)

        self.assertRaises(ExtensionNotFoundException,
                          c.handle_not_found)

    def test_build_command_string(self):
        result = CallCommand('1001')._build_command_string()

        assert_that(result, equal_to('call 1001'))

    def test_handle_result_declined(self):
        c = CallCommand(sentinel.exten)

        self.assertRaises(CallDeclinedException,
                          c.handle_call_declined)


class TestHoldCommand(TestCase):

    def test_build_command_string(self):
        result = HoldCommand()._build_command_string()

        assert_that(result, equal_to('pause'))


class TestHangupCommand(TestCase):

    def test_build_command_string(self):
        result = HangupCommand()._build_command_string()

        assert_that(result, equal_to('terminate'))

    def test_handle_result_no_call(self):
        c = HangupCommand()

        self.assertRaises(NoActiveCallException, c.handle_no_active_calls)


class TestHookStatus(TestCase):

    def test_build_command_string(self):
        result = HookStatusCommand()._build_command_string()

        assert_that(result, equal_to('status hook'))

    def test_phone_answered(self):
        c = HookStatusCommand()

        assert_that(c.handle_answered(), equal_to(HookStatus.ANSWERED))

    def test_phone_ringback_tone(self):
        c = HookStatusCommand()

        assert_that(c.handle_ringback_tone(), equal_to(HookStatus.RINGBACK_TONE))

    def test_phone_ringing(self):
        c = HookStatusCommand()

        assert_that(c.handle_ringing(), equal_to(HookStatus.RINGING))

    def test_phone_off_hook(self):
        c = HookStatusCommand()

        assert_that(c.handle_offhook(), equal_to(HookStatus.OFFHOOK))


class TestRegisterCommand(TestCase):

    def setUp(self):
        self._uname = 'name'
        self._passwd = 'secret'
        self._hostname = '127.0.0.1'

    def test_handle_result_failure(self):
        c = RegisterCommand(self._uname, self._passwd, self._hostname)

        self.assertRaises(LinphoneException, c.handle_failure)

    def test_build_command_string(self):
        command_string = RegisterCommand(
            'abc', '5eCr37', '127.0.0.1'
        )._build_command_string()

        assert_that(
            command_string,
            equal_to('register sip:abc@127.0.0.1 127.0.0.1 5eCr37')
        )


class TestUnregisterCommand(TestCase):

    def test_handle_result_not_registered(self):
        c = UnregisterCommand()

        self.assertRaises(LinphoneException, c.handle_not_registered)

    def test_build_command_string(self):
        command = UnregisterCommand()._build_command_string()

        assert_that(command, equal_to('unregister'))
