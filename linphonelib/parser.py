# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class LinphoneParsingError(Exception):
    pass


# NOTE: Since there are no stable delimiter to know when the message start or stop, then we guess
# that we already have all the message in the buffer ...
def parse_buffer(raw_buffer, status_callback):
    unparsed_buffer = raw_buffer
    while unparsed_buffer:
        head, sep, unparsed_buffer = unparsed_buffer.partition(b'\nStatus')
        if not sep:
            unparsed_buffer = head
            head, sep, unparsed_buffer = unparsed_buffer.partition(b'\nEvent-type')

        unparsed_buffer = sep.lstrip(b'\n') + unparsed_buffer
        try:
            _parse_msg(head, status_callback)
        except LinphoneParsingError:
            continue

    return b''


def _parse_msg(data, status_callback):
    data = data.replace(b'\n\n', b'\n').strip(b'\n')
    lines = data.decode('utf8', 'replace').split('\n')

    try:
        first_header, first_value = _parse_line(lines[0])
    except LinphoneParsingError:
        raise LinphoneParsingError('unexpected data: %r' % data)

    message = {}
    message[first_header] = first_value
    for line in lines[1:]:
        try:
            header, value = _parse_line(line)
        except LinphoneParsingError:
            continue  # ignore invalid line
        message[header] = value

    if first_header == 'Status':
        status_callback(first_value, message)


def _parse_line(line):
    try:
        header, value = line.split(':', 1)
    except ValueError:
        raise LinphoneParsingError()
    value = value.lstrip()
    return header, value
