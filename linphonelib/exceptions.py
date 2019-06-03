# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later


class LinphoneException(Exception):
    pass


class CommandTimeoutException(LinphoneException):
    pass


class LinphoneEOFException(LinphoneException):
    pass


class ExtensionNotFoundException(LinphoneException):
    pass


class CallDeclinedException(LinphoneException):
    pass


class NoActiveCallException(LinphoneException):
    pass


class CallAlreadyInProgressException(LinphoneException):
    pass
