# Copyright 2019-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock

from hamcrest import (
    assert_that,
    empty,
)

from ..parser import parse_buffer

MESSAGE_DELIMITER = b'\r\n\r\n'
EVENT_DELIMITER = b'Event: '
RESPONSE_DELIMITER = b'Response: '


class TestParser(unittest.TestCase):
    def setUp(self):
        self.status_callback = Mock()

    def test_given_no_delimiter_found_then_no_buffer_returned(self):
        raw_buffer = b'unhandled case'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_not_called()

    def test_given_incomplete_message_then_no_buffer_returned(self):
        raw_buffer = b'previous_msg\nStatus: '

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_called_once_with('', {'Status': ''})

    def test_given_complete_message_then_callback_and_buffer_emptied(self):
        raw_buffer = b'Status: Ok'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_called_once_with('Ok', {'Status': 'Ok'})

    def test_given_complete_messages_then_multiple_callback_and_buffer_emptied(self):
        raw_buffer = b'Status: Ok\nStatus: Error'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_any_call('Ok', {'Status': 'Ok'})
        self.status_callback.assert_any_call('Error', {'Status': 'Error'})

    def test_given_complete_messages_when_event_type(self):
        raw_buffer = b'Status: Ok\nEvent-type: random'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_called_once_with('Ok', {'Status': 'Ok'})

    def test_given_unknown_message_then_no_callback(self):
        raw_buffer = b'Unknown message'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_not_called()

    def test_given_unparseable_body_then_line_is_ignored(self):
        raw_buffer = b'Status: Ok\nInvalid body\n'

        unparsed_buffer = parse_buffer(raw_buffer, self.status_callback)

        assert_that(unparsed_buffer, empty())
        self.status_callback.assert_any_call('Ok', {'Status': 'Ok'})
