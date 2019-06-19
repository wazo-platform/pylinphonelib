# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pexpect

from linphonelib.exceptions import (
    ExtensionNotFoundException,
    CallAlreadyInProgressException,
    CallDeclinedException,
    LinphoneException,
    NoActiveCallException,
)
from linphonelib.base_command import (
    BaseCommand,
    SimpleCommand,
    pattern,
)


class AnswerCommand(SimpleCommand):

    command = 'answer'

    @pattern('Call \d+ with .* connected.')
    def handle_connected(self):
        pass

    @pattern('There are no calls to answer.')
    def handle_no_call(self):
        raise NoActiveCallException()


class CallCommand(BaseCommand):

    def __init__(self, exten):
        self._exten = exten

    def __eq__(self, other):
        return self._exten == other._exten

    @pattern([
        'Call answered by <sip:.*>.',  # 3.6.X
        'Call answered by sip:.*.',  # 3.12.X
        'Remote ringing.',
        'Call \d+ to <sip:.*> ringing.'
    ])
    def handle_success(self):
        pass

    @pattern('Not Found')
    def handle_not_found(self):
        raise ExtensionNotFoundException('Failed to call {}'.format(self._exten))

    @pattern('Call declined')
    def handle_call_declined(self):
        raise CallDeclinedException('Call to {} declined'.format(self._exten))

    def _build_command_string(self):
        return 'call {}'.format(self._exten)


class HangupCommand(SimpleCommand):

    command = 'terminate'

    @pattern('Call ended')
    def handle_success(self):
        pass

    @pattern('No active calls')
    def handle_no_active_calls(self):
        raise NoActiveCallException()

    @pattern(['Could not stop the call with id \d+', 'Could not stop the active call.'])
    def handle_count_not_stop_the_call(self):
        raise LinphoneException('Hangup failed')


class HoldCommand(SimpleCommand):

    command = 'pause'

    @pattern('Call .* is now paused.')
    def handle_success(self):
        pass

    @pattern('you can only pause when a call is in process')
    def handle_no_call_in_progress(self):
        raise NoActiveCallException()


class HookStatus:
    OFFHOOK = 0
    RINGING = 1
    ANSWERED = 2
    RINGBACK_TONE = 3


class HookStatusCommand(SimpleCommand):

    command = 'status hook'

    @pattern([
        'hook=offhook',  # 3.6.X
        'hook=on-hook',  # 3.12.X
    ])
    def handle_offhook(self):
        return HookStatus.OFFHOOK

    @pattern('hook=ringing sip:.*')
    def handle_ringback_tone(self):
        return HookStatus.RINGBACK_TONE

    @pattern('Incoming call from ".*" <sip:.*>')
    def handle_ringing(self):
        return HookStatus.RINGING

    @pattern(['hook=answered duration=\d+ ".*" <sip:.*>', 'Call out, hook=.* duration=.*'])
    def handle_answered(self):
        return HookStatus.ANSWERED


def new_is_talking_to_command(caller_id):
    to_match = 'hook=answered duration=\d+ "{}" <sip:.*>'.format(caller_id)

    class IsTalkingToCommand(SimpleCommand):

        command = 'status hook'

        @pattern(to_match)
        def handle_answered(self):
            return True

    return IsTalkingToCommand


class RegisterCommand(BaseCommand):

    def __init__(self, uname, passwd, hostname):
        self._uname = uname
        self._passwd = passwd
        self._hostname = hostname

    def __eq__(self, other):
        return (
            self._uname == other._uname and
            self._passwd == other._passwd and
            self._hostname == other._hostname
        )

    @pattern([
        'Registration on <sip:.*> successful.',  # 3.6.X
        'Registration on sip:.* successful.',  # 3.12.X
    ])
    def handle_success(self):
        pass

    @pattern([
        'Registration on <sip:.*> failed:.*',  # 3.6.X
        'Registration on sip:.* failed:.*',  # 3.12.X
    ])
    def handle_failure(self):
        raise LinphoneException('Registration failed')

    def _build_command_string(self):
        return 'register sip:{name}@{host} {host} {passwd}'.format(
            name=self._uname,
            passwd=self._passwd,
            host=self._hostname,
        )


class ResumeCommand(SimpleCommand):

    command = 'resume'

    @pattern('Call resumed.')
    def handle_success(self):
        pass

    @pattern('There is already a call in process pause or stop it first')
    def handle_already_on_a_call(self):
        raise CallAlreadyInProgressException()

    @pattern('There is no calls at this time.')
    def handle_no_call_to_resume(self):
        raise CallAlreadyInProgressException()


class TransferCommand(BaseCommand):

    def __init__(self, exten):
        self._exten = exten

    def __eq__(self, other):
        return self._exten == other._exten

    @pattern('Call ended')
    def handle_success(self):
        pass

    @pattern("No active call, please specify a call id among the ones listed by 'calls' command.")
    def handle_no_active_call(self):
        raise ExtensionNotFoundException('Failed to call {}'.format(self._exten))

    def _build_command_string(self):
        return 'transfer {}'.format(self._exten)


class UnregisterCommand(SimpleCommand):

    command = 'unregister'

    @pattern('Unregistration on sip:.* done.')
    def handle_success(self):
        pass

    @pattern('unregistered')
    def handle_not_registered(self):
        raise LinphoneException('Unregister failed')


class QuitCommand(SimpleCommand):

    command = 'quit'

    @pattern(pexpect.EOF)
    def handle_success(self):
        pass
