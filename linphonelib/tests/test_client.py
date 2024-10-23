# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import socket
import unittest
from unittest.mock import Mock, patch

from hamcrest import assert_that, has_properties, instance_of

from ..client import LinphoneClient
from ..exceptions import LinphoneConnectionError


class TestLinphoneClient(unittest.TestCase):
    def setUp(self):
        self.filename = 'socket.sock'
        self.socket = Mock()
        self.client = LinphoneClient(self.filename)
        self.client._sock = self.socket

    @patch('socket.socket')
    def test_when_connect_socket_then_socket_created(self, mock_socket_constructor):
        self.client._sock = None
        self.client.connect()

        mock_socket_constructor.assert_called_once_with(
            socket.AF_UNIX, socket.SOCK_STREAM
        )

    @patch('socket.socket')
    def test_when_connect_twice_then_only_one_socket_is_created(
        self, mock_socket_constructor
    ):
        self.client._sock = None
        self.client.connect()
        self.client.connect()

        mock_socket_constructor.assert_called_once_with(
            socket.AF_UNIX, socket.SOCK_STREAM
        )

    def test_when_send_encoded_data_then_data_sent_to_socket(self):
        raw_data = b'register xyz'

        self.client.send_data(raw_data)

        self.socket.sendall.assert_called_once_with(raw_data)

    def test_when_send_decoded_data_then_data_sent_to_socket(self):
        data = 'register xyz'

        self.client.send_data(data)

        expected_data = data.encode('utf-8')
        self.socket.sendall.assert_called_once_with(expected_data)

    def test_given_not_connected_when_disconnect_then_no_error(self):
        self.client._sock = None
        self.client.disconnect()

    def test_given_connected_when_disconnect_then_socket_closed(self):
        self.client.connect()

        self.client.disconnect()

        self.socket.close.assert_called_once_with()

    def test_given_connected_when_disconnect_twice_then_socket_closed_only_once(self):
        self.client.connect()

        self.client.disconnect()
        self.client.disconnect()

        self.socket.close.assert_called_once_with()

    def test_given_complete_message_when_parse_next_message_then_return_message_queue(
        self,
    ):
        data = b'Status: Ok\nId: 42\n'
        self.socket.recv.return_value = data

        message = self.client.parse_next_status_message()

        assert_that(
            message, has_properties(status='Ok', body={'Status': 'Ok', 'Id': '42'})
        )

    def test_given_remaining_message_when_parse_next_message_then_return_messages_queue(
        self,
    ):
        self.client._buffer = b'Status: '
        self.socket.recv.return_value = b'Ok\nId: 42'

        message = self.client.parse_next_status_message()

        assert_that(message, has_properties(status='Ok'))

    def test_given_non_utf8_message_when_parse_next_message_then_return_str_messages(
        self,
    ):
        self.socket.recv.return_value = b'Status: Ok\ndata: \xE9\n'

        message = self.client.parse_next_status_message()

        assert_that(message.body['data'], instance_of(str))

    def test_given_recv_socket_error_when_parse_next_message_then_raise_amiconnectionerror(
        self,
    ):
        self.socket.recv.side_effect = socket.error

        self.assertRaises(
            LinphoneConnectionError, self.client.parse_next_status_message
        )

    def test_given_socket_recv_nothing_when_parse_next_message_then_raise_amiconnectionerror(
        self,
    ):
        self.socket.recv.return_value = b''

        self.assertRaises(
            LinphoneConnectionError, self.client.parse_next_status_message
        )

    @patch('socket.socket')
    def test_is_server_up_true(self, mock_socket_constructor):
        self.client._sock = None
        socket_instance = mock_socket_constructor.return_value = Mock()
        socket_instance.recv.return_value = b'Status: OK\n'

        result = self.client.is_server_up()

        assert result is True
        mock_socket_constructor.assert_called_once_with(
            socket.AF_UNIX, socket.SOCK_STREAM
        )

    @patch('socket.socket')
    def test_is_server_up_true_already_connected(self, mock_socket_constructor):
        result = self.client.is_server_up()

        assert result is True
        mock_socket_constructor.assert_not_called()

    @patch('socket.socket')
    def test_is_server_up_false_connection_refused(self, mock_socket_constructor):
        self.client._sock = None
        mock_socket_constructor.return_value = socket = Mock()
        socket.connect.side_effect = OSError('connection refused')

        result = self.client.is_server_up()

        assert result is False
