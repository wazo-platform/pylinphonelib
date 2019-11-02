# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess


# NOTE: Improve using docker python library
class LinphoneServer:

    _DOCKER_IMG = "wazopbx/wazo-linphone"

    def __init__(self, mount_path):
        self._mount_path = mount_path
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

    def force_stop(self):
        cmd = ['docker', 'kill', self._docker_name]
        subprocess.run(cmd)
