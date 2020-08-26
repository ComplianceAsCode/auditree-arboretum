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

import io
import json
import os
import pathlib
import subprocess
import tempfile
import zipfile

from compliance.evidence import evidences, store_raw_evidence
from compliance.fetch import ComplianceFetcher

import requests

import yaml

from ...ibm_cloud.util.iam import get_tokens


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

    def _fetch_ibm_cloud_resource(self):
        resource_types = self.config.get(
            'org.ibm_cloud.cluster_resource.target_resource_types',
            ClusterResourceFetcher.RESOURCE_TYPE_DEFAULT
        )
        cluster_list = {}
        with evidences(self.locker, 'raw/ibm_cloud/cluster_list.json') as ev:
            cluster_list = json.loads(ev.content)

        resources = {}
        for account in cluster_list:
            api_key = getattr(
                self.config.creds['ibm_cloud'], f'{account}_api_key'
            )

            tokens = get_tokens(api_key)
            resources[account] = []
            for cluster in cluster_list[account]:
                try:
                    if cluster['type'] == 'kubernetes':
                        # get token for an IKS cluster
                        # https://cloud.ibm.com/apidocs/kubernetes#getclusterconfig
                        headers = {
                            'Authorization': 'Bearer '
                            f'{tokens["access_token"]}',
                            'X-Auth-Refresh-Token': tokens['refresh_token']
                        }
                        resp = requests.get(
                            'https://containers.cloud.ibm.com'
                            '/global/v1/clusters/'
                            f'{cluster["id"]}/config',
                            headers=headers
                        )
                        resp.raise_for_status()
                        z = zipfile.ZipFile(io.BytesIO(resp.content))
                        cluster_token = None
                        ca_cert_filepath = None
                        for name in z.namelist():
                            p = pathlib.Path(name)
                            if p.name.startswith('kube-config'):
                                kubeconfig = yaml.safe_load(z.read(name))
                                cluster_token = kubeconfig['users'][0]['user'][
                                    'auth-provider']['config']['id-token']
                            if p.name.endswith('.pem'):
                                tmpdir = tempfile.TemporaryDirectory()
                                z.extract(name, path=tmpdir.name)
                                ca_cert_filepath = os.path.join(
                                    tmpdir.name, name
                                )
                        if cluster_token is None:
                            self.logger.error(
                                'Failed to extract token from the config file '
                                'for cluster "%s".',
                                cluster['name']
                            )
                            continue
                        if ca_cert_filepath is None:
                            self.logger.error(
                                'Failed to extract CA certificate file (*.pem)'
                                ' from the config file'
                                ' for cluster "%s".',
                                cluster['name']
                            )
                            continue
                        headers = {'Authorization': f'Bearer {cluster_token}'}
                        cluster['resources'] = {}
                        for resource in resource_types:
                            resp = requests.get(
                                f'{cluster["serverURL"]}/api/v1/{resource}s',
                                headers=headers,
                                verify=ca_cert_filepath
                            )
                            resp.raise_for_status()
                            cluster['resources'][resource] = resp.json(
                            )['items']
                    elif cluster['type'] == 'openshift':
                        self.logger.warning(
                            'Not implemented cluster type %s: %s',
                            cluster['type'],
                            cluster['name']
                        )
                    else:
                        self.logger.warning(
                            'Ignoring unsupported cluster type "%s": %s',
                            cluster['type'],
                            cluster['name']
                        )
                    resources[account].append(cluster)
                except Exception as e:
                    self.logger.error(
                        'Failed to get resource from cluster "%s": %s',
                        cluster['name'],
                        str(e)
                    )

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
