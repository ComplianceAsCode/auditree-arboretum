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
"""Github organization direct collaborators check."""

import json

from compliance.check import ComplianceCheck
from compliance.evidence import DAY, ReportEvidence, get_evidence_by_path
from compliance.utils.data_parse import get_sha256_hash


class OrgCollaboratorsCheck(ComplianceCheck):
    """Checks for organization repo direct collaborators."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Organization repo direct collaborators check'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'org_direct_collaborators.md',
                    'permissions',
                    DAY,
                    'Organization repo direct collaborators report.'
                )
            ]
        )
        return cls

    def test_org_direct_collaborators(self):
        """Check that there are no direct collaborators in the org repos."""
        orgs = self.config.get('org.permissions.org_integrity.orgs')
        for org in orgs:
            host, org_name = org['url'].rsplit('/', 1)
            service = 'gh'
            if 'gitlab' in host:
                service = 'gl'
            elif 'bitbucket' in host:
                service = 'bb'

            url_hash = get_sha256_hash([org['url']], 10)
            fname = f'{service}_direct_collaborators_{url_hash}.json'
            repos = json.loads(
                get_evidence_by_path(f'raw/permissions/{fname}',
                                     self.locker).content
            )
            for repo in repos:
                all_users = repos[repo]
                if not all_users:
                    continue
                self.add_failures(
                    'unexpected-org-collaborators',
                    {
                        'org': org_name,
                        'repo': repo,
                        'users': [u['login'] for u in all_users]
                    }
                )

    def msg_org_direct_collaborators(self):
        """
        Organization repository direct collaborators notifier.

        :returns: notification dictionary
        """
        return {
            'subtitle': 'Unexpected direct collaborators in organizations',
            'body': None
        }

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['permissions/org_direct_collaborators.md']
