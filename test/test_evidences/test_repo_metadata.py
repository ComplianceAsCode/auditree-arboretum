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
"""Repo metadata evidence unit tests."""

import json
import unittest

from arboretum.auditree.evidences.repo_metadata import RepoMetadataEvidence


class RepoMetadataEvidenceTest(unittest.TestCase):
    """RepoMetadataEvidence unit tests."""

    def test_no_content(self):
        """Ensure properties requiring content return None when no content."""
        evidence = RepoMetadataEvidence('gh_foo.json', 'bar')
        self.assertIsNone(evidence.repo_size)
        self.assertIsNone(evidence.relevant_content)

    def test_gl_not_implemented(self):
        """Ensure NotImplementedError raised for Gitlab."""
        evidence = RepoMetadataEvidence('gl_foo.json', 'bar')
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = 'Support for Gitlab coming soon...'
        with self.assertRaises(NotImplementedError) as rs:
            _ = evidence.repo_size
        self.assertEqual(str(rs.exception), gl_err_msg)

    def test_bb_not_implemented(self):
        """Ensure NotImplementedError raised for Bitbucket."""
        evidence = RepoMetadataEvidence('bb_foo.json', 'bar')
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = 'Support for Bitbucket coming soon...'
        with self.assertRaises(NotImplementedError) as rs:
            _ = evidence.repo_size
        self.assertEqual(str(rs.exception), gl_err_msg)

    def test_repo_size(self):
        """Ensure repo size is returned."""
        evidence = RepoMetadataEvidence('gh_foo.json', 'bar')
        evidence.set_content(
            open('./test/fixtures/gh_repo_metadata.json').read()
        )
        self.assertEqual(evidence.repo_size, 12345)

    def test_relevant_content(self):
        """Ensure all IGNORED_REPO_METADATA fields are parsed out."""
        evidence = RepoMetadataEvidence('gh_foo.json', 'bar')
        evidence.set_content(
            open('./test/fixtures/gh_repo_metadata.json').read()
        )
        self.assertEqual(json.loads(evidence.relevant_content), {'foo': 'bar'})
