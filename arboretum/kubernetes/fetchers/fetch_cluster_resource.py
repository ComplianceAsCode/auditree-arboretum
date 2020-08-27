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
"""Cluster resource fetcher for various types of clusters."""

import json
import subprocess
from importlib import import_module

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
            'org.kubernetes.cluster_resource.cluster_list_types'
        )

        resources = {}
        for cltype in cluster_list_types:
            try:
                if cltype == 'kubernetes':
                    resources['kubernetes'] = self._fetch_bom_resource()
                else:
                    module_name = (
                        'arboretum.kubernetes.fetchers.'
                        f'fetch_cluster_resource_{cltype}'
                    )
                    function_name = 'fetch_cluster_resource'
                    try:
                        module = import_module(module_name)
                    except ModuleNotFoundError:
                        self.logger.error(
                            'Failed to load plugin for cluster type "%s": %s',
                            cltype,
                            module_name
                        )
                        raise
                    try:
                        fetcher = getattr(module, function_name)
                    except AttributeError:
                        self.logger.error(
                            'Failed to load expected funtion "%s" '
                            'in module "%s"',
                            function_name,
                            module_name
                        )
                        raise
                    resources[cltype] = fetcher(self)
            except Exception as e:
                self.logger.error(
                    'Failed to fetch resources for cluster list "%s": %s',
                    cltype,
                    str(e)
                )
                raise
        return json.dumps(resources)

    def _fetch_bom_resource(self):
        resource_types = self.config.get(
            'org.kubernetes.cluster_resource.target_resource_types',
            ClusterResourceFetcher.RESOURCE_TYPE_DEFAULT
        )

        bom = {}
        with evidences(self.locker, 'raw/kubernetes/cluster_list.json') as ev:
            bom = json.loads(ev.content)

        resources = {}
        for c in bom:
            cluster_resources = []
            for r in resource_types:
                args = [
                    'kubectl',
                    '--kubeconfig',
                    c['kubeconfig'],
                    'get',
                    r,
                    '-A',
                    '-o',
                    'json'
                ]
                cp = self._run_command(args)
                out = cp.stdout
                cluster_resources.extend(json.loads(out)['items'])
            resources[c['account']] = [
                {
                    'name': c['name'], 'resources': cluster_resources
                }
            ]
        return resources

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
