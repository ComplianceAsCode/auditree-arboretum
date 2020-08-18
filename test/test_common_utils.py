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
"""Arboretum common utilities tests."""

import unittest

from arboretum.common.exceptions import CommandExecutionError
from arboretum.common.utils import parse_seconds, run_command


class CommonUtilsTest(unittest.TestCase):
    """Arboretum common utilities tests."""

    def test_singular_form(self):
        """Ensure that singular form is returned when expected."""
        self.assertEqual(parse_seconds(86400), '1 day')
        self.assertEqual(parse_seconds(3600), '1 hour')
        self.assertEqual(parse_seconds(60), '1 minute')
        self.assertEqual(parse_seconds(1), '1 second')

    def test_plural_form(self):
        """Ensure that plural form is returned when expected."""
        self.assertEqual(parse_seconds(172800), '2 days')
        self.assertEqual(parse_seconds(7200), '2 hours')
        self.assertEqual(parse_seconds(120), '2 minutes')
        self.assertEqual(parse_seconds(2), '2 seconds')

    def test_free_form_mix(self):
        """Ensure that proper string is returned when expected."""
        self.assertEqual(parse_seconds(86410), '1 day, 10 seconds')
        self.assertEqual(
            parse_seconds(123456), '1 day, 10 hours, 17 minutes, 36 seconds'
        )

    def test_run_command_strings(self):
        """Ensure that the function works.

        It should accept either a space-separated string or a list of string.
        """
        self.assertEqual(run_command('echo -n hello'), ('hello', ''))
        self.assertEqual(run_command(['echo', '-n', 'hello']), ('hello', ''))

    def test_run_command_error_args(self):
        """Ensure that the function raises exception for wrong params."""
        self.assertRaises(TypeError, run_command, 1)
        self.assertRaises(TypeError, run_command, (1, 2))
        self.assertRaises(TypeError, run_command, {'a': 'b'})
        self.assertRaises(TypeError, run_command, None)
        # following errors will be come from subprocess.Popen
        self.assertRaises(IndexError, run_command, [])
        self.assertRaises(TypeError, run_command, [1, 2])

    def test_run_command_secret_masking(self):
        """Ensure that the specified secret text is masked."""
        with self.assertRaises(CommandExecutionError) as cm:
            run_command('file --MYSECRET', secrets=['MYSECRET'])
        self.assertTrue('MYSECRET' not in cm.exception.stderr)
        self.assertTrue('***' in cm.exception.stderr)
        with self.assertRaises(CommandExecutionError) as cm:
            run_command(
                'file --MYSECRETMYCONFIDENTIAL',
                secrets=['MYSECRET', 'MYCONFIDENTIAL']
            )
        self.assertTrue('MYSECRET' not in cm.exception.stderr)
        self.assertTrue('MYCONFIDENTIAL' not in cm.exception.stderr)
        self.assertTrue('******' in cm.exception.stderr)
