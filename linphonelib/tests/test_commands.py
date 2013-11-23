# -*- coding: utf-8 -*-

import pexpect

from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib.commands import RegisterCommand
from linphonelib import LinphoneException
from mock import Mock
from mock import sentinel
from unittest import TestCase


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
        self._child.expect.return_value = 0

        self.assertRaises(LinphoneException, c.execute, self._child)

    def test_build_command_string(self):
        command_string = RegisterCommand._build_command_string('abc', '5eCr37', '127.0.0.1')

        assert_that(command_string, equal_to('register sip:abc@127.0.0.1 127.0.0.1 5eCr37'))
