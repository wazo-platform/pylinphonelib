# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import unittest
from unittest.mock import Mock

from ..commands import RegisterStatus, RegisterStatusCommand

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
