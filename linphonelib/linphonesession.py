# -*- coding: utf-8 -*-

import os
import pexpect
import tempfile

from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand


class LinphoneException(Exception):
    pass


class Session(object):

    def __init__(self, uname, secret, hostname, local_port):
        self._uname = uname
        self._secret = secret
        self._hostname = hostname
        self._linphone_shell = _Shell(local_port)

    def register(self):
        cmd = RegisterCommand(self._uname, self._secret, self._hostname)
        self._linphone_shell.execute(cmd)

    def unregister(self):
        cmd = UnregisterCommand()
        self._linphone_shell.execute(cmd)


class _Shell(object):

    _CONFIG_FILE_CONTENT = '''\
[sip]
sip_port=%(port)s
'''

    def __init__(self, port):
        self._port = port
        self._process = None
        self._config_filename = ''

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

    def _create_config_file(self):
        if self._config_filename:
            return self._config_filename

        content = self._CONFIG_FILE_CONTENT % {'port': self._port}

        with tempfile.NamedTemporaryFile(delete=False) as f:
            self._config_filename = f.name
            f.write(content)

        return self._config_filename
