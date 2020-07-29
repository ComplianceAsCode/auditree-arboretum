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

from arboretum.common.utils import parse_seconds


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
