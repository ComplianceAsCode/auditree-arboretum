# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2020 IBM Corp. All rights reserved.
#
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
"""Common error classes."""


class CommandExecutionError(RuntimeError):
    """Represents error at executing command."""

    def __init__(self, cmd, stdout, stderr, returncode):
        """Initialize an instance.

        Initialize an instance with the return values of the command.
        """
        self.__cmd = cmd
        self.__stdout = stdout
        self.__stderr = stderr
        self.__returncode = returncode

    def __str__(self):
        """Get information about the command line and its result."""
        return (
            f'Error running command: {self.cmd}\n'
            f'returncode: {self.returncode}\n'
            f'stdout: {self.stdout}\n'
            f'stderr: {self.stderr}'
        )

    @property
    def cmd(self):
        """Get command line text."""
        return self.__cmd

    @property
    def stdout(self):
        """Get standard out text of the command."""
        return self.__stdout

    @property
    def stderr(self):
        """Get standard error text of the command."""
        return self.__stderr

    @property
    def returncode(self):
        """Get return code of the command."""
        return self.__returncode
