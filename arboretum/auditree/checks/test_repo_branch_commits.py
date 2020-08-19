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
"""Repository/branch new commits check."""

from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_commit import RepoCommitEvidence

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences


class RepoBranchNewCommitsCheck(ComplianceCheck):
    """Monitor repository/branch new commits."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Repository/Branch New Commits'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'repo_branch_new_commits.md',
                    'auditree',
                    DAY,
                    'Repository/branch new commits report.'
                )
            ]
        )
        return cls

    def test_new_repo_branch_commits(self):
        """Check for new commits made to a repo/branch."""
        branches = self.config.get('org.auditree.repo_integrity.branches')
        for repo_url, repo_branches in branches.items():
            parsed = urlparse(repo_url)
            service = 'gh'
            if 'gitlab' in parsed.hostname:
                service = 'gl'
            elif 'bitbucket' in parsed.hostname:
                service = 'bb'
            repo = parsed.path.strip('/')
            for repo_branch in repo_branches:
                # If included, skip check on the evidence locker
                if (repo_url == self.locker.repo_url
                        and repo_branch == self.locker.branch):
                    continue
                filename = [
                    service,
                    repo.lower().replace('/', '_').replace('-', '_'),
                    repo_branch.lower().replace('-', '_'),
                    'recent_commits.json'
                ]
                path = f'raw/auditree/{"_".join(filename)}'
                with evidences(self, path) as raw:
                    commits = RepoCommitEvidence.from_evidence(raw)
                    for commit in commits.author_info:
                        commit['repo'] = repo_url
                        commit['branch'] = repo_branch
                        self.add_warnings('Recent Commits Found', commit)

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['auditree/repo_branch_new_commits.md']

    def get_notification_message(self):
        """
        Repository/branch new commits check notifier.

        :returns: notification dictionary
        """
        return {'subtitle': 'Repository/branch new commits', 'body': None}
