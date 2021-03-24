# -*- mode:python; coding:utf-8 -*-
# Copyright (c) 2021 IBM Corp. All rights reserved.
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
"""Github repositories permissions checks."""

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences
from compliance.utils.data_parse import get_sha256_hash


class GithubOrgPermissionsCheck(ComplianceCheck):
    """Monitor the permissions of Github repositories."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Report on Github Repositories Permissions'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'org_permissions.md',
                    'permissions',
                    DAY,
                    'Github Repository Permissions.'
                )
            ]
        )
        return cls

    def test_repo_permissions(self):
        """Check the access to Github repositories containing source code."""
        orgs = self.config.get('org.permissions.org_integrity.orgs')
        for org in orgs:
            host, org_name = org['url'].rsplit('/', 1)
            url_hash = get_sha256_hash([org['url']], 10)
            evidence_paths = {
                'direct': 'raw/permissions/gh_direct_collaborators_'
                + f'{url_hash}.json',
                'outside': 'raw/permissions/gh_outside_collaborators_'
                + f'{url_hash}.json',
                'forks': f'raw/permissions/gh_forks_{url_hash}.json',
                'teams': f'raw/permissions/gh_teams_{url_hash}.json',
            }
            with evidences(self, evidence_paths) as ev:
                self.add_failures(
                    org['url'],
                    self._check_collabs(
                        ev['direct'].content_as_json,
                        ev['outside'].content_as_json
                    )
                )
                self.add_warnings(
                    org['url'], self._check_forks(ev['forks'].content_as_json)
                )
                self.add_successes(
                    org['url'], self._check_teams(ev['teams'].content_as_json)
                )

    def _check_collabs(self, ev_direct, ev_outside):
        repocollabs = []
        for repo in ev_direct:
            collabs = []
            for c in ev_direct[repo]:
                c['member'] = c not in ev_outside[repo]
                collabs.append(c)
            if not collabs:
                continue
            if collabs:
                repocollabs.append({'repo': repo, 'collabs': collabs})
        return repocollabs

    def _check_forks(self, evidence):
        repoforks = []
        for repo in evidence:
            forks = [f['html_url'] for f in evidence[repo]]
            if not forks:
                continue
            if forks:
                repoforks.append({'repo': repo, 'forks': forks})
        return repoforks

    def _check_teams(self, evidence):
        repoteams = []
        for repo in evidence:
            teams = [t['name'] for t in evidence[repo]]
            if not teams:
                continue
            if teams:
                repoteams.append({'repo': repo, 'teams': teams})
        return repoteams

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['permissions/org_permissions.md']
