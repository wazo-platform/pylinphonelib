#!/bin/bash
umask 0000

/root/linphone-sdk/build/linphone-sdk/desktop/bin/linphone-daemon \
    --disable-stats-events \
    --config /tmp/linphone/linphonerc \
    --pipe /tmp/linphone/socket
