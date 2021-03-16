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
"""Github repository issues fetcher."""

import json

from arboretum.common.constants import GH_HOST_URL

from compliance.evidence import DAY, RawEvidence, raw_evidence
from compliance.fetch import ComplianceFetcher
from compliance.utils.data_parse import get_sha256_hash
from compliance.utils.services.github import Github


class GithubIssuesFetcher(ComplianceFetcher):
    """Fetch Github repository issues."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.gh_pool = {}
        cls.configs = cls.config.get('org.issue_mgmt.github')
        return cls

    def fetch_issues(self):
        """Fetch Github repository issues."""
        for config in self.configs:
            host = config.get('host', GH_HOST_URL)
            repo = config['repo']
            fname = f'gh_repo_{get_sha256_hash([host, repo], 10)}_issues.json'
            self.config.add_evidences(
                [
                    RawEvidence(
                        fname,
                        'issues',
                        DAY,
                        f'Github issues for {host}/{repo} repository'
                    )
                ]
            )
            with raw_evidence(self.locker, f'issues/{fname}') as evidence:
                if evidence:
                    if host not in self.gh_pool.keys():
                        self.gh_pool[host] = Github(base_url=host)
                    issues = []
                    for search in self._compose_searches(config, host):
                        issue_ids = [i['id'] for i in issues]
                        for result in self.gh_pool[host].search_issues(search):
                            if result['id'] not in issue_ids:
                                issues.append(result)
                    evidence.set_content(json.dumps(issues))

    def _compose_searches(self, config, host):
        base = f'repo:{config["repo"]} is:issue'
        if 'search' in config.keys():
            return [f'{base} {config["search"]}']
        searches = []
        for state in config.get('states', ['open']):
            base += f' is:{state}'
        for label in self._get_labels(config, host):
            searches.append(f'{base} label:"{label}"')
        return searches

    def _get_labels(self, config, host):
        if not config.get('labels'):
            return []
        repo = config['repo']
        path = f'repos/{repo}/labels'
        all_label_content = self.gh_pool[host].paginate_api(path)
        all_labels = [label['name'] for label in all_label_content]
        label_filters = {
            'equals': lambda lbl: lbl == _label,
            'contains': lambda lbl: _label in lbl,
            'startswith': lambda lbl: lbl.startswith(_label),
            'endswith': lambda lbl: lbl.endswith(_label)
        }
        labels = set()
        for operator, config_labels in config['labels'].items():
            for _label in config_labels:
                labels.update(filter(label_filters[operator], all_labels))
        return list(labels)
