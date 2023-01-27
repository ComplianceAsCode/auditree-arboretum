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
"""IBM Cloud cluster resource fetcher."""

import io
import json
import pathlib
import tempfile
import zipfile

from arboretum.common.iam_ibm_utils import get_tokens
from arboretum.common.kube_constants import RESOURCE_TYPES_DEFAULT
from arboretum.common.kube_utils import get_cluster_resources

from compliance.evidence import (
    DAY,
    RawEvidence,
    get_evidence_dependency,
    store_raw_evidence,
)
from compliance.fetch import ComplianceFetcher

import yaml


class ICClusterResourceFetcher(ComplianceFetcher):
    """Fetch resources of IBM Cloud Kubernetes clusters."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.config.add_evidences(
            [
                RawEvidence(
                    "cluster_resources.json",
                    "ibm_cloud",
                    DAY,
                    "IBM Cloud Kubernetes cluster resources",
                )
            ]
        )
        cls.resource_types = cls.config.get(
            "org.ibm_cloud.cluster_resources.types", RESOURCE_TYPES_DEFAULT
        )
        cls.tempdir = tempfile.TemporaryDirectory()
        return cls

    @classmethod
    def tearDownClass(cls):
        """Cleanup class."""
        cls.tempdir.cleanup()

    @store_raw_evidence("ibm_cloud/cluster_resources.json")
    def fetch_cluster_resource(self):
        """Fetch cluster resources."""
        cluster_list_evidence = get_evidence_dependency(
            "raw/ibm_cloud/cluster_list.json", self.locker
        )
        cluster_list = cluster_list_evidence.content_as_json
        resources = {}
        for account in cluster_list:
            api_key = self.config.creds.get("ibm_cloud", f"{account}_api_key")
            access_token, refresh_token = get_tokens(api_key)
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-Auth-Refresh-Token": refresh_token,
            }
            self.session("https://containers.cloud.ibm.com", **headers)

            resources[account] = []
            for cluster in cluster_list[account]:
                self.session("https://containers.cloud.ibm.com", **headers)
                config_url = f'/global/v1/clusters/{cluster["id"]}/config'
                resp = self.session().get(config_url)
                resp.raise_for_status()
                cluster_config = zipfile.ZipFile(io.BytesIO(resp.content))
                if cluster["type"] == "kubernetes":
                    cluster_token, ca_cert = self._get_iks_credentials(cluster_config)
                elif cluster["type"] == "openshift":
                    cluster_token = self._get_roks_credentials(cluster, api_key)
                    ca_cert = None
                self.session(cluster["serverURL"], **headers)
                cluster["resources"] = get_cluster_resources(
                    self.session(), cluster_token, self.resource_types, ca_cert
                )
                resources[account].append(cluster)

        return json.dumps(resources)

    def _get_iks_credentials(self, cluster_config):
        """Get credentials for an IKS cluster.

        This function implements the procedure described in
        https://cloud.ibm.com/apidocs/kubernetes#getclusterconfig
        """
        for name in cluster_config.namelist():
            p = pathlib.PurePath(name)
            if p.name.startswith("kube-config"):
                kubeconfig = yaml.safe_load(cluster_config.read(name))
                usr = kubeconfig["users"][0]["user"]
                cluster_token = usr["auth-provider"]["config"]["id-token"]
            if p.suffix == ".pem":
                cluster_config.extract(name, path=self.tempdir.name)
                ca_cert_filepath = str(pathlib.PurePath(self.tempdir.name, name))
        return cluster_token, ca_cert_filepath

    def _get_roks_credentials(self, cluster, api_key):
        """Get credentials for a ROKS cluster.

        This function implements the procedure described in
        https://cloud.ibm.com/docs/openshift?topic=openshift-access_cluster#access_automation
        """
        s = self.session(cluster["serverURL"])
        oauth_path = "/.well-known/oauth-authorization-server"
        resp = s.get(oauth_path)
        resp.raise_for_status()
        token_endpoint = resp.json()["token_endpoint"]
        oauth_server = token_endpoint.split("/")[2]
        s = self.session(f"https://{oauth_server}")
        token_path = (
            "/oauth/authorize?client_id="  # nosec B105
            "openshift-challenging-client&response_type=token"
        )
        resp = s.get(
            token_path,
            auth=("apikey", api_key),
            headers={"X-CSRF-Token": "a"},
            allow_redirects=False,
        )
        location = resp.headers["Location"]
        cluster_token = location.split("access_token=", 1)[1].split("&", 1)[0]

        return cluster_token
