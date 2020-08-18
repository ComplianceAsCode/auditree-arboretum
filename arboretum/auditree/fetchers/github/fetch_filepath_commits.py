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
"""Github repository branch file path recent commits fetcher."""

import json
import os
from datetime import datetime
from urllib.parse import urlparse

from arboretum.auditree.evidences.repo_commit import RepoCommitEvidence
from arboretum.common.constants import LOCKER_DTTM_FORMAT

from compliance.evidence import DAY, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.services.github import Github


class GithubFilePathCommitsFetcher(ComplianceFetcher):
    """Fetch Github repository branch file path recent commits metadata."""

    def fetch_gh_repo_branch_file_path_recent_commits_details(self):
        """Fetch Github repository branch file path recent commits metadata."""
        filepaths = self.config.get('org.auditree.repo_integrity.filepaths')
        current_url = None
        github = None
        for repo_url, repo_branches in filepaths.items():
            parsed = urlparse(repo_url)
            base_url = f'{parsed.scheme}://{parsed.hostname}'
            repo = parsed.path.strip('/')
            for branch, repo_filepaths in repo_branches.items():
                for filepath in repo_filepaths:
                    ev_file_prefix = f'{repo}_{branch}_{filepath}'.lower()
                    for symbol in [' ', '/', '-', '.']:
                        ev_file_prefix = ev_file_prefix.replace(symbol, '_')
                    path = [
                        'auditree', f'gh_{ev_file_prefix}_recent_commits.json'
                    ]
                    if base_url != current_url:
                        github = Github(self.config.creds, base_url)
                        current_url = base_url
                    self.config.add_evidences(
                        [
                            RepoCommitEvidence(
                                path[1],
                                path[0],
                                DAY,
                                (
                                    f'Github recent commits for {repo} repo '
                                    f'{branch} branch, {filepath} file path'
                                )
                            )
                        ]
                    )
                    joined_path = os.path.join(*path)
                    with raw_evidence(self.locker, joined_path) as evidence:
                        if evidence:
                            meta = self.locker.get_evidence_metadata(
                                evidence.path
                            )
                            if meta is None:
                                meta = {}
                            utcnow = datetime.utcnow()
                            now = utcnow.strftime(LOCKER_DTTM_FORMAT)
                            since = datetime.strptime(
                                meta.get('last_update', now),
                                LOCKER_DTTM_FORMAT
                            )
                            evidence.set_content(
                                json.dumps(
                                    github.get_commit_details(
                                        repo, since, branch, filepath
                                    )
                                )
                            )
