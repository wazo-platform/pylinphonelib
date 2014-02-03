# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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
from hamcrest import contains_inanyorder
from hamcrest import equal_to
from unittest import TestCase
from linphonelib.base_command import BaseCommand
from linphonelib.base_command import pattern
from linphonelib import CommandTimeoutException
from linphonelib import LinphoneEOFException
from mock import Mock
from mock import sentinel


class TestBaseCommandResultHandling(TestCase):

    def test_command_dispatching(self):
        cb1 = Mock()
        cb2 = Mock()

        class S(BaseCommand):
            def __init__(self):
                self.add_handler(sentinel.first, cb1)
                self.add_handler(sentinel.second, cb2)

        s = S()

        cb1_index = self._index_of(sentinel.first, s._handlers)

        s._handle_result(cb1_index)

        cb1.assert_called_once_with(s)
        assert_that(cb2.call_count, equal_to(0))

    @staticmethod
    def _index_of(pattern, handlers):
        for i in xrange(len(handlers)):
            if handlers[i][0] == pattern:
                return i
        raise LookupError('%s is not a member of handlers' % pattern)


class TestBaseCommandHandlers(TestCase):

    def test_subcommands_have_handlers(self):
        class S(BaseCommand):
            def __init__(self):
                pass

        s = S()

        self.assertTrue(hasattr(s, '_handlers'))

    def test_handler_is_filled(self):
        class S(BaseCommand):
            @pattern('lol1')
            def f1(self):
                pass

            @pattern('lol2')
            def f2(self):
                pass

        s = S()

        assert_that(s._param_list(), contains_inanyorder('lol1', 'lol2'))

    def test_multiple_pattern_on_the_same_handler(self):
        class S(BaseCommand):
            @pattern(['lol1', 'lol2'])
            def f1(self):
                pass

        s = S()

        assert_that(s._param_list(), contains_inanyorder('lol1', 'lol2'))

    def test_that_handlers_can_be_defined_in_init(self):
        class S(BaseCommand):
            def __init__(self):
                self.add_handler(sentinel.pattern, lambda: None)

        s = S()

        assert_that(s._param_list(), contains_inanyorder(sentinel.pattern))

    def test_that_handlers_can_be_defined_in_init_and_as_decorators(self):
        class S(BaseCommand):
            def __init__(self):
                self.add_handler('init', lambda: None)

            @pattern('decorator')
            def handler(self):
                pass

        s = S()

        print s._handlers

        assert_that(s._param_list(),
                    contains_inanyorder('init', 'decorator'))


class TestBaseCommandExceptions(TestCase):

    def test_timeout_exception(self):
        mocked_process = Mock()
        mocked_process.expect.side_effect = pexpect.TIMEOUT('')

        c = BaseCommand()
        c._build_command_string = lambda: ''

        self.assertRaises(CommandTimeoutException, c.execute, mocked_process)

    def test_eof_exception(self):
        mocked_process = Mock()
        mocked_process.expect.side_effect = pexpect.EOF('')

        c = BaseCommand()
        c._build_command_string = lambda: ''

        self.assertRaises(LinphoneEOFException, c.execute, mocked_process)
