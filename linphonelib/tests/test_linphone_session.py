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

import pexpect

from hamcrest import assert_that
from hamcrest import equal_to
from linphonelib.commands import _BaseCommand
from linphonelib.commands import AnswerCommand
from linphonelib.commands import CallCommand
from linphonelib.commands import HangupCommand
from linphonelib.commands import RegisterCommand
from linphonelib.commands import UnregisterCommand
from linphonelib.linphonesession import _Shell
from linphonelib import Session
from mock import MagicMock
from mock import Mock
from mock import patch
from mock import sentinel
from unittest import TestCase


class TestLinphoneSession(TestCase):

    def setUp(self):
        self._name, self._passwd, self._hostname = 'abc', 'secret', '127.0.0.1'
        self._s = Session(self._name, self._passwd, self._hostname, sentinel.local_port)
        self._shell = self._s._linphone_shell = Mock(_Shell)

    def test_answer(self):
        self._s.answer()

        self._shell.execute.assert_called_once_with(AnswerCommand())

    def test_call(self):
        self._s.call(sentinel.exten)

        self._shell.execute.assert_called_once_with(
            CallCommand(sentinel.exten)
        )

    def test_hangup(self):
        self._s.hangup()

        self._shell.execute.assert_called_once_with(HangupCommand())

    def test_register(self):
        self._s.register()

        self._shell.execute.assert_called_once_with(
            RegisterCommand(self._name, self._passwd, self._hostname)
        )

    def test_unregister(self):
        self._s.unregister()

        self._shell.execute.assert_called_once_with(UnregisterCommand())


class TestShell(TestCase):

    def setUp(self):
        self._filename = '/tmp/abcdef'

    def test_execute(self):
        s = _Shell(sentinel.port)
        s._process = Mock(pexpect.spawn)
        cmd = Mock(_BaseCommand)

        s.execute(cmd)

        cmd.execute.assert_called_once_with(s._process)

    def test_start(self):
        launch_command = 'linphonec -c %s' % self._filename
        s = _Shell(sentinel.port)
        s._create_config_file = Mock(return_value=self._filename)

        mock_spawn = Mock(pexpect.spawn)
        with patch('pexpect.spawn', Mock(return_value=mock_spawn)) as spawn:
            s._start()

            assert_that(s._process, equal_to(mock_spawn))
            spawn.assert_called_once_with(launch_command)

    @patch('tempfile.NamedTemporaryFile', create=True, return_value=MagicMock(spec=file))
    def test_create_config_file(self, mock_open):
        port = 5061
        mocked_file = mock_open.return_value.__enter__.return_value
        mocked_file.name = self._filename
        s = _Shell(port)

        result = s._create_config_file()

        expected_content = '''\
[sip]
sip_port=%s
''' % port
        mocked_file.write.assert_called_once_with(expected_content)

        assert_that(result, equal_to(self._filename))
        assert_that(s._config_filename, equal_to(self._filename))

    def test_create_config_file_already_exists(self):
        s = _Shell(sentinel.port)
        s._config_filename = self._filename

        filename = s._create_config_file()

        assert_that(filename, equal_to(self._filename))

    @patch('os.path.exists', Mock(return_value=True))
    @patch('os.unlink')
    def test_cleanup(self, mock_unlink):
        s = _Shell(sentinel.port)
        s._config_filename = self._filename
        child = s._process = Mock(pexpect.spawn)

        del s

        mock_unlink.assert_called_once_with(self._filename)
        child.terminate.assert_called_once_with(force=True)
