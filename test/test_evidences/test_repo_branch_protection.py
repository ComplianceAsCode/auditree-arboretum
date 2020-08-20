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
"""Repo branch protection evidence unit tests."""

import unittest

from arboretum.auditree.evidences.repo_branch_protection import (
    RepoBranchProtectionEvidence
)


class RepoBranchProtectionEvidenceTest(unittest.TestCase):
    """RepoBranchProtectionEvidence unit tests."""

    def test_no_content(self):
        """Ensure properties requiring content return None when no content."""
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        self.assertIsNone(evidence.admin_enforce)
        self.assertIsNone(evidence.signed_commits_required)
        self.assertIsNone(evidence.as_a_dict)

    def test_gl_not_implemented(self):
        """Ensure NotImplementedError raised for Gitlab."""
        evidence = RepoBranchProtectionEvidence('gl_foo.json', 'bar')
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = 'Support for Gitlab coming soon...'
        with self.assertRaises(NotImplementedError) as ae:
            _ = evidence.admin_enforce
        self.assertEqual(str(ae.exception), gl_err_msg)
        with self.assertRaises(NotImplementedError) as scr:
            _ = evidence.signed_commits_required
        self.assertEqual(str(scr.exception), gl_err_msg)

    def test_bb_not_implemented(self):
        """Ensure NotImplementedError raised for Bitbucket."""
        evidence = RepoBranchProtectionEvidence('bb_foo.json', 'bar')
        evidence.set_content('{"matters": "not"}')
        gl_err_msg = 'Support for Bitbucket coming soon...'
        with self.assertRaises(NotImplementedError) as ae:
            _ = evidence.admin_enforce
        self.assertEqual(str(ae.exception), gl_err_msg)
        with self.assertRaises(NotImplementedError) as scr:
            _ = evidence.signed_commits_required
        self.assertEqual(str(scr.exception), gl_err_msg)

    def test_as_a_dict(self):
        """Ensure dict returned when content is present."""
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        evidence.set_content('{"foo": "bar"}')
        self.assertEqual(evidence.as_a_dict, {'foo': 'bar'})

    def test_admin_enforce(self):
        """Ensure enforce admin details returned."""
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        evidence.set_content('{"foo": "bar"}')
        self.assertFalse(evidence.admin_enforce)
        evidence.set_content('{"enforce_admins": {"enabled": true}}')
        # False expected because as_a_dict content already fetched
        self.assertFalse(evidence.admin_enforce)
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        evidence.set_content('{"enforce_admins": {"enabled": true}}')
        # True expected because evidence is a new object
        self.assertTrue(evidence.admin_enforce)

    def test_signed_commits_required(self):
        """Ensure enforce admin details returned."""
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        evidence.set_content('{"foo": "bar"}')
        self.assertFalse(evidence.signed_commits_required)
        evidence.set_content('{"required_signatures": {"enabled": true}}')
        # False expected because as_a_dict content already fetched
        self.assertFalse(evidence.signed_commits_required)
        evidence = RepoBranchProtectionEvidence('gh_foo.json', 'bar')
        evidence.set_content('{"required_signatures": {"enabled": true}}')
        # True expected because evidence is a new object
        self.assertTrue(evidence.signed_commits_required)
