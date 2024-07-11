# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import collections
import socket

from . import parser
from .exceptions import LinphoneConnectionError

DEFAULT_TIMEOUT = 10
StatusMessage = collections.namedtuple('Message', ['status', 'body'])


class LinphoneClient:
    _BUFSIZE = 4096

    def __init__(self, filename, logfile=None):
        self._filename = filename
        self._logfile = logfile
        self._sock = None
        self._buffer = b''
        self._status_queue = collections.deque()

    def _log_write(self, message):
        if self._logfile:
            self._logfile.write(message)

    def connect(self):
        if self._sock is None:
            self._log_write(f'Connecting Linphone client to {self._filename}')
            self._connect_socket()

    def disconnect(self):
        if self._sock is not None:
            self._log_write('Disconnecting Linphone client')
            self._disconnect_socket()

    def is_server_up(self):
        if self._sock is not None:
            return True

        try:
            self._log_write('Probing Linphone server')
            self._connect_socket()
            return True
        except LinphoneConnectionError:
            return False
        finally:
            self._disconnect_socket()

    def parse_next_status_message(self):
        while not self._status_queue:
            self._add_data_to_buffer()
            self._parse_buffer()
        return self._pop_message()

    def _parser_status_callback(self, status, message_body):
        message = StatusMessage(status, message_body)
        self._status_queue.append(message)

    def _connect_socket(self):
        try:
            self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._sock.settimeout(DEFAULT_TIMEOUT)
            self._sock.connect(self._filename)
        except OSError as e:
            raise LinphoneConnectionError(e)

    def _disconnect_socket(self):
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()
        self._sock = None
        self._buffer = b''

    def _add_data_to_buffer(self):
        data = self._recv_data_from_socket()
        self._buffer += data

    def _parse_buffer(self):
        self._buffer = parser.parse_buffer(self._buffer, self._parser_status_callback)

    def _pop_message(self):
        message = self._status_queue.pop()
        self._status_queue.clear()
        return message

    def send_data(self, data):
        self._log_write(f'Send data: {data}')
        if isinstance(data, str):
            data = data.encode('utf-8')
        self._send_data_to_socket(data)

    def _send_data_to_socket(self, data):
        try:
            self._sock.sendall(data)
        except OSError as e:
            raise LinphoneConnectionError(e)

    def _recv_data_from_socket(self):
        try:
            data = self._sock.recv(self._BUFSIZE)
            self._log_write(f'Received data: {data}')
        except OSError as e:
            raise LinphoneConnectionError(e)
        if not data:
            raise LinphoneConnectionError('Connection closed from remote')
        return data
