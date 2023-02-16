# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from linphonelib.exceptions import (
    ExtensionNotFoundException,
    LinphoneException,
    NoActiveCallException,
)
from linphonelib.base_command import BaseCommand


class AnswerCommand(BaseCommand):
    command = 'answer'

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        if message['Reason'] == 'No call to accept.':
            raise NoActiveCallException()
        raise LinphoneException(message['Reason'])


class CallCommand(BaseCommand):
    def __init__(self, exten, hostname):
        self._exten = exten
        self._hostname = hostname

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        if message['Reason'] == 'Call creation failed.':
            raise ExtensionNotFoundException()
        raise LinphoneException(message['Reason'])

    @property
    def command(self):
        return f'call sip:{self._exten}@{self._hostname}'


class DTMFCommand(BaseCommand):
    def __init__(self, digit):
        self._digit = digit

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        # DTMF command never send Status: Error
        pass

    @property
    def command(self):
        return f'dtmf {self._digit}'


class HangupCommand(BaseCommand):
    command = 'terminate'

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        if message['Reason'] == 'No active call.':
            raise NoActiveCallException()
        raise LinphoneException(message['Reason'])


class HoldCommand(BaseCommand):
    command = 'call-pause'

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        if message['Reason'] == 'No current call available.':
            raise NoActiveCallException()
        raise LinphoneException(message['Reason'])


class CallStatus:
    OFF = 0
    RINGING = 1
    ANSWERED = 2


class CallStatusCommand(BaseCommand):
    command = 'call-status'

    def handle_status_ok(self, message):
        if message['State'] == 'LinphoneCallStreamsRunning':
            return CallStatus.ANSWERED
        if message['State'] == 'LinphoneCallIncomingReceived':
            return CallStatus.RINGING

    def handle_status_error(self, message):
        if message['Reason'] == 'No current call available.':
            return CallStatus.OFF


class CallStatsCommand(BaseCommand):
    command = 'call-stats'

    def handle_status_ok(self, message):
        return message

    def handle_status_error(self, message):
        raise LinphoneException(message['Reason'])


class IsTalkingToCommand(BaseCommand):
    command = 'call-status'

    def __init__(self, caller_id):
        self._caller_id = caller_id

    def handle_status_ok(self, message):
        if message['State'] != 'LinphoneCallStreamsRunning':
            raise LinphoneException('Not in conversation')

        if self._caller_id not in message['From']:
            raise LinphoneException(f'Do not talking to {self._caller_id}')

        return True

    def handle_status_error(self, message):
        raise LinphoneException(message['Reason'])


class IsRingingShowingCommand(BaseCommand):
    command = 'call-status'

    def __init__(self, caller_id):
        self._caller_id = caller_id

    def handle_status_ok(self, message):
        if message['State'] != 'LinphoneCallIncomingReceived':
            raise LinphoneException('Not ringing')

        if self._caller_id not in message['From']:
            raise LinphoneException(f'Do not ringing showing {self._caller_id}')

        return True

    def handle_status_error(self, message):
        raise LinphoneException(message['Reason'])


class RegisterCommand(BaseCommand):
    def __init__(self, uname, passwd, hostname):
        self._uname = uname
        self._passwd = passwd
        self._hostname = hostname

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        # register command never send Status: Error
        pass

    @property
    def command(self):
        return f'register sip:{self._uname}@{self._hostname} {self._hostname} {self._passwd}'


class RegisterStatus:
    REGISTERED = 0
    FAIL = 1


class RegisterStatusCommand(BaseCommand):
    command = 'register-status ALL'

    def handle_status_ok(self, message):
        if message['State'] == 'LinphoneRegistrationOk':
            return RegisterStatus.REGISTERED
        if message['State'] == 'LinphoneRegistrationFailed':
            return RegisterStatus.FAIL

    def handle_status_error(self, message):
        raise NotImplementedError()


class ResumeCommand(BaseCommand):
    def __init__(self, call_id):
        self._call_id = call_id

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        if message['Reason'] == 'No current call available.':
            raise NoActiveCallException()
        raise LinphoneException(message['Reason'])

    @property
    def command(self):
        if self._call_id is None:
            raise LinphoneException('Invalid call ID')
        return f'call-resume {self._call_id}'


class TransferCommand(BaseCommand):
    def __init__(self, exten):
        self._exten = exten

    def handle_status_ok(self, message):
        raise NotImplementedError()

    def handle_status_error(self, message):
        raise NotImplementedError()

    @property
    def command(self):
        return f'transfer {self._exten}'


class UnregisterCommand(BaseCommand):
    command = 'unregister ALL'

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        # unregister command never send Status: Error
        pass


class QuitCommand(BaseCommand):
    command = 'quit'

    def handle_status_ok(self, message):
        pass

    def handle_status_error(self, message):
        # quit command never send Status: Error
        pass
