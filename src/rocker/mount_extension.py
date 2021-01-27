# Copyright 2019 Open Source Robotics Foundation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from argparse import ArgumentTypeError
import os
from rocker.extensions import RockerExtension


class Mount(RockerExtension):

    name = 'mount'

    @classmethod
    def get_name(cls):
        return cls.name

    def precondition_environment(self, cli_args):
        pass

    def validate_environment(self, cli_args):
        pass

    def get_preamble(self, cli_args):
        return ''

    def get_snippet(self, cli_args):
        return ''

    def get_docker_args(self, cli_args):
        args = ['']

        volumes = cli_args.get('volume') or []
        mounts = cli_args.get('mount') or []
        # flatten cli_args['mount']
        if mounts:
            mounts = [ x for sublist in cli_args['mount'] for x in sublist]

        # for backwards compatibility:
        #  - interpret --mount arguments without commas with colons like --volume
        #  - interpret --mount arguments without commas and without colons as a single host folder
        #    (absolute or relative to the current working directory) that will be mounted
        #    under the same name in the container
        temp = []
        for mount in mounts:
            elems = mount.split(',')
            if len(elems) == 1:
                if ':' in elems[0]:
                    volumes.append(elems[0])
                else:
                    host_dir = os.path.abspath(elems[0])
                    args.append('-v {0}:{0}'.format(host_dir))
            else:
                temp.append(mount)
        mounts = temp

        # --mount arguments are forwarded as-is.
        for mount in mounts:
            args.append('--mount {0}'.format(mount))

        # --volumes/-v are eventually resolved relative to the current working directory, but otherwise
        # forwarded as-us.
        for volume in volumes:
            elems = volume.split(':')
            host_dir = os.path.abspath(elems[0])
            if len(elems) == 1:
                args.append('-v {0}:{0}'.format(host_dir))
            elif len(elems) == 2:
                container_dir = elems[1]
                args.append('-v {0}:{1}'.format(host_dir, container_dir))
            elif len(elems) == 3:
                container_dir = elems[1]
                options = elems[2]
                args.append('-v {0}:{1}:{2}'.format(host_dir, container_dir, options))
            else:
                raise ArgumentTypeError('--volume expects arguments in format HOST-DIR[:CONTAINER-DIR[:OPTIONS]]')

        return ' '.join(args)

    @staticmethod
    def register_arguments(parser, defaults={}):
        parser.add_argument('-v', '--volume',
            metavar='HOST-DIR[:CONTAINER-DIR[:OPTIONS]]',
            type=str,
            action='append',
            default=defaults.get('volume', argparse.SUPPRESS),
            help='mount volumes in container (equivalent to docker run -v)')
        parser.add_argument('--mount',
            metavar='<key>=<value>[,<key>=<value>[,...]]',
            type=str,
            nargs='+',
            action='append',
            default=defaults.get('mount', argparse.SUPPRESS),
            help='mount volumes in container (equivalent to docker run --mount)')

    @classmethod
    def check_args_for_activation(cls, cli_args):
        """ Returns true if the arguments indicate that this extension should be activated otherwise false."""
        return cli_args.get('volume') or cli_args.get('mount')
