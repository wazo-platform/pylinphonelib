# -*- coding: utf-8 -*-

from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib import LinphoneException
from mock import sentinel
from unittest import TestCase


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

        self.assertRaises(LinphoneException, c._handle_result, result_index)

    def test_build_command_string(self):
        result = CallCommand('1001')._build_command_string()

        assert_that(result, equal_to('call 1001'))


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
