# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import subprocess
import time
from typing import TYPE_CHECKING, TextIO

if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper


# NOTE: Improve using docker python library
class LinphoneServer:
    _DOCKER_IMG = "wazoplatform/wazo-linphone"

    def __init__(self, socket_file, mount_path, logfile):
        self._mount_path = mount_path
        self._socket_file = socket_file
        self._logfile = logfile
        self._docker_name = os.path.basename(self._mount_path)

    def _log_write(self, message):
        if self._logfile:
            self._logfile.write(message)

    def is_running(self):
        cmd = ['docker', 'container', 'ls', '-qf', f'name={self._docker_name}']
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        return len(result.stdout)

    def start(self):
        cmd = [
            'docker',
            'run',
            '--detach',
            '--name',
            self._docker_name,
            '--volume',
            f'{self._mount_path}:/tmp/linphone',
            self._DOCKER_IMG,
        ]
        self._log_write('Starting linphone container...')
        completed_process = subprocess.run(cmd, stdout=subprocess.PIPE)
        self._container_id = completed_process.stdout.decode('utf-8').strip()
        self._log_write('Waiting for linphone container to be ready...')
        self._wait_until_ready()
        self._log_write('Linphone container ready!')

    def dump_container_output(self, log_file: TextIO | _TemporaryFileWrapper):
        self._log_write('Linphone server logs:')
        completed_process = subprocess.run(
            ['docker', 'logs', '--timestamps', self._container_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log_file.write(completed_process.stdout.decode('utf-8'))
        self._log_write('End of Linphone server logs')

    def force_stop(self):
        cmd = ['docker', 'kill', self._docker_name]
        subprocess.run(cmd)

    def _is_ready(self):
        return os.path.exists(self._socket_file)

    def cleanup(self):
        subprocess.run(
            ['docker', 'rm', self._container_id],
            stdout=subprocess.DEVNULL,
        )

    def _wait_until_ready(self):
        tries = 10
        interval = 0.5
        for _ in range(tries):
            if self._is_ready():
                return
            time.sleep(interval)

        raise Exception('Unable to get socket file')
