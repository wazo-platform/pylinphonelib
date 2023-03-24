# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import time
import tempfile

from contextlib import contextmanager
from functools import wraps
from linphonelib.client import LinphoneClient
from linphonelib.exceptions import LinphoneException
from linphonelib.server import LinphoneServer
from linphonelib.commands import (
    AnswerCommand,
    CallCommand,
    CallStatusCommand,
    CallStatsCommand,
    DTMFCommand,
    HangupCommand,
    HoldCommand,
    IsTalkingToCommand,
    IsRingingShowingCommand,
    QuitCommand,
    RegisterCommand,
    RegisterStatusCommand,
    ResumeCommand,
    TransferCommand,
    UnregisterCommand,
)


def _execute(f):
    @wraps(f)
    def func(self, *args):
        return self._linphone_wrapper.execute(f(self, *args))

    return func


class Session:
    def __init__(
        self, uname, secret, hostname, local_sip_port, local_rtp_port, logfile=None
    ):
        self._uname = uname
        self._secret = secret
        self._hostname = hostname
        self._linphone_wrapper = _LinphoneWrapper(
            local_sip_port, local_rtp_port, logfile
        )
        self._call_id = None

    def __str__(self):
        return 'Session %(_uname)s@%(_hostname)s' % self.__dict__

    def close(self):
        self._linphone_wrapper.stop_and_clean()

    @_execute
    def answer(self):
        return AnswerCommand()

    @_execute
    def call(self, exten):
        return CallCommand(exten, self._hostname)

    @_execute
    def send_dtmf(self, digit):
        return DTMFCommand(digit)

    @_execute
    def hangup(self):
        return HangupCommand()

    @_execute
    def hold(self):
        self._call_id = self.call_stats()['Id']
        return HoldCommand()

    @_execute
    def call_status(self):
        return CallStatusCommand()

    @_execute
    def call_stats(self):
        return CallStatsCommand()

    @_execute
    def register(self):
        return RegisterCommand(self._uname, self._secret, self._hostname)

    @_execute
    def register_status(self):
        return RegisterStatusCommand()

    @_execute
    def resume(self):
        id_to_resume = self._call_id
        self._call_id = None
        return ResumeCommand(id_to_resume)

    @_execute
    def is_talking_to(self, caller_id):
        return IsTalkingToCommand(caller_id)

    @_execute
    def is_ringing_showing(self, caller_id):
        return IsRingingShowingCommand(caller_id)

    @_execute
    def transfer(self, exten):
        return TransferCommand(exten)

    @_execute
    def unregister(self):
        return UnregisterCommand()


class _LinphoneWrapper:
    _CONFIG_FILE_CONTENT = '''\
[sip]
sip_port={sip_port}
ipv6_migration_done=1
use_ipv6=0

[rtp]
audio_rtp_port={rtp_port}
'''

    def __init__(self, sip_port, rtp_port, logfile=None):
        self._sip_port = sip_port
        self._rtp_port = rtp_port
        self._logfile = logfile
        self._mount_path = ''
        self._config_file = ''
        self._socket_file = ''
        self._client = None
        self._server = None
        self._configured = False

    def _log_write(self, message):
        if self._logfile:
            self._logfile.write(message)

    def stop_and_clean(self):
        if self._server.is_running():
            try:
                self.execute(QuitCommand())
            except LinphoneException as e:
                self._log_write(str(e))

            self._log_write('Stopping Linphone container...')
            self._wait_until_server_stopped()

        if os.path.exists(self._mount_path):
            if os.path.exists(self._config_file):
                os.unlink(self._config_file)
            os.rmdir(self._mount_path)

    def _configure(self):
        self._mount_path = tempfile.mkdtemp()
        self._config_file = self._create_config_file(self._mount_path)
        self._socket_file = os.path.join(self._mount_path, 'socket')

        self._server = LinphoneServer(self._socket_file, self._mount_path, self._logfile)
        self._client = LinphoneClient(self._socket_file, self._logfile)

        self._configured = True

    def execute(self, cmd):
        if not self._configured:
            self._configure()
        if not self._server.is_running():
            self._server.start()

        try:
            self._client.connect()
            return cmd.execute(self._client)
        finally:
            self._client.disconnect()

    def _create_config_file(self, path):
        content = self._CONFIG_FILE_CONTENT.format(
            sip_port=self._sip_port, rtp_port=self._rtp_port
        )
        config_file = os.path.join(path, 'linphonerc')
        with open(config_file, 'w+') as f:
            f.write(content)

        return config_file

    def _wait_until_server_stopped(self):
        tries = 10
        interval = 0.5
        for _ in range(tries):
            if not self._server.is_running():
                return
            time.sleep(interval)
        self._server.force_stop()


@contextmanager
def registering(session):
    session.register()
    try:
        yield session
    finally:
        session.unregister()
