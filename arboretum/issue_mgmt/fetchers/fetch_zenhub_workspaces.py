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
"""Github repository Zenhub workspaces fetcher."""

import json

from arboretum.common.constants import GH_HOST_URL, ZH_API_ROOT

from compliance.evidence import DAY, RawEvidence, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.data_parse import get_sha256_hash
from compliance.utils.http import BaseSession
from compliance.utils.services.github import Github


class ZenhubWorkspacesFetcher(ComplianceFetcher):
    """Fetch Zenhub workspaces."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.gh_pool = {}
        cls.zh_pool = {}
        cls.configs = cls.config.get('org.issue_mgmt.zenhub')
        return cls

    @classmethod
    def tearDownClass(cls):
        """Clean up and housekeeping."""
        for session in cls.zh_pool.values():
            session.close()

    def fetch_workspaces(self):
        """Fetch Github repository Zenhub workspaces."""
        for config in self.configs:
            gh_host = config.get('github_host', GH_HOST_URL)
            zh_root = config.get('api_root', ZH_API_ROOT)
            repo = config['github_repo']
            repo_hash = get_sha256_hash([gh_host, repo], 10)
            fname = f'zh_repo_{repo_hash}_workspaces.json'
            self.config.add_evidences(
                [
                    RawEvidence(
                        fname,
                        'issues',
                        DAY,
                        f'Zenhub workspaces for {gh_host}/{repo} repository'
                    )
                ]
            )
            with raw_evidence(self.locker, f'issues/{fname}') as evidence:
                if evidence:
                    if gh_host not in self.gh_pool.keys():
                        self.gh_pool[gh_host] = Github(base_url=gh_host)
                    if zh_root not in self.zh_pool.keys():
                        self.zh_pool[zh_root] = BaseSession(zh_root)
                        service = 'zenhub'
                        if zh_root != ZH_API_ROOT:
                            service = 'zenhub_enterprise'
                        token = self.config.creds[service].token
                        self.zh_pool[zh_root].headers.update(
                            {
                                'Content-Type': 'application/json',
                                'X-Authentication-Token': token
                            }
                        )
                    workspaces = self._get_workspaces(
                        repo, config.get('workspaces'), gh_host, zh_root
                    )
                    evidence.set_content(json.dumps(workspaces))

    def _get_workspaces(self, repo, ws_names, gh_host, zh_root):
        repo_id = self.gh_pool[gh_host].get_repo_details(repo)['id']
        resp = self.zh_pool[zh_root].get(
            f'/p2/repositories/{repo_id}/workspaces'
        )
        resp.raise_for_status()
        workspaces = resp.json()
        if ws_names:
            workspaces = [w for w in workspaces if w['name'] in ws_names]
        results = {}
        for ws in workspaces:
            resp = self.zh_pool[zh_root].get(
                f'/p2/workspaces/{ws["id"]}/repositories/{repo_id}/board'
            )
            resp.raise_for_status()
            results[ws['name']] = resp.json()
        return results
