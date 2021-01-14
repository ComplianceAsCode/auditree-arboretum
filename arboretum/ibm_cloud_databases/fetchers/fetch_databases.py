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
"""IBM Cloud Databases list fetcher."""
import json

from arboretum.common.iam_ibm_utils import get_tokens
from arboretum.common.ibm_constants import RESOURCE_CONTROLLER_BASE_URL

from compliance.evidence import DAY, RawEvidence, raw_evidence
from compliance.fetch import ComplianceFetcher


class DatabasesFetcher(ComplianceFetcher):
    """Fetches databases list."""

    @classmethod
    def setUpClass(cls):
        """Initialize object from config file."""
        cls.accounts = cls.config.get('org.icd.list.accounts')
        for acct in cls.accounts:
            acct_name = acct['account_name']
            cls.config.add_evidences(
                [
                    RawEvidence(
                        f'databases_{acct_name}.json',
                        'icd',
                        DAY,
                        'list of all databases for account'
                    )
                ]
            )
        headers = {'Accept': 'application/json'}
        cls.session(RESOURCE_CONTROLLER_BASE_URL, **headers)

        return cls

    def fetch_databases(self):
        """Fetch IBM Cloud Databases for each account."""
        for acct in self.accounts:
            acct_name = acct['account_name']
            evidence_path = f'raw/icd/databases_{acct_name}.json'
            resource_group_ids = acct['resource_group_id']
            if isinstance(resource_group_ids, str):
                resource_group_ids = [resource_group_ids]

            with raw_evidence(self.locker, evidence_path) as evidence:
                if evidence:
                    db_list = []
                    for resource_group_id in resource_group_ids:
                        db_list.append(
                            self._get_ibmcloud_db_list(
                                acct_name, resource_group_id
                            )
                        )

                    evidence.set_content(json.dumps(db_list))

    def _get_ibmcloud_db_list(self, account, resource_group_id):

        # get credential for the account
        api_key = getattr(self.config.creds['ibm_cloud'], f'{account}_api_key')
        # get database list
        # https://cloud.ibm.com/apidocs/resource-controller/resource-controller
        self.session().headers.update(
            {'Authorization': f'Bearer {get_tokens(api_key)[0]}'}
        )
        resp = self.session().get(
            '/v1/resource_instances',
            params={
                'resource_group_id': resource_group_id,
                'resource_plan_id': 'databases-for-*'
            }
        )
        resp.raise_for_status()
        return resp.json()
