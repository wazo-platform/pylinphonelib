# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class LinphoneException(Exception):
    pass


class CommandTimeoutException(LinphoneException):
    pass


class ExtensionNotFoundException(LinphoneException):
    pass


class LinphoneConnectionError(LinphoneException):
    pass


class NoActiveCallException(LinphoneException):
    pass
