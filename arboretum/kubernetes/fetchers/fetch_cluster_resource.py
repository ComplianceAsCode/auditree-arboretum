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
"""Kubernetes stand-alone cluster resource fetcher."""

import json

from arboretum.common.kube_constants import RESOURCE_TYPES_DEFAULT
from arboretum.common.kube_utils import get_cluster_resources

from compliance.evidence import DAY, RawEvidence, store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterResourceFetcher(ComplianceFetcher):
    """Fetch resources of Kubernetes stand-alone clusters."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.config.add_evidences(
            [
                RawEvidence(
                    "cluster_resources.json",
                    "kubernetes",
                    DAY,
                    "Kubernetes cluster resources",
                )
            ]
        )
        cls.resource_types = cls.config.get(
            "org.kubernetes.cluster_resources.types", RESOURCE_TYPES_DEFAULT
        )
        return cls

    @store_raw_evidence("kubernetes/cluster_resources.json")
    def fetch_cluster_resources(self):
        """Fetch cluster resources."""
        clusters = self.config.get("org.kubernetes.cluster_resources.clusters")
        for cluster in clusters:
            token = self.config.creds.get("kubernetes", f'{cluster["label"]}_token')
            cluster["resources"] = get_cluster_resources(
                self.session(cluster["server"]),
                token,
                self.resource_types,
                verify=False,
            )
        return json.dumps(clusters)
