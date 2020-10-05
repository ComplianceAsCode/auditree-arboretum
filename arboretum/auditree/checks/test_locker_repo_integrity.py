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
"""Evidence locker repo integrity checks."""

from datetime import datetime, timedelta
from difflib import context_diff
from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_branch_protection import (
    RepoBranchProtectionEvidence
)
from arboretum.auditree.evidences.repo_metadata import RepoMetadataEvidence

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences


class LockerRepoIntegrityCheck(ComplianceCheck):
    """Monitor the integrity of evidence locker repositories."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Locker Repository Integrity'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'locker_repo_integrity.md',
                    'auditree',
                    DAY,
                    'Evidence locker repository integrity report.'
                )
            ]
        )
        return cls

    def test_metadata_integrity(self):
        """Check whether the repo details have unexpectedly changed."""
        locker_urls = self.config.get(
            'org.auditree.locker_integrity.repos',
            self.config.get(
                'org.auditree.repo_integrity.repos',
                [self.config.get('locker.repo_url')]
            )
        )
        for locker_url in locker_urls:
            parsed = urlparse(locker_url)
            service = 'gh'
            if 'gitlab' in parsed.hostname:
                service = 'gl'
            elif 'bitbucket' in parsed.hostname:
                service = 'bb'
            repo = parsed.path.strip('/')
            filename = [
                service,
                repo.lower().replace('/', '_').replace('-', '_'),
                'repo_metadata.json'
            ]
            path = f'raw/auditree/{"_".join(filename)}'
            with evidences(self, path) as raw:
                evidence_found = True
                previous_dt = datetime.utcnow() - timedelta(days=1)
                try:
                    previous_raw = self.get_historical_evidence(
                        path, previous_dt
                    )
                except ValueError:
                    self.add_failures(
                        'Locker Repository Metadata - (No prior evidence)',
                        (
                            'No prior evidence found on or prior '
                            f'to {previous_dt.strftime("%b %d, %Y")} '
                            f'for locker `{locker_url}`.'
                        )
                    )
                    evidence_found = False
                if evidence_found:
                    current = RepoMetadataEvidence.from_evidence(raw)
                    prev = RepoMetadataEvidence.from_evidence(previous_raw)
                    if current.repo_size < prev.repo_size:
                        self.add_warnings(
                            'Locker Repository Metadata - (Locker shrunk)',
                            (
                                f'Locker `{locker_url}` appears to have '
                                'shrunk in size/content.  It was '
                                f'{str(prev.repo_size)} and is '
                                f'now {str(current.repo_size)}.'
                            )
                        )
                    difference = ''.join(
                        context_diff(
                            prev.filtered_content.splitlines(keepends=True),
                            current.filtered_content.splitlines(keepends=True),
                            path,
                            path,
                            previous_dt.strftime('%b %d, %Y'),
                            datetime.utcnow().strftime('%b %d, %Y')
                        )
                    )
                    if difference:
                        self.add_failures(
                            'Locker Repository Metadata - (Metadata changed)',
                            (
                                f'Locker `{locker_url}` details have changed.'
                                f'\n\n```\n{difference}\n```\n'
                            )
                        )

    def test_branch_protection_integrity(self):
        """Check whether branch protection settings are set for admins."""
        locker_branches = self.config.get(
            'org.auditree.locker_integrity.branches',
            self.config.get(
                'org.auditree.repo_integrity.branches',
                {self.config.get('locker.repo_url'): ['master']}
            )
        )
        for locker_url, branches in locker_branches.items():
            parsed = urlparse(locker_url)
            service = 'gh'
            if 'gitlab' in parsed.hostname:
                service = 'gl'
            elif 'bitbucket' in parsed.hostname:
                service = 'bb'
            repo = parsed.path.strip('/')
            for branch in branches:
                filename = [
                    service,
                    repo.lower().replace('/', '_').replace('-', '_'),
                    branch.lower().replace('-', '_'),
                    'branch_protection.json'
                ]
                path = f'raw/auditree/{"_".join(filename)}'
                with evidences(self, path) as raw:
                    evidence = RepoBranchProtectionEvidence.from_evidence(raw)
                    if not evidence.admin_enforce:
                        self.add_failures(
                            'Locker Branch Protection',
                            (
                                f'Branch protection for `{locker_url}` '
                                f'`{branch}` branch '
                                'is not enforced for administrators.'
                            )
                        )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['auditree/locker_repo_integrity.md']

    def msg_metadata_integrity(self):
        """
        Evidence locker metadata integrity check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'Locker metadata settings', 'body': None}

    def msg_branch_protection_integrity(self):
        """
        Evidence locker branch protection integrity check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'Locker branch protection settings', 'body': None}
