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

from collections import namedtuple
from linphonelib.exceptions import CommandTimeoutException
from linphonelib.exceptions import LinphoneEOFException


_PATTERN_MARK = '_matched_by'

_MatchPair = namedtuple('_MatchPair', ['pattern', 'function'])


def _mark_function(f, pattern):
    f.func_dict[_PATTERN_MARK] = pattern


def _is_marked(f):
    return type(f).__name__ == 'function' and _PATTERN_MARK in f.func_dict


def _get_matching_pattern(f):
    return f.func_dict[_PATTERN_MARK]


def pattern(pattern):
    """
    mark decorated function objects to be added to _handlers at object
    initialization.
    """
    def decorator(f):
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        _mark_function(decorated, pattern)
        return decorated
    return decorator


class _BaseCommandMeta(type):

    def __new__(meta, name, bases, dct):
        """
        add _handlers to the BaseCommand and add each decorated @pattern
        function to the _handlers
        """
        dct['_handlers'] = [_MatchPair(_get_matching_pattern(f), f)
                            for f in dct.itervalues() if _is_marked(f)]

        return super(_BaseCommandMeta, meta).__new__(meta, name, bases, dct)


class BaseCommand(object):

    __metaclass__ = _BaseCommandMeta

    def execute(self, process):
        cmd_string = self._build_command_string()
        process.sendline(cmd_string)
        try:
            result = process.expect(self._param_list())
        except pexpect.TIMEOUT:
            raise CommandTimeoutException(self.__class__.__name__)
        except pexpect.EOF:
            raise LinphoneEOFException(self.__class__.__name__)
        else:
            self._handle_result(result)

    def add_handler(self, pattern, function):
        self._handlers.append(_MatchPair(pattern, function))

    def _param_list(self):
        return [pair.pattern for pair in self._handlers]

    def _handle_result(self, result):
        self._handlers[result].function(self)
