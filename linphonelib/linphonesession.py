# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pexpect
import tempfile

from contextlib import contextmanager
from functools import wraps
from linphonelib.commands import (
    AnswerCommand,
    CallCommand,
    QuitCommand,
    HangupCommand,
    HoldCommand,
    HookStatusCommand,
    new_is_talking_to_command,
    RegisterCommand,
    ResumeCommand,
    UnregisterCommand,
    TransferCommand,
)


def _execute(f):
    @wraps(f)
    def func(self, *args):
        return self._linphone_shell.execute(f(self, *args))
    return func


class Session:

    def __init__(self, uname, secret, hostname, local_sip_port, local_rtp_port, logfile=None):
        self._uname = uname
        self._secret = secret
        self._hostname = hostname
        self._linphone_shell = _Shell(local_sip_port, local_rtp_port, logfile)

    def __str__(self):
        return 'Session %(_uname)s@%(_hostname)s' % self.__dict__

    @_execute
    def answer(self):
        return AnswerCommand()

    @_execute
    def call(self, exten):
        return CallCommand(exten)

    @_execute
    def hangup(self):
        return HangupCommand()

    @_execute
    def hold(self):
        return HoldCommand()

    @_execute
    def hook_status(self):
        return HookStatusCommand()

    @_execute
    def register(self):
        return RegisterCommand(self._uname, self._secret, self._hostname)

    @_execute
    def resume(self):
        return ResumeCommand()

    @_execute
    def is_talking_to(self, caller_id):
        IsTalkingToCommand = new_is_talking_to_command(caller_id)
        return IsTalkingToCommand()

    @_execute
    def transfer(self, exten):
        return TransferCommand(exten)

    @_execute
    def unregister(self):
        return UnregisterCommand()


class _Shell:

    _DOCKER_IMG = "wazopbx/wazo-linphone"

    _CONFIG_FILE_CONTENT = '''\
[sip]
sip_port={sip_port}

[rtp]
audio_rtp_port={rtp_port}
'''

    def __init__(self, sip_port, rtp_port, logfile=None):
        self._sip_port = sip_port
        self._rtp_port = rtp_port
        self._process = None
        self._config_filename = ''
        self._logfile = logfile

    def __del__(self):
        if self._process:
            self.execute(QuitCommand())
            if self._process.isalive():
                self._process.terminate(force=True)

        if os.path.exists(self._config_filename):
            os.unlink(self._config_filename)

    def execute(self, cmd):
        if not self._process:
            self._start()

        return cmd.execute(self._process)

    def _start(self):
        config_file = self._create_config_file()
        if os.getenv('USE_DOCKER'):
            cmd = "docker run --rm -ti -v {linphonerc}:/root/.linphonerc {docker_image}".format(
                linphonerc=config_file,
                docker_image=self._DOCKER_IMG,
            )
        else:
            cmd = 'sh -c "linphonec -c {linphonerc}" &'.format(linphonerc=config_file)

        self._process = pexpect.spawn(cmd, encoding='utf-8')
        if self._logfile:
            self._process.logfile = self._logfile

    def _create_config_file(self):
        if self._config_filename:
            return self._config_filename

        content = self._CONFIG_FILE_CONTENT.format(sip_port=self._sip_port, rtp_port=self._rtp_port)

        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            self._config_filename = f.name
            f.write(content)

        return self._config_filename


@contextmanager
def registering(session):
    session.register()
    try:
        yield session
    finally:
        session.unregister()
