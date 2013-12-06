# -*- coding: utf-8 -*-

import pexpect

from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib import LinphoneException
from mock import Mock
from mock import sentinel
from unittest import TestCase


class TestAnswerCommand(TestCase):

    def setUp(self):
        self._child = Mock(pexpect.spawn)

    def test_execute_success(self):
        c = AnswerCommand()
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 0

        c.execute(self._child)

        self._child.sendline.assert_called_once_with(sentinel.command_string)

    def test_handle_result_no_call(self):
        c = AnswerCommand()
        result_index = c._param_list().index('There are no calls to answer.')

        self.assertRaises(LinphoneException, c._handle_result, result_index)

    def test_build_command_string(self):
        result = AnswerCommand._build_command_string()

        assert_that(result, equal_to('answer'))


class TestCallCommand(TestCase):

    def setUp(self):
        self._child = Mock(pexpect.spawn)

    def test_execute_success(self):
        c = CallCommand(sentinel.exten)
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 0

        c.execute(self._child)

        self._child.sendline.assert_called_once_with(sentinel.command_string)

    def test_execute_failure(self):
        c = CallCommand('1999')
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 2

        self.assertRaises(LinphoneException, c.execute, self._child)

    def test_build_command_string(self):
        result = CallCommand._build_command_string('1001')

        assert_that(result, equal_to('call 1001'))


class TestRegisterCommand(TestCase):

    def setUp(self):
        self._child = Mock(pexpect.spawn)
        self._uname = 'name'
        self._passwd = 'secret'
        self._hostname = '127.0.0.1'

    def test_execute_success(self):
        c = RegisterCommand(self._uname, self._passwd, self._hostname)
        c._build_command_string = Mock(return_value=sentinel.command_string)

        c.execute(self._child)

        self._child.sendline.assert_called_once_with(sentinel.command_string)

    def test_execute_failure(self):
        c = RegisterCommand(self._uname, self._passwd, self._hostname)
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 1

        self.assertRaises(LinphoneException, c.execute, self._child)

    def test_build_command_string(self):
        command_string = RegisterCommand._build_command_string('abc', '5eCr37', '127.0.0.1')

        assert_that(command_string, equal_to('register sip:abc@127.0.0.1 127.0.0.1 5eCr37'))


class TestUnregisterCommand(TestCase):

    def setUp(self):
        self._child = Mock(pexpect.spawn)

    def test_execute_success(self):
        c = UnregisterCommand()
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 0

        c.execute(self._child)

        self._child.sendline.assert_called_once_with(sentinel.command_string)

    def test_execute_failure(self):
        c = UnregisterCommand()
        c._build_command_string = Mock(return_value=sentinel.command_string)
        self._child.expect.return_value = 1

        self.assertRaises(LinphoneException, c.execute, self._child)

    def test_build_command_string(self):
        command = UnregisterCommand._build_command_string()

        assert_that(command, equal_to('unregister'))
