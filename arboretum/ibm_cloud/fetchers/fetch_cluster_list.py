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
import subprocess

from arboretum.common.utils import mask_secrets

from compliance.evidence import store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterListFetcher(ComplianceFetcher):
    """Fetch the list of IBM Cloud clusters."""

    @store_raw_evidence('ibm_cloud/cluster_list.json')
    def fetch_cluster_list(self):
        """Fetch IBM Cloud cluster list."""
        accounts = self.config.get('org.ibm_cloud.cluster_list.account')
        cluster_list = {}
        for account in accounts:
            cluster_list[account] = self._get_cluster_list(account)
        return json.dumps(cluster_list)

    def _run_command(self, args):
        return subprocess.run(
            args,
            text=True,
            timeout=30,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            shell=False
        )

    def _get_cluster_list(self, account):

        logger = self.locker.logger.getChild('ibm_cloud.cluster_list_fetcher')
        # get credential for the account
        api_key = getattr(self.config.creds['ibm_cloud'], f'{account}_api_key')

        # login
        try:
            self._run_command(
                ['ibmcloud', 'login', '--no-region', '--apikey', api_key]
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                'Failed to login with account %s: %s',
                account,
                mask_secrets(str(e), [api_key])
            )
            return

        # get cluster list
        cluster_list = None
        cmd = ['ibmcloud', 'cs', 'cluster', 'ls', '--json']
        try:
            cp = self._run_command(cmd)
            cluster_list = cp.stdout
        except subprocess.CalledProcessError as e:
            if e.returncode == 2:  # RC: 2 == no plugin
                logger.warning(
                    'Kubernetes service plugin missing.  '
                    'Attempting to install plugin...'
                )
                self._run_command(
                    ['ibmcloud', 'plugin', 'install', 'kubernetes-service']
                )
                cp = self._run_command(cmd)
                cluster_list = cp.stdout
            else:
                raise
        finally:
            self._run_command(['ibmcloud', 'logout'])

        return json.loads(cluster_list)
