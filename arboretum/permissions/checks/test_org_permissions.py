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

from ..evidences.org_direct_collaborators import OrgDirectCollaboratorsEvidence
from ..evidences.org_repo_forks import OrgRepoForksEvidence
from ..evidences.org_teams import OrgTeamsEvidence


class OrgPermissionsCheck(ComplianceCheck):
    """Monitor repository organization permissions."""

    @property
    def title(self):
        """
        Return the title of the checks.

        :returns: the title of the checks
        """
        return 'Report on Repository Organization Permissions'

    @classmethod
    def setUpClass(cls):
        """Initialize the check object with configuration settings."""
        cls.config.add_evidences(
            [
                ReportEvidence(
                    'org_permissions.md',
                    'permissions',
                    DAY,
                    'Repository Permissions.'
                )
            ]
        )
        return cls

    def test_org_permissions(self):
        """Check the access to organization repositories."""
        orgs = self.config.get('org.permissions.org_integrity.orgs')
        for org in orgs:
            host = org['url'].rsplit('/', 1)
            url_hash = get_sha256_hash([org['url']], 10)
            service = 'gh'
            if 'gitlab' in host:
                service = 'gl'
            elif 'bitbucket' in host:
                service = 'bb'
            evidence_paths = {
                'direct': f'raw/permissions/{service}_direct_collaborators_'
                + f'{url_hash}.json',
                'forks': f'raw/permissions/{service}_forks_{url_hash}.json',
                'teams': f'raw/permissions/{service}_teams_{url_hash}.json',
            }
            with evidences(self, evidence_paths) as ev:
                dc_ev = OrgDirectCollaboratorsEvidence.from_evidence(
                    ev['direct']
                )
                f_ev = OrgRepoForksEvidence.from_evidence(ev['forks'])
                t_ev = OrgTeamsEvidence.from_evidence(ev['teams'])

                self.add_failures(org['url'], dc_ev.direct_collabs)
                self.add_warnings(org['url'], f_ev.forks)
                self.add_successes(org['url'], t_ev.teams)

    def get_reports(self):
        """
        Provide the check report name.

        :returns: the report(s) generated for this check
        """
        return ['permissions/org_permissions.md']
