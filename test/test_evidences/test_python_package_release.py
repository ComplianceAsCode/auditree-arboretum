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
"""Python package release evidence unit tests."""

import unittest

from arboretum.auditree.evidences.python_package_release import PackageReleaseEvidence


class PythonPackageReleaseTest(unittest.TestCase):
    """PythonPackageRelease unit tests."""

    def test_latest_release_success(self):
        """Ensure that latest available release is returned."""
        evidence = PackageReleaseEvidence("foo.xml", "bar")
        evidence.set_content(open("./test/fixtures/pypi_release_info.xml").read())
        self.assertEqual(evidence.latest_release, "1.0.2")

    def test_latest_release_none(self):
        """Ensure latest release is None if no content."""
        evidence = PackageReleaseEvidence("foo.xml", "bar")
        self.assertIsNone(evidence.latest_release)

    def test_latest_release_already_set(self):
        """Ensure that latest release only retrieved if not yet set."""
        evidence = PackageReleaseEvidence("foo.xml", "bar")
        evidence._latest_release = "foo.bar.baz"
        evidence.set_content(open("./test/fixtures/pypi_release_info.xml").read())
        self.assertEqual(evidence.latest_release, "foo.bar.baz")
