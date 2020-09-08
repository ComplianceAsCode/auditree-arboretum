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
"""IBM Cloud cluster list fetcher."""

import json

from arboretum.common.iam_ibm_utils import get_tokens
from arboretum.common.ibm_constants import IC_CONTAINERS_BASE_URL

from compliance.evidence import DAY, RawEvidence, store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterListFetcher(ComplianceFetcher):
    """Fetch the list of IBM Cloud clusters."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.config.add_evidences(
            [
                RawEvidence(
                    'cluster_list.json',
                    'ibm_cloud',
                    DAY,
                    'IBM Cloud cluster list inventory'
                )
            ]
        )
        headers = {'Accept': 'application/json'}
        cls.session(IC_CONTAINERS_BASE_URL, **headers)

        return cls

    @store_raw_evidence('ibm_cloud/cluster_list.json')
    def fetch_cluster_list(self):
        """Fetch IBM Cloud cluster list."""
        accounts = self.config.get('org.ibm_cloud.accounts')
        cluster_list = {}
        for account in accounts:
            cluster_list[account] = self._get_cluster_list(account)
        return json.dumps(cluster_list)

    def _get_cluster_list(self, account):

        # get credential for the account
        api_key = getattr(self.config.creds['ibm_cloud'], f'{account}_api_key')
        # get cluster list
        # https://cloud.ibm.com/apidocs/kubernetes#getclusters
        self.session().headers.update(
            {'Authorization': f'Bearer {get_tokens(api_key)[0]}'}
        )
        resp = self.session().get('/global/v1/clusters')
        resp.raise_for_status()
        return resp.json()
