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

from linphonelib.exceptions import CommandTimeoutException
from linphonelib.exceptions import LinphoneEOFException


def pattern(pattern):
    """
    appends a tupple (pattern, function) to the _handlers
    of the command class
    """
    def decorator(f):
        def decorated(*args, **kwargs):
            return f(*args, **kwargs)
        decorated.func_dict['_matched_by'] = pattern
        return decorated
    return decorator


class _BaseCommandMeta(type):

    def __new__(meta, name, bases, dct):
        """
        all base command subclass should have a _handlers list even when
        an __init__ is defined
        all decorated method are also added to _handlers
        """
        if '_handlers' not in dct:
            dct['_handlers'] = []

        for f in dct.itervalues():
            if type(f).__name__ != 'function':
                continue
            if '_matched_by' not in f.func_dict:
                continue
            pattern = f.func_dict['_matched_by']
            dct['_handlers'].append((pattern, f))

        return super(_BaseCommandMeta, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        return super(_BaseCommandMeta, cls).__init__(name, bases, dct)


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

    def _param_list(self):
        return [pair[0] for pair in self._handlers]

    def _handle_result(self, result):
        self._handlers[result]()
