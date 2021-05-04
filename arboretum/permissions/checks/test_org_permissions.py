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
"""Repository organization permissions check."""

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, evidences
from compliance.utils.data_parse import get_sha256_hash


class OrgPermissionsCheck(ComplianceCheck):
    """Checks for repository organization/owner permissions."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Repository Organization/Owner Permissions'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'org_permissions.md',
                    'permissions',
                    DAY,
                    'Repository organization permission report.'
                )
            ]
        )
        return cls

    def test_org_permissions(self):
        """Check the access to organization repositories."""
        orgs = self.config.get('org.permissions.org_integrity.orgs')
        for org in orgs:
            host, org_name = org['url'].rsplit('/', 1)
            service = 'gh'
            if 'gitlab' in host:
                service = 'gl'
            elif 'bitbucket' in host:
                service = 'bb'
            url_hash = get_sha256_hash([org['url']], 10)
            evidence_paths = {
                'direct': f'raw/permissions/{service}_direct_collaborators_'
                + f'{url_hash}.json',
                'outside': f'raw/permissions/{service}_outside_collaborators_'
                + f'{url_hash}.json',
                'forks': f'raw/permissions/{service}_forks_{url_hash}.json'
            }
            with evidences(self, evidence_paths) as raws:
                self._generate_results(org_name, raws)

    def _generate_results(self, org, ev):
        self.add_failures(
            org,
            self._check_collabs(
                ev['direct'].content_as_json, ev['outside'].content_as_json
            )
        )
        self.add_warnings(org, self._check_forks(ev['forks'].content_as_json))

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

    def get_notification_message(self):
        """
        Repository Organization/Owner Permissions check notifier.

        :returns: notification dictionary
        """
        return {
            'subtitle': 'Repository Organization/Owner Permissions',
            'body': None
        }

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['permissions/org_permissions.md']
