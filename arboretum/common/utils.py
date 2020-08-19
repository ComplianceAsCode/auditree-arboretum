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
"""Common utility functions."""

import subprocess

from compliance.evidence import DAY, HOUR


def parse_seconds(seconds):
    """
    Parse seconds (int) into a human readable string.

    :returns: "D days, H hours, M minutes, S seconds" string
    """
    intervals = [
        ('days', DAY), ('hours', HOUR), ('minutes', 60), ('seconds', 1)
    ]
    formatted = []
    for interval in intervals:
        q, r = divmod(seconds, interval[1])
        if q:
            unit = interval[0][:-1] if q == 1 else interval[0]
            formatted.append(f'{q} {unit}')
        seconds = r
    return ', '.join(formatted)


def mask_secrets(text, secrets):
    """
    Replace secret words in a text with `***`.

    :param str text: a string which may contain secret words.
    :param list[str] secrets: secret word list.
    :returns: masked text.
    """
    for s in secrets:
        text = text.replace(s, '***')
    return text


def run_command(cmd, input_text=None, timeout=None):
    """
    Execute system command.

    This is a wrapper for `subprocess.run()`.

    Example 1: `run_command(['echo', '-n', 'hello'])` returns `('hello','')`.

    Example 2: `run_command(['cat'], input='hello')` returns `('hello','')`.

    Use `subprocess.run()` if other complicated parameters (e.g., encoding)
    should be specified.

    :param list[str] cmd: command line arguments
    :param str input_text: text for standard input of command
    :param int timeout: timeout for command in seconds
    :raises subprocess.CalledProcessError: if the command finishes with
                                           non-zero returncode.
    :raises subprocess.TimeoutExpires: if timeout expires.
    :raises TypeError: if some of `cmd` element is not a `str`.
    :raises IndexError: if length of `cmd` is zero.
    :returns: a tuple of standard output and standard error of the command.
    """
    cp = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        shell=False
    )
    return cp.stdout, cp.stderr
