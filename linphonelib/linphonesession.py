# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os
import pexpect
import tempfile

from contextlib import contextmanager
from functools import wraps
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import HangupCommand
from linphonelib.commands import HookStatusCommand
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib.exceptions import LinphoneException


def _execute(f):
    @wraps(f)
    def func(self, *args):
        return self._linphone_shell.execute(f(self, *args))
    return func


class Session(object):

    def __init__(self, uname, secret, hostname, local_port, logfile=None):
        self._uname = uname
        self._secret = secret
        self._hostname = hostname
        self._linphone_shell = _Shell(local_port, logfile)

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
    def hook_status(self):
        return HookStatusCommand()

    @_execute
    def register(self):
        return RegisterCommand(self._uname, self._secret, self._hostname)

    @_execute
    def unregister(self):
        return UnregisterCommand()


class _Shell(object):

    _CONFIG_FILE_CONTENT = '''\
[sip]
sip_port=%(port)s
'''

    def __init__(self, port, logfile=None):
        self._port = port
        self._process = None
        self._config_filename = ''
        self._logfile = logfile

    def __del__(self):
        if os.path.exists(self._config_filename):
            os.unlink(self._config_filename)

        if self._process:
            if not self._process.terminate(force=True):
                raise LinphoneException('Failed to terminate the linphone process')

    def execute(self, cmd):
        if not self._process:
            self._start()

        cmd.execute(self._process)

    def _start(self):
        self._process = pexpect.spawn('linphonec -c %s' % self._create_config_file())
        if self._logfile:
            self._process.logfile = self._logfile

    def _create_config_file(self):
        if self._config_filename:
            return self._config_filename

        content = self._CONFIG_FILE_CONTENT % {'port': self._port}

        with tempfile.NamedTemporaryFile(delete=False) as f:
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
