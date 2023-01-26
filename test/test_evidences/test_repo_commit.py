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
"""Repo commit evidence unit tests."""

import unittest

from arboretum.auditree.evidences.repo_commit import RepoCommitEvidence


class RepoCommitEvidenceTest(unittest.TestCase):
    """RepoCommitEvidence unit tests."""

    def test_no_content(self):
        """Ensure properties requiring content return None when no content."""
        evidence = RepoCommitEvidence("gh_foo.json", "bar")
        self.assertIsNone(evidence.signed_status)
        self.assertIsNone(evidence.author_info)
        self.assertIsNone(evidence.as_a_list)

    def test_gl_not_implemented(self):
        """Ensure NotImplementedError raised for Gitlab."""
        evidence = RepoCommitEvidence("gl_foo.json", "bar")
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = "Support for Gitlab coming soon..."
        with self.assertRaises(NotImplementedError) as ss:
            _ = evidence.signed_status
        self.assertEqual(str(ss.exception), gl_err_msg)
        with self.assertRaises(NotImplementedError) as ai:
            _ = evidence.author_info
        self.assertEqual(str(ai.exception), gl_err_msg)

    def test_bb_not_implemented(self):
        """Ensure NotImplementedError raised for Bitbucket."""
        evidence = RepoCommitEvidence("bb_foo.json", "bar")
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = "Support for Bitbucket coming soon..."
        with self.assertRaises(NotImplementedError) as ss:
            _ = evidence.signed_status
        self.assertEqual(str(ss.exception), gl_err_msg)
        with self.assertRaises(NotImplementedError) as ai:
            _ = evidence.author_info
        self.assertEqual(str(ai.exception), gl_err_msg)

    def test_as_a_list(self):
        """Ensure dict returned when content is present."""
        evidence = RepoCommitEvidence("gh_foo.json", "bar")
        evidence.set_content('[{"foo": "bar"}]')
        self.assertEqual(evidence.as_a_list, [{"foo": "bar"}])

    def test_signed_status(self):
        """Ensure commit signed details returned."""
        evidence = RepoCommitEvidence("gh_foo.json", "bar")
        evidence.set_content(open("./test/fixtures/gh_repo_commits.json").read())
        self.assertEqual(
            evidence.signed_status,
            [{"sha": "a123456789", "url": "https://the-commit-url", "signed": True}],
        )

    def test_author_info(self):
        """Ensure commit author details returned."""
        evidence = RepoCommitEvidence("gh_foo.json", "bar")
        evidence.set_content(open("./test/fixtures/gh_repo_commits.json").read())
        self.assertEqual(
            evidence.author_info,
            [
                {
                    "sha": "a123456789",
                    "url": "https://the-commit-url",
                    "author": "The Dude",
                    "datetime": "2020-08-20T12:12:12Z",
                }
            ],
        )
