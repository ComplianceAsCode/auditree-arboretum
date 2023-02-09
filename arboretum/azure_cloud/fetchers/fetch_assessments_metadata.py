# Copyright (c) 2023 EnterpriseDB Corp. All rights reserved.
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
"""Azure Cloud assessment metadata fetcher API."""

import json

from arboretum.azure_cloud.fetchers.common import (
    get_assessments_by_account,
    get_azure_accounts,
    get_credentials,
)
from arboretum.azure_cloud.fetchers.azure_constants import AZURE_MANAGEMENT_BASE_URL

from compliance.evidence import HOUR, RawEvidence, raw_evidence
from compliance.fetch import ComplianceFetcher

from parameterized import parameterized


class AssessmentsMetaDataListFetcher(ComplianceFetcher):
    """Fetch assessments metadata in the specified subscription."""

    @classmethod
    def setUpClass(cls):
        """Initialize the fetcher object with configuration settings."""
        headers = {"Accept": "application/json"}
        cls.session(AZURE_MANAGEMENT_BASE_URL, **headers)
        return cls

    @parameterized.expand(get_azure_accounts)
    def fetch_full_assessment_metadata_list(self, account):
        """Fetch Azure Cloud full assessment metadata."""
        _, _, _, subscription_id = get_credentials(self.config, account)
        api = (
            f"subscriptions/{subscription_id}"
            + "/providers/Microsoft.Security/"
            + "assessmentMetadata?api-version=2020-01-01"
        )
        assessments_by_account = get_assessments_by_account(
            account, self.session(), self.config, api
        )
        evidence_path = f"azure_cloud/assessment_metadata_{account}_list.json"
        self.config.add_evidences(
            [
                RawEvidence(
                    evidence_path,
                    "azure_cloud",
                    8 * HOUR,
                    f"Azure Cloud assessments metadata list for account {account}",
                )
            ]
        )
        with raw_evidence(self.locker, evidence_path) as evidence:
            if evidence:
                evidence.set_content(json.dumps(assessments_by_account))
