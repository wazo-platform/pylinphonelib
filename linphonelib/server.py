# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
import time


# NOTE: Improve using docker python library
class LinphoneServer:

    _DOCKER_IMG = "wazoplatform/wazo-linphone"

    def __init__(self, socket_file, mount_path):
        self._mount_path = mount_path
        self._socket_file = socket_file
        self._docker_name = os.path.basename(self._mount_path)

    def is_running(self):
        cmd = ['docker', 'container', 'ls', '-qf', 'name={}'.format(self._docker_name)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        return len(result.stdout)

    def start(self):
        cmd = [
            'docker',
            'run',
            '--rm', '-d',
            '--name', self._docker_name,
            '-v', '{}:/tmp/linphone'.format(self._mount_path),
            self._DOCKER_IMG
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL)
        self._wait_until_ready()

    def force_stop(self):
        cmd = ['docker', 'kill', self._docker_name]
        subprocess.run(cmd)

    def _is_ready(self):
        return os.path.exists(self._socket_file)

    def _wait_until_ready(self):
        tries = 10
        interval = 0.5
        for _ in range(tries):
            if self._is_ready():
                return
            time.sleep(interval)

        raise Exception('Unable to get socket file')
