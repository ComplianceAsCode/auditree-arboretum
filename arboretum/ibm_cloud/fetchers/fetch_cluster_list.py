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
"""IKS cluster list fetcher."""

import json

from arboretum.common.errors import CommandExecutionError
from arboretum.common.utils import run_command

from compliance.evidence import store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterListFetcher(ComplianceFetcher):
    """Fetch the list of IBM Cloud clusters."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.logger = cls.locker.logger.getChild(
            'ibm_cloud.cluster_list_fetcher'
        )
        return cls

    @store_raw_evidence('ibm_cloud/cluster_list.json')
    def fetch_cluster_list(self):
        """Fetch IBM Cloud cluster list."""
        for account in self.config.get(
                'org.ibm_cloud.cluster_list.config.account'):
            return json.dumps({account: self._get_cluster_list(account)})

    def _get_cluster_list(self, account):

        # get credential for the account
        api_key = getattr(self.config.creds['ibm_cloud'], account + '_api_key')

        # login
        run_command(
            f'ibmcloud login --no-region --apikey {api_key}',
            secrets=[api_key]
        )

        # get cluster list
        cluster_list = None
        cmd = 'ibmcloud cs cluster ls --json'
        try:
            cluster_list = run_command(cmd)
        except CommandExecutionError as e:
            if e.returncode == 2:  # "2" means no plugin error
                self.logger.warning(
                    'Failed to execute "ibmcloud cs" command'
                    ' - trying to install the cs plugin'
                )
                run_command('ibmcloud plugin install kubernetes-service')
                cluster_list = run_command(cmd)
            else:
                raise e
        return json.loads(cluster_list)
