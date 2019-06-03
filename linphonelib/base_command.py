# Copyright 2014-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pexpect

from collections import namedtuple
from linphonelib.exceptions import CommandTimeoutException
from linphonelib.exceptions import LinphoneEOFException


_PATTERN_MARK = '_matched_by'

_MatchPair = namedtuple('_MatchPair', ['pattern', 'function'])


def _mark_function(function, patterns):
    if _PATTERN_MARK not in function.__dict__:
        function.__dict__[_PATTERN_MARK] = []
    function.__dict__[_PATTERN_MARK].extend(patterns)


def _is_marked(function):
    return type(function).__name__ == 'function' and _PATTERN_MARK in function.__dict__


def _get_matching_patterns(function):
    return function.__dict__[_PATTERN_MARK]


def pattern(patterns):
    """
    mark decorated function objects to be added to _handlers at object
    initialization.
    """
    if type(patterns) is not list:
        patterns = [patterns]

    def decorator(f):
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        _mark_function(decorated, patterns)
        return decorated
    return decorator


class _BaseCommandMeta(type):

    def __new__(meta, name, bases, dct):
        """
        add _handlers to the BaseCommand and add each decorated @pattern
        function to the _handlers
        """
        pairs = []
        for function in dct.values():
            if not _is_marked(function):
                continue
            for pattern in _get_matching_patterns(function):
                pairs.append(_MatchPair(pattern, function))

        dct['_handlers'] = pairs

        return super(_BaseCommandMeta, meta).__new__(meta, name, bases, dct)


class BaseCommand(metaclass=_BaseCommandMeta):

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
            return self._handle_result(result)

    def add_handler(self, pattern, function):
        self._handlers.append(_MatchPair(pattern, function))

    def _param_list(self):
        return [pair.pattern for pair in self._handlers]

    def _handle_result(self, result):
        return self._handlers[result].function(self)


class SimpleCommand(BaseCommand):

    command = None

    def __eq__(self, other):
        return type(self) == type(other)

    def __ne__(self, other):
        return type(self) != type(other)

    def _build_command_string(self):
        assert self.command is not None, '{} should have a command field'.format(self.__class__.__name__)
        return self.command
