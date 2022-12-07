# Copyright 2014-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import abc

from linphonelib.exceptions import (
    CommandTimeoutException,
    LinphoneConnectionError,
)


class BaseCommand(metaclass=abc.ABCMeta):
    def execute(self, linphone_client):
        cmd_string = self.command
        linphone_client.send_data(cmd_string)
        try:
            message = linphone_client.parse_next_status_message()
        except LinphoneConnectionError as e:
            raise CommandTimeoutException(f'{self.__class__.__name__}: {e}')
        if message.status == 'Ok':
            return self.handle_status_ok(message.body)
        elif message.status == 'Error':
            return self.handle_status_error(message.body)

        raise NotImplementedError(f'Status: {message.status}')

    @abc.abstractmethod
    def handle_status_ok(self, message):
        pass

    @abc.abstractmethod
    def handle_status_error(self, message):
        pass

    @property
    @abc.abstractmethod
    def command(self, message):
        pass
