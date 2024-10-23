# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import time

from linphonelib.client import LinphoneClient


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
            '--rm',
            '--detach',
            '--name',
            self._docker_name,
            '--volume',
            f'{self._mount_path}:/tmp/linphone',
            self._DOCKER_IMG,
        ]
        self._log_write('Starting linphone container...')
        subprocess.run(cmd, stdout=subprocess.DEVNULL)
        self._log_write('Waiting for linphone container to be ready...')
        self._wait_until_ready()
        self._log_write('Linphone container ready!')

    def force_stop(self):
        cmd = ['docker', 'kill', self._docker_name]
        subprocess.run(cmd)

    def _wait_until_ready(self):
        client = LinphoneClient(self._socket_file, self._logfile)
        tries = 10
        interval = 0.5
        for _ in range(tries):
            if client.is_server_up():
                return
            time.sleep(interval)

        raise Exception('Unable to get socket file')
