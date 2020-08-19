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
"""Repository/branch/filepath new commits check."""

from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_commit import RepoCommitEvidence

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences


class FilepathNewCommitsCheck(ComplianceCheck):
    """Monitor repository/branch/filepath new commits."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Repository/Branch/Filepath New Commits'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'filepath_new_commits.md',
                    'auditree',
                    DAY,
                    'Repository/branch/filepath new commits report.'
                )
            ]
        )
        return cls

    def test_new_filepath_commits(self):
        """Check for new commits made to a repo/branch/filepath."""
        filepaths = self.config.get('org.auditree.repo_integrity.filepaths')
        for repo_url, repo_branches in filepaths.items():
            parsed = urlparse(repo_url)
            service = 'gh'
            if 'gitlab' in parsed.hostname:
                service = 'gl'
            elif 'bitbucket' in parsed.hostname:
                service = 'bb'
            repo = parsed.path.strip('/')
            for repo_branch, repo_filepaths in repo_branches.items():
                for filepath in repo_filepaths:
                    ev_file_prefix = f'{repo}_{repo_branch}_{filepath}'.lower()
                    for symbol in [' ', '/', '-', '.']:
                        ev_file_prefix = ev_file_prefix.replace(symbol, '_')
                    fname = f'{service}_{ev_file_prefix}_recent_commits.json'
                    with evidences(self, f'raw/auditree/{fname}') as raw:
                        commits = RepoCommitEvidence.from_evidence(raw)
                        for commit in commits.author_info:
                            commit['repo'] = repo_url
                            commit['branch'] = repo_branch
                            self.add_warnings(
                                f'Recent Commits Found - (`{filepath}`)',
                                commit
                            )

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['auditree/filepath_new_commits.md']

    def get_notification_message(self):
        """
        Repository/branch/filepath new commits check notifier.

        :returns: notification dictionary
        """
        return {
            'subtitle': 'Repository/branch/filepath new commits', 'body': None
        }
