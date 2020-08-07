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

from compliance.evidence import evidences, store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterResourceFetcher(ComplianceFetcher):
    """Fetch the resources of clusters."""

    RESOURCE_TYPE_DEFAULT = ['node', 'pod', 'configmap']

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.logger = cls.locker.logger.getChild(
            'kubernetes.cluster_resource_fetcher'
        )
        return cls

    @store_raw_evidence('kubernetes/cluster_resource.json')
    def fetch_cluster_resource(self):
        """Fetch cluster resources of listed clusters."""
        cluster_list_types = self.config.get(
            'org.kubernetes.cluster_resource.config.cluster_list_types'
        )

        resources = {}
        for cltype in cluster_list_types:
            try:
                if cltype == 'kubernetes':
                    resources['kubernetes'] = self._fetch_bom_resource()
                elif cltype == 'ibm_cloud':
                    resources['ibm_cloud'] = self._fetch_ibm_cloud_resource()
                else:
                    self.logger.error(
                        'Specified cluster list type "%s" is not supported',
                        cltype
                    )
            except Exception as e:
                self.logger.error(
                    'Failed to fetch resources for cluster list "%s": %s',
                    cltype,
                    str(e)
                )
            continue

        return json.dumps(resources)

    def _fetch_bom_resource(self):
        resource_types = self.config.get(
            'org.kubernetes.cluster_resource.config.target_resource_types',
            ClusterResourceFetcher.RESOURCE_TYPE_DEFAULT
        )

        bom = {}
        with evidences(self.locker, 'raw/kubernetes/cluster_list.json') as ev:
            bom = json.loads(ev.content)

        resources = {}
        for c in bom:
            cluster_resources = []
            for r in resource_types:
                cmd = (
                    f'kubectl --kubeconfig {c["kubeconfig"]}'
                    f' get {r} -A -o json'
                )
                out = run_command(cmd)
                cluster_resources.extend(json.loads(out)['items'])
            resources[c['account']] = [
                {
                    'name': c['name'], 'resources': cluster_resources
                }
            ]
        return resources

    def _fetch_ibm_cloud_resource(self):
        resource_types = self.config.get(
            'org.ibm_cloud.cluster_resource.config.target_resource_types',
            ClusterResourceFetcher.RESOURCE_TYPE_DEFAULT
        )
        cluster_list = {}
        with evidences(self.locker, 'raw/ibm_cloud/cluster_list.json') as ev:
            cluster_list = json.loads(ev.content)

        resources = {}
        for account in cluster_list:
            api_key = getattr(
                self.config.creds['ibm_cloud'], account + '_api_key'
            )
            # login
            run_command(
                f'ibmcloud login --no-region --apikey {api_key}',
                secrets=[api_key]
            )
            resources[account] = []
            for cluster in cluster_list[account]:
                # get configuration
                cmd = f'ibmcloud cs cluster config -s -c {cluster["name"]}'
                try:
                    run_command(cmd)
                except CommandExecutionError as e:
                    if e.returncode == 2:  # 2 means no plugin error
                        self.logger.warning(
                            'Failed to execute '
                            '"ibmcloud cs" command. '
                            'trying to install the cs plugin.'
                        )
                        run_command(
                            'ibmcloud plugin install kubernetes-service'
                        )
                        run_command(cmd)
                    else:
                        raise e

                # login using "oc" command if the target is openshift
                if cluster['type'] == 'openshift':
                    run_command(f'oc login -u apikey -p {api_key}')

                # get resources
                resource_list = []
                for resource in resource_types:
                    try:
                        output = run_command(
                            f'kubectl get {resource} -A -o json'
                        )
                        resource_list.extend(json.loads(output)['items'])
                    except RuntimeError:
                        self.logger.warning(
                            'Failed to get %s resource in cluster %s',
                            resource,
                            cluster['name']
                        )
                cluster['resources'] = resource_list
                resources[account].append(cluster)

        return resources
