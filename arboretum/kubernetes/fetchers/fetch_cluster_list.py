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
"""Fetch cluster list by using other providers' fetch_cluster_list function."""
import json

from compliance.evidence import store_raw_evidence
from compliance.fetch import ComplianceFetcher


class ClusterListFetcher(ComplianceFetcher):
    """Fetch BOM (Bill of Materials) as cluster list."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        cls.logger = cls.locker.logger.getChild(
            'kubernetes.cluster_list_fetcher'
        )
        return cls

    @store_raw_evidence('kubernetes/cluster_list.json')
    def fetch_cluster_list(self):
        """Fetch BOM (Bill of Materials) as cluster list."""
        bom = self.config.get('org.kubernetes.cluster_list.bom')
        return json.dumps(bom)
