# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import unittest
from unittest.mock import Mock

from ..commands import (
    IsRingingShowingCommand,
    IsTalkingToCommand,
    RegisterStatus,
    RegisterStatusCommand,
)
from ..exceptions import LinphoneException

StatusMessage = collections.namedtuple('Message', ['status', 'body'])


class TestRegisterStatusCommand(unittest.TestCase):
    def setUp(self):
        self.command = RegisterStatusCommand()

    def _make_client(self, status, body):
        client = Mock()
        client.parse_next_status_message.return_value = StatusMessage(status, body)
        return client

    def test_registered(self):
        client = self._make_client(
            'Ok', {'Status': 'Ok', 'State': 'LinphoneRegistrationOk'}
        )
        result = self.command.execute(client)
        assert result == RegisterStatus.REGISTERED

    def test_registration_failed(self):
        client = self._make_client(
            'Ok', {'Status': 'Ok', 'State': 'LinphoneRegistrationFailed'}
        )
        result = self.command.execute(client)
        assert result == RegisterStatus.FAIL

    def test_no_registration(self):
        client = self._make_client('Ok', {'Status': 'Ok'})
        result = self.command.execute(client)
        assert result == RegisterStatus.NOT_REGISTERED


class TestIsRingingShowingCommand(unittest.TestCase):
    def setUp(self):
        self.command = IsRingingShowingCommand('Good')

    def _make_client(self, status, body):
        client = Mock()
        client.parse_next_status_message.return_value = StatusMessage(status, body)
        return client

    def test_ringing_showing_caller_id(self):
        client = self._make_client(
            'Ok',
            {
                'Status': 'Ok',
                'State': 'LinphoneCallIncomingReceived',
                'From': '"Good" <sip:0015555555555@example.com>',
            },
        )
        result = self.command.execute(client)
        assert result is True

    def test_no_current_call(self):
        client = self._make_client(
            'Error', {'Status': 'Error', 'Reason': 'No current call available.'}
        )
        result = self.command.execute(client)
        assert result is False

    def test_other_error_still_raises(self):
        client = self._make_client(
            'Error', {'Status': 'Error', 'Reason': 'Something went wrong.'}
        )
        with self.assertRaises(LinphoneException):
            self.command.execute(client)

    def test_ringing_showing_another_caller_id_raises(self):
        client = self._make_client(
            'Ok',
            {
                'Status': 'Ok',
                'State': 'LinphoneCallIncomingReceived',
                'From': '"Bad" <sip:0015555555551@example.com>',
            },
        )
        with self.assertRaises(LinphoneException):
            self.command.execute(client)


class TestIsTalkingToCommand(unittest.TestCase):
    def setUp(self):
        self.command = IsTalkingToCommand('Good')

    def _make_client(self, status, body):
        client = Mock()
        client.parse_next_status_message.return_value = StatusMessage(status, body)
        return client

    def test_talking_to_caller_id(self):
        client = self._make_client(
            'Ok',
            {
                'Status': 'Ok',
                'State': 'LinphoneCallStreamsRunning',
                'From': '"Good" <sip:0015555555555@example.com>',
            },
        )
        result = self.command.execute(client)
        assert result is True

    def test_no_current_call(self):
        client = self._make_client(
            'Error', {'Status': 'Error', 'Reason': 'No current call available.'}
        )
        result = self.command.execute(client)
        assert result is False

    def test_other_error_still_raises(self):
        client = self._make_client(
            'Error', {'Status': 'Error', 'Reason': 'Something went wrong.'}
        )
        with self.assertRaises(LinphoneException):
            self.command.execute(client)
