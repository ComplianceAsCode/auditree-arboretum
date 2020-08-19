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
from subprocess import CalledProcessError, TimeoutExpired

from arboretum.common.utils import mask_secrets, parse_seconds, run_command


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

    def test_run_command(self):
        """Ensure that run_command works."""
        self.assertEqual(run_command(['echo', '-n', 'hello']), ('hello', ''))
        self.assertEqual(run_command(['cat'], input='hello'), ('hello', ''))
        self.assertRaises(
            TimeoutExpired, run_command, ['sleep', '100'], timeout=3
        )
        self.assertRaises(
            CalledProcessError, run_command, ['file', '--XXXXXXX']
        )

    def test_mask_secrets(self):
        """Ensure that the specified secret text is masked."""
        self.assertEqual(
            mask_secrets('hello MYSECRET MYKEY', ['MYSECRET', 'MYKEY']),
            'hello *** ***'
        )
        self.assertEqual(
            mask_secrets('hello MYMYKEYMYMY', ['MYSECRET', 'MYKEY']),
            'hello MY***MYMY'
        )
