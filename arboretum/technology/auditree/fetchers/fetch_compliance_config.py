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
"""Compliance execution configuration fetcher."""

import json

from compliance.evidence import HOUR, RawEvidence
from compliance.fetch import ComplianceFetcher


class ComplianceConfigFetcher(ComplianceFetcher):
    """Fetch the current current compliance tooling configuration."""

    def fetch_compliance_configuration(self):
        """Fetch the compliance tooling configuration.

        - Evidence is refreshed to the locker regardless of TTL
        - Evidence is valid for the next two hours (for the check)
        """
        evidence = RawEvidence(
            'compliance_config.json',
            'auditree',
            2 * HOUR,
            'Compliance Configuration'
        )
        evidence.set_content(json.dumps(self.config.raw_config))
        self.locker.add_evidence(evidence)
